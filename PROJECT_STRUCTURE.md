# Project Structure Documentation

## 📁 Great British Beer - Django Project Structure

```
great-british-beer/
├── 📁 .github/                    # GitHub workflows and templates
│   └── workflows/                 # CI/CD automation
├── 📁 .venv/                      # Python virtual environment
├── 📁 .vscode/                    # VS Code configuration
├── 📁 core/                       # Core app - site-wide functionality
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py                  # Core models (if any)
│   ├── views.py                   # Home, about, contact views
│   ├── urls.py                    # Core URL patterns
│   └── migrations/
├── 📁 greatbritishbeer/           # Django project settings
│   ├── __init__.py
│   ├── settings.py                # Main settings file
│   ├── urls.py                    # Root URL configuration
│   ├── wsgi.py                    # WSGI application
│   └── asgi.py                    # ASGI application
├── 📁 reviews/                    # Reviews app - beer reviews functionality
│   ├── __init__.py
│   ├── admin.py                   # Admin interface configuration
│   ├── apps.py
│   ├── models.py                  # Beer, Review, Rating models
│   ├── views.py                   # Review CRUD operations
│   ├── forms.py                   # Review and beer forms
│   ├── urls.py                    # Reviews URL patterns
│   └── migrations/                # Database migrations
├── 📁 users/                      # Users app - authentication & profiles
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py                  # Custom User model
│   ├── views.py                   # Auth views (login, register, profile)
│   ├── forms.py                   # User forms
│   ├── urls.py                    # User URL patterns
│   └── migrations/
├── 📁 static/                     # Static files (development)
│   ├── css/
│   │   └── style.css              # Custom CSS
│   ├── js/
│   │   └── script.js              # Custom JavaScript
│   └── images/
├── 📁 staticfiles/                # Collected static files (production)
├── 📁 templates/                  # HTML templates
│   ├── base.html                  # Base template
│   ├── core/                      # Core app templates
│   │   ├── home.html
│   │   ├── about.html
│   │   └── contact.html
│   ├── reviews/                   # Reviews app templates
│   │   ├── beer_list.html
│   │   ├── beer_detail.html
│   │   ├── review_list.html
│   │   └── review_form.html
│   └── users/                     # Users app templates
│       ├── login.html
│       ├── register.html
│       └── profile.html
├── 📄 manage.py                   # Django management script
├── 📄 requirements.txt            # Python dependencies
├── 📄 runtime.txt                 # Python version for deployment
├── 📄 Procfile                    # Process file for deployment
├── 📄 railway.json                # Railway deployment config
├── 📄 .env.example                # Environment variables template
├── 📄 .gitignore                  # Git ignore rules
├── 📄 README.md                   # Project documentation
├── 📄 DEPLOYMENT.md              # Deployment instructions
├── 📄 FRONTEND_VALIDATION.md     # Frontend validation checklist
├── 📄 CODE_QUALITY_CHECKLIST.md # Code quality guidelines
├── 📄 setup.md                   # Development setup guide
├── 📄 sample_beers.json          # Sample data for testing
└── 📄 db.sqlite3                 # Development database
```

## 🏗️ Architecture Overview

### **Django Apps Structure**
- **core/**: Site-wide functionality (home, about, contact)
- **users/**: User authentication and profile management
- **reviews/**: Beer reviews and ratings system

### **Key Design Patterns**
- **MVT Pattern**: Model-View-Template Django architecture
- **App-based organization**: Modular, reusable components
- **Template inheritance**: DRY principle with base.html
- **Static file organization**: Separate CSS, JS, and images

### **Database Design**
- **Custom User Model**: Extended Django user with email auth
- **Normalized Relations**: Proper foreign keys and constraints
- **Migration System**: Version-controlled schema changes

### **Frontend Architecture**
- **Bootstrap 5.3.2**: Responsive CSS framework
- **Progressive Enhancement**: Works without JavaScript
- **Component-based CSS**: Reusable UI components
- **AJAX Integration**: Enhanced user interactions

### **Security Implementation**
- **CSRF Protection**: All forms protected
- **User Authentication**: Django's built-in auth system
- **Input Validation**: Both client and server-side
- **Static File Security**: Proper headers and policies

## 📋 Development Standards

### **File Naming Conventions**
- Snake_case for Python files
- kebab-case for templates and static files
- PascalCase for Django models and classes
- UPPERCASE for constants and environment variables

### **Code Organization**
- Views organized by functionality
- Models with proper relationships
- Forms with validation logic
- Templates with inheritance hierarchy

### **Documentation Standards**
- Docstrings for all functions and classes
- Type hints for function parameters
- README files for setup instructions
- Inline comments for complex logic

## 🚀 Deployment Structure

### **Production Files**
- `Procfile`: Gunicorn server configuration
- `requirements.txt`: Production dependencies
- `runtime.txt`: Python version specification
- `railway.json`: Platform-specific deployment

### **Environment Configuration**
- `.env.example`: Template for environment variables
- `settings.py`: Environment-aware configuration
- `staticfiles/`: Production static file collection

## 🔄 Development Workflow

1. **Local Development**: SQLite database, debug mode
2. **Static Files**: Development server with static files
3. **Testing**: Unit tests and integration tests
4. **Deployment**: Production with PostgreSQL and static CDN

This structure follows Django best practices and ensures maintainable, scalable code organization.
