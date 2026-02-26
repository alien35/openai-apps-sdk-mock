#!/usr/bin/env python3
"""Test early zip code validation for phone-only states."""

import asyncio
from insurance_server_python.tool_handlers import _get_enhanced_quick_quote

async def test_early_validation():
    """Test early zip code validation scenarios."""

    print("=" * 70)
    print("TEST 1: Normal state (California) - should need more info")
    print("=" * 70)

    result = await _get_enhanced_quick_quote({
        "ZIP Code": "92821"  # Brea, CA
    })

    print(f"Content: {result.get('content', [{}])[0].text if result.get('content') else 'None'}")
    print(f"Has structured_content: {bool(result.get('structured_content'))}")
    print()

    print("=" * 70)
    print("TEST 2: Phone-only state (Alaska) - should show phone widget immediately")
    print("=" * 70)

    result = await _get_enhanced_quick_quote({
        "ZIP Code": "99501"  # Anchorage, AK
    })

    content_text = result.get('content', [{}])[0].text if result.get('content') else 'None'
    print(f"Content: {content_text}")
    structured = result.get('structured_content', {})
    print(f"State: {structured.get('state')}")
    print(f"Carriers: {len(structured.get('carriers', []))}")
    print(f"Has widget meta: {bool(result.get('meta'))}")
    print()

    print("=" * 70)
    print("TEST 3: Hawaii (phone-only state)")
    print("=" * 70)

    result = await _get_enhanced_quick_quote({
        "ZIP Code": "96814"  # Honolulu, HI
    })

    content_text = result.get('content', [{}])[0].text if result.get('content') else 'None'
    print(f"Content: {content_text}")
    structured = result.get('structured_content', {})
    print(f"State: {structured.get('state')}")
    print(f"Carriers: {len(structured.get('carriers', []))}")
    print()

    print("=" * 70)
    print("TEST 4: Massachusetts (phone-only state)")
    print("=" * 70)

    result = await _get_enhanced_quick_quote({
        "ZIP Code": "02108"  # Boston, MA
    })

    content_text = result.get('content', [{}])[0].text if result.get('content') else 'None'
    print(f"Content: {content_text}")
    structured = result.get('structured_content', {})
    print(f"State: {structured.get('state')}")
    print(f"Carriers: {len(structured.get('carriers', []))}")
    print()

if __name__ == "__main__":
    asyncio.run(test_early_validation())
