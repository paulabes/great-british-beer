# Great British Beer - Django Setup Instructions

Welcome to the Great British Beer review blog! Follow these steps to get your project up and running.

## Prerequisites
- Python 3.8 or higher
- PostgreSQL (optional - will use SQLite for development)
- Git

## Installation Steps

### 1. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
source venv/bin/activate  # On Mac/Linux
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Setup
Create a `.env` file in the root directory with:
```
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
```

### 4. Database Setup
```bash
# Create and apply migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (IMPORTANT - you must do this manually for security)
python manage.py createsuperuser
```

**SECURITY NOTE**: Django requires you to manually create admin credentials using `python manage.py createsuperuser` for security reasons. Use these suggested details or create your own:
- Username: admin
- Email: admin@greatbritish.beer
- Password: (choose a secure password)

### 5. Load Sample Data
```bash
python manage.py loaddata sample_beers.json
```

### 6. Run Development Server
```bash
python manage.py runserver
```

## Access Points

- **Main Site**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **User Registration**: http://127.0.0.1:8000/accounts/register/
- **Login**: http://127.0.0.1:8000/accounts/login/

## Admin Features

The admin panel includes:
- Beer database management
- Review moderation
- User management
- Category and tag management
- Bulk actions for review approval
- Advanced filtering

## Sample Content

The project includes three pre-configured beer reviews:
1. Tribute Pale Ale by St. Austell Brewery (4.5/5)
2. London Pride by Fuller's (4/5)
3. Punk IPA by BrewDog (4.2/5)

## Production Deployment

For production deployment:
1. Set `DEBUG=False` in settings
2. Configure PostgreSQL database
3. Set up static files serving
4. Configure email backend for password reset
5. Set proper domain in `ALLOWED_HOSTS`

## Support

For issues or questions, check the Django documentation or review the code comments in the project files.

Happy beer reviewing! 🍺
