"""
Base scraper class for all beer data scrapers.

Provides common functionality for rate limiting, error handling,
data validation, and robots.txt compliance.
"""

import logging
import requests
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from fake_useragent import UserAgent

from .utils.rate_limiter import RateLimiter, RetryStrategy
from .utils.robots_checker import RobotsChecker
from .utils.validators import (
    validate_beer_data,
    validate_brewery_data,
    ValidationError
)
from .utils.normalizers import (
    normalize_beer_data,
    normalize_brewery_data
)


logger = logging.getLogger('beer_scraper')


class BaseScraper(ABC):
    """
    Abstract base class for all scrapers.

    Provides common functionality:
    - HTTP session management with proper headers
    - Rate limiting and retry logic
    - Robots.txt compliance checking
    - Data validation and normalization
    - Error handling and logging
    """

    def __init__(self, source_name: str, rate_limit: float = 2.0,
                 check_robots: bool = True):
        """
        Initialize base scraper.

        Args:
            source_name: Name of data source (for rate limiting)
            rate_limit: Delay between requests in seconds
            check_robots: Whether to check robots.txt
        """
        self.source_name = source_name
        self.rate_limit = rate_limit
        self.check_robots_txt = check_robots

        # HTTP session with proper headers
        self.session = requests.Session()
        self.session.headers.update(self._get_headers())

        # Rate limiter
        self.rate_limiter = RateLimiter({
            self.source_name: rate_limit,
            'default': rate_limit
        })

        # Robots checker
        self.robots_checker = RobotsChecker(
            user_agent=self.session.headers.get('User-Agent', '*')
        )

        # Retry strategy
        self.retry_strategy = RetryStrategy(
            max_attempts=3,
            base_delay=5.0,
            max_delay=60.0,
            backoff_factor=2.0
        )

        # Statistics
        self.stats = {
            'requests_made': 0,
            'breweries_scraped': 0,
            'beers_scraped': 0,
            'validation_errors': 0,
            'http_errors': 0,
        }

        logger.info(f"Initialized {self.__class__.__name__} scraper")

    def _get_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers for requests.

        Returns:
            Dictionary of headers
        """
        try:
            ua = UserAgent()
            user_agent = ua.random
        except Exception:
            # Fallback user agent
            user_agent = (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/91.0.4472.124 Safari/537.36'
            )

        return {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-GB,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    def make_request(self, url: str, method: str = 'GET', **kwargs) -> Optional[requests.Response]:
        """
        Make HTTP request with rate limiting, retry logic, and robots.txt checking.

        Args:
            url: URL to request
            method: HTTP method (GET, POST, etc.)
            **kwargs: Additional arguments for requests

        Returns:
            Response object or None if failed

        Raises:
            requests.RequestException: If request fails after retries
        """
        # Check robots.txt
        if self.check_robots_txt and not self.robots_checker.can_fetch(url):
            logger.warning(f"URL disallowed by robots.txt: {url}")
            return None

        # Rate limit
        self.rate_limiter.wait(self.source_name)

        # Make request with retry
        def _request():
            logger.debug(f"Making {method} request to {url}")
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response

        try:
            response = self.retry_strategy.execute(_request)
            self.stats['requests_made'] += 1
            return response

        except requests.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            self.stats['http_errors'] += 1
            raise

    def validate_and_normalize_beer(self, beer_data: Dict) -> Optional[Dict]:
        """
        Validate and normalize beer data.

        Args:
            beer_data: Raw beer data dictionary

        Returns:
            Normalized beer data or None if validation fails
        """
        try:
            # Normalize data
            normalized = normalize_beer_data(beer_data)

            # Validate
            is_valid, errors = validate_beer_data(normalized)

            if not is_valid:
                logger.warning(f"Beer validation failed: {errors}")
                self.stats['validation_errors'] += 1
                return None

            return normalized

        except Exception as e:
            logger.error(f"Error validating beer data: {e}")
            self.stats['validation_errors'] += 1
            return None

    def validate_and_normalize_brewery(self, brewery_data: Dict) -> Optional[Dict]:
        """
        Validate and normalize brewery data.

        Args:
            brewery_data: Raw brewery data dictionary

        Returns:
            Normalized brewery data or None if validation fails
        """
        try:
            # Normalize data
            normalized = normalize_brewery_data(brewery_data)

            # Validate
            is_valid, errors = validate_brewery_data(normalized)

            if not is_valid:
                logger.warning(f"Brewery validation failed: {errors}")
                self.stats['validation_errors'] += 1
                return None

            return normalized

        except Exception as e:
            logger.error(f"Error validating brewery data: {e}")
            self.stats['validation_errors'] += 1
            return None

    # Abstract methods to be implemented by subclasses

    @abstractmethod
    def fetch_breweries(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Fetch brewery data from source.

        Args:
            limit: Optional limit on number of breweries to fetch

        Returns:
            List of brewery data dictionaries
        """
        pass

    @abstractmethod
    def fetch_beers(self, brewery_name: Optional[str] = None,
                    limit: Optional[int] = None) -> List[Dict]:
        """
        Fetch beer data from source.

        Args:
            brewery_name: Optional brewery to filter by
            limit: Optional limit on number of beers to fetch

        Returns:
            List of beer data dictionaries
        """
        pass

    def get_stats(self) -> Dict:
        """
        Get scraper statistics.

        Returns:
            Dictionary of statistics
        """
        return self.stats.copy()

    def reset_stats(self):
        """Reset scraper statistics."""
        for key in self.stats:
            self.stats[key] = 0
        logger.info(f"Reset statistics for {self.__class__.__name__}")

    def close(self):
        """Clean up resources."""
        self.session.close()
        logger.info(f"Closed {self.__class__.__name__} scraper")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False
