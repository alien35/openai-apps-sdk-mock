"""Utility functions for the insurance server."""

from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Optional
from uuid import uuid4
from pydantic import BaseModel
from typing import Type, cast
import logging

from .constants import (
    STATE_ABBREVIATION_TO_NAME,
    STATE_NAME_TO_CANONICAL,
    STATE_NAME_TO_ABBREVIATION,
    RELATION_ALLOWED_VALUES,
    RELATION_MAPPINGS,
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

    api_key = os.getenv("GOOGLE_MAPS_API_KEY")

    if not api_key:
        logger.warning("GOOGLE_MAPS_API_KEY not set, using fallback zip code lookup")
        return _lookup_city_state_from_zip_fallback(zip_code)

    try:
        # Call Google Geocoding API
        url = "https://maps.googleapis.com/maps/api/geocode/json"
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
        result = data["results"][0]
        address_components = result.get("address_components", [])

        city = None
        neighborhood = None
        state = None

        for component in address_components:
            types = component.get("types", [])

            # Look for city (locality)
            if "locality" in types:
                city = component.get("long_name")

            # Look for neighborhood as fallback (some zips only have neighborhood)
            if "neighborhood" in types and not city:
                neighborhood = component.get("long_name")

            # Look for state (administrative_area_level_1)
            if "administrative_area_level_1" in types:
                state = component.get("long_name")

        # If no locality found, check postcode_localities (multi-city zips)
        if not city:
            postcode_localities = result.get("postcode_localities", [])
            if postcode_localities:
                city = postcode_localities[0]  # Use first city
                logger.info(f"Zip {zip_code} has multiple cities: {postcode_localities}, using {city}")

        # Use neighborhood as last resort if no city found
        if not city and neighborhood:
            city = neighborhood
            logger.info(f"Using neighborhood '{neighborhood}' as city for zip {zip_code}")

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
