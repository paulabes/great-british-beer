from django import forms
from django.contrib.auth import get_user_model
from .models import Beer, Review, ReviewComment, Category, Brewery
from ckeditor.widgets import CKEditorWidget

User = get_user_model()


class ReviewForm(forms.ModelForm):
    """Form for creating and editing beer reviews"""
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Add Bootstrap classes to form fields
        for field_name, field in self.fields.items():
            if field_name not in ['content', 'rating', 'appearance_rating', 
                                 'aroma_rating', 'taste_rating', 'mouthfeel_rating']:
                field.widget.attrs['class'] = 'form-control'
    
    class Meta:
        model = Review
        fields = [
            'beer', 'title', 'content', 'rating',
            'appearance_rating', 'aroma_rating', 'taste_rating', 'mouthfeel_rating',
            'serving_style', 'drinking_location', 'food_pairing', 'tags'
        ]
        widgets = {
            'beer': forms.Select(attrs={'class': 'form-select'}),
            'content': CKEditorWidget(),
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'appearance_rating': forms.Select(attrs={'class': 'form-select'}),
            'aroma_rating': forms.Select(attrs={'class': 'form-select'}),
            'taste_rating': forms.Select(attrs={'class': 'form-select'}),
            'mouthfeel_rating': forms.Select(attrs={'class': 'form-select'}),
            'tags': forms.TextInput(attrs={
                'placeholder': 'Add tags separated by commas',
                'class': 'form-control'
            }),
        }


class BeerForm(forms.ModelForm):
    """Form for adding new beers (admin use)"""
    
    class Meta:
        model = Beer
        fields = [
            'name', 'brewery', 'category', 'description', 'abv', 'ibu',
            'color', 'style', 'image', 'tags', 'meta_description', 'meta_keywords'
        ]
        widgets = {
            'description': CKEditorWidget(),
            'meta_description': forms.Textarea(attrs={'rows': 3}),
        }


class BeerSearchForm(forms.Form):
    """Form for searching beers"""
    search = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search beers, breweries, or styles...',
            'class': 'form-control'
        })
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    brewery = forms.ModelChoiceField(
        queryset=Brewery.objects.all(),
        required=False,
        empty_label="All Breweries",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    min_rating = forms.ChoiceField(
        choices=[('', 'Any Rating')] + [(i, f'{i}+ Stars') for i in range(1, 6)],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    sort_by = forms.ChoiceField(
        choices=[
            ('name', 'Name A-Z'),
            ('-name', 'Name Z-A'),
            ('-created_at', 'Newest First'),
            ('created_at', 'Oldest First'),
            ('-avg_rating', 'Highest Rated'),
            ('avg_rating', 'Lowest Rated'),
        ],
        required=False,
        initial='-created_at',
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class CommentForm(forms.ModelForm):
    """Form for adding comments to reviews"""
    
    class Meta:
        model = ReviewComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Share your thoughts on this review...',
                'class': 'form-control'
            })
        }


# Alias for backward compatibility
ReviewCommentForm = CommentForm


class NewsletterSignupForm(forms.Form):
    """Newsletter signup form"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your email',
            'class': 'form-control'
        })
    )
    name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Your name (optional)',
            'class': 'form-control'
        })
    )
