"""
Image downloading utilities with concurrent downloads and validation.
"""

import logging
import os
import requests
from io import BytesIO
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional, Tuple
from PIL import Image


logger = logging.getLogger('beer_scraper.images')


class ImageDownloader:
    """
    Concurrent image downloader with validation and processing.
    """

    def __init__(self, max_workers: int = 5, timeout: int = 30, max_retries: int = 2):
        """
        Initialize image downloader.

        Args:
            max_workers: Number of concurrent download threads
            timeout: Timeout per image in seconds
            max_retries: Number of retry attempts per image
        """
        self.max_workers = max_workers
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        self.stats = {
            'total': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
        }

    def download_image(self, url: str, save_path: str,
                      max_size: Tuple[int, int] = (600, 600)) -> bool:
        """
        Download and process single image.

        Args:
            url: Image URL
            save_path: Path to save image
            max_size: Maximum dimensions (width, height)

        Returns:
            True if successful, False otherwise
        """
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Downloading image from {url} (attempt {attempt + 1})")

                # Download image
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()

                # Check content type
                content_type = response.headers.get('Content-Type', '')
                if not content_type.startswith('image/'):
                    logger.warning(f"Invalid content type: {content_type} for {url}")
                    return False

                # Load image with PIL
                img_data = BytesIO(response.content)
                img = Image.open(img_data)

                # Convert RGBA to RGB if needed
                if img.mode == 'RGBA':
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])  # Alpha channel as mask
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')

                # Resize if needed
                if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                    logger.debug(f"Resized image to {img.size}")

                # Ensure directory exists
                os.makedirs(os.path.dirname(save_path), exist_ok=True)

                # Save image
                img.save(save_path, 'JPEG', quality=85, optimize=True)

                logger.info(f"Successfully downloaded image to {save_path}")
                return True

            except requests.RequestException as e:
                logger.warning(f"HTTP error downloading {url}: {e}")
                if attempt < self.max_retries - 1:
                    continue
            except Exception as e:
                logger.error(f"Error processing image {url}: {e}")
                return False

        logger.error(f"Failed to download {url} after {self.max_retries} attempts")
        return False

    def download_images(self, image_tasks: List[Dict]) -> Dict:
        """
        Download multiple images concurrently.

        Args:
            image_tasks: List of dicts with 'url' and 'save_path' keys

        Returns:
            Dictionary with statistics

        Example:
            tasks = [
                {'url': 'https://...', 'save_path': '/path/to/beer1.jpg'},
                {'url': 'https://...', 'save_path': '/path/to/beer2.jpg'},
            ]
            results = downloader.download_images(tasks)
        """
        self.stats['total'] = len(image_tasks)
        logger.info(f"Starting download of {len(image_tasks)} images with {self.max_workers} workers")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            futures = {
                executor.submit(
                    self.download_image,
                    task['url'],
                    task['save_path']
                ): task for task in image_tasks
            }

            # Process completed tasks
            for future in as_completed(futures):
                task = futures[future]
                try:
                    success = future.result()
                    if success:
                        self.stats['successful'] += 1
                    else:
                        self.stats['failed'] += 1
                except Exception as e:
                    logger.error(f"Exception downloading {task['url']}: {e}")
                    self.stats['failed'] += 1

        logger.info(
            f"Image download complete: {self.stats['successful']} successful, "
            f"{self.stats['failed']} failed out of {self.stats['total']}"
        )

        return self.stats.copy()

    def validate_image_url(self, url: str) -> bool:
        """
        Validate image URL without downloading.

        Args:
            url: Image URL

        Returns:
            True if valid, False otherwise
        """
        if not url:
            return False

        try:
            # HEAD request to check content type
            response = self.session.head(url, timeout=10)
            content_type = response.headers.get('Content-Type', '')

            return content_type.startswith('image/')

        except Exception as e:
            logger.debug(f"Could not validate image URL {url}: {e}")
            return False

    def get_stats(self) -> Dict:
        """Get download statistics."""
        return self.stats.copy()

    def reset_stats(self):
        """Reset statistics."""
        for key in self.stats:
            self.stats[key] = 0

    def close(self):
        """Close session."""
        self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False


def download_single_image(url: str, save_path: str,
                         max_size: Tuple[int, int] = (600, 600)) -> bool:
    """
    Convenience function to download single image.

    Args:
        url: Image URL
        save_path: Path to save image
        max_size: Maximum dimensions

    Returns:
        True if successful, False otherwise
    """
    with ImageDownloader() as downloader:
        return downloader.download_image(url, save_path, max_size)


def download_multiple_images(image_tasks: List[Dict],
                            max_workers: int = 5) -> Dict:
    """
    Convenience function to download multiple images.

    Args:
        image_tasks: List of {'url', 'save_path'} dicts
        max_workers: Number of concurrent threads

    Returns:
        Statistics dictionary
    """
    with ImageDownloader(max_workers=max_workers) as downloader:
        return downloader.download_images(image_tasks)
