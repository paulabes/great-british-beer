from django.test import TestCase, Client
from django.urls import reverse
from django.db import connection
from django.conf import settings
from django.test.utils import override_settings
from reviews.models import Beer, Category, Brewery, Review, ReviewComment
from django.contrib.auth import get_user_model

User = get_user_model()

@override_settings(DEBUG=True)
class BeerDetailPerformanceTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.brewery = Brewery.objects.create(name='Test Brewery', slug='test-brewery')
        self.beer = Beer.objects.create(
            name='Test Beer',
            slug='test-beer',
            brewery=self.brewery,
            category=self.category,
            abv=5.0
        )

        # Create 5 reviews with different users
        for i in range(5):
            user = User.objects.create_user(username=f'user{i}', email=f'user{i}@example.com', password='password')
            review = Review.objects.create(
                beer=self.beer,
                user=user,
                title=f'Review {i}',
                content='Content',
                rating=5,
                is_approved=True,
                appearance_rating=5,
                aroma_rating=5,
                taste_rating=5,
                mouthfeel_rating=5
            )
            # Create 2 comments per review
            for j in range(2):
                comment_user = User.objects.create_user(username=f'comment_user_{i}_{j}', email=f'comment_user_{i}_{j}@example.com', password='password')
                ReviewComment.objects.create(
                    review=review,
                    user=comment_user,
                    content=f'Comment {j}',
                    is_approved=True
                )

    def test_beer_detail_queries(self):
        url = reverse('reviews:beer_detail', kwargs={'slug': self.beer.slug})

        # Measure queries
        # Expected queries with optimization:
        # 1. Beer (select_related brewery, category)
        # 2. Reviews Count (pagination)
        # 3. Aggregates (stats)
        # 4. Reviews List (paginated, select_related user, annotate likes)
        # 5. Comments (prefetch with filtered queryset)
        # 6. Comment Users (prefetch - actually managed by select_related inside Prefetch?)
        #
        # If I use Prefetch('comments', queryset=ReviewComment.objects.select_related('user')),
        # Django usually does 1 query for comments+users join.
        #
        # So total queries should be 5.

        # NOTE:
        # 1. Beer query
        # 2. Count query (Pagination)
        # 3. Aggregate query
        # 4. Reviews fetch
        # 5. Comments fetch
        #
        # Total 5.

        with self.assertNumQueries(5):
             response = self.client.get(url)
             self.assertIn('reviews', response.context)
             self.assertEqual(len(response.context['reviews']), 5)
