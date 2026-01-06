"""
RateBeer scraper using the unofficial ratebeer Python library.

Fetches beer data including ratings, ABV, IBU, and descriptions.
"""

import logging
from typing import List, Dict, Optional
from decimal import Decimal

try:
    import ratebeer
    RATEBEER_AVAILABLE = True
except ImportError:
    RATEBEER_AVAILABLE = False
    logger = logging.getLogger('beer_scraper.ratebeer')
    logger.warning("ratebeer library not available - RateBeer scraper disabled")

from ..base import BaseScraper


logger = logging.getLogger('beer_scraper.ratebeer')


class RateBeerScraper(BaseScraper):
    """
    Scraper for RateBeer using unofficial Python library.

    Note: This is an unofficial scraper and may break if RateBeer changes their site.
    """

    def __init__(self):
        """Initialize RateBeer scraper."""
        if not RATEBEER_AVAILABLE:
            raise ImportError("ratebeer library not installed")

        super().__init__(
            source_name='ratebeer',
            rate_limit=2.0,  # 2 seconds between requests
            check_robots=True  # Respect robots.txt
        )

        # Initialize RateBeer API
        try:
            self.rb = ratebeer.RateBeer()
            logger.info("Initialized RateBeer API client")
        except Exception as e:
            logger.error(f"Failed to initialize RateBeer client: {e}")
            raise

    def fetch_breweries(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Fetch brewery data from RateBeer.

        Note: RateBeer library doesn't have direct brewery search,
        so this method returns empty list. Use OpenBreweryDB for breweries.

        Args:
            limit: Not used

        Returns:
            Empty list (use OpenBreweryDB for brewery data)
        """
        logger.warning("Use OpenBreweryDB for brewery data - RateBeer focuses on beers")
        return []

    def fetch_beers(self, brewery_name: Optional[str] = None,
                    limit: Optional[int] = None) -> List[Dict]:
        """
        Fetch beer data from RateBeer.

        Args:
            brewery_name: Optional brewery to search for
            limit: Optional limit on number of beers

        Returns:
            List of beer data dictionaries
        """
        beers = []

        if not brewery_name:
            logger.warning("brewery_name required for RateBeer search")
            return []

        try:
            logger.info(f"Searching RateBeer for beers from '{brewery_name}'...")

            # Search for brewery
            search_results = self.rb.search(brewery_name)

            if not search_results or 'breweries' not in search_results:
                logger.warning(f"No breweries found for '{brewery_name}'")
                return []

            breweries = search_results['breweries']

            if not breweries:
                logger.warning(f"No breweries in search results for '{brewery_name}'")
                return []

            # Get first matching brewery
            brewery = breweries[0]
            brewery_id = brewery.get('id')

            if not brewery_id:
                logger.warning(f"No brewery ID found for '{brewery_name}'")
                return []

            logger.info(f"Found brewery: {brewery.get('name')} (ID: {brewery_id})")

            # Get beers for brewery
            brewery_beers = self.rb.get_brewery(brewery_id)

            if not brewery_beers or 'beers' not in brewery_beers:
                logger.warning(f"No beers found for brewery {brewery_id}")
                return []

            # Process each beer
            for beer_data in brewery_beers['beers']:
                processed = self._process_beer(beer_data, brewery_name)

                if processed:
                    beers.append(processed)
                    self.stats['beers_scraped'] += 1

                    # Check limit
                    if limit and len(beers) >= limit:
                        logger.info(f"Reached limit of {limit} beers")
                        break

            logger.info(f"Fetched {len(beers)} beers for '{brewery_name}'")

        except Exception as e:
            logger.error(f"Error fetching beers from RateBeer: {e}")

        return beers

    def _process_beer(self, data: Dict, brewery_name: str) -> Optional[Dict]:
        """
        Process beer data from RateBeer.

        Args:
            data: Raw beer data from RateBeer
            brewery_name: Brewery name

        Returns:
            Normalized beer dictionary or None if invalid

        RateBeer Data Format (approximate):
            {
                'name': 'Punk IPA',
                'id': '12345',
                'style': 'IPA - American',
                'abv': 5.6,
                'ibu': 45,
                'description': 'A hoppy IPA...',
                'overall_rating': 85,
                'style_rating': 90,
            }
        """
        try:
            # Extract fields
            beer_dict = {
                'name': data.get('name', ''),
                'brewery': brewery_name,
                'style': data.get('style', 'Ale'),
                'abv': data.get('abv'),
                'ibu': data.get('ibu'),
                'description': data.get('description', ''),
            }

            # Validate and normalize
            normalized = self.validate_and_normalize_beer(beer_dict)

            if normalized:
                logger.debug(f"Processed beer: {normalized['name']}")
                return normalized
            else:
                logger.warning(f"Validation failed for beer: {data.get('name')}")
                return None

        except Exception as e:
            logger.error(f"Error processing beer {data.get('name')}: {e}")
            return None

    def search_beer(self, beer_name: str) -> Optional[Dict]:
        """
        Search for specific beer by name.

        Args:
            beer_name: Beer name to search

        Returns:
            Beer data dictionary or None if not found
        """
        try:
            logger.info(f"Searching for beer: '{beer_name}'")

            results = self.rb.search(beer_name)

            if not results or 'beers' not in results:
                logger.warning(f"No results for '{beer_name}'")
                return None

            beers = results['beers']

            if not beers:
                logger.warning(f"No beers in results for '{beer_name}'")
                return None

            # Get first match
            beer_data = beers[0]
            beer_id = beer_data.get('id')

            if not beer_id:
                return None

            # Get full beer details
            full_beer = self.rb.get_beer(beer_id)

            if full_beer:
                # Extract brewery name
                brewery_name = full_beer.get('brewery', {}).get('name', 'Unknown Brewery')
                return self._process_beer(full_beer, brewery_name)

            return None

        except Exception as e:
            logger.error(f"Error searching for beer '{beer_name}': {e}")
            return None

    def fetch_beers_by_style(self, style: str, limit: Optional[int] = 50) -> List[Dict]:
        """
        Fetch beers by style (e.g., 'IPA', 'Stout').

        Args:
            style: Beer style to search
            limit: Maximum number of beers to fetch

        Returns:
            List of beer dictionaries
        """
        beers = []

        try:
            logger.info(f"Searching for '{style}' beers...")

            # Search by style
            results = self.rb.search(style)

            if not results or 'beers' not in results:
                logger.warning(f"No results for style '{style}'")
                return []

            # Process results
            for beer_data in results['beers'][:limit]:
                brewery_name = beer_data.get('brewery', 'Unknown Brewery')
                processed = self._process_beer(beer_data, brewery_name)

                if processed:
                    beers.append(processed)
                    self.stats['beers_scraped'] += 1

            logger.info(f"Fetched {len(beers)} '{style}' beers")

        except Exception as e:
            logger.error(f"Error fetching beers by style '{style}': {e}")

        return beers
