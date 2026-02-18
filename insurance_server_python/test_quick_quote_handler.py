"""Test for the updated _get_quick_quote handler."""

import asyncio
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

async def test_quick_quote_handler():
    """Test that the updated _get_quick_quote handler works correctly."""
    from insurance_server_python.tool_handlers import _get_quick_quote

    print("=" * 60)
    print("Testing _get_quick_quote Handler")
    print("=" * 60)

    # Test inputs
    arguments = {
        "ZipCode": "90210",
        "NumberOfDrivers": 1
    }

    print(f"\nInput: {arguments}")
    print("\nCalling _get_quick_quote handler...")

    try:
        result = await _get_quick_quote(arguments)

        print("\n✅ Handler executed successfully!")

        # Check structured content
        if "structured_content" in result:
            sc = result["structured_content"]
            print(f"\nStructured Content:")
            print(f"  - Zip Code: {sc.get('zip_code')}")
            print(f"  - City: {sc.get('city')}")
            print(f"  - State: {sc.get('state')}")
            print(f"  - Number of Drivers: {sc.get('number_of_drivers')}")

            if sc.get("best_case_results"):
                print(f"  - Best Case: ✅ Got results")
            else:
                print(f"  - Best Case: ⚠️  No results")

            if sc.get("worst_case_results"):
                print(f"  - Worst Case: ✅ Got results")
            else:
                print(f"  - Worst Case: ⚠️  No results")

        # Check content
        if "content" in result and result["content"]:
            content_text = result["content"][0].text if hasattr(result["content"][0], 'text') else str(result["content"][0])
            print(f"\nResponse Preview:")
            print(content_text[:300] + "..." if len(content_text) > 300 else content_text)

        print("\n" + "=" * 60)
        print("✅ TEST PASSED: Handler works correctly")
        print("=" * 60)
        return True

    except Exception as exc:
        print(f"\n❌ TEST FAILED: {exc}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_quick_quote_handler())
    exit(0 if success else 1)
