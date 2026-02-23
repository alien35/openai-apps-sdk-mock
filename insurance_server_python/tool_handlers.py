"""Tool handlers and business logic for insurance operations."""

import json
import logging
import os
from pathlib import Path
from typing import Any, Mapping, Optional
import httpx
from pydantic import ValidationError
from datetime import datetime, timedelta

from .models import (
    InsuranceStateInput,
    PersonalAutoCustomerIntake,
    PersonalAutoDriverRosterInput,
    PersonalAutoDriverIntake,
    PersonalAutoVehicleIntake,
    PersonalAutoRateRequest,
    PersonalAutoRateResultsRequest,
    QuickQuoteIntake,
    ToolInvocationResult,
)
from .constants import (
    PERSONAL_AUTO_RATE_ENDPOINT,
    PERSONAL_AUTO_RATE_RESULTS_ENDPOINT,
    DEFAULT_CARRIER_INFORMATION,
)
from .carrier_logos import get_carrier_logo
from .utils import (
    _extract_request_id,
    _sanitize_personal_auto_rate_request,
    _log_network_request,
    _log_network_response,
    state_abbreviation,
    format_rate_results_summary,
    _lookup_city_state_from_zip,
)
from .carrier_logos import get_carrier_logo

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


# ═══════════════════════════════════════════════════════════════
# Session storage for collection engines (in-memory for POC)
# In production, use Redis or database
# ═══════════════════════════════════════════════════════════════
_session_engines = {}


