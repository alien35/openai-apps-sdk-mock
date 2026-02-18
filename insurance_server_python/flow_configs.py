"""Flow configurations: Define what fields to collect and in what order.

This module allows business users to modify collection flows without code changes.
Supports A/B testing, state-specific flows, and version control.
"""

from typing import List, Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass, field


class FlowType(Enum):
    """Types of collection flows."""
    QUICK_QUOTE = "quick_quote"
    DETAILED_QUOTE = "detailed_quote"


class StageType(Enum):
    """Type of collection stage."""
    COLLECTION = "collection"  # Normal field collection
    REVIEW = "review"           # Review and correction stage


@dataclass
class StageConfig:
    """Configuration for a single collection stage."""
    name: str
    fields: List[str]
    optional_fields: List[str] = field(default_factory=list)
    description: str = ""
    stage_type: StageType = StageType.COLLECTION
    allow_corrections: bool = True


@dataclass
class FlowConfig:
    """Complete flow configuration."""
    name: str
    flow_type: FlowType
    stages: List[StageConfig]
    submission_criteria: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════
# Quick Quote Flow Versions
# ═══════════════════════════════════════════════════════════════

# Version 1: Minimal Quick Quote (Original)
QUICK_QUOTE_V1 = FlowConfig(
    name="quick_quote_v1",
    flow_type=FlowType.QUICK_QUOTE,
    stages=[
        StageConfig(
            name="initial",
            fields=["ZipCode", "NumberOfDrivers"],
            optional_fields=[],
            description="Minimal info for quote range"
        )
    ],
    submission_criteria={
        "required_fields": ["ZipCode", "NumberOfDrivers"],
        "generate_scenarios": True,
    },
    metadata={
        "version": "1.0",
        "active": True,
        "description": "Original minimal quick quote"
    }
)

# Version 2: Quick Quote with Email (Lead Capture)
QUICK_QUOTE_V2 = FlowConfig(
    name="quick_quote_v2",
    flow_type=FlowType.QUICK_QUOTE,
    stages=[
        StageConfig(
            name="initial",
            fields=["ZipCode", "NumberOfDrivers", "EmailAddress"],
            optional_fields=["EmailAddress"],
            description="Quick quote with optional email for follow-up"
        )
    ],
    submission_criteria={
        "required_fields": ["ZipCode", "NumberOfDrivers"],
        "generate_scenarios": True,
    },
    metadata={
        "version": "2.0",
        "active": False,
        "ab_test": "email_capture",
        "description": "Quick quote with email collection"
    }
)

# Version 3: Quick Quote with Credit Consent
QUICK_QUOTE_V3 = FlowConfig(
    name="quick_quote_v3",
    flow_type=FlowType.QUICK_QUOTE,
    stages=[
        StageConfig(
            name="initial",
            fields=[
                "ZipCode",
                "NumberOfDrivers",
                "FirstName",
                "LastName",
                "DateOfBirth",
            ],
            optional_fields=["EmailAddress"],
            description="Quick quote with credit-based pricing"
        )
    ],
    submission_criteria={
        "required_fields": ["ZipCode", "NumberOfDrivers", "FirstName", "LastName", "DateOfBirth"],
        "generate_scenarios": False,
        "run_credit_check": True,
    },
    metadata={
        "version": "3.0",
        "active": False,
        "ab_test": "credit_based_quick_quote",
        "description": "Quick quote with personal info for credit check"
    }
)


# ═══════════════════════════════════════════════════════════════
# Flow Registry
# ═══════════════════════════════════════════════════════════════

FLOW_REGISTRY = {
    "quick_quote_v1": QUICK_QUOTE_V1,
    "quick_quote_v2": QUICK_QUOTE_V2,
    "quick_quote_v3": QUICK_QUOTE_V3,
}


def get_flow(name: str) -> Optional[FlowConfig]:
    """Get flow configuration by name."""
    return FLOW_REGISTRY.get(name)


def get_active_flow(flow_type: FlowType, state: Optional[str] = None) -> Optional[FlowConfig]:
    """Get active flow for a type and optional state.

    Args:
        flow_type: Type of flow to get
        state: Optional state for state-specific flows

    Returns:
        Active flow configuration or None
    """
    candidates = [
        flow for flow in FLOW_REGISTRY.values()
        if flow.flow_type == flow_type and flow.metadata.get("active", False)
    ]

    # Prefer state-specific flows
    if state:
        state_specific = [
            flow for flow in candidates
            if flow.metadata.get("state_specific") == state
        ]
        if state_specific:
            return state_specific[0]

    # Return first active flow
    return candidates[0] if candidates else None


def get_ab_test_variant(test_name: str) -> Optional[FlowConfig]:
    """Get flow for a specific A/B test.

    Args:
        test_name: Name of the A/B test

    Returns:
        Flow configuration or None
    """
    for flow in FLOW_REGISTRY.values():
        if flow.metadata.get("ab_test") == test_name:
            return flow
    return None


def list_flows_by_type(flow_type: FlowType) -> List[FlowConfig]:
    """List all flows of a given type.

    Args:
        flow_type: Type of flow

    Returns:
        List of flow configurations
    """
    return [
        flow for flow in FLOW_REGISTRY.values()
        if flow.flow_type == flow_type
    ]
