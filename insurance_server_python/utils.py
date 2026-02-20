"""Utility functions for the insurance server."""

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Optional
from uuid import uuid4
from pydantic import BaseModel, ValidationError
from typing import Type, cast
import logging

from .constants import (
    STATE_ABBREVIATION_TO_NAME,
    STATE_NAME_TO_CANONICAL,
    STATE_NAME_TO_ABBREVIATION,
    RELATION_ALLOWED_VALUES,
    RELATION_MAPPINGS,
    TERM_MAPPINGS,
    PAYMENT_METHOD_MAPPINGS,
    POLICY_TYPE_MAPPINGS,
    BUMP_LIMIT_MAPPINGS,
    PURCHASE_TYPE_MAPPINGS,
    RESIDENCY_STATUS_MAPPINGS,
    RESIDENCY_TYPE_MAPPINGS,
    LICENSE_STATUS_MAPPINGS,
    LIABILITY_BI_LIMIT_MAPPINGS,
    PROPERTY_DAMAGE_LIMIT_MAPPINGS,
    MED_PAY_LIMIT_MAPPINGS,
)

logger = logging.getLogger(__name__)


def _model_schema(model: Type[BaseModel]) -> Dict[str, Any]:
    """Return a JSON schema for a Pydantic model using alias names."""
    return cast(Dict[str, Any], model.model_json_schema(by_alias=True))


def _sanitize_headers_for_logging(headers: Mapping[str, str]) -> Dict[str, str]:
    """Return a copy of headers with sensitive values masked."""
    sanitized = dict(headers)
    if "x-api-key" in sanitized:
        sanitized["x-api-key"] = "***redacted***"
    return sanitized


def _log_network_request(
    *, method: str, url: str, headers: Mapping[str, str], payload: Mapping[str, Any] | None
) -> None:
    """Log an outgoing network request."""
    logger.info(
        "Sending %s request to %s with headers=%s payload=%s",
        method,
        url,
        _sanitize_headers_for_logging(headers),
        payload,
    )


def _log_network_response(
    *, method: str, url: str, status: int, response_text: str
) -> None:
    """Log the response received for a network request."""
    logger.info(
        "Received %s response from %s with status=%s body=%s",
        method,
        url,
        status,
        response_text,
    )


def normalize_state_name(value: Optional[str]) -> Optional[str]:
    """Normalize state values to their canonical long-form name."""
    if value is None or not isinstance(value, str):
        return value

    trimmed = value.strip()
    if not trimmed:
        return trimmed

    upper_value = trimmed.upper()
    if upper_value in STATE_ABBREVIATION_TO_NAME:
        return STATE_ABBREVIATION_TO_NAME[upper_value]

    canonical = STATE_NAME_TO_CANONICAL.get(upper_value)
    if canonical:
        return canonical

    return trimmed


def state_abbreviation(value: Optional[str]) -> Optional[str]:
    """Return the two-letter abbreviation for a state value if known."""
    if value is None:
        return None

    normalized = normalize_state_name(value)
    if not isinstance(normalized, str):
        return normalized

    return STATE_NAME_TO_ABBREVIATION.get(normalized)


def generate_quote_identifier(now: Optional[datetime] = None) -> str:
    """Return a unique quote identifier."""
    # ``now`` is kept for API compatibility but no longer used: identifiers are
    # now generated entirely from a random UUID so they do not leak ordering
    # information and better mirror the production behaviour of the quoting
    # systems this mock server represents.
    _ = now  # pragma: no cover - preserved for signature compatibility

    return str(uuid4()).upper()


def _extract_identifier(arguments: Mapping[str, Any]) -> Optional[str]:
    """Extract a trimmed identifier from tool arguments if present."""
    raw_identifier = arguments.get("Identifier") or arguments.get("identifier")
    if not isinstance(raw_identifier, str):
        return None

    normalized = raw_identifier.strip()
    return normalized.upper() if normalized else None


def _extract_request_id(arguments: Mapping[str, Any]) -> Optional[str]:
    """Best-effort extraction of an OpenAI request identifier."""
    candidate_keys = (
        "openai/requestId",
        "openai.toolInvocation/requestId",
        "requestId",
        "request_id",
    )

    for key in candidate_keys:
        value = arguments.get(key)
        if isinstance(value, str):
            normalized = value.strip()
            if normalized:
                return normalized

    nested_keys = ("openai", "metadata", "meta", "context")
    for key in nested_keys:
        nested = arguments.get(key)
        if isinstance(nested, Mapping):
            nested_id = _extract_request_id(nested)
            if nested_id:
                return nested_id

    return None