async def _get_quick_quote_adaptive(arguments: Mapping[str, Any]) -> ToolInvocationResult:
    """Adaptive quick quote using collection engine.

    This handler uses the adaptive architecture to collect fields in any order
    based on the active flow configuration.
    """
    from .collection_engine import create_collection_engine, CollectionStatus
    from .flow_configs import FlowType
    from .field_defaults import build_minimal_payload_with_defaults

    # Extract session ID (from metadata or generate)
    session_id = arguments.get("session_id", "default_session")

    # Get or create collection engine
    if session_id not in _session_engines:
        engine = create_collection_engine(FlowType.QUICK_QUOTE)
        if not engine:
            return {
                "response_text": "Unable to start quick quote. No active flow configured.",
            }
        _session_engines[session_id] = engine
    else:
        engine = _session_engines[session_id]

    # Collect fields from arguments
    # Filter out non-field arguments
    field_arguments = {
        k: v for k, v in arguments.items()
        if k in ["ZipCode", "NumberOfDrivers", "EmailAddress", "FirstName", "LastName", "DateOfBirth"]
    }

    state = engine.collect_fields(field_arguments)

    # Check if we have validation errors
    if state.validation_errors:
        error_messages = "\n".join([
            f"• {field}: {error}"
            for field, error in state.validation_errors.items()
        ])
        return {
            "structured_content": {
                "collected_fields": state.collected_fields,
                "validation_errors": state.validation_errors,
            },
            "response_text": f"There were some issues with the information provided:\n\n{error_messages}",
        }

    # Check if we need more information
    if state.status == CollectionStatus.INCOMPLETE:
        next_questions = engine.get_next_questions(limit=3)
        progress = engine.get_progress()

        questions_text = "\n".join([
            f"• {q.prompt_text}" + (f" (Example: {q.example})" if q.example else "")
            for q in next_questions
        ])

        return {
            "structured_content": {
                "collected_fields": state.collected_fields,
                "missing_fields": state.missing_fields,
                "progress": progress,
            },
            "response_text": (
                f"To get your quick quote, I need a bit more information:\n\n"
                f"{questions_text}\n\n"
                f"Progress: {progress['percent_complete']}% complete"
            ),
        }

    # We have all required fields - generate quote
    logger.info(f"Quick quote collection complete for session {session_id}")

    # Extract collected values
    zip_code = state.collected_fields.get("ZipCode")
    num_drivers = state.collected_fields.get("NumberOfDrivers")
    email = state.collected_fields.get("EmailAddress")

    # Look up city and state
    city_state = _lookup_city_state_from_zip(zip_code)
    if not city_state:
        return {
            "response_text": f"Unable to find location information for zip code {zip_code}. Please provide a valid US zip code.",
        }

    city, state_name = city_state
    effective_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    # Generate best case scenario
    best_case_customer = {
        "FirstName": "Best",
        "LastName": "Case",
        "Address": {
            "Street1": "123 Main St",
            "City": city,
            "State": state_name,
            "ZipCode": zip_code,
        },
        "MonthsAtResidence": 60,
        "PriorInsuranceInformation": {"PriorInsurance": True},
    }

    best_case_drivers = []
    for i in range(num_drivers):
        driver = {
            "DriverId": i + 1,
            "FirstName": f"Driver{i+1}",
            "LastName": "BestCase",
            "DateOfBirth": "1989-01-01",
            "Gender": "Male" if i % 2 == 0 else "Female",
            "MaritalStatus": "Married",
            "LicenseInformation": {"LicenseStatus": "Valid"},
            "Attributes": {
                "PropertyInsurance": True,
                "Relation": "Insured" if i == 0 else "Spouse",
                "ResidencyStatus": "Own",
                "ResidencyType": "Home",
            }
        }
        best_case_drivers.append(driver)

    best_case_vehicle = {
        "VehicleId": 1,
        "Vin": "1HGCM82633A123456",
        "Year": 2018,
        "Make": "Honda",
        "Model": "Accord",
        "BodyType": "Sedan",
        "UseType": "Commute",
        "AssignedDriverId": 1,
        "MilesToWork": 10,
        "PercentToWork": 50,
        "AnnualMiles": 12000,
        "CoverageInformation": {
            "CollisionDeductible": "$500",
            "ComprehensiveDeductible": "$500",
            "RentalLimit": "None",
            "TowingLimit": "None",
            "SafetyGlassCoverage": False,
        }
    }

    best_case_payload = build_minimal_payload_with_defaults(
        customer=best_case_customer,
        drivers=best_case_drivers,
        vehicles=[best_case_vehicle],
        policy_coverages={},
        identifier=f"QUICK_BEST_{zip_code}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        effective_date=effective_date,
        state=state_name,
    )

    # Generate worst case scenario
    worst_case_customer = {
        "FirstName": "Worst",
        "LastName": "Case",
        "Address": {
            "Street1": "123 Main St",
            "City": city,
            "State": state_name,
            "ZipCode": zip_code,
        },
        "MonthsAtResidence": 12,
        "PriorInsuranceInformation": {
            "PriorInsurance": False,
            "ReasonForNoInsurance": "Other"
        },
    }

    worst_case_drivers = []
    for i in range(num_drivers):
        driver = {
            "DriverId": i + 1,
            "FirstName": f"Driver{i+1}",
            "LastName": "Worst",
            "DateOfBirth": "2006-01-01",
            "Gender": "Male",
            "MaritalStatus": "Single",
            "LicenseInformation": {
                "LicenseStatus": "Valid",
                "MonthsLicensed": 24,
            },
            "Attributes": {
                "PropertyInsurance": False,
                "Relation": "Insured" if i == 0 else "Child",
                "ResidencyStatus": "Rent",
                "ResidencyType": "Apartment",
            }
        }
        worst_case_drivers.append(driver)

    worst_case_vehicle = {
        "VehicleId": 1,
        "Vin": "5YJ3E1EA5KF123456",
        "Year": 2023,
        "Make": "Tesla",
        "Model": "Model 3",
        "BodyType": "Sedan",
        "UseType": "Commute",
        "AssignedDriverId": 1,
        "MilesToWork": 30,
        "PercentToWork": 80,
        "AnnualMiles": 18000,
        "CoverageInformation": {
            "CollisionDeductible": "$500",
            "ComprehensiveDeductible": "$500",
            "RentalLimit": "None",
            "TowingLimit": "None",
            "SafetyGlassCoverage": False,
        }
    }

    worst_case_payload = build_minimal_payload_with_defaults(
        customer=worst_case_customer,
        drivers=worst_case_drivers,
        vehicles=[worst_case_vehicle],
        policy_coverages={},
        identifier=f"QUICK_WORST_{zip_code}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        effective_date=effective_date,
        state=state_name,
    )

    # Submit both quotes (same logic as original handler)
    _sanitize_personal_auto_rate_request(best_case_payload)
    best_case_payload["CarrierInformation"] = DEFAULT_CARRIER_INFORMATION
    _sanitize_personal_auto_rate_request(worst_case_payload)
    worst_case_payload["CarrierInformation"] = DEFAULT_CARRIER_INFORMATION

    state_code = state_abbreviation(state_name) or state_name
    url = f"{PERSONAL_AUTO_RATE_ENDPOINT}/{state_code}/rates/latest?multiAgency=false"
    headers = _personal_auto_rate_headers()

    best_results = None
    worst_results = None

    try:
        # Submit best case
        logger.info("Submitting best case scenario for quick quote")
        async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as client:
            best_response = await client.post(url, headers=headers, json=best_case_payload)

        if not best_response.is_error:
            best_parsed = best_response.json()
            best_tx_id = best_parsed.get("transactionId")

            if best_tx_id:
                async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as client:
                    results_response = await client.get(
                        PERSONAL_AUTO_RATE_RESULTS_ENDPOINT,
                        headers=headers,
                        params={"Id": best_tx_id}
                    )
                if not results_response.is_error:
                    best_results = results_response.json()

        # Submit worst case
        logger.info("Submitting worst case scenario for quick quote")
        async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as client:
            worst_response = await client.post(url, headers=headers, json=worst_case_payload)

        if not worst_response.is_error:
            worst_parsed = worst_response.json()
            worst_tx_id = worst_parsed.get("transactionId")

            if worst_tx_id:
                async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as client:
                    results_response = await client.get(
                        PERSONAL_AUTO_RATE_RESULTS_ENDPOINT,
                        headers=headers,
                        params={"Id": worst_tx_id}
                    )
                if not results_response.is_error:
                    worst_results = results_response.json()

    except httpx.HTTPError as exc:
        logger.exception("Quick quote request failed")
        return {
            "response_text": f"Failed to get quotes due to network error: {exc}",
        }

    # Format response
    message = f"**Quick Quote Range for {city}, {state_name}** (Zip: {zip_code})\n\n"

    if best_results:
        best_summary = format_rate_results_summary(best_results)
        if best_summary:
            message += (
                f"**BEST CASE** (experienced driver, reliable vehicle):\n"
                f"{best_summary}\n\n"
            )

    if worst_results:
        worst_summary = format_rate_results_summary(worst_results)
        if worst_summary:
            message += (
                f"**WORST CASE** (new driver, newer vehicle):\n"
                f"{worst_summary}\n\n"
            )

    if email:
        message += f"\nWe'll send these results to {email}.\n\n"

    message += (
        "\nYour actual rate will fall within this range based on your specific details.\n\n"
        "**Ready for a more accurate quote?** I can collect your actual driver and "
        "vehicle information to give you a precise premium."
    )

    # Clean up session
    _session_engines.pop(session_id, None)

    import mcp.types as types
    return {
        "structured_content": {
            "zip_code": zip_code,
            "number_of_drivers": num_drivers,
            "email": email,
            "city": city,
            "state": state_name,
            "best_case_results": best_results,
            "worst_case_results": worst_results,
            "stage": "quick_quote_complete",
        },
        "content": [types.TextContent(type="text", text=message)],
    }


