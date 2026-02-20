"""State-specific carrier mapping for quick quote estimates.

Each state has a predefined set of 3 insurance carriers that are shown
to users when they request a quick quote.
"""

from typing import List, Dict, Optional

# State name to abbreviation mapping
STATE_NAME_TO_ABBR: Dict[str, str] = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR",
    "california": "CA", "colorado": "CO", "connecticut": "CT", "delaware": "DE",
    "florida": "FL", "georgia": "GA", "hawaii": "HI", "idaho": "ID",
    "illinois": "IL", "indiana": "IN", "iowa": "IA", "kansas": "KS",
    "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD",
    "massachusetts": "MA", "michigan": "MI", "minnesota": "MN", "mississippi": "MS",
    "missouri": "MO", "montana": "MT", "nebraska": "NE", "nevada": "NV",
    "new hampshire": "NH", "new jersey": "NJ", "new mexico": "NM", "new york": "NY",
    "north carolina": "NC", "north dakota": "ND", "ohio": "OH", "oklahoma": "OK",
    "oregon": "OR", "pennsylvania": "PA", "rhode island": "RI", "south carolina": "SC",
    "south dakota": "SD", "tennessee": "TN", "texas": "TX", "utah": "UT",
    "vermont": "VT", "virginia": "VA", "washington": "WA", "west virginia": "WV",
    "wisconsin": "WI", "wyoming": "WY", "district of columbia": "DC",
}

# State-specific carrier mappings (using abbreviations only)
# Each state maps to exactly 3 carriers in display order
STATE_CARRIER_MAP: Dict[str, List[str]] = {
    "CA": [
        "Orion Indemnity",
        "Mercury Auto Insurance",
        "Progressive Insurance"
    ],
    "TX": [
        "Mercury Auto Insurance",
        "Progressive Insurance",
        "State Farm"
    ],
    "FL": [
        "Progressive Insurance",
        "Mercury Auto Insurance",
        "State Farm"
    ],
    "NY": [
        "Mercury Auto Insurance",
        "State Farm",
        "Progressive Insurance"
    ],
    "IL": [
        "State Farm",
        "Mercury Auto Insurance",
        "Progressive Insurance"
    ],
    "PA": [
        "Mercury Auto Insurance",
        "Progressive Insurance",
        "State Farm"
    ],
    "OH": [
        "State Farm",
        "Progressive Insurance",
        "Mercury Auto Insurance"
    ],
    "GA": [
        "Progressive Insurance",
        "State Farm",
        "Mercury Auto Insurance"
    ],
    "NC": [
        "Mercury Auto Insurance",
        "State Farm",
        "Progressive Insurance"
    ],
    "MI": [
        "Progressive Insurance",
        "Mercury Auto Insurance",
        "State Farm"
    ],
}

# Default carriers for states not in the map
DEFAULT_CARRIERS = [
    "Mercury Auto Insurance",
    "Progressive Insurance",
    "State Farm"
]


def normalize_state(state: str) -> Optional[str]:
    """Normalize state input to standard abbreviation.

    Args:
        state: State name or abbreviation (e.g., "California", "CA", "california")

    Returns:
        Two-letter state abbreviation (e.g., "CA") or None if not found
    """
    if not state:
        return None

    # Clean input
    state_clean = state.strip()

    # Check if already a valid abbreviation
    state_upper = state_clean.upper()
    if len(state_upper) == 2 and state_upper in STATE_CARRIER_MAP:
        return state_upper

    # Try to find in full state names
    state_lower = state_clean.lower()
    if state_lower in STATE_NAME_TO_ABBR:
        return STATE_NAME_TO_ABBR[state_lower]

    # Check all valid abbreviations (including ones not in our carrier map)
    all_abbrs = set(STATE_NAME_TO_ABBR.values())
    if state_upper in all_abbrs:
        return state_upper

    return None


def get_carriers_for_state(state: str) -> List[str]:
    """Get the list of carriers for a given state.

    Args:
        state: State name or abbreviation (e.g., "California", "CA", "california")

    Returns:
        List of 3 carrier names in display order
    """
    import logging
    logger = logging.getLogger(__name__)

    # Normalize state to abbreviation
    state_abbr = normalize_state(state)
    logger.info(f"get_carriers_for_state: input='{state}', normalized='{state_abbr}'")

    # Look up carriers by abbreviation
    if state_abbr and state_abbr in STATE_CARRIER_MAP:
        carriers = STATE_CARRIER_MAP[state_abbr]
        logger.info(f"Found carriers for {state_abbr}: {carriers}")
        return carriers

    # Return default carriers if no match found
    logger.warning(f"No carriers found for state '{state}' (abbr: {state_abbr}), using defaults: {DEFAULT_CARRIERS}")
    return DEFAULT_CARRIERS


def get_carrier_display_name(carrier: str) -> str:
    """Get standardized display name for a carrier.

    Args:
        carrier: Carrier name (may be in various formats)

    Returns:
        Standardized carrier display name
    """
    carrier_lower = carrier.lower()

    if "orion" in carrier_lower:
        return "Orion Indemnity"
    elif "mercury" in carrier_lower:
        return "Mercury Auto Insurance"
    elif "progressive" in carrier_lower:
        return "Progressive Insurance"
    elif "state farm" in carrier_lower or "statefarm" in carrier_lower:
        return "State Farm"

    # Return original if no match
    return carrier
