from django.test import TestCase, Client, override_settings
from reviews.models import Beer, Brewery, Category
from django.db import connection, reset_queries
from django.urls import reverse

@override_settings(DEBUG=True)
class PerformanceTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Ale", slug="ale")
        self.brewery = Brewery.objects.create(name="Brewery X", slug="brewery-x", location="London")

        beers = []
        for i in range(15):
            beers.append(Beer(
                name=f"Beer {i}",
                slug=f"beer-{i}",
                brewery=self.brewery,
                category=self.category,
                abv=5.0,
                style="Stout"
            ))
        Beer.objects.bulk_create(beers)

    def test_beer_list_queries(self):
        # Warm up
        self.client.get(reverse('reviews:beer_list'))
        reset_queries()

        print("\n--- Capturing queries for beer_list ---")
        # Optimized expectation:
        # 1. Count (Paginator)
        # 2. Select (Page)
        # 3. Categories
        # 4. Breweries
        # Redundant count removed.
        with self.assertNumQueries(4):
            response = self.client.get(reverse('reviews:beer_list'))

        print(f"Total Queries executed: {len(connection.queries)}")
        for i, q in enumerate(connection.queries):
             print(f"{i+1}. {q['sql']}")
