from django.shortcuts import render
from django.db.models import Avg, Count
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.core.management import call_command
from reviews.models import Beer, Review
import os
import random
from django.conf import settings


def home(request):
    """Home page view with featured content"""
    # Get sponsored beers (or random beers if no sponsored ones exist)
    sponsored_beers = Beer.objects.filter(is_sponsored=True).select_related('brewery', 'category').annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    )[:3]

    # If no sponsored beers, use random beers as placeholders
    if not sponsored_beers.exists():
        sponsored_beers = Beer.objects.select_related('brewery', 'category').annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        ).order_by('?')[:3]

    # Get top 6 beers by average star rating
    featured_beers = Beer.objects.select_related('brewery', 'category').annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    ).order_by('-avg_rating', '-review_count')[:6]

    # Get latest reviews
    latest_reviews = Review.objects.filter(
        is_approved=True
    ).select_related('beer', 'beer__brewery', 'user').order_by('-created_at')[:6]

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

    # Get a random beer image from the beers folder
    hero_beer_image = None
    beers_folder = os.path.join(settings.MEDIA_ROOT, 'beers')
    if os.path.exists(beers_folder):
        beer_images = [f for f in os.listdir(beers_folder)
                       if f.endswith(('.jpg', '.jpeg', '.png', '.webp')) and
                       os.path.isfile(os.path.join(beers_folder, f))]
        if beer_images:
            random_image = random.choice(beer_images)
            # Verify the file exists before setting
            image_path = os.path.join(beers_folder, random_image)
            if os.path.exists(image_path):
                hero_beer_image = f'beers/{random_image}'

    context = {
        'sponsored_beers': sponsored_beers,
        'featured_beers': featured_beers,
        'latest_reviews': latest_reviews,
        'beer_of_month': beer_of_month,
        'hero_beer_image': hero_beer_image,
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


def scrape_beers_daily(request):
    """Scrape beers from brewery websites - requires secret parameter"""
    # Simple protection with a secret parameter
    secret = request.GET.get('secret', '')
    if secret != 'scrape2026':
        return HttpResponse('Unauthorized', status=401)

    try:
        # Run the daily scraping command
        from io import StringIO
        import sys

        # Capture output
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        call_command('daily_beer_scrape')

        output = sys.stdout.getvalue()
        sys.stdout = old_stdout

        beer_count = Beer.objects.count()

        return HttpResponse(f'''
            <h1>Daily Beer Scraping Complete!</h1>
            <p>Total beers in database: {beer_count}</p>
            <h3>Scraping Log:</h3>
            <pre style="background: #f5f5f5; padding: 20px; border-radius: 8px; max-height: 600px; overflow-y: scroll;">
{output}
            </pre>
            <p><a href="/">Go to homepage</a></p>
        ''')
    except Exception as e:
        return HttpResponse(f'<h1>Error scraping beers</h1><pre>{str(e)}</pre>', status=500)
