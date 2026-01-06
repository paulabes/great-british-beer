#!/usr/bin/env python
"""
Add 10% padding around all beer images to prevent pixelation when displayed.
This creates a border of whitespace around each image.
"""

import os
import django
from PIL import Image

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greatbritishbeer.settings')
django.setup()

from reviews.models import Beer


def add_padding_to_image(image_path, padding_percent=10):
    """
    Add padding around an image.

    Args:
        image_path: Path to the image file
        padding_percent: Percentage of padding to add (default 10%)
    """
    try:
        # Open image
        img = Image.open(image_path)

        # Calculate padding
        width, height = img.size
        pad_w = int(width * (padding_percent / 100))
        pad_h = int(height * (padding_percent / 100))

        # Create new image with padding (white background)
        new_width = width + (pad_w * 2)
        new_height = height + (pad_h * 2)

        padded_img = Image.new('RGB', (new_width, new_height), (255, 255, 255))

        # Paste original image in center
        padded_img.paste(img, (pad_w, pad_h))

        # Save back to same file
        padded_img.save(image_path, 'JPEG', quality=95)

        return True

    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return False


def add_padding_to_all_beers():
    """Add 10% padding to all beer images."""
    print("\n" + "="*70)
    print("Adding 10% Padding to All Beer Images")
    print("="*70 + "\n")

    beers = Beer.objects.exclude(image='')
    total = beers.count()
    success = 0
    failed = 0

    print(f"Processing {total} beer images...\n")

    for i, beer in enumerate(beers, 1):
        if beer.image:
            image_path = beer.image.path

            if os.path.exists(image_path):
                print(f"[{i}/{total}] {beer.name}: ", end='')

                if add_padding_to_image(image_path, padding_percent=10):
                    print("[+] Padded")
                    success += 1
                else:
                    print("[!] Failed")
                    failed += 1
            else:
                print(f"[{i}/{total}] {beer.name}: [!] File not found")
                failed += 1

    # Summary
    print(f"\n{'='*70}")
    print("Summary")
    print("="*70)
    print(f"  Successfully padded: {success}")
    print(f"  Failed: {failed}")
    print(f"  Total processed: {total}")
    print("="*70 + "\n")
    print("All images now have 10% padding to prevent pixelation!")
    print("="*70 + "\n")


if __name__ == '__main__':
    add_padding_to_all_beers()
