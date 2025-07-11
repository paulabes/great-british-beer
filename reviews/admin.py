from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Avg, Count
from .models import Category, Brewery, Beer, Review, ReviewLike, ReviewComment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin for beer categories"""
    list_display = ['name', 'slug', 'beer_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at']
    
    def beer_count(self, obj):
        """Show number of beers in category"""
        return obj.beers.count()
    beer_count.short_description = 'Beers'


@admin.register(Brewery)
class BreweryAdmin(admin.ModelAdmin):
    """Admin for breweries"""
    list_display = ['name', 'location', 'founded_year', 'beer_count', 'created_at']
    list_filter = ['location', 'founded_year', 'created_at']
    search_fields = ['name', 'location', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at']
    
    def beer_count(self, obj):
        """Show number of beers from brewery"""
        return obj.beers.count()
    beer_count.short_description = 'Beers'


class ReviewInline(admin.TabularInline):
    """Inline reviews for beer admin"""
    model = Review
    extra = 0
    readonly_fields = ['user', 'rating', 'created_at', 'is_approved']
    fields = ['user', 'title', 'rating', 'is_approved', 'created_at']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Beer)
class BeerAdmin(admin.ModelAdmin):
    """Admin for beers"""
    list_display = [
        'name', 'brewery', 'category', 'abv', 'style',
        'average_rating', 'review_count', 'is_featured', 'created_at'
    ]
    list_filter = [
        'category', 'brewery', 'is_featured', 'created_at',
        'abv', 'style'
    ]
    search_fields = ['name', 'brewery__name', 'style', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at', 'average_rating', 'review_count']
    filter_horizontal = ['tags']
    inlines = [ReviewInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'brewery', 'category', 'description')
        }),
        ('Beer Details', {
            'fields': ('abv', 'ibu', 'color', 'style', 'image')
        }),
        ('SEO & Marketing', {
            'fields': ('meta_description', 'meta_keywords', 'is_featured')
        }),
        ('Tags & Statistics', {
            'fields': ('tags', 'average_rating', 'review_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def average_rating(self, obj):
        """Display average rating with stars"""
        avg = obj.get_average_rating()
        if avg:
            stars = '★' * int(avg) + '☆' * (5 - int(avg))
            return format_html(
                '<span title="{}">{}</span>',
                f'{avg:.1f}', stars
            )
        return 'No ratings'
    average_rating.short_description = 'Avg Rating'
    
    def review_count(self, obj):
        """Display review count"""
        count = obj.get_review_count()
        return f"{count} review{'s' if count != 1 else ''}"
    review_count.short_description = 'Reviews'
    
    actions = ['make_featured', 'remove_featured']
    
    def make_featured(self, request, queryset):
        """Mark selected beers as featured"""
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} beers marked as featured.')
    make_featured.short_description = 'Mark as featured'
    
    def remove_featured(self, request, queryset):
        """Remove featured status from selected beers"""
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} beers removed from featured.')
    remove_featured.short_description = 'Remove from featured'


class ReviewCommentInline(admin.TabularInline):
    """Inline comments for review admin"""
    model = ReviewComment
    extra = 0
    readonly_fields = ['user', 'created_at']
    fields = ['user', 'content', 'is_approved', 'created_at']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin for reviews"""
    list_display = [
        'title', 'beer', 'user', 'rating_display', 'is_approved',
        'is_featured', 'like_count', 'created_at'
    ]
    list_filter = [
        'rating', 'is_approved', 'is_featured', 'created_at',
        'beer__category', 'beer__brewery'
    ]
    search_fields = [
        'title', 'content', 'user__username', 'beer__name',
        'beer__brewery__name'
    ]
    readonly_fields = [
        'created_at', 'updated_at', 'like_count', 'comment_count'
    ]
    filter_horizontal = ['tags']
    inlines = [ReviewCommentInline]
    
    fieldsets = (
        ('Review Information', {
            'fields': ('beer', 'user', 'title', 'content', 'rating')
        }),
        ('Detailed Ratings', {
            'fields': (
                'appearance_rating', 'aroma_rating',
                'taste_rating', 'mouthfeel_rating'
            ),
            'classes': ('collapse',)
        }),
        ('Additional Details', {
            'fields': (
                'serving_style', 'drinking_location', 'food_pairing'
            ),
            'classes': ('collapse',)
        }),
        ('Management', {
            'fields': ('is_approved', 'is_featured', 'meta_description')
        }),
        ('Tags & Statistics', {
            'fields': ('tags', 'like_count', 'comment_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def rating_display(self, obj):
        """Display rating with stars"""
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span title="{}/5">{}</span>', obj.rating, stars)
    rating_display.short_description = 'Rating'
    
    def like_count(self, obj):
        """Display like count"""
        count = obj.likes.count()
        return f"{count} like{'s' if count != 1 else ''}"
    like_count.short_description = 'Likes'
    
    def comment_count(self, obj):
        """Display comment count"""
        count = obj.comments.count()
        return f"{count} comment{'s' if count != 1 else ''}"
    comment_count.short_description = 'Comments'
    
    actions = ['approve_reviews', 'unapprove_reviews', 'make_featured']
    
    def approve_reviews(self, request, queryset):
        """Approve selected reviews"""
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} reviews approved.')
    approve_reviews.short_description = 'Approve selected reviews'
    
    def unapprove_reviews(self, request, queryset):
        """Unapprove selected reviews"""
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} reviews unapproved.')
    unapprove_reviews.short_description = 'Unapprove selected reviews'
    
    def make_featured(self, request, queryset):
        """Mark selected reviews as featured"""
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} reviews marked as featured.')
    make_featured.short_description = 'Mark as featured'


@admin.register(ReviewLike)
class ReviewLikeAdmin(admin.ModelAdmin):
    """Admin for review likes"""
    list_display = ['review', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['review__title', 'user__username']
    readonly_fields = ['created_at']


@admin.register(ReviewComment)
class ReviewCommentAdmin(admin.ModelAdmin):
    """Admin for review comments"""
    list_display = ['review', 'user', 'content_preview', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['content', 'user__username', 'review__title']
    readonly_fields = ['created_at']
    
    def content_preview(self, obj):
        """Show preview of comment content"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'
    
    actions = ['approve_comments', 'unapprove_comments']
    
    def approve_comments(self, request, queryset):
        """Approve selected comments"""
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} comments approved.')
    approve_comments.short_description = 'Approve selected comments'
    
    def unapprove_comments(self, request, queryset):
        """Unapprove selected comments"""
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} comments unapproved.')
    unapprove_comments.short_description = 'Unapprove selected comments'
