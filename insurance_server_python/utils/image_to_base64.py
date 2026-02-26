#!/usr/bin/env python3
"""
Utility script to convert images to base64 data URIs for use in widgets.
This allows images to be embedded directly in MCP responses without external requests.

Usage:
    python insurance_server_python/utils/image_to_base64.py path/to/image.png

The script will output a data URI that can be used in carrier_logos.py
"""

import base64
import mimetypes
import sys
from pathlib import Path


def image_to_base64(image_path: str) -> str:
    """
    Convert an image file to a base64 data URI.

    Args:
        image_path: Path to the image file

    Returns:
        A data URI string like "data:image/png;base64,..."
    """
    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    # Detect MIME type
    mime_type, _ = mimetypes.guess_type(str(path))
    if not mime_type or not mime_type.startswith('image/'):
        raise ValueError(f"File does not appear to be an image: {image_path}")

    # Read and encode
    with open(path, 'rb') as f:
        image_data = f.read()

    base64_data = base64.b64encode(image_data).decode('utf-8')

    return f"data:{mime_type};base64,{base64_data}"


def generate_python_constant(image_path: str, constant_name: str = None) -> str:
    """
    Generate a Python constant definition for an image.

    Args:
        image_path: Path to the image file
        constant_name: Name for the Python constant (default: uppercase filename)

    Returns:
        Python code defining the constant
    """
    path = Path(image_path)

    if constant_name is None:
        # Generate constant name from filename (e.g., "mercury.png" -> "MERCURY_LOGO")
        constant_name = path.stem.upper().replace('-', '_').replace(' ', '_') + "_LOGO"

    data_uri = image_to_base64(image_path)
    file_size = len(data_uri)

    return f'''# {path.name} ({file_size:,} bytes)
{constant_name} = "{data_uri}"
'''


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python image_to_base64.py <image_path> [constant_name]")
        print("\nExample:")
        print("  python insurance_server_python/utils/image_to_base64.py assets/images/mercury.png")
        print("\nThis will output Python code you can copy into carrier_logos.py")
        sys.exit(1)

    image_path = sys.argv[1]
    constant_name = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        code = generate_python_constant(image_path, constant_name)
        print(code)
        print("\n# Add this to insurance_server_python/carrier_logos.py")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
