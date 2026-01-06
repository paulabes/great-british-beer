"""
Dark Star Brewing Co website scraper.
"""

import logging
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import re

from .base_brewery import BreweryWebsiteScraper


logger = logging.getLogger('beer_scraper.brewery.darkstar')


class DarkStarScraper(BreweryWebsiteScraper):
    """Scraper for Dark Star Brewing Co website."""

    def __init__(self):
        super().__init__(
            brewery_name='Dark Star Brewing Co',
            base_url='https://www.darkstarbrewing.co.uk'
        )

    def fetch_beers(self, brewery_name: Optional[str] = None,
                    limit: Optional[int] = None) -> List[Dict]:
        """
        Fetch beers from Dark Star website.

        Returns:
            List of beer dictionaries with name, image_url, etc.
        """
        beers = []

        # Dark Star beers page
        beers_url = f"{self.base_url}/beers"

        logger.info(f"Fetching beers from {beers_url}")

        soup = self._get_soup(beers_url)
        if not soup:
            logger.error("Could not fetch Dark Star beers page")
            return beers

        # Find beer listings - this will vary by site structure
        # Common patterns: divs with class 'product', 'beer-card', etc.
        beer_elements = soup.find_all(['div', 'article'], class_=re.compile(r'product|beer|brew', re.I))

        if not beer_elements:
            # Try alternative selectors
            beer_elements = soup.find_all('a', href=re.compile(r'/beer/|/product/'))

        logger.info(f"Found {len(beer_elements)} potential beer elements")

        for element in beer_elements:
            try:
                beer_data = self._parse_beer_element(element)
                if beer_data:
                    beers.append(beer_data)
                    self.stats['beers_scraped'] += 1

                    if limit and len(beers) >= limit:
                        break
            except Exception as e:
                logger.error(f"Error parsing beer element: {e}")

        logger.info(f"Scraped {len(beers)} beers from Dark Star")
        return beers

    def _parse_beer_element(self, element) -> Optional[Dict]:
        """
        Parse beer information from HTML element.

        Args:
            element: BeautifulSoup element

        Returns:
            Beer dictionary or None
        """
        # Extract beer name
        name_elem = element.find(['h2', 'h3', 'h4', 'a'], class_=re.compile(r'title|name|product', re.I))
        if not name_elem:
            name_elem = element.find('a')

        if not name_elem:
            return None

        beer_name = name_elem.get_text(strip=True)

        # Extract image
        img_elem = element.find('img')
        image_url = self._extract_image_url(img_elem) if img_elem else None

        # Extract description if available
        desc_elem = element.find(['p', 'div'], class_=re.compile(r'description|excerpt', re.I))
        description = desc_elem.get_text(strip=True) if desc_elem else ''

        beer_data = {
            'name': beer_name,
            'brewery': self.brewery_name,
            'image_url': image_url,
            'description': description,
        }

        logger.debug(f"Parsed beer: {beer_name}")
        return beer_data
