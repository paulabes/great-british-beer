#!/usr/bin/env python
"""
Quick script to check superuser accounts in Django database.
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greatbritishbeer.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

print("=== SUPERUSER ACCOUNTS ===")
superusers = User.objects.filter(is_superuser=True)

if superusers.exists():
    for user in superusers:
        print(f"• Username: {user.username}")
        print(f"  Email: {user.email}")
        print(f"  Active: {user.is_active}")
        print(f"  Staff: {user.is_staff}")
        print(f"  Date joined: {user.date_joined}")
        print("-" * 30)
else:
    print("❌ No superuser accounts found!")
    print("\nTo create a superuser, run:")
    print("python manage.py createsuperuser")
