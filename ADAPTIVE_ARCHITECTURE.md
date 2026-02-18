# Adaptive Architecture: Flexible Question Flow

## Problem Statement

Insurance quote requirements change frequently:
- **Business decisions**: "Let's collect email upfront instead of later"
- **A/B testing**: "Version A asks for drivers first, Version B asks vehicles first"
- **Market changes**: "California now requires prior address for new regulation"
- **Optimization**: "Quick quote now needs credit consent, not just zip"

**Current Risk**: Hard-coded stages mean each change requires code modifications across multiple files.

**Goal**: Design an adaptable architecture where:
- Question order can change via configuration
- New fields can be added without code changes
- Stages can be reordered or combined
- Field requirements can vary by state/product

---

## Architectural Principles

### 1. Separation of Concerns

```
┌─────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                       │
│              (What to ask, in what order)                    │
│                    ↓ Configuration                           │
├─────────────────────────────────────────────────────────────┤
│                     COLLECTION LAYER                         │
│              (How to collect and validate)                   │
│                    ↓ Data Models                             │
├─────────────────────────────────────────────────────────────┤
│                     PERSISTENCE LAYER                        │
│               (Where to store partial data)                  │
│                    ↓ State Management                        │
├─────────────────────────────────────────────────────────────┤
│                     SUBMISSION LAYER                         │
│              (When and how to submit quote)                  │
└─────────────────────────────────────────────────────────────┘
```

### 2. Configuration Over Code

```python
# Bad: Hard-coded stages
def stage_1():
    collect_zip()
    collect_drivers()

# Good: Configuration-driven
STAGE_CONFIG = {
    "quick_quote": {
        "fields": ["zip_code", "number_of_drivers"],
        "optional": []
    }
}
```

### 3. Composable Field Collection

```python
# Fields are independent, composable units
collect_field("FirstName")
collect_field("ZipCode")
# Order doesn't matter to the system
```

### 4. Progressive State Building

```python
# State accumulates, order-agnostic
state = {}
state.update(collect_customer_name())    # Can happen first
state.update(collect_vehicle_vin())       # Or first
state.update(collect_driver_dob())        # Or first
# System knows when it has "enough" to proceed
```

---

## Solution: Configuration-Driven Field Collection

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     FIELD REGISTRY                              │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Field Definition: "ZipCode"                            │    │
│  │   • Type: string                                        │    │
│  │   • Validation: 5 digits                                │    │
│  │   • Prompt: "What's your zip code?"                     │    │
│  │   • Dependencies: []                                    │    │
│  │   • Context: ["location", "quick_quote"]               │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                     FLOW CONFIGURATION                          │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ Flow: "quick_quote_v2"                                 │    │
│  │   Stage 1: [ZipCode, NumberOfDrivers, EmailAddress]   │    │
│  │   Stage 2: [CustomerName, DriverDetails]              │    │
│  │   Stage 3: [VehicleInfo]                               │    │
│  │   Submit: when all required fields collected          │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                     COLLECTION ENGINE                           │
│  • Reads flow config                                            │
│  • Tracks which fields collected                                │
│  • Validates completeness                                       │
│  • Adapts to any order                                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Implementation Plan

### Phase 1: Field Registry System

Create a centralized registry of all possible fields with metadata.

#### File: `insurance_server_python/field_registry.py`

