from django.shortcuts import render
from django.db.models import Avg, Count
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.core.management import call_command
from reviews.models import Beer, Review


def home(request):
    """Home page view with featured content"""
    # Get featured beers with highest ratings
    featured_beers = Beer.objects.annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    ).filter(review_count__gte=1).order_by('-avg_rating')[:6]
    
    # Get latest reviews
    latest_reviews = Review.objects.filter(
        is_approved=True
    ).select_related('beer', 'user').order_by('-created_at')[:6]
    
    # Get beer of the month (highest rated beer this month)
    this_month = timezone.now().replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )
    beer_of_month = Beer.objects.annotate(
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


def populate_database(request):
    """Populate database with dummy data - requires secret parameter"""
    # Simple protection with a secret parameter
    secret = request.GET.get('secret', '')
    if secret != 'populate2026':
        return HttpResponse('Unauthorized', status=401)

    try:
        call_command('populate_db')
        return HttpResponse('''
            <h1>Database populated successfully!</h1>
            <p>The Railway database has been populated with:</p>
            <ul>
                <li>8 test users (password: password123)</li>
                <li>10 beer categories</li>
                <li>15 British breweries</li>
                <li>25 beers</li>
                <li>35 reviews with ratings and likes</li>
            </ul>
            <p><a href="/">Go to homepage</a></p>
        ''')
    except Exception as e:
        return HttpResponse(f'<h1>Error populating database</h1><pre>{str(e)}</pre>', status=500)
