from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from reviews.models import Category, Brewery, Beer, Review, ReviewLike, ReviewComment
from decimal import Decimal
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate database with dummy British beer data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to populate database...'))

        # Create users
        self.create_users()

        # Create categories
        self.create_categories()

        # Create breweries
        self.create_breweries()

        # Create beers
        self.create_beers()

        # Create reviews
        self.create_reviews()

        self.stdout.write(self.style.SUCCESS('Database populated successfully!'))

    def create_users(self):
        self.stdout.write('Creating users...')

        users_data = [
            {'username': 'john_smith', 'email': 'john@example.com', 'first_name': 'John', 'last_name': 'Smith'},
            {'username': 'emma_jones', 'email': 'emma@example.com', 'first_name': 'Emma', 'last_name': 'Jones'},
            {'username': 'oliver_brown', 'email': 'oliver@example.com', 'first_name': 'Oliver', 'last_name': 'Brown'},
            {'username': 'sophia_wilson', 'email': 'sophia@example.com', 'first_name': 'Sophia', 'last_name': 'Wilson'},
            {'username': 'james_taylor', 'email': 'james@example.com', 'first_name': 'James', 'last_name': 'Taylor'},
            {'username': 'emily_davies', 'email': 'emily@example.com', 'first_name': 'Emily', 'last_name': 'Davies'},
            {'username': 'george_evans', 'email': 'george@example.com', 'first_name': 'George', 'last_name': 'Evans'},
            {'username': 'charlotte_thomas', 'email': 'charlotte@example.com', 'first_name': 'Charlotte', 'last_name': 'Thomas'},
        ]

        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f'  Created user: {user.username}')

    def create_categories(self):
        self.stdout.write('Creating beer categories...')

        categories_data = [
            {'name': 'Pale Ale', 'description': 'Light to medium-bodied ales with a hoppy character'},
            {'name': 'IPA', 'description': 'India Pale Ales, hop-forward with higher ABV'},
            {'name': 'Bitter', 'description': 'Traditional British bitter ales'},
            {'name': 'Porter', 'description': 'Dark ales with roasted malt flavors'},
            {'name': 'Stout', 'description': 'Very dark, rich ales with coffee and chocolate notes'},
            {'name': 'Lager', 'description': 'Crisp, clean, bottom-fermented beers'},
            {'name': 'Wheat Beer', 'description': 'Beers brewed with a large proportion of wheat'},
            {'name': 'Golden Ale', 'description': 'Light, refreshing ales with golden color'},
            {'name': 'Amber Ale', 'description': 'Medium-bodied ales with caramel and toffee notes'},
            {'name': 'Brown Ale', 'description': 'Malty ales with nutty, caramel flavors'},
        ]

        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'slug': slugify(cat_data['name']),
                    'description': cat_data['description'],
                }
            )
            if created:
                self.stdout.write(f'  Created category: {category.name}')

    def create_breweries(self):
        self.stdout.write('Creating breweries...')

        breweries_data = [
            {'name': 'Fullers', 'location': 'London', 'founded_year': 1845},
            {'name': 'Timothy Taylor', 'location': 'Yorkshire', 'founded_year': 1858},
            {'name': 'Adnams', 'location': 'Suffolk', 'founded_year': 1872},
            {'name': 'Hook Norton', 'location': 'Oxfordshire', 'founded_year': 1849},
            {'name': 'Thornbridge', 'location': 'Derbyshire', 'founded_year': 2005},
            {'name': 'Meantime', 'location': 'London', 'founded_year': 1999},
            {'name': 'Brewdog', 'location': 'Scotland', 'founded_year': 2007},
            {'name': 'Camden Town Brewery', 'location': 'London', 'founded_year': 2010},
            {'name': 'Cloudwater', 'location': 'Manchester', 'founded_year': 2014},
            {'name': 'Beavertown', 'location': 'London', 'founded_year': 2011},
            {'name': 'Tiny Rebel', 'location': 'Wales', 'founded_year': 2012},
            {'name': 'Magic Rock', 'location': 'Yorkshire', 'founded_year': 2011},
            {'name': 'Marble', 'location': 'Manchester', 'founded_year': 1997},
            {'name': 'Wild Beer Co', 'location': 'Somerset', 'founded_year': 2012},
            {'name': 'Kernel', 'location': 'London', 'founded_year': 2009},
        ]

        for brewery_data in breweries_data:
            brewery, created = Brewery.objects.get_or_create(
                name=brewery_data['name'],
                defaults={
                    'slug': slugify(brewery_data['name']),
                    'location': brewery_data['location'],
                    'founded_year': brewery_data['founded_year'],
                    'description': f"A renowned British brewery based in {brewery_data['location']}, established in {brewery_data['founded_year']}.",
                }
            )
            if created:
                self.stdout.write(f'  Created brewery: {brewery.name}')

    def create_beers(self):
        self.stdout.write('Creating beers...')

        beers_data = [
            {'name': 'London Pride', 'brewery': 'Fullers', 'category': 'Bitter', 'abv': 4.7, 'ibu': 30, 'style': 'Best Bitter', 'description': 'A classic British ale with a rich balance of malty richness and distinctive hoppy bitterness.'},
            {'name': 'Landlord', 'brewery': 'Timothy Taylor', 'category': 'Pale Ale', 'abv': 4.3, 'ibu': 35, 'style': 'Pale Ale', 'description': 'Multi-award winning pale ale with a complex citrus hop aroma.'},
            {'name': 'Broadside', 'brewery': 'Adnams', 'category': 'Bitter', 'abv': 6.3, 'ibu': 40, 'style': 'Strong Bitter', 'description': 'A full-bodied premium bitter with a rich ruby color and fruity character.'},
            {'name': 'Old Hooky', 'brewery': 'Hook Norton', 'category': 'Bitter', 'abv': 4.6, 'ibu': 32, 'style': 'Best Bitter', 'description': 'A well-balanced, tawny-red classic English ale.'},
            {'name': 'Jaipur IPA', 'brewery': 'Thornbridge', 'category': 'IPA', 'abv': 5.9, 'ibu': 45, 'style': 'IPA', 'description': 'Citrus and tropical fruit aromas with a lasting bitter finish.'},
            {'name': 'London Lager', 'brewery': 'Meantime', 'category': 'Lager', 'abv': 4.5, 'ibu': 25, 'style': 'Premium Lager', 'description': 'A crisp, clean lager with subtle hop character.'},
            {'name': 'Punk IPA', 'brewery': 'Brewdog', 'category': 'IPA', 'abv': 5.6, 'ibu': 35, 'style': 'IPA', 'description': 'Tropical fruit, light caramel notes, and an all-out riot of grapefruit, pineapple and lychee.'},
            {'name': 'Hells Lager', 'brewery': 'Camden Town Brewery', 'category': 'Lager', 'abv': 4.6, 'ibu': 22, 'style': 'Craft Lager', 'description': 'A crisp Bavarian-style lager with a smooth, clean finish.'},
            {'name': 'DIPA', 'brewery': 'Cloudwater', 'category': 'IPA', 'abv': 8.0, 'ibu': 60, 'style': 'Double IPA', 'description': 'Bold, hop-forward double IPA with intense tropical fruit flavors.'},
            {'name': 'Gamma Ray', 'brewery': 'Beavertown', 'category': 'Pale Ale', 'abv': 5.4, 'ibu': 38, 'style': 'American Pale Ale', 'description': 'Bursting with juicy tropical and citrus flavors.'},
            {'name': 'Cwtch', 'brewery': 'Tiny Rebel', 'category': 'Amber Ale', 'abv': 4.6, 'ibu': 30, 'style': 'Red Ale', 'description': 'A Welsh red ale with balanced malt and hop character.'},
            {'name': 'High Wire', 'brewery': 'Magic Rock', 'category': 'Pale Ale', 'abv': 5.5, 'ibu': 42, 'style': 'West Coast Pale Ale', 'description': 'Grapefruit-led pale ale with pine resin and caramel.'},
            {'name': 'Pint', 'brewery': 'Marble', 'category': 'Bitter', 'abv': 3.9, 'ibu': 40, 'style': 'Session Bitter', 'description': 'Refreshing session bitter with citrus hop notes.'},
            {'name': 'Bibble', 'brewery': 'Wild Beer Co', 'category': 'IPA', 'abv': 4.2, 'ibu': 35, 'style': 'Session IPA', 'description': 'Light, hoppy session IPA with tropical fruit character.'},
            {'name': 'Table Beer', 'brewery': 'Kernel', 'category': 'Pale Ale', 'abv': 3.0, 'ibu': 28, 'style': 'Table Beer', 'description': 'Low ABV pale ale perfect for any occasion.'},
            {'name': 'Past Master 1891', 'brewery': 'Fullers', 'category': 'Porter', 'abv': 7.4, 'ibu': 45, 'style': 'Victorian Porter', 'description': 'Rich, complex porter brewed from a Victorian recipe.'},
            {'name': 'Old Peculier', 'brewery': 'Timothy Taylor', 'category': 'Brown Ale', 'abv': 5.6, 'ibu': 25, 'style': 'Old Ale', 'description': 'Full-bodied dark ale with rich fruit and malt flavors.'},
            {'name': 'Ghost Ship', 'brewery': 'Adnams', 'category': 'Pale Ale', 'abv': 4.5, 'ibu': 42, 'style': 'Pale Ale', 'description': 'Citrus and tropical fruit with a clean, bitter finish.'},
            {'name': 'Saint Petersburg', 'brewery': 'Thornbridge', 'category': 'Stout', 'abv': 7.7, 'ibu': 50, 'style': 'Imperial Stout', 'description': 'Complex imperial stout with coffee and chocolate notes.'},
            {'name': 'Yakima Red', 'brewery': 'Meantime', 'category': 'Amber Ale', 'abv': 4.1, 'ibu': 35, 'style': 'Red Ale', 'description': 'American-style red ale with caramel malt and citrus hops.'},
            {'name': 'Lost Lager', 'brewery': 'Brewdog', 'category': 'Lager', 'abv': 4.5, 'ibu': 30, 'style': 'Pilsner', 'description': 'A clean, crisp craft lager.'},
            {'name': 'Week Nite', 'brewery': 'Camden Town Brewery', 'category': 'Lager', 'abv': 4.0, 'ibu': 20, 'style': 'Session Lager', 'description': 'Easy-drinking session lager for any day of the week.'},
            {'name': 'Neck Oil', 'brewery': 'Beavertown', 'category': 'IPA', 'abv': 4.3, 'ibu': 28, 'style': 'Session IPA', 'description': 'Juicy session IPA with low bitterness.'},
            {'name': 'Clwb Tropicana', 'brewery': 'Tiny Rebel', 'category': 'IPA', 'abv': 5.5, 'ibu': 40, 'style': 'Fruited IPA', 'description': 'Tropical IPA bursting with pineapple, mango and peach.'},
            {'name': 'Cannonball', 'brewery': 'Magic Rock', 'category': 'IPA', 'abv': 7.4, 'ibu': 60, 'style': 'IPA', 'description': 'Intense, tropical, resinous IPA with massive hop character.'},
        ]

        for beer_data in beers_data:
            brewery = Brewery.objects.get(name=beer_data['brewery'])
            category = Category.objects.get(name=beer_data['category'])

            beer, created = Beer.objects.get_or_create(
                name=beer_data['name'],
                brewery=brewery,
                defaults={
                    'slug': slugify(f"{beer_data['name']}-{brewery.name}"),
                    'category': category,
                    'abv': Decimal(str(beer_data['abv'])),
                    'ibu': beer_data.get('ibu'),
                    'style': beer_data['style'],
                    'description': beer_data['description'],
                    'is_featured': random.choice([True, False, False, False]),
                }
            )
            if created:
                self.stdout.write(f'  Created beer: {beer.name}')

    def create_reviews(self):
        self.stdout.write('Creating reviews...')

        review_templates = [
            {
                'title': 'Excellent British ale',
                'content': 'This is a fantastic example of British brewing at its finest. The balance between malt and hops is perfect, with a smooth finish that leaves you wanting more.',
                'rating': 5
            },
            {
                'title': 'Solid pint',
                'content': 'A reliable choice at the pub. Good flavor profile with nice hop character. Would definitely order again.',
                'rating': 4
            },
            {
                'title': 'Outstanding flavor',
                'content': 'The complexity of flavors in this beer is remarkable. Notes of citrus, pine, and caramel work together beautifully. One of the best I have had.',
                'rating': 5
            },
            {
                'title': 'Decent session beer',
                'content': 'Perfect for a long session at the local. Not too strong, easy drinking, with enough flavor to keep it interesting.',
                'rating': 4
            },
            {
                'title': 'Classic British bitter',
                'content': 'Everything you would expect from a traditional bitter. Malty sweetness balanced with earthy hops. Very drinkable.',
                'rating': 4
            },
            {
                'title': 'Hop lovers dream',
                'content': 'If you love hops, this is for you. Bursting with citrus and tropical fruit flavors. The bitterness is bold but not overwhelming.',
                'rating': 5
            },
            {
                'title': 'Nice and refreshing',
                'content': 'Great refreshment on a warm day. Clean, crisp, and easy to drink. The perfect beer garden companion.',
                'rating': 4
            },
            {
                'title': 'Full of character',
                'content': 'This beer has real personality. Rich malt backbone with interesting hop notes. Very well crafted.',
                'rating': 5
            },
            {
                'title': 'Good but not great',
                'content': 'It is a solid beer, nothing wrong with it, but it does not particularly stand out. Would drink it again though.',
                'rating': 3
            },
            {
                'title': 'Perfectly balanced',
                'content': 'The balance in this beer is exceptional. Every element works together harmoniously. A masterclass in brewing.',
                'rating': 5
            },
        ]

        users = list(User.objects.all())
        beers = list(Beer.objects.all())

        # Create 30-40 reviews
        for i in range(35):
            user = random.choice(users)
            beer = random.choice(beers)
            template = random.choice(review_templates)

            # Skip if user already reviewed this beer
            if Review.objects.filter(user=user, beer=beer).exists():
                continue

            review = Review.objects.create(
                beer=beer,
                user=user,
                title=template['title'],
                content=template['content'],
                rating=template['rating'],
                appearance_rating=random.randint(3, 5),
                aroma_rating=random.randint(3, 5),
                taste_rating=random.randint(3, 5),
                mouthfeel_rating=random.randint(3, 5),
                serving_style=random.choice(['Draft', 'Bottle', 'Can']),
                is_approved=True,
                is_featured=random.choice([True, False, False, False]),
            )
            self.stdout.write(f'  Created review: {review.title} for {beer.name}')

            # Add some likes
            if random.random() < 0.3:
                num_likes = random.randint(1, 5)
                likers = random.sample(users, min(num_likes, len(users)))
                for liker in likers:
                    if liker != user:
                        ReviewLike.objects.get_or_create(review=review, user=liker)
