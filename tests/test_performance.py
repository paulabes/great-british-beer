from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from reviews.models import Beer, Review, Brewery, Category, ReviewLike, ReviewComment
from decimal import Decimal
from django.test.utils import CaptureQueriesContext
from django.db import connection

User = get_user_model()

class ReviewListPerformanceTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password')

        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.brewery = Brewery.objects.create(name='Test Brewery', slug='test-brewery')

        self.beer = Beer.objects.create(
            name='Test Beer',
            slug='test-beer',
            brewery=self.brewery,
            category=self.category,
            abv=Decimal('5.0'),
            style='Lager'
        )

        # Create 10 reviews
        for i in range(10):
            reviewer = User.objects.create_user(username=f'reviewer{i}', email=f'reviewer{i}@example.com', password='password')
            review = Review.objects.create(
                beer=self.beer,
                user=reviewer,
                rating=5,
                title=f'Review {i}',
                content=f'Content {i}',
                is_approved=True
            )

            # Add some likes
            ReviewLike.objects.create(review=review, user=self.user)

            # Add some comments
            ReviewComment.objects.create(review=review, user=self.user, content='Comment', is_approved=True)

    def test_review_list_queries(self):
        url = reverse('reviews:review_list')

        # Determine expected query count
        with CaptureQueriesContext(connection) as ctx:
             response = self.client.get(url)
             self.assertEqual(response.status_code, 200)

        print(f"Number of queries: {len(ctx.captured_queries)}")
        # We expect optimized queries
        # 1 main query (with annotations) + pagination count + misc = ~4-5
        self.assertLess(len(ctx.captured_queries), 10)
