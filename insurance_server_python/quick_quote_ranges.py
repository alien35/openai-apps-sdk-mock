"""Placeholder quote ranges for quick quote functionality.

These ranges are based on typical California insurance premiums and provide
users with instant feedback before collecting detailed information.
"""

from typing import Optional, Tuple

# Base ranges by region (6-month premium)
# Format: (best_case_min, best_case_max, worst_case_min, worst_case_max)
REGION_BASE_RANGES = {
    "Los Angeles Metro": (800, 1200, 2400, 3600),
    "San Francisco Bay Area": (900, 1400, 2600, 4000),
    "San Diego": (750, 1100, 2200, 3400),
    "Sacramento": (700, 1000, 2000, 3000),
    "Inland Empire": (650, 950, 1900, 2800),
    "Orange County": (850, 1250, 2500, 3800),
    "Central Valley": (600, 900, 1800, 2700),
    "Default California": (750, 1100, 2200, 3300),
}

# Zip code to region mapping (California)
ZIP_TO_REGION = {
    # Los Angeles Metro
    "900": "Los Angeles Metro",
    "901": "Los Angeles Metro",
    "902": "Los Angeles Metro",
    "903": "Los Angeles Metro",
    "904": "Los Angeles Metro",
    "905": "Los Angeles Metro",
    "906": "Los Angeles Metro",
    "911": "Los Angeles Metro",  # Pasadena
    "912": "Los Angeles Metro",  # Glendale

    # San Francisco Bay Area
    "940": "San Francisco Bay Area",
    "941": "San Francisco Bay Area",
    "942": "San Francisco Bay Area",
    "943": "San Francisco Bay Area",
    "944": "San Francisco Bay Area",
    "945": "San Francisco Bay Area",
    "946": "San Francisco Bay Area",
    "947": "San Francisco Bay Area",
    "948": "San Francisco Bay Area",
    "949": "San Francisco Bay Area",
    "950": "San Francisco Bay Area",
    "951": "San Francisco Bay Area",  # San Jose

    # San Diego
    "920": "San Diego",
    "921": "San Diego",

    # Sacramento
    "956": "Sacramento",
    "957": "Sacramento",
    "958": "Sacramento",

    # Inland Empire
    "917": "Inland Empire",  # Riverside
    "922": "Inland Empire",  # San Bernardino
    "923": "Inland Empire",
    "924": "Inland Empire",
    "925": "Inland Empire",

    # Orange County
    "926": "Orange County",
    "927": "Orange County",

    # Central Valley
    "930": "Central Valley",  # Oxnard
    "931": "Central Valley",  # Santa Barbara
    "932": "Central Valley",
    "933": "Central Valley",  # Bakersfield
    "935": "Central Valley",  # Fresno
    "936": "Central Valley",
}

# Multiplier per additional driver (after first driver)
ADDITIONAL_DRIVER_MULTIPLIER = 1.3


def get_region_from_zip(zip_code: str) -> str:
    """Get region name from zip code.

    Args:
        zip_code: 5-digit zip code

    Returns:
        Region name for rate lookup
    """
    if not zip_code or len(zip_code) < 3:
        return "Default California"

    # Try 3-digit prefix
    prefix = zip_code[:3]
    region = ZIP_TO_REGION.get(prefix)

    if region:
        return region

    # California zip codes start with 9
    if zip_code.startswith("9"):
        return "Default California"

    # Non-California (shouldn't happen in this implementation)
    return "Default California"


def calculate_quote_range(
    zip_code: str,
    num_drivers: int,
    city: Optional[str] = None,
    state: Optional[str] = None
) -> Tuple[int, int, int, int]:
    """Calculate placeholder quote range based on location and driver count.

    Args:
        zip_code: 5-digit zip code
        num_drivers: Number of drivers (1-10)
        city: City name (optional, for display only)
        state: State name (optional, for display only)

    Returns:
        Tuple of (best_min, best_max, worst_min, worst_max) for 6-month premium
    """
    region = get_region_from_zip(zip_code)
    base_best_min, base_best_max, base_worst_min, base_worst_max = REGION_BASE_RANGES[region]

    # Adjust for number of drivers (beyond first driver)
    if num_drivers > 1:
        additional_drivers = num_drivers - 1
        multiplier = 1 + (additional_drivers * (ADDITIONAL_DRIVER_MULTIPLIER - 1))

        best_min = int(base_best_min * multiplier)
        best_max = int(base_best_max * multiplier)
        worst_min = int(base_worst_min * multiplier)
        worst_max = int(base_worst_max * multiplier)
    else:
        best_min = base_best_min
        best_max = base_best_max
        worst_min = base_worst_min
        worst_max = base_worst_max

    return (best_min, best_max, worst_min, worst_max)


def format_quote_range_message(
    zip_code: str,
    city: str,
    state: str,
    num_drivers: int,
) -> str:
    """Format a user-friendly message with placeholder quote ranges.

    Args:
        zip_code: 5-digit zip code
        city: City name
        state: State name
        num_drivers: Number of drivers

    Returns:
        Formatted message with quote ranges
    """
    best_min, best_max, worst_min, worst_max = calculate_quote_range(zip_code, num_drivers)
    region = get_region_from_zip(zip_code)

    message = f"**Quick Quote Range for {city}, {state}** (Zip: {zip_code})\n\n"

    message += "Based on typical rates in your area:\n\n"

    message += f"**BEST CASE SCENARIO**\n"
    message += f"(Experienced driver, clean record, reliable vehicle)\n"
    message += f"💰 **${best_min:,} - ${best_max:,}** per 6 months\n"
    message += f"   ≈ ${int(best_min/6):,} - ${int(best_max/6):,} per month\n\n"

    message += f"**WORST CASE SCENARIO**\n"
    message += f"(New driver, newer vehicle, limited history)\n"
    message += f"💰 **${worst_min:,} - ${worst_max:,}** per 6 months\n"
    message += f"   ≈ ${int(worst_min/6):,} - ${int(worst_max/6):,} per month\n\n"

    message += "───────────────────────────────────\n\n"
    message += "Your actual rate will depend on:\n"
    message += "• Driver ages and experience\n"
    message += "• Vehicle year, make, and model\n"
    message += "• Driving history and claims\n"
    message += "• Coverage selections\n\n"

    message += "**Ready for your personalized quote?**\n\n"
    message += "I can collect your actual driver and vehicle information to get you "
    message += "precise quotes from multiple carriers."

    return message
