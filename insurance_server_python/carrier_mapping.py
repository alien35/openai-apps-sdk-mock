"""State-specific carrier mapping for quick quote estimates.

Each state has a predefined set of insurance carriers that are shown
to users when they request a quick quote.
"""

from typing import List, Dict, Optional

# Carrier name constants
GEICO = "Geico"
PROGRESSIVE = "Progressive Insurance"
SAFECO = "Safeco Insurance"
MERCURY = "Mercury Auto Insurance"
NATGEN = "National General"
FOREMOST = "Foremost Insurance Group"
DAIRYLAND = "Dairyland Insurance"
CLEARCOVER = "Clearcover"
ASSURANCE_AMERICA = "Assurance America"
GAINSCO = "Gainsco"
INFINITY = "Infinity Insurance Company"
ROOT = "Root"

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
STATE_CARRIER_MAP: Dict[str, List[str]] = {
    "AL": [GEICO, PROGRESSIVE, SAFECO],
    "AK": [],
    "AZ": [GEICO, PROGRESSIVE, MERCURY],
    "AR": [GEICO, PROGRESSIVE, SAFECO],
    "CA": [PROGRESSIVE, MERCURY, NATGEN],
    "CO": [GEICO, PROGRESSIVE, SAFECO],
    "CT": [PROGRESSIVE, SAFECO, NATGEN],
    "DE": [GEICO, PROGRESSIVE, NATGEN],
    "DC": [GEICO, PROGRESSIVE],
    "FL": [GEICO, PROGRESSIVE, MERCURY],
    "GA": [GEICO, PROGRESSIVE, MERCURY],
    "HI": [],
    "ID": [GEICO, PROGRESSIVE, SAFECO],
    "IL": [GEICO, PROGRESSIVE, MERCURY],
    "IN": [GEICO, PROGRESSIVE, SAFECO],
    "IA": [GEICO, PROGRESSIVE, SAFECO],
    "KS": [GEICO, PROGRESSIVE, SAFECO],
    "KY": [GEICO, PROGRESSIVE, SAFECO],
    "LA": [GEICO, PROGRESSIVE, SAFECO],
    "ME": [GEICO, PROGRESSIVE, SAFECO],
    "MD": [GEICO, PROGRESSIVE, SAFECO],
    "MA": [],
    "MI": [PROGRESSIVE, FOREMOST],
    "MN": [PROGRESSIVE, SAFECO, FOREMOST],
    "MS": [GEICO, PROGRESSIVE, SAFECO],
    "MO": [GEICO, PROGRESSIVE, SAFECO],
    "MT": [GEICO, PROGRESSIVE, SAFECO],
    "NE": [GEICO, PROGRESSIVE, SAFECO],
    "NV": [PROGRESSIVE, MERCURY, SAFECO],
    "NH": [PROGRESSIVE, SAFECO, NATGEN],
    "NJ": [PROGRESSIVE, MERCURY, SAFECO],
    "NM": [GEICO, PROGRESSIVE, SAFECO],
    "NY": [PROGRESSIVE, MERCURY],
    "NC": [PROGRESSIVE, SAFECO, NATGEN],
    "ND": [GEICO, SAFECO],
    "OH": [GEICO, PROGRESSIVE, SAFECO],
    "OK": [GEICO, PROGRESSIVE, SAFECO],
    "OR": [GEICO, PROGRESSIVE, SAFECO],
    "PA": [PROGRESSIVE, SAFECO, NATGEN],
    "RI": [PROGRESSIVE, SAFECO, NATGEN],
    "SC": [GEICO, PROGRESSIVE, SAFECO],
    "SD": [GEICO, PROGRESSIVE, SAFECO],
    "TN": [GEICO, PROGRESSIVE, SAFECO],
    "TX": [GEICO, PROGRESSIVE, MERCURY],
    "UT": [GEICO, PROGRESSIVE, SAFECO],
    "VT": [PROGRESSIVE, SAFECO],
    "WT": [PROGRESSIVE, SAFECO, NATGEN],
    "VA": [GEICO, PROGRESSIVE, SAFECO],
    "WA": [PROGRESSIVE, SAFECO, NATGEN],
    "WV": [GEICO, PROGRESSIVE, SAFECO],
    "WI": [GEICO, PROGRESSIVE, SAFECO],
    "WY": [GEICO, PROGRESSIVE, SAFECO],
}

# Default carriers for states not in the map or with empty lists
DEFAULT_CARRIERS = [
    GEICO,
    PROGRESSIVE,
    SAFECO
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
        List of carrier names in display order (may be empty list for some states)
    """
    import logging
    logger = logging.getLogger(__name__)

    # Normalize state to abbreviation
    state_abbr = normalize_state(state)
    logger.info(f"get_carriers_for_state: input='{state}', normalized='{state_abbr}'")

    # Look up carriers by abbreviation
    if state_abbr and state_abbr in STATE_CARRIER_MAP:
        carriers = STATE_CARRIER_MAP[state_abbr]

        # If empty list, use defaults
        if not carriers:
            logger.warning(f"Empty carrier list for {state_abbr}, using defaults: {DEFAULT_CARRIERS}")
            return DEFAULT_CARRIERS

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

    # Match against known carriers
    if "geico" in carrier_lower:
        return GEICO
    elif "progressive" in carrier_lower:
        return PROGRESSIVE
    elif "safeco" in carrier_lower:
        return SAFECO
    elif "mercury" in carrier_lower:
        return MERCURY
    elif "national general" in carrier_lower or "natgen" in carrier_lower:
        return NATGEN
    elif "foremost" in carrier_lower:
        return FOREMOST
    elif "dairyland" in carrier_lower:
        return DAIRYLAND
    elif "clearcover" in carrier_lower:
        return CLEARCOVER
    elif "assurance america" in carrier_lower:
        return ASSURANCE_AMERICA
    elif "gainsco" in carrier_lower:
        return GAINSCO
    elif "infinity" in carrier_lower:
        return INFINITY
    elif "root" in carrier_lower:
        return ROOT

    # Return original if no match
    return carrier
