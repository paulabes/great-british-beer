"""
Add image URLs to beers for display.
Using placeholder beer images from Unsplash.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greatbritishbeer.settings')
django.setup()

from reviews.models import Beer
from django.core.files.base import ContentFile
import requests
from PIL import Image
from io import BytesIO

# Generic beer images from Unsplash (free to use)
BEER_IMAGES = [
    'https://images.unsplash.com/photo-1608270586620-248524c67de9?w=800&h=600&fit=crop',  # IPA glass
    'https://images.unsplash.com/photo-1612528443702-f6741f70a049?w=800&h=600&fit=crop',  # Dark beer
    'https://images.unsplash.com/photo-1535958636474-b021ee887b13?w=800&h=600&fit=crop',  # Golden beer
    'https://images.unsplash.com/photo-1618183479302-1e0aa382c36b?w=800&h=600&fit=crop',  # Lager
    'https://images.unsplash.com/photo-1608434332718-1db37e9daf80?w=800&h=600&fit=crop',  # Craft beer
    'https://images.unsplash.com/photo-1572490122747-3968b75cc699?w=800&h=600&fit=crop',  # Beer flight
    'https://images.unsplash.com/photo-1600788907416-456118662447?w=800&h=600&fit=crop',  # Beer tap
    'https://images.unsplash.com/photo-1615332579937-4e1b32d0d4e8?w=800&h=600&fit=crop',  # Pale ale
]

def download_and_save_image(url, beer):
    """Download image and save to beer."""
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

        # Resize to 600x600
        img.thumbnail((600, 600), Image.Resampling.LANCZOS)

        # Save to BytesIO
        output = BytesIO()
        img.save(output, format='JPEG', quality=85)
        output.seek(0)

        # Save to model
        filename = f"{beer.slug}.jpg"
        beer.image.save(filename, ContentFile(output.read()), save=True)

        print(f"  [+] Saved image for {beer.name}")
        return True

    except Exception as e:
        print(f"  [!] Error downloading image for {beer.name}: {e}")
        return False

def add_images_to_beers():
    """Add images to all beers."""
    beers = Beer.objects.filter(image='')

    print(f"Adding images to {beers.count()} beers...\n")

    success_count = 0

    for i, beer in enumerate(beers):
        # Cycle through available images
        image_url = BEER_IMAGES[i % len(BEER_IMAGES)]

        if download_and_save_image(image_url, beer):
            success_count += 1

    print(f"\n{'='*50}")
    print(f"Summary:")
    print(f"  Images added: {success_count}/{beers.count()}")
    print(f"{'='*50}\n")

if __name__ == '__main__':
    add_images_to_beers()
