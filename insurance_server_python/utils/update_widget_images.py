#!/usr/bin/env python3
"""
Script to update widget_assets.py with base64 encoded images
"""
import base64
from pathlib import Path

def image_to_base64_data_uri(image_path: str) -> str:
    """Convert an image file to a base64 data URI."""
    with open(image_path, 'rb') as image_file:
        encoded = base64.b64encode(image_file.read()).decode('utf-8')
    return f'data:image/png;base64,{encoded}'

def main():
    # Get the paths
    script_dir = Path(__file__).parent
    assets_dir = script_dir.parent / 'assets' / 'images'
    output_file = script_dir.parent / 'widget_assets.py'

    # Convert images
    car_background = image_to_base64_data_uri(str(assets_dir / 'car-background.png'))
    phone_background = image_to_base64_data_uri(str(assets_dir / 'phone-background.png'))
    powered_by = image_to_base64_data_uri(str(assets_dir / 'powered-by.png'))

    # Generate the Python file
    content = f'''"""
Widget asset constants - Base64 encoded images
"""

CAR_BACKGROUND_BASE64 = "{car_background}"

PHONE_BACKGROUND_BASE64 = "{phone_background}"

POWERED_BY_LOGO_BASE64 = "{powered_by}"
'''

    # Write to file
    with open(output_file, 'w') as f:
        f.write(content)

    print(f"Successfully updated {output_file}")
    print(f"  - CAR_BACKGROUND_BASE64: {len(car_background)} bytes")
    print(f"  - PHONE_BACKGROUND_BASE64: {len(phone_background)} bytes")
    print(f"  - POWERED_BY_LOGO_BASE64: {len(powered_by)} bytes")

if __name__ == '__main__':
    main()
