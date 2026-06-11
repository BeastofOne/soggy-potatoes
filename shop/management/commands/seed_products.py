from django.core.management import call_command
from django.core.management.base import BaseCommand

from shop.models import Product


class Command(BaseCommand):
    help = (
        "Load fixtures/products_seed.json only if no products exist yet. "
        "Safe to run on every deploy; never overwrites live product edits."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Load the fixture even if products already exist (overwrites matching IDs).',
        )

    def handle(self, *args, **options):
        if Product.objects.exists() and not options['force']:
            self.stdout.write(
                self.style.NOTICE(
                    f'Skipping seed: {Product.objects.count()} products already in database. '
                    'Use --force to load the fixture anyway.'
                )
            )
            return

        call_command('loaddata', 'fixtures/products_seed.json')
        self.stdout.write(self.style.SUCCESS('Product fixture loaded.'))
