import logging

import jwt
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from jwt import PyJWKClient


logger = logging.getLogger(__name__)
User = get_user_model()

GOOGLE_CERTS_URL = 'https://www.googleapis.com/oauth2/v3/certs'
GOOGLE_ISSUERS = {
    'accounts.google.com',
    'https://accounts.google.com',
}


class GoogleAuthError(Exception):
    """Raised when Google ID token verification or user provisioning fails."""


def _client_id() -> str:
    return (getattr(settings, 'GOOGLE_CLIENT_ID', '') or '').strip().strip('"').strip("'")


def verify_google_id_token(token: str) -> dict:
    client_id = _client_id()
    if not client_id:
        raise GoogleAuthError('Google Sign-In is not configured on the server.')
    if not token or not isinstance(token, str):
        raise GoogleAuthError('Missing Google ID token.')

    try:
        jwks_client = PyJWKClient(GOOGLE_CERTS_URL, cache_keys=True, lifespan=3600)
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=['RS256'],
            audience=client_id,
            issuer=list(GOOGLE_ISSUERS),
            options={
                'require': ['exp', 'iat', 'iss', 'aud', 'email'],
            },
            leeway=30,
        )
    except jwt.ExpiredSignatureError as exc:
        raise GoogleAuthError('Google sign-in expired. Please try again.') from exc
    except jwt.InvalidAudienceError as exc:
        logger.warning(
            'Google audience mismatch. Expected client_id=%r',
            client_id[:20] + '...',
        )
        raise GoogleAuthError(
            'Google Client ID on the server does not match this app. '
            'Check GOOGLE_CLIENT_ID in .env.'
        ) from exc
    except jwt.InvalidIssuerError as exc:
        raise GoogleAuthError('Invalid Google token issuer.') from exc
    except jwt.PyJWKClientConnectionError as exc:
        logger.exception('Cannot download Google JWKS from %s', GOOGLE_CERTS_URL)
        raise GoogleAuthError(
            'Server cannot reach Google (certs). '
            'Outbound HTTPS to googleapis.com is blocked or timed out.'
        ) from exc
    except jwt.PyJWKClientError as exc:
        logger.exception('Google JWKS/client error')
        raise GoogleAuthError(
            f'Could not load Google signing keys: {exc}'
        ) from exc
    except jwt.InvalidTokenError as exc:
        logger.warning('Invalid Google JWT: %s', exc)
        raise GoogleAuthError('Invalid Google ID token.') from exc
    except requests.RequestException as exc:
        logger.exception('Network error verifying Google token')
        raise GoogleAuthError(
            'Server cannot reach Google to verify sign-in. '
            'Check VPS outbound network / firewall.'
        ) from exc
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
