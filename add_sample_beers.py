"""
Quick script to add sample beers to existing breweries.
"""
import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greatbritishbeer.settings')
django.setup()

from reviews.models import Brewery, Category, Beer
from django.utils.text import slugify

# Sample beer data for British breweries
SAMPLE_BEERS = [
    # Dark Star Brewing Co
    ('Hophead', 'Dark Star Brewing Co', 'Pale Ale', Decimal('3.8'), 35, 'Golden', 'Session IPA',
     'A zesty pale ale with citrus and tropical fruit notes. Refreshing and sessionable.'),
    ('American Pale Ale', 'Dark Star Brewing Co', 'Pale Ale', Decimal('4.7'), 40, 'Amber', 'American Pale Ale',
     'Classic American-style pale ale with Cascade hops and biscuity malt.'),

    # Harveys & Son
    ('Sussex Best Bitter', 'Harveys & Son', 'Bitter', Decimal('4.0'), 35, 'Amber', 'Best Bitter',
     'Traditional Sussex bitter with a balance of malt and hops. A local favorite since 1790.'),
    ('Old Ale', 'Harveys & Son', 'Strong Ale', Decimal('4.3'), 30, 'Dark Brown', 'Old Ale',
     'Rich, full-bodied dark ale with fruity complexity.'),

    # Brighton Bier
    ('West Pier', 'Brighton Bier', 'Pale Ale', Decimal('4.5'), 40, 'Golden', 'Pale Ale',
     'Crisp, refreshing pale ale brewed in the heart of Brighton.'),
    ('Underdog', 'Brighton Bier', 'IPA', Decimal('5.8'), 55, 'Amber', 'IPA',
     'Bold IPA packed with American hops for a citrusy, resinous punch.'),

    # Burning Sky Brewery
    ('Plateau', 'Burning Sky Brewery', 'Pale Ale', Decimal('3.5'), 30, 'Golden', 'Table Beer',
     'Light, sessionable beer with delicate hop character. Perfect for any occasion.'),
    ('Aurora', 'Burning Sky Brewery', 'IPA', Decimal('5.6'), 45, 'Golden', 'IPA',
     'Modern IPA with tropical fruit aromas and a clean, bitter finish.'),

    # UnBarred
    ('Juicy', 'UnBarred', 'IPA', Decimal('6.5'), 50, 'Hazy Yellow', 'New England IPA',
     'Juicy, hazy IPA bursting with tropical fruit flavors and soft mouthfeel.'),
    ('Table Beer', 'UnBarred', 'Golden Ale', Decimal('3.5'), 25, 'Golden', 'Session Ale',
     'Easy-drinking golden ale perfect for extended sessions.'),

    # Goodwood
    ('Revival', 'Goodwood', 'Lager', Decimal('4.5'), 20, 'Golden', 'Pilsner',
     'Crisp Czech-style pilsner with floral hop notes.'),

    # Hand Brew Co
    ('IPA', 'Hand Brew Co', 'IPA', Decimal('5.2'), 45, 'Amber', 'IPA',
     'Traditional English IPA with earthy hops and caramel malt.'),

    # Kissingate
    ('Sussex', 'Kissingate', 'Bitter', Decimal('3.9'), 32, 'Amber', 'Best Bitter',
     'Classic Sussex bitter with balanced malt and hop character.'),

    # The Long Man
    ('Long Blonde', 'The Long Man', 'Golden Ale', Decimal('3.8'), 30, 'Golden', 'Blonde Ale',
     'Light, refreshing blonde ale with subtle hop bitterness.'),
    ('Old Man', 'The Long Man', 'Strong Ale', Decimal('4.3'), 28, 'Dark', 'Old Ale',
     'Traditional old ale with rich, malty sweetness.'),

    # 360 Degree
    ('Pale Ale', '360 Degree', 'Pale Ale', Decimal('4.2'), 38, 'Golden', 'Pale Ale',
     'Modern pale ale with balanced malt and citrus hops.'),

    # Arundel Brewery
    ('Castle', 'Arundel Brewery', 'Bitter', Decimal('3.8'), 30, 'Amber', 'Bitter',
     'Traditional Sussex bitter brewed in the shadow of Arundel Castle.'),

    # Hurst
    ('Founder', 'Hurst', 'Bitter', Decimal('4.2'), 35, 'Amber', 'Best Bitter',
     'Well-balanced best bitter with a smooth, malty character.'),
]

def create_sample_beers():
    """Create sample beers for existing breweries."""
    created_count = 0
    skipped_count = 0

    print("Adding sample beers to breweries...\n")

    for beer_data in SAMPLE_BEERS:
        name, brewery_name, category_name, abv, ibu, color, style, description = beer_data

        try:
            # Get brewery
            brewery = Brewery.objects.get(name=brewery_name)

            # Get category
            category = Category.objects.get(name=category_name)

            # Check if beer already exists
            slug = slugify(f"{name}-{brewery_name}")
            if Beer.objects.filter(slug=slug).exists():
                print(f"  [-] Skipped: {name} (already exists)")
                skipped_count += 1
                continue

            # Create beer
            beer = Beer.objects.create(
                name=name,
                slug=slug,
                brewery=brewery,
                category=category,
                description=description,
                abv=abv,
                ibu=ibu,
                color=color,
                style=style,
                is_featured=False
            )

            print(f"  [+] Created: {name} by {brewery_name} ({category_name}, {abv}% ABV)")
            created_count += 1

        except Brewery.DoesNotExist:
            print(f"  [!] Error: Brewery '{brewery_name}' not found")
            skipped_count += 1
        except Category.DoesNotExist:
            print(f"  [!] Error: Category '{category_name}' not found")
            skipped_count += 1
        except Exception as e:
            print(f"  [!] Error creating {name}: {e}")
            skipped_count += 1

    print(f"\n{'='*50}")
    print(f"Summary:")
    print(f"  Created: {created_count} beers")
    print(f"  Skipped: {skipped_count} beers")
    print(f"{'='*50}\n")

if __name__ == '__main__':
    create_sample_beers()
