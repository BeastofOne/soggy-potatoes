"""
Management command to import sticker images from the Sort Later folder.
Usage: python manage.py import_stickers
"""
import os
import shutil
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from shop.models import Category, Product


class Command(BaseCommand):
    help = 'Import sticker images from the Sort Later folder'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source',
            type=str,
            default='/Users/jacobphillips/Desktop/Sort Later/soggypotatoes-site/Images/',
            help='Source directory containing sticker images'
        )
        parser.add_argument(
            '--price',
            type=float,
            default=3.99,
            help='Default price for stickers'
        )
        parser.add_argument(
            '--stock',
            type=int,
            default=100,
            help='Default stock quantity'
        )

    def handle(self, *args, **options):
        source_dir = options['source']
        default_price = Decimal(str(options['price']))
        default_stock = options['stock']

        if not os.path.exists(source_dir):
            self.stderr.write(self.style.ERROR(f'Source directory not found: {source_dir}'))
            return

        # Create categories based on sticker types
        categories = {
            'character_sheet': self._get_or_create_category(
                'Character Sheets',
                'Detailed character reference sheets'
            ),
            'duo': self._get_or_create_category(
                'Duo Stickers',
                'Stickers featuring two characters together'
            ),
            'single': self._get_or_create_category(
                'Single Character',
                'Individual character stickers'
            ),
        }

        # Get media products directory
        from django.conf import settings
        products_dir = os.path.join(settings.MEDIA_ROOT, 'products')
        os.makedirs(products_dir, exist_ok=True)

        # Process each image
        imported = 0
        skipped = 0

        for filename in os.listdir(source_dir):
            if filename.startswith('.'):
                continue

            if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                continue

            # Determine category based on filename
            name_lower = filename.lower()
            if 'character sheet' in name_lower:
                category = categories['character_sheet']
                # Adjust price for character sheets (more detailed)
                price = Decimal('5.99')
            elif ' and ' in name_lower:
                category = categories['duo']
                price = Decimal('4.99')
            else:
                category = categories['single']
                price = default_price

            # Create product name from filename
            name = os.path.splitext(filename)[0]
            # Clean up the name
            name = name.replace('_', ' ').replace('-', ' ')

            # Generate slug
            base_slug = slugify(name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            # Check if product already exists (by similar name)
            if Product.objects.filter(name__iexact=name).exists():
                self.stdout.write(f'Skipping (exists): {name}')
                skipped += 1
                continue

            # Copy image to media folder
            source_path = os.path.join(source_dir, filename)
            # Normalize filename for storage
            safe_filename = slugify(os.path.splitext(filename)[0]) + os.path.splitext(filename)[1].lower()
            dest_path = os.path.join(products_dir, safe_filename)

            shutil.copy2(source_path, dest_path)

            # Create product
            product = Product.objects.create(
                name=name,
                slug=slug,
                description=f"Adorable {name} sticker. Premium vinyl, waterproof, and durable. Perfect for laptops, water bottles, notebooks, and more!",
                price=price,
                category=category,
                stock=default_stock,
                is_active=True,
                is_featured=(imported < 6),  # First 6 products are featured
                image=f'products/{safe_filename}'
            )

            self.stdout.write(self.style.SUCCESS(f'Imported: {name} (${price})'))
            imported += 1

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Import complete! {imported} products imported, {skipped} skipped.'))

    def _get_or_create_category(self, name, description):
        """Get or create a category."""
        slug = slugify(name)
        category, created = Category.objects.get_or_create(
            slug=slug,
            defaults={
                'name': name,
                'description': description,
                'is_active': True,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created category: {name}'))
        return category
