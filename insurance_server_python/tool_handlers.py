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
    from .models import QuickQuoteIntake

    payload = QuickQuoteIntake.model_validate(arguments)

    logger.info(f"Quick quote request: zip={payload.zip_code}, drivers={payload.num_drivers}, vehicles={payload.num_vehicles}, coverage={payload.coverage_preference}")

    # EARLY VALIDATION: Check if we only have zip_code
    # This allows us to validate the location and show phone widget immediately if needed
    has_only_zip = (
        payload.num_vehicles is None and
        payload.vehicles is None and
        payload.coverage_preference is None and
        payload.num_drivers is None and
        payload.drivers is None
    )

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

    # EARLY PHONE-ONLY STATE DETECTION
    # If user only provided zip code and it's phone-only or lookup failed, return phone widget immediately
    phone_only_states = ["AK", "HI", "MA", "Alaska", "Hawaii", "Massachusetts"]
    is_phone_only = (state and state in phone_only_states) or lookup_failed

    if has_only_zip and is_phone_only:
        logger.info(f"Early validation: {state or 'unknown'} is phone-only or lookup failed - showing phone widget without asking for more info")

        import mcp.types as types
        from .widget_registry import WIDGETS_BY_ID, QUICK_QUOTE_RESULTS_WIDGET_IDENTIFIER, _embedded_widget_resource, _tool_meta

        # Get widget metadata
        quick_quote_widget = WIDGETS_BY_ID[QUICK_QUOTE_RESULTS_WIDGET_IDENTIFIER]
        widget_resource = _embedded_widget_resource(quick_quote_widget)
        widget_meta = {
            **_tool_meta(quick_quote_widget),
            "openai.com/widget": widget_resource.model_dump(mode="json"),
        }

        # Normalize state to abbreviation
        state_abbr = state_abbreviation(state) if state else None

        # Create message
        if lookup_failed:
            message = f"I'd be happy to help you get a quote for zip code {payload.zip_code}. Please give us a call to speak with a licensed agent who can provide personalized quotes and help you find the best coverage."
        else:
            message = f"I'd be happy to help you get a quote in {city}, {state}. Since we require a call for quotes in {state}, please contact us to speak with a licensed agent who specializes in {state} insurance and can provide personalized quotes."

        # Return phone widget immediately
        return {
            "structured_content": {
                "zip_code": payload.zip_code,
                "city": city,
                "state": state_abbr,
                "num_drivers": 1,
                "num_vehicles": 1,
                "carriers": [],  # Empty for phone-only
                "mercury_logo": get_carrier_logo("Mercury Auto Insurance"),
                "stage": "quick_quote_complete",
                "lookup_failed": lookup_failed,
            },
            "content": [types.TextContent(type="text", text=message)],
            "meta": widget_meta,
        }

    # VALIDATION: Check if we have all required fields to generate a quote
    # If not, we should not proceed (this should not happen if assistant follows instructions)
    missing_fields = []
    if payload.num_vehicles is None:
        missing_fields.append("number of vehicles")
    if payload.vehicles is None or len(payload.vehicles) == 0:
        missing_fields.append("vehicle information")
    if payload.coverage_preference is None:
        missing_fields.append("coverage preference")
    if payload.num_drivers is None:
        missing_fields.append("number of drivers")
    if payload.drivers is None or len(payload.drivers) == 0:
        missing_fields.append("driver information")

    if missing_fields:
        logger.warning(f"Incomplete quote request - missing: {', '.join(missing_fields)}")
        import mcp.types as types
        error_message = (
            f"I need more information to generate your quote. Please provide:\n"
            f"{'• ' + chr(10) + '• '.join(missing_fields)}"
        )
        return {
            "content": [types.TextContent(type="text", text=error_message)],
            "structured_content": {},
        }

    # Get counts from payload
    num_drivers = payload.num_drivers
    num_vehicles = payload.num_vehicles

    if not lookup_failed:
        logger.info(f"Quick quote: {num_drivers} drivers, {num_vehicles} vehicles in {city}, {state}")

    # Skip quote calculation if lookup failed - we'll show phone-only prompt
    if lookup_failed:
        carriers = []
        message = f"I can help you get a quote for zip code {payload.zip_code}. Please call us for a personalized quote.\n\n"
        message += "Our licensed agents can provide personalized quotes and answer any questions you have about coverage options, deductibles, and discounts."
    else:
        # Get primary driver and vehicle info
        primary_driver = payload.drivers[0]
        primary_vehicle = payload.vehicles[0]

        # Get additional driver info if present
        additional_driver_age = payload.drivers[1].age if len(payload.drivers) > 1 else None
        additional_driver_marital = payload.drivers[1].marital_status if len(payload.drivers) > 1 else None

        # Normalize coverage type (convert liability_only/full_coverage to old format)
        coverage_type = "full_coverage" if payload.coverage_preference == "full_coverage" else "liability"

        # Calculate enhanced ranges based on provided details
        best_min, best_max, worst_min, worst_max = calculate_enhanced_quote_range(
            zip_code=payload.zip_code,
            city=city,
            state=state,
            primary_driver_age=primary_driver.age,
            primary_driver_marital_status=primary_driver.marital_status,
            vehicle_1_year=primary_vehicle.year,
            coverage_type=coverage_type,
            num_drivers=num_drivers,
            num_vehicles=num_vehicles,
            additional_driver_age=additional_driver_age,
            additional_driver_marital_status=additional_driver_marital,
        )

        # Build message
        message = "Perfect! I've generated your insurance quote estimates.\n\n"
        message += "**Your Profile:**\n"
        message += f"📍 Location: {city}, {state} {payload.zip_code}\n"

        # List vehicles
        for idx, vehicle in enumerate(payload.vehicles, 1):
            vehicle_label = "Vehicle" if idx == 1 else f"Vehicle {idx}"
            message += f"🚗 {vehicle_label}: {vehicle.year} {vehicle.make} {vehicle.model}\n"

        # Coverage
        coverage_display = 'Full Coverage (Liability + Comp/Coll)' if payload.coverage_preference == 'full_coverage' else 'Liability Only'
        message += f"🛡️ Coverage: {coverage_display}\n"

        # List drivers
        for idx, driver in enumerate(payload.drivers, 1):
            driver_label = "Primary Driver" if idx == 1 else f"Driver {idx}"
            message += f"👤 {driver_label}: Age {driver.age}, {driver.marital_status.title()}\n"

        message += "\n\n**Your estimated quotes from 3 carriers are displayed above.**\n\n"
        message += "These are estimates based on your information. Click 'Get personalized quote' to get a final rate.\n\n"
        message += "You can review the carrier options, compare pricing, and select the one that fits your needs best. If you'd like help understanding the differences between coverage or adjusting deductibles to lower your premium, just let me know!"

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

        # Prepare vehicle dict using primary vehicle
        vehicle_dict = {
            "year": primary_vehicle.year,
            "make": primary_vehicle.make,
            "model": primary_vehicle.model,
        }

        # Determine coverage type for estimation engine
        coverage_type_for_engine = "full" if payload.coverage_preference == "full_coverage" else "liability"

        # Generate estimates
        try:
            estimates = estimator.estimate_quotes(
                state=normalized or "CA",
                zip_code=payload.zip_code,
                age=primary_driver.age,
                marital_status=primary_driver.marital_status,
                vehicle=vehicle_dict,
                coverage_type=coverage_type_for_engine,
                carriers=carrier_names,
            )

            # Log detailed calculation breakdown to file
            from .quote_logger import log_quick_quote_calculation
            from .pricing.risk_score import calculate_risk_score

            risk_score = calculate_risk_score(
                age=primary_driver.age,
                marital_status=primary_driver.marital_status,
                vehicle_age=2026 - vehicle_dict["year"],
                zip_code=payload.zip_code,
                coverage_type=coverage_type_for_engine,
                accidents=0,
                tickets=0,
            )

            try:
                explanation_file = log_quick_quote_calculation(
                    state=normalized or "CA",
                    zip_code=payload.zip_code,
                    age=primary_driver.age,
                    marital_status=primary_driver.marital_status,
                    vehicle=vehicle_dict,
                    coverage_type=coverage_type_for_engine,
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
        "primary_driver_age": payload.drivers[0].age if payload.drivers else None,
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
        f"for your profile in {city}, {state}. Here are your estimated rates:\n\n"
        f"You can review the carrier options, compare pricing, and select the one that fits your needs best. "
        f"If you'd like help understanding the differences between coverage or adjusting deductibles to lower your premium, just let me know!"
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
