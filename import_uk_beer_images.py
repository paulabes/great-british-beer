#!/usr/bin/env python
"""
Multi-tier approach to import images for UK beers.

Tier 1: Search Unsplash for specific beer + brewery names
Tier 2: Search by beer style/category for relevant images
Tier 3: Use generic beer images as fallback

This approach provides beer-specific images where possible, falling back to
appropriate style-based or generic images.
"""

import os
import django
import time
import requests
from io import BytesIO
from PIL import Image

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greatbritishbeer.settings')
django.setup()

from reviews.models import Beer
from django.core.files.base import ContentFile


# Unsplash API configuration (using public demo access)
UNSPLASH_ACCESS_KEY = 'your_access_key_here'  # Get free key at unsplash.com/developers
UNSPLASH_SEARCH_URL = 'https://api.unsplash.com/search/photos'

# Style-specific search terms for better image matching
STYLE_SEARCH_TERMS = {
    'IPA': ['india pale ale beer', 'hoppy beer glass', 'craft ipa'],
    'Pale Ale': ['pale ale beer', 'golden beer glass', 'craft pale ale'],
    'Bitter': ['english bitter beer', 'traditional bitter', 'cask ale'],
    'Stout': ['stout beer', 'dark beer glass', 'guinness style'],
    'Porter': ['porter beer', 'dark ale glass'],
    'Lager': ['lager beer', 'pilsner glass', 'crisp beer'],
    'Golden Ale': ['golden ale beer', 'blonde beer glass'],
    'Amber Ale': ['amber ale beer', 'red ale glass'],
    'Strong Ale': ['strong ale beer', 'barley wine glass'],
    'Session IPA': ['session ipa beer', 'light ipa glass'],
    'Blonde Ale': ['blonde ale beer', 'light beer glass'],
}

# Fallback generic beer images (high quality Unsplash)
GENERIC_BEER_IMAGES = [
    'https://images.unsplash.com/photo-1608270586620-248524c67de9?w=800&h=800&fit=crop',  # IPA
    'https://images.unsplash.com/photo-1618183479302-1e0aa382c36b?w=800&h=800&fit=crop',  # Lager
    'https://images.unsplash.com/photo-1535958636474-b021ee887b13?w=800&h=800&fit=crop',  # Golden
    'https://images.unsplash.com/photo-1612528443702-f6741f70a049?w=800&h=800&fit=crop',  # Dark
    'https://images.unsplash.com/photo-1608434332718-1db37e9daf80?w=800&h=800&fit=crop',  # Craft
    'https://images.unsplash.com/photo-1600788907416-456118662447?w=800&h=800&fit=crop',  # Tap
]


def search_unsplash_beer_image(beer_name, brewery_name, category_name):
    """
    Search Unsplash for beer-specific image.

    Returns image URL if found, None otherwise.
    """
    if UNSPLASH_ACCESS_KEY == 'your_access_key_here':
        print(f"    [!] Unsplash API key not configured - skipping search")
        return None

    # Try different search combinations
    search_queries = [
        f"{beer_name} {brewery_name} beer",
        f"{brewery_name} {beer_name}",
        f"{category_name} beer glass",
    ]

    for query in search_queries:
        try:
            params = {
                'query': query,
                'per_page': 1,
                'orientation': 'squarish'
            }
            headers = {
                'Authorization': f'Client-ID {UNSPLASH_ACCESS_KEY}'
            }

            response = requests.get(UNSPLASH_SEARCH_URL, params=params, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get('results'):
                    image_url = data['results'][0]['urls']['regular']
                    print(f"    [+] Found on Unsplash: {query}")
                    return image_url

            # Rate limiting
            time.sleep(0.5)

        except Exception as e:
            print(f"    [!] Unsplash search error: {e}")
            continue

    return None


def get_style_based_image(category_name):
    """Get appropriate image based on beer style/category."""
    # Get search terms for this style
    search_terms = STYLE_SEARCH_TERMS.get(category_name)

    if not search_terms or UNSPLASH_ACCESS_KEY == 'your_access_key_here':
        return None

    try:
        # Use first search term for this style
        params = {
            'query': search_terms[0],
            'per_page': 1,
            'orientation': 'squarish'
        }
        headers = {
            'Authorization': f'Client-ID {UNSPLASH_ACCESS_KEY}'
        }

        response = requests.get(UNSPLASH_SEARCH_URL, params=params, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data.get('results'):
                return data['results'][0]['urls']['regular']

        time.sleep(0.5)

    except Exception as e:
        print(f"    [!] Style search error: {e}")

    return None


def download_and_save_image(url, beer):
    """Download image and save to beer model."""
    try:
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
        print(f"    [!] Download error: {e}")
        return False


def import_beer_images():
    """Import images for all beers without images."""
    print("\n" + "="*70)
    print("Importing Beer Images - Multi-Tier Approach")
    print("="*70 + "\n")

    # Get beers without images
    beers_without_images = Beer.objects.filter(image='')
    total_beers = beers_without_images.count()

    if total_beers == 0:
        print("All beers already have images!")
        return

    print(f"Found {total_beers} beers without images\n")

    if UNSPLASH_ACCESS_KEY == 'your_access_key_here':
        print("[!] NOTE: Unsplash API key not configured")
        print("    Using generic fallback images only")
        print("    Get a free API key at: https://unsplash.com/developers\n")

    stats = {
        'specific': 0,      # Found beer-specific image
        'style': 0,         # Found style-appropriate image
        'generic': 0,       # Used generic fallback
        'failed': 0         # Failed to add image
    }

    for i, beer in enumerate(beers_without_images, 1):
        print(f"[{i}/{total_beers}] {beer.name} ({beer.brewery.name})")

        image_url = None
        image_type = None

        # Tier 1: Search for specific beer
        if UNSPLASH_ACCESS_KEY != 'your_access_key_here':
            image_url = search_unsplash_beer_image(
                beer.name,
                beer.brewery.name,
                beer.category.name
            )
            if image_url:
                image_type = 'specific'

        # Tier 2: Get style-based image
        if not image_url and UNSPLASH_ACCESS_KEY != 'your_access_key_here':
            image_url = get_style_based_image(beer.category.name)
            if image_url:
                image_type = 'style'

        # Tier 3: Use generic fallback
        if not image_url:
            image_url = GENERIC_BEER_IMAGES[i % len(GENERIC_BEER_IMAGES)]
            image_type = 'generic'

        # Download and save
        if download_and_save_image(image_url, beer):
            stats[image_type] += 1
            print(f"    [+] Added {image_type} image\n")
        else:
            stats['failed'] += 1
            print(f"    [!] Failed to add image\n")

        # Rate limiting
        if UNSPLASH_ACCESS_KEY != 'your_access_key_here':
            time.sleep(1)

    # Print summary
    print("="*70)
    print("Summary")
    print("="*70)
    print(f"  Beer-specific images: {stats['specific']}")
    print(f"  Style-based images: {stats['style']}")
    print(f"  Generic fallback images: {stats['generic']}")
    print(f"  Failed: {stats['failed']}")
    print(f"  Total processed: {total_beers}")
    print(f"\n  Beers with images: {Beer.objects.exclude(image='').count()}/{Beer.objects.count()}")
    print("="*70 + "\n")


if __name__ == '__main__':
    import_beer_images()
