#!/usr/bin/env python
"""
Simple script to add generic but high-quality beer images to all beers.
Uses curated Unsplash images that don't require API access.

This is the fastest way to get all beers looking good!
"""

import os
import django
import requests
from io import BytesIO
from PIL import Image

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greatbritishbeer.settings')
django.setup()

from reviews.models import Beer
from django.core.files.base import ContentFile


# High quality, curated beer images from Unsplash (public domain)
# Each image is selected to represent different beer styles
# Using 1600x1600 for high resolution displays
BEER_IMAGES = {
    # IPAs and Hoppy Beers
    'IPA': 'https://images.unsplash.com/photo-1608270586620-248524c67de9?w=1600&h=1600&fit=crop&q=90',
    'Session IPA': 'https://images.unsplash.com/photo-1608270586620-248524c67de9?w=1600&h=1600&fit=crop&q=90',

    # Pale Ales and Golden Beers
    'Pale Ale': 'https://images.unsplash.com/photo-1535958636474-b021ee887b13?w=1600&h=1600&fit=crop&q=90',
    'Golden Ale': 'https://images.unsplash.com/photo-1618885472179-5e474019f2a9?w=1600&h=1600&fit=crop&q=90',
    'Blonde Ale': 'https://images.unsplash.com/photo-1535958636474-b021ee887b13?w=1600&h=1600&fit=crop&q=90',

    # Lagers
    'Lager': 'https://images.unsplash.com/photo-1618183479302-1e0aa382c36b?w=1600&h=1600&fit=crop&q=90',

    # Dark Beers
    'Stout': 'https://images.unsplash.com/photo-1612528443702-f6741f70a049?w=1600&h=1600&fit=crop&q=90',
    'Porter': 'https://images.unsplash.com/photo-1608434332718-1db37e9daf80?w=1600&h=1600&fit=crop&q=90',

    # Bitters and Traditional Ales
    'Bitter': 'https://images.unsplash.com/photo-1535961652354-923cb08225a7?w=1600&h=1600&fit=crop&q=90',
    'Amber Ale': 'https://images.unsplash.com/photo-1612528443702-f6741f70a049?w=1600&h=1600&fit=crop&q=90',
    'Strong Ale': 'https://images.unsplash.com/photo-1572490122747-3968b75cc699?w=1600&h=1600&fit=crop&q=90',
}

# Default fallback for any style not in the map
DEFAULT_IMAGE = 'https://images.unsplash.com/photo-1608270586620-248524c67de9?w=1600&h=1600&fit=crop&q=90'


def get_image_for_beer(beer):
    """Get the most appropriate image URL for a beer based on its category."""
    category_name = beer.category.name

    # Try exact match first
    if category_name in BEER_IMAGES:
        return BEER_IMAGES[category_name]

    # Try partial matches
    for style, url in BEER_IMAGES.items():
        if style.lower() in category_name.lower():
            return url

    # Fallback to default
    return DEFAULT_IMAGE


def download_and_save_image(url, beer):
    """Download image and save to beer model at high resolution."""
    try:
        print(f"  Downloading image for {beer.name}...")

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

        # Don't resize here - let model handle it at 1200x1200
        # Just ensure it's not absurdly large
        if img.height > 2400 or img.width > 2400:
            img.thumbnail((2400, 2400), Image.Resampling.LANCZOS)

        # Save to BytesIO with high quality
        output = BytesIO()
        img.save(output, format='JPEG', quality=95)
        output.seek(0)

        # Save to model (model will resize to 1200x1200 max)
        filename = f"{beer.slug}.jpg"
        beer.image.save(filename, ContentFile(output.read()), save=True)

        print(f"  [+] Saved image for {beer.name}")
        return True

    except Exception as e:
        print(f"  [!] Error downloading image for {beer.name}: {e}")
        return False


def import_images():
    """Add style-appropriate images to all beers without images."""
    print("\n" + "="*70)
    print("Adding Style-Appropriate Beer Images")
    print("="*70 + "\n")

    beers = Beer.objects.filter(image='')
    total_beers = beers.count()

    if total_beers == 0:
        print("All beers already have images!\n")
        return

    print(f"Adding images to {total_beers} beers...")
    print("Each beer will get an image matching its style.\n")

    success_count = 0
    failed_count = 0

    for beer in beers:
        print(f"\n{beer.name} ({beer.category.name})")
        image_url = get_image_for_beer(beer)

        if download_and_save_image(image_url, beer):
            success_count += 1
        else:
            failed_count += 1

    # Print summary
    print(f"\n{'='*70}")
    print("Summary")
    print("="*70)
    print(f"  Successfully added: {success_count}")
    print(f"  Failed: {failed_count}")
    print(f"  Total beers with images: {Beer.objects.exclude(image='').count()}/{Beer.objects.count()}")
    print("="*70 + "\n")


if __name__ == '__main__':
    import_images()
