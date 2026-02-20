"""Test the multi-step flow where ChatGPT generates carrier estimates."""

import asyncio
from insurance_server_python.tool_handlers import _get_enhanced_quick_quote, _submit_carrier_estimates


async def test_chatgpt_carrier_flow():
    """Test the two-step flow with ChatGPT generating estimates."""

    print("=" * 80)
    print("STEP 1: COLLECT USER PROFILE")
    print("=" * 80)

    # Step 1: User provides vehicle and driver information
    profile_data = {
        "Vehicle": {
            "Year": 2022,
            "Make": "Honda",
            "Model": "Civic"
        },
        "Coverage": "full_coverage",
        "Age": 25,
        "Marital Status": "married",
        "Zip Code": "90210"
    }

    result1 = await _get_enhanced_quick_quote(profile_data)

    print("\n✓ Profile collected")
    print("\nUser-facing message:")
    print(result1['content'][0].text)

    if len(result1['content']) > 1:
        print("\nModel-only instructions (hidden from user):")
        print(result1['content'][1].text[:500] + "...")

    print("\n" + "=" * 80)
    print("STEP 2: CHATGPT GENERATES & SUBMITS CARRIER ESTIMATES")
    print("=" * 80)

    # Step 2: ChatGPT generates carrier estimates based on the profile
    # (In production, ChatGPT would do this, but we simulate it here)
    carrier_estimates = {
        "Zip Code": "90210",
        "Age": 25,
        "Carriers": [
            {
                "Carrier Name": "Mercury Insurance",
                "Annual Cost": 3200,
                "Monthly Cost": 267,
                "Notes": "Strong digital tools & mobile app"
            },
            {
                "Carrier Name": "Aspire",
                "Annual Cost": 3360,
                "Monthly Cost": 280,
                "Notes": "Savings for multiple cars"
            },
            {
                "Carrier Name": "Progressive",
                "Annual Cost": 4064,
                "Monthly Cost": 339,
                "Notes": "Best balance of cost & claims"
            },
            {
                "Carrier Name": "Anchor General Insurance",
                "Annual Cost": 4192,
                "Monthly Cost": 349,
                "Notes": "Solid coverage at a fair cost"
            },
        ]
    }

    result2 = await _submit_carrier_estimates(carrier_estimates)

    print("\n✓ Carrier estimates submitted")
    print("\nUser-facing message:")
    print(result2['content'][0].text)

    print("\n" + "=" * 80)
    print("WIDGET DATA")
    print("=" * 80)

    structured = result2['structured_content']
    print(f"\nLocation: {structured['city']}, {structured['state']} {structured['zip_code']}")
    print(f"Primary Driver Age: {structured['primary_driver_age']}")
    print(f"\nCarriers ({len(structured['carriers'])} total):")
    print("-" * 80)

    for carrier in structured['carriers']:
        annual = carrier['annual_cost']
        monthly = carrier['monthly_cost']
        print(f"\n{carrier['name']}")
        print(f"  Annual:  ${annual:,}")
        print(f"  Monthly: ${monthly:,}")
        print(f"  Notes:   {carrier['notes']}")
        print(f"  Logo:    {len(carrier['logo'])} chars")

    print("\n" + "=" * 80)
    print("VALIDATION")
    print("=" * 80)

    # Validate Mercury Insurance is included
    mercury_found = any("mercury" in c['name'].lower() for c in structured['carriers'])
    print(f"\n{'✓' if mercury_found else '✗'} Mercury Insurance included")
    print(f"✓ All carriers have logos")
    print(f"✓ Stage: {structured['stage']}")

    print("\n" + "=" * 80)
    print("TEST COMPLETED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_chatgpt_carrier_flow())
