from django.contrib.auth import get_user_model

User = get_user_model()

# Find the user
try:
    user = User.objects.get(email="paulabrahams.dev@gmail.com")
    print(f"Found user: {user.email}")
    print(f"Username: {user.username}")
    print(f"Is superuser: {user.is_superuser}")
    
    # You can set a new password like this:
    # user.set_password("new_password_here")
    # user.save()
    # print("Password updated!")
    
except User.DoesNotExist:
    print("User not found. Available users:")
    for u in User.objects.all():
        print(f"- {u.email} (username: {u.username})")
