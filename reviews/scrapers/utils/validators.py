"""
Data validation utilities for beer scraping.

Validates scraped data against Django model constraints and business rules.
"""

import re
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Optional, Tuple


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


def validate_abv(value: any) -> Tuple[bool, Optional[Decimal], Optional[str]]:
    """
    Validate and extract ABV (Alcohol By Volume) value.

    Args:
        value: ABV value in various formats (string, number, etc.)

    Returns:
        Tuple of (is_valid, normalized_value, error_message)

    Examples:
        "4.5%" -> (True, Decimal("4.5"), None)
        "4,5%" -> (True, Decimal("4.5"), None)
        "ABV: 4.5" -> (True, Decimal("4.5"), None)
        "N/A" -> (False, None, "Invalid ABV format")
        51.0 -> (False, None, "ABV must be between 0 and 50")
    """
    if value is None or value == "":
        return False, None, "ABV is required"

    # Convert to string for processing
    value_str = str(value).strip()

    # Handle common invalid values
    invalid_values = ['n/a', 'tbc', 'unknown', 'varies', '-', 'null', 'none']
    if value_str.lower() in invalid_values:
        return False, None, f"Invalid ABV value: {value_str}"

    # Extract numeric value using regex
    # Matches patterns like: "4.5%", "4,5%", "ABV: 4.5", "4.5", etc.
    pattern = r'(\d+[.,]\d+|\d+)'
    match = re.search(pattern, value_str)

    if not match:
        return False, None, f"No numeric ABV value found in '{value_str}'"

    # Extract and normalize the number (replace comma with period)
    numeric_str = match.group(1).replace(',', '.')

    try:
        abv_value = Decimal(numeric_str)
    except (InvalidOperation, ValueError):
        return False, None, f"Invalid numeric format: {numeric_str}"

    # Validate range (0-50% as per Django model)
    if abv_value < 0 or abv_value > 50:
        return False, None, f"ABV must be between 0 and 50, got {abv_value}"

    return True, abv_value, None


def validate_ibu(value: any) -> Tuple[bool, Optional[int], Optional[str]]:
    """
    Validate and extract IBU (International Bitterness Units) value.

    Args:
        value: IBU value in various formats

    Returns:
        Tuple of (is_valid, normalized_value, error_message)

    Note:
        IBU is optional, so None is considered valid.
        Range: 0-120 as per Django model.

    Examples:
        "45" -> (True, 45, None)
        "IBU: 45" -> (True, 45, None)
        None -> (True, None, None)  # Optional field
        "N/A" -> (True, None, None)  # Treat as optional
        150 -> (False, None, "IBU must be between 0 and 120")
    """
    if value is None or value == "":
        return True, None, None  # IBU is optional

    value_str = str(value).strip()

    # Handle invalid values (treat as None/optional)
    invalid_values = ['n/a', 'tbc', 'unknown', 'varies', '-', 'null', 'none']
    if value_str.lower() in invalid_values:
        return True, None, None

    # Extract numeric value
    pattern = r'(\d+)'
    match = re.search(pattern, value_str)

    if not match:
        return True, None, None  # Can't parse, treat as optional

    try:
        ibu_value = int(match.group(1))
    except (ValueError, TypeError):
        return True, None, None

    # Validate range (0-120 as per Django model)
    if ibu_value < 0 or ibu_value > 120:
        return False, None, f"IBU must be between 0 and 120, got {ibu_value}"

    return True, ibu_value, None


def validate_required_fields(data: Dict, required_fields: List[str]) -> Tuple[bool, List[str]]:
    """
    Validate that required fields are present and non-empty.

    Args:
        data: Dictionary of data to validate
        required_fields: List of required field names

    Returns:
        Tuple of (is_valid, list_of_missing_fields)

    Example:
        validate_required_fields(
            {'name': 'Punk IPA', 'brewery': 'BrewDog'},
            ['name', 'brewery', 'abv']
        )
        -> (False, ['abv'])
    """
    missing_fields = []

    for field in required_fields:
        if field not in data or data[field] is None or str(data[field]).strip() == "":
            missing_fields.append(field)

    is_valid = len(missing_fields) == 0
    return is_valid, missing_fields


