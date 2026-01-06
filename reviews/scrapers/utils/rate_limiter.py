"""
Rate limiting utilities for polite web scraping.

Implements rate limiting with exponential backoff and configurable delays.
"""

import time
import random
import logging
from functools import wraps
from typing import Dict, Optional, Callable
from collections import defaultdict
from datetime import datetime, timedelta


logger = logging.getLogger('beer_scraper.rate_limiter')


# Default rate limits (seconds between requests)
DEFAULT_RATE_LIMITS = {
    'openbrewerydb': 1.0,
    'ratebeer': 2.0,
    'brewery_sites': 3.0,
    'default': 2.0,
}


class RateLimiter:
    """
    Rate limiter with per-source tracking and exponential backoff.

    Tracks last request time for each source and enforces minimum delays.
    """

    def __init__(self, rate_limits: Optional[Dict[str, float]] = None):
        """
        Initialize rate limiter.

        Args:
            rate_limits: Dictionary mapping source names to delay in seconds
        """
        self.rate_limits = rate_limits or DEFAULT_RATE_LIMITS.copy()
        self.last_request_time = defaultdict(lambda: datetime.min)
        self.request_counts = defaultdict(int)

    def wait(self, source: str = 'default', jitter: bool = True):
        """
        Wait appropriate time before making next request to source.

        Args:
            source: Source name (e.g., 'openbrewerydb', 'ratebeer')
            jitter: Add random jitter (±20%) to delay
        """
        delay = self.rate_limits.get(source, self.rate_limits['default'])

        # Add jitter to prevent thundering herd
        if jitter:
            jitter_amount = delay * 0.2  # ±20%
            delay += random.uniform(-jitter_amount, jitter_amount)
            delay = max(0.5, delay)  # Minimum 0.5 seconds

        # Calculate time since last request
        last_request = self.last_request_time[source]
        time_since_last = (datetime.now() - last_request).total_seconds()

        # Wait if needed
        if time_since_last < delay:
            sleep_time = delay - time_since_last
            logger.debug(f"Rate limiting {source}: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)

        # Update last request time
        self.last_request_time[source] = datetime.now()
        self.request_counts[source] += 1

    def reset(self, source: Optional[str] = None):
        """
        Reset rate limiter for source.

        Args:
            source: Source name, or None to reset all
        """
        if source:
            self.last_request_time[source] = datetime.min
            self.request_counts[source] = 0
        else:
            self.last_request_time.clear()
            self.request_counts.clear()

    def get_stats(self, source: Optional[str] = None) -> Dict:
        """
        Get rate limiter statistics.

        Args:
            source: Source name, or None for all sources

        Returns:
            Dictionary of statistics
        """
        if source:
            return {
                'source': source,
                'request_count': self.request_counts[source],
                'last_request': self.last_request_time[source],
            }
        else:
            return {
                source: {
                    'request_count': self.request_counts[source],
                    'last_request': self.last_request_time[source],
                }
                for source in self.request_counts.keys()
            }


# Global rate limiter instance
_global_rate_limiter = RateLimiter()


def rate_limited(source: str = 'default', jitter: bool = True):
    """
    Decorator to rate limit function calls.

    Args:
        source: Source name for rate limiting
        jitter: Add random jitter to delays

    Example:
        @rate_limited('openbrewerydb')
        def fetch_breweries():
            # Makes request to Open Brewery DB
            pass
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            _global_rate_limiter.wait(source, jitter)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def exponential_backoff(max_attempts: int = 3, base_delay: float = 5.0,
                        max_delay: float = 60.0, backoff_factor: float = 2.0):
    """
    Decorator to retry function with exponential backoff on failure.

    Args:
        max_attempts: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        backoff_factor: Multiplier for each retry

    Example:
        @exponential_backoff(max_attempts=3, base_delay=5)
        def fetch_data():
            # May raise exception
            pass
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {e}"
                    )

                    if attempt < max_attempts - 1:
                        # Calculate delay with exponential backoff
                        delay = min(base_delay * (backoff_factor ** attempt), max_delay)

                        # Add jitter
                        delay += random.uniform(0, delay * 0.2)

                        logger.info(f"Retrying in {delay:.2f}s...")
                        time.sleep(delay)

            # All attempts failed
            logger.error(f"All {max_attempts} attempts failed for {func.__name__}")
            raise last_exception

        return wrapper
    return decorator


class RetryStrategy:
    """
    Configurable retry strategy with exponential backoff.
    """

    def __init__(self, max_attempts: int = 3, base_delay: float = 5.0,
                 max_delay: float = 60.0, backoff_factor: float = 2.0):
        """
        Initialize retry strategy.

        Args:
            max_attempts: Maximum number of attempts
            base_delay: Initial delay in seconds
            max_delay: Maximum delay cap
            backoff_factor: Multiplier for each retry
        """
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor

    def execute(self, func: Callable, *args, **kwargs):
        """
        Execute function with retry strategy.

        Args:
            func: Function to execute
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function

        Returns:
            Function result if successful

        Raises:
            Last exception if all attempts fail
        """
        last_exception = None

        for attempt in range(self.max_attempts):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                logger.warning(
                    f"Attempt {attempt + 1}/{self.max_attempts} failed: {e}"
                )

                if attempt < self.max_attempts - 1:
                    delay = self._calculate_delay(attempt)
                    logger.info(f"Retrying in {delay:.2f}s...")
                    time.sleep(delay)

        logger.error(f"All {self.max_attempts} attempts failed")
        raise last_exception

    def _calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for given attempt number.

        Args:
            attempt: Attempt number (0-indexed)

        Returns:
            Delay in seconds
        """
        delay = min(
            self.base_delay * (self.backoff_factor ** attempt),
            self.max_delay
        )

        # Add jitter (0-20%)
        delay += random.uniform(0, delay * 0.2)

        return delay


def wait_for_rate_limit(source: str = 'default', jitter: bool = True):
    """
    Wait for rate limit before proceeding.

    Args:
        source: Source name
        jitter: Add random jitter
    """
    _global_rate_limiter.wait(source, jitter)


def reset_rate_limiter(source: Optional[str] = None):
    """
    Reset global rate limiter.

    Args:
        source: Source to reset, or None for all
    """
    _global_rate_limiter.reset(source)


def get_rate_limit_stats(source: Optional[str] = None) -> Dict:
    """
    Get rate limiter statistics.

    Args:
        source: Source name, or None for all

    Returns:
        Statistics dictionary
    """
    return _global_rate_limiter.get_stats(source)
