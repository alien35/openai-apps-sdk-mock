"""Configuration Loader - Loads field and flow configs from JSON files.

This module provides a bridge between external JSON configuration files
and the Python objects used by the collection engine.

Benefits:
- Non-developers can modify flows via JSON
- Hot-reload without code changes
- Version control for configuration
- Easy A/B testing and rollbacks
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import re

from .field_registry import FieldDefinition, FieldType, FieldContext
from .flow_configs import FlowConfig, StageConfig, FlowType, StageType


# ═══════════════════════════════════════════════════════════════
# Configuration File Paths
# ═══════════════════════════════════════════════════════════════

CONFIG_DIR = Path(__file__).parent / "config"
FIELDS_CONFIG_PATH = CONFIG_DIR / "fields.json"
FLOWS_CONFIG_PATH = CONFIG_DIR / "flows.json"


# ═══════════════════════════════════════════════════════════════
# Field Registry Loader
# ═══════════════════════════════════════════════════════════════

def _create_validation_function(validation_config: Dict[str, Any]):
    """Create a validation function from JSON config.

    Args:
        validation_config: Dictionary with validation rules

    Returns:
        Validation function that returns bool
    """
    if "pattern" in validation_config:
        pattern = re.compile(validation_config["pattern"])
        return lambda v: isinstance(v, str) and pattern.match(v) is not None

    if "min" in validation_config or "max" in validation_config:
        min_val = validation_config.get("min")
        max_val = validation_config.get("max")
        return lambda v: (
            isinstance(v, int) and
            (min_val is None or v >= min_val) and
            (max_val is None or v <= max_val)
        )

    if "min_length" in validation_config or "max_length" in validation_config:
        min_len = validation_config.get("min_length")
        max_len = validation_config.get("max_length")
        return lambda v: (
            isinstance(v, str) and
            (min_len is None or len(v) >= min_len) and
            (max_len is None or len(v) <= max_len)
        )

    # Default: always valid
    return lambda v: True


def load_field_registry() -> Dict[str, FieldDefinition]:
    """Load field definitions from JSON configuration.

    Returns:
        Dictionary mapping field names to FieldDefinition objects
    """
    if not FIELDS_CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Fields configuration not found: {FIELDS_CONFIG_PATH}\n"
            "Please create insurance_server_python/config/fields.json"
        )

    with open(FIELDS_CONFIG_PATH, 'r') as f:
        config = json.load(f)

    field_registry = {}

    for field_name, field_config in config.get("fields", {}).items():
        # Parse field type
        field_type_str = field_config.get("field_type", "string")
        field_type = FieldType(field_type_str)

        # Parse contexts
        contexts = [
            FieldContext(ctx)
            for ctx in field_config.get("contexts", [])
        ]

        # Create validation function
        validation_config = field_config.get("validation", {})
        validation_fn = _create_validation_function(validation_config)

        # Create field definition
        field_def = FieldDefinition(
            name=field_config["name"],
            alias=field_config.get("alias", field_config["name"]),
            field_type=field_type,
            required=field_config.get("required", False),
            validation_fn=validation_fn,
            prompt_text=field_config.get("prompt_text", ""),
            help_text=field_config.get("help_text", ""),
            example=field_config.get("example", ""),
            contexts=contexts if contexts else [],
            depends_on=field_config.get("depends_on", []),
            group=field_config.get("group"),
            api_path=field_config.get("api_path"),
        )

        field_registry[field_name] = field_def

    return field_registry


# ═══════════════════════════════════════════════════════════════
# Flow Configuration Loader
# ═══════════════════════════════════════════════════════════════

def load_flow_configs() -> List[FlowConfig]:
    """Load flow configurations from JSON file.

    Returns:
        List of FlowConfig objects
    """
    if not FLOWS_CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Flows configuration not found: {FLOWS_CONFIG_PATH}\n"
            "Please create insurance_server_python/config/flows.json"
        )

    with open(FLOWS_CONFIG_PATH, 'r') as f:
        config = json.load(f)

    flows = []

    for flow_config in config.get("flows", []):
        # Parse flow type
        flow_type = FlowType(flow_config["flow_type"])

        # Parse stages
        stages = []
        for stage_config in flow_config.get("stages", []):
            stage_type_str = stage_config.get("stage_type", "collection")
            stage_type = StageType(stage_type_str)

            stage = StageConfig(
                name=stage_config["name"],
                fields=stage_config.get("fields", []),
                optional_fields=stage_config.get("optional_fields", []),
                description=stage_config.get("description", ""),
                stage_type=stage_type,
                allow_corrections=stage_config.get("allow_corrections", True),
            )
            stages.append(stage)

        # Create flow config
        flow = FlowConfig(
            name=flow_config["name"],
            flow_type=flow_type,
            stages=stages,
            submission_criteria=flow_config.get("submission_criteria", {}),
            metadata=flow_config.get("metadata", {}),
        )
        flows.append(flow)

    return flows


# ═══════════════════════════════════════════════════════════════
# Hot Reload Support
# ═══════════════════════════════════════════════════════════════

_cached_fields: Optional[Dict[str, FieldDefinition]] = None
_cached_flows: Optional[List[FlowConfig]] = None


def reload_config():
    """Force reload of all configuration from files.

    Call this to pick up changes to JSON files without restarting the server.
    """
    global _cached_fields, _cached_flows
    _cached_fields = None
    _cached_flows = None
    print("✓ Configuration reloaded from files")


def get_field_registry() -> Dict[str, FieldDefinition]:
    """Get field registry (cached).

    Returns:
        Dictionary mapping field names to FieldDefinition objects
    """
    global _cached_fields
    if _cached_fields is None:
        _cached_fields = load_field_registry()
    return _cached_fields


def get_flow_configs() -> List[FlowConfig]:
    """Get flow configurations (cached).

    Returns:
        List of FlowConfig objects
    """
    global _cached_flows
    if _cached_flows is None:
        _cached_flows = load_flow_configs()
    return _cached_flows


# ═══════════════════════════════════════════════════════════════
# Convenience Functions
# ═══════════════════════════════════════════════════════════════

def get_active_flow_from_config(flow_type: FlowType) -> Optional[FlowConfig]:
    """Get the active flow for a given type from config files.

    Args:
        flow_type: Type of flow to get

    Returns:
        Active FlowConfig or None if not found
    """
    flows = get_flow_configs()

    for flow in flows:
        if flow.flow_type == flow_type and flow.metadata.get("active", False):
            return flow

    return None


def list_flows_by_type_from_config(flow_type: FlowType) -> List[FlowConfig]:
    """List all flows of a given type from config files.

    Args:
        flow_type: Type of flows to list

    Returns:
        List of matching FlowConfig objects
    """
    flows = get_flow_configs()
    return [f for f in flows if f.flow_type == flow_type]


# ═══════════════════════════════════════════════════════════════
# Validation
# ═══════════════════════════════════════════════════════════════

def validate_config():
    """Validate all configuration files.

    Raises:
        ValueError: If configuration is invalid
    """
    # Load and validate fields
    fields = load_field_registry()
    print(f"✓ Loaded {len(fields)} field definitions")

    # Load and validate flows
    flows = load_flow_configs()
    print(f"✓ Loaded {len(flows)} flow configurations")

    # Validate that all fields referenced in flows exist
    for flow in flows:
        for stage in flow.stages:
            for field_name in stage.fields + stage.optional_fields:
                if field_name not in fields:
                    raise ValueError(
                        f"Flow '{flow.name}' stage '{stage.name}' references "
                        f"unknown field: '{field_name}'"
                    )

    print("✓ All flow field references are valid")

    # Check for active flows per type
    active_counts = {}
    for flow in flows:
        if flow.metadata.get("active", False):
            flow_type = flow.flow_type.value
            active_counts[flow_type] = active_counts.get(flow_type, 0) + 1

    print(f"✓ Active flows: {active_counts}")

    return True


if __name__ == "__main__":
    """Test configuration loading."""
    print("=" * 70)
    print("Configuration Validation")
    print("=" * 70)

    try:
        validate_config()
        print("\n✅ Configuration is valid!")
    except Exception as e:
        print(f"\n❌ Configuration error: {e}")
        exit(1)
