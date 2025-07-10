from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Avg, Count
from .forms import CustomUserCreationForm, UserUpdateForm, LoginForm
from .models import User
from reviews.models import Review


def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('users:login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


def user_login(request):
    """User login view"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                user = User.objects.get(email=email)
                user = authenticate(request, username=user.username, password=password)
                if user:
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.username}!')
                    next_url = request.GET.get('next', 'core:home')
                    return redirect(next_url)
            except User.DoesNotExist:
                form.add_error(None, 'Invalid email or password.')
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})


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
