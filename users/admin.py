from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Custom admin for User model"""
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = [
        'username', 'email', 'first_name', 'last_name',
        'is_verified', 'is_staff', 'date_joined'
    ]
    list_filter = [
        'is_staff', 'is_superuser', 'is_active',
        'is_verified', 'date_joined'
    ]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': (
                'bio', 'location', 'avatar', 'date_of_birth',
                'favorite_beer_style', 'is_verified'
            )
        }),
        ('Social Media', {
            'fields': ('website', 'twitter_handle')
        }),
        ('Privacy Settings', {
            'fields': ('show_email', 'show_location')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('email', 'first_name', 'last_name')
        }),
    )
    
    def get_queryset(self, request):
        """Add review count to queryset"""
        qs = super().get_queryset(request)
        return qs.prefetch_related('reviews')
    
    def review_count(self, obj):
        """Display review count in admin"""
        return obj.reviews.filter(is_approved=True).count()
    review_count.short_description = 'Reviews'
    
    list_display = list_display + ['review_count']