```python
"""
Field registry: Centralized definition of all collectable fields.

Benefits:
- Single source of truth for field metadata
- Easy to add/remove/modify fields
- Validation rules in one place
- Prompt text configurable
"""

from dataclasses import dataclass
from typing import List, Optional, Callable, Any
from enum import Enum


class FieldType(Enum):
    """Field data types."""
    STRING = "string"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    DATE = "date"
    ENUM = "enum"
    OBJECT = "object"
    ARRAY = "array"


class FieldContext(Enum):
    """Contexts where fields are used."""
    QUICK_QUOTE = "quick_quote"
    CUSTOMER = "customer"
    DRIVER = "driver"
    VEHICLE = "vehicle"
    POLICY = "policy"
    COVERAGE = "coverage"


@dataclass
class FieldDefinition:
    """Definition of a single field."""

    # Identity
    name: str  # e.g., "ZipCode"
    alias: str  # JSON key e.g., "ZipCode"

    # Type & Validation
    field_type: FieldType
    required: bool = False
    validation_fn: Optional[Callable[[Any], bool]] = None
    enum_values: Optional[List[str]] = None

    # User Experience
    prompt_text: str = ""  # "What's your zip code?"
    help_text: str = ""  # "This is used to determine your location"
    example: str = ""  # "94103"

    # Context & Organization
    contexts: List[FieldContext] = None
    group: Optional[str] = None  # "address", "license_info", etc.
    depends_on: List[str] = None  # Fields that must be collected first

    # API Mapping
    api_path: str = ""  # "Customer.Address.ZipCode"
    default_value: Optional[Any] = None

    def __post_init__(self):
        if self.contexts is None:
            self.contexts = []
        if self.depends_on is None:
            self.depends_on = []


# ═══════════════════════════════════════════════════════════════
# FIELD DEFINITIONS
# ═══════════════════════════════════════════════════════════════

FIELD_REGISTRY = {
    # ──────────────────────────────────────────────────────────
    # Quick Quote Fields
    # ──────────────────────────────────────────────────────────
    "ZipCode": FieldDefinition(
        name="ZipCode",
        alias="ZipCode",
        field_type=FieldType.STRING,
        required=True,
        validation_fn=lambda v: v.isdigit() and len(v) == 5,
        prompt_text="What's your zip code?",
        help_text="We use this to determine your location and applicable rates",
        example="94103",
        contexts=[FieldContext.QUICK_QUOTE, FieldContext.CUSTOMER],
        group="location",
        api_path="Customer.Address.ZipCode",
    ),

    "NumberOfDrivers": FieldDefinition(
        name="NumberOfDrivers",
        alias="NumberOfDrivers",
        field_type=FieldType.INTEGER,
        required=True,
        validation_fn=lambda v: 1 <= v <= 10,
        prompt_text="How many drivers will be on the policy?",
        help_text="Include all household members who will drive the vehicle",
        example="2",
        contexts=[FieldContext.QUICK_QUOTE],
        group="drivers",
        api_path=None,  # Not directly in API, used for quote generation
    ),

    "EmailAddress": FieldDefinition(
        name="EmailAddress",
        alias="EmailAddress",
        field_type=FieldType.STRING,
        required=False,  # Can be optional
        validation_fn=lambda v: "@" in v and "." in v,
        prompt_text="What's your email address?",
        help_text="We'll send your quote here",
        example="john@example.com",
        contexts=[FieldContext.QUICK_QUOTE, FieldContext.CUSTOMER],
        group="contact",
        api_path="Customer.ContactInformation.EmailAddress",
    ),

    # ──────────────────────────────────────────────────────────
    # Customer Fields
    # ──────────────────────────────────────────────────────────
    "FirstName": FieldDefinition(
        name="FirstName",
        alias="FirstName",
        field_type=FieldType.STRING,
        required=True,
        prompt_text="What's your first name?",
        example="John",
        contexts=[FieldContext.CUSTOMER, FieldContext.DRIVER],
        group="identity",
        api_path="Customer.FirstName",
    ),

    "LastName": FieldDefinition(
        name="LastName",
        alias="LastName",
        field_type=FieldType.STRING,
        required=True,
        prompt_text="What's your last name?",
        example="Smith",
        contexts=[FieldContext.CUSTOMER, FieldContext.DRIVER],
        group="identity",
        api_path="Customer.LastName",
    ),

    "Street1": FieldDefinition(
        name="Street1",
        alias="Street1",
        field_type=FieldType.STRING,
        required=True,
        prompt_text="What's your street address?",
        example="123 Main St",
        contexts=[FieldContext.CUSTOMER],
        group="address",
        depends_on=["ZipCode"],  # Collect zip first for context
        api_path="Customer.Address.Street1",
    ),

    "City": FieldDefinition(
        name="City",
        alias="City",
        field_type=FieldType.STRING,
        required=True,
        prompt_text="What city do you live in?",
        example="San Francisco",
        contexts=[FieldContext.CUSTOMER],
        group="address",
        depends_on=["ZipCode"],
        api_path="Customer.Address.City",
    ),

    "State": FieldDefinition(
        name="State",
        alias="State",
        field_type=FieldType.STRING,
        required=True,
        prompt_text="What state?",
        example="California",
        contexts=[FieldContext.CUSTOMER],
        group="address",
        depends_on=["ZipCode"],
        api_path="Customer.Address.State",
    ),

    "MonthsAtResidence": FieldDefinition(
        name="MonthsAtResidence",
        alias="MonthsAtResidence",
        field_type=FieldType.INTEGER,
        required=True,
        validation_fn=lambda v: v >= 0,
        prompt_text="How long have you lived at this address?",
        help_text="In months. Example: 2 years = 24 months",
        example="24",
        contexts=[FieldContext.CUSTOMER],
        group="residence",
        api_path="Customer.MonthsAtResidence",
    ),

    "PriorInsurance": FieldDefinition(
        name="PriorInsurance",
        alias="PriorInsurance",
        field_type=FieldType.BOOLEAN,
        required=True,
        prompt_text="Do you currently have auto insurance?",
        contexts=[FieldContext.CUSTOMER],
        group="insurance_history",
        api_path="Customer.PriorInsuranceInformation.PriorInsurance",
    ),

    # ──────────────────────────────────────────────────────────
    # Driver Fields
    # ──────────────────────────────────────────────────────────
    "DateOfBirth": FieldDefinition(
        name="DateOfBirth",
        alias="DateOfBirth",
        field_type=FieldType.DATE,
        required=True,
        prompt_text="What's the driver's date of birth?",
        help_text="Format: YYYY-MM-DD",
        example="1985-03-15",
        contexts=[FieldContext.DRIVER],
        group="identity",
        api_path="RatedDrivers[].DateOfBirth",
    ),

    "Gender": FieldDefinition(
        name="Gender",
        alias="Gender",
        field_type=FieldType.ENUM,
        required=True,
        enum_values=["Male", "Female"],
        prompt_text="What's the driver's gender?",
        contexts=[FieldContext.DRIVER],
        group="demographics",
        api_path="RatedDrivers[].Gender",
    ),

    "MaritalStatus": FieldDefinition(
        name="MaritalStatus",
        alias="MaritalStatus",
        field_type=FieldType.ENUM,
        required=True,
        enum_values=["Single", "Married", "Divorced", "Widowed"],
        prompt_text="What's the driver's marital status?",
        contexts=[FieldContext.DRIVER],
        group="demographics",
        api_path="RatedDrivers[].MaritalStatus",
    ),

    "LicenseStatus": FieldDefinition(
        name="LicenseStatus",
        alias="LicenseStatus",
        field_type=FieldType.ENUM,
        required=True,
        enum_values=["Valid", "Permit", "Suspended", "Revoked"],
        prompt_text="What's the status of the driver's license?",
        contexts=[FieldContext.DRIVER],
        group="license",
        api_path="RatedDrivers[].LicenseInformation.LicenseStatus",
    ),

    # ──────────────────────────────────────────────────────────
    # Vehicle Fields
    # ──────────────────────────────────────────────────────────
    "VIN": FieldDefinition(
        name="VIN",
        alias="Vin",
        field_type=FieldType.STRING,
        required=False,  # Can use Year/Make/Model instead
        validation_fn=lambda v: len(v) == 17 if v else True,
        prompt_text="What's the vehicle's VIN?",
        help_text="17-character vehicle identification number",
        example="1HGCM82633A123456",
        contexts=[FieldContext.VEHICLE],
        group="vehicle_identity",
        api_path="Vehicles[].Vin",
    ),

    "Year": FieldDefinition(
        name="Year",
        alias="Year",
        field_type=FieldType.INTEGER,
        required=True,
        validation_fn=lambda v: 1990 <= v <= 2025,
        prompt_text="What year is the vehicle?",
        example="2019",
        contexts=[FieldContext.VEHICLE],
        group="vehicle_identity",
        api_path="Vehicles[].Year",
    ),

    "Make": FieldDefinition(
        name="Make",
        alias="Make",
        field_type=FieldType.STRING,
        required=True,
        prompt_text="What make is the vehicle?",
        example="Honda",
        contexts=[FieldContext.VEHICLE],
        group="vehicle_identity",
        depends_on=["Year"],
        api_path="Vehicles[].Make",
    ),

    "Model": FieldDefinition(
        name="Model",
        alias="Model",
        field_type=FieldType.STRING,
        required=True,
        prompt_text="What model?",
        example="Accord",
        contexts=[FieldContext.VEHICLE],
        group="vehicle_identity",
        depends_on=["Year", "Make"],
        api_path="Vehicles[].Model",
    ),

    "AnnualMiles": FieldDefinition(
        name="AnnualMiles",
        alias="AnnualMiles",
        field_type=FieldType.INTEGER,
        required=True,
        validation_fn=lambda v: 0 <= v <= 100000,
        prompt_text="How many miles per year do you drive?",
        example="12000",
        contexts=[FieldContext.VEHICLE],
        group="usage",
        api_path="Vehicles[].AnnualMiles",
    ),
}


def get_field(name: str) -> Optional[FieldDefinition]:
    """Get field definition by name."""
    return FIELD_REGISTRY.get(name)


def get_fields_by_context(context: FieldContext) -> List[FieldDefinition]:
    """Get all fields for a given context."""
    return [
        field for field in FIELD_REGISTRY.values()
        if context in field.contexts
    ]


def get_required_fields(context: FieldContext) -> List[FieldDefinition]:
    """Get required fields for a context."""
    return [
        field for field in get_fields_by_context(context)
        if field.required
    ]


def validate_field_value(field_name: str, value: Any) -> tuple[bool, Optional[str]]:
    """Validate a field value.

    Returns:
        (is_valid, error_message)
    """
    field = get_field(field_name)
    if not field:
        return False, f"Unknown field: {field_name}"

    if field.required and value is None:
        return False, f"{field.name} is required"

    if field.validation_fn and not field.validation_fn(value):
        return False, f"Invalid value for {field.name}"

    if field.enum_values and value not in field.enum_values:
        return False, f"{field.name} must be one of: {', '.join(field.enum_values)}"

    return True, None
```

