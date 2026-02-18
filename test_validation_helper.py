#!/usr/bin/env python3
"""
Validation helper for testing conversational batch collection.
Run this to quickly verify tool responses during manual testing.
"""

import json
import sys


def validate_customer_response(response_json: dict) -> None:
    """Validate a customer collection tool response."""
    print("\n=== CUSTOMER VALIDATION ===")

    structured = response_json.get("structured_content", {})
    validation = structured.get("validation", {})

    print(f"✓ Customer data present: {bool(structured.get('customer'))}")
    print(f"✓ Customer complete: {validation.get('customer_complete')}")
    print(f"✓ Missing fields: {validation.get('missing_fields', [])}")

    if validation.get("customer_complete"):
        print("✅ PASS: Customer batch complete")
    else:
        print("⚠️  INCOMPLETE: Still need fields")
        for field in validation.get("missing_fields", []):
            print(f"   - {field}")


def validate_driver_response(response_json: dict) -> None:
    """Validate a driver collection tool response."""
    print("\n=== DRIVER VALIDATION ===")

    structured = response_json.get("structured_content", {})
    validation = structured.get("validation", {})
    drivers = structured.get("rated_drivers", [])

    print(f"✓ Number of drivers: {len(drivers)}")
    print(f"✓ Drivers complete: {validation.get('drivers_complete')}")
    print(f"✓ Customer complete: {validation.get('customer_complete')}")
    print(f"✓ Missing fields: {validation.get('missing_fields', [])}")

    if validation.get("drivers_complete"):
        print("✅ PASS: Driver batch complete")
    else:
        print("⚠️  INCOMPLETE: Still need fields")

    if validation.get("customer_complete") is False:
        print("⚠️  Forward-append opportunity: Customer fields can be added")


def validate_vehicle_response(response_json: dict) -> None:
    """Validate a vehicle collection tool response."""
    print("\n=== VEHICLE VALIDATION ===")

    structured = response_json.get("structured_content", {})
    validation = structured.get("validation", {})
    vehicles = structured.get("vehicles", [])

    print(f"✓ Number of vehicles: {len(vehicles)}")
    print(f"✓ Vehicles complete: {validation.get('vehicles_complete')}")
    print(f"✓ Drivers complete: {validation.get('drivers_complete')}")
    print(f"✓ Customer complete: {validation.get('customer_complete')}")
    print(f"✓ Missing fields: {validation.get('missing_fields', [])}")

    all_complete = (
        validation.get("vehicles_complete") and
        (validation.get("drivers_complete") in [True, None]) and
        (validation.get("customer_complete") in [True, None])
    )

    if all_complete:
        print("✅ PASS: All batches complete, ready for rate request")
    else:
        print("⚠️  INCOMPLETE: Still need fields")


def validate_rate_request_response(response_json: dict) -> None:
    """Validate a rate request tool response."""
    print("\n=== RATE REQUEST VALIDATION ===")

    structured = response_json.get("structured_content", {})

    print(f"✓ Request sent: {bool(structured.get('request'))}")
    print(f"✓ Status code: {structured.get('status')}")
    print(f"✓ Rate results present: {bool(structured.get('rate_results'))}")

    if structured.get("status") == 200:
        print("✅ PASS: Rate request succeeded")
        rate_results = structured.get("rate_results", {})
        carriers = rate_results.get("carrierResults", [])
        print(f"✓ Carrier results: {len(carriers)} carriers returned")
    else:
        print(f"❌ FAIL: Rate request failed with status {structured.get('status')}")


def main():
    """Main validation function."""
    if len(sys.argv) < 3:
        print("Usage: python test_validation_helper.py <tool_name> <response_json>")
        print("\nTool names:")
        print("  - customer")
        print("  - driver")
        print("  - vehicle")
        print("  - rate")
        print("\nExample:")
        print('  python test_validation_helper.py customer \'{"structured_content": {...}}\'')
        sys.exit(1)

    tool_name = sys.argv[1].lower()
    response_json_str = sys.argv[2]

    try:
        response_json = json.loads(response_json_str)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        sys.exit(1)

    validators = {
        "customer": validate_customer_response,
        "driver": validate_driver_response,
        "vehicle": validate_vehicle_response,
        "rate": validate_rate_request_response,
    }

    validator = validators.get(tool_name)
    if not validator:
        print(f"❌ Unknown tool: {tool_name}")
        print(f"   Valid tools: {', '.join(validators.keys())}")
        sys.exit(1)

    validator(response_json)


if __name__ == "__main__":
    main()
