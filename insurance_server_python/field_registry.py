"""Field registry: Centralized definition of all collectable fields.

This module provides a single source of truth for all fields that can be
collected during the insurance quote process. Each field has validation rules,
prompt text, dependencies, and API mapping information.
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


class FieldContext(Enum):
    """Contexts where fields are used."""
    QUICK_QUOTE = "quick_quote"
    CUSTOMER = "customer"
    DRIVER = "driver"
    VEHICLE = "vehicle"


@dataclass
class FieldDefinition:
    """Definition of a single collectable field."""

    # Identity
    name: str
    alias: str

    # Type & Validation
    field_type: FieldType
    required: bool = False
    validation_fn: Optional[Callable[[Any], bool]] = None
    enum_values: Optional[List[str]] = None

    # User Experience
    prompt_text: str = ""
    help_text: str = ""
    example: str = ""

    # Context & Organization
    contexts: List[FieldContext] = None
    group: Optional[str] = None
    depends_on: List[str] = None

    # API Mapping
    api_path: str = ""
    default_value: Optional[Any] = None

    def __post_init__(self):
        if self.contexts is None:
            self.contexts = []
        if self.depends_on is None:
            self.depends_on = []


# Field Registry - Quick Quote Fields
FIELD_REGISTRY = {
    "ZipCode": FieldDefinition(
        name="ZipCode",
        alias="ZipCode",
        field_type=FieldType.STRING,
        required=True,
        validation_fn=lambda v: isinstance(v, str) and v.isdigit() and len(v) == 5,
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
        validation_fn=lambda v: isinstance(v, int) and 1 <= v <= 10,
        prompt_text="How many drivers will be on the policy?",
        help_text="Include all household members who will drive the vehicle",
        example="2",
        contexts=[FieldContext.QUICK_QUOTE],
        group="drivers",
        api_path=None,  # Used for scenario generation, not directly in API
    ),

    "EmailAddress": FieldDefinition(
        name="EmailAddress",
        alias="EmailAddress",
        field_type=FieldType.STRING,
        required=False,
        validation_fn=lambda v: isinstance(v, str) and "@" in v and "." in v,
        prompt_text="What's your email address?",
        help_text="We'll send your quote here (optional)",
        example="john@example.com",
        contexts=[FieldContext.QUICK_QUOTE, FieldContext.CUSTOMER],
        group="contact",
        api_path="Customer.ContactInformation.EmailAddress",
    ),

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

    "DateOfBirth": FieldDefinition(
        name="DateOfBirth",
        alias="DateOfBirth",
        field_type=FieldType.DATE,
        required=True,
        prompt_text="What's your date of birth?",
        help_text="Format: YYYY-MM-DD",
        example="1985-03-15",
        contexts=[FieldContext.CUSTOMER],
        group="identity",
        api_path="Customer.DateOfBirth",
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

    if value is None:
        return True, None  # Optional field not provided

    if field.validation_fn and not field.validation_fn(value):
        return False, f"Invalid value for {field.name}"

    if field.enum_values and value not in field.enum_values:
        return False, f"{field.name} must be one of: {', '.join(field.enum_values)}"

    return True, None
