"""
Data normalization utilities for beer scraping.

Normalizes data from various sources into consistent formats for database storage.
"""

import re
from decimal import Decimal, InvalidOperation
from typing import Optional, Dict


# British beer style to category mapping
STYLE_TO_CATEGORY = {
    # IPA variations
    'american ipa': 'IPA',
    'english ipa': 'IPA',
    'british ipa': 'IPA',
    'ipa': 'IPA',
    'india pale ale': 'IPA',
    'double ipa': 'IPA',
    'imperial ipa': 'IPA',
    'session ipa': 'IPA',
    'new england ipa': 'IPA',
    'neipa': 'IPA',
    'west coast ipa': 'IPA',

    # Pale Ale variations
    'pale ale': 'Pale Ale',
    'american pale ale': 'Pale Ale',
    'english pale ale': 'Pale Ale',
    'apa': 'Pale Ale',
    'epa': 'Pale Ale',

    # Bitter variations
    'bitter': 'Bitter',
    'best bitter': 'Bitter',
    'extra special bitter': 'Bitter',
    'esb': 'Bitter',
    'premium bitter': 'Bitter',
    'session bitter': 'Bitter',

    # Stout variations
    'stout': 'Stout',
    'dry stout': 'Stout',
    'irish stout': 'Stout',
    'milk stout': 'Stout',
    'sweet stout': 'Stout',
    'cream stout': 'Stout',
    'oatmeal stout': 'Stout',
    'imperial stout': 'Stout',
    'russian imperial stout': 'Stout',
    'chocolate stout': 'Stout',
    'coffee stout': 'Stout',

    # Porter variations
    'porter': 'Porter',
    'robust porter': 'Porter',
    'baltic porter': 'Porter',
    'brown porter': 'Porter',

    # Lager variations
    'lager': 'Lager',
    'pilsner': 'Lager',
    'pilsener': 'Lager',
    'pils': 'Lager',
    'helles': 'Lager',
    'munich helles': 'Lager',
    'vienna lager': 'Lager',
    'märzen': 'Lager',
    'oktoberfest': 'Lager',
    'bock': 'Lager',
    'doppelbock': 'Lager',
    'dunkel': 'Lager',
    'schwarzbier': 'Lager',

    # Wheat Beer variations
    'wheat': 'Wheat Beer',
    'wheat beer': 'Wheat Beer',
    'weizen': 'Wheat Beer',
    'weissbier': 'Wheat Beer',
    'hefeweizen': 'Wheat Beer',
    'witbier': 'Wheat Beer',
    'white beer': 'Wheat Beer',

    # Golden Ale variations
    'golden ale': 'Golden Ale',
    'blonde ale': 'Golden Ale',
    'blonde': 'Golden Ale',
    'summer ale': 'Golden Ale',

    # Amber Ale variations
    'amber ale': 'Amber Ale',
    'amber': 'Amber Ale',
    'red ale': 'Amber Ale',
    'irish red ale': 'Amber Ale',

    # Brown Ale variations
    'brown ale': 'Brown Ale',
    'brown': 'Brown Ale',
    'english brown ale': 'Brown Ale',
    'american brown ale': 'Brown Ale',
    'nut brown ale': 'Brown Ale',

    # Mild variations
    'mild': 'Mild',
    'dark mild': 'Mild',
    'light mild': 'Mild',

    # Strong Ale variations
    'strong ale': 'Strong Ale',
    'old ale': 'Strong Ale',
    'barley wine': 'Strong Ale',
    'barleywine': 'Strong Ale',
    'english strong ale': 'Strong Ale',
    'scotch ale': 'Strong Ale',
    'wee heavy': 'Strong Ale',
}

# Default category if style not found
DEFAULT_CATEGORY = 'Golden Ale'


