"""
Upload local media files to Cloudinary so existing database image paths resolve.

django-cloudinary-storage generates URLs like:
    https://res.cloudinary.com/<cloud>/image/upload/v1/media/products/name.png
which means the Cloudinary public_id must be `media/products/name` (the file
extension in the URL is just the delivery format). This command uploads every
file under MEDIA_ROOT to that exact public_id, so image fields that already
hold paths like `products/name.png` start working without any DB changes.

Usage: python manage.py sync_to_cloudinary [--dry-run]
"""
import os
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}


class Command(BaseCommand):
    help = 'Upload local media files to Cloudinary under the public IDs the storage backend expects'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be uploaded without actually uploading'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        if not os.getenv('CLOUDINARY_URL'):
            self.stderr.write(self.style.ERROR(
                'CLOUDINARY_URL environment variable not set.\n'
                'Format: cloudinary://API_KEY:API_SECRET@CLOUD_NAME'
            ))
            return

        import cloudinary
        import cloudinary.uploader

        media_root = Path(settings.MEDIA_ROOT)
        if not media_root.is_dir():
            self.stderr.write(self.style.ERROR(f'MEDIA_ROOT not found: {media_root}'))
            return

        uploaded = 0
        errors = 0
        for path in sorted(media_root.rglob('*')):
            if not path.is_file() or path.suffix.lower() not in IMAGE_EXTENSIONS:
                continue

            relative = path.relative_to(media_root)
            # public_id matches the storage backend's URL: media/<path without extension>
            public_id = f'media/{relative.parent}/{relative.stem}'.replace('\\', '/')

            if dry_run:
                self.stdout.write(f'  Would upload {relative} -> {public_id}')
                uploaded += 1
                continue

            try:
                cloudinary.uploader.upload(
                    str(path),
                    public_id=public_id,
                    overwrite=True,
                    unique_filename=False,
                    use_filename=False,
                    resource_type='image',
                    invalidate=True,
                )
                self.stdout.write(self.style.SUCCESS(f'  Uploaded {relative}'))
                uploaded += 1
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'  Error uploading {relative}: {e}'))
                errors += 1

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - no files were uploaded'))
        self.stdout.write(self.style.SUCCESS(f'Sync complete: {uploaded} uploaded, {errors} errors'))
