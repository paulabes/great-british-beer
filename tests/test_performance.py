from django.test import TestCase
from django.db.models import Avg, Count, Q
from reviews.models import Beer, Brewery, Category, Review, User
from django.template import Template, Context

class PerformanceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.brewery = Brewery.objects.create(name='Test Brewery', slug='test-brewery')
        self.beer = Beer.objects.create(name='Test Beer', slug='test-beer', brewery=self.brewery, category=self.category, abv=5.0)
        Review.objects.create(beer=self.beer, user=self.user, title='R1', content='C1', rating=5, is_approved=True)

    def test_beer_list_annotation_usage(self):
        # Simulate the query in beer_list view (updated to use average_rating)
        queryset = Beer.objects.select_related('brewery', 'category').annotate(
            average_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True)),
            review_count=Count('reviews', filter=Q(reviews__is_approved=True))
        )
        beer = queryset.first()

        # Verify annotations are present
        self.assertEqual(beer.average_rating, 5.0)
        self.assertEqual(beer.review_count, 1)

        # Check template rendering
        t = Template("{% if beer.average_rating %}HAS_RATING{% else %}NO_RATING{% endif %}")
        c = Context({'beer': beer})
        rendered = t.render(c)
        print(f"Rendered: {rendered}")

        # This should now pass
        self.assertEqual(rendered, "HAS_RATING")
