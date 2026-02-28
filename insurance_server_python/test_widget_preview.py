#!/usr/bin/env python3
"""Quick widget preview generator for development.

Generates a standalone HTML file with mock data to preview the quote widget
without needing to run the full server or use ChatGPT.

Usage:
    python insurance_server_python/test_widget_preview.py
    # Opens preview.html in your browser
"""

import json
import os
import sys
import webbrowser
from pathlib import Path

# Add parent directory to path so we can import the widget
sys.path.insert(0, str(Path(__file__).parent.parent))

from insurance_server_python.quick_quote_results_widget import QUICK_QUOTE_RESULTS_WIDGET_HTML
from insurance_server_python.carrier_logos import get_carrier_logo


def generate_mock_data():
    """Generate mock carrier data for testing."""
    carriers = [
        {
            "name": "Mercury Auto Insurance",
            "logo": get_carrier_logo("Mercury Auto Insurance"),
            "monthly_cost": 298,
            "annual_cost": 3576,
            "range_monthly_low": 250,
            "range_monthly_high": 350,
            "range_annual_low": 3000,
            "range_annual_high": 4200,
            "confidence": "high",
            "explanations": [
                "Good driver discount applied",
                "Multi-policy savings included",
                "Based on your age group"
            ]
        },
        {
            "name": "Progressive Insurance",
            "logo": get_carrier_logo("Progressive Insurance"),
            "monthly_cost": 320,
            "annual_cost": 3840,
            "range_monthly_low": 280,
            "range_monthly_high": 370,
            "range_annual_low": 3360,
            "range_annual_high": 4440,
            "confidence": "medium",
            "explanations": [
                "Snapshot program available",
                "Name Your Price tool eligible"
            ]
        },
        {
            "name": "National General Insurance",
            "logo": get_carrier_logo("National General Insurance"),
            "monthly_cost": 317,
            "annual_cost": 3804,
            "range_monthly_low": 270,
            "range_monthly_high": 365,
            "range_annual_low": 3240,
            "range_annual_high": 4380,
            "confidence": "medium",
            "explanations": [
                "Competitive regional rates",
                "Good student discount available"
            ]
        }
    ]

    return {
        "zip_code": "93281",
        "city": "Brea",
        "state": "CA",
        "primary_driver_age": 32,
        "num_drivers": 1,
        "num_vehicles": 1,
        "carriers": carriers,
        "mercury_logo": get_carrier_logo("Mercury Auto Insurance"),
        "stage": "quick_quote_complete",
        "lookup_failed": False
    }


def generate_preview_html(output_path="preview.html"):
    """Generate a standalone HTML preview file."""
    mock_data = generate_mock_data()

    # Inject mock data into the widget HTML
    html_with_data = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Widget Preview - Quick Quote Results</title>
</head>
<body>
{QUICK_QUOTE_RESULTS_WIDGET_HTML}

<script>
// Inject mock data for testing
(function() {{
    console.log('=== MOCK DATA PREVIEW MODE ===');
    console.log('Injecting mock data...');

    const mockData = {json.dumps(mock_data, indent=2)};

    // Simulate the OpenAI globals structure
    window.openai = {{
        toolOutput: mockData,
        structured_content: mockData,
        structuredContent: mockData
    }};

    console.log('Mock data injected:', mockData);

    // Trigger the hydration
    setTimeout(() => {{
        const event = new CustomEvent('openai:set_globals', {{
            detail: {{ globals: window.openai }}
        }});
        window.dispatchEvent(event);
        console.log('Hydration triggered');
    }}, 100);
}})();
</script>

<div style="position: fixed; top: 10px; right: 10px; background: #1565c0; color: white; padding: 8px 16px; border-radius: 4px; font-family: monospace; font-size: 12px; z-index: 10000;">
    PREVIEW MODE
</div>

</body>
</html>
""".strip()

    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_with_data)

    return os.path.abspath(output_path)


def main():
    """Generate preview and open in browser."""
    print("🔧 Generating widget preview...")

    output_path = generate_preview_html()
    print(f"✓ Generated: {output_path}")

    print("\n📊 Mock Data Summary:")
    mock_data = generate_mock_data()
    print(f"  - Location: {mock_data['city']}, {mock_data['state']} {mock_data['zip_code']}")
    print(f"  - Drivers: {mock_data['num_drivers']}")
    print(f"  - Vehicles: {mock_data['num_vehicles']}")
    print(f"  - Carriers: {len(mock_data['carriers'])}")
    for i, carrier in enumerate(mock_data['carriers'], 1):
        print(f"    {i}. {carrier['name']}: ${carrier['monthly_cost']}/mo (${carrier['annual_cost']}/year)")

    print("\n🌐 Opening preview in browser...")
    try:
        webbrowser.open(f'file://{output_path}')
        print("✓ Browser opened")
    except Exception as e:
        print(f"⚠️  Could not auto-open browser: {e}")
        print(f"   Please manually open: file://{output_path}")

    print("\n✅ Preview ready!")
    print(f"\nTo regenerate: python {__file__}")
    print(f"To view: open {output_path}")


if __name__ == "__main__":
    main()