def _normalize_enum_value(value: Optional[str], mapping: Mapping[str, str]) -> Optional[str]:
    if value is None:
        return None

    normalized = value.strip()
    if not normalized:
        return None

    key = "".join(ch for ch in normalized.lower() if ch.isalnum())
    return mapping.get(key, normalized)


def _normalize_relation_value(value: Optional[str]) -> Optional[str]:
    normalized = _normalize_enum_value(value, RELATION_MAPPINGS)
    if normalized is None:
        return None

    return normalized if normalized in RELATION_ALLOWED_VALUES else None


def _normalize_coverage_value(value: Optional[str], mapping: Mapping[str, str]) -> Optional[str]:
    if value is None:
        return None

    normalized = value.strip()
    if not normalized:
        return None

    key = "".join(ch for ch in normalized.lower() if ch.isalnum())
    return mapping.get(key, normalized)


def _ensure_iso_datetime(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None

    trimmed = value.strip()
    if not trimmed:
        return None

    candidate = trimmed.replace("Z", "+00:00")
    parsed: Optional[datetime] = None
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError:
        try:
            parsed = datetime.strptime(trimmed, "%Y-%m-%d")
            parsed = parsed.replace(tzinfo=timezone.utc)
        except ValueError:
            return trimmed

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _sanitize_personal_auto_rate_request(request_body: Dict[str, Any]) -> None:
    """Normalize and sanitize a personal auto rate request body in-place."""
    effective_date = _ensure_iso_datetime(request_body.get("EffectiveDate"))
    if effective_date:
        request_body["EffectiveDate"] = effective_date

    term = _normalize_enum_value(request_body.get("Term"), TERM_MAPPINGS)
    request_body["Term"] = term or "Semi Annual"

    payment_method = _normalize_enum_value(
        request_body.get("PaymentMethod"), PAYMENT_METHOD_MAPPINGS
    )
    if payment_method:
        request_body["PaymentMethod"] = payment_method
    else:
        request_body.setdefault("PaymentMethod", "Default")

    policy_type = _normalize_enum_value(request_body.get("PolicyType"), POLICY_TYPE_MAPPINGS)
    if policy_type:
        request_body["PolicyType"] = policy_type
    else:
        request_body.setdefault("PolicyType", "Standard")

    bump_limits = _normalize_enum_value(request_body.get("BumpLimits"), BUMP_LIMIT_MAPPINGS)
    if bump_limits:
        request_body["BumpLimits"] = bump_limits
    else:
        request_body.setdefault("BumpLimits", "No Bumping")

    customer = request_body.get("Customer")
    customer_state: Optional[str] = None
    customer_address: Optional[Dict[str, Any]] = None
    if isinstance(customer, dict):
        customer.setdefault("MonthsAtResidence", 24)
        address = customer.get("Address")
        if isinstance(address, dict):
            state_value = normalize_state_name(address.get("State"))
            if isinstance(state_value, str):
                address["State"] = state_value
                customer_state = state_value
            customer_address = address

        prior = customer.get("PriorInsuranceInformation")
        if not isinstance(prior, dict):
            prior = {}
        prior.setdefault("PriorInsurance", False)
        prior_reason = _normalize_enum_value(
            prior.get("ReasonForNoInsurance"), {"other": "Other"}
        )
        prior["ReasonForNoInsurance"] = prior_reason or "Other"
        customer["PriorInsuranceInformation"] = prior

    policy_coverages = request_body.setdefault("PolicyCoverages", {})
    if isinstance(policy_coverages, dict):
        liability = _normalize_coverage_value(
            policy_coverages.get("LiabilityBiLimit"), LIABILITY_BI_LIMIT_MAPPINGS
        )
        policy_coverages["LiabilityBiLimit"] = liability or "30000/60000"

        pd_limit = _normalize_coverage_value(
            policy_coverages.get("LiabilityPdLimit"), PROPERTY_DAMAGE_LIMIT_MAPPINGS
        )
        policy_coverages["LiabilityPdLimit"] = pd_limit or "15000"

        med_pay = _normalize_coverage_value(
            policy_coverages.get("MedPayLimit"), MED_PAY_LIMIT_MAPPINGS
        )
        policy_coverages["MedPayLimit"] = med_pay or "None"

        um_bi = _normalize_coverage_value(
            policy_coverages.get("UninsuredMotoristBiLimit"), LIABILITY_BI_LIMIT_MAPPINGS
        )
        policy_coverages["UninsuredMotoristBiLimit"] = um_bi or "30000/60000"

        accidental = _normalize_coverage_value(
            policy_coverages.get("AccidentalDeathLimit"), {
                "0": "None",
                "none": "None",
                "5000": "5000",
                "10000": "10000",
                "15000": "15000",
                "25000": "25000",
            }
        )
        policy_coverages["AccidentalDeathLimit"] = accidental or "None"
        policy_coverages.setdefault(
            "UninsuredMotoristPd/CollisionDamageWaiver", False
        )

    rated_drivers = request_body.get("RatedDrivers", [])
    default_driver_id: Optional[int] = None
    for driver in rated_drivers:
        if not isinstance(driver, dict):
            continue

        date_of_birth = _ensure_iso_datetime(driver.get("DateOfBirth"))
        if date_of_birth:
            driver["DateOfBirth"] = date_of_birth

        if default_driver_id is None:
            driver_id = driver.get("DriverId")
            if isinstance(driver_id, int):
                default_driver_id = driver_id

        attributes = driver.get("Attributes")
        if isinstance(attributes, dict):
            relation = _normalize_relation_value(attributes.get("Relation"))
            residency_status = _normalize_enum_value(
                attributes.get("ResidencyStatus"), RESIDENCY_STATUS_MAPPINGS
            )
            residency_type = _normalize_enum_value(
                attributes.get("ResidencyType"), RESIDENCY_TYPE_MAPPINGS
            )

            if relation:
                attributes["Relation"] = relation
            else:
                attributes.pop("Relation", None)

            if residency_status:
                attributes["ResidencyStatus"] = residency_status
            else:
                attributes.pop("ResidencyStatus", None)

            if residency_type:
                attributes["ResidencyType"] = residency_type
            else:
                attributes.pop("ResidencyType", None)

        license_info = driver.setdefault("LicenseInformation", {})
        if isinstance(license_info, dict):
            license_status = _normalize_enum_value(
                license_info.get("LicenseStatus"), LICENSE_STATUS_MAPPINGS
            )
            if license_status:
                license_info["LicenseStatus"] = license_status
            else:
                license_info.pop("LicenseStatus", None)
            license_info.setdefault("LicenseStatus", "Valid")
            license_info.setdefault("MonthsLicensed", 24)
            license_info.setdefault("MonthsStateLicensed", 24)
            license_info.setdefault("MonthsForeignLicense", 0)
            license_info.setdefault("CountryOfOrigin", "None")
            license_info.setdefault("MonthsMvrExperience", 24)
            license_info.setdefault("MonthsSuspended", 0)
            if not license_info.get("LicenseNumber"):
                license_info["LicenseNumber"] = "UNKNOWN0000"
            if not license_info.get("StateLicensed") and customer_state:
                license_info["StateLicensed"] = customer_state
            license_info.setdefault("ForeignNational", False)
            license_info.setdefault("InternationalDriversLicense", False)

    vehicles = request_body.get("Vehicles", [])
    for vehicle in vehicles:
        if not isinstance(vehicle, dict):
            continue

        purchase_type = _normalize_enum_value(
            vehicle.get("PurchaseType"), PURCHASE_TYPE_MAPPINGS
        )
        if purchase_type:
            vehicle["PurchaseType"] = purchase_type
        else:
            vehicle.pop("PurchaseType", None)

        if not vehicle.get("Vin"):
            vehicle["Vin"] = "2FMPK4J99J"

        if not vehicle.get("AssignedDriverId") and default_driver_id is not None:
            vehicle["AssignedDriverId"] = default_driver_id

        vehicle.setdefault("Usage", "Work School")
        vehicle.setdefault("LeasedVehicle", False)
        vehicle.setdefault("RideShare", False)
        vehicle.setdefault("Salvaged", False)
        if not vehicle.get("GaragingAddress") and customer_address is not None:
            vehicle["GaragingAddress"] = deepcopy(customer_address)

        coverage = vehicle.get("CoverageInformation")
        if isinstance(coverage, dict):
            coverage.setdefault("CollisionDeductible", "None")
            coverage.setdefault("ComprehensiveDeductible", "None")
            rental_limit = _normalize_coverage_value(
                coverage.get("RentalLimit"), MED_PAY_LIMIT_MAPPINGS
            )
            coverage["RentalLimit"] = rental_limit or "None"
            towing_limit = _normalize_coverage_value(
                coverage.get("TowingLimit"), MED_PAY_LIMIT_MAPPINGS
            )
            coverage["TowingLimit"] = towing_limit or "None"
            coverage.setdefault("GapCoverage", False)
            coverage.setdefault("CustomEquipmentValue", 0)
            coverage.setdefault("SafetyGlassCoverage", False)
            vehicle["CoverageInformation"] = {
                "CollisionDeductible": "None",
                "ComprehensiveDeductible": "None",
                "RentalLimit": "None",
                "TowingLimit": "None",
                "GapCoverage": False,
                "CustomEquipmentValue": 0,
                "SafetyGlassCoverage": False,
            }



def format_rate_results_summary(rate_results: Any) -> str:
    """Format a textual summary of rate results for the model context."""
    if not isinstance(rate_results, dict):
        return ""

    carrier_results = rate_results.get("CarrierResults") or rate_results.get("carrierResults")
    if not isinstance(carrier_results, list) or not carrier_results:
        return ""

    summary_lines = ["Rate Results Summary:"]

    for result in carrier_results:
        if not isinstance(result, dict):
            continue

        carrier_name = result.get("CarrierName") or result.get("carrierName") or "Unknown Carrier"
        program_name = (
            result.get("ProgramName") or result.get("programName") or 
            result.get("ProductName") or result.get("productName") or 
            "Auto Program"
        )
        
        # Extract premium and term
        total_premium = result.get("TotalPremium")
        if total_premium is None:
            total_premium = result.get("totalPremium")
            
        term = (
            result.get("Term") or result.get("term") or 
            result.get("TermDescription") or result.get("termDescription") or 
            "Term"
        )
        
        premium_str = f"${total_premium:,.2f}" if isinstance(total_premium, (int, float)) else "N/A"
        
        summary_lines.append(f"- {carrier_name} ({program_name}): {premium_str} / {term}")
        
        # Coverages
        coverages = []
        bi = result.get("BodilyInjuryLimit") or result.get("bodilyInjuryLimit")
        if bi: coverages.append(f"BI: {bi}")
        
        pd = result.get("PropertyDamageLimit") or result.get("propertyDamageLimit")
        if pd: coverages.append(f"PD: {pd}")
        
        um = result.get("UninsuredMotoristLimit") or result.get("uninsuredMotoristLimit")
        if um: coverages.append(f"UM: {um}")
        
        if coverages:
            summary_lines.append(f"  Coverages: {', '.join(coverages)}")

        # Payment options
        installments = result.get("Installments") or result.get("installments")
        if isinstance(installments, list) and installments:
            payment_opts = []
            for inst in installments:
                if not isinstance(inst, dict): continue
                amount = inst.get("InstallmentAmount") or inst.get("installmentAmount")
                count = inst.get("InstallmentCount") or inst.get("installmentCount")
                down = inst.get("DownPayment") or inst.get("downPayment")
                
                opt_str = ""
                if down: opt_str += f"${down:,.2f} down"
                if amount and count:
                    if opt_str: opt_str += " + "
                    opt_str += f"${amount:,.2f} x {count}"
                
                if opt_str: payment_opts.append(opt_str)
            
            if payment_opts:
                summary_lines.append(f"  Payment Options: {'; '.join(payment_opts)}")

    return "\\n".join(summary_lines)


def get_nested_value(obj: Any, path: str) -> Any:
    """Get a nested value from an object using dot notation path."""
    parts = path.split(".")
    current = obj
    for part in parts:
        if current is None:
            return None
        if isinstance(current, dict):
            current = current.get(part)
        else:
            current = getattr(current, part, None)
    return current


def validate_required_fields(data: Dict[str, Any], required_fields: list[str]) -> list[str]:
    """Check if required fields are present and return list of missing fields."""
    missing = []
    for field_path in required_fields:
        value = get_nested_value(data, field_path)
        if value is None or (isinstance(value, str) and not value.strip()):
            missing.append(field_path)
    return missing


def _lookup_city_state_from_zip(zip_code: str) -> Optional[tuple[str, str]]:
    """Look up city and state from a zip code using Google Maps Geocoding API.

    Uses GOOGLE_MAPS_API_KEY from environment variables. Falls back to
    hard-coded values if API fails.

    Args:
        zip_code: 5-digit US zip code

    Returns:
        Tuple of (city, state) or None if zip code not found
    """
    import httpx
    import os
    from urllib.parse import quote

    api_key = os.getenv("GOOGLE_MAPS_API_KEY")

    if not api_key:
        logger.warning("GOOGLE_MAPS_API_KEY not set, using fallback zip code lookup")
        return _lookup_city_state_from_zip_fallback(zip_code)

    try:
        # Call Google Geocoding API
        url = f"https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": zip_code,
            "key": api_key,
            "components": "country:US"  # Restrict to US addresses
        }

        response = httpx.get(url, params=params, timeout=5.0)

        if response.status_code != 200:
            logger.warning(f"Google Geocoding API returned status {response.status_code}")
            return _lookup_city_state_from_zip_fallback(zip_code)

        data = response.json()

        if data.get("status") != "OK" or not data.get("results"):
            logger.warning(f"Google Geocoding API status: {data.get('status')} for zip {zip_code}")
            return _lookup_city_state_from_zip_fallback(zip_code)

        # Parse address components to extract city and state
        address_components = data["results"][0].get("address_components", [])

        city = None
        state = None

        for component in address_components:
            types = component.get("types", [])

            # Look for city (locality)
            if "locality" in types:
                city = component.get("long_name")

            # Look for state (administrative_area_level_1)
            if "administrative_area_level_1" in types:
                state = component.get("long_name")

        if city and state:
            logger.info(f"Resolved zip {zip_code} to {city}, {state}")
            return (city, state)
        else:
            logger.warning(f"Could not extract city/state from Google API for zip {zip_code}")
            return _lookup_city_state_from_zip_fallback(zip_code)

    except httpx.TimeoutException:
        logger.warning(f"Google Geocoding API timeout for zip {zip_code}")
        return _lookup_city_state_from_zip_fallback(zip_code)
    except Exception as e:
        logger.warning(f"Error looking up zip {zip_code}: {e}")
        return _lookup_city_state_from_zip_fallback(zip_code)


