from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count, Case, When, Value, IntegerField, Prefetch
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django import forms
from .models import Beer, Review, Category, Brewery, ReviewLike, ReviewComment
from .forms import ReviewForm, BeerSearchForm, CommentForm, BeerForm


def beer_list(request):
    """List all beers with search and filtering"""
    form = BeerSearchForm(request.GET)
    beers = Beer.objects.select_related('brewery', 'category').annotate(
        avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True)),
        review_count=Count('reviews', filter=Q(reviews__is_approved=True))
    )
    
    if form.is_valid():
        query = form.cleaned_data.get('query')
        if query:
            beers = beers.filter(
                Q(name__icontains=query) |
                Q(brewery__name__icontains=query) |
                Q(style__icontains=query) |
                Q(description__icontains=query)
            )
        
        category = form.cleaned_data.get('category')
        if category:
            beers = beers.filter(category=category)
        
        min_rating = form.cleaned_data.get('min_rating')
        if min_rating:
            beers = beers.filter(avg_rating__gte=int(min_rating))
        
        abv_range = form.cleaned_data.get('abv_range')
        if abv_range == 'low':
            beers = beers.filter(abv__lte=4)
        elif abv_range == 'medium':
            beers = beers.filter(abv__gt=4, abv__lte=7)
        elif abv_range == 'high':
            beers = beers.filter(abv__gt=7)
        
        sort_by = form.cleaned_data.get('sort_by')
        if sort_by:
            if sort_by in ['avg_rating', '-avg_rating']:
                beers = beers.order_by(f'{sort_by}', '-review_count')
            else:
                beers = beers.order_by(sort_by)
        else:
            beers = beers.order_by('-created_at')
    else:
        beers = beers.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(beers, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get categories and breweries for filters
    categories = Category.objects.all().order_by('name')
    breweries = Brewery.objects.all().order_by('name')

    context = {
        'beers': page_obj,  # Template expects 'beers'
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'form': form,
        'total_beers': beers.count(),
        'categories': categories,
        'breweries': breweries,
    }
    return render(request, 'reviews/beer_list.html', context)


def beer_detail(request, slug):
    """Detailed view of a single beer"""
    beer = get_object_or_404(Beer.objects.select_related('brewery', 'category'), slug=slug)
    reviews = Review.objects.filter(
        beer=beer, is_approved=True
    ).select_related('user').prefetch_related(
        Prefetch('comments', queryset=ReviewComment.objects.filter(is_approved=True).select_related('user'))
    ).annotate(
        likes_count=Count('likes', distinct=True)
    ).order_by('-created_at')
    
    # Pagination for reviews
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calculate statistics in one query
    aggregates = reviews.aggregate(
        avg_rating=Avg('rating'),
        total_reviews=Count('id'),
        star_1=Count(Case(When(rating=1, then=1), output_field=IntegerField())),
        star_2=Count(Case(When(rating=2, then=1), output_field=IntegerField())),
        star_3=Count(Case(When(rating=3, then=1), output_field=IntegerField())),
        star_4=Count(Case(When(rating=4, then=1), output_field=IntegerField())),
        star_5=Count(Case(When(rating=5, then=1), output_field=IntegerField())),
    )

    total_reviews = aggregates['total_reviews']

    # Statistics
    stats = {
        'avg_rating': aggregates['avg_rating'],
        'total_reviews': total_reviews,
        'rating_distribution': {},
    }
    
    # Calculate rating distribution
    for i in range(1, 6):
        count = aggregates[f'star_{i}']
        stats['rating_distribution'][i] = {
            'count': count,
            'percentage': (count / total_reviews * 100) if total_reviews > 0 else 0
        }
    
    # Check if user has already reviewed this beer
    user_review = None
    if request.user.is_authenticated:
        user_review = Review.objects.filter(beer=beer, user=request.user).first()
    
    context = {
        'beer': beer,
        'page_obj': page_obj,
        'stats': stats,
        'user_review': user_review,
        'reviews': page_obj,
    }
    return render(request, 'reviews/beer_detail.html', context)


@login_required
def review_create(request, beer_slug=None):
    """Create a new review"""
    beer = None
    if beer_slug:
        beer = get_object_or_404(Beer, slug=beer_slug)
        # Check if user already reviewed this beer
        if Review.objects.filter(beer=beer, user=request.user).exists():
            messages.warning(request, 'You have already reviewed this beer.')
            return redirect('reviews:beer_detail', slug=beer.slug)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, user=request.user)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            if beer:
                review.beer = beer
            review.save()
            form.save_m2m()  # Save tags
            
            messages.success(
                request,
                'Your review has been submitted and is pending approval.'
            )
            return redirect('reviews:beer_detail', slug=review.beer.slug)
    else:
        initial_data = {}
        if beer:
            initial_data['beer'] = beer
        form = ReviewForm(initial=initial_data, user=request.user)
        if beer:
            form.fields['beer'].widget = forms.HiddenInput()
    
    context = {
        'form': form,
        'beer': beer,
        'page_title': f'Review {beer.name}' if beer else 'Write a Review',
    }
    return render(request, 'reviews/review_form.html', context)