---

### Phase 2: Flow Configuration System

Define collection flows as JSON/YAML configuration.

#### File: `insurance_server_python/flow_configs.py`

```python
"""
Flow configurations: Define what fields to collect and in what order.

Benefits:
- Business users can modify flows without code changes
- A/B test different flows easily
- State-specific or product-specific flows
- Version control for flow changes
"""

from typing import List, Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass


class FlowType(Enum):
    """Types of collection flows."""
    QUICK_QUOTE = "quick_quote"
    DETAILED_QUOTE = "detailed_quote"
    FULL_APPLICATION = "full_application"


@dataclass
class StageConfig:
    """Configuration for a single collection stage."""
    name: str
    fields: List[str]  # Field names from registry
    optional_fields: List[str] = None
    description: str = ""

    def __post_init__(self):
        if self.optional_fields is None:
            self.optional_fields = []


@dataclass
class FlowConfig:
    """Complete flow configuration."""
    name: str
    flow_type: FlowType
    stages: List[StageConfig]
    submission_criteria: Dict[str, Any]
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


# ═══════════════════════════════════════════════════════════════
# FLOW DEFINITIONS
# ═══════════════════════════════════════════════════════════════

# ───────────────────────────────────────────────────────────────
# Version 1: Original Quick Quote (Minimal)
# ───────────────────────────────────────────────────────────────
QUICK_QUOTE_V1 = FlowConfig(
    name="quick_quote_v1",
    flow_type=FlowType.QUICK_QUOTE,
    stages=[
        StageConfig(
            name="initial",
            fields=["ZipCode", "NumberOfDrivers"],
            description="Minimal info for quote range"
        )
    ],
    submission_criteria={
        "required_fields": ["ZipCode", "NumberOfDrivers"],
        "generate_scenarios": True,
    },
    metadata={
        "version": "1.0",
        "active": False,  # Superseded by v2
    }
)

# ───────────────────────────────────────────────────────────────
# Version 2: Quick Quote with Email (Lead Capture)
# ───────────────────────────────────────────────────────────────
QUICK_QUOTE_V2 = FlowConfig(
    name="quick_quote_v2",
    flow_type=FlowType.QUICK_QUOTE,
    stages=[
        StageConfig(
            name="initial",
            fields=["ZipCode", "NumberOfDrivers", "EmailAddress"],
            optional_fields=["EmailAddress"],  # Email is optional
            description="Quick quote with optional email for follow-up"
        )
    ],
    submission_criteria={
        "required_fields": ["ZipCode", "NumberOfDrivers"],
        "generate_scenarios": True,
    },
    metadata={
        "version": "2.0",
        "active": True,  # Current version
        "ab_test": "email_capture",
    }
)

# ───────────────────────────────────────────────────────────────
# Version 3: Quick Quote with Credit Consent
# ───────────────────────────────────────────────────────────────
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
                "DateOfBirth",  # For credit check
            ],
            optional_fields=["EmailAddress"],
            description="Quick quote with credit-based pricing"
        )
    ],
    submission_criteria={
        "required_fields": ["ZipCode", "NumberOfDrivers", "FirstName", "LastName", "DateOfBirth"],
        "generate_scenarios": False,  # Use actual credit data
        "run_credit_check": True,
    },
    metadata={
        "version": "3.0",
        "active": False,  # Testing phase
        "ab_test": "credit_based_quick_quote",
    }
)

# ───────────────────────────────────────────────────────────────
# Detailed Quote Flow: Three Stages
# ───────────────────────────────────────────────────────────────
DETAILED_QUOTE_STANDARD = FlowConfig(
    name="detailed_quote_standard",
    flow_type=FlowType.DETAILED_QUOTE,
    stages=[
        StageConfig(
            name="customer",
            fields=[
                "FirstName",
                "LastName",
                "Street1",
                "City",
                "State",
                "ZipCode",
                "MonthsAtResidence",
                "PriorInsurance",
            ],
            optional_fields=["EmailAddress"],
            description="Customer profile information"
        ),
        StageConfig(
            name="drivers",
            fields=[
                "FirstName",  # Per driver
                "LastName",
                "DateOfBirth",
                "Gender",
                "MaritalStatus",
                "LicenseStatus",
            ],
            description="Driver information (repeat for each driver)"
        ),
        StageConfig(
            name="vehicles",
            fields=[
                "Year",
                "Make",
                "Model",
                "AnnualMiles",
            ],
            optional_fields=["VIN"],
            description="Vehicle information (repeat for each vehicle)"
        ),
    ],
    submission_criteria={
        "required_stages": ["customer", "drivers", "vehicles"],
        "min_drivers": 1,
        "min_vehicles": 1,
    },
    metadata={
        "version": "1.0",
        "active": True,
    }
)

# ───────────────────────────────────────────────────────────────
# California Specific: Requires Additional Info
# ───────────────────────────────────────────────────────────────
DETAILED_QUOTE_CALIFORNIA = FlowConfig(
    name="detailed_quote_california",
    flow_type=FlowType.DETAILED_QUOTE,
    stages=[
        StageConfig(
            name="customer",
            fields=[
                "FirstName",
                "LastName",
                "Street1",
                "City",
                "State",
                "ZipCode",
                "MonthsAtResidence",
                "PriorInsurance",
                "PriorAddress",  # CA requirement
            ],
            optional_fields=["EmailAddress"],
            description="Customer profile with CA requirements"
        ),
        StageConfig(
            name="drivers",
            fields=[
                "FirstName",
                "LastName",
                "DateOfBirth",
                "Gender",
                "MaritalStatus",
                "LicenseStatus",
                "GoodStudentDiscount",  # CA specific
            ],
            description="Driver information with CA discounts"
        ),
        StageConfig(
            name="vehicles",
            fields=[
                "Year",
                "Make",
                "Model",
                "AnnualMiles",
                "AntiTheftDevice",  # CA discount
            ],
            optional_fields=["VIN"],
            description="Vehicle information with CA features"
        ),
    ],
    submission_criteria={
        "required_stages": ["customer", "drivers", "vehicles"],
        "min_drivers": 1,
        "min_vehicles": 1,
        "state": "California",
    },
    metadata={
        "version": "1.0",
        "active": True,
        "state_specific": "CA",
    }
)


# ═══════════════════════════════════════════════════════════════
# FLOW REGISTRY
# ═══════════════════════════════════════════════════════════════

FLOW_REGISTRY = {
    "quick_quote_v1": QUICK_QUOTE_V1,
    "quick_quote_v2": QUICK_QUOTE_V2,
    "quick_quote_v3": QUICK_QUOTE_V3,
    "detailed_quote_standard": DETAILED_QUOTE_STANDARD,
    "detailed_quote_california": DETAILED_QUOTE_CALIFORNIA,
}


def get_flow(name: str) -> Optional[FlowConfig]:
    """Get flow configuration by name."""
    return FLOW_REGISTRY.get(name)


def get_active_flow(flow_type: FlowType, state: Optional[str] = None) -> Optional[FlowConfig]:
    """Get active flow for a type and optional state."""
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
    """Get flow for a specific A/B test."""
    for flow in FLOW_REGISTRY.values():
        if flow.metadata.get("ab_test") == test_name and flow.metadata.get("active"):
            return flow
    return None
```

