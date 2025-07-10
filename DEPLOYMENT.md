# Deployment Guide for Great British Beer

This guide covers deploying the Great British Beer Django application to production environments.

## Heroku Deployment (Recommended)

This section covers deploying to Heroku, which is ideal for Django applications and easiest for beginners.

### Prerequisites for Heroku
- Heroku account (free tier available)
- Heroku CLI installed
- Git repository

### 1. Install Heroku CLI
Download from: https://devcenter.heroku.com/articles/heroku-cli

### 2. Login to Heroku
```bash
heroku login
```

### 3. Create Heroku App
```bash
cd /path/to/great-british-beer
heroku create your-app-name
# or let Heroku generate a name:
# heroku create
```

### 4. Add PostgreSQL Database
```bash
heroku addons:create heroku-postgresql:mini
```

### 5. Set Environment Variables
```bash
heroku config:set SECRET_KEY="your-secret-key-here"
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS="your-app-name.herokuapp.com"
heroku config:set EMAIL_HOST="smtp.gmail.com"
heroku config:set EMAIL_PORT=587
heroku config:set EMAIL_USE_TLS=True
heroku config:set EMAIL_HOST_USER="your-email@gmail.com"
heroku config:set EMAIL_HOST_PASSWORD="your-app-password"
heroku config:set DEFAULT_FROM_EMAIL="noreply@your-app-name.herokuapp.com"
```

### 6. Create Required Files

Create a `Procfile` in your project root:
```
web: gunicorn greatbritishbeer.wsgi:application
release: python manage.py migrate
```

Create `runtime.txt` in project root:
```
python-3.11.7
```

### 7. Update requirements.txt
Ensure these packages are in your requirements.txt:
```
gunicorn
psycopg2-binary
whitenoise
dj-database-url
```

### 8. Update Django Settings for Heroku
Add to your `settings.py`:
```python
import dj_database_url
import os

# Database configuration for Heroku
if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
    }

# Static files configuration
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Whitenoise middleware (add to MIDDLEWARE)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this line
    # ... rest of your middleware
]
```

### 9. Deploy to Heroku
```bash
git add .
git commit -m "Prepare for Heroku deployment"
git push heroku main
```

### 10. Run Initial Setup
```bash
heroku run python manage.py createsuperuser
heroku run python manage.py setup_sample_data
```

### 11. Open Your App
```bash
heroku open
```

### Heroku Maintenance Commands
```bash
# View logs
heroku logs --tail

# Run Django commands
heroku run python manage.py migrate
heroku run python manage.py collectstatic --noinput
heroku run python manage.py shell

# Scale dynos
heroku ps:scale web=1

# Restart app
heroku restart

# View config vars
heroku config

# Database backup
heroku pg:backups:capture
heroku pg:backups:download
```

## Alternative Deployment Options

### 1. **DigitalOcean App Platform**
- Managed platform service
- Easy Django deployment
- Database included
- Reasonable pricing

### 2. **PythonAnywhere**
- Django-friendly hosting
- Free tier available
- Good for learning/small projects
- Web-based console

### 3. **VPS Deployment** (Traditional Server Setup)
- Full control over server
- More cost-effective for large applications
- Requires more setup (see VPS section below)
- Platforms: DigitalOcean, Linode, AWS EC2, etc.

---

## VPS Deployment (Traditional Server Setup)

This guide covers deploying the Great British Beer Django application to a production environment.

## Prerequisites

- Ubuntu/Debian server (or similar Linux distribution)
- Python 3.8+
- PostgreSQL 12+
- Nginx
- Domain name pointed to your server

## Server Setup

### 1. Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Required Packages
```bash
sudo apt install python3-pip python3-dev python3-venv
sudo apt install postgresql postgresql-contrib
sudo apt install nginx
sudo apt install git
```

### 3. Create Application User
```bash
sudo adduser gbeer
sudo usermod -aG sudo gbeer
su - gbeer
```

## Database Setup

### 1. Create PostgreSQL Database
```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE greatbritishbeer;
CREATE USER gbeeruser WITH PASSWORD 'your_secure_password';
ALTER ROLE gbeeruser SET client_encoding TO 'utf8';
ALTER ROLE gbeeruser SET default_transaction_isolation TO 'read committed';
ALTER ROLE gbeeruser SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE greatbritishbeer TO gbeeruser;
\q
```

## Application Deployment

### 1. Clone Repository
```bash
cd /home/gbeer
git clone https://github.com/yourusername/great-british-beer.git
cd great-british-beer
```

### 2. Create Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

### 4. Environment Configuration
```bash
cp .env.example .env
nano .env
```

