#!/usr/bin/env python3
"""Test the ZIP-only flow to ensure it doesn't generate a full quote prematurely."""

import sys
import asyncio
from insurance_server_python.tool_handlers import _get_enhanced_quick_quote


async def test_zip_only_rejected():
    """Test that providing only a ZIP code is rejected with error message."""
    print("=" * 80)
    print("TEST 1: ZIP code only (should be rejected)")
    print("=" * 80)

    result = await _get_enhanced_quick_quote({
        "ZIP Code": "90210"
    })

    print("\nResult keys:", result.keys())
    print("\nStructured content:", result.get("structured_content", {}))

    content = result.get("content", [])
    if content:
        print("\nText content:")
        for item in content:
            if hasattr(item, 'text'):
                preview = item.text[:300] + "..." if len(item.text) > 300 else item.text
                print(preview)

    # Verify it rejects with error message (no carriers)
    structured_content = result.get("structured_content", {})
    has_carriers = "carriers" in structured_content and len(structured_content["carriers"]) > 0

    # Check if error message mentions missing fields
    error_text = content[0].text if content and hasattr(content[0], 'text') else ""
    has_error_message = "Missing information" in error_text or "missing" in error_text.lower()

    if has_carriers:
        print("\n❌ FAIL: Generated carriers when it should reject!")
        return False
    elif has_error_message:
        print("\n✓ PASS: Rejected with error message about missing fields")
        return True
    else:
        print("\n❌ FAIL: Should have error message about missing fields")
        return False


async def test_batch1_only_rejected():
    """Test that providing only Batch 1 is rejected (needs Batch 2)."""
    print("\n" + "=" * 80)
    print("TEST 2: Complete Batch 1 only (should be rejected)")
    print("=" * 80)

    result = await _get_enhanced_quick_quote({
        "ZIP Code": "90210",
        "Number of Vehicles": 1,
        "Vehicles": [{"Year": 2020, "Make": "Honda", "Model": "Accord"}],
        "Coverage Preference": "full_coverage"
    })

    print("\nResult keys:", result.keys())
    print("\nStructured content:", result.get("structured_content", {}))

    content = result.get("content", [])
    if content:
        print("\nText content:")
        for item in content:
            if hasattr(item, 'text'):
                preview = item.text[:300] + "..." if len(item.text) > 300 else item.text
                print(preview)

    # Verify it rejects (no carriers) and mentions missing driver info
    structured_content = result.get("structured_content", {})
    has_carriers = "carriers" in structured_content and len(structured_content["carriers"]) > 0

    error_text = content[0].text if content and hasattr(content[0], 'text') else ""
    mentions_drivers = "driver" in error_text.lower()

    if has_carriers:
        print("\n❌ FAIL: Generated carriers when it should reject!")
        return False
    elif mentions_drivers:
        print("\n✓ PASS: Rejected with message about missing driver info")
        return True
    else:
        print("\n❌ FAIL: Should mention missing driver information")
        return False


async def test_complete_flow_normal_state():
    """Test that providing all required fields for normal state generates a quote."""
    print("\n" + "=" * 80)
    print("TEST 3: Complete flow - normal state (should generate quote widget)")
    print("=" * 80)

    result = await _get_enhanced_quick_quote({
        "ZIP Code": "90210",
        "Number of Vehicles": 1,
        "Vehicles": [{"Year": 2020, "Make": "Honda", "Model": "Accord"}],
        "Coverage Preference": "full_coverage",
        "Number of Drivers": 1,
        "Drivers": [{"Age": 30, "Marital Status": "married"}]
    })

    print("\nResult keys:", result.keys())
    print("\nStructured content keys:", result.get("structured_content", {}).keys())

    content = result.get("content", [])
    if content:
        print("\nText content preview:")
        for item in content[:1]:  # Just show first item
            if hasattr(item, 'text'):
                preview = item.text[:200] + "..." if len(item.text) > 200 else item.text
                print(preview)

    # Verify it generates carriers
    structured_content = result.get("structured_content", {})
    carriers = structured_content.get("carriers", [])

    if carriers and len(carriers) > 0:
        print(f"\n✓ PASS: Generated {len(carriers)} carrier quotes")
        return True
    else:
        print("\n❌ FAIL: Should have generated carrier quotes!")
        return False


async def test_complete_flow_phone_state():
    """Test that providing all required fields for phone-only state shows phone widget."""
    print("\n" + "=" * 80)
    print("TEST 4: Complete flow - phone-only state (should show phone widget)")
    print("=" * 80)

    result = await _get_enhanced_quick_quote({
        "ZIP Code": "99501",  # Anchorage, AK
        "Number of Vehicles": 1,
        "Vehicles": [{"Year": 2020, "Make": "Honda", "Model": "Accord"}],
        "Coverage Preference": "full_coverage",
        "Number of Drivers": 1,
        "Drivers": [{"Age": 30, "Marital Status": "married"}]
    })

    print("\nResult keys:", result.keys())
    print("\nStructured content:", result.get("structured_content", {}))

    content = result.get("content", [])
    if content:
        print("\nText content preview:")
        for item in content[:1]:
            if hasattr(item, 'text'):
                preview = item.text[:200] + "..." if len(item.text) > 200 else item.text
                print(preview)

    # Verify it shows phone-only widget (no carriers)
    structured_content = result.get("structured_content", {})
    has_carriers = "carriers" in structured_content and len(structured_content["carriers"]) > 0

    meta = result.get("meta", {})
    widget_uri = meta.get("openai/outputTemplate", "")

    if has_carriers:
        print("\n❌ FAIL: Should not generate carriers for phone-only state!")
        return False
    elif "phone-only" in widget_uri:
        print("\n✓ PASS: Shows phone-only widget for Alaska")
        return True
    else:
        print(f"\n❌ FAIL: Expected phone-only widget, got: {widget_uri}")
        return False


async def main():
    """Run all tests."""
    print("Testing strict two-batch flow enforcement\n")

    results = []

    results.append(await test_zip_only_rejected())
    results.append(await test_batch1_only_rejected())
    results.append(await test_complete_flow_normal_state())
    results.append(await test_complete_flow_phone_state())

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("\n✓ ALL TESTS PASSED")
        sys.exit(0)
    else:
        print(f"\n❌ {total - passed} TEST(S) FAILED")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
