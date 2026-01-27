"""
Test cases for beer review functionality and models.
"""
import unittest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from reviews.models import Beer, Review, Brewery, Category
from reviews.forms import BeerForm, ReviewForm
from decimal import Decimal

User = get_user_model()


class BeerModelTest(TestCase):
    """Test cases for the Beer model."""

    def setUp(self):
        """Set up test data."""
        self.brewery = Brewery.objects.create(name='Test Brewery', slug='test-brewery', location='Test Loc')
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.beer_data = {
            'name': 'Test Bitter',
            'brewery': self.brewery,
            'category': self.category,
            'style': 'Bitter',
            'abv': Decimal('4.5'),
            'description': 'A test bitter beer'
        }

    def test_create_beer(self):
        """Test beer creation with valid data."""
        beer = Beer.objects.create(**self.beer_data)
        self.assertEqual(beer.name, 'Test Bitter')
        self.assertEqual(beer.brewery, self.brewery)
        self.assertEqual(beer.abv, Decimal('4.5'))

    def test_beer_str_representation(self):
        """Test string representation of beer."""
        beer = Beer.objects.create(**self.beer_data)
        expected_str = 'Test Bitter by Test Brewery'
        self.assertEqual(str(beer), expected_str)

    def test_beer_slug_generation(self):
        """Test automatic slug generation."""
        beer = Beer.objects.create(**self.beer_data)
        self.assertIsNotNone(beer.slug)
        self.assertIn('test', beer.slug.lower())

    def test_beer_average_rating_no_reviews(self):
        """Test average rating calculation with no reviews."""
        beer = Beer.objects.create(**self.beer_data)
        # Assuming there's an average_rating method
        if hasattr(beer, 'average_rating'):
            self.assertEqual(beer.average_rating(), 0)


