"""Tool handlers and business logic for insurance operations."""

import logging
import os
from typing import Any, Mapping

from pydantic import ValidationError

from .models import (
    InsuranceStateInput,
    ToolInvocationResult,
)
from .carrier_logos import get_carrier_logo
from .utils import (
    _extract_request_id,
    _lookup_city_state_from_zip,
    state_abbreviation,
)

logger = logging.getLogger(__name__)


def _insurance_state_tool_handler(
    arguments: Mapping[str, Any], widget_id: str, widget_meta: dict, widget_resource: dict
) -> ToolInvocationResult:
    """Handle insurance state selector tool invocation."""
    request_id = _extract_request_id(arguments) or "<unknown>"

    try:
        InsuranceStateInput.model_validate(arguments)
    except ValidationError as error:
        logger.info(
            "Insurance state widget validation failed for %s (request_id=%s): %s",
            widget_id,
            request_id,
            error.errors(),
        )
        raise

    logger.debug(
        "Insurance state widget returning selector for %s (request_id=%s)",
        widget_id,
        request_id,
    )
    return {
        "structured_content": {},
        "meta": {
            **widget_meta,
            "openai.com/widget": widget_resource,
        },
    }


async def _get_enhanced_quick_quote(arguments: Mapping[str, Any]) -> ToolInvocationResult:
    """Get an enhanced quick quote with detailed driver and vehicle information.

    Returns more accurate rate estimates based on provided driver age, vehicle details,
    coverage type, and optional additional driver information.
    """
    from .utils import _lookup_city_state_from_zip
    from .quick_quote_ranges import calculate_enhanced_quote_range
    from .models import EnhancedQuickQuoteIntake

    payload = EnhancedQuickQuoteIntake.model_validate(arguments)

    logger.info(f"Enhanced quick quote request: zip={payload.zip_code}, age={payload.primary_driver_age}, marital={payload.primary_driver_marital_status}, coverage={payload.coverage_type}")

    # Look up city and state from zip code
    city_state = _lookup_city_state_from_zip(payload.zip_code)

    # If lookup fails, treat as phone-only fallback (don't error out)
    if not city_state:
        logger.warning(f"Failed to resolve location for zip {payload.zip_code} - treating as phone-only fallback")
        city = None
        state = None
        lookup_failed = True
    else:
        city, state = city_state
        lookup_failed = False
        logger.info(f"Resolved location: {city}, {state}")

    # Count drivers and vehicles
    num_drivers = 2 if payload.additional_driver else 1
    num_vehicles = 2 if payload.vehicle_2 else 1

    if not lookup_failed:
        logger.info(f"Enhanced quick quote: {num_drivers} drivers, {num_vehicles} vehicles in {city}, {state}")

    # Skip quote calculation if lookup failed - we'll show phone-only prompt
    if lookup_failed:
        carriers = []
        message = f"I can help you get a quote for zip code {payload.zip_code}. Please call us for a personalized quote."
    else:
        # Calculate enhanced ranges based on provided details
        best_min, best_max, worst_min, worst_max = calculate_enhanced_quote_range(
            zip_code=payload.zip_code,
            city=city,
            state=state,
            primary_driver_age=payload.primary_driver_age,
            primary_driver_marital_status=payload.primary_driver_marital_status,
            vehicle_1_year=payload.vehicle_1.year,
            coverage_type=payload.coverage_type,
            num_drivers=num_drivers,
            num_vehicles=num_vehicles,
            additional_driver_age=payload.additional_driver.age if payload.additional_driver else None,
            additional_driver_marital_status=payload.additional_driver.marital_status if payload.additional_driver else None,
        )

        # Build message
        message = "Perfect! I've generated your insurance quote estimates.\n\n"
        message += "**Your Profile:**\n"
        message += f"📍 Location: {city}, {state} {payload.zip_code}\n"
        message += f"🚗 Vehicle: {payload.vehicle_1.year} {payload.vehicle_1.make} {payload.vehicle_1.model}\n"
        if payload.vehicle_2:
            message += f"🚗 Vehicle 2: {payload.vehicle_2.year} {payload.vehicle_2.make} {payload.vehicle_2.model}\n"
        message += f"🛡️ Coverage: {'Full Coverage (Liability + Comp/Coll)' if payload.coverage_type == 'full_coverage' else 'Liability Only'}\n"
        message += f"👤 Primary Driver: Age {payload.primary_driver_age}, {payload.primary_driver_marital_status.title()}\n"
        if payload.additional_driver:
            message += f"👥 Additional Driver: Age {payload.additional_driver.age}, {payload.additional_driver.marital_status.title()}\n"
        message += "\n\n**Your estimated quotes from 3 carriers are displayed above.**\n\n"
        message += "These are estimates based on your information. Click 'Continue to Personalized Quote' to get a final rate."

        import mcp.types as types
        from .widget_registry import WIDGETS_BY_ID, QUICK_QUOTE_RESULTS_WIDGET_IDENTIFIER, _embedded_widget_resource, _tool_meta
        from .carrier_mapping import get_carriers_for_state

        # Get server base URL from environment
        server_base_url = os.getenv("SERVER_BASE_URL", "http://localhost:8000")

        # Get state-specific carriers
        logger.info("=== CARRIER SELECTION DEBUG ===")
        logger.info(f"Raw state from Google API: '{state}'")
        from .carrier_mapping import normalize_state
        normalized = normalize_state(state)
        logger.info(f"Normalized state: '{normalized}'")
        carrier_names = get_carriers_for_state(state)
        logger.info(f"Carriers for {state}: {carrier_names}")
        logger.info("=== END CARRIER DEBUG ===")

        # Generate carrier estimates using the estimation engine
        from .pricing import InsuranceQuoteEstimator

        estimator = InsuranceQuoteEstimator()

        # Prepare vehicle dict
        vehicle_dict = {
            "year": payload.vehicle_1.year,
            "make": payload.vehicle_1.make,
            "model": payload.vehicle_1.model,
        }

        # Determine coverage type
        coverage_type = "full" if payload.coverage_type == "full_coverage" else "liability"

        # Generate estimates
        try:
            estimates = estimator.estimate_quotes(
                state=normalized or "CA",
                zip_code=payload.zip_code,
                age=payload.primary_driver_age,
                marital_status=payload.primary_driver_marital_status,
                vehicle=vehicle_dict,
                coverage_type=coverage_type,
                carriers=carrier_names,
            )

            # Log detailed calculation breakdown to file
            from .quote_logger import log_quick_quote_calculation
            from .pricing.risk_score import calculate_risk_score

            risk_score = calculate_risk_score(
                age=payload.primary_driver_age,
                marital_status=payload.primary_driver_marital_status,
                vehicle_age=2026 - vehicle_dict["year"],
                zip_code=payload.zip_code,
                coverage_type=coverage_type,
                accidents=0,
                tickets=0,
            )

            try:
                explanation_file = log_quick_quote_calculation(
                    state=normalized or "CA",
                    zip_code=payload.zip_code,
                    age=payload.primary_driver_age,
                    marital_status=payload.primary_driver_marital_status,
                    vehicle=vehicle_dict,
                    coverage_type=coverage_type,
                    baseline=estimates["baseline"],
                    quotes=estimates["quotes"],
                    risk_score=risk_score,
                )
                logger.info(f"Quote calculation breakdown saved to: {explanation_file}")
            except Exception as log_error:
                logger.warning(f"Failed to write quote explanation: {log_error}")

            # Format for widget
            carriers = []
            for quote in estimates["quotes"]:
                carriers.append({
                    "name": quote["carrier"],
                    "logo": get_carrier_logo(quote["carrier"]),
                    "annual_cost": quote["annual"],
                    "monthly_cost": quote["monthly"],
                    "range_monthly_low": quote["range_monthly"][0],
                    "range_monthly_high": quote["range_monthly"][1],
                    "range_annual_low": quote["range_annual"][0],
                    "range_annual_high": quote["range_annual"][1],
                    "confidence": quote["confidence"],
                    "explanations": quote["explanations"],
                })

            logger.info(f"Generated {len(carriers)} carrier estimates using estimation engine")
            for carrier in carriers:
                logger.info(
                    f"  {carrier['name']}: ${carrier['monthly_cost']}/mo "
                    f"(${carrier['range_monthly_low']}-${carrier['range_monthly_high']})"
                )

        except Exception as e:
            logger.error(f"Error generating estimates: {e}", exc_info=True)
            # Fallback to simple estimates
            carriers = []
            base_annual = (best_min + best_max + worst_min + worst_max) // 4

            for i, carrier_name in enumerate(carrier_names):
                if i == 0:
                    annual_cost = int(base_annual * 0.90)
                elif i == 1:
                    annual_cost = base_annual
                else:
                    annual_cost = int(base_annual * 1.10)

                monthly_cost = annual_cost // 12

                carriers.append({
                    "name": carrier_name,
                    "logo": get_carrier_logo(carrier_name),
                    "annual_cost": annual_cost,
                    "monthly_cost": monthly_cost,
                    "range_low": int(monthly_cost * 0.70),
                    "range_high": int(monthly_cost * 1.30),
                    "confidence": "low",
                    "explanations": ["Limited information - estimates may vary significantly"],
                })
            logger.warning("Using fallback estimates due to error")

    # (End of if/else block - common code for both paths follows)
    import mcp.types as types
    from .widget_registry import WIDGETS_BY_ID, QUICK_QUOTE_RESULTS_WIDGET_IDENTIFIER, _embedded_widget_resource, _tool_meta

    # Get server base URL from environment
    server_base_url = os.getenv("SERVER_BASE_URL", "http://localhost:8000")

    # Get widget metadata
    quick_quote_widget = WIDGETS_BY_ID[QUICK_QUOTE_RESULTS_WIDGET_IDENTIFIER]
    widget_resource = _embedded_widget_resource(quick_quote_widget)
    widget_meta = {
        **_tool_meta(quick_quote_widget),
        "openai.com/widget": widget_resource.model_dump(mode="json"),
    }

    # Normalize state to abbreviation for consistent frontend handling
    state_abbr = state_abbreviation(state) if state else None

    # Build structured content
    structured_content = {
        "zip_code": payload.zip_code,
        "city": city,
        "state": state_abbr,  # Use abbreviation for consistent phone-only state detection
        "primary_driver_age": payload.primary_driver_age,
        "num_drivers": num_drivers,
        "num_vehicles": num_vehicles,
        "server_url": server_base_url,
        "carriers": carriers,
        "mercury_logo": get_carrier_logo("Mercury Auto Insurance"),  # Always show Mercury in header
        "stage": "quick_quote_complete",
        "lookup_failed": lookup_failed,  # Flag to indicate failed zip lookup
    }

    logger.info("=== RETURNING STRUCTURED CONTENT ===")
    if lookup_failed:
        logger.info(f"Lookup failed for zip {payload.zip_code} - showing phone-only prompt")
    else:
        logger.info(f"City: {city}, State: {state_abbr} (original: {state})")
    logger.info(f"Number of carriers in response: {len(carriers)}")
    for i, carrier in enumerate(carriers):
        logger.info(f"  Carrier {i+1}: {carrier['name']} - ${carrier['annual_cost']}/year")
    logger.info("=== END STRUCTURED CONTENT ===")

    # Return the widget with carrier data
    return {
        "structured_content": structured_content,
        "content": [types.TextContent(type="text", text=message)],
        "meta": widget_meta,
    }



