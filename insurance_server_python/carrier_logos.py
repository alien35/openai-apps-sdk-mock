"""
Carrier logo database - Base64-encoded data URIs for insurance carrier logos.

To add a new logo:
1. Place the image file in insurance_server_python/assets/images/
2. Run: python insurance_server_python/utils/image_to_base64.py insurance_server_python/assets/images/carrier_name.png
3. Copy the output into this file
4. Add an entry to CARRIER_LOGOS dictionary

Supported formats: PNG, JPG, SVG, WebP
Recommended: PNG with transparent background, max 200x100px
"""

# Default placeholder logo (generic insurance icon)
DEFAULT_LOGO = "/assets/images/mercury-logo.png"

# Individual carrier logos
# To add more carriers, use the utility script:
# python insurance_server_python/utils/image_to_base64.py path/to/logo.png

# Example carrier logos (these would be replaced with actual logos):
# MERCURY_LOGO = "data:image/png;base64,..."
# GEICO_LOGO = "data:image/png;base64,..."
# STATE_FARM_LOGO = "data:image/png;base64,..."
# PROGRESSIVE_LOGO = "data:image/png;base64,..."
# ALLSTATE_LOGO = "data:image/png;base64,..."


# Dictionary mapping carrier names to their logos
# Keys should match the carrier names returned by your rating API
CARRIER_LOGOS = {
    # Add your carriers here:
    # "Mercury Insurance": MERCURY_LOGO,
    # "GEICO": GEICO_LOGO,
    # "State Farm": STATE_FARM_LOGO,
    # "Progressive": PROGRESSIVE_LOGO,
    # "Allstate": ALLSTATE_LOGO,
}


def get_carrier_logo(carrier_name: str) -> str:
    """
    Get the logo for a carrier by name.
    Falls back to DEFAULT_LOGO if carrier not found.

    Args:
        carrier_name: Name of the insurance carrier

    Returns:
        Base64 data URI for the carrier's logo
    """
    return CARRIER_LOGOS.get(carrier_name, DEFAULT_LOGO)
