from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
import sys

User = get_user_model()

class Command(BaseCommand):
    help = 'Setup Heroku database with migrations and sample data'

    def handle(self, *args, **options):
        self.stdout.write('Starting Heroku setup...')
        
        try:
            # Run migrations
            self.stdout.write('Running migrations...')
            call_command('migrate', verbosity=0)
            self.stdout.write(self.style.SUCCESS('✓ Migrations completed'))
            
            # Check if admin user exists
            if not User.objects.filter(username='admin').exists():
                # Create superuser
                self.stdout.write('Creating admin user...')
                User.objects.create_superuser(
                    username='admin',
                    email='admin@greatbritish.beer',
                    password='admin123'
                )
                self.stdout.write(self.style.SUCCESS('✓ Admin user created'))
            else:
                self.stdout.write('✓ Admin user already exists')
            
            # Load sample data
            self.stdout.write('Loading sample data...')
            call_command('setup_sample_data', verbosity=0)
            self.stdout.write(self.style.SUCCESS('✓ Sample data loaded'))
            
            self.stdout.write(self.style.SUCCESS('🍺 Heroku setup completed successfully!'))
            self.stdout.write('You can now visit your app.')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error during setup: {str(e)}'))
            sys.exit(1)
