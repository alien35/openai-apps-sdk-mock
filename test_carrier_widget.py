"""Test the new carrier table widget."""

import asyncio
from insurance_server_python.tool_handlers import _get_enhanced_quick_quote


async def test_carrier_widget():
    """Test carrier widget with sample data."""

    print("=" * 80)
    print("CARRIER WIDGET TEST")
    print("=" * 80)

    # Test case: Young driver, newer vehicle, full coverage in LA
    test_data = {
        # Vehicles
        "Vehicle1": {
            "year": 2022,
            "make": "Honda",
            "model": "Civic"
        },
        "CoverageType": "full_coverage",

        # Drivers
        "PrimaryDriverAge": 25,
        "PrimaryDriverMaritalStatus": "single",
        "ZipCode": "90210"  # Beverly Hills / LA area
    }

    result = await _get_enhanced_quick_quote(test_data)

    print("\nMessage to user:")
    print(result['content'][0].text)

    print("\n" + "=" * 80)
    print("STRUCTURED CONTENT - CARRIER QUOTES")
    print("=" * 80)

    structured = result['structured_content']
    print(f"\nLocation: {structured['city']}, {structured['state']} {structured['zip_code']}")
    print(f"Drivers: {structured['number_of_drivers']}")
    print(f"Vehicles: {structured['number_of_vehicles']}")

    if 'carriers' in structured:
        print(f"\nCarriers ({len(structured['carriers'])} total):")
        print("-" * 80)
        for carrier in structured['carriers']:
            annual = carrier['annual_cost']
            monthly = carrier['monthly_cost']
            print(f"\n{carrier['name']}")
            print(f"  Annual:  ${annual:,}")
            print(f"  Monthly: ${monthly:,}")
            print(f"  Notes:   {carrier['notes']}")
    else:
        print("\n⚠️  WARNING: No carriers array in structured_content!")

    print("\n" + "=" * 80)
    print("WIDGET DATA VALIDATION")
    print("=" * 80)

    required_fields = ['zip_code', 'city', 'state', 'carriers']
    for field in required_fields:
        status = "✓" if field in structured else "✗"
        print(f"{status} {field}")

    if 'carriers' in structured:
        print(f"\n✓ Carriers array present with {len(structured['carriers'])} carriers")
        carrier_required = ['name', 'annual_cost', 'monthly_cost', 'notes']
        for i, carrier in enumerate(structured['carriers'], 1):
            print(f"\n  Carrier {i}: {carrier.get('name', 'MISSING NAME')}")
            for field in carrier_required:
                status = "✓" if field in carrier else "✗"
                print(f"    {status} {field}")

    print("\n" + "=" * 80)
    print("TEST COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_carrier_widget())