def normalize_abv(value: any) -> Optional[Decimal]:
    """
    Normalize ABV value to Decimal format.

    Args:
        value: ABV value in various formats

    Returns:
        Decimal value or None if invalid

    Examples:
        "4.5%" -> Decimal("4.5")
        "4,5%" -> Decimal("4.5")
        "ABV: 4.5" -> Decimal("4.5")
        "N/A" -> None
    """
    if value is None or value == "":
        return None

    value_str = str(value).strip()

    # Handle invalid values
    invalid_values = ['n/a', 'tbc', 'unknown', 'varies', '-', 'null', 'none']
    if value_str.lower() in invalid_values:
        return None

    # Extract numeric value
    pattern = r'(\d+[.,]\d+|\d+)'
    match = re.search(pattern, value_str)

    if not match:
        return None

    # Normalize (replace comma with period)
    numeric_str = match.group(1).replace(',', '.')

    try:
        abv_value = Decimal(numeric_str)
        # Validate range
        if 0 <= abv_value <= 50:
            return abv_value
    except (InvalidOperation, ValueError):
        pass

    return None


def normalize_ibu(value: any) -> Optional[int]:
    """
    Normalize IBU value to integer format.

    Args:
        value: IBU value in various formats

    Returns:
        Integer value or None if invalid/missing

    Examples:
        "45" -> 45
        "IBU: 45" -> 45
        "N/A" -> None
    """
    if value is None or value == "":
        return None

    value_str = str(value).strip()

    # Handle invalid values
    invalid_values = ['n/a', 'tbc', 'unknown', 'varies', '-', 'null', 'none']
    if value_str.lower() in invalid_values:
        return None

    # Extract numeric value
    pattern = r'(\d+)'
    match = re.search(pattern, value_str)

    if not match:
        return None

    try:
        ibu_value = int(match.group(1))
        # Validate range
        if 0 <= ibu_value <= 120:
            return ibu_value
    except (ValueError, TypeError):
        pass

    return None


def normalize_location(location: str) -> str:
    """
    Standardize UK location names.

    Args:
        location: Raw location string

    Returns:
        Normalized location string

    Examples:
        "London, UK" -> "London"
        "Cornwall, England" -> "Cornwall"
        "Glasgow, Scotland" -> "Glasgow"
    """
    if not location:
        return ""

    location = location.strip()

    # Remove common suffixes
    suffixes_to_remove = [
        ', UK', ', United Kingdom', ', England', ', Scotland',
        ', Wales', ', Northern Ireland', ', GB', ', Great Britain'
    ]

    for suffix in suffixes_to_remove:
        if location.endswith(suffix):
            location = location[:-len(suffix)].strip()

    return location


def normalize_style(style: str) -> str:
    """
    Map beer style to standard category.

    Args:
        style: Beer style string

    Returns:
        Normalized category name

    Examples:
        "American IPA" -> "IPA"
        "Export Stout" -> "Stout"
        "Best Bitter" -> "Bitter"
        "Unknown Style" -> "Golden Ale" (default)
    """
    if not style:
        return DEFAULT_CATEGORY

    style_lower = style.strip().lower()

    # Direct lookup
    if style_lower in STYLE_TO_CATEGORY:
        return STYLE_TO_CATEGORY[style_lower]

    # Fuzzy matching - check if any key is contained in the style
    for style_key, category in STYLE_TO_CATEGORY.items():
        if style_key in style_lower or style_lower in style_key:
            return category

    # Default fallback
    return DEFAULT_CATEGORY


def normalize_brewery_name(name: str) -> str:
    """
    Normalize brewery name for consistency.

    Args:
        name: Raw brewery name

    Returns:
        Normalized brewery name

    Examples:
        "BrewDog Brewery" -> "BrewDog"
        "Fuller's Brewery Ltd." -> "Fuller's"
    """
    if not name:
        return ""

    name = name.strip()

    # Remove common brewery suffixes
    suffixes_to_remove = [
        ' Brewery',
        ' Brewing Company',
        ' Brewing Co.',
        ' Brewing',
        ' Brewers',
        ' Beer Company',
        ' Beer Co.',
        ' Ltd.',
        ' Ltd',
        ' Limited',
        ' plc',
        ' PLC',
    ]

    for suffix in suffixes_to_remove:
        if name.endswith(suffix):
            name = name[:-len(suffix)].strip()

    return name


