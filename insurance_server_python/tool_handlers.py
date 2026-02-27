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
    import uuid
    from .utils import _lookup_city_state_from_zip
    from .quick_quote_ranges import calculate_enhanced_quote_range
    from .models import QuickQuoteIntake
    from .duplicate_detection import is_duplicate_call, get_duplicate_info
    from .structured_logging import (
        log_tool_call,
        log_duplicate_call,
        log_quote_request,
        log_batch_incomplete,
        log_phone_only_state,
        log_quote_generated,
        log_carrier_estimation,
    )
    import mcp.types as types

    # Generate unique call ID for tracking this invocation
    call_id = str(uuid.uuid4())[:8]
    logger.info("🎯 CALL START [%s] ========================================", call_id)
    logger.info("Tool: get-enhanced-quick-quote")
    logger.info("Call ID: %s", call_id)
    logger.info("Arguments: %s", arguments)

    # Check for duplicate calls
    if is_duplicate_call("get-enhanced-quick-quote", dict(arguments)):
        dup_info = get_duplicate_info("get-enhanced-quick-quote", dict(arguments))
        seconds_ago = int(dup_info["seconds_ago"]) if dup_info else 0

        logger.warning(
            f"🔄 DUPLICATE CALL DETECTED - Same quote request was made {seconds_ago} seconds ago. "
            f"Rejecting to prevent repeated widget generation."
        )

        # Log duplicate call event
        log_duplicate_call(
            tool_name="get-enhanced-quick-quote",
            seconds_since_last=seconds_ago,
        )

        return {
            "content": [types.TextContent(
                type="text",
                text=(
                    f"⚠️ I already generated this quote {seconds_ago} seconds ago. "
                    f"The quote widget should be displayed above. "
                    f"If you need a different quote, please provide different information (different ZIP code, vehicles, drivers, etc.)."
                )
            )],
            "structured_content": {},
        }

    payload = QuickQuoteIntake.model_validate(arguments)

    # DETAILED LOGGING: Log exactly what fields were provided
    logger.info("=" * 80)
    logger.info("QUICK QUOTE TOOL INVOKED")
    logger.info("=" * 80)
    logger.info(f"Raw arguments received: {arguments}")
    logger.info(f"Parsed payload fields:")
    logger.info(f"  - zip_code: {payload.zip_code}")
    logger.info(f"  - num_vehicles: {payload.num_vehicles}")
    logger.info(f"  - vehicles: {payload.vehicles}")
    logger.info(f"  - coverage_preference: {payload.coverage_preference}")
    logger.info(f"  - num_drivers: {payload.num_drivers}")
    logger.info(f"  - drivers: {payload.drivers}")
    logger.info("=" * 80)

    # Structured logging: Log quote request
    log_quote_request(
        zip_code=payload.zip_code,
        num_vehicles=payload.num_vehicles,
        num_drivers=payload.num_drivers,
        coverage_preference=payload.coverage_preference,
    )

    # Log tool call
    has_all = (
        payload.num_vehicles is not None and
        payload.vehicles and
        payload.coverage_preference is not None and
        payload.num_drivers is not None and
        payload.drivers
    )
    log_tool_call(
        tool_name="get-enhanced-quick-quote",
        has_all_fields=has_all,
        zip_code=payload.zip_code,
    )

    # ⛔ STRICT VALIDATION: ALL FIELDS REQUIRED - NO PARTIAL CALLS ALLOWED ⛔
    # This tool should ONLY be called after the assistant has collected ALL information
    # from BOTH batches. No early validation, no partial calls.

    import mcp.types as types

    missing_fields = []

    # Check ALL required fields
    if payload.num_vehicles is None:
        missing_fields.append("Number of vehicles")
    if payload.vehicles is None or len(payload.vehicles) == 0:
        missing_fields.append("Vehicle details (year, make, model)")
    if payload.coverage_preference is None:
        missing_fields.append("Coverage preference")
    if payload.num_drivers is None:
        missing_fields.append("Number of drivers")
    if payload.drivers is None or len(payload.drivers) == 0:
        missing_fields.append("Driver details (age, marital status)")

    # If ANY field is missing, reject the call with clear guidance
    if missing_fields:
        logger.error(f"❌ TOOL CALLED TOO EARLY - Missing fields: {', '.join(missing_fields)}")

        # Determine which batch is incomplete
        batch1_fields = ["Number of vehicles", "Vehicle details (year, make, model)", "Coverage preference"]
        batch2_fields = ["Number of drivers", "Driver details (age, marital status)"]

        batch1_missing = [f for f in missing_fields if f in batch1_fields]
        batch2_missing = [f for f in missing_fields if f in batch2_fields]

        if batch1_missing:
            log_batch_incomplete(
                batch_name="batch_1",
                missing_fields=batch1_missing,
                zip_code=payload.zip_code,
            )
        if batch2_missing:
            log_batch_incomplete(
                batch_name="batch_2",
                missing_fields=batch2_missing,
                zip_code=payload.zip_code,
            )

        error_message = (
            "⚠️ This tool requires ALL information from both batches before being called.\n\n"
            "**Missing information:**\n"
            + "\n".join(f"• {field}" for field in missing_fields) +
            "\n\n**Instructions:**\n"
            "1. First, collect: ZIP code, number of vehicles, vehicle details, and coverage preference\n"
            "2. Then, collect: number of drivers and driver details (age, marital status)\n"
            "3. Only after collecting ALL information, call this tool\n\n"
            "Please collect the missing information before calling this tool again."
        )
        return {
            "content": [types.TextContent(type="text", text=error_message)],
            "structured_content": {},
        }

    # ✅ ALL FIELDS PRESENT - Proceed with quote generation
    logger.info("✅ ALL FIELDS PRESENT - Proceeding with quote generation")

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

    # Check if this is a phone-only state (AK, HI, MA)
    PHONE_ONLY_STATES = ["AK", "HI", "MA", "Alaska", "Hawaii", "Massachusetts"]
    is_phone_only = (state and state in PHONE_ONLY_STATES) or lookup_failed

    # If phone-only state, show phone widget instead of quote
    if is_phone_only:
        logger.info(f"Phone-only state detected: {state or 'unknown'} - showing phone widget")

        # Log phone-only state event
        log_phone_only_state(
            zip_code=payload.zip_code,
            state=state or "unknown",
            lookup_failed=lookup_failed,
        )

        from .widget_registry import WIDGETS_BY_ID, PHONE_ONLY_WIDGET_IDENTIFIER, _embedded_widget_resource

        # Get phone-only widget metadata
        phone_only_widget = WIDGETS_BY_ID[PHONE_ONLY_WIDGET_IDENTIFIER]
        widget_resource = _embedded_widget_resource(phone_only_widget)

        # Build metadata - don't include openai/outputTemplate since we're embedding the widget
        # Including both causes ChatGPT to render the widget twice
        widget_meta = {
            "openai/toolInvocation/invoking": phone_only_widget.invoking,
            "openai/toolInvocation/invoked": phone_only_widget.invoked,
            "openai/widgetAccessible": True,
            "openai/resultCanProduceWidget": True,
            "annotations": {
                "destructiveHint": False,
                "openWorldHint": False,
                "readOnlyHint": True,
            },
            "openai.com/widget": widget_resource.model_dump(mode="json"),
        }

        # Normalize state to abbreviation
        state_abbr = state_abbreviation(state) if state else None

        # Get CTA URL configuration
        from .url_config import get_cta_params_json
        cta_config = get_cta_params_json()

        # Create concise message directing them to call
        if lookup_failed:
            message = f"Thanks! I've submitted your details for a quote. Please call the number above to complete your quote with a licensed agent.\n\nLet me know if you have any questions!"
        else:
            message = f"Thanks! I've submitted your details for a quote in {city}, {state}. Please call the number above to get your personalized quote from a licensed agent.\n\nLet me know if you have any questions!"

        # Return phone-only widget
        return {
            "structured_content": {
                "success": True,  # Clear success indicator
                "phone_only": True,  # Explicit flag for phone-only state
                "zip_code": payload.zip_code,
                "city": city,
                "state": state_abbr,
                "lookup_failed": lookup_failed,
                "cta_config": cta_config,  # CTA URL configuration
            },
            "content": [types.TextContent(type="text", text=message)],
            "meta": widget_meta,
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
        message += "These are estimates based on your information. Click 'Get personalized quote' on any carrier above to get a final rate and complete your purchase.\n\n"
        message += "Let me know if you have any questions!"

        import mcp.types as types
        from .widget_registry import WIDGETS_BY_ID, QUICK_QUOTE_RESULTS_WIDGET_IDENTIFIER, _embedded_widget_resource
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

            # Log carrier estimation
            log_carrier_estimation(
                zip_code=payload.zip_code,
                state=normalized or "CA",
                num_carriers=len(estimates["quotes"]),
                baseline_annual=estimates["baseline"]["annual"],
                confidence=estimates["quotes"][0]["confidence"] if estimates["quotes"] else "unknown",
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
    from .widget_registry import WIDGETS_BY_ID, QUICK_QUOTE_RESULTS_WIDGET_IDENTIFIER, _embedded_widget_resource

    # Get server base URL from environment
    server_base_url = os.getenv("SERVER_BASE_URL", "http://localhost:8000")

    # Get widget metadata
    quick_quote_widget = WIDGETS_BY_ID[QUICK_QUOTE_RESULTS_WIDGET_IDENTIFIER]
    widget_resource = _embedded_widget_resource(quick_quote_widget)

    # Build metadata - don't include openai/outputTemplate since we're embedding the widget
    # Including both causes ChatGPT to render the widget twice
    widget_meta = {
        "openai/toolInvocation/invoking": quick_quote_widget.invoking,
        "openai/toolInvocation/invoked": quick_quote_widget.invoked,
        "openai/widgetAccessible": True,
        "openai/resultCanProduceWidget": True,
        "annotations": {
            "destructiveHint": False,
            "openWorldHint": False,
            "readOnlyHint": True,
        },
        "openai.com/widget": widget_resource.model_dump(mode="json"),
    }

    # Normalize state to abbreviation for consistent frontend handling
    state_abbr = state_abbreviation(state) if state else None

    # Get CTA URL configuration
    from .url_config import get_cta_params_json
    cta_config = get_cta_params_json()

    # Build structured content
    structured_content = {
        "success": True,  # Clear success indicator
        "quote_generated": True,  # Explicit flag that quote was generated
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
        "cta_config": cta_config,  # CTA URL configuration for building personalized links
    }

    logger.info("=== RETURNING STRUCTURED CONTENT [%s] ===", call_id)
    if lookup_failed:
        logger.info(f"Lookup failed for zip {payload.zip_code} - showing phone-only prompt")
    else:
        logger.info(f"City: {city}, State: {state_abbr} (original: {state})")
    logger.info(f"Number of carriers in response: {len(carriers)}")
    for i, carrier in enumerate(carriers):
        logger.info(f"  Carrier {i+1}: {carrier['name']} - ${carrier['annual_cost']}/year")
    logger.info("=== END STRUCTURED CONTENT ===")

    # Log successful quote generation
    log_quote_generated(
        zip_code=payload.zip_code,
        state=state_abbr,
        num_carriers=len(carriers),
        num_vehicles=num_vehicles,
        num_drivers=num_drivers,
        coverage_type=payload.coverage_preference,
        city=city,
        lookup_failed=lookup_failed,
    )

    # Build the response
    response = {
        "structured_content": structured_content,
        "content": [types.TextContent(type="text", text=message)],
        "meta": widget_meta,
    }

    # DETAILED RESPONSE INSPECTION
    logger.info("╔" + "═" * 78 + "╗")
    logger.info("║ 📤 RESPONSE INSPECTION [%s]", call_id.ljust(65) + "║")
    logger.info("╠" + "═" * 78 + "╣")

    # Content inspection
    logger.info("║ Content Array:")
    logger.info("║   - Length: %d", len(response["content"]))
    for idx, content_item in enumerate(response["content"]):
        logger.info("║   - Item %d: type=%s", idx, content_item.type)
        if hasattr(content_item, 'text'):
            text_preview = content_item.text[:100].replace('\n', ' ') if content_item.text else "None"
            logger.info("║     Text preview: %s...", text_preview)

    # Structured content inspection
    logger.info("║")
    logger.info("║ Structured Content:")
    logger.info("║   - Keys: %s", list(structured_content.keys()))
    logger.info("║   - success: %s", structured_content.get('success'))
    logger.info("║   - quote_generated: %s", structured_content.get('quote_generated'))
    logger.info("║   - stage: %s", structured_content.get('stage'))
    logger.info("║   - Number of carriers: %d", len(structured_content.get('carriers', [])))

    # Carrier details
    if structured_content.get('carriers'):
        logger.info("║   - Carrier details:")
        for i, carrier in enumerate(structured_content['carriers']):
            logger.info("║     [%d] %s: $%d/year ($%d/month)",
                       i+1, carrier.get('name'), carrier.get('annual_cost', 0), carrier.get('monthly_cost', 0))

    # Meta inspection
    logger.info("║")
    logger.info("║ Meta:")
    logger.info("║   - Keys: %s", list(widget_meta.keys()))
    if "openai/outputTemplate" in widget_meta:
        template = widget_meta["openai/outputTemplate"]
        if isinstance(template, dict):
            logger.info("║   - outputTemplate type: %s", template.get('type'))
            logger.info("║   - outputTemplate uri: %s", template.get('uri'))
        else:
            logger.info("║   - outputTemplate: %s", template)
    if "openai.com/widget" in widget_meta:
        widget_info = widget_meta["openai.com/widget"]
        if isinstance(widget_info, dict):
            logger.info("║   - widget type: %s", widget_info.get('type'))
            logger.info("║   - widget embedded: %s", 'embedded' in widget_info)
        else:
            logger.info("║   - widget: %s", widget_info)

    logger.info("╚" + "═" * 78 + "╝")
    logger.info("🏁 CALL END [%s] ==========================================", call_id)

    # Return the widget with carrier data
    return response



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

    # Get CTA URL configuration
    from .url_config import get_cta_params_json
    cta_config = get_cta_params_json()

    return {
        "structured_content": {
            "zip_code": payload.zip_code,
            "city": city,
            "state": state,
            "primary_driver_age": payload.primary_driver_age,
            "carriers": carriers_with_logos,
            "mercury_logo": get_carrier_logo("Mercury Auto Insurance"),  # Always show Mercury in header
            "stage": "carrier_estimates_complete",
            "cta_config": cta_config,  # CTA URL configuration
        },
        "content": [types.TextContent(type="text", text=message)],
    }
