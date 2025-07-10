# 🍺 Great British Beer

A fully functional Django-powered beer review blog featuring user-generated content, ratings, and comprehensive beer database management.

## ✨ Features

### Core Functionality
- **User Authentication**: Registration, login, profile management with avatar uploads
- **Beer Database**: Comprehensive beer catalog with breweries, categories, and detailed information
- **Review System**: 5-star rating system with detailed reviews and comments
- **Advanced Search**: Filter beers by category, brewery, rating, and more
- **Admin Dashboard**: Complete content moderation and management tools

### User Experience
- **Responsive Design**: Bootstrap 5 with custom beer-themed styling
- **Rich Text Editor**: CKEditor for detailed reviews
- **Image Uploads**: Beer photos and user avatars with automatic resizing
- **Social Features**: Like reviews, comment system, user profiles
- **Interactive Elements**: AJAX-powered likes and dynamic comment forms
- **Newsletter Signup**: Email subscription functionality
- **SEO Optimized**: Meta tags, Open Graph tags, sitemaps, and semantic URLs

### Admin Features
- **Content Moderation**: Approve/reject reviews and comments
- **Bulk Actions**: Manage multiple items efficiently
- **Advanced Filtering**: Find content quickly with comprehensive filters
- **Statistics Dashboard**: Review and user analytics
- **Role-based Permissions**: Secure access control
- **Sample Data Management**: Built-in management commands for sample content

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Git (optional, for version control)

### Installation

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd great-british-beer
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   copy .env.example .env
   # Edit .env with your settings
   ```

5. **Run database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a superuser account**
   ```bash
   python manage.py createsuperuser
   ```
   Use these suggested credentials or create your own:
   - **Username**: admin
   - **Email**: admin@greatbritish.beer
   - **Password**: (choose a secure password)

7. **Load sample data**
   ```bash
   python manage.py loaddata sample_beers.json
   # Or create sample data with reviews:
   python manage.py setup_sample_data --with-reviews
   ```

8. **Start the development server**
   ```bash
   python manage.py runserver
   ```

9. **Access the application**
   - **Main Site**: http://127.0.0.1:8000/
   - **Admin Panel**: http://127.0.0.1:8000/admin/

## 📖 Sample Content

The project includes comprehensive sample data loaded via management commands:

### 🍻 Featured Sample Beers

#### Tribute Pale Ale by St. Austell Brewery
- **Rating**: 4.5/5 stars
- **Style**: Pale Ale
- **ABV**: 4.2%
- **IBU**: 35
- **Review**: "A classic Cornish pale ale with beautiful citrus notes and a crisp finish. Perfect companion to fish and chips by the seaside."

#### London Pride by Fuller's
- **Rating**: 4/5 stars
- **Style**: Bitter
- **ABV**: 4.7%
- **IBU**: 40
- **Review**: "Iconic London bitter with perfectly balanced malt flavors and a rich brewing heritage spanning centuries."

#### Punk IPA by BrewDog
- **Rating**: 4.2/5 stars
- **Style**: IPA
- **ABV**: 5.6%
- **IBU**: 60
- **Review**: "Bold Scottish IPA packed with tropical fruit hops that helped spark the UK's craft beer revolution."

### 🏭 Sample Breweries
- **St. Austell Brewery** (Cornwall, 1851)
- **Fuller's Brewery** (London, 1845)
- **BrewDog** (Scotland, 2007)

### 📊 Sample Categories
- Pale Ale
- Bitter
- IPA
- Stout
- Lager

All sample data includes realistic reviews, ratings, and user-generated content to demonstrate the platform's capabilities.

## 🏗️ Project Structure

```
greatbritishbeer/
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
├── sample_beers.json           # Sample data fixture
├── setup.md                    # Detailed setup instructions
├── DEPLOYMENT.md               # Complete production deployment guide
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
├── greatbritishbeer/          # Main project directory
│   ├── settings.py            # Django settings
│   ├── settings_production.py # Production-specific settings
│   ├── urls.py               # URL configuration
│   ├── wsgi.py               # WSGI configuration
│   └── asgi.py               # ASGI configuration
├── core/                      # Core app (homepage, about)
│   ├── views.py              # Core views
│   ├── urls.py               # Core URL patterns
│   └── context_processors.py # Global template context
├── users/                     # User authentication app
│   ├── models.py             # Extended User model
│   ├── views.py              # Auth views
│   ├── forms.py              # User forms
│   ├── urls.py               # User URL patterns
│   └── admin.py              # User admin configuration
├── reviews/                   # Beer reviews app
│   ├── models.py             # Beer, Review, Category models
│   ├── views.py              # Review views
│   ├── forms.py              # Review forms
│   ├── urls.py               # Review URL patterns
│   ├── admin.py              # Review admin configuration
│   ├── sitemaps.py           # SEO sitemaps
│   └── management/           # Management commands
│       └── commands/
│           └── setup_sample_data.py
├── templates/                 # HTML templates
│   ├── base.html             # Base template with navigation & footer
│   ├── core/                 # Core app templates (home, about, contact)
│   ├── users/                # User app templates (profile, edit)
│   ├── registration/         # Authentication templates
│   └── reviews/              # Review app templates (beer list/detail, review forms)
└── static/                    # Static files
    ├── css/
    │   ├── custom.css        # Custom beer-themed styles
    │   └── style.css         # Additional styling
    ├── js/
    │   ├── script.js         # Interactive features
    │   └── main.js           # Core JavaScript
    └── images/               # Site images and uploads
