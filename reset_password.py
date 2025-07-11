#!/usr/bin/env python
"""
Script to reset password for a user
"""
import os
import sys
import django
from django.contrib.auth import get_user_model

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()


def reset_password():
    User = get_user_model()
    email = "paulabrahams.dev@gmail.com"
    
    try:
        user = User.objects.get(email=email)
        print(f"Found user: {user.email} (username: {user.username})")
        print(f"Is superuser: {user.is_superuser}")
        
        # Set new password
        new_password = input("Enter new password: ")
        confirm_password = input("Confirm password: ")
        
        if new_password != confirm_password:
            print("Passwords don't match!")
            return
            
        user.set_password(new_password)
        user.save()
        print("Password updated successfully!")
        
    except User.DoesNotExist:
        print(f"User with email {email} not found.")
        print("Available users:")
        for user in User.objects.all():
            print(f"- {user.email} (username: {user.username}, "
                  f"superuser: {user.is_superuser})")


if __name__ == "__main__":
    reset_password()
