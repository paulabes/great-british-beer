import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

def reset_password():
    User = get_user_model()
    email = "paulabrahams.dev@gmail.com"
    new_password = "admin123"  # You can change this
    
    try:
        user = User.objects.get(email=email)
        user.set_password(new_password)
        user.save()
        print(f"SUCCESS: Password reset for {email}")
        print(f"New password: {new_password}")
        return True
    except User.DoesNotExist:
        print(f"ERROR: User {email} not found")
        print("Available users:")
        for u in User.objects.all():
            print(f"  - {u.email}")
        return False

if __name__ == "__main__":
    reset_password()
