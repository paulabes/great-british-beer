"""
Base class for brewery-specific scrapers.
Each brewery has different website structure, so we need custom scrapers.
"""

import logging
from typing import List, Dict, Optional
from bs4 import BeautifulSoup

from ..base import BaseScraper


logger = logging.getLogger('beer_scraper.brewery')


class BreweryWebsiteScraper(BaseScraper):
    """
    Base class for scraping individual brewery websites.

    Each brewery has different HTML structure, so subclasses
    must implement their own parsing logic.
    """

    def __init__(self, brewery_name: str, base_url: str):
        """
        Initialize brewery scraper.

        Args:
            brewery_name: Name of the brewery
            base_url: Base URL of brewery website
        """
        super().__init__(
            source_name=f'brewery_{brewery_name.lower().replace(" ", "_")}',
            rate_limit=3.0,  # 3 seconds between requests
            check_robots=True
        )
        self.brewery_name = brewery_name
        self.base_url = base_url

    def fetch_breweries(self, limit: Optional[int] = None) -> List[Dict]:
        """Not used for brewery-specific scrapers."""
        return []

    def fetch_beers(self, brewery_name: Optional[str] = None,
                    limit: Optional[int] = None) -> List[Dict]:
        """
        Fetch beers from brewery website.
        Must be implemented by subclass.
        """
        raise NotImplementedError("Subclass must implement fetch_beers()")

    def _get_soup(self, url: str) -> Optional[BeautifulSoup]:
        """
        Get BeautifulSoup object for URL.

        Args:
            url: URL to fetch

        Returns:
            BeautifulSoup object or None if failed
        """
        try:
            response = self.make_request(url, timeout=30)
            if response:
                return BeautifulSoup(response.content, 'lxml')
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
        return None

    def _extract_image_url(self, img_element) -> Optional[str]:
        """
        Extract image URL from img element.

        Args:
            img_element: BeautifulSoup img element

        Returns:
            Full image URL or None
        """
        if not img_element:
            return None

        # Try different attributes
        img_url = img_element.get('src') or img_element.get('data-src')

        if not img_url:
            return None

        # Make absolute URL if relative
        if img_url.startswith('//'):
            img_url = 'https:' + img_url
        elif img_url.startswith('/'):
            img_url = self.base_url.rstrip('/') + img_url
        elif not img_url.startswith('http'):
            img_url = self.base_url.rstrip('/') + '/' + img_url

        return img_url
