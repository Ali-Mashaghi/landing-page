import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token


logger = logging.getLogger(__name__)
User = get_user_model()


class GoogleAuthError(Exception):
    """Raised when Google ID token verification or user provisioning fails."""


def verify_google_id_token(token: str) -> dict:
    client_id = (getattr(settings, 'GOOGLE_CLIENT_ID', '') or '').strip()
    if not client_id:
        raise GoogleAuthError('Google Sign-In is not configured on the server.')
    if not token:
        raise GoogleAuthError('Missing Google ID token.')

    try:
        payload = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            audience=client_id,
            clock_skew_in_seconds=10,
        )
    except ValueError as exc:
        logger.warning('Google ID token rejected: %s', exc)
        raise GoogleAuthError('Invalid or expired Google ID token.') from exc
    except Exception as exc:
        logger.exception('Google ID token verification failed')
        raise GoogleAuthError(
            'Could not verify Google sign-in. Please try again.'
        ) from exc

    issuer = payload.get('iss')
    if issuer not in ('accounts.google.com', 'https://accounts.google.com'):
        raise GoogleAuthError('Invalid token issuer.')

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

    # Cap lengths to model field limits
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
            # auto_now fields should not be listed in update_fields on all Django versions
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
        # Race: another request created the same email
        user = User.objects.filter(email__iexact=email).first()
        if user is None:
            raise GoogleAuthError('Could not create account from Google.') from exc
        return user, False

    return user, True