def review_detail(request, pk):
    """Detailed view of a single review"""
    review = get_object_or_404(Review, pk=pk, is_approved=True)
    comments = review.comments.filter(is_approved=True).select_related('user')
    
    # Handle comment form
    comment_form = None
    if request.user.is_authenticated:
        if request.method == 'POST':
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.review = review
                comment.user = request.user
                comment.save()
                messages.success(request, 'Your comment has been added.')
                return redirect('reviews:review_detail', pk=review.pk)
        else:
            comment_form = CommentForm()
    
    # Check if user has liked this review
    user_liked = False
    if request.user.is_authenticated:
        user_liked = ReviewLike.objects.filter(review=review, user=request.user).exists()
    
    context = {
        'review': review,
        'comments': comments,
        'comment_form': comment_form,
        'user_liked': user_liked,
        'like_count': review.likes.count(),
    }
    return render(request, 'reviews/review_detail.html', context)


@login_required
@require_POST
def toggle_like(request, review_id):
    """Toggle like status for a review (AJAX)"""
    review = get_object_or_404(Review, id=review_id, is_approved=True)
    like, created = ReviewLike.objects.get_or_create(
        review=review, user=request.user
    )
    
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    
    return JsonResponse({
        'liked': liked,
        'like_count': review.likes.count()
    })


def category_detail(request, slug):
    """List beers in a specific category"""
    category = get_object_or_404(Category, slug=slug)
    beers = Beer.objects.filter(category=category).select_related('brewery').annotate(
        avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True)),
        review_count=Count('reviews', filter=Q(reviews__is_approved=True))
    ).order_by('-avg_rating', '-review_count')
    
    # Pagination
    paginator = Paginator(beers, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
        'total_beers': beers.count(),
    }
    return render(request, 'reviews/category_detail.html', context)


def brewery_list(request):
    """List all breweries"""
    breweries = Brewery.objects.annotate(
        beer_count=Count('beers')
    ).order_by('name')

    # Pagination
    paginator = Paginator(breweries, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'breweries': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'total_breweries': breweries.count(),
    }
    return render(request, 'reviews/brewery_list.html', context)


def brewery_detail(request, slug):
    """List beers from a specific brewery"""
    brewery = get_object_or_404(Brewery, slug=slug)
    beers = Beer.objects.filter(brewery=brewery).select_related('category').annotate(
        avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True)),
        review_count=Count('reviews', filter=Q(reviews__is_approved=True))
    ).order_by('-avg_rating', '-review_count')

    # Pagination
    paginator = Paginator(beers, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'brewery': brewery,
        'page_obj': page_obj,
        'total_beers': beers.count(),
    }
    return render(request, 'reviews/brewery_detail.html', context)


def review_list(request):
    """List all approved reviews"""
    reviews = Review.objects.filter(is_approved=True).select_related(
        'beer', 'beer__brewery', 'user'
    ).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(reviews, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'total_reviews': reviews.count(),
    }
    return render(request, 'reviews/review_list.html', context)


@login_required
def beer_create(request):
    """Create a new beer (restricted to staff users)"""
    if not request.user.is_staff:
        messages.error(request, 'You must be a staff member to add new beers.')
        return redirect('reviews:beer_list')
    
    if request.method == 'POST':
        form = BeerForm(request.POST, request.FILES)
        if form.is_valid():
            beer = form.save()
            messages.success(
                request, f'Beer "{beer.name}" has been added successfully!'
            )
            return redirect('reviews:beer_detail', slug=beer.slug)
    else:
        form = BeerForm()
    
    context = {
        'form': form,
        'title': 'Add New Beer'
    }
    return render(request, 'reviews/beer_form.html', context)
