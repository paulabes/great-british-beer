#!/usr/bin/env python
"""
Scrape actual product images from brewery websites for all UK beers.

This scraper visits each brewery's website and attempts to find
product images for their beers.

Install required packages:
pip install requests beautifulsoup4 pillow lxml
"""

import os
import django
import requests
import time
import re
from bs4 import BeautifulSoup
from io import BytesIO
from PIL import Image
from urllib.parse import urljoin, urlparse

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greatbritishbeer.settings')
django.setup()

from reviews.models import Beer
from django.core.files.base import ContentFile


# Headers to mimic a real browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


def clean_beer_name(name):
    """Clean beer name for matching."""
    # Remove common suffixes and extras
    name = re.sub(r'\s*\d+ml.*$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*\d+\s*x\s*\d+ml.*$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*bottle.*$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*can.*$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*cask.*$', '', name, flags=re.IGNORECASE)
    return name.lower().strip()


def find_product_image_on_page(url, beer_name):
    """
    Visit a product page and find the main product image.

    Args:
        url: Product page URL
        beer_name: Name of beer to match

    Returns:
        Image URL or None
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'lxml')

        # Common selectors for product images
        image_selectors = [
            'img.product-image',
            'img.product-main-image',
            'img[alt*="product"]',
            'img[alt*="beer"]',
            '.product-image img',
            '.product-photo img',
            '.product-gallery img',
            'div.product img',
            'figure.product img',
            'img[itemprop="image"]',
        ]

        for selector in image_selectors:
            img_tags = soup.select(selector)
            for img in img_tags:
                src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                if src:
                    # Convert relative URLs to absolute
                    full_url = urljoin(url, src)

                    # Skip thumbnails and icons
                    if any(x in full_url.lower() for x in ['thumb', 'icon', 'logo', 'small']):
                        continue

                    # Skip very small images
                    if any(f'{size}x{size}' in full_url for size in [50, 75, 100, 150]):
                        continue

                    return full_url

        # Fallback: Find any large image
        all_images = soup.find_all('img')
        for img in all_images:
            src = img.get('src') or img.get('data-src')
            if src and (img.get('width', 0) > 200 or img.get('height', 0) > 200):
                full_url = urljoin(url, src)
                if not any(x in full_url.lower() for x in ['thumb', 'icon', 'logo']):
                    return full_url

    except Exception as e:
        print(f"    [!] Error scraping page: {e}")

    return None


def scrape_brewdog(beer):
    """Scrape BrewDog website for beer images."""
    try:
        # Search BrewDog website
        search_url = f"https://www.brewdog.com/uk/search?q={beer.name.replace(' ', '+')}"
        response = requests.get(search_url, headers=HEADERS, timeout=15)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'lxml')

            # Find product links
            product_links = soup.select('a.product-item__link, a[href*="/product/"]')

            for link in product_links:
                href = link.get('href')
                if href:
                    product_url = urljoin('https://www.brewdog.com', href)

                    # Check if this is the right beer
                    link_text = link.get_text().lower()
                    if clean_beer_name(beer.name) in clean_beer_name(link_text):
                        image_url = find_product_image_on_page(product_url, beer.name)
                        if image_url:
                            return image_url

    except Exception as e:
        print(f"    [!] BrewDog scrape error: {e}")

    return None


def scrape_fullers(beer):
    """Scrape Fuller's website for beer images."""
    try:
        # Fuller's beer pages
        beer_slug = beer.name.lower().replace(' ', '-').replace("'", '')
        product_url = f"https://www.fullers.co.uk/beers/{beer_slug}"

        response = requests.get(product_url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            return find_product_image_on_page(product_url, beer.name)

    except Exception as e:
        print(f"    [!] Fuller's scrape error: {e}")

    return None


def scrape_adnams(beer):
    """Scrape Adnams website for beer images."""
    try:
        # Adnams uses Shopify
        search_url = f"https://shop.adnams.co.uk/search?q={beer.name.replace(' ', '+')}"
        response = requests.get(search_url, headers=HEADERS, timeout=15)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'lxml')
            product_links = soup.select('a.product-card__link, a[href*="/products/"]')

            for link in product_links:
                href = link.get('href')
                if href and clean_beer_name(beer.name) in clean_beer_name(href):
                    product_url = urljoin('https://shop.adnams.co.uk', href)
                    image_url = find_product_image_on_page(product_url, beer.name)
                    if image_url:
                        return image_url

    except Exception as e:
        print(f"    [!] Adnams scrape error: {e}")

    return None


