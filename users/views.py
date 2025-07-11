from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Avg
from .forms import CustomUserCreationForm, UserUpdateForm
from .models import User
from reviews.models import Review


def register(request):
    """User registration view.
    
    Handles GET and POST requests for user registration.
    On successful registration, redirects to login page.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Registration successful! You can now log in.'
            )
            return redirect('users:login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


def user_login(request):
    """User login view.
    
    Handles email-based authentication for users.
    On successful login, redirects to home or next URL.
    """
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        if email and password:
            try:
                user_obj = User.objects.get(email=email)
                if user_obj.check_password(password) and user_obj.is_active:
                    login(request, user_obj)
                    messages.success(
                        request,
                        f'Welcome back, {user_obj.username}!'
                    )
                    next_url = request.GET.get('next', 'core:home')
                    return redirect(next_url)
                else:
                    messages.error(request, 'Invalid credentials.')
            except User.DoesNotExist:
                messages.error(request, 'Invalid credentials.')
        else:
            messages.error(
                request,
                'Please enter both email and password.'
            )
    
    return render(request, 'users/login.html')


def user_logout(request):
    """User logout view"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('core:home')


@login_required
def profile(request):
    """User profile view"""
    user = request.user
    reviews = Review.objects.filter(
        user=user, is_approved=True
    ).select_related('beer').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(reviews, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    stats = {
        'total_reviews': reviews.count(),
        'avg_rating': reviews.aggregate(Avg('rating'))['rating__avg'],
        'beer_count': reviews.values('beer').distinct().count(),
    }
    
    context = {
        'profile_user': user,
        'page_obj': page_obj,
        'stats': stats,
    }
    return render(request, 'users/profile.html', context)


@login_required
def edit_profile(request):
    """Edit user profile view"""
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('users:profile')
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'users/edit_profile.html', {'form': form})


def public_profile(request, username):
    """Public profile view for other users"""
    user = get_object_or_404(User, username=username)
    reviews = Review.objects.filter(
        user=user, is_approved=True
    ).select_related('beer').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(reviews, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    stats = {
        'total_reviews': reviews.count(),
        'avg_rating': reviews.aggregate(Avg('rating'))['rating__avg'],
        'beer_count': reviews.values('beer').distinct().count(),
    }
    
    context = {
        'profile_user': user,
        'page_obj': page_obj,
        'stats': stats,
        'is_own_profile': request.user == user,
    }
    return render(request, 'users/public_profile.html', context)
