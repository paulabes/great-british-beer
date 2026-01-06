"""
Robots.txt compliance checker for ethical web scraping.

Checks if URLs can be scraped according to robots.txt rules.
"""

import logging
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
from typing import Dict, Optional


logger = logging.getLogger('beer_scraper.robots')


class RobotsChecker:
    """
    Check robots.txt compliance for URLs.

    Caches robot parsers to avoid repeated fetches.
    """

    def __init__(self, user_agent: str = '*'):
        """
        Initialize robots checker.

        Args:
            user_agent: User agent string to check permissions for
        """
        self.user_agent = user_agent
        self._parsers: Dict[str, RobotFileParser] = {}

    def can_fetch(self, url: str) -> bool:
        """
        Check if URL can be fetched according to robots.txt.

        Args:
            url: URL to check

        Returns:
            True if allowed, False if disallowed

        Note:
            If robots.txt cannot be fetched, assumes allowed (fail open).
        """
        try:
            parsed_url = urlparse(url)
            domain = f"{parsed_url.scheme}://{parsed_url.netloc}"

            # Get or create parser for domain
            if domain not in self._parsers:
                self._parsers[domain] = self._fetch_robots(domain)

            parser = self._parsers[domain]

            if parser is None:
                # Could not fetch robots.txt, assume allowed
                logger.warning(f"Could not fetch robots.txt for {domain}, assuming allowed")
                return True

            # Check if URL is allowed
            allowed = parser.can_fetch(self.user_agent, url)

            if not allowed:
                logger.warning(f"URL disallowed by robots.txt: {url}")

            return allowed

        except Exception as e:
            logger.error(f"Error checking robots.txt for {url}: {e}")
            # On error, assume allowed (fail open)
            return True

    def _fetch_robots(self, domain: str) -> Optional[RobotFileParser]:
        """
        Fetch and parse robots.txt for domain.

        Args:
            domain: Domain URL (e.g., "https://example.com")

        Returns:
            RobotFileParser or None if fetch fails
        """
        try:
            robots_url = f"{domain}/robots.txt"
            logger.debug(f"Fetching robots.txt from {robots_url}")

            parser = RobotFileParser()
            parser.set_url(robots_url)
            parser.read()

            logger.info(f"Successfully loaded robots.txt for {domain}")
            return parser

        except Exception as e:
            logger.warning(f"Could not fetch robots.txt for {domain}: {e}")
            return None

    def get_crawl_delay(self, url: str) -> Optional[float]:
        """
        Get crawl delay for URL from robots.txt.

        Args:
            url: URL to check

        Returns:
            Crawl delay in seconds, or None if not specified
        """
        try:
            parsed_url = urlparse(url)
            domain = f"{parsed_url.scheme}://{parsed_url.netloc}"

            if domain not in self._parsers:
                self._parsers[domain] = self._fetch_robots(domain)

            parser = self._parsers[domain]

            if parser is None:
                return None

            # Get crawl delay for user agent
            delay = parser.crawl_delay(self.user_agent)

            if delay:
                logger.info(f"Crawl delay for {domain}: {delay}s")

            return delay

        except Exception as e:
            logger.error(f"Error getting crawl delay for {url}: {e}")
            return None

    def clear_cache(self, domain: Optional[str] = None):
        """
        Clear cached robots.txt parsers.

        Args:
            domain: Specific domain to clear, or None for all
        """
        if domain:
            if domain in self._parsers:
                del self._parsers[domain]
                logger.debug(f"Cleared robots.txt cache for {domain}")
        else:
            self._parsers.clear()
            logger.debug("Cleared all robots.txt cache")


# Global robots checker instance
_global_robots_checker = RobotsChecker(
    user_agent='GreatBritishBeerBot/1.0 (+https://greatbritish.beer)'
)


def can_fetch(url: str, user_agent: Optional[str] = None) -> bool:
    """
    Check if URL can be fetched according to robots.txt.

    Args:
        url: URL to check
        user_agent: Optional custom user agent

    Returns:
        True if allowed, False if disallowed

    Example:
        if can_fetch('https://example.com/beers'):
            # Proceed with scraping
            pass
    """
    if user_agent:
        checker = RobotsChecker(user_agent)
        return checker.can_fetch(url)
    else:
        return _global_robots_checker.can_fetch(url)


def get_crawl_delay(url: str, user_agent: Optional[str] = None) -> Optional[float]:
    """
    Get crawl delay for URL from robots.txt.

    Args:
        url: URL to check
        user_agent: Optional custom user agent

    Returns:
        Crawl delay in seconds, or None if not specified

    Example:
        delay = get_crawl_delay('https://example.com')
        if delay:
            time.sleep(delay)
    """
    if user_agent:
        checker = RobotsChecker(user_agent)
        return checker.get_crawl_delay(url)
    else:
        return _global_robots_checker.get_crawl_delay(url)


def clear_robots_cache(domain: Optional[str] = None):
    """
    Clear cached robots.txt data.

    Args:
        domain: Specific domain to clear, or None for all
    """
    _global_robots_checker.clear_cache(domain)


def check_url_allowed(url: str, user_agent: str = '*') -> tuple[bool, Optional[str]]:
    """
    Check if URL is allowed and return detailed result.

    Args:
        url: URL to check
        user_agent: User agent string

    Returns:
        Tuple of (is_allowed, reason_if_disallowed)

    Example:
        allowed, reason = check_url_allowed('https://example.com/beers')
        if not allowed:
            print(f"Cannot scrape: {reason}")
    """
    try:
        checker = RobotsChecker(user_agent)
        allowed = checker.can_fetch(url)

        if allowed:
            return True, None
        else:
            return False, "Disallowed by robots.txt"

    except Exception as e:
        logger.error(f"Error checking URL: {e}")
        return True, None  # Fail open