Configure the following variables:
```env
SECRET_KEY=your_very_secret_key_here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_NAME=greatbritishbeer
DB_USER=gbeeruser
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

### 5. Database Migration
```bash
python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py setup_sample_data
```

### 6. Create Static Files Directory
```bash
sudo mkdir -p /var/www/greatbritishbeer/static
sudo mkdir -p /var/www/greatbritishbeer/media
sudo chown -R gbeer:gbeer /var/www/greatbritishbeer
```

### 7. Collect Static Files
```bash
python manage.py collectstatic --settings=greatbritishbeer.settings_production
```

## Gunicorn Setup

### 1. Create Gunicorn Service File
```bash
sudo nano /etc/systemd/system/greatbritishbeer.service
```

```ini
[Unit]
Description=Great British Beer Django Application
After=network.target

[Service]
User=gbeer
Group=gbeer
WorkingDirectory=/home/gbeer/great-british-beer
Environment="PATH=/home/gbeer/great-british-beer/.venv/bin"
ExecStart=/home/gbeer/great-british-beer/.venv/bin/gunicorn --workers 3 --bind unix:/home/gbeer/great-british-beer/greatbritishbeer.sock greatbritishbeer.wsgi:application

[Install]
WantedBy=multi-user.target
```

### 2. Start and Enable Service
```bash
sudo systemctl start greatbritishbeer
sudo systemctl enable greatbritishbeer
sudo systemctl status greatbritishbeer
```

## Nginx Configuration

### 1. Create Nginx Site Configuration
```bash
sudo nano /etc/nginx/sites-available/greatbritishbeer
```

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /var/www/greatbritishbeer;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        root /var/www/greatbritishbeer;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/gbeer/great-british-beer/greatbritishbeer.sock;
    }
}
```

### 2. Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/greatbritishbeer /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

## SSL Configuration (Let's Encrypt)

### 1. Install Certbot
```bash
sudo apt install certbot python3-certbot-nginx
```

### 2. Obtain SSL Certificate
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### 3. Auto-renewal
```bash
sudo crontab -e
```
Add: `0 12 * * * /usr/bin/certbot renew --quiet`

## Monitoring and Maintenance

### 1. Log Files
- Application logs: `/home/gbeer/great-british-beer/logs/django.log`
- Nginx logs: `/var/log/nginx/access.log` and `/var/log/nginx/error.log`
- Systemd logs: `sudo journalctl -u greatbritishbeer`

### 2. Restart Services
```bash
# Restart application
sudo systemctl restart greatbritishbeer

# Restart nginx
sudo systemctl restart nginx

# Check status
sudo systemctl status greatbritishbeer
sudo systemctl status nginx
```

### 3. Database Backup
Create a backup script:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h localhost -U gbeeruser greatbritishbeer > /home/gbeer/backups/greatbritishbeer_$DATE.sql
```

## Security Considerations

1. Use strong passwords for database and admin accounts
2. Keep system packages updated
3. Configure firewall (ufw)
4. Regular security updates
5. Monitor log files for suspicious activity
6. Use environment variables for sensitive data
7. Enable HTTPS only
8. Regular database backups

## Performance Optimization

1. Use Redis for caching
2. Configure database connection pooling
3. Optimize static file serving
4. Enable gzip compression in Nginx
5. Monitor server resources
6. Use CDN for static assets

## Troubleshooting

### Common Issues

1. **Permission denied errors**: Check file permissions and ownership
2. **Database connection errors**: Verify PostgreSQL is running and credentials are correct
3. **Static files not loading**: Check STATIC_ROOT and run collectstatic
4. **502 Bad Gateway**: Check Gunicorn service status and socket file permissions

### Log Locations
```bash
# Application logs
tail -f /home/gbeer/great-british-beer/logs/django.log

# Gunicorn logs
sudo journalctl -u greatbritishbeer -f

# Nginx logs
sudo tail -f /var/log/nginx/error.log
```

## Updates and Maintenance

To update the application:
```bash
cd /home/gbeer/great-british-beer
source .venv/bin/activate
git pull origin main
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart greatbritishbeer
```

# GitHub Deployment Guide

This section covers creating a GitHub repository and deploying your Django application to various platforms from GitHub.

## Step 1: Create GitHub Repository

### 1. Create Repository on GitHub
1. Go to [github.com](https://github.com) and sign in
2. Click the **"+"** button in the top right corner
3. Select **"New repository"**
4. Fill in the repository details:
   - **Repository name**: `great-british-beer`
   - **Description**: `A Django beer review blog with user-generated content, ratings, and advanced features`
   - **Visibility**: Choose Public or Private
   - **Do NOT initialize** with README, .gitignore, or license (we already have these)
5. Click **"Create repository"**

### 2. Push Your Code to GitHub
Open PowerShell in your project directory and run:

```powershell
# Navigate to your project directory
cd "d:\Dropbox\code\live\great-british-beer"

# Check git status (should already be initialized)
git status

# Add GitHub remote (replace 'yourusername' with your actual GitHub username)
git remote add origin https://github.com/yourusername/great-british-beer.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 2: Platform-Specific Deployment

### Option A: Deploy to Railway (Recommended for beginners)

Railway is a modern platform that makes Django deployment simple.

