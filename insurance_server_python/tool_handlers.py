"""Tool handlers and business logic for insurance operations."""

import json
import logging
import os
from pathlib import Path
from typing import Any, Mapping, Optional
import httpx
from pydantic import ValidationError

from .models import (
    InsuranceStateInput,
    PersonalAutoCustomerIntake,
    PersonalAutoDriverRosterInput,
    PersonalAutoDriverIntake,
    PersonalAutoVehicleIntake,
    PersonalAutoRateRequest,
    PersonalAutoRateResultsRequest,
    ToolInvocationResult,
)
from .constants import (
    PERSONAL_AUTO_RATE_ENDPOINT,
    PERSONAL_AUTO_RATE_RESULTS_ENDPOINT,
    DEFAULT_CARRIER_INFORMATION,
)
from .utils import (
    _extract_request_id,
    _sanitize_personal_auto_rate_request,
    _log_network_request,
    _log_network_response,
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


def _collect_personal_auto_customer(arguments: Mapping[str, Any]) -> ToolInvocationResult:
    """Collect and validate customer profile information."""
    payload = PersonalAutoCustomerIntake.model_validate(arguments)
    customer = payload.customer
    full_name = " ".join(
        part
        for part in [customer.first_name, customer.middle_name, customer.last_name]
        if part
    )
    message = f"Captured customer profile for {full_name.strip()}.".strip()
    return {
        "structured_content": payload.model_dump(by_alias=True),
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
    """Collect and validate rated driver information."""
    payload = PersonalAutoDriverIntake.model_validate(arguments)
    driver_count = len(payload.rated_drivers)
    names = [
        " ".join(
            part
            for part in [driver.first_name, driver.middle_name, driver.last_name]
            if part
        )
        for driver in payload.rated_drivers
    ]
    if driver_count == 1:
        message = f"Captured driver profile for {names[0]}."
    else:
        listed = ", ".join(names)
        message = f"Captured driver profiles for {driver_count} drivers: {listed}."
    return {
        "structured_content": payload.model_dump(by_alias=True),
        "response_text": message,
    }


def _collect_personal_auto_vehicles(arguments: Mapping[str, Any]) -> ToolInvocationResult:
    """Collect and validate vehicle information."""
    payload = PersonalAutoVehicleIntake.model_validate(arguments)
    vehicle_count = len(payload.vehicles)
    summaries = []
    for vehicle in payload.vehicles:
        descriptor = f"{vehicle.year or ''} {vehicle.make or ''} {vehicle.model or ''}".strip()
        summaries.append(descriptor or f"Vehicle {vehicle.vehicle_id}")
    if vehicle_count == 1:
        message = f"Captured vehicle information for {summaries[0]}."
    else:
        listed = ", ".join(summaries)
        message = f"Captured vehicle information for {vehicle_count} vehicles: {listed}."
    return {
        "structured_content": payload.model_dump(by_alias=True),
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
    payload = PersonalAutoRateRequest.model_validate(arguments)
    request_body = payload.model_dump(by_alias=True, exclude_none=True)
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
        f"Received personal auto rate response (transaction {transaction_id})."
        if transaction_id
        else "Received personal auto rate response."
    )
    if transaction_id and rate_results is not None:
        message += " Retrieved carrier rate results."

    return {
        "structured_content": {
            "request": request_body,
            "response": parsed_response,
            "status": status_code,
            "rate_results": rate_results,
            "rate_results_status": rate_results_status,
        },
        "response_text": message,
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
        "response_text": message,
    }

    logger.info("Structured content keys: %s", list(result["structured_content"].keys()))
    logger.info("=== END RETRIEVE TOOL RETURN ===")

    return result
