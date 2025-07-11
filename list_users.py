import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

print("=== User Management Script ===")
print(f"Total users: {User.objects.count()}")

for user in User.objects.all():
    print(f"Email: {user.email}")
    print(f"Username: {user.username}")
    print(f"Superuser: {user.is_superuser}")
    print("---")

# Try to find the specific user
try:
    target_user = User.objects.get(email="paulabrahams.dev@gmail.com")
    print(f"Found target user: {target_user.email}")
    print("To reset password, run:")
    print("user.set_password('new_password')")
    print("user.save()")
except User.DoesNotExist:
    print("User paulabrahams.dev@gmail.com not found")
