from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from reviews.models import Beer, Review, Brewery, Category, ReviewLike, ReviewComment
from decimal import Decimal

User = get_user_model()

@override_settings(DEBUG=True)
class PerformanceTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        self.brewery = Brewery.objects.create(name='Test Brewery', slug='test-brewery')
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.beer = Beer.objects.create(
            name='Test Beer',
            slug='test-beer',
            brewery=self.brewery,
            category=self.category,
            style='Test Style',
            abv=Decimal('5.0'),
            description='Test Description'
        )
        self.review = Review.objects.create(
            beer=self.beer,
            user=self.user,
            rating=5,
            title='Test Review',
            content='Test Content',
            is_approved=True
        )
        # Create a like and a comment to ensure counts are non-zero
        ReviewLike.objects.create(review=self.review, user=self.user)
        ReviewComment.objects.create(review=self.review, user=self.user, content="Test Comment")

    def test_beer_list_queries(self):
        url = reverse('reviews:beer_list')
        # Expected:
        # 1. Paginator count
        # 2. Beer list (paginated)
        # 3. Categories list
        # 4. Breweries list
        # Total: 4
        with self.assertNumQueries(4):
            self.client.get(url)

    def test_brewery_list_queries(self):
        url = reverse('reviews:brewery_list')
        # Expected:
        # 1. Paginator count
        # 2. Brewery list (paginated)
        # Total: 2
        with self.assertNumQueries(2):
            self.client.get(url)

    def test_brewery_detail_queries(self):
        url = reverse('reviews:brewery_detail', kwargs={'slug': self.brewery.slug})
        # Expected:
        # 1. Get brewery
        # 2. Paginator count (beers)
        # 3. Beer list (paginated)
        # Total: 3
        with self.assertNumQueries(3):
            self.client.get(url)

    def test_review_list_queries(self):
        url = reverse('reviews:review_list')
        # Expected:
        # 1. Paginator count
        # 2. Review list (paginated with annotations)
        # Total: 2
        with self.assertNumQueries(2):
            self.client.get(url)
