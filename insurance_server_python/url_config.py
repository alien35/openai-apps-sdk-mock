"""URL configuration for external links and CTAs.

This module centralizes all external URLs used in the insurance widgets,
making them easy to update and configure.

To change the CTA URL, simply edit the values below and restart the server.
"""

# ============================================================================
# CONFIGURATION - Edit these values as needed
# ============================================================================

# Base URL where users will be redirected to complete their quote
# Change this to switch between test and production
CTA_BASE_URL = "https://tst.aisinsurance.com/auto-quote"

# Query parameters that will be appended to the URL
# These are used for tracking and attribution
CTA_PARAMS = {
    "refid5": "chatgptapp",
}

# ============================================================================
# Functions - No need to edit below this line
# ============================================================================


def get_cta_url(zip_code: str) -> str:
    """Build the complete CTA URL with all required parameters.

    Args:
        zip_code: The user's ZIP code to pre-fill

    Returns:
        Complete URL with all query parameters

    Example:
        >>> get_cta_url("90210")
        'https://tst.aisinsurance.com/auto-quote?refid5=chatgptapp&zip=90210'
    """
    # Build query parameters
    params = []

    # Add default parameters
    for key, value in CTA_PARAMS.items():
        params.append(f"{key}={value}")

    # Add zip code (required)
    params.append(f"zip={zip_code}")

    # Combine into full URL
    query_string = "&".join(params)
    return f"{CTA_BASE_URL}?{query_string}"


def get_cta_base_url() -> str:
    """Get the base CTA URL.

    Returns:
        Base URL without query parameters
    """
    return CTA_BASE_URL


def get_cta_params_json() -> dict:
    """Get CTA parameters as a JSON-serializable dict for JavaScript.

    Returns:
        Dictionary with base URL and default parameters
    """
    return {
        "base_url": CTA_BASE_URL,
        "params": CTA_PARAMS,
    }