async def _submit_carrier_estimates(arguments: Mapping[str, Any]) -> ToolInvocationResult:
    """Accept ChatGPT-generated carrier estimates and render the final quote widget."""
    from .models import CarrierEstimatesSubmission
    import mcp.types as types

    payload = CarrierEstimatesSubmission.model_validate(arguments)

    # Get location info from zip code
    city_state = _lookup_city_state_from_zip(payload.zip_code)
    if not city_state:
        return {
            "response_text": f"Unable to find location information for zip code {payload.zip_code}.",
        }
    city, state = city_state

    # Add logo to each carrier
    carriers_with_logos = [
        {
            "name": carrier.name,
            "logo": get_carrier_logo(carrier.name),
            "annual_cost": carrier.annual_cost,
            "monthly_cost": carrier.monthly_cost,
            "notes": carrier.notes
        }
        for carrier in payload.carriers
    ]

    # If no carriers provided or too few, use hard-coded defaults
    if len(carriers_with_logos) < 3:
        logger.info("Using hard-coded carrier data (provided carriers: %d)", len(carriers_with_logos))
        carriers_with_logos = [
            {
                "name": "Geico",
                "logo": get_carrier_logo("Geico"),
                "annual_cost": 3100,
                "monthly_cost": 258,
                "notes": "Widely available nationwide"
            },
            {
                "name": "Progressive Insurance",
                "logo": get_carrier_logo("Progressive Insurance"),
                "annual_cost": 3600,
                "monthly_cost": 300,
                "notes": "Best balance of cost & claims service"
            },
            {
                "name": "Safeco Insurance",
                "logo": get_carrier_logo("Safeco Insurance"),
                "annual_cost": 3800,
                "monthly_cost": 317,
                "notes": "Strong coverage options"
            },
        ]

    # Build success message
    message = (
        f"Perfect! I've compiled insurance quotes from {len(carriers_with_logos)} carriers "
        f"for your profile in {city}, {state}. Here are your estimated rates:"
    )

    return {
        "structured_content": {
            "zip_code": payload.zip_code,
            "city": city,
            "state": state,
            "primary_driver_age": payload.primary_driver_age,
            "carriers": carriers_with_logos,
            "mercury_logo": get_carrier_logo("Mercury Auto Insurance"),  # Always show Mercury in header
            "stage": "carrier_estimates_complete",
        },
        "content": [types.TextContent(type="text", text=message)],
    }
