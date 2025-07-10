def site_context(request):
    """Global context processor for site-wide variables"""
    return {
        'site_name': 'Great British Beer',
        'site_description': 'User-generated beer reviews and ratings for the finest British ales, lagers, and craft beers.',
        'site_keywords': 'beer reviews, British beer, ale, lager, craft beer, brewery, beer ratings',
        'domain': 'greatbritish.beer',
    }