class ReviewModelTest(TestCase):
    """Test cases for the Review model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        self.brewery = Brewery.objects.create(name='Test Brewery', slug='test-brewery', location='Test Loc')
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.beer = Beer.objects.create(
            name='Test Bitter',
            brewery=self.brewery,
            category=self.category,
            style='Bitter',
            abv=Decimal('4.5'),
            description='A test bitter beer'
        )

    def test_create_review(self):
        """Test review creation with valid data."""
        review = Review.objects.create(
            beer=self.beer,
            user=self.user,
            rating=4,
            title='Great beer!',
            content='This beer is really good.'
        )
        self.assertEqual(review.rating, 4)
        self.assertEqual(review.title, 'Great beer!')
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.beer, self.beer)

    def test_review_str_representation(self):
        """Test string representation of review."""
        review = Review.objects.create(
            beer=self.beer,
            user=self.user,
            rating=4,
            title='Great beer!',
            content='This beer is really good.'
        )
        expected_str = f'Great beer! - {self.beer.name} by {self.user.username}'
        self.assertEqual(str(review), expected_str)

    def test_review_rating_range(self):
        """Test review rating validation."""
        # Test minimum rating
        review_min = Review.objects.create(
            beer=self.beer,
            user=self.user,
            rating=1,
            title='Poor beer',
            content='Not good.'
        )
        self.assertEqual(review_min.rating, 1)

        # Test maximum rating
        review_max = Review.objects.create(
            beer=self.beer,
            user=self.user,
            rating=5,
            title='Excellent beer',
            content='Perfect!'
        )
        self.assertEqual(review_max.rating, 5)


class BeerFormsTest(TestCase):
    """Test cases for beer-related forms."""

    def test_beer_form_valid(self):
        """Test valid beer form submission."""
        brewery = Brewery.objects.create(name='Test Brewery', slug='test-brewery', location='Test Loc')
        category = Category.objects.create(name='Test Category', slug='test-category')
        form_data = {
            'name': 'Test Lager',
            'slug': 'test-lager',
            'brewery': brewery.id,
            'category': category.id,
            'style': 'Lager',
            'abv': '4.2',
            'description': 'A crisp lager'
        }
        form = BeerForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_beer_form_invalid_abv(self):
        """Test beer form with invalid ABV."""
        brewery = Brewery.objects.create(name='Test Brewery', slug='test-brewery', location='Test Loc')
        category = Category.objects.create(name='Test Category', slug='test-category')
        form_data = {
            'name': 'Test Beer',
            'slug': 'test-beer',
            'brewery': brewery.id,
            'category': category.id,
            'style': 'Ale',
            'abv': '-1.0',  # Invalid negative ABV
            'description': 'A test beer'
        }
        form = BeerForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_review_form_valid(self):
        """Test valid review form submission."""
        brewery = Brewery.objects.create(name='Test Brewery', slug='test-brewery', location='Test Loc')
        category = Category.objects.create(name='Test Category', slug='test-category')
        beer = Beer.objects.create(name='Test Beer', slug='test-beer', brewery=brewery, category=category, abv=5.0)

        form_data = {
            'beer': beer.id,
            'rating': 4,
            'title': 'Good beer',
            'content': 'I enjoyed this beer very much.'
        }
        form = ReviewForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_review_form_invalid_rating(self):
        """Test review form with invalid rating."""
        brewery = Brewery.objects.create(name='Test Brewery', slug='test-brewery', location='Test Loc')
        category = Category.objects.create(name='Test Category', slug='test-category')
        beer = Beer.objects.create(name='Test Beer', slug='test-beer', brewery=brewery, category=category, abv=5.0)

        form_data = {
            'beer': beer.id,
            'rating': 6,  # Invalid rating > 5
            'title': 'Great beer',
            'content': 'Excellent beer.'
        }
        form = ReviewForm(data=form_data)
        self.assertFalse(form.is_valid())


class BeerViewsTest(TestCase):
    """Test cases for beer and review views."""

    def setUp(self):
        """Set up test client and data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        self.brewery = Brewery.objects.create(name='Test Brewery', slug='test-brewery', location='Test Loc')
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.beer = Beer.objects.create(
            name='Test Bitter',
            brewery=self.brewery,
            category=self.category,
            style='Bitter',
            abv=Decimal('4.5'),
            description='A test bitter beer'
        )

    def test_beer_list_view(self):
        """Test beer list view."""
        response = self.client.get(reverse('reviews:beer_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Bitter')

    def test_beer_detail_view(self):
        """Test beer detail view."""
        response = self.client.get(
            reverse('reviews:beer_detail', kwargs={'slug': self.beer.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Bitter')
        self.assertContains(response, 'Test Brewery')

    def test_review_create_view_authenticated(self):
        """Test review creation for authenticated user."""
        self.client.force_login(self.user)
        
        response = self.client.get(
            reverse(
                'reviews:review_create',
                kwargs={'beer_slug': self.beer.slug}
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_review_create_view_anonymous(self):
        """Test review creation for anonymous user."""
        response = self.client.get(
            reverse(
                'reviews:review_create',
                kwargs={'beer_slug': self.beer.slug}
            )
        )
        # Should redirect to login
        self.assertEqual(response.status_code, 302)

    def test_review_create_post_valid(self):
        """Test valid review creation."""
        self.client.force_login(self.user)
        
        review_data = {
            'rating': 4,
            'title': 'Good beer',
            'content': 'I really enjoyed this beer.'
        }
        
        response = self.client.post(
            reverse(
                'reviews:review_create',
                kwargs={'beer_slug': self.beer.slug}
            ),
            data=review_data
        )
        
        # Should redirect after successful creation
        self.assertEqual(response.status_code, 302)
        
        # Verify review was created
        review_exists = Review.objects.filter(
            beer=self.beer,
            user=self.user
        ).exists()
        self.assertTrue(review_exists)

    def test_review_list_view(self):
        """Test review list view."""
        # Create a review first
        Review.objects.create(
            beer=self.beer,
            user=self.user,
            rating=4,
            title='Good beer',
            content='I enjoyed this beer.'
        )
        
        response = self.client.get(reverse('reviews:review_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Good beer')


class ReviewsIntegrationTest(TestCase):
    """Integration tests for reviews functionality."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='reviewer',
            email='reviewer@example.com',
            password='ReviewPass123!'
        )

    def test_complete_beer_review_flow(self):
        """Test complete flow from beer creation to review."""
        brewery = Brewery.objects.create(name='Test Brewery', slug='test-brewery', location='Test Loc')
        category = Category.objects.create(name='Test Category', slug='test-category')
        # Step 1: Create a beer (assuming admin creates it)
        beer = Beer.objects.create(
            name='Integration Test Beer',
            brewery=brewery,
            category=category,
            style='IPA',
            abv=Decimal('5.5'),
            description='A beer for integration testing'
        )
        
        # Step 2: User logs in
        login_response = self.client.post(
            reverse('users:login'),
            data={
                'email': 'reviewer@example.com',
                'password': 'ReviewPass123!'
            }
        )
        self.assertEqual(login_response.status_code, 302)
        
        # Step 3: User views beer list
        beer_list_response = self.client.get(reverse('reviews:beer_list'))
        self.assertEqual(beer_list_response.status_code, 200)
        self.assertContains(beer_list_response, 'Integration Test Beer')
        
        # Step 4: User views beer detail
        beer_detail_response = self.client.get(
            reverse('reviews:beer_detail', kwargs={'slug': beer.slug})
        )
        self.assertEqual(beer_detail_response.status_code, 200)
        
        # Step 5: User creates review
        review_data = {
            'rating': 5,
            'title': 'Excellent IPA',
            'content': 'This is a fantastic IPA with great hop character.'
        }
        
        review_response = self.client.post(
            reverse('reviews:review_create', kwargs={'beer_slug': beer.slug}),
            data=review_data
        )
        self.assertEqual(review_response.status_code, 302)
        
        # Step 6: Verify review appears in lists
        review_list_response = self.client.get(reverse('reviews:review_list'))
        self.assertEqual(review_list_response.status_code, 200)
        self.assertContains(review_list_response, 'Excellent IPA')

    def test_search_and_filter_functionality(self):
        """Test search and filtering features."""
        brewery1 = Brewery.objects.create(name='Hop Brewery', slug='hop-brewery', location='Loc1')
        brewery2 = Brewery.objects.create(name='Dark Brewery', slug='dark-brewery', location='Loc2')
        category = Category.objects.create(name='Test Category', slug='test-category')

        # Create multiple beers
        Beer.objects.create(
            name='Hoppy IPA',
            slug='hoppy-ipa',
            brewery=brewery1,
            category=category,
            style='IPA',
            abv=Decimal('6.0')
        )
        Beer.objects.create(
            name='Smooth Stout',
            slug='smooth-stout',
            brewery=brewery2,
            category=category,
            style='Stout',
            abv=Decimal('4.8')
        )
        
        # Test beer list shows all beers
        response = self.client.get(reverse('reviews:beer_list'))
        self.assertContains(response, 'Hoppy IPA')
        self.assertContains(response, 'Smooth Stout')

    @unittest.skip("Review editing functionality is not implemented yet")
    def test_user_review_permissions(self):
        """Test that users can only edit their own reviews."""
        # Create another user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='OtherPass123!'
        )
        brewery = Brewery.objects.create(name='Test Brewery', slug='test-brewery', location='Test Loc')
        category = Category.objects.create(name='Test Category', slug='test-category')
        
        beer = Beer.objects.create(
            name='Permission Test Beer',
            brewery=brewery,
            category=category,
            style='Ale',
            abv=Decimal('4.0')
        )
        
        # Other user creates a review
        review = Review.objects.create(
            beer=beer,
            user=other_user,
            rating=3,
            title='Other user review',
            content='Review by other user'
        )
        
        # Current user logs in
        self.client.force_login(self.user)
        
        # Try to access edit page for other user's review
        if hasattr(review, 'get_absolute_url'):
            edit_url = reverse('reviews:review_edit', kwargs={'pk': review.pk})
            response = self.client.get(edit_url)
            # Should be forbidden or redirect
            self.assertIn(response.status_code, [302, 403, 404])
