"""
Management command to scrape real beer images from brewery websites.
"""

import os
import logging
from typing import Dict, List
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.db.models import Q
import requests
from PIL import Image
from io import BytesIO

from reviews.models import Beer, Brewery
from reviews.scrapers.brewery_scrapers.darkstar import DarkStarScraper
from reviews.scrapers.brewery_scrapers.harveys import HarveysScraper
from reviews.scrapers.brewery_scrapers.brighton_bier import BrightonBierScraper
from reviews.scrapers.brewery_scrapers.burning_sky import BurningSkyScraper


logger = logging.getLogger('beer_scraper')


class Command(BaseCommand):
    help = 'Scrape real beer images from brewery websites'

    def add_arguments(self, parser):
        parser.add_argument(
            '--brewery',
            type=str,
            help='Scrape only a specific brewery (e.g., "Dark Star Brewing Co")'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without saving images'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Verbose output'
        )

    def handle(self, *args, **options):
        if options['verbose']:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)

        dry_run = options['dry_run']
        specific_brewery = options.get('brewery')

        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('Scraping Beer Images from Brewery Websites'))
        self.stdout.write(self.style.SUCCESS('='*60 + '\n'))

        if dry_run:
            self.stdout.write(self.style.WARNING('[!] DRY RUN - No images will be saved\n'))

        # Initialize scrapers
        scrapers = {
            'Dark Star Brewing Co': DarkStarScraper(),
            'Harveys & Son': HarveysScraper(),
            'Brighton Bier': BrightonBierScraper(),
            'Burning Sky Brewery': BurningSkyScraper(),
        }

        # Filter to specific brewery if requested
        if specific_brewery:
            if specific_brewery in scrapers:
                scrapers = {specific_brewery: scrapers[specific_brewery]}
            else:
                self.stdout.write(
                    self.style.ERROR(f'[!] Brewery "{specific_brewery}" not found')
                )
                self.stdout.write(f'Available breweries: {", ".join(scrapers.keys())}')
                return

        total_updated = 0
        total_failed = 0
        total_not_found = 0

        # Process each brewery
        for brewery_name, scraper in scrapers.items():
            self.stdout.write(f'\n{brewery_name}')
            self.stdout.write('-' * 60)

            # Check if brewery exists in database
            brewery = Brewery.objects.filter(name=brewery_name).first()
            if not brewery:
                self.stdout.write(
                    self.style.WARNING(f'  [!] Brewery not found in database: {brewery_name}')
                )
                continue

            # Get beers for this brewery
            beers = Beer.objects.filter(brewery=brewery)
            if not beers.exists():
                self.stdout.write(
                    self.style.WARNING(f'  [!] No beers found for brewery: {brewery_name}')
                )
                continue

            self.stdout.write(f'  Found {beers.count()} beers in database')

            # Scrape beers from website
            try:
                scraped_beers = scraper.fetch_beers()
                self.stdout.write(f'  Scraped {len(scraped_beers)} beers from website')
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  [!] Error scraping brewery: {e}')
                )
                logger.exception(f'Error scraping {brewery_name}')
                continue

            # Match scraped beers with database beers
            updated, failed, not_found = self._match_and_update_images(
                beers, scraped_beers, dry_run
            )

            total_updated += updated
            total_failed += failed
            total_not_found += not_found

        # Print summary
        self.stdout.write(f'\n{"="*60}')
        self.stdout.write(self.style.SUCCESS('Summary'))
        self.stdout.write('='*60)
        self.stdout.write(f'  [+] Images updated: {total_updated}')
        self.stdout.write(f'  [!] Failed downloads: {total_failed}')
        self.stdout.write(f'  [-] Not found on website: {total_not_found}')
        self.stdout.write('='*60 + '\n')

    def _match_and_update_images(self, db_beers, scraped_beers: List[Dict],
                                  dry_run: bool) -> tuple:
        """
        Match database beers with scraped beers and update images.

        Returns:
            Tuple of (updated_count, failed_count, not_found_count)
        """
        updated = 0
        failed = 0
        not_found = 0

        # Create lookup dictionary from scraped beers
        scraped_lookup = {}
        for beer_data in scraped_beers:
            beer_name = beer_data.get('name', '').lower().strip()
            if beer_name and beer_data.get('image_url'):
                scraped_lookup[beer_name] = beer_data

        # Match each database beer
        for db_beer in db_beers:
            beer_name_lower = db_beer.name.lower().strip()

            # Try exact match first
            scraped_data = scraped_lookup.get(beer_name_lower)

            # Try partial match if exact match fails
            if not scraped_data:
                for scraped_name, data in scraped_lookup.items():
                    if scraped_name in beer_name_lower or beer_name_lower in scraped_name:
                        scraped_data = data
                        break

            if not scraped_data:
                self.stdout.write(f'    [-] Not found: {db_beer.name}')
                not_found += 1
                continue

            image_url = scraped_data.get('image_url')
            if not image_url:
                self.stdout.write(f'    [-] No image URL: {db_beer.name}')
                not_found += 1
                continue

            # Download and save image
            if dry_run:
                self.stdout.write(f'    [DRY RUN] Would update: {db_beer.name}')
                updated += 1
            else:
                success = self._download_and_save_image(image_url, db_beer)
                if success:
                    self.stdout.write(
                        self.style.SUCCESS(f'    [+] Updated: {db_beer.name}')
                    )
                    updated += 1
                else:
                    self.stdout.write(
                        self.style.ERROR(f'    [!] Failed: {db_beer.name}')
                    )
                    failed += 1

        return updated, failed, not_found

    def _download_and_save_image(self, url: str, beer) -> bool:
        """
        Download image from URL and save to beer model.

        Args:
            url: Image URL
            beer: Beer model instance

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.debug(f'Downloading image: {url}')

            response = requests.get(url, timeout=30)
            response.raise_for_status()

            # Open with PIL
            img = Image.open(BytesIO(response.content))

            # Convert to RGB if needed
            if img.mode in ('RGBA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[3])
                else:
                    background.paste(img)
                img = background

            # Resize to 600x600
            img.thumbnail((600, 600), Image.Resampling.LANCZOS)

            # Save to BytesIO
            output = BytesIO()
            img.save(output, format='JPEG', quality=85)
            output.seek(0)

            # Save to model
            filename = f"{beer.slug}.jpg"
            beer.image.save(filename, ContentFile(output.read()), save=True)

            return True

        except Exception as e:
            logger.error(f'Error downloading image for {beer.name}: {e}')
            return False
