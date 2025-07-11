from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'List all superuser accounts'

    def handle(self, *args, **options):
        User = get_user_model()
        superusers = User.objects.filter(is_superuser=True)
        
        self.stdout.write(
            self.style.SUCCESS('=== SUPERUSER ACCOUNTS ===')
        )
        
        if superusers.exists():
            for user in superusers:
                self.stdout.write(f"🔑 Username: {user.username}")
                self.stdout.write(f"   Email: {user.email}")
                self.stdout.write(f"   Active: {'✅' if user.is_active else '❌'}")
                self.stdout.write(f"   Staff: {'✅' if user.is_staff else '❌'}")
                self.stdout.write(f"   Created: {user.date_joined}")
                self.stdout.write("-" * 40)
        else:
            self.stdout.write(
                self.style.WARNING('❌ No superuser accounts found!')
            )
            self.stdout.write(
                'To create a superuser, run: python manage.py createsuperuser'
            )
