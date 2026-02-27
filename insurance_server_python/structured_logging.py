"""Structured logging for insurance application events.

This module provides standardized logging for key events that can be ingested
by monitoring systems like Grafana, Datadog, or CloudWatch.

Event Types:
- TOOL_CALL: When a tool is invoked
- QUOTE_GENERATED: When a quote is successfully generated
- QUOTE_REQUEST: When quote generation is initiated
- DUPLICATE_CALL: When a duplicate call is detected
- PHONE_ONLY_STATE: When a phone-only state is encountered
- VALIDATION_ERROR: When input validation fails
- BATCH_INCOMPLETE: When user provides incomplete data
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def log_tool_call(
    tool_name: str,
    session_id: Optional[str] = None,
    has_all_fields: bool = False,
    **kwargs
) -> None:
    """Log when a tool is called.

    Args:
        tool_name: Name of the tool being called
        session_id: Optional session identifier
        has_all_fields: Whether all required fields were provided
        **kwargs: Additional context fields
    """
    extra = {
        "event": "tool_call",
        "tool_name": tool_name,
        "session_id": session_id or "unknown",
        "has_all_fields": has_all_fields,
        **kwargs
    }

    logger.info(
        f"[TOOL_CALL] tool={tool_name} session_id={session_id or 'unknown'} has_all_fields={has_all_fields}",
        extra=extra
    )


def log_quote_generated(
    zip_code: str,
    state: Optional[str],
    num_carriers: int,
    num_vehicles: int,
    num_drivers: int,
    coverage_type: str,
    session_id: Optional[str] = None,
    **kwargs
) -> None:
    """Log when a quote is successfully generated.

    Args:
        zip_code: ZIP code for the quote
        state: State (or None if lookup failed)
        num_carriers: Number of carriers in quote
        num_vehicles: Number of vehicles
        num_drivers: Number of drivers
        coverage_type: Type of coverage (full_coverage or liability_only)
        session_id: Optional session identifier
        **kwargs: Additional context fields
    """
    extra = {
        "event": "quote_generated",
        "zip_code": zip_code,
        "state": state or "unknown",
        "num_carriers": num_carriers,
        "num_vehicles": num_vehicles,
        "num_drivers": num_drivers,
        "coverage_type": coverage_type,
        "session_id": session_id or "unknown",
        **kwargs
    }

    logger.info(
        f"[QUOTE_GENERATED] zip={zip_code} state={state or 'unknown'} carriers={num_carriers} "
        f"vehicles={num_vehicles} drivers={num_drivers} coverage={coverage_type} session_id={session_id or 'unknown'}",
        extra=extra
    )


def log_phone_only_state(
    zip_code: str,
    state: str,
    lookup_failed: bool,
    session_id: Optional[str] = None,
    **kwargs
) -> None:
    """Log when a phone-only state is detected.

    Args:
        zip_code: ZIP code that triggered phone-only
        state: State detected (or None if lookup failed)
        lookup_failed: Whether ZIP lookup failed
        session_id: Optional session identifier
        **kwargs: Additional context fields
    """
    extra = {
        "event": "phone_only_state",
        "zip_code": zip_code,
        "state": state or "unknown",
        "lookup_failed": lookup_failed,
        "session_id": session_id or "unknown",
        **kwargs
    }

    logger.info(
        f"[PHONE_ONLY_STATE] zip={zip_code} state={state} lookup_failed={lookup_failed} session_id={session_id or 'unknown'}",
        extra=extra
    )


def log_duplicate_call(
    tool_name: str,
    seconds_since_last: int,
    session_id: Optional[str] = None,
    **kwargs
) -> None:
    """Log when a duplicate call is detected.

    Args:
        tool_name: Name of the tool
        seconds_since_last: Seconds since the last identical call
        session_id: Optional session identifier
        **kwargs: Additional context fields
    """
    extra = {
        "event": "duplicate_call",
        "tool_name": tool_name,
        "seconds_since_last": seconds_since_last,
        "session_id": session_id or "unknown",
        **kwargs
    }

    logger.warning(
        f"[DUPLICATE_CALL] tool={tool_name} seconds_ago={seconds_since_last} session_id={session_id or 'unknown'}",
        extra=extra
    )


def log_validation_error(
    tool_name: str,
    error_type: str,
    error_details: str,
    session_id: Optional[str] = None,
    **kwargs
) -> None:
    """Log when input validation fails.

    Args:
        tool_name: Name of the tool
        error_type: Type of validation error
        error_details: Description of the error
        session_id: Optional session identifier
        **kwargs: Additional context fields
    """
    extra = {
        "event": "validation_error",
        "tool_name": tool_name,
        "error_type": error_type,
        "error_details": error_details,
        "session_id": session_id or "unknown",
        **kwargs
    }

    logger.warning(
        f"[VALIDATION_ERROR] tool={tool_name} type={error_type} details={error_details} session_id={session_id or 'unknown'}",
        extra=extra
    )


def log_batch_incomplete(
    batch_name: str,
    missing_fields: list,
    session_id: Optional[str] = None,
    **kwargs
) -> None:
    """Log when a batch of fields is incomplete.

    Args:
        batch_name: Name of the batch (e.g., "batch_1", "batch_2")
        missing_fields: List of missing field names
        session_id: Optional session identifier
        **kwargs: Additional context fields
    """
    extra = {
        "event": "batch_incomplete",
        "batch_name": batch_name,
        "missing_fields": missing_fields,
        "missing_count": len(missing_fields),
        "session_id": session_id or "unknown",
        **kwargs
    }

    logger.info(
        f"[BATCH_INCOMPLETE] batch={batch_name} missing={len(missing_fields)} fields={','.join(missing_fields)} session_id={session_id or 'unknown'}",
        extra=extra
    )


def log_carrier_estimation(
    zip_code: str,
    state: str,
    num_carriers: int,
    baseline_annual: int,
    confidence: str,
    session_id: Optional[str] = None,
    **kwargs
) -> None:
    """Log when carrier estimates are generated.

    Args:
        zip_code: ZIP code
        state: State abbreviation
        num_carriers: Number of carriers estimated
        baseline_annual: Baseline annual premium
        confidence: Confidence level (low, medium, high)
        session_id: Optional session identifier
        **kwargs: Additional context fields
    """
    extra = {
        "event": "carrier_estimation",
        "zip_code": zip_code,
        "state": state,
        "num_carriers": num_carriers,
        "baseline_annual": baseline_annual,
        "confidence": confidence,
        "session_id": session_id or "unknown",
        **kwargs
    }

    logger.info(
        f"[CARRIER_ESTIMATION] zip={zip_code} state={state} carriers={num_carriers} "
        f"baseline=${baseline_annual} confidence={confidence} session_id={session_id or 'unknown'}",
        extra=extra
    )


def log_quote_request(
    zip_code: str,
    num_vehicles: Optional[int],
    num_drivers: Optional[int],
    coverage_preference: Optional[str],
    session_id: Optional[str] = None,
    **kwargs
) -> None:
    """Log when a quote request is initiated.

    Args:
        zip_code: ZIP code for quote
        num_vehicles: Number of vehicles (or None)
        num_drivers: Number of drivers (or None)
        coverage_preference: Coverage type (or None)
        session_id: Optional session identifier
        **kwargs: Additional context fields
    """
    extra = {
        "event": "quote_request",
        "zip_code": zip_code,
        "num_vehicles": num_vehicles,
        "num_drivers": num_drivers,
        "coverage_preference": coverage_preference,
        "session_id": session_id or "unknown",
        **kwargs
    }

    logger.info(
        f"[QUOTE_REQUEST] zip={zip_code} vehicles={num_vehicles} drivers={num_drivers} "
        f"coverage={coverage_preference} session_id={session_id or 'unknown'}",
        extra=extra
    )
