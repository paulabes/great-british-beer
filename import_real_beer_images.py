#!/usr/bin/env python
"""
Import actual product/marketing images for UK beers.

This script searches for real beer images from multiple sources:
1. Brewery websites (direct product images)
2. Google Images (specific beer + brewery searches)
3. Untappd (beer database with official images)

Requires: google-search-results (SerpApi) for Google Images
Install: pip install google-search-results
"""

import os
import django
import requests
import time
from io import BytesIO
from PIL import Image
from urllib.parse import quote_plus

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greatbritishbeer.settings')
django.setup()

from reviews.models import Beer
from django.core.files.base import ContentFile


# Brewery-specific image search URLs
BREWERY_WEBSITES = {
    'BrewDog': 'https://www.brewdog.com/uk/',
    'Timothy Taylor': 'https://www.timothytaylor.co.uk/',
    "Fuller's": 'https://www.fullers.co.uk/',
    'Adnams': 'https://www.adnams.co.uk/',
    'Black Sheep Brewery': 'https://www.blacksheepbrewery.com/',
    'St Austell Brewery': 'https://www.staustellbrewery.co.uk/',
    'Greene King': 'https://www.greeneking.co.uk/',
    'T&R Theakston': 'https://www.theakstons.co.uk/',
    "Marston's": 'https://www.marstons.co.uk/',
    "Wells & Young's": 'https://www.charleswells.co.uk/',
    'Beavertown Brewery': 'https://beavertownbrewery.co.uk/',
    'Thornbridge Brewery': 'https://thornbridgebrewery.co.uk/',
    'Wychwood Brewery': 'https://www.wychwoodbrewery.co.uk/',
    'Shepherd Neame': 'https://www.shepherdneame.co.uk/',
    'Hook Norton Brewery': 'https://www.hooky.co.uk/',
    'Wadworth': 'https://www.wadworth.co.uk/',
    'Meantime Brewing': 'https://www.meantimebrewing.com/',
    'Camden Town Brewery': 'https://www.camdentownbrewery.com/',
    'Wild Beer Co': 'https://wildbeerco.com/',
    'Oakham Ales': 'https://www.oakhamales.com/',
}


def search_google_images(beer_name, brewery_name):
    """
    Search Google Images for specific beer.

    Note: This is a manual approach - you'll need to:
    1. Search Google Images for "{beer_name} {brewery_name} beer bottle"
    2. Copy the first product image URL
    3. Add it to a CSV or JSON file

    For automated approach, you can use:
    - SerpApi (paid, $50/month)
    - Custom Scrapy spider
    - Selenium automation
    """
    search_query = f"{beer_name} {brewery_name} beer bottle label"
    google_url = f"https://www.google.com/search?q={quote_plus(search_query)}&tbm=isch"

    print(f"    Manual search needed: {google_url}")
    return None


def search_untappd(beer_name, brewery_name):
    """
    Search Untappd for beer image.

    Untappd has official beer images but requires scraping or API access.
    Free tier allows limited searches.
    """
    # Untappd search URL (manual for now)
    search_query = f"{beer_name} {brewery_name}"
    untappd_url = f"https://untappd.com/search?q={quote_plus(search_query)}&type=beer"

    print(f"    Check Untappd: {untappd_url}")
    return None


def find_beer_image_url(beer):
    """
    Find the best image URL for a beer.

    Returns URL or None if not found.
    """
    beer_name = beer.name
    brewery_name = beer.brewery.name

    print(f"\nSearching for: {beer_name} ({brewery_name})")

    # Check if brewery has a website
    if brewery_name in BREWERY_WEBSITES:
        print(f"  Brewery website: {BREWERY_WEBSITES[brewery_name]}")

    # Search methods (manual for now - would need APIs for automation)
    search_google_images(beer_name, brewery_name)
    search_untappd(beer_name, brewery_name)

    return None


