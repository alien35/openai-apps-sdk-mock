"""
Risk scoring and uncertainty range calculation.
"""

from typing import Dict, Tuple, Any
from .config import (
    RISK_SCORE_WEIGHTS,
    CONFIDENCE_BANDS,
    MONTHLY_MINIMUM_BY_STATE,
    MONTHLY_MAXIMUM,
)
from .factors import get_zip_multiplier


def calculate_risk_score(
    age: int,
    marital_status: str,
    vehicle_age: int,
    zip_code: str,
    coverage_type: str,
    accidents: int = 0,
    tickets: int = 0,
) -> float:
    """
    Calculate overall risk score from 0.0 (lowest risk) to 1.0 (highest risk).

    This score is used to interpolate carrier multipliers between their
    low and high range.

    Args:
        age: Driver age
        marital_status: Marital status
        vehicle_age: Age of vehicle in years
        zip_code: ZIP code
        coverage_type: Coverage type
        accidents: Number of accidents (if available)
        tickets: Number of tickets (if available)

    Returns:
        Risk score between 0.0 and 1.0
    """
    score = 0.5  # Start at middle baseline

    # Age contribution (weighted by RISK_SCORE_WEIGHTS["age"])
    age_contribution = 0.0
    if age < 21:
        age_contribution = 0.50  # Very high risk
    elif age < 25:
        age_contribution = 0.30  # High risk
    elif age < 30:
        age_contribution = 0.15  # Moderate risk
    elif age <= 65:
        age_contribution = -0.15  # Low risk (discount)
    else:
        age_contribution = 0.10  # Slightly elevated for seniors

    score += age_contribution * RISK_SCORE_WEIGHTS["age"] / 0.50  # Normalize

    # Marital status contribution
    marital_contribution = 0.0
    if "married" in marital_status.lower():
        marital_contribution = -0.10  # Discount
    elif "single" in marital_status.lower():
        marital_contribution = 0.05  # Slight increase

    score += marital_contribution * RISK_SCORE_WEIGHTS["marital"] / 0.10

    # Vehicle age contribution
    vehicle_contribution = 0.0
    if vehicle_age <= 2:
        vehicle_contribution = 0.15  # Higher value, more at risk
    elif vehicle_age >= 10:
        vehicle_contribution = -0.10  # Lower value, less at risk

    score += vehicle_contribution * RISK_SCORE_WEIGHTS["vehicle_age"] / 0.15

    # ZIP cost contribution
    zip_mult = get_zip_multiplier(zip_code)
    zip_contribution = 0.0
    if zip_mult > 1.30:
        zip_contribution = 0.20  # High-cost area
    elif zip_mult > 1.10:
        zip_contribution = 0.10  # Moderate-cost area
    elif zip_mult < 0.90:
        zip_contribution = -0.15  # Low-cost area

    score += zip_contribution * RISK_SCORE_WEIGHTS["zip_cost"] / 0.20

    # Coverage type contribution
    coverage_contribution = 0.0
    if "liability" in coverage_type.lower():
        coverage_contribution = -0.10  # Less coverage = less premium

    score += coverage_contribution * RISK_SCORE_WEIGHTS["coverage"] / 0.10

    # Violations contribution (if provided)
    if accidents or tickets:
        violations_contribution = min(accidents * 0.20, 0.30) + min(tickets * 0.10, 0.20)
        score += violations_contribution * RISK_SCORE_WEIGHTS["violations"] / 0.50

    # Clamp to valid range
    return max(0.0, min(1.0, score))


def assess_data_completeness(inputs: Dict[str, Any]) -> Tuple[float, str]:
    """
    Assess how complete the input data is and return uncertainty band.

    More complete data = tighter confidence bands.

    Args:
        inputs: Dictionary of all input values

    Returns:
        (band_percentage, confidence_level)
        Example: (0.30, "medium") means ±30% range with medium confidence
    """
    score = 0

    # Core inputs we always collect
    if inputs.get("age") is not None:
        score += 1
    if inputs.get("zip_code"):
        score += 1
    if inputs.get("vehicle"):
        score += 1
    if inputs.get("coverage_type"):
        score += 1
    if inputs.get("marital_status"):
        score += 1

    # Optional inputs that improve accuracy
    if inputs.get("accidents") is not None:
        score += 1
    if inputs.get("tickets") is not None:
        score += 1
    if inputs.get("annual_mileage") is not None:
        score += 1
    if inputs.get("credit_tier"):
        score += 1
    if inputs.get("continuous_insurance") is not None:
        score += 1

    # Determine band based on score
    for min_score, band, confidence in CONFIDENCE_BANDS:
        if score >= min_score:
            return (band, confidence)

    # Fallback
    return (0.40, "low")


def calculate_range(
    point_estimate_monthly: float,
    band_percentage: float,
    state: str,
) -> Tuple[int, int]:
    """
    Calculate realistic price range with sanity bounds.

    Args:
        point_estimate_monthly: Base monthly estimate
        band_percentage: Uncertainty band (e.g., 0.30 for ±30%)
        state: State abbreviation

    Returns:
        (low_monthly, high_monthly) tuple of integers
    """
    # Calculate raw range
    low = point_estimate_monthly * (1 - band_percentage)
    high = point_estimate_monthly * (1 + band_percentage)

    # Apply state-specific minimum
    monthly_min = MONTHLY_MINIMUM_BY_STATE.get(
        state,
        MONTHLY_MINIMUM_BY_STATE["DEFAULT"]
    )

    # Apply bounds
    low = max(low, monthly_min)
    high = min(high, MONTHLY_MAXIMUM)

    # Ensure low < high
    if low >= high:
        high = low * 1.20  # At least 20% above minimum

    return (int(low), int(high))
