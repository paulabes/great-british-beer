from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import authenticate
from .models import User


class CustomUserCreationForm(UserCreationForm):
    """Custom user registration form"""
    email = forms.EmailField(
        required=True, 
        help_text="Required. Enter a valid email address.",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        max_length=30, 
        required=False, 
        help_text="Optional.",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30, 
        required=False, 
        help_text="Optional.",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    """Custom user change form for admin"""
    class Meta:
        model = User
        fields = '__all__'


class UserUpdateForm(forms.ModelForm):
    """Form for users to update their profile"""
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'bio', 'location',
            'avatar', 'date_of_birth', 'favorite_beer_style',
            'website', 'twitter_handle', 'show_email', 'show_location'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 4}),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        user_id = self.instance.id
        if User.objects.filter(email=email).exclude(id=user_id).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email


class LoginForm(forms.Form):
    """Custom login form"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email address'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    remember_me = forms.BooleanField(required=False)
    
    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        
        if email and password:
            try:
                user = User.objects.get(email=email)
                user = authenticate(username=user.username, password=password)
                if not user:
                    raise forms.ValidationError("Invalid email or password.")
                if not user.is_active:
                    raise forms.ValidationError("This account is inactive.")
            except User.DoesNotExist:
                raise forms.ValidationError("Invalid email or password.")
        
        return self.cleaned_data