#### 1. Prepare for Railway
Create a `railway.json` file in your project root:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "nixpacks"
  },
  "deploy": {
    "startCommand": "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn greatbritishbeer.wsgi:application",
    "restartPolicyType": "on-failure",
    "restartPolicyMaxRetries": 10
  }
}
```

#### 2. Deploy to Railway
1. Go to [railway.app](https://railway.app)
2. Sign up/in with your GitHub account
3. Click **"New Project"**
4. Select **"Deploy from GitHub repo"**
5. Choose your `great-british-beer` repository
6. Railway will automatically detect it's a Django app
7. Add environment variables in Railway dashboard:
   - `SECRET_KEY`: Generate a new secret key
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: `*.railway.app`
   - `DATABASE_URL`: (Railway will provide this automatically)
8. Deploy and get your live URL

### Option B: Deploy to Heroku

#### 1. Prepare for Heroku
Create a `Procfile` in your project root:

```
web: gunicorn greatbritishbeer.wsgi:application
release: python manage.py migrate && python manage.py collectstatic --noinput
```

Create a `runtime.txt` file:
```
python-3.11.0
```

#### 2. Deploy to Heroku
1. Install Heroku CLI from [heroku.com](https://heroku.com)
2. Login: `heroku login`
3. Create app: `heroku create your-app-name`
4. Add PostgreSQL: `heroku addons:create heroku-postgresql:hobby-dev`
5. Set environment variables:
   ```bash
   heroku config:set SECRET_KEY=your_secret_key
   heroku config:set DEBUG=False
   heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com
   ```
6. Deploy: `git push heroku main`

### Option C: Deploy to DigitalOcean App Platform

#### 1. Prepare App Spec
Create a `.do/app.yaml` file:

```yaml
name: great-british-beer
services:
- name: web
  source_dir: /
  github:
    repo: yourusername/great-british-beer
    branch: main
  run_command: gunicorn --worker-tmp-dir /dev/shm greatbritishbeer.wsgi:application
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: DEBUG
    value: "False"
  - key: SECRET_KEY
    value: "your_secret_key_here"
databases:
- name: db
  engine: PG
  num_nodes: 1
  size: basic-xs
```

#### 2. Deploy to DigitalOcean
1. Go to [cloud.digitalocean.com](https://cloud.digitalocean.com)
2. Create account and navigate to Apps
3. Click **"Create App"**
4. Connect your GitHub repository
5. Configure using the app.yaml spec
6. Deploy

## Step 3: Post-Deployment Setup

### 1. Create Superuser
For most platforms, you'll need to create a superuser after deployment:

```bash
# Railway
railway run python manage.py createsuperuser

# Heroku
heroku run python manage.py createsuperuser

# DigitalOcean (via console)
python manage.py createsuperuser
```

### 2. Load Sample Data
```bash
# Railway
railway run python manage.py setup_sample_data

# Heroku
heroku run python manage.py setup_sample_data
```

### 3. Configure Domain (Optional)
- Set up custom domain in your platform's dashboard
- Update `ALLOWED_HOSTS` in environment variables
- Configure SSL (usually automatic on these platforms)

## Step 4: Ongoing Updates

### Update Process
1. Make changes to your code locally
2. Test thoroughly
3. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Your update message"
   git push origin main
   ```
4. Most platforms auto-deploy from GitHub pushes

### Environment Variables Management
Keep sensitive data in environment variables:
- `SECRET_KEY`
- `DATABASE_URL`
- `EMAIL_HOST_PASSWORD`
- `DEBUG=False`

## Troubleshooting GitHub Deployment

### Common Issues

1. **Build Fails**: Check requirements.txt and ensure all dependencies are listed
2. **Static Files Not Loading**: Ensure `STATIC_ROOT` is set and `collectstatic` runs
3. **Database Errors**: Verify `DATABASE_URL` is set correctly
4. **Permission Errors**: Check file permissions and ensure `DEBUG=False`

### Useful Commands

```bash
# Check deployment logs
railway logs  # Railway
heroku logs --tail  # Heroku

# Run migrations remotely
railway run python manage.py migrate
heroku run python manage.py migrate

# Access database console
railway run python manage.py dbshell
heroku run python manage.py dbshell
```

## Security for Production

1. **Environment Variables**: Never commit sensitive data to GitHub
2. **Secret Key**: Generate a new secret key for production
3. **Debug Mode**: Always set `DEBUG=False` in production
4. **Allowed Hosts**: Restrict to your domain only
5. **HTTPS**: Enable SSL/TLS (usually automatic on hosting platforms)

## Cost Considerations

- **Railway**: Free tier available, pay-as-you-go
- **Heroku**: Free tier discontinued, starts at $5/month
- **DigitalOcean**: Starts at $5/month
- **PythonAnywhere**: Free tier available, paid plans from $5/month

## Next Steps

1. Choose your preferred deployment platform
2. Follow the specific deployment steps above
3. Configure your domain and SSL
4. Set up monitoring and backups
5. Consider implementing CI/CD for automated deployments

---
