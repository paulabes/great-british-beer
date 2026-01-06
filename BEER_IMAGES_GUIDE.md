# Beer Images Import Guide

This guide explains all the available options for importing images for your beers.

## Quick Start (Recommended)

For the fastest results with good quality images:

```bash
python import_generic_beer_images.py
```

This will add style-appropriate images to all beers immediately, no API keys required.

---

## Available Methods

### Method 1: Generic Style-Based Images (FASTEST) ⭐

**File:** `import_generic_beer_images.py`

**Pros:**
- Works immediately, no setup required
- Fast - processes all beers in 1-2 minutes
- High quality curated images from Unsplash
- Style-appropriate (IPAs get hoppy images, Stouts get dark images, etc.)
- Completely free, no API limits

**Cons:**
- Not beer-specific (won't show actual product photos)
- Multiple beers may share similar images

**Usage:**
```bash
python import_generic_beer_images.py
```

**Best for:** Getting your site looking professional quickly

---

### Method 2: Unsplash API Search (BEST QUALITY)

**File:** `import_uk_beer_images.py`

**Pros:**
- Can search for specific beer names
- Falls back to style-based images
- High quality professional photography
- Millions of images to choose from

**Cons:**
- Requires free Unsplash API key
- Rate limited (50 requests/hour on free tier)
- May not find specific UK craft beers

**Setup:**
1. Go to https://unsplash.com/developers
2. Create a free account
3. Create a new application
4. Copy your Access Key
5. Edit `import_uk_beer_images.py` and replace:
   ```python
   UNSPLASH_ACCESS_KEY = 'your_access_key_here'
   ```
   with your actual key

**Usage:**
```bash
python import_uk_beer_images.py
```

**Best for:** Maximum image variety and quality

---

### Method 3: Brewery Website Scraping (MOST AUTHENTIC)

**File:** `reviews/management/commands/scrape_beer_images.py`

**Pros:**
- Gets actual product photos from brewery websites
- Most authentic representation of each beer
- Automatically matches database beers with website beers

**Cons:**
- Only works for breweries with scrapers implemented
- Scrapers break when websites change
- Time-consuming to maintain

**Currently supported breweries:**
- Dark Star Brewing Co ✓
- Harveys & Son (needs URL update)
- Brighton Bier (needs URL update)
- Burning Sky Brewery (needs URL update)

**Usage:**
```bash
# All supported breweries
python manage.py scrape_beer_images

# Specific brewery only
python manage.py scrape_beer_images --brewery "Dark Star Brewing Co"

# Dry run (test without saving)
python manage.py scrape_beer_images --dry-run

# Verbose output
python manage.py scrape_beer_images --verbose
```

**Best for:** Breweries with working scrapers, when you need authentic product photos

---

### Method 4: Manual Upload via Django Admin

**Pros:**
- Complete control over images
- Can upload exact product photos
- No technical setup required

**Cons:**
- Very time-consuming for many beers
- Requires manual download of each image

**Usage:**
1. Go to http://localhost:8000/admin/reviews/beer/
2. Click on a beer
3. Scroll to "Image" field
4. Click "Choose File" and upload
5. Save

**Best for:** Featured beers, special promotions, or small numbers of beers

---

## Recommended Workflow

For your 95 beers, we recommend this approach:

### Step 1: Quick Generic Images
```bash
python import_generic_beer_images.py
```
This gets all beers looking good immediately (1-2 minutes).

### Step 2: Optional - Enhanced Search
If you want better variety:
1. Get free Unsplash API key
2. Run `python import_uk_beer_images.py`
3. This will search for more specific images

### Step 3: Optional - Specific Beers
For featured or sponsored beers:
- Manually upload high-quality product photos via Django admin
- Or contact breweries for official product images

---

## Image Specifications

All images are automatically:
- Resized to 600x600px maximum
- Converted to JPEG format
- Compressed to 85% quality for fast loading
- Saved to `media/beers/` directory

---

## Troubleshooting

### "All beers already have images"
All your beers have images! To replace existing images, you can either:
- Delete images via Django admin
- Modify the scripts to update all beers (remove `.filter(image='')`)

### "Connection timeout" or "Network error"
- Check your internet connection
- Unsplash might be temporarily down
- Try again in a few minutes

### "Unsplash API rate limit exceeded"
- Free tier allows 50 requests/hour
- Wait an hour and try again
- Or use the generic images script instead

### Images not showing on website
- Make sure `MEDIA_URL` and `MEDIA_ROOT` are configured in settings.py
- Check that media files are served correctly in development
- Run `python manage.py collectstatic` for production

---

## Production Deployment

When deploying to Railway or other hosting:

1. Make sure to run the image import before deploying, or
2. Set up Railway persistent storage for media files
3. Configure Railway to serve static/media files
4. Images are stored in the database's connected media storage

---

## Future Enhancements

Potential improvements to consider:

1. **Brewery Logo Integration:** Add brewery logos to beer cards
2. **Multiple Images:** Support image galleries for each beer
3. **User-Uploaded Images:** Let users add their own beer photos
4. **Automatic Updates:** Schedule daily image checks for new beers
5. **Image CDN:** Use Cloudinary or similar for optimized delivery

---

## Questions?

If you need help with beer images:
- Check this guide first
- Look at the comments in each script
- Test with `--dry-run` flags before committing changes
