from django.contrib.sitemaps import Sitemap
from .models import Beer, Review


class BeerSitemap(Sitemap):
    """Sitemap for beer pages"""
    changefreq = "weekly"
    priority = 0.8
    
    def items(self):
        return Beer.objects.all()
    
    def lastmod(self, obj):
        return obj.updated_at


class ReviewSitemap(Sitemap):
    """Sitemap for review pages"""
    changefreq = "monthly"
    priority = 0.6
    
    def items(self):
        return Review.objects.filter(is_approved=True)
    
    def lastmod(self, obj):
        return obj.updated_at