async def _get_quick_quote(arguments: Mapping[str, Any]) -> ToolInvocationResult:
    """Get a quick quote range with just zip code and number of drivers.

    Returns placeholder ranges based on typical premiums in the area.
    This provides instant feedback without making API calls with synthetic data.
    """
    from .utils import _lookup_city_state_from_zip
    from .quick_quote_ranges import format_quote_range_message, calculate_quote_range

    payload = QuickQuoteIntake.model_validate(arguments)
    zip_code = payload.zip_code
    num_drivers = payload.number_of_drivers

    logger.info(f"Quick quote request: zip={zip_code}, drivers={num_drivers}")

    # Look up city and state from zip code
    city_state = _lookup_city_state_from_zip(zip_code)
    if not city_state:
        return {
            "response_text": f"Unable to find location information for zip code {zip_code}. Please provide a valid US zip code.",
        }

    city, state = city_state
    logger.info(f"Resolved location: {city}, {state}")

    # Calculate placeholder ranges
    best_min, best_max, worst_min, worst_max = calculate_quote_range(
        zip_code, num_drivers, city, state
    )

    # Format message
    message = format_quote_range_message(zip_code, city, state, num_drivers)

    import mcp.types as types
    return {
        "structured_content": {
            "zip_code": zip_code,
            "number_of_drivers": num_drivers,
            "city": city,
            "state": state,
            "best_case_range": {
                "min": best_min,
                "max": best_max,
                "per_month_min": int(best_min / 6),
                "per_month_max": int(best_max / 6),
            },
            "worst_case_range": {
                "min": worst_min,
                "max": worst_max,
                "per_month_min": int(worst_min / 6),
                "per_month_max": int(worst_max / 6),
            },
            "stage": "quick_quote_complete",
            "is_placeholder": True,  # Indicate these are estimates
        },
        "content": [types.TextContent(type="text", text=message)],
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
    if not city_state:
        return {
            "response_text": f"Unable to find location information for zip code {payload.zip_code}. Please provide a valid US zip code.",
        }

    city, state = city_state
    logger.info(f"Resolved location: {city}, {state}")

    # Count drivers and vehicles
    num_drivers = 2 if payload.additional_driver else 1
    num_vehicles = 2 if payload.vehicle_2 else 1

    logger.info(f"Enhanced quick quote: {num_drivers} drivers, {num_vehicles} vehicles in {city}, {state}")

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
    message = f"Perfect! I've generated your insurance quote estimates.\n\n"
    message += f"**Your Profile:**\n"
    message += f"📍 Location: {city}, {state} {payload.zip_code}\n"
    message += f"🚗 Vehicle: {payload.vehicle_1.year} {payload.vehicle_1.make} {payload.vehicle_1.model}\n"
    if payload.vehicle_2:
        message += f"🚗 Vehicle 2: {payload.vehicle_2.year} {payload.vehicle_2.make} {payload.vehicle_2.model}\n"
    message += f"🛡️ Coverage: {'Full Coverage (Liability + Comp/Coll)' if payload.coverage_type == 'full_coverage' else 'Liability Only'}\n"
    message += f"👤 Primary Driver: Age {payload.primary_driver_age}, {payload.primary_driver_marital_status.title()}\n"
    if payload.additional_driver:
        message += f"👥 Additional Driver: Age {payload.additional_driver.age}, {payload.additional_driver.marital_status.title()}\n"
    message += f"\n\n**Your estimated quotes from 3 carriers are displayed above.**\n\n"
    message += f"These are estimates based on your information. Click 'Continue to Personalized Quote' to get a final rate."

    import mcp.types as types
    from .widget_registry import WIDGETS_BY_ID, QUICK_QUOTE_RESULTS_WIDGET_IDENTIFIER, _embedded_widget_resource, _tool_meta
    from .carrier_mapping import get_carriers_for_state

    # Get server base URL from environment
    server_base_url = os.getenv("SERVER_BASE_URL", "http://localhost:8000")

    # Get state-specific carriers
    logger.info(f"=== CARRIER SELECTION DEBUG ===")
    logger.info(f"Raw state from Google API: '{state}'")
    from .carrier_mapping import normalize_state
    normalized = normalize_state(state)
    logger.info(f"Normalized state: '{normalized}'")
    carrier_names = get_carriers_for_state(state)
    logger.info(f"Carriers for {state}: {carrier_names}")
    logger.info(f"=== END CARRIER DEBUG ===")

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

        # Format for widget
        carriers = []
        for quote in estimates["quotes"]:
            carriers.append({
                "name": quote["carrier"],
                "logo": get_carrier_logo(quote["carrier"]),
                "annual_cost": quote["annual"],
                "monthly_cost": quote["monthly"],
                "range_low": quote["range_monthly"][0],
                "range_high": quote["range_monthly"][1],
                "confidence": quote["confidence"],
                "explanations": quote["explanations"],
            })

        logger.info(f"Generated {len(carriers)} carrier estimates using estimation engine")
        for carrier in carriers:
            logger.info(
                f"  {carrier['name']}: ${carrier['monthly_cost']}/mo "
                f"(${carrier['range_low']}-${carrier['range_high']})"
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

    # Get widget metadata
    quick_quote_widget = WIDGETS_BY_ID[QUICK_QUOTE_RESULTS_WIDGET_IDENTIFIER]
    widget_resource = _embedded_widget_resource(quick_quote_widget)
    widget_meta = {
        **_tool_meta(quick_quote_widget),
        "openai.com/widget": widget_resource.model_dump(mode="json"),
    }

    # Build structured content
    structured_content = {
        "zip_code": payload.zip_code,
        "city": city,
        "state": state,
        "primary_driver_age": payload.primary_driver_age,
        "num_drivers": num_drivers,
        "num_vehicles": num_vehicles,
        "server_url": server_base_url,
        "carriers": carriers,
        "mercury_logo": get_carrier_logo("Mercury Auto Insurance"),  # Always show Mercury in header
        "stage": "quick_quote_complete",
    }

    logger.info(f"=== RETURNING STRUCTURED CONTENT ===")
    logger.info(f"City: {city}, State: {state}")
    logger.info(f"Number of carriers in response: {len(carriers)}")
    for i, carrier in enumerate(carriers):
        logger.info(f"  Carrier {i+1}: {carrier['name']} - ${carrier['annual_cost']}/year")
    logger.info(f"=== END STRUCTURED CONTENT ===")

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


def _collect_personal_auto_customer(arguments: Mapping[str, Any]) -> ToolInvocationResult:
    """Collect and validate customer profile information."""
    from .models import CumulativeCustomerIntake
    from .utils import validate_required_fields, get_nested_value

    payload = CumulativeCustomerIntake.model_validate(arguments)

    # Required fields for customer batch
    required_fields = [
        "FirstName",
        "LastName",
        "Address.Street1",
        "Address.City",
        "Address.State",
        "Address.ZipCode",
        "MonthsAtResidence",
        "PriorInsuranceInformation.PriorInsurance",
    ]

    # Validate completeness
    customer_data = payload.customer or {}
    missing = validate_required_fields(customer_data, required_fields)

    # Build response message
    if customer_data:
        first_name = get_nested_value(customer_data, "FirstName") or ""
        middle_name = get_nested_value(customer_data, "MiddleName") or ""
        last_name = get_nested_value(customer_data, "LastName") or ""
        full_name = " ".join(part for part in [first_name, middle_name, last_name] if part)
        message = f"Captured customer profile for {full_name.strip()}." if full_name.strip() else "Captured customer information."
    else:
        message = "Ready to collect customer information."

    if missing:
        message += f" Still need: {', '.join(missing)}."

    return {
        "structured_content": {
            "customer": customer_data,
            "validation": {
                "customer_complete": len(missing) == 0,
                "missing_fields": missing,
            }
        },
        "response_text": message,
    }


def _collect_personal_auto_driver_roster(
    arguments: Mapping[str, Any]
) -> ToolInvocationResult:
    """Collect and validate driver roster information."""
    payload = PersonalAutoDriverRosterInput.model_validate(arguments)
    entries = payload.driver_roster
    names = [
        " ".join(
            part
            for part in [entry.first_name, entry.middle_name, entry.last_name]
            if part
        )
        for entry in entries
    ]

    if not names:
        message = "Captured an empty driver roster."
    elif len(names) == 1:
        message = f"Captured driver roster entry for {names[0]}."
    else:
        listed = ", ".join(names)
        message = (
            f"Captured driver roster entries for {len(names)} drivers: {listed}."
        )

    return {
        "structured_content": payload.model_dump(by_alias=True),
        "response_text": message,
    }


def _collect_personal_auto_drivers(arguments: Mapping[str, Any]) -> ToolInvocationResult:
    """Collect and validate rated driver information (can append customer fields)."""
    from .models import CumulativeDriverIntake
    from .utils import validate_required_fields, get_nested_value

    payload = CumulativeDriverIntake.model_validate(arguments)

    # Required fields for driver batch
    driver_required_fields = [
        "FirstName",
        "LastName",
        "DateOfBirth",
        "Gender",
        "MaritalStatus",
        "LicenseInformation.LicenseStatus",
        "Attributes.PropertyInsurance",
        "Attributes.Relation",
        "Attributes.ResidencyStatus",
        "Attributes.ResidencyType",
    ]

    # Customer required fields (for forward-appending)
    customer_required_fields = [
        "FirstName",
        "LastName",
        "Address.Street1",
        "Address.City",
        "Address.State",
        "Address.ZipCode",
        "MonthsAtResidence",
        "PriorInsuranceInformation.PriorInsurance",
    ]

    # Validate drivers
    drivers_data = payload.rated_drivers or []
    driver_missing = []
    if drivers_data:
        for idx, driver_data in enumerate(drivers_data):
            missing = validate_required_fields(driver_data, driver_required_fields)
            if missing:
                driver_missing.extend([f"Driver[{idx}].{field}" for field in missing])

    # Validate customer (if provided for forward-appending)
    customer_data = payload.customer or {}
    customer_missing = validate_required_fields(customer_data, customer_required_fields) if customer_data else []

    # Build message
    if drivers_data:
        driver_count = len(drivers_data)
        names = []
        for driver in drivers_data:
            first_name = get_nested_value(driver, "FirstName") or ""
            middle_name = get_nested_value(driver, "MiddleName") or ""
            last_name = get_nested_value(driver, "LastName") or ""
            full_name = " ".join(part for part in [first_name, middle_name, last_name] if part)
            names.append(full_name if full_name.strip() else "Driver")
        if driver_count == 1:
            message = f"Captured driver profile for {names[0]}."
        else:
            listed = ", ".join(names)
            message = f"Captured driver profiles for {driver_count} drivers: {listed}."
    else:
        message = "Ready to collect driver information."

    all_missing = customer_missing + driver_missing
    if all_missing:
        message += f" Still need: {', '.join(all_missing)}."

    return {
        "structured_content": {
            "customer": customer_data if customer_data else None,
            "rated_drivers": drivers_data,
            "validation": {
                "customer_complete": len(customer_missing) == 0 if customer_data else None,
                "drivers_complete": len(driver_missing) == 0,
                "missing_fields": all_missing,
            }
        },
        "response_text": message,
    }


def _collect_personal_auto_vehicles(arguments: Mapping[str, Any]) -> ToolInvocationResult:
    """Collect and validate vehicle information (can append customer/driver fields)."""
    from .models import CumulativeVehicleIntake
    from .utils import validate_required_fields, get_nested_value

    payload = CumulativeVehicleIntake.model_validate(arguments)

    # Required fields for vehicle batch
    vehicle_required_fields = [
        "Vin",
        "Year",
        "Make",
        "Model",
        "BodyType",
        "UseType",
        "AssignedDriverId",
        "CoverageInformation.CollisionDeductible",
        "CoverageInformation.ComprehensiveDeductible",
        "CoverageInformation.RentalLimit",
        "CoverageInformation.TowingLimit",
        "CoverageInformation.SafetyGlassCoverage",
        "PercentToWork",
        "MilesToWork",
        "AnnualMiles",
    ]

    # Customer required fields
    customer_required_fields = [
        "FirstName",
        "LastName",
        "Address.Street1",
        "Address.City",
        "Address.State",
        "Address.ZipCode",
        "MonthsAtResidence",
        "PriorInsuranceInformation.PriorInsurance",
    ]

    # Driver required fields
    driver_required_fields = [
        "FirstName",
        "LastName",
        "DateOfBirth",
        "Gender",
        "MaritalStatus",
        "LicenseInformation.LicenseStatus",
        "Attributes.PropertyInsurance",
        "Attributes.Relation",
        "Attributes.ResidencyStatus",
        "Attributes.ResidencyType",
    ]

    # Validate vehicles
    vehicles_data = payload.vehicles or []
    vehicle_missing = []
    if vehicles_data:
        for idx, vehicle_data in enumerate(vehicles_data):
            missing = validate_required_fields(vehicle_data, vehicle_required_fields)
            if missing:
                vehicle_missing.extend([f"Vehicle[{idx}].{field}" for field in missing])

    # Validate customer (if provided for forward-appending)
    customer_data = payload.customer or {}
    customer_missing = validate_required_fields(customer_data, customer_required_fields) if customer_data else []

    # Validate drivers (if provided for forward-appending)
    drivers_data = payload.rated_drivers or []
    driver_missing = []
    if drivers_data:
        for idx, driver_data in enumerate(drivers_data):
            missing = validate_required_fields(driver_data, driver_required_fields)
            if missing:
                driver_missing.extend([f"Driver[{idx}].{field}" for field in missing])

    # Build message
    if vehicles_data:
        vehicle_count = len(vehicles_data)
        summaries = []
        for vehicle_data in vehicles_data:
            year = get_nested_value(vehicle_data, "Year") or ""
            make = get_nested_value(vehicle_data, "Make") or ""
            model = get_nested_value(vehicle_data, "Model") or ""
            descriptor = f"{year} {make} {model}".strip()
            summaries.append(descriptor if descriptor else "Vehicle")
        if vehicle_count == 1:
            message = f"Captured vehicle information for {summaries[0]}."
        else:
            listed = ", ".join(summaries)
            message = f"Captured vehicle information for {vehicle_count} vehicles: {listed}."
    else:
        message = "Ready to collect vehicle information."

    all_missing = customer_missing + driver_missing + vehicle_missing
    if all_missing:
        message += f" Still need: {', '.join(all_missing)}."

    return {
        "structured_content": {
            "customer": customer_data if customer_data else None,
            "rated_drivers": drivers_data if drivers_data else None,
            "vehicles": vehicles_data,
            "validation": {
                "customer_complete": len(customer_missing) == 0 if customer_data else None,
                "drivers_complete": len(driver_missing) == 0 if drivers_data else None,
                "vehicles_complete": len(vehicle_missing) == 0,
                "missing_fields": all_missing,
            }
        },
        "response_text": message,
    }


def _personal_auto_rate_headers() -> dict[str, str]:
    """Get headers for personal auto rate API requests."""
    api_key = os.getenv("PERSONAL_AUTO_RATE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Missing PERSONAL_AUTO_RATE_API_KEY environment variable for personal auto rate requests."
        )
    return {
        "Content-Type": "application/json",
        "User-Agent": "insomnia/11.6.1",
        "x-api-key": api_key,
    }


async def _request_personal_auto_rate(arguments: Mapping[str, Any]) -> ToolInvocationResult:
    """Request personal auto insurance rate."""
    from .field_defaults import build_minimal_payload_with_defaults

    payload = PersonalAutoRateRequest.model_validate(arguments)
    request_body = payload.model_dump(by_alias=True, exclude_none=True)

    # Check if this is a minimal submission (missing optional fields)
    # If customer is missing optional fields like MiddleName, DeclinedEmail, etc., apply defaults
    customer_data = request_body.get("Customer", {})
    is_minimal = (
        customer_data.get("MiddleName") is None and
        customer_data.get("DeclinedEmail") is None and
        len(customer_data.keys()) < 15  # Minimal customer has ~8 required fields, full has 15+
    )

    if is_minimal:
        logger.info("Detected minimal submission, applying defaults")
        # Build payload with defaults
        enriched_payload = build_minimal_payload_with_defaults(
            customer=customer_data,
            drivers=request_body.get("RatedDrivers", []),
            vehicles=request_body.get("Vehicles", []),
            policy_coverages=request_body.get("PolicyCoverages", {}),
            identifier=request_body.get("Identifier", ""),
            effective_date=request_body.get("EffectiveDate", ""),
            state=customer_data.get("Address", {}).get("State", "CA"),
            term=request_body.get("Term"),
            payment_method=request_body.get("PaymentMethod"),
            policy_type=request_body.get("PolicyType"),
        )
        request_body = enriched_payload
        logger.info("Applied defaults to minimal submission")

    _sanitize_personal_auto_rate_request(request_body)
    request_body["CarrierInformation"] = DEFAULT_CARRIER_INFORMATION

    try:
        log_path = Path(__file__).with_name("personal_auto_rate_request.json")
        log_path.write_text(
            json.dumps(request_body, indent=2, sort_keys=True), encoding="utf-8"
        )
    except OSError as exc:  # pragma: no cover - filesystem error handling
        logger.warning("Failed to write personal auto rate request body: %s", exc)

    state = payload.customer.address.state
    state_code = state_abbreviation(state) or state
    url = f"{PERSONAL_AUTO_RATE_ENDPOINT}/{state_code}/rates/latest?multiAgency=false"

    headers = _personal_auto_rate_headers()

    _log_network_request(method="POST", url=url, headers=headers, payload=request_body)

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as client:
            response = await client.post(
                url,
                headers=headers,
                json=request_body,
            )
    except httpx.HTTPError as exc:  # pragma: no cover - network error handling
        logger.exception("Personal auto rate request failed due to network error")
        raise RuntimeError(f"Failed to request personal auto rate: {exc}") from exc

    status_code = response.status_code
    response_text = response.text
    _log_network_response(
        method="POST", url=url, status=status_code, response_text=response_text
    )
    parsed_response: Any = {}
    if response_text.strip():
        try:
            parsed_response = response.json()
        except (json.JSONDecodeError, ValueError) as exc:
            raise RuntimeError(
                f"Failed to parse personal auto rate response: {exc}"
            ) from exc

    if response.is_error:
        raise RuntimeError(
            f"Personal auto rate request failed with status {status_code}: {response_text}"
        )

    transaction_id = parsed_response.get("transactionId")
    rate_results: Any = None
    rate_results_status: Optional[int] = None
    if transaction_id:
        results_url = PERSONAL_AUTO_RATE_RESULTS_ENDPOINT
        _log_network_request(
            method="GET",
            url=results_url,
            headers=headers,
            payload={"params": {"Id": transaction_id}},
        )
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as client:
                rate_results_response = await client.get(
                    results_url,
                    headers=headers,
                    params={"Id": transaction_id},
                )
        except httpx.HTTPError as exc:  # pragma: no cover - network error handling
            logger.exception(
                "Personal auto rate results request failed due to network error"
            )
            raise RuntimeError(
                f"Failed to request personal auto rate results: {exc}"
            ) from exc

        rate_results_status = rate_results_response.status_code
        rate_results_text = rate_results_response.text
        _log_network_response(
            method="GET",
            url=results_url,
            status=rate_results_status,
            response_text=rate_results_text,
        )
        if rate_results_response.is_error:
            raise RuntimeError(
                "Personal auto rate results request failed with "
                f"status {rate_results_status}: {rate_results_text}"
            )
        if rate_results_text.strip():
            try:
                rate_results = rate_results_response.json()
            except (json.JSONDecodeError, ValueError) as exc:
                raise RuntimeError(
                    f"Failed to parse personal auto rate results response: {exc}"
                ) from exc

    message = (
        f"Submitted personal auto rate request for {payload.identifier} (transaction {transaction_id})."
        if transaction_id
        else f"Submitted personal auto rate request for {payload.identifier}."
    )
    if transaction_id and rate_results is not None:
        message += " Retrieved carrier rate results."
        summary = format_rate_results_summary(rate_results)
        if summary:
            message += f"\n\n{summary}"

    # Build content array with model-visible transaction ID
    import mcp.types as types
    content = [types.TextContent(type="text", text=message)]

    # Add transaction ID as model-only context so assistant can reference it later
    if transaction_id:
        content.append(
            types.TextContent(
                type="text",
                text=json.dumps({
                    "quoteId": payload.identifier,
                    "transactionId": transaction_id
                }),
                annotations=types.Annotations(audience=["assistant"])
            )
        )

    return {
        "structured_content": {
            "identifier": payload.identifier,
            "request": request_body,
            "response": parsed_response,
            "status": status_code,
            "rate_results": rate_results,
            "rate_results_status": rate_results_status,
        },
        "content": content,
    }


async def _retrieve_personal_auto_rate_results(
    arguments: Mapping[str, Any]
) -> ToolInvocationResult:
    """Retrieve personal auto rate results by identifier."""
    payload = PersonalAutoRateResultsRequest.model_validate(arguments)
    identifier = payload.identifier

    headers = _personal_auto_rate_headers()

    _log_network_request(
        method="GET",
        url=PERSONAL_AUTO_RATE_RESULTS_ENDPOINT,
        headers=headers,
        payload={"params": {"Id": identifier}},
    )

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as client:
            response = await client.get(
                PERSONAL_AUTO_RATE_RESULTS_ENDPOINT,
                headers=headers,
                params={"Id": identifier},
            )
    except httpx.HTTPError as exc:  # pragma: no cover - network error handling
        logger.exception(
            "Personal auto rate results retrieval failed due to network error"
        )
        raise RuntimeError(
            f"Failed to retrieve personal auto rate results: {exc}"
        ) from exc

    status_code = response.status_code
    response_text = response.text
    _log_network_response(
        method="GET",
        url=PERSONAL_AUTO_RATE_RESULTS_ENDPOINT,
        status=status_code,
        response_text=response_text,
    )
    rate_results: Any = None
    if response_text.strip():
        try:
            rate_results = response.json()
        except (json.JSONDecodeError, ValueError) as exc:
            raise RuntimeError(
                f"Failed to parse personal auto rate results response: {exc}"
            ) from exc

    if response.is_error:
        raise RuntimeError(
            "Personal auto rate results request failed with "
            f"status {status_code}: {response_text}"
        )

    message = f"Retrieved personal auto rate results for {identifier}."
    if not rate_results:
        message += " No carrier results were returned."
    elif rate_results:
        summary = format_rate_results_summary(rate_results)
        if summary:
            message += f"\n\n{summary}"

    # Build content array with model-visible identifier
    import mcp.types as types
    content = [types.TextContent(type="text", text=message)]

    # Add identifier as model-only context so assistant can reference it later
    content.append(
        types.TextContent(
            type="text",
            text=json.dumps({
                "quoteId": identifier,
                "transactionId": identifier
            }),
            annotations=types.Annotations(audience=["assistant"])
        )
    )

    # Log the structure we're returning for debugging
    logger.info("=== RETRIEVE TOOL RETURNING ===")
    logger.info("Message: %s", message)
    logger.info("Rate results type: %s", type(rate_results))
    if rate_results:
        logger.info("Rate results keys: %s", list(rate_results.keys()) if isinstance(rate_results, dict) else "not a dict")
        if isinstance(rate_results, dict) and "carrierResults" in rate_results:
            logger.info("carrierResults found at top level, length: %s", len(rate_results.get("carrierResults", [])))
        if isinstance(rate_results, dict) and "CarrierResults" in rate_results:
            logger.info("CarrierResults found at top level, length: %s", len(rate_results.get("CarrierResults", [])))

    result = {
        "structured_content": {
            "identifier": identifier,
            "rate_results": rate_results,
            "status": status_code,
        },
        "content": content,
    }

    logger.info("Structured content keys: %s", list(result["structured_content"].keys()))
    logger.info("=== END RETRIEVE TOOL RETURN ===")

    return result


async def _start_wizard_flow(arguments: Mapping[str, Any]) -> ToolInvocationResult:
    """Start the insurance application wizard.

    This tool launches the wizard widget and can pre-fill data from quick quote.
    """
    from .wizard_config_loader import get_wizard_flow, get_wizard_fields

    zip_code = arguments.get("zip_code")
    num_drivers = arguments.get("number_of_drivers")

    logger.info(f"Starting wizard flow with zip={zip_code}, drivers={num_drivers}")

    message = "Great! Let's collect your complete information to get an accurate quote. "
    message += "I'll guide you through a quick 5-step process."

    if zip_code:
        message += f"\n\nI've pre-filled your zip code ({zip_code})"
        if num_drivers:
            message += f" and number of drivers ({num_drivers})"
        message += " from your quick quote."

    # Load wizard configuration
    wizard_config = get_wizard_flow()
    fields_config = get_wizard_fields()

    # Get server base URL from environment (for widgets to make API calls)
    server_base_url = os.getenv("SERVER_BASE_URL", "http://localhost:8000")

    import mcp.types as types
    return {
        "structured_content": {
            "wizard_started": True,
            "wizard_config": wizard_config,
            "fields_config": fields_config,
            "server_url": server_base_url,
            "pre_fill_data": {
                "zipCode": zip_code,
                "numberOfDrivers": num_drivers,
            },
            "stage": "wizard_active",
        },
        "content": [types.TextContent(type="text", text=message)],
    }


async def _submit_wizard_form(arguments: Mapping[str, Any]) -> ToolInvocationResult:
    """Submit completed wizard form data.

    This handler receives form data from the wizard, transforms it to API payload,
    and submits to the rating API.
    """
    from .wizard_config_loader import build_payload_from_form_data

    form_data = arguments.get("form_data", {})

    if not form_data:
        return {
            "response_text": "No form data provided. Please complete the wizard first.",
        }

    logger.info("Processing wizard form submission")
    logger.debug(f"Form data fields: {list(form_data.keys())}")

    try:
        # Build API payload from form data using config
        payload = build_payload_from_form_data(form_data)

        # Validate required fields are present
        required_fields = ["Identifier", "EffectiveDate", "Customer", "Vehicles", "RatedDrivers"]
        missing = [f for f in required_fields if f not in payload or not payload[f]]

        if missing:
            return {
                "response_text": f"Wizard form is incomplete. Missing required data: {', '.join(missing)}",
            }

        logger.info(f"Built API payload for identifier: {payload.get('Identifier')}")

        # Submit to rating API (reuse existing handler logic)
        _sanitize_personal_auto_rate_request(payload)
        payload["CarrierInformation"] = DEFAULT_CARRIER_INFORMATION

        state = payload.get("Customer", {}).get("Address", {}).get("State", "CA")
        state_code = state_abbreviation(state) or state
        url = f"{PERSONAL_AUTO_RATE_ENDPOINT}/{state_code}/rates/latest?multiAgency=false"

        headers = _personal_auto_rate_headers()

        _log_network_request(method="POST", url=url, headers=headers, payload=payload)

        async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as client:
            response = await client.post(url, headers=headers, json=payload)

        status_code = response.status_code
        response_text = response.text
        _log_network_response(method="POST", url=url, status=status_code, response_text=response_text)

        parsed_response: Any = {}
        if response_text.strip():
            parsed_response = response.json()

        if response.is_error:
            raise RuntimeError(
                f"Rating request failed with status {status_code}: {response_text}"
            )

        transaction_id = parsed_response.get("transactionId")

        # Fetch rate results
        rate_results: Any = None
        if transaction_id:
            results_url = PERSONAL_AUTO_RATE_RESULTS_ENDPOINT
            async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as client:
                rate_results_response = await client.get(
                    results_url,
                    headers=headers,
                    params={"Id": transaction_id},
                )

            if not rate_results_response.is_error and rate_results_response.text.strip():
                rate_results = rate_results_response.json()

        # Build response message
        identifier = payload.get("Identifier", "your quote")
        message = f"✅ **Application Submitted Successfully!**\n\n"
        message += f"Quote ID: {identifier}\n"

        if transaction_id:
            message += f"Transaction ID: {transaction_id}\n\n"

        if rate_results:
            summary = format_rate_results_summary(rate_results)
            if summary:
                message += f"{summary}\n\n"

        message += "Your detailed quote has been generated. "
        message += "Would you like to compare carriers or modify any details?"

        import mcp.types as types
        content = [types.TextContent(type="text", text=message)]

        # Add transaction ID for assistant context
        if transaction_id:
            content.append(
                types.TextContent(
                    type="text",
                    text=json.dumps({
                        "quoteId": identifier,
                        "transactionId": transaction_id
                    }),
                    annotations=types.Annotations(audience=["assistant"])
                )
            )

        return {
            "structured_content": {
                "identifier": identifier,
                "transaction_id": transaction_id,
                "request": payload,
                "response": parsed_response,
                "rate_results": rate_results,
                "stage": "quote_complete",
            },
            "content": content,
        }

    except Exception as e:
        logger.exception("Wizard form submission failed")
        return {
            "response_text": f"Failed to process wizard submission: {str(e)}",
        }