---

### Phase 3: Dynamic Collection Engine

Build an engine that uses field registry + flow config to collect data in any order.

#### File: `insurance_server_python/collection_engine.py`

```python
"""
Collection Engine: Orchestrates field collection based on configuration.

Benefits:
- Order-agnostic collection
- Validates against registry
- Tracks state progressively
- Supports forward/backward compatibility
"""

from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum

from .field_registry import (
    FIELD_REGISTRY,
    FieldDefinition,
    FieldContext,
    get_field,
    validate_field_value,
)
from .flow_configs import (
    FlowConfig,
    StageConfig,
    get_active_flow,
    FlowType,
)


class CollectionStatus(Enum):
    """Status of collection process."""
    INCOMPLETE = "incomplete"
    STAGE_COMPLETE = "stage_complete"
    READY_TO_SUBMIT = "ready_to_submit"
    SUBMITTED = "submitted"


@dataclass
class CollectionState:
    """Tracks collection progress."""
    flow_name: str
    collected_fields: Dict[str, Any] = field(default_factory=dict)
    current_stage: int = 0
    status: CollectionStatus = CollectionStatus.INCOMPLETE
    missing_fields: List[str] = field(default_factory=list)
    validation_errors: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class CollectionEngine:
    """Engine for dynamic field collection."""

    def __init__(self, flow_config: FlowConfig):
        self.flow = flow_config
        self.state = CollectionState(flow_name=flow_config.name)

    def collect_fields(self, fields: Dict[str, Any]) -> CollectionState:
        """
        Collect a batch of fields.

        Order-agnostic: Fields can be provided in any order.
        Progressive: Builds on previously collected fields.
        Validating: Checks each field against registry.

        Args:
            fields: Dictionary of field_name -> value

        Returns:
            Updated collection state
        """
        # Validate and collect each field
        for field_name, value in fields.items():
            # Get field definition
            field_def = get_field(field_name)
            if not field_def:
                self.state.validation_errors[field_name] = f"Unknown field: {field_name}"
                continue

            # Validate value
            is_valid, error = validate_field_value(field_name, value)
            if not is_valid:
                self.state.validation_errors[field_name] = error
                continue

            # Check dependencies
            missing_deps = self._check_dependencies(field_def)
            if missing_deps:
                self.state.validation_errors[field_name] = (
                    f"Missing dependencies: {', '.join(missing_deps)}"
                )
                continue

            # Store field
            self.state.collected_fields[field_name] = value

            # Clear any previous errors for this field
            self.state.validation_errors.pop(field_name, None)

        # Update state
        self._update_status()

        return self.state

    def _check_dependencies(self, field_def: FieldDefinition) -> List[str]:
        """Check if field dependencies are met."""
        missing = []
        for dep in field_def.depends_on:
            if dep not in self.state.collected_fields:
                missing.append(dep)
        return missing

    def _update_status(self):
        """Update collection status based on collected fields."""
        # Get all required fields for current stage
        current_stage_config = self.flow.stages[self.state.current_stage]
        required = [
            f for f in current_stage_config.fields
            if f not in current_stage_config.optional_fields
        ]

        # Check if current stage is complete
        stage_missing = [f for f in required if f not in self.state.collected_fields]
        self.state.missing_fields = stage_missing

        if not stage_missing:
            # Current stage complete
            if self.state.current_stage < len(self.flow.stages) - 1:
                # More stages remain
                self.state.status = CollectionStatus.STAGE_COMPLETE
            else:
                # All stages complete, check submission criteria
                if self._check_submission_criteria():
                    self.state.status = CollectionStatus.READY_TO_SUBMIT
                else:
                    self.state.status = CollectionStatus.STAGE_COMPLETE
        else:
            self.state.status = CollectionStatus.INCOMPLETE

    def _check_submission_criteria(self) -> bool:
        """Check if submission criteria are met."""
        criteria = self.flow.submission_criteria

        # Check all required fields across all stages
        if "required_fields" in criteria:
            for field_name in criteria["required_fields"]:
                if field_name not in self.state.collected_fields:
                    return False

        # Check required stages
        if "required_stages" in criteria:
            # For now, assume stages completed sequentially
            if self.state.current_stage < len(self.flow.stages) - 1:
                return False

        return True

    def advance_stage(self) -> bool:
        """
        Move to next stage if current stage is complete.

        Returns:
            True if advanced, False if cannot advance
        """
        if self.state.status != CollectionStatus.STAGE_COMPLETE:
            return False

        if self.state.current_stage >= len(self.flow.stages) - 1:
            return False  # Already at last stage

        self.state.current_stage += 1
        self._update_status()
        return True

    def get_next_questions(self, limit: int = 3) -> List[FieldDefinition]:
        """
        Get the next questions to ask user.

        Smart ordering:
        - Dependencies first
        - Required before optional
        - Grouped fields together

        Args:
            limit: Max number of questions to return

        Returns:
            List of field definitions to collect next
        """
        current_stage = self.flow.stages[self.state.current_stage]
        collected = set(self.state.collected_fields.keys())

        # Get uncollected required fields
        uncollected = [
            f for f in current_stage.fields
            if f not in collected
        ]

        # Sort by dependencies and importance
        def sort_key(field_name: str) -> tuple:
            field_def = get_field(field_name)
            if not field_def:
                return (999, "")  # Unknown fields last

            # Priority: required > optional
            priority = 0 if field_def.required else 1

            # Secondary: fields with satisfied dependencies first
            unsatisfied_deps = len(self._check_dependencies(field_def))

            return (priority, unsatisfied_deps, field_def.group or "", field_name)

        uncollected.sort(key=sort_key)

        # Return field definitions
        return [
            get_field(name) for name in uncollected[:limit]
            if get_field(name) is not None
        ]

    def build_api_payload(self) -> Dict[str, Any]:
        """
        Build API payload from collected fields.

        Maps field registry names to API structure.
        """
        payload = {}

        for field_name, value in self.state.collected_fields.items():
            field_def = get_field(field_name)
            if not field_def or not field_def.api_path:
                continue

            # Parse API path (e.g., "Customer.Address.ZipCode")
            path_parts = field_def.api_path.split(".")

            # Build nested structure
            current = payload
            for part in path_parts[:-1]:
                # Handle array notation like "RatedDrivers[]"
                if part.endswith("[]"):
                    part = part[:-2]
                    if part not in current:
                        current[part] = [{}]
                    current = current[part][0]  # Use first element for now
                else:
                    if part not in current:
                        current[part] = {}
                    current = current[part]

            # Set the value
            final_key = path_parts[-1]
            current[final_key] = value

        return payload

    def get_progress(self) -> Dict[str, Any]:
        """Get collection progress summary."""
        total_fields = sum(len(stage.fields) for stage in self.flow.stages)
        collected_count = len(self.state.collected_fields)

        return {
            "flow": self.flow.name,
            "current_stage": self.state.current_stage + 1,
            "total_stages": len(self.flow.stages),
            "stage_name": self.flow.stages[self.state.current_stage].name,
            "fields_collected": collected_count,
            "total_fields": total_fields,
            "percent_complete": int((collected_count / total_fields) * 100),
            "status": self.state.status.value,
            "missing_fields": self.state.missing_fields,
            "validation_errors": self.state.validation_errors,
        }


# ═══════════════════════════════════════════════════════════════
# FACTORY FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def create_collection_engine(
    flow_type: FlowType,
    state: Optional[str] = None,
    ab_test: Optional[str] = None,
) -> Optional[CollectionEngine]:
    """
    Create a collection engine for a flow.

    Args:
        flow_type: Type of flow (quick_quote, detailed_quote, etc.)
        state: Optional state for state-specific flows
        ab_test: Optional A/B test name

    Returns:
        CollectionEngine instance or None if no matching flow
    """
    # Try A/B test first
    if ab_test:
        from .flow_configs import get_ab_test_variant
        flow = get_ab_test_variant(ab_test)
        if flow:
            return CollectionEngine(flow)

    # Get active flow for type/state
    flow = get_active_flow(flow_type, state)
    if not flow:
        return None

    return CollectionEngine(flow)
```

