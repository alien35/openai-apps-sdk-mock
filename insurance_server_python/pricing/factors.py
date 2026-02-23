"""
Factor calculation functions for insurance quote estimation.

All factors use configuration from config.py for easy adjustment.
"""

from typing import Tuple
from .config import (
    AGE_FACTOR_CURVES,
    MARITAL_STATUS_FACTORS,
    VEHICLE_AGE_FACTORS,
    VEHICLE_TYPE_FACTORS,
    LUXURY_MAKES,
    PERFORMANCE_MODELS,
    ECONOMY_MODELS,
    ZIP_BUCKET_MULTIPLIERS,
    COVERAGE_TYPE_FACTORS,
    ZIP_COST_DESCRIPTIONS,
)


def calculate_age_factor(age: int) -> Tuple[float, str]:
    """
    Calculate age-based premium multiplier.

    Args:
        age: Driver's age

    Returns:
        (multiplier, explanation)
    """
    for min_age, max_age, multiplier, description in AGE_FACTOR_CURVES:
        if min_age <= age <= max_age:
            return (multiplier, description)

    # Fallback for edge cases
    return (1.00, f"Age {age} - standard rates")


def calculate_marital_factor(marital_status: str) -> Tuple[float, str]:
    """
    Calculate marital status premium multiplier.

    Args:
        marital_status: Marital status string (married, single, etc.)

    Returns:
        (multiplier, explanation)
    """
    status_lower = marital_status.lower().strip()

    # Check each status keyword
    for keyword, (multiplier, description) in MARITAL_STATUS_FACTORS.items():
        if keyword in status_lower:
            return (multiplier, description)

    # Default
    return MARITAL_STATUS_FACTORS["default"]


def calculate_vehicle_factor(
    year: int,
    make: str,
    model: str,
    current_year: int = 2026
) -> Tuple[float, str]:
    """
    Calculate vehicle-based premium multiplier.

    Considers both vehicle age and type (luxury, performance, economy).

    Args:
        year: Vehicle year
        make: Vehicle make
        model: Vehicle model
        current_year: Current year for age calculation

    Returns:
        (multiplier, explanation)
    """
    vehicle_age = current_year - year
    make_upper = make.upper().strip()
    model_upper = model.upper().strip()

    # Calculate age factor
    age_multiplier = 1.00
    age_description = "Standard age vehicle"

    for max_age, multiplier, description in VEHICLE_AGE_FACTORS:
        if vehicle_age <= max_age:
            age_multiplier = multiplier
            age_description = description
            break

    # Determine vehicle type
    type_multiplier = 1.00
    type_description = "Standard vehicle type"

    if any(luxury in make_upper for luxury in LUXURY_MAKES):
        type_multiplier, type_description = VEHICLE_TYPE_FACTORS["luxury"]
    elif any(perf in model_upper for perf in PERFORMANCE_MODELS):
        type_multiplier, type_description = VEHICLE_TYPE_FACTORS["performance"]
    elif any(econ in model_upper for econ in ECONOMY_MODELS):
        type_multiplier, type_description = VEHICLE_TYPE_FACTORS["economy"]

    # Combine factors
    final_multiplier = age_multiplier * type_multiplier
    explanation = f"{year} {make} {model}: {age_description}; {type_description}"

    return (final_multiplier, explanation)


def get_zip_multiplier(zip_code: str) -> float:
    """
    Get cost multiplier based on ZIP code.

    Args:
        zip_code: 5-digit ZIP code

    Returns:
        Cost multiplier (e.g., 1.35 for high-cost area)
    """
    if not zip_code or len(zip_code) < 3:
        return 1.0

    # Try 3-digit prefix lookup
    prefix = zip_code[:3]
    if prefix in ZIP_BUCKET_MULTIPLIERS:
        return ZIP_BUCKET_MULTIPLIERS[prefix]

    # Try 2-digit for broader area
    prefix_2 = zip_code[:2]
    if prefix_2 in ZIP_BUCKET_MULTIPLIERS:
        return ZIP_BUCKET_MULTIPLIERS[prefix_2]

    # Default to suburban baseline
    return ZIP_BUCKET_MULTIPLIERS.get("SUBURBAN", 1.0)


def get_zip_description(zip_multiplier: float) -> str:
    """
    Get human-readable description of ZIP cost level.

    Args:
        zip_multiplier: The multiplier value

    Returns:
        Description string
    """
    if zip_multiplier >= 1.30:
        return ZIP_COST_DESCRIPTIONS["high"]
    elif zip_multiplier >= 1.10:
        return ZIP_COST_DESCRIPTIONS["medium_high"]
    elif zip_multiplier <= 0.90:
        return ZIP_COST_DESCRIPTIONS["low"]
    else:
        return ZIP_COST_DESCRIPTIONS["medium"]


def calculate_coverage_factor(coverage_type: str) -> Tuple[float, str]:
    """
    Calculate coverage type premium multiplier.

    Args:
        coverage_type: Coverage type string (full, liability, etc.)

    Returns:
        (multiplier, explanation)
    """
    coverage_lower = coverage_type.lower().strip()

    # Check each coverage keyword
    for keyword, (multiplier, description) in COVERAGE_TYPE_FACTORS.items():
        if keyword in coverage_lower:
            return (multiplier, description)

    # Default
    return COVERAGE_TYPE_FACTORS["default"]