def download_and_save_image(url, beer):
    """Download image and save to beer model."""
    try:
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
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

        # Resize to 600x600 max
        img.thumbnail((600, 600), Image.Resampling.LANCZOS)

        # Save to BytesIO
        output = BytesIO()
        img.save(output, format='JPEG', quality=90)
        output.seek(0)

        # Save to model
        filename = f"{beer.slug}.jpg"
        beer.image.save(filename, ContentFile(output.read()), save=True)

        print(f"  [+] Saved image for {beer.name}")
        return True

    except Exception as e:
        print(f"  [!] Download error: {e}")
        return False


def import_from_csv():
    """
    Import beer images from a CSV file.

    CSV format:
    beer_name,brewery_name,image_url
    Punk IPA,BrewDog,https://example.com/punk-ipa.jpg
    """
    import csv

    csv_file = 'beer_images.csv'

    if not os.path.exists(csv_file):
        print(f"\n{csv_file} not found!")
        print("Create a CSV file with columns: beer_name,brewery_name,image_url")
        return

    print("\n" + "="*70)
    print("Importing Beer Images from CSV")
    print("="*70 + "\n")

    success = 0
    failed = 0
    not_found = 0

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            beer_name = row['beer_name']
            brewery_name = row['brewery_name']
            image_url = row['image_url']

            # Find beer in database
            beer = Beer.objects.filter(
                name__iexact=beer_name,
                brewery__name__iexact=brewery_name
            ).first()

            if not beer:
                print(f"[-] Beer not found: {beer_name} ({brewery_name})")
                not_found += 1
                continue

            print(f"\n{beer_name} ({brewery_name})")

            if download_and_save_image(image_url, beer):
                success += 1
            else:
                failed += 1

    # Summary
    print(f"\n{'='*70}")
    print("Summary")
    print("="*70)
    print(f"  Successfully imported: {success}")
    print(f"  Failed: {failed}")
    print(f"  Not found in database: {not_found}")
    print(f"  Total beers with images: {Beer.objects.exclude(image='').count()}/{Beer.objects.count()}")
    print("="*70 + "\n")


def generate_search_list():
    """
    Generate a list of beers needing images with search URLs.

    This helps you manually find images.
    """
    print("\n" + "="*70)
    print("UK Beers - Image Search URLs")
    print("="*70 + "\n")

    beers = Beer.objects.filter(image='').select_related('brewery', 'category')

    print(f"Found {beers.count()} beers without images\n")
    print("Format: beer_name,brewery_name,google_search_url,untappd_search_url\n")

    # Create CSV
    with open('beer_image_search_urls.csv', 'w', encoding='utf-8', newline='') as f:
        f.write('beer_name,brewery_name,category,google_url,untappd_url\n')

        for beer in beers:
            search_query = f"{beer.name} {beer.brewery.name} beer"
            google_url = f"https://www.google.com/search?q={quote_plus(search_query)}&tbm=isch"
            untappd_url = f"https://untappd.com/search?q={quote_plus(search_query)}&type=beer"

            f.write(f'"{beer.name}","{beer.brewery.name}","{beer.category.name}",{google_url},{untappd_url}\n')

            print(f"{beer.name} ({beer.brewery.name})")
            print(f"  Google: {google_url}")
            print(f"  Untappd: {untappd_url}\n")

    print("\n" + "="*70)
    print("Search URLs saved to: beer_image_search_urls.csv")
    print("="*70 + "\n")
    print("\nNext steps:")
    print("1. Open beer_image_search_urls.csv")
    print("2. For each beer, click the Google/Untappd link")
    print("3. Find the official product image")
    print("4. Copy the image URL")
    print("5. Create beer_images.csv with format: beer_name,brewery_name,image_url")
    print("6. Run: python import_real_beer_images.py --from-csv")


if __name__ == '__main__':
    import sys

    if '--from-csv' in sys.argv:
        import_from_csv()
    else:
        generate_search_list()
        print("\n" + "="*70)
        print("TIP: For automated import, consider:")
        print("  - SerpApi for Google Images (https://serpapi.com)")
        print("  - Untappd API (https://untappd.com/api)")
        print("  - Web scraping brewery websites directly")
        print("="*70 + "\n")
