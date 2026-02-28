"""Test to verify minimum quick quote requirements and get a success response.

This test demonstrates the absolute minimum data needed to get a successful
insurance quote from the Personal Auto Rate API.
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import httpx

from insurance_server_python.field_defaults import build_minimal_payload_with_defaults
from insurance_server_python.constants import (
    PERSONAL_AUTO_RATE_ENDPOINT,
    PERSONAL_AUTO_RATE_RESULTS_ENDPOINT,
    DEFAULT_CARRIER_INFORMATION,
)
from insurance_server_python.utils import (
    _sanitize_personal_auto_rate_request,
    state_abbreviation,
)


async def test_minimum_quick_quote():
    """Test that we can get a successful quote with minimum required data."""

    # Load environment variables
    load_dotenv()
    api_key = os.getenv("PERSONAL_AUTO_RATE_API_KEY")
    if not api_key:
        print("❌ ERROR: PERSONAL_AUTO_RATE_API_KEY not set in .env file")
        return False

    print("=" * 60)
    print("Testing Minimum Quick Quote")
    print("=" * 60)

    # Minimum required data for a quote
    zip_code = "90210"  # Beverly Hills, CA
    state = "California"
    city = "Beverly Hills"
    num_drivers = 1

    print(f"\n📍 Location: {city}, {state} (Zip: {zip_code})")
    print(f"👥 Number of drivers: {num_drivers}")

    # Calculate effective date (tomorrow)
    effective_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    print(f"📅 Effective date: {effective_date}")

    # Minimum customer data
    customer = {
        "Identifier": f"cust-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "FirstName": "John",
        "LastName": "Doe",
        "Address": {
            "Street1": "123 Main St",
            "City": city,
            "State": state,
            "ZipCode": zip_code,
        },
        "MonthsAtResidence": 24,
        "PriorInsuranceInformation": {
            "PriorInsurance": False,
            "ReasonForNoInsurance": "Other"
        },
    }

    # Minimum driver data
    drivers = [
        {
            "DriverId": 1,
            "FirstName": "John",
            "LastName": "Doe",
            "DateOfBirth": "1985-06-15",  # ~39 years old
            "Gender": "Male",
            "MaritalStatus": "Married",
            "LicenseInformation": {
                "LicenseStatus": "Valid",
                "LicenseNumber": "UNKNOWN0000",
                "MonthsLicensed": 240,
                "MonthsMvrExperience": 240,
                "MonthsStateLicensed": 240,
                "StateLicensed": state
            },
            "Attributes": {
                "PropertyInsurance": True,
                "Relation": "Insured",
                "ResidencyStatus": "Own",
                "ResidencyType": "Home",
            }
        }
    ]

    # Minimum vehicle data
    vehicles = [
        {
            "VehicleId": 1,
            "Vin": "1HGCM82633A123456",  # Honda Accord VIN
            "AssignedDriverId": 1,
            "Usage": "Work School",
            "GaragingAddress": {
                "Street1": "123 Main St",
                "City": city,
                "State": state,
                "ZipCode": zip_code,
            },
            "CoverageInformation": {
                "CollisionDeductible": "None",
                "ComprehensiveDeductible": "None",
                "RentalLimit": "None",
                "TowingLimit": "None",
                "SafetyGlassCoverage": False,
            }
        }
    ]

    # Build complete payload with defaults
    print("\n🔧 Building payload with defaults...")
    payload = build_minimal_payload_with_defaults(
        customer=customer,
        drivers=drivers,
        vehicles=vehicles,
        policy_coverages={},  # Will use state minimums
        identifier=f"TEST_MIN_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        effective_date=effective_date,
        state=state,
    )

    # Sanitize and add carrier information
    _sanitize_personal_auto_rate_request(payload)
    payload["CarrierInformation"] = DEFAULT_CARRIER_INFORMATION

    # Save payload for debugging
    with open("/tmp/test_quick_quote_payload.json", "w") as f:
        json.dump(payload, f, indent=2)
    print("✅ Payload saved to /tmp/test_quick_quote_payload.json for debugging")

    # Print payload summary
    print("✅ Payload built successfully")
    print(f"   - Customer: {customer['FirstName']} {customer['LastName']}")
    print(f"   - Drivers: {len(drivers)}")
    print(f"   - Vehicles: {len(vehicles)} (VIN: {vehicles[0]['Vin']})")
    print(f"   - Identifier: {payload['Identifier']}")

    # Submit rate request
    state_code = state_abbreviation(state) or state
    url = f"{PERSONAL_AUTO_RATE_ENDPOINT}/{state_code}/rates/latest?multiAgency=false"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "insomnia/11.6.1",
        "x-api-key": api_key,
    }

    print(f"\n🚀 Submitting rate request to {state_code} endpoint...")

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
            response = await client.post(url, headers=headers, json=payload)

        if response.is_error:
            print(f"❌ Rate request failed: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return False

        parsed_response = response.json()
        transaction_id = parsed_response.get("transactionId")

        if not transaction_id:
            print("❌ No transaction ID in response")
            print(f"   Response: {parsed_response}")
            return False

        print("✅ Rate request successful!")
        print(f"   Transaction ID: {transaction_id}")

        # Retrieve results
        print("\n📊 Retrieving rate results...")

        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
            results_response = await client.get(
                PERSONAL_AUTO_RATE_RESULTS_ENDPOINT,
                headers=headers,
                params={"Id": transaction_id}
            )

        if results_response.is_error:
            print(f"❌ Results request failed: {results_response.status_code}")
            print(f"   Response: {results_response.text[:500]}")
            return False

        results = results_response.json()

        # Check for carrier results
        carrier_results = results.get("carrierResults") or results.get("CarrierResults") or []

        if not carrier_results:
            print("⚠️  No carrier results returned")
            print(f"   Response keys: {list(results.keys())}")
            return False

        print("✅ Rate results retrieved successfully!")
        print(f"   Number of carrier quotes: {len(carrier_results)}")

        # Display results summary
        print("\n" + "=" * 60)
        print("QUOTE RESULTS")
        print("=" * 60)

        for idx, carrier in enumerate(carrier_results, 1):
            carrier_name = carrier.get("carrierName") or carrier.get("CarrierName", "Unknown")
            products = carrier.get("products") or carrier.get("Products") or []

            # Check for errors
            errors = carrier.get("Errors") or carrier.get("errors") or []

            print(f"\n{idx}. {carrier_name}")

            if products:
                for product in products:
                    product_name = product.get("productName") or product.get("ProductName", "")
                    premium = product.get("totalPremium") or product.get("TotalPremium")
                    status = product.get("status") or product.get("Status", "")

                    if premium:
                        print(f"   - {product_name}: ${premium:.2f} ({status})")
                    else:
                        print(f"   - {product_name}: {status}")
            else:
                print("   No products available")

            # Show errors if any
            if errors:
                print("   Errors:")
                for error in errors:
                    error_text = error.get("Text") or error.get("text", "Unknown error")
                    print(f"     - {error_text}")

        print("\n" + "=" * 60)
        print("✅ SUCCESS: Minimum quick quote test passed!")
        print("=" * 60)

        return True

    except httpx.HTTPError as exc:
        print(f"❌ Network error: {exc}")
        return False
    except Exception as exc:
        print(f"❌ Unexpected error: {exc}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Run the test
    success = asyncio.run(test_minimum_quick_quote())
    exit(0 if success else 1)
