# Railway Deployment Guide - Great British Beer

This guide will help you deploy the Great British Beer Django app to Railway for free.

## Why Railway?

- **Free Tier**: $5 credit per month (enough for small apps)
- **PostgreSQL included**: Free PostgreSQL database
- **Easy deployment**: Direct GitHub integration
- **No credit card required**: Start immediately
- **Automatic HTTPS**: SSL certificates included

## Prerequisites

- A GitHub account
- Your Great British Beer repository pushed to GitHub
- A Railway account (free signup at https://railway.app)

## Step-by-Step Deployment

### 1. Sign Up for Railway

1. Go to https://railway.app
2. Click "Login" and sign in with your GitHub account
3. Authorize Railway to access your GitHub repositories

### 2. Create a New Project

1. Click "New Project" on your Railway dashboard
2. Select "Deploy from GitHub repo"
3. Choose the `great-british-beer` repository
4. Railway will automatically detect it's a Python/Django project

### 3. Add PostgreSQL Database

1. In your Railway project, click "New Service"
2. Select "Database"
3. Choose "PostgreSQL"
4. Railway will automatically provision a PostgreSQL database
5. The `DATABASE_URL` environment variable will be automatically set

### 4. Configure Environment Variables

Click on your Django service, then go to the "Variables" tab and add:

```
SECRET_KEY=<generate-a-secure-random-key-here>
DEBUG=False
ALLOWED_HOSTS=.railway.app
DISABLE_COLLECTSTATIC=1
```

**To generate a secure SECRET_KEY:**
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. Deploy

1. Railway will automatically deploy your app
2. Watch the build logs in the "Deployments" tab
3. The first deployment may take 3-5 minutes

### 6. Run Migrations

After the initial deployment:

1. Click on your service
2. Go to "Settings" tab
3. Scroll to "Deploy Triggers"
4. Railway will run migrations automatically via the Procfile `release` command

OR manually run migrations:
1. Click on your service
2. Go to "Settings" > "Terminal"
3. Run: `python manage.py migrate`

### 7. Create Superuser

To access the Django admin:

1. Open the Railway terminal for your service
2. Run: `python manage.py createsuperuser`
3. Follow the prompts to create an admin user

### 8. Load Sample Data (Optional)

To populate your site with sample beers:

1. In the Railway terminal, run:
```bash
python manage.py setup_sample_data
```

### 9. Get Your Live URL

1. In your service settings, go to "Networking"
2. Click "Generate Domain"
3. Railway will give you a URL like: `https://your-app.up.railway.app`
4. Visit your live site!

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | Yes | - | Django secret key (generate a random one) |
| `DEBUG` | No | True | Set to `False` in production |
| `DATABASE_URL` | Auto | - | Automatically set by Railway PostgreSQL |
| `ALLOWED_HOSTS` | No | - | Already configured for `.railway.app` |
| `DISABLE_COLLECTSTATIC` | No | - | Set to `1` if using Nixpacks |

## Custom Domain (Optional)

To use your own domain (e.g., greatbritish.beer):

1. In Railway, go to service "Settings" > "Networking"
2. Click "Custom Domain"
3. Enter your domain
4. Add the provided DNS records to your domain registrar
5. Update `ALLOWED_HOSTS` in environment variables to include your domain

## File Uploads & Media

Railway provides ephemeral storage. For persistent media files (user uploads, beer images), you'll need to:

1. Use an S3-compatible storage service (AWS S3, Cloudflare R2, Backblaze B2)
2. Install `django-storages` and configure it
3. Or use Railway's Volume feature (Settings > Volumes)

## Monitoring & Logs

- View real-time logs in the "Deployments" tab
- Check resource usage in the "Metrics" tab
- Set up alerts in "Settings" > "Alerts"

## Troubleshooting

### Build Fails

**Error:** `psycopg2-binary` fails to install
- **Solution:** Railway provides PostgreSQL libraries, but if it fails, the nixpacks.toml file should handle it

### Static Files Not Loading

**Error:** CSS/JS files return 404
- **Solution:** Ensure `STATICFILES_STORAGE` is set correctly in settings.py (already configured with WhiteNoise)
- Check that collectstatic runs in the build phase (configured in nixpacks.toml)

### Database Connection Issues

**Error:** Can't connect to PostgreSQL
- **Solution:** Ensure the PostgreSQL service is running
- Verify `DATABASE_URL` is set in environment variables
- Check that `dj-database-url` is in requirements.txt

### 500 Server Error

- Set `DEBUG=True` temporarily to see detailed errors
- Check logs in Railway dashboard
- Verify all environment variables are set correctly

## Cost & Free Tier Limits

Railway's free tier includes:
- **$5 credit per month**
- **500 hours of usage** (enough for always-on small apps)
- **100 GB bandwidth**
- **PostgreSQL database included**

For a small Django app like Great British Beer, the free tier should be sufficient for development and low-traffic production use.

## Backing Up Your Database

### Automated Backups (Recommended)

Railway doesn't provide automatic backups on the free tier. Use Railway's CLI or manual exports:

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Export database
railway run pg_dump $DATABASE_URL > backup.sql
```

### Manual Backup via Admin

1. Use Django's `dumpdata` command:
```bash
railway run python manage.py dumpdata > backup.json
```

## Next Steps

1. Set up email for password resets (configure EMAIL settings)
2. Add custom domain
3. Configure media storage (S3/Cloudflare R2)
4. Set up monitoring and alerts
5. Create a backup strategy

## Support & Resources

- Railway Documentation: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Django on Railway Guide: https://docs.railway.app/guides/django

## Quick Deploy Checklist

- [ ] Sign up for Railway
- [ ] Connect GitHub repository
- [ ] Add PostgreSQL service
- [ ] Set environment variables (SECRET_KEY, DEBUG=False)
- [ ] Deploy and watch build logs
- [ ] Run migrations
- [ ] Create superuser
- [ ] Generate domain and test site
- [ ] (Optional) Load sample data
- [ ] (Optional) Configure custom domain

---

**Your Great British Beer app is now live on Railway!** 🍺🇬🇧
