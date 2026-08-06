from django.core.management.base import BaseCommand, CommandError

from hero.services.google_auth import GoogleAuthError, load_google_jwks


class Command(BaseCommand):
    help = (
        'Download Google OAuth JWKS (signing certs) for offline / blocked-VPS verify. '
        'Run this on a machine that can reach googleapis.com, then copy the file to the VPS.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Fetch from network even if a local JWKS file already exists.',
        )

    def handle(self, *args, **options):
        try:
            jwks = load_google_jwks(force_network=True)
        except GoogleAuthError as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(self.style.SUCCESS(
            f'Fetched {len(jwks.get("keys", []))} Google signing keys.'
        ))
        self.stdout.write(
            'If GOOGLE_JWKS_PATH is set, the file was updated. '
            'Copy it to your VPS if you ran this command locally.'
        )
