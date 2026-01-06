"""
Django management command to scrape British beer data.

Usage:
    python manage.py scrape_british_beers --sources all --dry-run
    python manage.py scrape_british_beers --sources openbrewerydb --max-breweries 10
"""

import logging
import time
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction
from pathlib import Path
from tqdm import tqdm
from slugify import slugify

from reviews.models import Category, Brewery, Beer
from reviews.scrapers.api_scrapers.openbrewerydb import OpenBreweryDBScraper
from reviews.scrapers.utils.normalizers import STYLE_TO_CATEGORY, DEFAULT_CATEGORY


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scraper.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('beer_scraper')


class Command(BaseCommand):
    help = 'Scrape British beer data from multiple sources'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sources',
            nargs='+',
            default=['openbrewerydb'],
            choices=['all', 'openbrewerydb'],
            help='Data sources to scrape'
        )

        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview what would be scraped without database changes'
        )

        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Delete all existing beers, breweries, categories before scraping'
        )

        parser.add_argument(
            '--max-breweries',
            type=int,
            default=None,
            help='Limit number of breweries to scrape'
        )

        parser.add_argument(
            '--skip-images',
            action='store_true',
            help='Skip downloading images'
        )

        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose logging'
        )

    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        self.clear_existing = options['clear_existing']
        self.max_breweries = options['max_breweries']
        self.skip_images = options['skip_images']
        self.verbose = options['verbose']
        self.sources = options['sources']

        if self.verbose:
            logger.setLevel(logging.DEBUG)

        if self.dry_run:
            self.stdout.write(self.style.WARNING("\n=== DRY RUN MODE - No changes will be saved ===\n"))

        start_time = datetime.now()

        try:
            # Create logs directory
            Path('logs').mkdir(exist_ok=True)

            # Pre-flight checks
            self.stdout.write("Running pre-flight checks...")
            self._preflight_checks()

            # Clear existing data
            if self.clear_existing and not self.dry_run:
                self.stdout.write("Clearing existing data...")
                self._clear_existing_data()

            # Create categories
            self.stdout.write("Creating beer categories...")
            categories = self._create_categories()

            # Scrape breweries and beers
            if 'all' in self.sources or 'openbrewerydb' in self.sources:
                self.stdout.write("\nScraping from Open Brewery DB...")
                self._scrape_openbrewerydb(categories)

            # Summary
            duration = (datetime.now() - start_time).total_seconds()
            self._print_summary(duration)

            if self.dry_run:
                self.stdout.write(self.style.WARNING("\n=== DRY RUN COMPLETE - No changes were saved ===\n"))
            else:
                self.stdout.write(self.style.SUCCESS("\n=== SCRAPING COMPLETE ===\n"))

        except Exception as e:
            logger.error(f"Scraping failed: {e}", exc_info=True)
            self.stdout.write(self.style.ERROR(f"\nError: {e}"))
            raise

    def _preflight_checks(self):
        """Run pre-flight checks."""
        # Check media directory
        media_root = Path(settings.MEDIA_ROOT)
        if not media_root.exists():
            media_root.mkdir(parents=True)
            logger.info(f"Created media directory: {media_root}")

    def _clear_existing_data(self):
        """Delete all existing beers, breweries, and categories."""
        with transaction.atomic():
            beer_count = Beer.objects.count()
            brewery_count = Brewery.objects.count()
            category_count = Category.objects.count()

            Beer.objects.all().delete()
            Brewery.objects.all().delete()
            Category.objects.all().delete()

            self.stdout.write(self.style.WARNING(
                f"Deleted {beer_count} beers, {brewery_count} breweries, {category_count} categories"
            ))

    def _create_categories(self):
        """Create standard British beer categories."""
        categories_data = [
            ('Pale Ale', 'Light to medium-bodied ales with hoppy character'),
            ('IPA', 'India Pale Ales, hop-forward with higher ABV'),
            ('Bitter', 'Traditional British bitter ales'),
            ('Porter', 'Dark ales with roasted malt flavors'),
            ('Stout', 'Very dark, rich ales with coffee and chocolate notes'),
            ('Lager', 'Crisp, clean, bottom-fermented beers'),
            ('Wheat Beer', 'Beers brewed with a large proportion of wheat'),
            ('Golden Ale', 'Light, refreshing ales with golden color'),
            ('Amber Ale', 'Medium-bodied ales with caramel and toffee notes'),
            ('Brown Ale', 'Malty ales with nutty, caramel flavors'),
            ('Mild', 'Low-alcohol, malty traditional British ales'),
            ('Strong Ale', 'High-alcohol ales with complex flavors'),
        ]

        categories = {}

        for name, description in tqdm(categories_data, desc="Creating categories"):
            if not self.dry_run:
                category, created = Category.objects.get_or_create(
                    name=name,
                    defaults={
                        'slug': slugify(name),
                        'description': description,
                    }
                )
                categories[name] = category
                if created:
                    logger.info(f"Created category: {name}")
            else:
                self.stdout.write(f"Would create category: {name}")
                categories[name] = None

        return categories

    def _scrape_openbrewerydb(self, categories):
        """Scrape breweries from Open Brewery DB."""
        scraper = OpenBreweryDBScraper()

        try:
            # Fetch breweries
            self.stdout.write("Fetching UK breweries...")
            brewery_data = scraper.fetch_breweries(limit=self.max_breweries)

            self.stdout.write(f"Found {len(brewery_data)} breweries")

            # Create breweries
            breweries_created = 0

            for data in tqdm(brewery_data, desc="Creating breweries"):
                if not self.dry_run:
                    try:
                        brewery, created = Brewery.objects.get_or_create(
                            name=data['name'],
                            defaults={
                                'slug': slugify(data['name']),
                                'description': data.get('description', ''),
                                'location': data['location'],
                                'website': data.get('website', ''),
                            }
                        )
                        if created:
                            breweries_created += 1
                            logger.info(f"Created brewery: {data['name']}")
                    except Exception as e:
                        logger.error(f"Error creating brewery {data['name']}: {e}")
                else:
                    self.stdout.write(f"Would create brewery: {data['name']} ({data['location']})")

            self.stdout.write(self.style.SUCCESS(f"Created {breweries_created} breweries"))

            # Print stats
            stats = scraper.get_stats()
            self.stdout.write(f"\nOpen Brewery DB Stats:")
            self.stdout.write(f"  Requests made: {stats['requests_made']}")
            self.stdout.write(f"  Breweries scraped: {stats['breweries_scraped']}")

        finally:
            scraper.close()

    def _print_summary(self, duration):
        """Print scraping summary."""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("SCRAPING SUMMARY")
        self.stdout.write("=" * 50)

        self.stdout.write(f"Duration: {duration:.1f} seconds")

        if not self.dry_run:
            self.stdout.write(f"\nCategories: {Category.objects.count()}")
            self.stdout.write(f"Breweries: {Brewery.objects.count()}")
            self.stdout.write(f"Beers: {Beer.objects.count()}")