---

### Phase 4: Tool Integration

Update existing tools to use the collection engine.

#### File: `insurance_server_python/tool_handlers.py` (Updates)

```python
"""
Update tool handlers to use collection engine.
"""

from .collection_engine import (
    create_collection_engine,
    CollectionEngine,
    CollectionStatus,
)
from .flow_configs import FlowType


# Store engines per session (in production, use Redis/DB)
_session_engines: Dict[str, CollectionEngine] = {}


def _get_or_create_engine(
    session_id: str,
    flow_type: FlowType,
    state: Optional[str] = None,
) -> CollectionEngine:
    """Get existing engine or create new one."""
    if session_id in _session_engines:
        return _session_engines[session_id]

    engine = create_collection_engine(flow_type, state)
    _session_engines[session_id] = engine
    return engine


async def _get_quick_quote_dynamic(arguments: Mapping[str, Any]) -> ToolInvocationResult:
    """
    Dynamic quick quote using collection engine.

    Adapts to whatever flow configuration is active.
    """
    # Extract session ID (from OpenAI or generate)
    session_id = arguments.get("session_id", "default")

    # Get or create engine for quick quote flow
    engine = _get_or_create_engine(
        session_id,
        FlowType.QUICK_QUOTE,
        state=arguments.get("state"),
    )

    # Collect fields from arguments
    state = engine.collect_fields(arguments)

    # Check if we have enough to proceed
    if state.status == CollectionStatus.INCOMPLETE:
        # Need more fields
        next_questions = engine.get_next_questions(limit=3)

        questions_text = "\n".join([
            f"• {q.prompt_text}" + (f" (Example: {q.example})" if q.example else "")
            for q in next_questions
        ])

        return {
            "structured_content": state.collected_fields,
            "response_text": (
                "To get your quick quote, I need a bit more information:\n\n"
                f"{questions_text}\n\n"
                f"Progress: {engine.get_progress()['percent_complete']}% complete"
            ),
        }

    # Have enough fields - generate quote
    # ... existing quick quote logic ...

    return {
        "structured_content": {
            **state.collected_fields,
            "quote_range": "...",
        },
        "response_text": "Here's your quote range...",
    }
```

