import json
import logging
import os
from pathlib import Path

import jwt
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from jwt.algorithms import RSAAlgorithm


logger = logging.getLogger(__name__)
User = get_user_model()

DEFAULT_GOOGLE_CERTS_URL = 'https://www.googleapis.com/oauth2/v3/certs'
GOOGLE_ISSUERS = {
    'accounts.google.com',
    'https://accounts.google.com',
}


class GoogleAuthError(Exception):
    """Raised when Google ID token verification or user provisioning fails."""


def _client_id() -> str:
    return (getattr(settings, 'GOOGLE_CLIENT_ID', '') or '').strip().strip('"').strip("'")


def _proxy_dict():
    proxy = (
        getattr(settings, 'GOOGLE_HTTPS_PROXY', '')
        or os.getenv('HTTPS_PROXY', '')
        or os.getenv('https_proxy', '')
        or os.getenv('HTTP_PROXY', '')
        or os.getenv('http_proxy', '')
    ).strip()
    if not proxy:
        return None
    return {'https': proxy, 'http': proxy}


def _jwks_path() -> Path | None:
    raw = (getattr(settings, 'GOOGLE_JWKS_PATH', '') or '').strip()
    if not raw:
        return None
    return Path(raw)


def _load_jwks_from_file() -> dict | None:
    path = _jwks_path()
    if path is None or not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        if not data.get('keys'):
            logger.warning('Google JWKS file has no keys: %s', path)
            return None
        logger.info('Loaded Google JWKS from file %s (%s keys)', path, len(data['keys']))
        return data
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning('Failed reading Google JWKS file %s: %s', path, exc)
        return None


def _fetch_jwks_from_network() -> dict:
    url = (getattr(settings, 'GOOGLE_JWKS_URL', '') or DEFAULT_GOOGLE_CERTS_URL).strip()
    proxies = _proxy_dict()
    try:
        response = requests.get(url, timeout=15, proxies=proxies)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        logger.exception('Failed fetching Google JWKS from %s', url)
        raise GoogleAuthError(
            'Server cannot reach Google (certs). '
            'Outbound HTTPS to googleapis.com is blocked or timed out. '
            'Set GOOGLE_JWKS_PATH to a cached certs file, or GOOGLE_HTTPS_PROXY.'
        ) from exc

    if not data.get('keys'):
        raise GoogleAuthError('Google JWKS response contained no keys.')

    path = _jwks_path()
    if path is not None:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(data), encoding='utf-8')
            logger.info('Cached Google JWKS to %s', path)
        except OSError:
            logger.warning('Could not cache Google JWKS to %s', path, exc_info=True)

    return data


def load_google_jwks(*, force_network: bool = False) -> dict:
    """
    Load Google signing keys.

    Order:
    1. Local cache file (works offline / blocked VPS) unless force_network
    2. Network fetch (optional proxy / custom JWKS URL)
    """
    if not force_network:
        cached = _load_jwks_from_file()
        if cached is not None:
            return cached
    return _fetch_jwks_from_network()


def _public_key_for_token(token: str, jwks: dict):
    try:
        header = jwt.get_unverified_header(token)
    except jwt.InvalidTokenError as exc:
        raise GoogleAuthError('Invalid Google ID token header.') from exc

    kid = header.get('kid')
    if not kid:
        raise GoogleAuthError('Google ID token is missing key id.')

    for key_data in jwks.get('keys', []):
        if key_data.get('kid') == kid:
            return RSAAlgorithm.from_jwk(json.dumps(key_data))

    # Kid rotated — try refreshing from network once if we used a file
    raise GoogleAuthError(
        'Google signing key not found in JWKS cache. '
        'Refresh data/google_jwks.json (keys rotate periodically).'
    )


def verify_google_id_token(token: str) -> dict:
    client_id = _client_id()
    if not client_id:
        raise GoogleAuthError('Google Sign-In is not configured on the server.')
    if not token or not isinstance(token, str):
        raise GoogleAuthError('Missing Google ID token.')

    try:
        jwks = load_google_jwks()
        try:
            public_key = _public_key_for_token(token, jwks)
        except GoogleAuthError:
            # Stale cache after Google key rotation — try live fetch once
            jwks = load_google_jwks(force_network=True)
            public_key = _public_key_for_token(token, jwks)

        payload = jwt.decode(
            token,
            public_key,
            algorithms=['RS256'],
            audience=client_id,
            issuer=list(GOOGLE_ISSUERS),
            options={'require': ['exp', 'iat', 'iss', 'aud', 'email']},
            leeway=30,
        )
    except GoogleAuthError:
        raise
    except jwt.ExpiredSignatureError as exc:
        raise GoogleAuthError('Google sign-in expired. Please try again.') from exc
    except jwt.InvalidAudienceError as exc:
        logger.warning('Google audience mismatch for configured client id')
        raise GoogleAuthError(
            'Google Client ID on the server does not match this app. '
            'Check GOOGLE_CLIENT_ID in .env.'
        ) from exc
    except jwt.InvalidIssuerError as exc:
        raise GoogleAuthError('Invalid Google token issuer.') from exc
    except jwt.InvalidTokenError as exc:
        logger.warning('Invalid Google JWT: %s', exc)
        raise GoogleAuthError('Invalid Google ID token.') from exc
    except Exception as exc:
        logger.exception('Unexpected Google token verification failure')
        raise GoogleAuthError(
            f'Could not verify Google sign-in ({type(exc).__name__}: {exc})'
        ) from exc

    email = (payload.get('email') or '').strip()
    if not email:
        raise GoogleAuthError('Google account has no email.')

    email_verified = payload.get('email_verified', False)
    if email_verified in (False, 'false', 'False', 0, '0'):
        raise GoogleAuthError('Google email is not verified.')

    return payload


def get_or_create_user_from_google(payload: dict):
    email = payload['email'].strip().lower()
    first_name = (payload.get('given_name') or '').strip() or email.split('@')[0]
    last_name = (payload.get('family_name') or '').strip() or '-'

    first_name = first_name[:200]
    last_name = last_name[:200]

    user = User.objects.filter(email__iexact=email).first()
    if user is not None:
        if not user.is_active:
            raise GoogleAuthError('This account is disabled.')
        updated_fields = []
        if not user.first_name and first_name:
            user.first_name = first_name
            updated_fields.append('first_name')
        if (not user.last_name or user.last_name == '-') and last_name != '-':
            user.last_name = last_name
            updated_fields.append('last_name')
        if updated_fields:
            user.save(update_fields=updated_fields)
        return user, False

    try:
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_staff=False,
            is_superuser=False,
            is_active=True,
        )
        user.set_unusable_password()
        user.save()
    except Exception as exc:
        logger.exception('Failed creating user from Google payload for %s', email)
        user = User.objects.filter(email__iexact=email).first()
        if user is None:
            raise GoogleAuthError('Could not create account from Google.') from exc
        return user, False

    return user, True
