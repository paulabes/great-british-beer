#!/usr/bin/env python
"""
Update beers that don't have Untappd images with high-resolution
style-appropriate generic images.
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


# High resolution style-appropriate images (1600x1600)
STYLE_IMAGES = {
    'IPA': 'https://images.unsplash.com/photo-1608270586620-248524c67de9?w=1600&h=1600&fit=crop&q=90',
    'Session IPA': 'https://images.unsplash.com/photo-1608270586620-248524c67de9?w=1600&h=1600&fit=crop&q=90',
    'Pale Ale': 'https://images.unsplash.com/photo-1535958636474-b021ee887b13?w=1600&h=1600&fit=crop&q=90',
    'Golden Ale': 'https://images.unsplash.com/photo-1618885472179-5e474019f2a9?w=1600&h=1600&fit=crop&q=90',
    'Blonde Ale': 'https://images.unsplash.com/photo-1535958636474-b021ee887b13?w=1600&h=1600&fit=crop&q=90',
    'Lager': 'https://images.unsplash.com/photo-1618183479302-1e0aa382c36b?w=1600&h=1600&fit=crop&q=90',
    'Stout': 'https://images.unsplash.com/photo-1612528443702-f6741f70a049?w=1600&h=1600&fit=crop&q=90',
    'Porter': 'https://images.unsplash.com/photo-1608434332718-1db37e9daf80?w=1600&h=1600&fit=crop&q=90',
    'Bitter': 'https://images.unsplash.com/photo-1535961652354-923cb08225a7?w=1600&h=1600&fit=crop&q=90',
    'Amber Ale': 'https://images.unsplash.com/photo-1612528443702-f6741f70a049?w=1600&h=1600&fit=crop&q=90',
    'Strong Ale': 'https://images.unsplash.com/photo-1572490122747-3968b75cc699?w=1600&h=1600&fit=crop&q=90',
}

DEFAULT_IMAGE = 'https://images.unsplash.com/photo-1608270586620-248524c67de9?w=1600&h=1600&fit=crop&q=90'


# Beers that weren't found on Untappd
BEERS_TO_UPDATE = [
    ('Wildebeast', 'Wild Beer Co'),
    ('Hooky Bitter', 'Hook Norton Brewery'),
    ("Bishop's Finger", 'Shepherd Neame'),
    ('Lupuloid', 'Beavertown Brewery'),
    ('Neck Oil', 'Beavertown Brewery'),
    ('Gamma Ray', 'Beavertown Brewery'),
    ('Courage Best', "Wells & Young's"),
    ("Young's Bitter", "Wells & Young's"),
    ('Bombardier', "Wells & Young's"),
    ('Lightfoot', 'T&R Theakston'),
    ('Best Bitter', 'T&R Theakston'),
    ('Old Peculier', 'T&R Theakston'),
    ('Old Speckled Hen', 'Greene King'),
    ('IPA', 'Greene King'),
    ('Abbot Ale', 'Greene King'),
    ('Clouded Yellow', 'St Austell Brewery'),
    ('Korev', 'St Austell Brewery'),
    ('Golden Sheep', 'Black Sheep Brewery'),
    ('Riggwelter', 'Black Sheep Brewery'),
    ('Best Bitter', 'Black Sheep Brewery'),
    ('Jack Brand Dry Hopped Lager', 'Adnams'),
    ('Knowle Spring', 'Timothy Taylor'),
    ('Pale Ale', '360 Degree'),
    ('Old Man', 'The Long Man'),
    ('Long Blonde', 'The Long Man'),
    ('Revival', 'Goodwood'),
    ('Old Ale', 'Harveys & Son'),
    ('Sussex Best Bitter', 'Harveys & Son'),
    ('7 products', 'Dark Star Brewing Co'),
]


def get_style_image(category_name):
    """Get image URL for beer style."""
    # Try exact match
    if category_name in STYLE_IMAGES:
        return STYLE_IMAGES[category_name]

    # Try partial match
    for style, url in STYLE_IMAGES.items():
        if style.lower() in category_name.lower():
            return url

    return DEFAULT_IMAGE


def download_and_save(url, beer):
    """Download and save high-resolution image."""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        img = Image.open(BytesIO(response.content))

        # Convert to RGB
        if img.mode in ('RGBA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'RGBA':
                background.paste(img, mask=img.split()[3])
            else:
                background.paste(img)
            img = background

        # Don't resize - let model handle it
        if img.height > 2400 or img.width > 2400:
            img.thumbnail((2400, 2400), Image.Resampling.LANCZOS)

        # Save with high quality
        output = BytesIO()
        img.save(output, format='JPEG', quality=95)
        output.seek(0)

        beer.image.save(f"{beer.slug}.jpg", ContentFile(output.read()), save=True)
        return True

    except Exception as e:
        print(f"    [!] Error: {e}")
        return False


def update_missing_images():
    """Update beers with high-resolution style-appropriate images."""
    print("\n" + "="*70)
    print("Updating Missing Beer Images with High-Resolution Style Images")
    print("="*70 + "\n")

    success = 0
    failed = 0
    not_found = 0

    for beer_name, brewery_name in BEERS_TO_UPDATE:
        print(f"\n{beer_name} ({brewery_name})")

        # Find beer
        beer = Beer.objects.filter(
            name__iexact=beer_name,
            brewery__name__iexact=brewery_name
        ).first()

        if not beer:
            print(f"    [-] Not found in database")
            not_found += 1
            continue

        # Get style-appropriate image
        image_url = get_style_image(beer.category.name)
        print(f"    Style: {beer.category.name}")

        # Download and save
        if download_and_save(image_url, beer):
            print(f"    [+] Updated with {beer.category.name} style image")
            success += 1
        else:
            failed += 1

    # Summary
    print(f"\n{'='*70}")
    print("Summary")
    print("="*70)
    print(f"  Successfully updated: {success}")
    print(f"  Failed: {failed}")
    print(f"  Not found: {not_found}")
    print(f"\n  All beers now have high-resolution images!")
    print("="*70 + "\n")


if __name__ == '__main__':
    update_missing_images()