---

## Usage Examples

### Example 1: Business Changes Flow (No Code Changes!)

**Scenario**: Marketing wants to collect email in quick quote for lead nurturing.

**Solution**: Update configuration only

```python
# File: insurance_server_python/flow_configs.py
# Just change active version

QUICK_QUOTE_V1.metadata["active"] = False  # OLD
QUICK_QUOTE_V2.metadata["active"] = True   # NEW (includes email)

# Deploy - no code changes needed!
```

### Example 2: A/B Test Different Flows

```python
# Route 50% of users to email capture version
import random

if random.random() < 0.5:
    engine = create_collection_engine(
        FlowType.QUICK_QUOTE,
        ab_test="email_capture"  # Uses QUICK_QUOTE_V2
    )
else:
    engine = create_collection_engine(
        FlowType.QUICK_QUOTE,
        # Uses default active flow (V1)
    )
```

### Example 3: State-Specific Requirements

```python
# California requires additional fields
engine = create_collection_engine(
    FlowType.DETAILED_QUOTE,
    state="California"  # Automatically uses CA-specific flow
)

# Other states use standard flow
engine = create_collection_engine(
    FlowType.DETAILED_QUOTE,
    state="Texas"  # Uses standard flow
)
```

---

## Benefits Summary

| Aspect | Before (Hard-coded) | After (Configuration-driven) |
|--------|---------------------|------------------------------|
| **Add field** | Modify 3-5 files | Add to registry |
| **Change order** | Rewrite stage logic | Update config |
| **A/B test** | Deploy new code | Toggle config flag |
| **State-specific** | If/else in code | Separate config |
| **Field validation** | Scattered | Centralized in registry |
| **Prompt text** | In code | In registry |
| **Testing** | Full regression | Config unit tests |
| **Business control** | Need developers | Edit JSON/YAML |

