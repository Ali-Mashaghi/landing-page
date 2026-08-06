from django.conf import settings
from django.contrib.auth import get_user_model
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token


User = get_user_model()


class GoogleAuthError(Exception):
    """Raised when Google ID token verification or user provisioning fails."""


def verify_google_id_token(token: str) -> dict:
    client_id = getattr(settings, 'GOOGLE_CLIENT_ID', '') or ''
    if not client_id:
        raise GoogleAuthError('Google Sign-In is not configured.')
    if not token:
        raise GoogleAuthError('Missing Google ID token.')

    try:
        payload = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            client_id,
        )
    except ValueError as exc:
        raise GoogleAuthError('Invalid Google ID token.') from exc

    if payload.get('iss') not in ('accounts.google.com', 'https://accounts.google.com'):
        raise GoogleAuthError('Invalid token issuer.')
    if not payload.get('email'):
        raise GoogleAuthError('Google account has no email.')
    if not payload.get('email_verified', False):
        raise GoogleAuthError('Google email is not verified.')

    return payload


def get_or_create_user_from_google(payload: dict):
    email = payload['email'].strip().lower()
    first_name = (payload.get('given_name') or '').strip() or email.split('@')[0]
    last_name = (payload.get('family_name') or '').strip() or '-'

    user = User.objects.filter(email__iexact=email).first()
    if user is not None:
        if not user.is_active:
            raise GoogleAuthError('This account is disabled.')
        updated_fields = []
        if not user.first_name and first_name:
            user.first_name = first_name
            updated_fields.append('first_name')
        if (not user.last_name or user.last_name == '-') and last_name and last_name != '-':
            user.last_name = last_name
            updated_fields.append('last_name')
        if updated_fields:
            user.save(update_fields=updated_fields + ['updated_date'])
        return user, False

    user = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
        is_staff=False,
        is_active=True,
    )
    user.set_unusable_password()
    user.save()
    return user, True
