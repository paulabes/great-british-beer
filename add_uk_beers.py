#!/usr/bin/env python
"""
Add a comprehensive list of UK-produced beers that are currently available.
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greatbritishbeer.settings')
django.setup()

from reviews.models import Brewery, Beer, Category
from slugify import slugify


# Comprehensive list of current UK beers
UK_BEERS = [
    # BrewDog
    ("BrewDog", "Scotland", [
        ("Punk IPA", "IPA", 5.6, 35, "Post-modern classic. Our flagship beer that set us on a mission to revolutionise beer."),
        ("Elvis Juice", "IPA", 6.5, 40, "Grapefruit infused IPA. All the citrus-infused hoppy aromas you'd expect."),
        ("Dead Pony Club", "Pale Ale", 3.8, 35, "California-style pale ale. Hoppy sessionable pale ale."),
        ("Hazy Jane", "IPA", 7.2, 30, "New England IPA. Fruit-forward, juicy and silky smooth."),
        ("Jet Black Heart", "Stout", 4.7, 50, "Oatmeal milk stout. Rich, smooth and full-bodied."),
        ("Lost Lager", "Lager", 4.5, 20, "Crisp hoppy lager. Refreshingly hoppy German-style lager."),
    ]),

    # Timothy Taylor
    ("Timothy Taylor", "Yorkshire", [
        ("Landlord", "Pale Ale", 4.3, 35, "Multiple award-winning pale ale. The perfect balance of malt and hops."),
        ("Boltmaker", "Bitter", 4.0, 30, "Premium bitter. Rich, full-bodied and perfectly balanced."),
        ("Golden Best", "Golden Ale", 3.5, 28, "Refreshing golden ale. Light, crisp and wonderfully drinkable."),
        ("Knowle Spring", "Blonde Ale", 4.2, 32, "Blonde beer with a citrus aroma."),
    ]),

    # Fuller's
    ("Fuller's", "London", [
        ("London Pride", "Bitter", 4.7, 31, "London's most iconic beer. Smooth, balanced and distinctly malty."),
        ("ESB", "Strong Ale", 5.9, 35, "Extra Special Bitter. Full-bodied premium bitter."),
        ("Frontier", "Lager", 4.5, 30, "Craft lager. Clean, crisp and refreshing."),
        ("Oliver's Island", "Golden Ale", 4.3, 25, "Golden beer with tropical fruit flavours."),
    ]),

    # Adnams
    ("Adnams", "Suffolk", [
        ("Southwold Bitter", "Bitter", 3.7, 32, "Classic English bitter. Well-balanced session ale."),
        ("Ghost Ship", "Pale Ale", 4.5, 45, "Citrus pale ale. Refreshingly bold."),
        ("Mosaic", "Pale Ale", 4.1, 40, "American-hopped pale ale with tropical flavours."),
        ("Jack Brand Dry Hopped Lager", "Lager", 4.5, 35, "Premium dry-hopped lager."),
    ]),

    # Black Sheep
    ("Black Sheep Brewery", "Yorkshire", [
        ("Best Bitter", "Bitter", 3.8, 34, "Classic Yorkshire bitter. Full-flavoured and distinctive."),
        ("Riggwelter", "Strong Ale", 5.9, 42, "Strong Yorkshire ale. Rich and complex."),
        ("Golden Sheep", "Golden Ale", 4.3, 38, "Refreshing golden ale with citrus notes."),
    ]),

    # St Austell
    ("St Austell Brewery", "Cornwall", [
        ("Tribute", "Pale Ale", 4.2, 38, "Cornish pale ale. Light, hoppy and refreshing."),
        ("Proper Job", "IPA", 5.5, 55, "Cornish IPA. Massively hopped and full of flavour."),
        ("Korev", "Lager", 4.8, 20, "Cornish lager. Crisp and refreshing."),
        ("Clouded Yellow", "Pale Ale", 4.0, 35, "Citrus pale ale with American hops."),
    ]),

    # Greene King
    ("Greene King", "Suffolk", [
        ("Abbot Ale", "Amber Ale", 5.0, 32, "Premium amber ale. Rich, smooth and distinctive."),
        ("IPA", "IPA", 3.6, 35, "Classic English IPA. Perfectly balanced."),
        ("Old Speckled Hen", "Amber Ale", 5.0, 30, "Premium English ale. Smooth and malty."),
    ]),

    # Theakston
    ("T&R Theakston", "Yorkshire", [
        ("Old Peculier", "Strong Ale", 5.6, 32, "Legendary old ale. Rich, dark and complex."),
        ("Best Bitter", "Bitter", 3.8, 30, "Classic Yorkshire bitter. Well-balanced session ale."),
        ("Lightfoot", "Golden Ale", 4.1, 35, "Refreshing golden ale with citrus notes."),
    ]),

    # Marston's
    ("Marston's", "Staffordshire", [
        ("Pedigree", "Bitter", 4.5, 32, "Burton bitter. Smooth, balanced and distinctive."),
        ("61 Deep", "IPA", 6.1, 45, "Bold IPA with intense hop flavours."),
        ("Resolution", "Lager", 4.7, 25, "Premium British lager."),
    ]),

    # Wells & Young's
    ("Wells & Young's", "Bedford", [
        ("Bombardier", "Bitter", 4.1, 32, "English premium bitter. Bold and distinctive."),
        ("Young's Bitter", "Bitter", 3.7, 30, "Classic London bitter. Well-balanced and refreshing."),
        ("Courage Best", "Bitter", 4.0, 28, "Traditional English bitter."),
    ]),

    # Beavertown
    ("Beavertown Brewery", "London", [
        ("Gamma Ray", "Pale Ale", 5.4, 45, "American pale ale. Tropical, juicy and sessionable."),
        ("Neck Oil", "Session IPA", 4.3, 40, "Session IPA. Hoppy but dangerously drinkable."),
        ("Lupuloid", "IPA", 6.7, 60, "IPA with huge citrus and pine flavours."),
    ]),

    # Thornbridge
    ("Thornbridge Brewery", "Derbyshire", [
        ("Jaipur", "IPA", 5.9, 45, "Award-winning IPA. Bursting with citrus and tropical fruit."),
        ("Lukas", "Lager", 4.2, 25, "Bohemian pilsner. Crisp and refreshing."),
        ("Crackendale", "Pale Ale", 4.0, 38, "Session pale ale with tropical notes."),
        ("Lord Marples", "Bitter", 4.0, 35, "Classic English bitter."),
    ]),

    # Wychwood
    ("Wychwood Brewery", "Oxfordshire", [
        ("Hobgoblin", "Amber Ale", 5.2, 33, "Ruby beer with a distinctive chocolatey character."),
        ("Hobgoblin Gold", "Golden Ale", 4.5, 35, "Golden ale with zesty citrus notes."),
        ("Scarecrow", "Golden Ale", 4.7, 40, "Organic golden ale."),
    ]),

    # Shepherd Neame
    ("Shepherd Neame", "Kent", [
        ("Spitfire", "Amber Ale", 4.5, 35, "Kentish ale commemorating the Battle of Britain."),
        ("Bishop's Finger", "Strong Ale", 5.0, 38, "Strong Kentish ale. Rich and full-bodied."),
        ("Whitstable Bay", "Pale Ale", 4.0, 32, "Refreshing pale ale from Kent."),
        ("Master Brew", "Bitter", 3.7, 28, "Classic Kentish session bitter."),
    ]),

    # Hook Norton
    ("Hook Norton Brewery", "Oxfordshire", [
        ("Hooky Bitter", "Bitter", 3.6, 32, "Classic English session bitter."),
        ("Old Hooky", "Strong Ale", 4.6, 35, "Rich, strong ale with malty character."),
        ("Hooky Gold", "Golden Ale", 4.1, 38, "Golden beer with citrus notes."),
    ]),

    # Wadworth
    ("Wadworth", "Wiltshire", [
        ("6X", "Bitter", 4.3, 32, "Classic English bitter. Malty and smooth."),
        ("Horizon", "Golden Ale", 4.0, 35, "Golden ale with citrus and tropical notes."),
        ("Swordfish", "Lager", 5.0, 25, "Premium British lager."),
    ]),

    # Meantime
    ("Meantime Brewing", "London", [
        ("London Pale Ale", "Pale Ale", 4.3, 40, "Hoppy London pale ale."),
        ("London Lager", "Lager", 4.5, 30, "Crisp London lager."),
        ("Yakima Red", "Amber Ale", 4.1, 35, "American-style amber ale."),
    ]),

    # Camden Town
    ("Camden Town Brewery", "London", [
        ("Hells Lager", "Lager", 4.6, 25, "Unfiltered German-style lager."),
        ("Pale Ale", "Pale Ale", 4.0, 40, "West Coast-style pale ale."),
        ("Week Nite", "Session IPA", 4.5, 45, "Session IPA. Hoppy and refreshing."),
    ]),

    # Wild Beer Co
    ("Wild Beer Co", "Somerset", [
        ("Pogo", "Pale Ale", 4.1, 35, "Fruity sessionable pale ale."),
        ("Wildebeast", "IPA", 6.0, 45, "Bold and hoppy IPA."),
        ("Somerset Wild", "Golden Ale", 4.4, 30, "Refreshing golden ale."),
    ]),

    # Oakham Ales
    ("Oakham Ales", "Peterborough", [
        ("Citra", "Golden Ale", 4.2, 42, "Single-hopped citrus ale. Award-winning."),
        ("JHB", "Bitter", 3.8, 38, "Jeffrey Hudson Bitter. Golden session ale."),
        ("Inferno", "Blonde Ale", 4.0, 40, "Blonde ale with tropical fruit notes."),
    ]),
]


def add_beers():
    """Add all UK beers to the database."""
    print("\n" + "="*70)
    print("Adding UK Beers to Database")
    print("="*70 + "\n")

    total_breweries_created = 0
    total_beers_created = 0
    total_beers_skipped = 0

    for brewery_name, location, beers in UK_BEERS:
        print(f"\n{brewery_name} ({location})")
        print("-" * 70)

        # Get or create brewery
        brewery, created = Brewery.objects.get_or_create(
            name=brewery_name,
            defaults={
                'slug': slugify(brewery_name),
                'location': location,
                'description': f'{brewery_name} - British Brewery based in {location}'
            }
        )

        if created:
            total_breweries_created += 1
            print(f"  [+] Created brewery: {brewery_name}")

        # Add beers
        for beer_name, category_name, abv, ibu, description in beers:
            # Check if exists
            if Beer.objects.filter(name__iexact=beer_name, brewery=brewery).exists():
                print(f"    [-] Already exists: {beer_name}")
                total_beers_skipped += 1
                continue

            # Get or create category
            category, _ = Category.objects.get_or_create(
                name=category_name,
                defaults={
                    'slug': slugify(category_name),
                    'description': f'{category_name} beers'
                }
            )

            # Create beer
            try:
                beer = Beer.objects.create(
                    name=beer_name,
                    slug=slugify(f"{beer_name}-{brewery_name}"),
                    brewery=brewery,
                    category=category,
                    description=description,
                    abv=abv,
                    ibu=ibu,
                )
                print(f"    [+] Added: {beer_name} ({abv}% ABV)")
                total_beers_created += 1
            except Exception as e:
                print(f"    [!] Error adding {beer_name}: {e}")

    # Print summary
    print(f"\n{'='*70}")
    print("Summary")
    print("="*70)
    print(f"  Breweries created: {total_breweries_created}")
    print(f"  Beers added: {total_beers_created}")
    print(f"  Beers skipped (already exist): {total_beers_skipped}")
    print(f"  Total beers in database: {Beer.objects.count()}")
    print(f"  Total breweries: {Brewery.objects.count()}")
    print("="*70 + "\n")


if __name__ == '__main__':
    add_beers()