def _lookup_city_state_from_zip_fallback(zip_code: str) -> Optional[tuple[str, str]]:
    """Fallback zip code lookup using hard-coded common zip codes.

    Used when Google Maps API is unavailable or fails.
    """
    # Common zip codes for demonstration
    ZIP_TO_LOCATION = {
        # California - Los Angeles area
        "90001": ("Los Angeles", "California"),
        "90210": ("Beverly Hills", "California"),
        "91101": ("Pasadena", "California"),
        "94102": ("San Francisco", "California"),
        "92101": ("San Diego", "California"),

        # Texas
        "75201": ("Dallas", "Texas"),
        "77001": ("Houston", "Texas"),
        "78701": ("Austin", "Texas"),
        "78201": ("San Antonio", "Texas"),

        # Florida
        "33101": ("Miami", "Florida"),
        "32801": ("Orlando", "Florida"),
        "33601": ("Tampa", "Florida"),

        # New York
        "10001": ("New York", "New York"),
        "10002": ("New York", "New York"),
        "11201": ("Brooklyn", "New York"),

        # Illinois
        "60601": ("Chicago", "Illinois"),
        "60602": ("Chicago", "Illinois"),
    }

    # Try exact lookup
    location = ZIP_TO_LOCATION.get(zip_code)
    if location:
        return location

    # Guess state by zip code prefix (rough approximation)
    # https://en.wikipedia.org/wiki/List_of_ZIP_Code_prefixes
    prefix = zip_code[:3]

    if prefix.startswith("9"):
        return ("California City", "California")
    elif prefix.startswith("7"):
        return ("Texas City", "Texas")
    elif prefix.startswith("3"):
        return ("Florida City", "Florida")
    elif prefix.startswith("1"):
        return ("New York City", "New York")
    elif prefix.startswith("6"):
        return ("Illinois City", "Illinois")

    # Default fallback
    return None
