# Daily Beer Scraping Setup

This guide explains how to set up automated daily beer scraping for Great British Beer.

## What Gets Scraped

The daily scraper automatically fetches new beers from:
- Dark Star Brewing Co
- Harveys & Son
- Brighton Bier
- Burning Sky Brewery

## Option 1: Railway Cron Jobs (Recommended)

Railway supports cron jobs as separate services.

### Setup Steps:

1. **Push your code to GitHub** (if not already done):
   ```bash
   git add .
   git commit -m "Add daily beer scraping"
   git push
   ```

2. **Create a new service in Railway**:
   - Go to your Railway project dashboard
   - Click "New" → "Empty Service"
   - Name it "Beer Scraper Cron"

3. **Connect to your repository**:
   - Click on the new service
   - Go to Settings → Source
   - Connect to the same GitHub repository as your main app

4. **Configure the service**:
   - Go to Settings → Deploy
   - Set **Root Directory**: (same as main app, usually empty)
   - Set **Start Command**: `python manage.py daily_beer_scrape`
   - Set **Cron Schedule**: `0 2 * * *` (runs at 2 AM daily)

5. **Add environment variables**:
   - Copy all environment variables from your main service
   - Make sure `DATABASE_URL` is set correctly

6. **Deploy**:
   - The cron job will now run daily at 2 AM UTC

## Option 2: Manual URL Trigger

You can trigger scraping manually or set up an external cron service.

### Manual Trigger:

Visit this URL (replace with your Railway domain):
```
https://your-app.up.railway.app/admin/scrape-beers/?secret=scrape2026
```

### Using External Cron Service:

Use a service like [cron-job.org](https://cron-job.org) or [EasyCron](https://www.easycron.com):

1. Create a free account
2. Add a new cron job
3. Set URL: `https://your-app.up.railway.app/admin/scrape-beers/?secret=scrape2026`
4. Set schedule: Daily at 2:00 AM
5. Save and activate

## Option 3: Local Testing

Test the scraper locally:

```bash
# Dry run (doesn't save to database)
python manage.py daily_beer_scrape --dry-run

# Actual scrape
python manage.py daily_beer_scrape
```

## Logs

Scraping logs are saved to:
- `logs/daily_scrape_YYYYMMDD.log`
- View recent logs: `cat logs/daily_scrape_*.log`

## Monitoring

Check if scraping is working:
1. Visit `/admin/scrape-beers/?secret=scrape2026`
2. Check the beer count on your homepage
3. Review logs in the `logs/` directory

## Customization

Edit `reviews/management/commands/daily_beer_scrape.py` to:
- Add more breweries
- Change the scraping schedule
- Modify what data gets scraped
- Add email notifications

## Troubleshooting

**No new beers added:**
- Check if brewery websites are accessible
- Review logs for errors
- Run with `--dry-run` to see what would be scraped

**Cron job not running:**
- Verify Railway cron schedule syntax
- Check Railway service logs
- Ensure environment variables are set correctly

**Duplicate beers:**
- The scraper automatically skips existing beers
- Check logs to see which beers were skipped
