#!/usr/bin/env python
"""
Import beer images from Untappd.

Untappd is a beer database with official images for most commercial beers.
This script searches Untappd for each beer and downloads the product image.

Install: pip install beautifulsoup4 lxml
"""

import os
import django
import requests
import time
import re
from bs4 import BeautifulSoup
from io import BytesIO
from PIL import Image
from urllib.parse import quote_plus

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greatbritishbeer.settings')
django.setup()

from reviews.models import Beer
from django.core.files.base import ContentFile


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
}


def search_untappd(beer_name, brewery_name):
    """
    Search Untappd for a beer and return its image URL.

    Args:
        beer_name: Name of the beer
        brewery_name: Name of the brewery

    Returns:
        Image URL or None
    """
    try:
        # Clean names for search
        search_query = f"{beer_name} {brewery_name}"
        search_url = f"https://untappd.com/search?q={quote_plus(search_query)}&type=beer"

        print(f"    Searching Untappd: {search_query}")

        response = requests.get(search_url, headers=HEADERS, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'lxml')

        # Find beer results
        beer_items = soup.select('.beer-item')

        if not beer_items:
            print(f"    [-] No results found")
            return None

        # Check first few results
        for item in beer_items[:3]:
            # Get beer name and brewery from result
            beer_link = item.select_one('.name a, h4 a')
            brewery_link = item.select_one('.brewery a')

            if not beer_link or not brewery_link:
                continue

            result_beer = beer_link.get_text().strip().lower()
            result_brewery = brewery_link.get_text().strip().lower()

            # Check if it's a match
            if beer_name.lower() in result_beer and brewery_name.lower() in result_brewery:
                # Get the beer image
                img = item.select_one('img.label, img[src*="untappd"]')

                if img:
                    img_url = img.get('src')

                    if img_url:
                        # Get highest resolution version available
                        # Untappd uses: /label_100x100/ for thumbnails
                        # Remove all size restrictions for full resolution
                        img_url = img_url.replace('_100x100', '')
                        img_url = img_url.replace('_sq', '')
                        img_url = img_url.replace('_200x200', '')
                        img_url = img_url.replace('_320x320', '')
                        img_url = img_url.replace('_640x640', '')

                        # Force highest quality
                        if 'untappd.akamaized.net' in img_url:
                            # Untappd CDN - request original size
                            img_url = img_url.split('?')[0]  # Remove query params that might limit size

                        print(f"    [+] Found on Untappd!")
                        return img_url

        print(f"    [-] No matching beer found")
        return None

    except Exception as e:
        print(f"    [!] Untappd search error: {e}")
        return None


def download_and_save_image(url, beer):
    """Download image and save to beer model at highest available resolution."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
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

        # Don't resize here - let the model handle it at 1200x1200
        # Just ensure it's not absurdly large (over 2400x2400)
        if img.height > 2400 or img.width > 2400:
            img.thumbnail((2400, 2400), Image.Resampling.LANCZOS)

        # Save to BytesIO with high quality
        output = BytesIO()
        img.save(output, format='JPEG', quality=95)
        output.seek(0)

        # Save to model (model will resize to 1200x1200 max)
        filename = f"{beer.slug}.jpg"
        beer.image.save(filename, ContentFile(output.read()), save=True)

        return True

    except Exception as e:
        print(f"    [!] Download error: {e}")
        return False


def import_untappd_images(update_all=False):
    """Import beer images from Untappd."""
    print("\n" + "="*70)
    print("Importing Beer Images from Untappd")
    print("="*70 + "\n")

    if update_all:
        beers = Beer.objects.all().select_related('brewery')
        print("Updating ALL beers (this will take a while!)\n")
    else:
        beers = Beer.objects.filter(image='').select_related('brewery')

    total = beers.count()

    if total == 0:
        print("All beers have images!")
        return

    print(f"Searching Untappd for {total} beers\n")
    print("Note: This may take several minutes due to rate limiting\n")

    stats = {
        'found': 0,
        'not_found': 0,
        'failed': 0
    }

    for i, beer in enumerate(beers, 1):
        print(f"\n[{i}/{total}] {beer.name} ({beer.brewery.name})")

        # Search Untappd
        image_url = search_untappd(beer.name, beer.brewery.name)

        if not image_url:
            stats['not_found'] += 1
            continue

        # Download and save
        if download_and_save_image(image_url, beer):
            print(f"    [+] Saved!")
            stats['found'] += 1
        else:
            stats['failed'] += 1

        # Rate limiting - be nice to Untappd
        time.sleep(3)

    # Summary
    print(f"\n{'='*70}")
    print("Summary")
    print("="*70)
    print(f"  Successfully imported: {stats['found']}")
    print(f"  Not found on Untappd: {stats['not_found']}")
    print(f"  Download failed: {stats['failed']}")
    print(f"\n  Total beers with images: {Beer.objects.exclude(image='').count()}/{Beer.objects.count()}")
    print("="*70 + "\n")


if __name__ == '__main__':
    import sys

    if '--all' in sys.argv:
        import_untappd_images(update_all=True)
    else:
        import_untappd_images(update_all=False)
