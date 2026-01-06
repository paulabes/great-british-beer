"""
Open Brewery DB API scraper.

Fetches UK brewery data from Open Brewery DB (https://www.openbrewerydb.org/)
Free, no API key required.
"""

import logging
from typing import List, Dict, Optional
import requests

from ..base import BaseScraper


logger = logging.getLogger('beer_scraper.openbrewerydb')


class OpenBreweryDBScraper(BaseScraper):
    """
    Scraper for Open Brewery DB API.

    Fetches brewery data for United Kingdom from the free Open Brewery DB API.
    """

    BASE_URL = 'https://api.openbrewerydb.org/v1/breweries'

    def __init__(self):
        """Initialize OpenBreweryDB scraper."""
        super().__init__(
            source_name='openbrewerydb',
            rate_limit=1.0,  # 1 second between requests
            check_robots=False  # API, no robots.txt needed
        )

    def fetch_breweries(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Fetch UK brewery data from Open Brewery DB.

        Args:
            limit: Optional limit on number of breweries

        Returns:
            List of brewery data dictionaries

        API Documentation:
            https://www.openbrewerydb.org/documentation
        """
        breweries = []
        page = 1
        per_page = 50  # API max

        logger.info("Fetching breweries from Open Brewery DB...")

        while True:
            try:
                # Fetch page of breweries
                # Note: Open Brewery DB uses 'United Kingdom' or country code 'gb'
                params = {
                    'by_country': 'England',  # Try England specifically
                    'per_page': per_page,
                    'page': page
                }

                logger.debug(f"Fetching page {page} (per_page={per_page})")

                response = self.make_request(
                    self.BASE_URL,
                    params=params,
                    timeout=30
                )

                if not response:
                    logger.warning(f"No response for page {page}")
                    break

                data = response.json()

                if not data:
                    logger.info(f"No more breweries after page {page-1}")
                    break

                # Process each brewery
                for brewery_data in data:
                    processed = self._process_brewery(brewery_data)
                    if processed:
                        breweries.append(processed)
                        self.stats['breweries_scraped'] += 1

                        # Check limit
                        if limit and len(breweries) >= limit:
                            logger.info(f"Reached limit of {limit} breweries")
                            return breweries

                logger.info(f"Fetched {len(data)} breweries from page {page} (total: {len(breweries)})")

                # Check if we got a full page (if not, we're done)
                if len(data) < per_page:
                    logger.info("Reached last page")
                    break

                page += 1

            except requests.RequestException as e:
                logger.error(f"Error fetching page {page}: {e}")
                break
            except Exception as e:
                logger.error(f"Unexpected error on page {page}: {e}")
                break

        logger.info(f"Fetched total of {len(breweries)} breweries from Open Brewery DB")
        return breweries

    def _process_brewery(self, data: Dict) -> Optional[Dict]:
        """
        Process brewery data from API response.

        Args:
            data: Raw brewery data from API

        Returns:
            Normalized brewery dictionary or None if invalid

        API Response Format:
            {
                "id": "b54b16e1-ac3b-4bff-a11f-f7ae9ddc27e0",
                "name": "BrewDog Brewery",
                "brewery_type": "large",
                "address_1": "123 Main St",
                "city": "Aberdeen",
                "state_province": "Scotland",
                "postal_code": "AB12 3CD",
                "country": "United Kingdom",
                "longitude": "-2.0",
                "latitude": "57.1",
                "phone": "1234567890",
                "website_url": "https://www.brewdog.com",
                "state": "Scotland",
                "street": "123 Main St"
            }
        """
        try:
            # Extract relevant fields
            brewery_dict = {
                'name': data.get('name', ''),
                'location': self._build_location(data),
                'website': data.get('website_url') or None,
                'description': f"{data.get('brewery_type', 'brewery').title()} brewery",
            }

            # Add founded year if available (not in API, but field exists)
            # API doesn't provide this, so we'll leave it empty

            # Validate and normalize
            normalized = self.validate_and_normalize_brewery(brewery_dict)

            if normalized:
                logger.debug(f"Processed brewery: {normalized['name']}")
                return normalized
            else:
                logger.warning(f"Validation failed for brewery: {data.get('name')}")
                return None

        except Exception as e:
            logger.error(f"Error processing brewery {data.get('name')}: {e}")
            return None

    def _build_location(self, data: Dict) -> str:
        """
        Build location string from API data.

        Args:
            data: Brewery data from API

        Returns:
            Location string (e.g., "Aberdeen, Scotland")
        """
        parts = []

        # Add city
        city = data.get('city')
        if city:
            parts.append(city)

        # Add state/province (Scotland, England, Wales, etc.)
        state = data.get('state_province') or data.get('state')
        if state:
            parts.append(state)

        # Join parts
        location = ', '.join(parts) if parts else 'United Kingdom'

        return location

    def fetch_beers(self, brewery_name: Optional[str] = None,
                    limit: Optional[int] = None) -> List[Dict]:
        """
        Fetch beer data from Open Brewery DB.

        Note: Open Brewery DB does not provide beer-specific data,
        only brewery information.

        Args:
            brewery_name: Optional brewery name (not used)
            limit: Optional limit (not used)

        Returns:
            Empty list (API doesn't provide beer data)
        """
        logger.warning("Open Brewery DB does not provide beer-specific data")
        return []

    def get_brewery_by_name(self, name: str) -> Optional[Dict]:
        """
        Search for brewery by name.

        Args:
            name: Brewery name to search

        Returns:
            Brewery data dictionary or None if not found
        """
        try:
            params = {
                'by_name': name,
                'by_country': 'united_kingdom',
            }

            response = self.make_request(
                self.BASE_URL,
                params=params,
                timeout=30
            )

            if not response:
                return None

            data = response.json()

            if data:
                return self._process_brewery(data[0])
            else:
                return None

        except Exception as e:
            logger.error(f"Error searching for brewery '{name}': {e}")
            return None
