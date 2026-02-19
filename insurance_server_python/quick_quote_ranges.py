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


def calculate_enhanced_quote_range(
    zip_code: str,
    city: str,
    state: str,
    primary_driver_age: int,
    primary_driver_marital_status: str,
    vehicle_1_year: int,
    coverage_type: str,
    num_drivers: int = 1,
    num_vehicles: int = 1,
    additional_driver_age: Optional[int] = None,
    additional_driver_marital_status: Optional[str] = None,
) -> Tuple[int, int, int, int]:
    """Calculate enhanced quote range based on detailed driver and vehicle information.

    Args:
        zip_code: 5-digit zip code
        city: City name
        state: State name
        primary_driver_age: Age of primary driver
        primary_driver_marital_status: Marital status of primary driver
        vehicle_1_year: Year of primary vehicle
        coverage_type: 'liability' or 'full_coverage'
        num_drivers: Number of drivers (1 or 2)
        num_vehicles: Number of vehicles (1 or 2)
        additional_driver_age: Age of additional driver if present
        additional_driver_marital_status: Marital status of additional driver if present

    Returns:
        Tuple of (best_min, best_max, worst_min, worst_max) for 6-month premium
    """
    # Start with base region ranges
    region = get_region_from_zip(zip_code)
    base_best_min, base_best_max, base_worst_min, base_worst_max = REGION_BASE_RANGES[region]

    # Age factor (younger drivers = higher rates)
    age_factor = 1.0
    if primary_driver_age < 25:
        age_factor = 1.8 if primary_driver_age < 20 else 1.5
    elif primary_driver_age < 30:
        age_factor = 1.2
    elif primary_driver_age >= 60:
        age_factor = 1.1

    # Marital status factor (married drivers typically get lower rates)
    marital_factor = 1.0
    if primary_driver_marital_status == "married":
        marital_factor = 0.9  # 10% discount for married
    elif primary_driver_marital_status in ["divorced", "widowed"]:
        marital_factor = 0.95  # 5% discount

    # Vehicle age factor (newer vehicles cost more to insure for full coverage)
    current_year = 2026
    vehicle_age = current_year - vehicle_1_year
    vehicle_factor = 1.0
    if coverage_type == "full_coverage":
        if vehicle_age < 3:
            vehicle_factor = 1.3  # Newer vehicles cost more for comp/coll
        elif vehicle_age < 7:
            vehicle_factor = 1.15
    else:
        # Liability only is cheaper
        vehicle_factor = 0.7

    # Coverage type factor
    coverage_factor = 1.5 if coverage_type == "full_coverage" else 1.0

    # Additional driver factor
    driver_factor = 1.0
    if num_drivers > 1 and additional_driver_age:
        if additional_driver_age < 25:
            driver_factor = 1.6 if additional_driver_age < 20 else 1.4
        else:
            driver_factor = 1.3

        # Additional driver marital status bonus
        if additional_driver_marital_status == "married":
            driver_factor *= 0.95  # Small additional discount if both married

    # Additional vehicle factor
    vehicle_count_factor = 1.4 if num_vehicles > 1 else 1.0

    # Apply all factors
    total_factor = age_factor * marital_factor * vehicle_factor * coverage_factor * driver_factor * vehicle_count_factor

    # Calculate adjusted ranges
    best_min = int(base_best_min * total_factor * 0.8)  # Best case: 20% discount
    best_max = int(base_best_max * total_factor * 0.9)  # Best case: 10% discount
    worst_min = int(base_worst_min * total_factor * 1.1)  # Worst case: 10% surcharge
    worst_max = int(base_worst_max * total_factor * 1.3)  # Worst case: 30% surcharge

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
