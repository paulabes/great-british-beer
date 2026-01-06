"""
Django management command to run daily beer scraping.
Scrapes beers from brewery websites and updates the database.

Usage:
    python manage.py daily_beer_scrape
    python manage.py daily_beer_scrape --dry-run
"""

import logging
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import transaction
from slugify import slugify
from pathlib import Path

from reviews.models import Brewery, Beer, Category
from reviews.scrapers.brewery_scrapers.darkstar import DarkStarScraper
from reviews.scrapers.brewery_scrapers.harveys import HarveysScraper
from reviews.scrapers.brewery_scrapers.brighton_bier import BrightonBierScraper
from reviews.scrapers.brewery_scrapers.burning_sky import BurningSkyScraper
from reviews.scrapers.utils.normalizers import STYLE_TO_CATEGORY, DEFAULT_CATEGORY


# Set up logging
logger = logging.getLogger('daily_scraper')


class Command(BaseCommand):
    help = 'Daily automated beer scraping from brewery websites'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without saving to database'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        # Create logs directory
        Path('logs').mkdir(exist_ok=True)

        # Configure logging
        log_file = Path('logs') / f'daily_scrape_{datetime.now().strftime("%Y%m%d")}.log'
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.setLevel(logging.INFO)

        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.SUCCESS('Daily Beer Scraping - ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        self.stdout.write(self.style.SUCCESS('='*70 + '\n'))

        if dry_run:
            self.stdout.write(self.style.WARNING('[DRY RUN MODE]\n'))

        # Define breweries and their scrapers
        breweries = [
            ('Dark Star Brewing Co', DarkStarScraper),
            ('Harveys & Son', HarveysScraper),
            ('Brighton Bier', BrightonBierScraper),
            ('Burning Sky Brewery', BurningSkyScraper),
        ]

        total_added = 0
        total_errors = 0

        for brewery_name, scraper_class in breweries:
            try:
                added = self._scrape_brewery(brewery_name, scraper_class, dry_run)
                total_added += added
            except Exception as e:
                total_errors += 1
                logger.error(f'Error processing {brewery_name}: {e}', exc_info=True)
                self.stdout.write(
                    self.style.ERROR(f'  [!] Error: {brewery_name} - {e}')
                )

        # Print summary
        self.stdout.write(f'\n{"="*70}')
        self.stdout.write(self.style.SUCCESS('Summary'))
        self.stdout.write('='*70)
        self.stdout.write(f'  New beers added: {total_added}')
        self.stdout.write(f'  Errors: {total_errors}')
        self.stdout.write(f'  Total beers in database: {Beer.objects.count()}')
        self.stdout.write(f'  Total breweries: {Brewery.objects.count()}')
        self.stdout.write('='*70 + '\n')

        logger.info(f'Daily scrape complete: {total_added} beers added, {total_errors} errors')

    def _scrape_brewery(self, brewery_name, scraper_class, dry_run):
        """Scrape beers from a specific brewery."""
        self.stdout.write(f'\n{brewery_name}')
        self.stdout.write('-' * 70)

        # Get or create brewery
        brewery = Brewery.objects.filter(name=brewery_name).first()
        if not brewery and not dry_run:
            brewery = Brewery.objects.create(
                name=brewery_name,
                slug=slugify(brewery_name),
                location='United Kingdom',
                description=f'{brewery_name} - British Brewery'
            )
            logger.info(f'Created brewery: {brewery_name}')

        # Initialize scraper
        try:
            scraper = scraper_class()
            beers_data = scraper.fetch_beers()
            self.stdout.write(f'  Found {len(beers_data)} beers on website')
            logger.info(f'{brewery_name}: Found {len(beers_data)} beers')
        except Exception as e:
            logger.error(f'{brewery_name}: Scraping failed - {e}')
            self.stdout.write(
                self.style.WARNING(f'  [!] Could not scrape: {e}')
            )
            return 0

        if not beers_data:
            return 0

        # Process beers
        beers_added = 0
        for beer_data in beers_data:
            beer_name = beer_data.get('name', '').strip()
            if not beer_name:
                continue

            # Skip if already exists
            if brewery and Beer.objects.filter(name__iexact=beer_name, brewery=brewery).exists():
                continue

            if dry_run:
                self.stdout.write(f'    [DRY RUN] Would add: {beer_name}')
                beers_added += 1
                continue

            # Add beer
            try:
                # Get category
                style = beer_data.get('style', 'Ale')
                category_name = STYLE_TO_CATEGORY.get(style.lower(), DEFAULT_CATEGORY)
                category, _ = Category.objects.get_or_create(
                    name=category_name,
                    defaults={
                        'slug': slugify(category_name),
                        'description': f'{category_name} beers'
                    }
                )

                # Handle ABV
                abv = beer_data.get('abv')
                if abv is None or abv == '':
                    abv = 5.0

                # Handle IBU
                ibu = beer_data.get('ibu')
                if ibu == '':
                    ibu = None

                # Create beer
                beer = Beer.objects.create(
                    name=beer_name,
                    slug=slugify(beer_name),
                    brewery=brewery,
                    category=category,
                    description=beer_data.get('description', '')[:500],
                    abv=abv,
                    ibu=ibu,
                )

                self.stdout.write(
                    self.style.SUCCESS(f'    [+] Added: {beer_name}')
                )
                logger.info(f'Added beer: {beer_name} ({brewery_name})')
                beers_added += 1

            except Exception as e:
                logger.error(f'Error adding beer {beer_name}: {e}')
                self.stdout.write(
                    self.style.ERROR(f'    [!] Failed to add: {beer_name}')
                )

        return beers_added
