"""Wizard Configuration Loader - Loads wizard flow config from JSON.

This module loads the wizard flow configuration and field definitions,
making them available to both backend (tool handlers) and frontend (via API).
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional


# ═══════════════════════════════════════════════════════════════
# Configuration File Paths
# ═══════════════════════════════════════════════════════════════

CONFIG_DIR = Path(__file__).parent / "config"
WIZARD_FIELDS_PATH = CONFIG_DIR / "wizard_fields.json"
WIZARD_FLOW_PATH = CONFIG_DIR / "wizard_flow.json"


# ═══════════════════════════════════════════════════════════════
# Wizard Configuration Loader
# ═══════════════════════════════════════════════════════════════

def load_wizard_fields() -> Dict[str, Any]:
    """Load wizard field definitions from JSON.

    Returns:
        Dictionary of field definitions
    """
    if not WIZARD_FIELDS_PATH.exists():
        raise FileNotFoundError(
            f"Wizard fields config not found: {WIZARD_FIELDS_PATH}"
        )

    with open(WIZARD_FIELDS_PATH, 'r') as f:
        config = json.load(f)

    return config.get("fields", {})


def load_wizard_flow() -> Dict[str, Any]:
    """Load wizard flow configuration from JSON.

    Returns:
        Wizard configuration dictionary
    """
    if not WIZARD_FLOW_PATH.exists():
        raise FileNotFoundError(
            f"Wizard flow config not found: {WIZARD_FLOW_PATH}"
        )

    with open(WIZARD_FLOW_PATH, 'r') as f:
        config = json.load(f)

    return config.get("wizard", {})


# ═══════════════════════════════════════════════════════════════
# Caching
# ═══════════════════════════════════════════════════════════════

_cached_wizard_fields: Optional[Dict[str, Any]] = None
_cached_wizard_flow: Optional[Dict[str, Any]] = None


def reload_wizard_config():
    """Force reload of wizard configuration from files."""
    global _cached_wizard_fields, _cached_wizard_flow
    _cached_wizard_fields = None
    _cached_wizard_flow = None
    print("✓ Wizard configuration reloaded")


def get_wizard_fields() -> Dict[str, Any]:
    """Get wizard fields (cached).

    Returns:
        Dictionary of field definitions
    """
    global _cached_wizard_fields
    if _cached_wizard_fields is None:
        _cached_wizard_fields = load_wizard_fields()
    return _cached_wizard_fields


def get_wizard_flow() -> Dict[str, Any]:
    """Get wizard flow configuration (cached).

    Returns:
        Wizard configuration dictionary
    """
    global _cached_wizard_flow
    if _cached_wizard_flow is None:
        _cached_wizard_flow = load_wizard_flow()
    return _cached_wizard_flow


# ═══════════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════════

def get_wizard_step(step_id: int) -> Optional[Dict[str, Any]]:
    """Get a specific wizard step by ID.

    Args:
        step_id: Step number (1-5)

    Returns:
        Step configuration or None if not found
    """
    wizard = get_wizard_flow()
    steps = wizard.get("steps", [])

    for step in steps:
        if step.get("id") == step_id:
            return step

    return None


def get_all_required_fields() -> List[str]:
    """Get list of all required field names across all steps.

    Returns:
        List of required field names
    """
    wizard = get_wizard_flow()
    return wizard.get("validation", {}).get("required_fields", [])


def get_field_definition(field_name: str) -> Optional[Dict[str, Any]]:
    """Get field definition by name.

    Args:
        field_name: Name of the field

    Returns:
        Field definition or None if not found
    """
    fields = get_wizard_fields()
    return fields.get(field_name)


def get_test_data() -> Dict[str, Any]:
    """Get test data for wizard.

    Returns:
        Dictionary of test field values
    """
    wizard = get_wizard_flow()
    test_config = wizard.get("test_data", {})

    if not test_config.get("enabled", False):
        return {}

    return test_config.get("data", {})


def build_payload_from_form_data(form_data: Dict[str, Any]) -> Dict[str, Any]:
    """Build API payload from form data using wizard config.

    Args:
        form_data: Dictionary of field_name -> value from form

    Returns:
        Structured payload ready for API submission
    """
    wizard = get_wizard_flow()
    payload_structure = wizard.get("submission", {}).get("payload_structure", {})

    # Recursively map form data to payload structure
    def map_structure(structure: Any) -> Any:
        if isinstance(structure, dict):
            result = {}
            for key, value in structure.items():
                if isinstance(value, str):
                    # This is a field reference
                    if value == "generated":
                        # Generate identifier
                        first = form_data.get("firstName", "user")
                        last = form_data.get("lastName", "quote")
                        import time
                        result[key] = f"{first[0].lower()}{last.lower()}-{int(time.time())}"
                    elif value in form_data:
                        # Map field value
                        field_value = form_data[value]
                        # Handle date conversion
                        if value in ["effectiveDate", "dateOfBirth", "sr22Date"]:
                            if field_value:
                                from datetime import datetime
                                try:
                                    dt = datetime.fromisoformat(field_value)
                                    field_value = dt.isoformat()
                                except Exception:
                                    pass
                        result[key] = field_value
                    else:
                        # Field not provided, use default or None
                        field_def = get_field_definition(value)
                        if field_def:
                            result[key] = field_def.get("default", None)
                        else:
                            result[key] = None
                else:
                    # Nested structure
                    result[key] = map_structure(value)
            return result
        elif isinstance(structure, list):
            return [map_structure(item) for item in structure]
        else:
            return structure

    payload = map_structure(payload_structure)

    # Add fixed policy coverages (not in form)
    payload["PolicyCoverages"] = {
        "LiabilityBiLimit": "30000/60000",
        "LiabilityPdLimit": "15000",
        "MedPayLimit": "None",
        "UninsuredMotoristBiLimit": "30000/60000",
        "AccidentalDeathLimit": "None",
        "UninsuredMotoristPd/CollisionDamageWaiver": False
    }

    # Add carrier information (hardcoded for now - could be config)
    payload["CarrierInformation"] = {
        "UseExactCarrierInfo": False,
        "Products": [
            {
                "AgencyId": "456494ef-0742-499c-92e0-db9fc8c78941",
                "ProductId": "9c0220c6-49c4-4358-aefc-d5bc51630fe5",
                "ProductName": "Anchor Gemini",
                "CarrierUserName": "autoinsspec",
                "CarrierPassword": "character99",
                "ProducerCode": "92000",
                "CarrierId": "0b0ab021-dd46-4d60-8cd5-e22901030008",
                "CarrierName": "Anchor General Ins"
            }
        ]
    }

    return payload


# ═══════════════════════════════════════════════════════════════
# Validation
# ═══════════════════════════════════════════════════════════════

def validate_wizard_config():
    """Validate wizard configuration files.

    Raises:
        ValueError: If configuration is invalid
    """
    # Load and validate fields
    fields = load_wizard_fields()
    print(f"✓ Loaded {len(fields)} wizard field definitions")

    # Load and validate flow
    wizard = load_wizard_flow()
    print(f"✓ Loaded wizard: {wizard.get('name')}")

    steps = wizard.get("steps", [])
    print(f"✓ Found {len(steps)} wizard steps")

    # Validate that all fields referenced in steps exist
    for step in steps:
        step_id = step.get("id")
        step_name = step.get("name")

        if step.get("is_review", False):
            # Review step
            review_sections = step.get("review_sections", [])
            for section in review_sections:
                for field_name in section.get("fields", []):
                    if field_name not in fields:
                        raise ValueError(
                            f"Step {step_id} ({step_name}) review section references "
                            f"unknown field: '{field_name}'"
                        )
        else:
            # Regular step
            sections = step.get("sections", [])
            for section in sections:
                for field_config in section.get("fields", []):
                    field_name = field_config.get("name")
                    if field_name not in fields:
                        raise ValueError(
                            f"Step {step_id} ({step_name}) section '{section.get('title')}' "
                            f"references unknown field: '{field_name}'"
                        )

    print("✓ All wizard field references are valid")

    # Validate required fields exist
    required = wizard.get("validation", {}).get("required_fields", [])
    for field_name in required:
        if field_name not in fields:
            raise ValueError(f"Required field not defined: '{field_name}'")

    print(f"✓ All {len(required)} required fields are defined")

    return True


if __name__ == "__main__":
    """Test wizard configuration loading."""
    print("=" * 70)
    print("Wizard Configuration Validation")
    print("=" * 70)

    try:
        validate_wizard_config()
        print("\n✅ Wizard configuration is valid!")
    except Exception as e:
        print(f"\n❌ Wizard configuration error: {e}")
        exit(1)