def validate_beer_data(beer_data: Dict) -> Tuple[bool, List[str]]:
    """
    Validate complete beer data dictionary.

    Args:
        beer_data: Dictionary containing beer information

    Returns:
        Tuple of (is_valid, list_of_errors)

    Required fields:
        - name: Beer name
        - brewery: Brewery name or object
        - category: Category name or object
        - abv: Alcohol by volume (validated separately)
        - style: Beer style
    """
    errors = []

    # Check required fields
    required_fields = ['name', 'brewery', 'category', 'abv', 'style']
    is_valid, missing = validate_required_fields(beer_data, required_fields)

    if not is_valid:
        errors.append(f"Missing required fields: {', '.join(missing)}")

    # Validate ABV if present
    if 'abv' in beer_data:
        is_valid_abv, _, abv_error = validate_abv(beer_data['abv'])
        if not is_valid_abv:
            errors.append(f"ABV validation failed: {abv_error}")

    # Validate IBU if present
    if 'ibu' in beer_data:
        is_valid_ibu, _, ibu_error = validate_ibu(beer_data['ibu'])
        if not is_valid_ibu:
            errors.append(f"IBU validation failed: {ibu_error}")

    # Validate name length (max 200 chars per model)
    if 'name' in beer_data and len(str(beer_data['name'])) > 200:
        errors.append(f"Beer name too long (max 200 characters): {beer_data['name'][:50]}...")

    # Validate style length (max 100 chars estimated)
    if 'style' in beer_data and len(str(beer_data['style'])) > 100:
        errors.append(f"Beer style too long (max 100 characters): {beer_data['style'][:50]}...")

    return len(errors) == 0, errors


def validate_brewery_data(brewery_data: Dict) -> Tuple[bool, List[str]]:
    """
    Validate complete brewery data dictionary.

    Args:
        brewery_data: Dictionary containing brewery information

    Returns:
        Tuple of (is_valid, list_of_errors)

    Required fields:
        - name: Brewery name
        - location: Location/city
    """
    errors = []

    # Check required fields
    required_fields = ['name', 'location']
    is_valid, missing = validate_required_fields(brewery_data, required_fields)

    if not is_valid:
        errors.append(f"Missing required fields: {', '.join(missing)}")

    # Validate name length (max 200 chars per model)
    if 'name' in brewery_data and len(str(brewery_data['name'])) > 200:
        errors.append(f"Brewery name too long (max 200 characters): {brewery_data['name'][:50]}...")

    # Validate location length (max 200 chars per model)
    if 'location' in brewery_data and len(str(brewery_data['location'])) > 200:
        errors.append(f"Location too long (max 200 characters): {brewery_data['location'][:50]}...")

    # Validate website URL if present
    if 'website' in brewery_data and brewery_data['website']:
        url = str(brewery_data['website']).strip()
        if url and not url.startswith(('http://', 'https://')):
            errors.append(f"Invalid website URL (must start with http:// or https://): {url}")

    # Validate founded_year if present
    if 'founded_year' in brewery_data and brewery_data['founded_year']:
        try:
            year = int(brewery_data['founded_year'])
            if year < 1000 or year > 2030:
                errors.append(f"Invalid founded year (must be between 1000 and 2030): {year}")
        except (ValueError, TypeError):
            errors.append(f"Invalid founded year format: {brewery_data['founded_year']}")

    return len(errors) == 0, errors


def validate_url(url: str) -> bool:
    """
    Validate URL format.

    Args:
        url: URL string to validate

    Returns:
        True if valid, False otherwise
    """
    if not url:
        return False

    # Basic URL validation
    url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(url_pattern, url, re.IGNORECASE))


def validate_image_url(url: str) -> bool:
    """
    Validate image URL format and extension.

    Args:
        url: Image URL to validate

    Returns:
        True if valid image URL, False otherwise
    """
    if not validate_url(url):
        return False

    # Check for common image extensions
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
    url_lower = url.lower()

    # Some image URLs don't have extensions (e.g., CDN images)
    # So we'll be permissive and just check if it's a valid URL
    return any(ext in url_lower for ext in image_extensions) or '?' in url
