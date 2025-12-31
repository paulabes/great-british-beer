from django.shortcuts import render
from django.db.models import Avg, Count
from django.utils import timezone
from reviews.models import Beer, Review


def home(request):
    """Home page view with featured content"""
    # Get featured beers with highest ratings
    featured_beers = Beer.objects.select_related('brewery', 'category').annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    ).filter(review_count__gte=1).order_by('-avg_rating')[:6]
    
    # Get latest reviews
    latest_reviews = Review.objects.filter(
        is_approved=True
    ).select_related('beer', 'user', 'beer__brewery').order_by('-created_at')[:6]
    
    # Get beer of the month (highest rated beer this month)
    this_month = timezone.now().replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )
    beer_of_month = Beer.objects.select_related('brewery').annotate(
        avg_rating=Avg('reviews__rating')
    ).filter(
        reviews__created_at__gte=this_month,
        reviews__is_approved=True
    ).order_by('-avg_rating').first()
    
    context = {
        'featured_beers': featured_beers,
        'latest_reviews': latest_reviews,
        'beer_of_month': beer_of_month,
    }
    return render(request, 'core/home.html', context)


def about(request):
    """About page view"""
    return render(request, 'core/about.html')


def contact(request):
    """Contact page view"""
    return render(request, 'core/contact.html')