---

## Migration Path

### Step 1: Add Registry & Configs (No Breaking Changes)
- Create `field_registry.py`
- Create `flow_configs.py`
- Define current flows as configs
- Existing tools still work

### Step 2: Build Engine (Parallel System)
- Create `collection_engine.py`
- Add new dynamic tools
- Run old and new in parallel
- Compare outputs

### Step 3: Migrate Tools (Gradual)
- Update one tool at a time
- Use engine internally
- Keep same external API
- Test thoroughly

### Step 4: Deprecate Old (When Ready)
- Remove hard-coded stages
- Keep only engine-based tools
- Update documentation

---

## Testing Strategy

```python
# Test field registry
def test_field_definition():
    field = get_field("ZipCode")
    assert field.required
    assert field.field_type == FieldType.STRING

    is_valid, _ = validate_field_value("ZipCode", "94103")
    assert is_valid

    is_valid, error = validate_field_value("ZipCode", "ABC")
    assert not is_valid

# Test flow configuration
def test_flow_selection():
    flow = get_active_flow(FlowType.QUICK_QUOTE)
    assert flow.name == "quick_quote_v2"  # Current active

    ca_flow = get_active_flow(FlowType.DETAILED_QUOTE, state="California")
    assert ca_flow.name == "detailed_quote_california"

# Test collection engine
def test_order_agnostic_collection():
    engine = create_collection_engine(FlowType.QUICK_QUOTE)

    # Collect in any order
    engine.collect_fields({"NumberOfDrivers": 2})
    engine.collect_fields({"ZipCode": "94103"})

    # Or all at once
    engine2 = create_collection_engine(FlowType.QUICK_QUOTE)
    engine2.collect_fields({
        "ZipCode": "94103",
        "NumberOfDrivers": 2,
    })

    # Both should have same result
    assert engine.state.status == engine2.state.status
```

---

## Conclusion

This adaptive architecture provides:

✅ **Configuration-driven flows** - Change question order without code
✅ **Order-agnostic collection** - Fields can be collected in any sequence
✅ **Centralized field registry** - Single source of truth
✅ **State management** - Progressive accumulation
✅ **A/B testing support** - Multiple flows in parallel
✅ **State-specific flows** - Different requirements per jurisdiction
✅ **Business control** - Non-developers can modify flows
✅ **Future-proof** - Easy to add new fields/flows

The system is now **adaptable to change** rather than **resistant to change**.
