"""
Django management command to scrape beer data from RateBeer for existing breweries.

Usage:
    python manage.py scrape_ratebeer_beers --brewery "Dark Star" --limit 10
    python manage.py scrape_ratebeer_beers --all --limit 5 --dry-run
"""

import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from slugify import slugify
from pathlib import Path
from tqdm import tqdm

from reviews.models import Category, Brewery, Beer
from reviews.scrapers.platform_scrapers.ratebeer_scraper import RateBeerScraper, RATEBEER_AVAILABLE
from reviews.scrapers.utils.normalizers import STYLE_TO_CATEGORY, DEFAULT_CATEGORY


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ratebeer_scraper.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('ratebeer_scraper')


class Command(BaseCommand):
    help = 'Scrape beer data from RateBeer for existing breweries'

    def add_arguments(self, parser):
        parser.add_argument(
            '--brewery',
            type=str,
            help='Scrape beers for specific brewery name'
        )

        parser.add_argument(
            '--all',
            action='store_true',
            help='Scrape beers for all breweries in database'
        )

        parser.add_argument(
            '--limit',
            type=int,
            default=20,
            help='Maximum number of beers per brewery (default: 20)'
        )

        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview what would be scraped without database changes'
        )

        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose logging'
        )

    def handle(self, *args, **options):
        if not RATEBEER_AVAILABLE:
            self.stdout.write(
                self.style.ERROR('RateBeer library not installed. Install with: pip install ratebeer')
            )
            return

        self.dry_run = options['dry_run']
        self.limit = options['limit']
        self.verbose = options['verbose']

        if self.verbose:
            logger.setLevel(logging.DEBUG)

        if self.dry_run:
            self.stdout.write(self.style.WARNING("\n=== DRY RUN MODE - No changes will be saved ===\n"))

        # Create logs directory
        Path('logs').mkdir(exist_ok=True)

        # Get breweries to scrape
        if options['brewery']:
            breweries = Brewery.objects.filter(name__icontains=options['brewery'])
            if not breweries.exists():
                self.stdout.write(
                    self.style.ERROR(f'No brewery found matching: {options["brewery"]}')
                )
                return
        elif options['all']:
            breweries = Brewery.objects.all()
        else:
            self.stdout.write(
                self.style.ERROR('Please specify --brewery or --all')
            )
            return

        self.stdout.write(f'\nFound {breweries.count()} breweries to scrape\n')

        # Initialize RateBeer scraper
        try:
            scraper = RateBeerScraper()
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to initialize RateBeer scraper: {e}')
            )
            return

        total_beers_created = 0
        total_beers_skipped = 0

        # Scrape each brewery
        for brewery in tqdm(breweries, desc="Processing breweries"):
            self.stdout.write(f'\n{"-" * 60}')
            self.stdout.write(f'Brewery: {brewery.name}')
            self.stdout.write(f'{"-" * 60}')

            # Fetch beers from RateBeer
            try:
                beer_data_list = scraper.fetch_beers(
                    brewery_name=brewery.name,
                    limit=self.limit
                )
            except Exception as e:
                logger.error(f'Error fetching beers for {brewery.name}: {e}')
                self.stdout.write(
                    self.style.ERROR(f'  Failed to fetch beers: {e}')
                )
                continue

            if not beer_data_list:
                self.stdout.write(
                    self.style.WARNING(f'  No beers found on RateBeer')
                )
                continue

            self.stdout.write(f'  Found {len(beer_data_list)} beers on RateBeer')

            # Create beers in database
            for beer_data in beer_data_list:
                created = self._create_beer(brewery, beer_data)
                if created:
                    total_beers_created += 1
                else:
                    total_beers_skipped += 1

        # Print summary
        self.stdout.write(f'\n{"=" * 60}')
        self.stdout.write(self.style.SUCCESS('Summary'))
        self.stdout.write('=' * 60)
        self.stdout.write(f'  Beers created: {total_beers_created}')
        self.stdout.write(f'  Beers skipped (already exist): {total_beers_skipped}')
        self.stdout.write('=' * 60 + '\n')

        if self.dry_run:
            self.stdout.write(self.style.WARNING("\n=== DRY RUN COMPLETE - No changes were saved ===\n"))
        else:
            self.stdout.write(self.style.SUCCESS("\n=== SCRAPING COMPLETE ===\n"))

        scraper.close()

    def _create_beer(self, brewery, beer_data):
        """Create a beer in the database."""
        if self.dry_run:
            self.stdout.write(f'    [DRY RUN] Would create: {beer_data["name"]}')
            return True

        try:
            # Check if beer already exists
            existing = Beer.objects.filter(
                name__iexact=beer_data['name'],
                brewery=brewery
            ).first()

            if existing:
                logger.debug(f'Beer already exists: {beer_data["name"]}')
                return False

            # Get or create category
            category_name = beer_data.get('category', DEFAULT_CATEGORY)
            category, _ = Category.objects.get_or_create(
                name=category_name,
                defaults={
                    'slug': slugify(category_name),
                    'description': f'{category_name} beers'
                }
            )

            # Create beer
            beer = Beer.objects.create(
                name=beer_data['name'],
                slug=slugify(beer_data['name']),
                brewery=brewery,
                category=category,
                description=beer_data.get('description', ''),
                abv=beer_data.get('abv'),
                ibu=beer_data.get('ibu'),
            )

            logger.info(f'Created beer: {beer.name} ({brewery.name})')
            self.stdout.write(
                self.style.SUCCESS(f'    [+] Created: {beer.name}')
            )
            return True

        except Exception as e:
            logger.error(f'Error creating beer {beer_data["name"]}: {e}')
            self.stdout.write(
                self.style.ERROR(f'    [!] Failed: {beer_data["name"]} - {e}')
            )
            return False
