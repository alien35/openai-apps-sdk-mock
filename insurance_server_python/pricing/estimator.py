"""
Main insurance quote estimation engine.

This ties together all the factors, risk scoring, and carrier-specific calculations.
"""

import logging
from typing import Dict, List, Any, Optional

from .config import (
    STATE_BASE_FULL_COVERAGE_ANNUAL,
    CARRIER_BASE_MULTIPLIERS,
    CARRIER_STATE_ADJUSTMENTS,
    CARRIER_PRICING_DESCRIPTIONS,
)
from .factors import (
    calculate_age_factor,
    calculate_marital_factor,
    calculate_vehicle_factor,
    get_zip_multiplier,
    get_zip_description,
    calculate_coverage_factor,
)
from .risk_score import (
    calculate_risk_score,
    assess_data_completeness,
    calculate_range,
)

logger = logging.getLogger(__name__)


class InsuranceQuoteEstimator:
    """
    Main estimation engine for insurance quotes.

    Generates realistic quote estimates with uncertainty ranges based on
    state rates, demographic factors, vehicle info, and carrier profiles.
    """

    def estimate_quotes(
        self,
        state: str,
        zip_code: str,
        age: int,
        marital_status: str,
        vehicle: Dict[str, Any],
        coverage_type: str,
        carriers: List[str],
        **optional_inputs,
    ) -> Dict[str, Any]:
        """
        Generate quote estimates for multiple carriers.

        Args:
            state: State abbreviation (e.g., "CA")
            zip_code: 5-digit ZIP code
            age: Driver age
            marital_status: Marital status
            vehicle: Dict with keys: year, make, model
            coverage_type: Coverage type (full, liability, etc.)
            carriers: List of carrier names to quote
            **optional_inputs: Additional inputs (accidents, tickets, mileage, etc.)

        Returns:
            Dictionary with structure:
            {
                "baseline": {
                    "annual": int,
                    "monthly": int,
                    "band": float,
                    "confidence": str
                },
                "quotes": [
                    {
                        "carrier": str,
                        "annual": int,
                        "monthly": int,
                        "range_monthly": [int, int],
                        "range_annual": [int, int],
                        "confidence": str,
                        "explanations": [str, ...]
                    },
                    ...
                ]
            }
        """
        logger.info(
            f"Estimating quotes for {state} {zip_code}, age {age}, "
            f"{len(carriers)} carriers"
        )

        # 1. Get base rate for state
        base_annual = STATE_BASE_FULL_COVERAGE_ANNUAL.get(
            state,
            STATE_BASE_FULL_COVERAGE_ANNUAL["DEFAULT"]
        )
        logger.debug(f"Base annual rate for {state}: ${base_annual}")

        # 2. Calculate all demographic/vehicle factors
        age_mult, age_exp = calculate_age_factor(age)
        logger.debug(f"Age factor: {age_mult}x - {age_exp}")

        marital_mult, marital_exp = calculate_marital_factor(marital_status)
        logger.debug(f"Marital factor: {marital_mult}x - {marital_exp}")

        vehicle_mult, vehicle_exp = calculate_vehicle_factor(
            year=vehicle.get("year", 2020),
            make=vehicle.get("make", "Honda"),
            model=vehicle.get("model", "Civic"),
        )
        logger.debug(f"Vehicle factor: {vehicle_mult}x - {vehicle_exp}")

        zip_mult = get_zip_multiplier(zip_code)
        zip_desc = get_zip_description(zip_mult)
        zip_exp = f"ZIP {zip_code} - {zip_desc}"
        logger.debug(f"ZIP factor: {zip_mult}x - {zip_exp}")

        coverage_mult, coverage_exp = calculate_coverage_factor(coverage_type)
        logger.debug(f"Coverage factor: {coverage_mult}x - {coverage_exp}")

        # 3. Calculate baseline premium
        baseline_annual = (
            base_annual *
            age_mult *
            marital_mult *
            vehicle_mult *
            zip_mult *
            coverage_mult
        )
        baseline_monthly = baseline_annual / 12

        logger.info(
            f"Baseline estimate: ${baseline_annual:.0f}/year "
            f"(${baseline_monthly:.0f}/month)"
        )

        # 4. Calculate risk score for carrier multiplier interpolation
        risk_score = calculate_risk_score(
            age=age,
            marital_status=marital_status,
            vehicle_age=2026 - vehicle.get("year", 2020),
            zip_code=zip_code,
            coverage_type=coverage_type,
            accidents=optional_inputs.get("accidents", 0),
            tickets=optional_inputs.get("tickets", 0),
        )
        logger.debug(f"Risk score: {risk_score:.2f}")

        # 5. Assess data completeness for confidence bands
        band, confidence = assess_data_completeness({
            "age": age,
            "zip_code": zip_code,
            "vehicle": vehicle,
            "coverage_type": coverage_type,
            "marital_status": marital_status,
            **optional_inputs,
        })
        logger.info(f"Confidence: {confidence} (±{band*100:.0f}%)")

        # 6. Generate carrier-specific quotes
        quotes = []
        for carrier in carriers:
            carrier_annual, carrier_exp = self._estimate_carrier(
                carrier=carrier,
                baseline_annual=baseline_annual,
                risk_score=risk_score,
                state=state,
            )
            carrier_monthly = carrier_annual / 12

            # Calculate range
            range_low, range_high = calculate_range(
                carrier_monthly,
                band,
                state
            )

            quote = {
                "carrier": carrier,
                "annual": int(carrier_annual),
                "monthly": int(carrier_monthly),
                "range_monthly": [range_low, range_high],
                "range_annual": [range_low * 12, range_high * 12],
                "confidence": confidence,
                "explanations": [
                    age_exp,
                    marital_exp,
                    vehicle_exp,
                    zip_exp,
                    coverage_exp,
                    carrier_exp,
                ]
            }
            quotes.append(quote)

            logger.debug(
                f"{carrier}: ${carrier_monthly:.0f}/mo "
                f"(range: ${range_low}-${range_high})"
            )

        # Sort by monthly price (lowest first)
        quotes.sort(key=lambda q: q["monthly"])

        result = {
            "baseline": {
                "annual": int(baseline_annual),
                "monthly": int(baseline_monthly),
                "band": band,
                "confidence": confidence,
            },
            "quotes": quotes,
        }

        logger.info(
            f"Generated {len(quotes)} quotes, "
            f"range: ${quotes[0]['monthly']}-${quotes[-1]['monthly']}/mo"
        )

        return result

    def _estimate_carrier(
        self,
        carrier: str,
        baseline_annual: float,
        risk_score: float,
        state: str,
    ) -> tuple[float, str]:
        """
        Calculate carrier-specific estimate and explanation.

        Args:
            carrier: Carrier name
            baseline_annual: Baseline annual premium
            risk_score: Overall risk score (0.0 to 1.0)
            state: State abbreviation

        Returns:
            (carrier_annual, explanation)
        """
        # Get carrier multiplier range
        multiplier_range = CARRIER_BASE_MULTIPLIERS.get(
            carrier,
            (1.00, 1.15)  # Default for unknown carriers
        )
        low_mult, high_mult = multiplier_range

        # Interpolate based on risk score
        # Low risk (0.0) → use low multiplier
        # High risk (1.0) → use high multiplier
        carrier_mult = low_mult + (high_mult - low_mult) * risk_score

        # Apply state-specific adjustment if exists
        state_adj = CARRIER_STATE_ADJUSTMENTS.get(carrier, {}).get(state, 0.0)
        carrier_mult += state_adj

        if state_adj != 0.0:
            logger.debug(
                f"{carrier} state adjustment for {state}: {state_adj:+.2f}"
            )

        # Calculate final estimate
        carrier_annual = baseline_annual * carrier_mult

        # Generate explanation based on multiplier
        if carrier_mult < 0.95:
            explanation = CARRIER_PRICING_DESCRIPTIONS["competitive"].format(
                carrier=carrier
            )
        elif carrier_mult > 1.15:
            explanation = CARRIER_PRICING_DESCRIPTIONS["elevated"].format(
                carrier=carrier
            )
        else:
            explanation = CARRIER_PRICING_DESCRIPTIONS["standard"].format(
                carrier=carrier
            )

        return (carrier_annual, explanation)
