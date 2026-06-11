"""
One-time admin account recovery, driven entirely by environment variables.

Render's free tier has no shell, so this runs as a build step (see build.sh).
It does nothing unless BOTH env vars are set:

    ADMIN_RESET_USERNAME  - account to reset (created as superuser if missing)
    ADMIN_RESET_PASSWORD  - the new password
    ADMIN_RESET_EMAIL     - optional, only used when creating a new account

After logging in, REMOVE these env vars from Render so the password stops
being reapplied on every deploy.
"""
import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Reset or create a superuser from ADMIN_RESET_USERNAME/ADMIN_RESET_PASSWORD env vars'

    def handle(self, *args, **options):
        username = os.getenv('ADMIN_RESET_USERNAME', '').strip()
        password = os.getenv('ADMIN_RESET_PASSWORD', '')

        if not username or not password:
            self.stdout.write('reset_admin_password: env vars not set, skipping.')
            return

        if len(password) < 8:
            self.stderr.write(self.style.ERROR(
                'reset_admin_password: ADMIN_RESET_PASSWORD must be at least 8 characters. Skipping.'
            ))
            return

        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': os.getenv('ADMIN_RESET_EMAIL', '')},
        )
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()

        action = 'created' if created else 'password reset'
        self.stdout.write(self.style.SUCCESS(
            f'reset_admin_password: superuser "{username}" {action}. '
            'Remove the ADMIN_RESET_* env vars after logging in!'
        ))
