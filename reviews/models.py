from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from ckeditor.fields import RichTextField
from taggit.managers import TaggableManager
from PIL import Image
import os

User = get_user_model()


class Category(models.Model):
    """Beer categories (Ales, Lagers, Stouts, IPAs, etc.)"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('reviews:category_detail', kwargs={'slug': self.slug})


class Brewery(models.Model):
    """Brewery information"""
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200)
    website = models.URLField(blank=True)
    founded_year = models.PositiveIntegerField(null=True, blank=True)
    image = models.ImageField(upload_to='breweries/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Breweries'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('reviews:brewery_detail', kwargs={'slug': self.slug})


class Beer(models.Model):
    """Beer model with all beer information"""
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    brewery = models.ForeignKey(Brewery, on_delete=models.CASCADE, related_name='beers')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='beers')
    description = RichTextField(blank=True, help_text="Description of the beer")
    abv = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        validators=[MinValueValidator(0), MaxValueValidator(50)],
        help_text="Alcohol by volume percentage"
    )
    ibu = models.PositiveIntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(120)],
        help_text="International Bitterness Units"
    )
    color = models.CharField(max_length=50, blank=True, help_text="Beer color description")
    style = models.CharField(max_length=100, help_text="Beer style (e.g., IPA, Stout, Lager)")
    image = models.ImageField(upload_to='beers/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_featured = models.BooleanField(default=False, help_text="Featured on homepage")
    
    # SEO fields
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=200, blank=True)
    
    tags = TaggableManager(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['name', 'brewery']
    
    def __str__(self):
        return f"{self.name} by {self.brewery.name}"
    
    def get_absolute_url(self):
        return reverse('reviews:beer_detail', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        if self.image:
            img = Image.open(self.image.path)
            if img.height > 600 or img.width > 600:
                output_size = (600, 600)
                img.thumbnail(output_size)
                img.save(self.image.path)
    
    def get_average_rating(self):
        """Calculate average rating for this beer"""
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            from django.db.models import Avg
            return reviews.aggregate(Avg('rating'))['rating__avg']
        return None
    
    def get_review_count(self):
        """Get total number of approved reviews"""
        return self.reviews.filter(is_approved=True).count()
    
    def get_latest_reviews(self, limit=5):
        """Get latest approved reviews for this beer"""
        return self.reviews.filter(is_approved=True).order_by('-created_at')[:limit]


class Review(models.Model):
    """User reviews for beers"""
    RATING_CHOICES = [
        (1, '1 Star - Poor'),
        (2, '2 Stars - Fair'),
        (3, '3 Stars - Good'),
        (4, '4 Stars - Very Good'),
        (5, '5 Stars - Excellent'),
    ]
    
    beer = models.ForeignKey(Beer, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    title = models.CharField(max_length=200)
    content = RichTextField(help_text="Your detailed review")
    rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    
    # Detailed rating fields
    appearance_rating = models.PositiveIntegerField(
        choices=[(i, i) for i in range(1, 6)], 
        null=True, blank=True,
        help_text="Rate the appearance (1-5)"
    )
    aroma_rating = models.PositiveIntegerField(
        choices=[(i, i) for i in range(1, 6)], 
        null=True, blank=True,
        help_text="Rate the aroma (1-5)"
    )
    taste_rating = models.PositiveIntegerField(
        choices=[(i, i) for i in range(1, 6)], 
        null=True, blank=True,
        help_text="Rate the taste (1-5)"
    )
    mouthfeel_rating = models.PositiveIntegerField(
        choices=[(i, i) for i in range(1, 6)], 
        null=True, blank=True,
        help_text="Rate the mouthfeel (1-5)"
    )
    
    # Additional fields
    serving_style = models.CharField(
        max_length=50, 
        blank=True,
        help_text="How was it served? (bottle, draft, can)"
    )
    drinking_location = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Where did you drink it?"
    )
    food_pairing = models.CharField(
        max_length=200, 
        blank=True,
        help_text="What food did you pair it with?"
    )
    
    # Review management
    is_approved = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # SEO fields
    meta_description = models.CharField(max_length=160, blank=True)
    
    tags = TaggableManager(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['beer', 'user']  # One review per user per beer
    
    def __str__(self):
        return f"{self.title} - {self.beer.name} by {self.user.username}"
    
    def get_absolute_url(self):
        return reverse('reviews:review_detail', kwargs={'pk': self.pk})
    
    def get_star_range(self):
        """Return range for template star display"""
        return range(1, 6)
    
    def get_rating_percentage(self):
        """Convert rating to percentage for progress bars"""
        return (self.rating / 5) * 100


class ReviewLike(models.Model):
    """Likes for reviews"""
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['review', 'user']
    
    def __str__(self):
        return f"{self.user.username} likes {self.review.title}"


class ReviewComment(models.Model):
    """Comments on reviews"""
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.review.title}"
