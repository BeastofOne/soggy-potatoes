"""
Management command to upload existing local media files to Cloudinary.
Usage: python manage.py sync_to_cloudinary
"""
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from shop.models import Product, Category
from users.models import UserProfile


class Command(BaseCommand):
    help = 'Upload existing local media files to Cloudinary'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be uploaded without actually uploading'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        # Check if Cloudinary is configured
        if not os.getenv('CLOUDINARY_URL'):
            self.stderr.write(self.style.ERROR(
                'CLOUDINARY_URL environment variable not set.\n'
                'Please set it before running this command.\n'
                'Format: cloudinary://API_KEY:API_SECRET@CLOUD_NAME'
            ))
            return

        import cloudinary
        import cloudinary.uploader

        self.stdout.write('Starting media sync to Cloudinary...\n')

        # Sync product images
        products = Product.objects.all()
        product_count = 0
        product_errors = 0

        self.stdout.write(f'Found {products.count()} products to sync...')

        for product in products:
            if not product.image:
                continue

            # Check if it's already a Cloudinary URL
            if hasattr(product.image, 'url') and 'cloudinary' in str(product.image.url):
                self.stdout.write(f'  Skipping (already on Cloudinary): {product.name}')
                continue

            # Get local file path
            local_path = os.path.join(settings.MEDIA_ROOT, str(product.image))

            if not os.path.exists(local_path):
                self.stderr.write(self.style.WARNING(f'  File not found: {local_path}'))
                product_errors += 1
                continue

            if dry_run:
                self.stdout.write(f'  Would upload: {product.name} ({local_path})')
                product_count += 1
                continue

            try:
                # Upload to Cloudinary
                result = cloudinary.uploader.upload(
                    local_path,
                    folder='soggy_potatoes/products',
                    public_id=f'product_{product.pk}',
                    overwrite=True,
                    resource_type='image'
                )

                # Update product image field with Cloudinary URL
                # The django-cloudinary-storage handles this automatically
                # but we need to re-save with the new path
                product.image = result['public_id']
                product.save(update_fields=['image'])

                self.stdout.write(self.style.SUCCESS(f'  Uploaded: {product.name}'))
                product_count += 1

            except Exception as e:
                self.stderr.write(self.style.ERROR(f'  Error uploading {product.name}: {e}'))
                product_errors += 1

        # Sync category images
        categories = Category.objects.exclude(image='').exclude(image__isnull=True)
        cat_count = 0

        for category in categories:
            if not category.image:
                continue

            local_path = os.path.join(settings.MEDIA_ROOT, str(category.image))

            if not os.path.exists(local_path):
                continue

            if dry_run:
                self.stdout.write(f'  Would upload category: {category.name}')
                cat_count += 1
                continue

            try:
                result = cloudinary.uploader.upload(
                    local_path,
                    folder='soggy_potatoes/categories',
                    public_id=f'category_{category.pk}',
                    overwrite=True,
                    resource_type='image'
                )
                category.image = result['public_id']
                category.save(update_fields=['image'])
                self.stdout.write(self.style.SUCCESS(f'  Uploaded category: {category.name}'))
                cat_count += 1
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'  Error: {e}'))

        # Sync user avatars
        profiles = UserProfile.objects.exclude(avatar='').exclude(avatar__isnull=True)
        avatar_count = 0

        for profile in profiles:
            if not profile.avatar:
                continue

            local_path = os.path.join(settings.MEDIA_ROOT, str(profile.avatar))

            if not os.path.exists(local_path):
                continue

            if dry_run:
                self.stdout.write(f'  Would upload avatar: {profile.user.username}')
                avatar_count += 1
                continue

            try:
                result = cloudinary.uploader.upload(
                    local_path,
                    folder='soggy_potatoes/avatars',
                    public_id=f'avatar_{profile.user.pk}',
                    overwrite=True,
                    resource_type='image'
                )
                profile.avatar = result['public_id']
                profile.save(update_fields=['avatar'])
                self.stdout.write(self.style.SUCCESS(f'  Uploaded avatar: {profile.user.username}'))
                avatar_count += 1
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'  Error: {e}'))

        # Summary
        self.stdout.write('')
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No files were actually uploaded'))
        self.stdout.write(self.style.SUCCESS(
            f'Sync complete!\n'
            f'  Products: {product_count} uploaded, {product_errors} errors\n'
            f'  Categories: {cat_count} uploaded\n'
            f'  Avatars: {avatar_count} uploaded'
        ))