def scrape_thornbridge(beer):
    """Scrape Thornbridge website for beer images."""
    try:
        # Thornbridge beer pages
        search_url = f"https://thornbridgebrewery.co.uk/?s={beer.name.replace(' ', '+')}"
        response = requests.get(search_url, headers=HEADERS, timeout=15)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'lxml')
            product_links = soup.select('a[href*="/beer/"], a.product-link')

            for link in product_links:
                href = link.get('href')
                if href:
                    product_url = urljoin('https://thornbridgebrewery.co.uk', href)
                    if clean_beer_name(beer.name) in clean_beer_name(product_url):
                        image_url = find_product_image_on_page(product_url, beer.name)
                        if image_url:
                            return image_url

    except Exception as e:
        print(f"    [!] Thornbridge scrape error: {e}")

    return None


def scrape_camden(beer):
    """Scrape Camden Town Brewery website."""
    try:
        # Camden uses simple URL structure
        beer_slug = beer.name.lower().replace(' ', '-')
        product_url = f"https://www.camdentownbrewery.com/beers/{beer_slug}"

        response = requests.get(product_url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            return find_product_image_on_page(product_url, beer.name)

    except Exception as e:
        print(f"    [!] Camden scrape error: {e}")

    return None


# Brewery scrapers mapping
BREWERY_SCRAPERS = {
    'BrewDog': scrape_brewdog,
    "Fuller's": scrape_fullers,
    'Adnams': scrape_adnams,
    'Thornbridge Brewery': scrape_thornbridge,
    'Camden Town Brewery': scrape_camden,
}


def download_and_save_image(url, beer):
    """Download image and save to beer model."""
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

        # Resize to 600x600 max
        img.thumbnail((600, 600), Image.Resampling.LANCZOS)

        # Save to BytesIO
        output = BytesIO()
        img.save(output, format='JPEG', quality=90)
        output.seek(0)

        # Save to model
        filename = f"{beer.slug}.jpg"
        beer.image.save(filename, ContentFile(output.read()), save=True)

        return True

    except Exception as e:
        print(f"    [!] Download error: {e}")
        return False


def scrape_beer_images():
    """Scrape product images for all beers."""
    print("\n" + "="*70)
    print("Scraping Brewery Product Images")
    print("="*70 + "\n")

    beers = Beer.objects.filter(image='').select_related('brewery')
    total = beers.count()

    if total == 0:
        print("All beers have images!")
        return

    print(f"Attempting to scrape images for {total} beers\n")

    stats = {
        'success': 0,
        'no_scraper': 0,
        'not_found': 0,
        'failed': 0
    }

    for i, beer in enumerate(beers, 1):
        print(f"[{i}/{total}] {beer.name} ({beer.brewery.name})")

        brewery_name = beer.brewery.name

        # Check if we have a scraper for this brewery
        if brewery_name not in BREWERY_SCRAPERS:
            print(f"    [-] No scraper for {brewery_name}")
            stats['no_scraper'] += 1
            continue

        # Run brewery-specific scraper
        scraper_func = BREWERY_SCRAPERS[brewery_name]
        image_url = scraper_func(beer)

        if not image_url:
            print(f"    [-] Image not found on website")
            stats['not_found'] += 1
            continue

        print(f"    [+] Found image: {image_url[:80]}...")

        # Download and save
        if download_and_save_image(image_url, beer):
            print(f"    [+] Saved!")
            stats['success'] += 1
        else:
            stats['failed'] += 1

        # Rate limiting
        time.sleep(2)

    # Summary
    print(f"\n{'='*70}")
    print("Summary")
    print("="*70)
    print(f"  Successfully scraped: {stats['success']}")
    print(f"  No scraper available: {stats['no_scraper']}")
    print(f"  Not found on website: {stats['not_found']}")
    print(f"  Download failed: {stats['failed']}")
    print(f"\n  Total beers with images: {Beer.objects.exclude(image='').count()}/{Beer.objects.count()}")
    print("="*70 + "\n")


if __name__ == '__main__':
    scrape_beer_images()