def normalize_beer_name(name: str) -> str:
    """
    Normalize beer name for consistency.

    Args:
        name: Raw beer name

    Returns:
        Normalized beer name

    Examples:
        "  Punk IPA  " -> "Punk IPA"
        "Punk IPA (500ml)" -> "Punk IPA"
    """
    if not name:
        return ""

    name = name.strip()

    # Remove volume indicators
    name = re.sub(r'\s*\([0-9]+ml\)', '', name)
    name = re.sub(r'\s*\([0-9]+\s*cl\)', '', name)
    name = re.sub(r'\s*[0-9]+ml', '', name)

    # Remove multiple spaces
    name = re.sub(r'\s+', ' ', name)

    return name.strip()


def normalize_url(url: str) -> Optional[str]:
    """
    Normalize URL format.

    Args:
        url: Raw URL string

    Returns:
        Normalized URL or None if invalid

    Examples:
        "www.example.com" -> "https://www.example.com"
        "http://example.com" -> "https://example.com"
    """
    if not url:
        return None

    url = url.strip()

    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    # Upgrade to HTTPS if HTTP
    if url.startswith('http://'):
        url = 'https://' + url[7:]

    return url


def normalize_description(description: str, max_length: int = 1000) -> str:
    """
    Normalize beer/brewery description text.

    Args:
        description: Raw description text
        max_length: Maximum length (default 1000)

    Returns:
        Normalized description

    Examples:
        "  Too much\nwhitespace  " -> "Too much whitespace"
    """
    if not description:
        return ""

    # Remove excessive whitespace
    description = re.sub(r'\s+', ' ', description)

    # Trim to max length
    if len(description) > max_length:
        description = description[:max_length-3] + '...'

    return description.strip()


def normalize_color(color: str) -> str:
    """
    Normalize beer color name.

    Args:
        color: Raw color string

    Returns:
        Normalized color name

    Examples:
        "golden yellow" -> "Golden"
        "dark brown" -> "Brown"
    """
    if not color:
        return ""

    color = color.strip().title()

    # Common color mappings
    color_map = {
        'Golden Yellow': 'Golden',
        'Light Golden': 'Golden',
        'Pale Yellow': 'Pale',
        'Light Amber': 'Amber',
        'Deep Amber': 'Amber',
        'Dark Brown': 'Brown',
        'Light Brown': 'Brown',
        'Black': 'Black',
        'Ruby Red': 'Red',
    }

    return color_map.get(color, color)


def normalize_beer_data(data: Dict) -> Dict:
    """
    Normalize all fields in beer data dictionary.

    Args:
        data: Raw beer data dictionary

    Returns:
        Normalized beer data dictionary
    """
    normalized = data.copy()

    if 'name' in normalized:
        normalized['name'] = normalize_beer_name(normalized['name'])

    if 'abv' in normalized:
        normalized['abv'] = normalize_abv(normalized['abv'])

    if 'ibu' in normalized:
        normalized['ibu'] = normalize_ibu(normalized['ibu'])

    if 'style' in normalized:
        # Keep original style, but also map to category
        original_style = normalized['style']
        if 'category' not in normalized or not normalized['category']:
            normalized['category'] = normalize_style(original_style)

    if 'description' in normalized:
        normalized['description'] = normalize_description(normalized['description'])

    if 'color' in normalized:
        normalized['color'] = normalize_color(normalized['color'])

    return normalized


def normalize_brewery_data(data: Dict) -> Dict:
    """
    Normalize all fields in brewery data dictionary.

    Args:
        data: Raw brewery data dictionary

    Returns:
        Normalized brewery data dictionary
    """
    normalized = data.copy()

    if 'name' in normalized:
        normalized['name'] = normalize_brewery_name(normalized['name'])

    if 'location' in normalized:
        normalized['location'] = normalize_location(normalized['location'])

    if 'website' in normalized:
        normalized['website'] = normalize_url(normalized['website'])

    if 'description' in normalized:
        normalized['description'] = normalize_description(normalized['description'])

    return normalized
