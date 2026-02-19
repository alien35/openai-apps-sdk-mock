"""Test the batched enhanced quick quote tool."""

import asyncio
from insurance_server_python.tool_handlers import _get_enhanced_quick_quote


async def test_batched_quick_quote():
    """Test batched enhanced quick quote with sample data."""

    print("=" * 80)
    print("BATCHED QUICK QUOTE TEST")
    print("=" * 80)

    # Test case 1: Single driver, single vehicle, full coverage
    print("\nTest 1: Married driver (35), single vehicle, full coverage")
    print("-" * 80)
    test_data_1 = {
        # BATCH 1 - Vehicles
        "Vehicle1": {
            "year": 2022,
            "make": "Toyota",
            "model": "Camry"
        },
        "CoverageType": "full_coverage",

        # BATCH 2 - Drivers
        "PrimaryDriverAge": 35,
        "PrimaryDriverMaritalStatus": "married",
        "ZipCode": "90210"  # Beverly Hills
    }

    result = await _get_enhanced_quick_quote(test_data_1)
    print(f"\n{result['content'][0].text}\n")
    best = result['structured_content']['best_case_range']
    worst = result['structured_content']['worst_case_range']
    print(f"Best Case: ${best['min']:,} - ${best['max']:,} per 6 months")
    print(f"Worst Case: ${worst['min']:,} - ${worst['max']:,} per 6 months")

    # Test case 2: Young single driver, newer vehicle
    print("\n" + "=" * 80)
    print("\nTest 2: Single young driver (22), newer vehicle, full coverage")
    print("-" * 80)
    test_data_2 = {
        # BATCH 1 - Vehicles
        "Vehicle1": {
            "year": 2024,
            "make": "Honda",
            "model": "Civic"
        },
        "CoverageType": "full_coverage",

        # BATCH 2 - Drivers
        "PrimaryDriverAge": 22,
        "PrimaryDriverMaritalStatus": "single",
        "ZipCode": "94102"  # San Francisco
    }

    result = await _get_enhanced_quick_quote(test_data_2)
    print(f"\n{result['content'][0].text}\n")
    best = result['structured_content']['best_case_range']
    worst = result['structured_content']['worst_case_range']
    print(f"Best Case: ${best['min']:,} - ${best['max']:,} per 6 months")
    print(f"Worst Case: ${worst['min']:,} - ${worst['max']:,} per 6 months")

    # Test case 3: Two drivers (married couple), two vehicles, liability only
    print("\n" + "=" * 80)
    print("\nTest 3: Married couple (40 & 38), two vehicles, liability only")
    print("-" * 80)
    test_data_3 = {
        # BATCH 1 - Vehicles
        "Vehicle1": {
            "year": 2018,
            "make": "Toyota",
            "model": "RAV4"
        },
        "Vehicle2": {
            "year": 2019,
            "make": "Honda",
            "model": "Accord"
        },
        "CoverageType": "liability",

        # BATCH 2 - Drivers
        "PrimaryDriverAge": 40,
        "PrimaryDriverMaritalStatus": "married",
        "AdditionalDriver": {
            "age": 38,
            "marital_status": "married"
        },
        "ZipCode": "92101"  # San Diego
    }

    result = await _get_enhanced_quick_quote(test_data_3)
    print(f"\n{result['content'][0].text}\n")
    best = result['structured_content']['best_case_range']
    worst = result['structured_content']['worst_case_range']
    print(f"Best Case: ${best['min']:,} - ${best['max']:,} per 6 months")
    print(f"Worst Case: ${worst['min']:,} - ${worst['max']:,} per 6 months")

    # Test case 4: Divorced driver with older vehicle
    print("\n" + "=" * 80)
    print("\nTest 4: Divorced driver (50), older vehicle, liability only")
    print("-" * 80)
    test_data_4 = {
        # BATCH 1 - Vehicles
        "Vehicle1": {
            "year": 2012,
            "make": "Ford",
            "model": "F-150"
        },
        "CoverageType": "liability",

        # BATCH 2 - Drivers
        "PrimaryDriverAge": 50,
        "PrimaryDriverMaritalStatus": "divorced",
        "ZipCode": "95814"  # Sacramento
    }

    result = await _get_enhanced_quick_quote(test_data_4)
    print(f"\n{result['content'][0].text}\n")
    best = result['structured_content']['best_case_range']
    worst = result['structured_content']['worst_case_range']
    print(f"Best Case: ${best['min']:,} - ${best['max']:,} per 6 months")
    print(f"Worst Case: ${worst['min']:,} - ${worst['max']:,} per 6 months")

    print("\n" + "=" * 80)
    print("BATCHED QUICK QUOTE TEST COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_batched_quick_quote())
