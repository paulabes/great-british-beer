from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from reviews.models import Beer, Brewery, Category, Review

User = get_user_model()

class PerformanceIssueTest(TestCase):
    def test_beer_list_ratings_display_and_performance(self):
        # Setup data
        client = Client()

        # Create dependencies
        brewery = Brewery.objects.create(
            name='Performance Brewery',
            slug='performance-brewery',
            location='London'
        )

        category = Category.objects.create(
            name='Performance Ale',
            slug='performance-ale'
        )

        # Create Beer
        beer = Beer.objects.create(
            name='Slow Beer',
            slug='slow-beer',
            brewery=brewery,
            category=category,
            abv=5.0,
            style='Ale',
            description='A beer to test performance.'
        )

        # Create User
        user = User.objects.create_user(
            username='perf_user',
            email='perf@example.com',
            password='password'
        )

        # Create Review (Approved)
        Review.objects.create(
            beer=beer,
            user=user,
            rating=5,
            title='Great!',
            content='Loved it.',
            is_approved=True
        )

        # Capture queries
        # Expected: 2 counts (paginator + total_beers), 2 sidebars (categories, breweries), 1 fetch = 5
        # If N+1 existed, it would be 6 (1 beer).
        with self.assertNumQueries(5):
            url = reverse('reviews:beer_list')
            response = client.get(url)

        content = response.content.decode('utf-8')

        # Check context
        beers = response.context['beers']
        beer_obj = beers[0]

        # Check HTML content for rating section
        # We check for "1 review" because "5.0" matches ABV too!
        # The rating section should now be VISIBLE because we fixed the template.
        self.assertIn("1 review", content, "Rating section should be visible now!")
