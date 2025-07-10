from django.contrib.auth.models import AbstractUser
from django.db import models
from PIL import Image


class User(AbstractUser):
    """Extended User model with additional fields"""
    email = models.EmailField(unique=True)
    bio = models.TextField(max_length=500, blank=True, help_text="Tell us about yourself")
    location = models.CharField(max_length=100, blank=True, help_text="Your location")
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        help_text="Profile picture"
    )
    date_of_birth = models.DateField(null=True, blank=True)
    favorite_beer_style = models.CharField(max_length=100, blank=True)
    is_verified = models.BooleanField(default=False, help_text="Email verified")
    
    # Social media links
    website = models.URLField(blank=True)
    twitter_handle = models.CharField(max_length=50, blank=True)
    
    # Privacy settings
    show_email = models.BooleanField(default=False, help_text="Show email on profile")
    show_location = models.BooleanField(default=True, help_text="Show location on profile")
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.username
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        if self.avatar:
            img = Image.open(self.avatar.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.avatar.path)
    
    @property
    def full_name(self):
        """Return full name or username if names not provided"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    @property
    def profile_picture(self):
        """Alias for avatar field for template compatibility"""
        return self.avatar
    
    def get_review_count(self):
        """Get total number of approved reviews by this user"""
        return self.reviews.filter(is_approved=True).count()
    
    def get_average_rating(self):
        """Get average rating given by this user"""
        from django.db.models import Avg
        approved_reviews = self.reviews.filter(is_approved=True)
        avg = approved_reviews.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else None
