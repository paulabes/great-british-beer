"""
Test cases for user authentication and profile functionality.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from users.forms import CustomUserCreationForm

User = get_user_model()


class UserModelTest(TestCase):
    """Test cases for the custom User model."""

    def setUp(self):
        """Set up test data."""
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'TestPass123!'
        }

    def test_create_user(self):
        """Test user creation with valid data."""
        user = User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password']
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('TestPass123!'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """Test superuser creation."""
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='AdminPass123!'
        )
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_user_str_representation(self):
        """Test string representation of user."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        self.assertEqual(str(user), 'testuser')


class UserFormsTest(TestCase):
    """Test cases for user forms."""

    def test_custom_user_creation_form_valid(self):
        """Test valid user registration form."""
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_custom_user_creation_form_duplicate_email(self):
        """Test form validation with duplicate email."""
        # Create existing user
        User.objects.create_user(
            username='existing',
            email='test@example.com',
            password='TestPass123!'
        )
        
        # Try to create user with same email
        form_data = {
            'username': 'newuser',
            'email': 'test@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_custom_user_creation_form_password_mismatch(self):
        """Test form validation with password mismatch."""
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'TestPass123!',
            'password2': 'DifferentPass123!'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())


class UserViewsTest(TestCase):
    """Test cases for user views."""

    def setUp(self):
        """Set up test client and user data."""
        self.client = Client()
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!'
        }
        self.login_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!'
        }

    def test_register_view_get(self):
        """Test GET request to registration page."""
        response = self.client.get(reverse('users:register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Account')

    def test_register_view_post_valid(self):
        """Test POST request with valid registration data."""
        response = self.client.post(
            reverse('users:register'),
            data=self.user_data
        )
        # Should redirect to login page after successful registration
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            User.objects.filter(username='testuser').exists()
        )

    def test_register_view_post_invalid(self):
        """Test POST request with invalid registration data."""
        invalid_data = self.user_data.copy()
        invalid_data['email'] = 'invalid-email'
        
        response = self.client.post(
            reverse('users:register'),
            data=invalid_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            User.objects.filter(username='testuser').exists()
        )

    def test_login_view_get(self):
        """Test GET request to login page."""
        response = self.client.get(reverse('users:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')

    def test_login_view_post_valid(self):
        """Test POST request with valid login credentials."""
        # Create user first
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        
        response = self.client.post(
            reverse('users:login'),
            data=self.login_data
        )
        # Should redirect after successful login
        self.assertEqual(response.status_code, 302)

    def test_login_view_post_invalid(self):
        """Test POST request with invalid login credentials."""
        response = self.client.post(
            reverse('users:login'),
            data={
                'email': 'nonexistent@example.com',
                'password': 'WrongPassword123!'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid')

    def test_profile_view_authenticated(self):
        """Test profile view for authenticated user."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        self.client.force_login(user)
        
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')

    def test_profile_view_anonymous(self):
        """Test profile view for anonymous user."""
        response = self.client.get(reverse('users:profile'))
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)

    def test_logout_view(self):
        """Test logout functionality."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        self.client.force_login(user)
        
        response = self.client.post(reverse('users:logout'))
        # Should redirect after logout
        self.assertEqual(response.status_code, 302)


class UserIntegrationTest(TestCase):
    """Integration tests for user functionality."""

    def setUp(self):
        """Set up test client."""
        self.client = Client()

    def test_complete_user_registration_flow(self):
        """Test complete user registration and login flow."""
        # Step 1: Register new user
        registration_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!'
        }
        
        register_response = self.client.post(
            reverse('users:register'),
            data=registration_data
        )
        self.assertEqual(register_response.status_code, 302)
        
        # Verify user was created
        user_exists = User.objects.filter(username='newuser').exists()
        self.assertTrue(user_exists)
        
        # Step 2: Login with new credentials
        login_response = self.client.post(
            reverse('users:login'),
            data={
                'email': 'newuser@example.com',
                'password': 'StrongPass123!'
            }
        )
        self.assertEqual(login_response.status_code, 302)
        
        # Step 3: Access profile page
        profile_response = self.client.get(reverse('users:profile'))
        self.assertEqual(profile_response.status_code, 200)
        self.assertContains(profile_response, 'newuser')

    def test_authentication_required_views(self):
        """Test that protected views require authentication."""
        protected_urls = [
            reverse('users:profile'),
        ]
        
        for url in protected_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertIn('login', response.url)
