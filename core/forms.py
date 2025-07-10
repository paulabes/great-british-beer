from django import forms
from .models import NewsletterSubscription


class NewsletterSubscriptionForm(forms.ModelForm):
    """Form for newsletter subscription"""
    
    class Meta:
        model = NewsletterSubscription
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email address'
            })
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if NewsletterSubscription.objects.filter(
                email=email, is_active=True).exists():
            raise forms.ValidationError(
                "This email is already subscribed to our newsletter."
            )
        return email
