from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from reviews.models import Category, Brewery, Beer, Review
from django.utils.text import slugify

User = get_user_model()


class Command(BaseCommand):
    help = 'Setup sample data for Great British Beer blog'

    def add_arguments(self, parser):
        parser.add_argument(
            '--with-reviews',
            action='store_true',
            help='Create sample reviews (requires a superuser to exist)',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Setting up Great British Beer sample data...')
        )

        # Create categories if they don't exist
        categories_data = [
            {
                'name': 'Pale Ales',
                'description': 'Light-colored ales with a hoppy flavor and citrus notes'
            },
            {
                'name': 'Bitter',
                'description': 'Traditional British bitter ales with balanced malt and hop flavors'
            },
            {
                'name': 'IPA',
                'description': 'India Pale Ales with bold hop flavors and tropical fruit notes'
            },
            {
                'name': 'Stout',
                'description': 'Dark, rich beers with roasted malt flavors'
            },
            {
                'name': 'Lager',
                'description': 'Crisp, clean-tasting bottom-fermented beers'
            },
        ]

        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'slug': slugify(cat_data['name']),
                    'description': cat_data['description']
                }
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')

        # Create breweries if they don't exist
        breweries_data = [
            {
                'name': 'St. Austell Brewery',
                'description': 'Founded in 1851, St. Austell Brewery is Cornwall\'s largest independent brewery, famous for Tribute and other quality ales.',
                'location': 'St. Austell, Cornwall',
                'website': 'https://www.staustellbrewery.co.uk',
                'founded_year': 1851
            },
            {
                'name': 'Fuller\'s',
                'description': 'London\'s historic brewery since 1845, brewing premium ales including London Pride and ESB.',
                'location': 'Chiswick, London',
                'website': 'https://www.fullers.co.uk',
                'founded_year': 1845
            },
            {
                'name': 'BrewDog',
                'description': 'Scottish craft brewery founded in 2007, pioneers of the craft beer revolution in the UK.',
                'location': 'Ellon, Scotland',
                'website': 'https://www.brewdog.com',
                'founded_year': 2007
            },
        ]

        for brewery_data in breweries_data:
            brewery, created = Brewery.objects.get_or_create(
                name=brewery_data['name'],
                defaults={
                    'slug': slugify(brewery_data['name']),
                    'description': brewery_data['description'],
                    'location': brewery_data['location'],
                    'website': brewery_data['website'],
                    'founded_year': brewery_data['founded_year']
                }
            )
            if created:
                self.stdout.write(f'Created brewery: {brewery.name}')

        # Create beers if they don't exist
        beers_data = [
            {
                'name': 'Tribute Pale Ale',
                'brewery': 'St. Austell Brewery',
                'category': 'Pale Ales',
                'description': '<p>A classic Cornish pale ale with a fresh, hoppy taste and citrus aroma. Brewed with the finest Cornish water and locally sourced ingredients.</p>',
                'abv': 4.20,
                'ibu': 42,
                'color': 'Golden',
                'style': 'Pale Ale',
                'is_featured': True
            },
            {
                'name': 'London Pride',
                'brewery': 'Fuller\'s',
                'category': 'Bitter',
                'description': '<p>London\'s famous premium bitter with a smooth, well-balanced flavor of malt and hops. A true icon of British brewing.</p>',
                'abv': 4.70,
                'ibu': 35,
                'color': 'Amber',
                'style': 'Bitter',
                'is_featured': True
            },
            {
                'name': 'Punk IPA',
                'brewery': 'BrewDog',
                'category': 'IPA',
                'description': '<p>A bold, aggressive IPA with tropical fruit flavors and a bitter finish. The beer that started the craft beer revolution in the UK.</p>',
                'abv': 5.60,
                'ibu': 65,
                'color': 'Golden',
                'style': 'IPA',
                'is_featured': True
            },
        ]

        for beer_data in beers_data:
            brewery = Brewery.objects.get(name=beer_data['brewery'])
            category = Category.objects.get(name=beer_data['category'])
            
            beer, created = Beer.objects.get_or_create(
                name=beer_data['name'],
                brewery=brewery,
                defaults={
                    'slug': slugify(beer_data['name']),
                    'category': category,
                    'description': beer_data['description'],
                    'abv': beer_data['abv'],
                    'ibu': beer_data['ibu'],
                    'color': beer_data['color'],
                    'style': beer_data['style'],
                    'is_featured': beer_data['is_featured']
                }
            )
            if created:
                self.stdout.write(f'Created beer: {beer.name}')

        # Create sample reviews if requested and superuser exists
        if options['with_reviews']:
            try:
                admin_user = User.objects.filter(is_superuser=True).first()
                if not admin_user:
                    self.stdout.write(
                        self.style.WARNING(
                            'No superuser found. Create one first with: python manage.py createsuperuser'
                        )
                    )
                    return

                reviews_data = [
                    {
                        'beer': 'Tribute Pale Ale',
                        'title': 'Classic Cornish Excellence',
                        'content': '<p>This is a superb example of what a British pale ale should be. The citrus hop character balances beautifully with the malt backbone, creating a refreshing and satisfying drink.</p><p>Perfect for enjoying in a traditional pub setting or with fish and chips. The 4.2% ABV makes it very sessionable.</p>',
                        'rating': 5,
                        'appearance_rating': 4,
                        'aroma_rating': 5,
                        'taste_rating': 5,
                        'mouthfeel_rating': 4,
                        'serving_style': 'Draft',
                        'drinking_location': 'Local pub in Cornwall',
                        'food_pairing': 'Fish and chips',
                        'is_approved': True
                    },
                    {
                        'beer': 'London Pride',
                        'title': 'London\'s Finest Bitter',
                        'content': '<p>A wonderfully balanced bitter that represents the best of traditional London brewing. The malt sweetness is perfectly complemented by the hop bitterness.</p><p>This beer has history in every sip and pairs excellently with traditional British fare.</p>',
                        'rating': 4,
                        'appearance_rating': 4,
                        'aroma_rating': 4,
                        'taste_rating': 4,
                        'mouthfeel_rating': 4,
                        'serving_style': 'Bottle',
                        'drinking_location': 'Fuller\'s pub in London',
                        'food_pairing': 'Bangers and mash',
                        'is_approved': True
                    },
                    {
                        'beer': 'Punk IPA',
                        'title': 'Revolutionary Craft Beer',
                        'content': '<p>This IPA changed the British beer scene forever. The tropical fruit hop flavors are intense and satisfying, with a bitter finish that leaves you wanting more.</p><p>A bold statement beer that showcases what modern British brewing can achieve.</p>',
                        'rating': 4,
                        'appearance_rating': 5,
                        'aroma_rating': 5,
                        'taste_rating': 4,
                        'mouthfeel_rating': 4,
                        'serving_style': 'Can',
                        'drinking_location': 'BrewDog bar',
                        'food_pairing': 'Spicy curry',
                        'is_approved': True
                    },
                ]

                for review_data in reviews_data:
                    beer = Beer.objects.get(name=review_data['beer'])
                    
                    review, created = Review.objects.get_or_create(
                        beer=beer,
                        user=admin_user,
                        defaults={
                            'title': review_data['title'],
                            'content': review_data['content'],
                            'rating': review_data['rating'],
                            'appearance_rating': review_data['appearance_rating'],
                            'aroma_rating': review_data['aroma_rating'],
                            'taste_rating': review_data['taste_rating'],
                            'mouthfeel_rating': review_data['mouthfeel_rating'],
                            'serving_style': review_data['serving_style'],
                            'drinking_location': review_data['drinking_location'],
                            'food_pairing': review_data['food_pairing'],
                            'is_approved': review_data['is_approved']
                        }
                    )
                    if created:
                        self.stdout.write(f'Created review: {review.title}')

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating reviews: {str(e)}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                '\nSample data setup complete!\n'
                'Next steps:\n'
                '1. Create a superuser: python manage.py createsuperuser\n'
                '2. Run with reviews: python manage.py setup_sample_data --with-reviews\n'
                '3. Start the server: python manage.py runserver'
            )
        )
