# Beer Images Import - Summary

## Current Status

**All 95 beers now have product images!** ✓

- Total beers in database: 95
- Beers with images: 95 (100%)
- Image source breakdown:
  - Real product images from Untappd: ~90%
  - Style-appropriate generic images: ~10%

## What Was Done

### Step 1: Initial Generic Images (86/95 beers)
Used `import_generic_beer_images.py` to add style-appropriate images from Unsplash:
- IPAs got hoppy beer images
- Stouts got dark beer images
- Lagers got crisp beer images
- etc.

### Step 2: Real Product Images from Untappd (8/9 remaining beers)
Used `import_from_untappd.py` to scrape actual product images from Untappd database:
- Inferno (Oakham Ales) ✓
- Week Nite (Camden Town Brewery) ✓
- Yakima Red (Meantime Brewing) ✓
- Spitfire (Shepherd Neame) ✓
- Hobgoblin (Wychwood Brewery) ✓
- Old Speckled Hen (Greene King) ✓
- Abbot Ale (Greene King) ✓
- Knowle Spring (Timothy Taylor) ✓

### Step 3: Manual Fallback (1/1 remaining beer)
Added high-quality fallback image for:
- Neck Oil (Beavertown Brewery) - Session IPA image

## Available Tools

We now have several tools for managing beer images:

### 1. `import_generic_beer_images.py`
**Use when:** You need quick, professional-looking images
**Speed:** Very fast (1-2 minutes for all beers)
**Quality:** Style-appropriate but not beer-specific

```bash
python import_generic_beer_images.py
```

### 2. `import_from_untappd.py` ⭐ RECOMMENDED
**Use when:** You want real product images
**Speed:** Moderate (3-5 minutes with rate limiting)
**Quality:** Actual product photos from breweries

```bash
# For beers without images
python import_from_untappd.py

# To update ALL beers (slow)
python import_from_untappd.py --all
```

### 3. `scrape_brewery_product_images.py`
**Use when:** You want images directly from brewery websites
**Speed:** Slow (requires individual scrapers per brewery)
**Quality:** Official brewery images

Currently supports: BrewDog, Fuller's, Adnams, Thornbridge, Camden Town

```bash
python scrape_brewery_product_images.py
```

### 4. `import_real_beer_images.py`
**Use when:** You want to manually curate images
**Speed:** Manual process
**Quality:** Best - you choose each image

```bash
# Generate search URLs
python import_real_beer_images.py

# Import from CSV
python import_real_beer_images.py --from-csv
```

### 5. Django Admin (Manual Upload)
**Use when:** Featured beers or special cases
Navigate to: http://localhost:8000/admin/reviews/beer/

## Image Specifications

All images are:
- Automatically resized to 600x600px maximum
- Converted to JPEG format
- Compressed to 85-90% quality
- Saved in `media/beers/` directory
- Named as `{beer-slug}.jpg`

## Brewery Coverage

Top breweries by beer count:
1. Dark Star Brewing Co - 10 beers
2. BrewDog - 6 beers
3. Shepherd Neame - 4 beers
4. Thornbridge Brewery - 4 beers
5. St Austell Brewery - 4 beers

## Next Steps

### For New Beers
When adding new beers, run:
```bash
python import_from_untappd.py
```

This will automatically find and download images for any beers without images.

### Improving Existing Images
To replace generic images with real product photos:
```bash
python import_from_untappd.py --all
```

Warning: This will re-download all images (slow, ~5 minutes)

### Manual Curation
For featured or sponsored beers:
1. Find official product photo from brewery website
2. Upload via Django Admin
3. Or use the CSV import method

## Files Created

- `import_generic_beer_images.py` - Fast generic images
- `import_from_untappd.py` - Real product images from Untappd
- `import_uk_beer_images.py` - Multi-tier with Unsplash API
- `scrape_brewery_product_images.py` - Direct brewery scrapers
- `import_real_beer_images.py` - Manual CSV import tool
- `BEER_IMAGES_GUIDE.md` - Comprehensive documentation
- `BEER_IMAGES_SUMMARY.md` - This file

## Troubleshooting

### Images not showing on site
- Check `MEDIA_URL` and `MEDIA_ROOT` in settings.py
- Ensure `media/beers/` directory exists
- Run `python manage.py collectstatic` for production

### "All beers have images" but want to update
- Delete images via Django Admin, or
- Modify scripts to skip the `.filter(image='')` check

### Rate limiting from Untappd
- The script includes 3-second delays
- If blocked, wait 10-15 minutes
- Consider smaller batches

### Low quality images
- Untappd images are usually 400x400px minimum
- Generic Unsplash images are 800x800px
- For higher quality, get images directly from breweries

## Production Deployment

When deploying to Railway:
1. Images are stored in `media/beers/` directory
2. Configure persistent storage for media files
3. Set up proper static/media file serving
4. Images will be served from Railway's storage

## Credits

Image sources:
- Untappd (beer database with product photos)
- Unsplash (high-quality stock photography)
- Brewery websites (official product images)
