#!/usr/bin/env python
"""
Quick script to scrape beers from brewery websites and add them to the database.
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greatbritishbeer.settings')
django.setup()

from reviews.models import Brewery, Beer, Category
from reviews.scrapers.brewery_scrapers.darkstar import DarkStarScraper
from reviews.scrapers.brewery_scrapers.harveys import HarveysScraper
from reviews.scrapers.brewery_scrapers.brighton_bier import BrightonBierScraper
from reviews.scrapers.brewery_scrapers.burning_sky import BurningSkyScraper
from reviews.scrapers.utils.normalizers import STYLE_TO_CATEGORY, DEFAULT_CATEGORY
from slugify import slugify


def add_beers_from_scraper(brewery_name, scraper_class):
    """Add beers from a brewery scraper."""
    print(f'\n{"=" * 60}')
    print(f'Processing: {brewery_name}')
    print("=" * 60)

    # Check if brewery exists
    brewery = Brewery.objects.filter(name=brewery_name).first()
    if not brewery:
        print(f'  Brewery not found in database, creating...')
        brewery = Brewery.objects.create(
            name=brewery_name,
            slug=slugify(brewery_name),
            location='United Kingdom',
            description=f'{brewery_name} brewery'
        )

    # Initialize scraper
    try:
        scraper = scraper_class()
        beers_data = scraper.fetch_beers()
        print(f'  Found {len(beers_data)} beers on website')
    except Exception as e:
        print(f'  Error scraping: {e}')
        return 0

    # Add beers
    beers_added = 0
    for beer_data in beers_data:
        beer_name = beer_data.get('name', '').strip()
        if not beer_name:
            continue

        # Check if exists
        if Beer.objects.filter(name__iexact=beer_name, brewery=brewery).exists():
            print(f'    [-] Already exists: {beer_name}')
            continue

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

        # Create beer
        abv = beer_data.get('abv')
        if abv is None or abv == '':
            abv = 5.0  # Default ABV if not provided

        ibu = beer_data.get('ibu')
        if ibu == '':
            ibu = None

        beer = Beer.objects.create(
            name=beer_name,
            slug=slugify(beer_name),
            brewery=brewery,
            category=category,
            description=beer_data.get('description', '')[:500],
            abv=abv,
            ibu=ibu,
        )
        print(f'    [+] Added: {beer_name}')
        beers_added += 1

    return beers_added


def main():
    print('\nScraping beers from brewery websites...\n')

    breweries = [
        ('Dark Star Brewing Co', DarkStarScraper),
        ('Harveys & Son', HarveysScraper),
        ('Brighton Bier', BrightonBierScraper),
        ('Burning Sky Brewery', BurningSkyScraper),
    ]

    total_added = 0
    for brewery_name, scraper_class in breweries:
        added = add_beers_from_scraper(brewery_name, scraper_class)
        total_added += added

    print(f'\n{"=" * 60}')
    print(f'Total beers added: {total_added}')
    print(f'Total beers in database: {Beer.objects.count()}')
    print("=" * 60)


if __name__ == '__main__':
    main()