```

## 🛠️ Technology Stack

### Backend
- **Django 4.2.7**: Web framework
- **Python 3.8+**: Programming language
- **SQLite**: Development database (PostgreSQL for production)
- **Pillow**: Image processing

### Frontend
- **Bootstrap 5**: CSS framework with custom beer-themed styling
- **Font Awesome**: Comprehensive icon library
- **Custom CSS**: Enhanced styling with CSS variables
- **Vanilla JavaScript**: Interactive features and AJAX calls

### Additional Packages
- **django-crispy-forms**: Bootstrap-styled form rendering
- **django-ckeditor**: Rich text editor for reviews
- **django-taggit**: Tagging system for beers
- **python-decouple**: Environment configuration management
- **Pillow**: Image processing and thumbnails

## 🎯 Usage Guide

### For Users
1. **Browse Beers**: Explore the beer catalog with search and filters
2. **Read Reviews**: See what others think about different beers
3. **Create Account**: Register to write your own reviews
4. **Write Reviews**: Share your beer experiences with ratings and photos
5. **Engage**: Like reviews and add comments to join the conversation

### For Administrators
1. **Access Admin Panel**: Use your superuser credentials
2. **Manage Content**: Approve/reject reviews and moderate comments
3. **Add Beers**: Expand the beer database with new entries
4. **User Management**: Handle user accounts and permissions
5. **Site Configuration**: Manage categories, breweries, and featured content

## 🚀 Production Deployment

For complete production deployment instructions, see the dedicated **[DEPLOYMENT.md](DEPLOYMENT.md)** guide which covers:

### Quick Deployment Overview
- **Server Setup**: Ubuntu/Debian with PostgreSQL, Nginx, and SSL
- **Application Deployment**: Gunicorn, systemd services, and static files
- **Security Configuration**: HTTPS, firewall, and security headers
- **Monitoring**: Log management and performance optimization

### Environment Configuration
1. Set `DEBUG=False` in production settings
2. Configure PostgreSQL database with proper credentials
3. Set up secure `SECRET_KEY` and environment variables
4. Configure email backend for user notifications
5. Set up static file serving with nginx
6. Enable SSL certificates with Let's Encrypt

### Security Checklist
- [ ] Update `SECRET_KEY` to a secure random value
- [ ] Set `DEBUG=False` and `ALLOWED_HOSTS` properly
- [ ] Configure HTTPS with SSL certificates
- [ ] Set up secure cookie and session settings
- [ ] Configure proper file permissions and ownership
- [ ] Set up regular automated database backups
- [ ] Monitor application and security logs
- [ ] Enable firewall and security headers

### Recommended Production Stack
- **Web Server**: nginx + gunicorn
- **Database**: PostgreSQL 12+ with connection pooling
- **Cache**: Redis for session storage and caching
- **File Storage**: Local filesystem or AWS S3
- **Monitoring**: System logs and application monitoring
- **Backup**: Automated PostgreSQL backups

## 🤝 Contributing

This is a complete, production-ready beer review blog. You can extend it by:

1. **Customize the design** by modifying CSS variables and templates
2. **Add new features** like brewery maps, beer comparisons, or social login
3. **Extend the admin** with additional analytics, reporting, and bulk operations
4. **Integrate APIs** for external beer data (Untappd, BreweryDB) or social sharing
5. **Add testing** with Django's comprehensive test framework
6. **Implement caching** for better performance with Redis or Memcached
7. **Add email notifications** for new reviews and user interactions
8. **Create mobile app** using Django REST framework API endpoints

### Development Workflow
1. Fork the repository and create feature branches
2. Follow Django best practices and PEP 8 style guidelines
3. Add tests for new functionality
4. Update documentation for any new features
5. Test thoroughly in development environment

## 📧 Support

For questions or issues:
1. Check the detailed **`setup.md`** file for installation help
2. Review the **`DEPLOYMENT.md`** guide for production deployment
3. Examine the code comments and docstrings for implementation details
4. Review Django documentation for framework-specific questions
5. Check the admin interface for content management features

## 📚 Additional Documentation

- **[setup.md](setup.md)**: Detailed development setup instructions
- **[DEPLOYMENT.md](DEPLOYMENT.md)**: Complete production deployment guide
- **[sample_beers.json](sample_beers.json)**: Sample data structure reference

## 📄 License

This project is provided as educational/demonstration code. Feel free to use and modify for your own projects.

---

**Enjoy exploring the world of Great British Beer! 🍺**
