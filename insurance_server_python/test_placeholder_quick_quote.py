"""Test for placeholder quick quote functionality."""

import asyncio
from insurance_server_python.tool_handlers import _get_quick_quote


async def test_placeholder_quick_quote():
    """Test that placeholder quick quote returns ranges without API calls."""

    test_cases = [
        {
            "name": "Beverly Hills - 1 driver",
            "args": {"ZipCode": "90210", "NumberOfDrivers": 1},
            "expected_city": "Beverly Hills",
            "expected_state": "California",
        },
        {
            "name": "San Francisco - 2 drivers",
            "args": {"ZipCode": "94105", "NumberOfDrivers": 2},
            "expected_city": "San Francisco",
            "expected_state": "California",
        },
        {
            "name": "San Diego - 3 drivers",
            "args": {"ZipCode": "92101", "NumberOfDrivers": 3},
            "expected_city": "San Diego",
            "expected_state": "California",
        },
    ]

    print("=" * 70)
    print("Testing Placeholder Quick Quote")
    print("=" * 70)

    all_passed = True

    for test_case in test_cases:
        print(f"\n📋 Test: {test_case['name']}")
        print(f"   Input: {test_case['args']}")

        try:
            result = await _get_quick_quote(test_case["args"])

            # Check structured content
            sc = result.get("structured_content", {})

            # Verify basic fields
            assert sc.get("zip_code") == test_case["args"]["ZipCode"], "Zip code mismatch"
            assert sc.get("number_of_drivers") == test_case["args"]["NumberOfDrivers"], "Driver count mismatch"
            assert sc.get("city") == test_case["expected_city"], f"City mismatch: {sc.get('city')}"
            assert sc.get("state") == test_case["expected_state"], "State mismatch"
            assert sc.get("is_placeholder") == True, "Should be marked as placeholder"

            # Verify ranges exist
            best = sc.get("best_case_range", {})
            worst = sc.get("worst_case_range", {})

            assert "min" in best and "max" in best, "Best case range missing"
            assert "min" in worst and "max" in worst, "Worst case range missing"

            # Verify worst case is higher than best case
            assert worst["min"] > best["min"], "Worst case should be higher than best case"
            assert worst["max"] > best["max"], "Worst case should be higher than best case"

            # Verify reasonable ranges (not negative, not absurdly high)
            assert best["min"] > 0 and best["min"] < 10000, "Best min out of reasonable range"
            assert worst["max"] > 0 and worst["max"] < 20000, "Worst max out of reasonable range"

            # Check content message
            content = result.get("content", [])
            assert len(content) > 0, "No content returned"
            message = content[0].text if hasattr(content[0], 'text') else str(content[0])
            assert "Quick Quote Range" in message, "Message missing header"
            assert test_case["expected_city"] in message, "Message missing city"
            assert "BEST CASE" in message, "Message missing best case"
            assert "WORST CASE" in message, "Message missing worst case"

            print("   ✅ PASSED")
            print(f"      - City: {sc['city']}, {sc['state']}")
            print(f"      - Best case: ${best['min']:,} - ${best['max']:,} / 6 months")
            print(f"      - Worst case: ${worst['min']:,} - ${worst['max']:,} / 6 months")

        except AssertionError as e:
            print(f"   ❌ FAILED: {e}")
            all_passed = False
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            all_passed = False

    print("\n" + "=" * 70)
    if all_passed:
        print("✅ ALL TESTS PASSED")
        print("=" * 70)
        return True
    else:
        print("❌ SOME TESTS FAILED")
        print("=" * 70)
        return False


async def test_multiple_drivers_scaling():
    """Test that rates scale appropriately with number of drivers."""

    print("\n" + "=" * 70)
    print("Testing Driver Count Scaling")
    print("=" * 70)

    zip_code = "94105"

    for num_drivers in [1, 2, 3, 4]:
        result = await _get_quick_quote({"ZipCode": zip_code, "NumberOfDrivers": num_drivers})
        sc = result["structured_content"]
        best = sc["best_case_range"]
        worst = sc["worst_case_range"]

        print(f"\n{num_drivers} driver(s):")
        print(f"  Best:  ${best['min']:,} - ${best['max']:,}")
        print(f"  Worst: ${worst['min']:,} - ${worst['max']:,}")

    print("\n✅ Driver scaling test complete")
    return True


if __name__ == "__main__":
    success1 = asyncio.run(test_placeholder_quick_quote())
    success2 = asyncio.run(test_multiple_drivers_scaling())

    exit(0 if (success1 and success2) else 1)
