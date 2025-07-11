#!/usr/bin/env python
"""
Create a superuser for the Great British Beer Django application.
"""
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greatbritishbeer.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def check_existing_superusers():
    """Check what superusers already exist."""
    print("=== EXISTING SUPERUSER ACCOUNTS ===")
    superusers = User.objects.filter(is_superuser=True)
    
    if superusers.exists():
        for user in superusers:
            print(f"• Username: {user.username}")
            print(f"  Email: {user.email}")
            print(f"  Active: {user.is_active}")
            print(f"  Date joined: {user.date_joined}")
            print("-" * 30)
        return True
    else:
        print("❌ No superuser accounts found!")
        return False

def create_default_superuser():
    """Create a default superuser if none exist."""
    if not User.objects.filter(is_superuser=True).exists():
        print("\n🔧 Creating default superuser...")
        user = User.objects.create_superuser(
            username='admin',
            email='admin@greatbritishbeer.com',
            password='admin123!'
        )
        print(f"✅ Created superuser: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Password: admin123!")
        print("\n⚠️  Remember to change this password in production!")
    else:
        print("\n✅ Superuser already exists")

if __name__ == '__main__':
    try:
        has_superusers = check_existing_superusers()
        if not has_superusers:
            create_default_superuser()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
