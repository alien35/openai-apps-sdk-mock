"""Insurance MCP server implemented with the Python FastMCP helper.

The server focuses exclusively on insurance workflows. It registers tools for
collecting quoting details and exposes the insurance state selector widget as a
reusable resource so the ChatGPT client can render it inline."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    TypedDict,
)
from typing import Type, cast
import inspect
import json
import logging
import os

import httpx
import mcp.types as types
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator
from starlette.requests import Request
from starlette.responses import JSONResponse
from dotenv import load_dotenv

from .insurance_state_widget import INSURANCE_STATE_WIDGET_HTML
from .insurance_quote_options_widget import (
    INSURANCE_QUOTE_OPTIONS_WIDGET_HTML,
)


logger = logging.getLogger(__name__)

load_dotenv()


@dataclass(frozen=True)
class WidgetDefinition:
    identifier: str
    title: str
    template_uri: str
    invoking: str
    invoked: str
    html: str
    response_text: str
    input_schema: Optional[Dict[str, Any]]
    tool_description: Optional[str] = None


class ToolInvocationResult(TypedDict, total=False):
    """Result structure returned by tool handlers."""

    structured_content: Dict[str, Any]
    response_text: str
    content: Sequence[types.Content]
    meta: Dict[str, Any]


ToolHandler = Callable[[Mapping[str, Any]], ToolInvocationResult | Awaitable[ToolInvocationResult]]


@dataclass(frozen=True)
class ToolRegistration:
    """Registry entry for a tool."""

    tool: types.Tool
    handler: ToolHandler
    default_response_text: str
    default_meta: Optional[Dict[str, Any]] = None


TOOL_REGISTRY: Dict[str, ToolRegistration] = {}


def register_tool(registration: ToolRegistration) -> None:
    """Register a tool so it can be listed and invoked."""

    TOOL_REGISTRY[registration.tool.name] = registration


def _model_schema(model: Type[BaseModel]) -> Dict[str, Any]:
    """Return a JSON schema for a Pydantic model using alias names."""

    return cast(Dict[str, Any], model.model_json_schema(by_alias=True))


INSURANCE_STATE_INPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "state": {
            "type": "string",
            "description": "Two-letter U.S. state or District of Columbia abbreviation (for example, \"CA\").",
            "minLength": 2,
            "maxLength": 2,
            "pattern": "^[A-Za-z]{2}$",
        }
    },
    "required": [],
    "additionalProperties": False,
}


DEFAULT_WIDGETS: Tuple[WidgetDefinition, ...] = (
    WidgetDefinition(
        identifier="insurance-state-selector",
        title="Collect insurance state",
        template_uri="ui://widget/insurance-state.html",
        invoking="Collecting a customer's state",
        invoked="Captured the customer's state",
        html=INSURANCE_STATE_WIDGET_HTML,
        response_text=
            "Let's confirm the customer's state so we can gather their driver and vehicle details for the quote.",
        input_schema=INSURANCE_STATE_INPUT_SCHEMA,
        tool_description=
            "Collects the customer's U.S. state so the assistant can continue gathering driver and vehicle information for their AIS auto quote.",
    ),
)

ADDITIONAL_WIDGETS: Tuple[WidgetDefinition, ...] = (
    WidgetDefinition(
        identifier="insurance-quote-options",
        title="Capture personal auto quote options",
        template_uri="ui://widget/insurance-quote-options.html",
        invoking="Collecting personal auto quote options",
        invoked="Captured personal auto quote options",
        html=INSURANCE_QUOTE_OPTIONS_WIDGET_HTML,
        response_text=
            "Let's review the quote details together so everything is normalized for rating.",
        input_schema=None,
        tool_description=(
            "Guides the user through selecting normalized personal auto quote options before invoking the rating flow."
        ),
    ),
)

widgets: Tuple[WidgetDefinition, ...] = DEFAULT_WIDGETS + ADDITIONAL_WIDGETS

INSURANCE_STATE_WIDGET_IDENTIFIER = "insurance-state-selector"
INSURANCE_STATE_WIDGET_TEMPLATE_URI = "ui://widget/insurance-state.html"
INSURANCE_QUOTE_OPTIONS_WIDGET_IDENTIFIER = "insurance-quote-options"
INSURANCE_QUOTE_OPTIONS_WIDGET_TEMPLATE_URI = "ui://widget/insurance-quote-options.html"


MIME_TYPE = "text/html+skybridge"


WIDGETS_BY_ID: Dict[str, WidgetDefinition] = {
    widget.identifier: widget for widget in widgets
}
WIDGETS_BY_URI: Dict[str, WidgetDefinition] = {
    widget.template_uri: widget for widget in widgets
}

if INSURANCE_STATE_WIDGET_IDENTIFIER not in WIDGETS_BY_ID:
    msg = (
        "Insurance state selector widget must be registered; "
        f"expected identifier '{INSURANCE_STATE_WIDGET_IDENTIFIER}' in widgets"
    )
    raise RuntimeError(msg)

if INSURANCE_STATE_WIDGET_TEMPLATE_URI not in WIDGETS_BY_URI:
    msg = (
        "Insurance state selector widget must expose the correct template URI; "
        f"expected '{INSURANCE_STATE_WIDGET_TEMPLATE_URI}' in widgets"
    )
    raise RuntimeError(msg)


if INSURANCE_QUOTE_OPTIONS_WIDGET_IDENTIFIER not in WIDGETS_BY_ID:
    msg = (
        "Personal auto quote options widget must be registered; "
        f"expected identifier '{INSURANCE_QUOTE_OPTIONS_WIDGET_IDENTIFIER}' in widgets"
    )
    raise RuntimeError(msg)

if INSURANCE_QUOTE_OPTIONS_WIDGET_TEMPLATE_URI not in WIDGETS_BY_URI:
    msg = (
        "Personal auto quote options widget must expose the correct template URI; "
        f"expected '{INSURANCE_QUOTE_OPTIONS_WIDGET_TEMPLATE_URI}' in widgets"
    )
    raise RuntimeError(msg)


class InsuranceStateInput(BaseModel):
    """Schema for the insurance state selector tool."""

    state: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=2,
        pattern=r"^[A-Za-z]{2}$",
        description="Two-letter U.S. state or District of Columbia abbreviation (for example, \"CA\").",
    )

    model_config = ConfigDict(extra="forbid")

    @field_validator("state", mode="before")
    @classmethod
    def _strip_state(cls, value: Optional[str]) -> Optional[str]:
        if value is None or not isinstance(value, str):
            return value
        return value.strip()

    @field_validator("state")
    @classmethod
    def _normalize_state(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        if not isinstance(value, str):
            return value
        return value.upper()


def _strip_string(value: Any) -> Any:
    if isinstance(value, str):
        return value.strip()
    return value


class AddressInput(BaseModel):
    street1: str = Field(..., alias="Street1")
    street2: Optional[str] = Field(default=None, alias="Street2")
    city: str = Field(..., alias="City")
    state: str = Field(..., alias="State", min_length=2, max_length=2)
    county: Optional[str] = Field(default=None, alias="County")
    zip_code: str = Field(..., alias="ZipCode")

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    _strip_street1 = field_validator("street1", mode="before")(_strip_string)
    _strip_street2 = field_validator("street2", mode="before")(_strip_string)
    _strip_city = field_validator("city", mode="before")(_strip_string)
    _strip_state = field_validator("state", mode="before")(_strip_string)
    _strip_county = field_validator("county", mode="before")(_strip_string)
    _strip_zip = field_validator("zip_code", mode="before")(_strip_string)

    @field_validator("state")
    @classmethod
    def _normalize_state(cls, value: str) -> str:
        return value.upper()


class ContactInformationInput(BaseModel):
    mobile_phone: Optional[str] = Field(default=None, alias="MobilePhone")
    home_phone: Optional[str] = Field(default=None, alias="HomePhone")
    work_phone: Optional[str] = Field(default=None, alias="WorkPhone")
    email_address: Optional[str] = Field(default=None, alias="EmailAddress")

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    _strip_mobile = field_validator("mobile_phone", mode="before")(_strip_string)
    _strip_home = field_validator("home_phone", mode="before")(_strip_string)
    _strip_work = field_validator("work_phone", mode="before")(_strip_string)
    _strip_email = field_validator("email_address", mode="before")(_strip_string)


class PriorInsuranceInformationInput(BaseModel):
    prior_insurance: bool = Field(alias="PriorInsurance")
    reason_for_no_insurance: Optional[str] = Field(
        default=None, alias="ReasonForNoInsurance"
    )

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    _strip_reason = field_validator(
        "reason_for_no_insurance", mode="before"
    )(_strip_string)


class CustomerProfileInput(BaseModel):
    identifier: str = Field(..., alias="Identifier")
    first_name: str = Field(..., alias="FirstName")
    middle_name: Optional[str] = Field(default=None, alias="MiddleName")
    last_name: str = Field(..., alias="LastName")
    declined_email: bool = Field(False, alias="DeclinedEmail")
    declined_phone: bool = Field(False, alias="DeclinedPhone")
    months_at_residence: Optional[int] = Field(default=None, alias="MonthsAtResidence")
    address: AddressInput = Field(..., alias="Address")
    contact_information: ContactInformationInput = Field(
        default_factory=ContactInformationInput, alias="ContactInformation"
    )
    prior_insurance_information: Optional[PriorInsuranceInformationInput] = Field(
        default=None, alias="PriorInsuranceInformation"
    )

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    _strip_identifier = field_validator("identifier", mode="before")(_strip_string)
    _strip_first = field_validator("first_name", mode="before")(_strip_string)
    _strip_middle = field_validator("middle_name", mode="before")(_strip_string)
    _strip_last = field_validator("last_name", mode="before")(_strip_string)


class LicenseInformationInput(BaseModel):
    license_number: Optional[str] = Field(default=None, alias="LicenseNumber")
    license_status: str = Field(..., alias="LicenseStatus")
    months_foreign_license: Optional[int] = Field(
        default=None, alias="MonthsForeignLicense"
    )
    months_licensed: Optional[int] = Field(default=None, alias="MonthsLicensed")
    months_state_licensed: Optional[int] = Field(
        default=None, alias="MonthsStateLicensed"
    )
    months_mvr_experience: Optional[int] = Field(
        default=None, alias="MonthsMvrExperience"
    )
    months_suspended: Optional[int] = Field(default=None, alias="MonthsSuspended")
    state_licensed: Optional[str] = Field(default=None, alias="StateLicensed")
    country_of_origin: Optional[str] = Field(default=None, alias="CountryOfOrigin")
    foreign_national: Optional[bool] = Field(default=None, alias="ForeignNational")
    international_drivers_license: Optional[bool] = Field(
        default=None, alias="InternationalDriversLicense"
    )

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    _strip_license_number = field_validator(
        "license_number", mode="before"
    )(_strip_string)
    _strip_license_status = field_validator(
        "license_status", mode="before"
    )(_strip_string)
    _strip_state_licensed = field_validator(
        "state_licensed", mode="before"
    )(_strip_string)
    _strip_country = field_validator("country_of_origin", mode="before")(_strip_string)

    @field_validator("state_licensed")
    @classmethod
    def _normalize_state(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        return value.upper()


class DriverAttributesInput(BaseModel):
    education_level: Optional[str] = Field(default=None, alias="EducationLevel")
    occasional_operator: Optional[bool] = Field(
        default=None, alias="OccasionalOperator"
    )
    property_insurance: Optional[bool] = Field(default=None, alias="PropertyInsurance")
    relation: Optional[str] = Field(default=None, alias="Relation")
    residency_status: Optional[str] = Field(default=None, alias="ResidencyStatus")
    residency_type: Optional[str] = Field(default=None, alias="ResidencyType")
    miles_to_work: Optional[int] = Field(default=None, alias="MilesToWork")

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    _strip_education = field_validator("education_level", mode="before")(_strip_string)
    _strip_relation = field_validator("relation", mode="before")(_strip_string)
    _strip_residency_status = field_validator(
        "residency_status", mode="before"
    )(_strip_string)
    _strip_residency_type = field_validator(
        "residency_type", mode="before"
    )(_strip_string)


class DriverDiscountsInput(BaseModel):
    distant_student: Optional[str] = Field(default=None, alias="DistantStudent")
    drivers_training: Optional[bool] = Field(default=None, alias="DriversTraining")
    drug_awareness: Optional[bool] = Field(default=None, alias="DrugAwareness")
    good_student: Optional[bool] = Field(default=None, alias="GoodStudent")
    single_parent: Optional[bool] = Field(default=None, alias="SingleParent")
    senior_driver_discount: Optional[bool] = Field(
        default=None, alias="SeniorDriverDiscount"
    )
    multiple_policies: Optional[bool] = Field(default=None, alias="MultiplePolicies")
    defensive_driving: Optional[bool] = Field(default=None, alias="DefensiveDriving")

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    _strip_distant = field_validator("distant_student", mode="before")(_strip_string)


class FinancialResponsibilityInformationInput(BaseModel):
    sr22: Optional[bool] = Field(default=None, alias="Sr22")
    sr22_reason: Optional[str] = Field(default=None, alias="Sr22Reason")
    sr22_state: Optional[str] = Field(default=None, alias="Sr22State")
    sr22_date: Optional[str] = Field(default=None, alias="Sr22Date")

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    _strip_reason = field_validator("sr22_reason", mode="before")(_strip_string)
    _strip_state = field_validator("sr22_state", mode="before")(_strip_string)
    _strip_date = field_validator("sr22_date", mode="before")(_strip_string)

    @field_validator("sr22_state")
    @classmethod
    def _normalize_state(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        return value.upper()


class DriverRosterEntryInput(BaseModel):
    driver_id: int = Field(..., alias="DriverId")
    first_name: str = Field(..., alias="FirstName")
    middle_name: Optional[str] = Field(default=None, alias="MiddleName")
    last_name: str = Field(..., alias="LastName")

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    _strip_first = field_validator("first_name", mode="before")(_strip_string)
    _strip_middle = field_validator("middle_name", mode="before")(_strip_string)
    _strip_last = field_validator("last_name", mode="before")(_strip_string)


class RatedDriverInput(BaseModel):
    driver_id: int = Field(..., alias="DriverId")
    first_name: str = Field(..., alias="FirstName")
    middle_name: Optional[str] = Field(default=None, alias="MiddleName")
    last_name: str = Field(..., alias="LastName")
    date_of_birth: str = Field(..., alias="DateOfBirth")
    gender: str = Field(..., alias="Gender")
    marital_status: str = Field(..., alias="MaritalStatus")
    months_employed: Optional[int] = Field(default=None, alias="MonthsEmployed")
    industry: Optional[str] = Field(default=None, alias="Industry")
    occupation: Optional[str] = Field(default=None, alias="Occupation")
    license_information: LicenseInformationInput = Field(..., alias="LicenseInformation")
    attributes: Optional[DriverAttributesInput] = Field(default=None, alias="Attributes")
    discounts: Optional[DriverDiscountsInput] = Field(default=None, alias="Discounts")
    financial_responsibility_information: Optional[
        FinancialResponsibilityInformationInput
    ] = Field(default=None, alias="FinancialResponsibilityInformation")

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    _strip_first = field_validator("first_name", mode="before")(_strip_string)
    _strip_middle = field_validator("middle_name", mode="before")(_strip_string)
    _strip_last = field_validator("last_name", mode="before")(_strip_string)
    _strip_gender = field_validator("gender", mode="before")(_strip_string)
    _strip_marital = field_validator("marital_status", mode="before")(_strip_string)
    _strip_industry = field_validator("industry", mode="before")(_strip_string)
    _strip_occupation = field_validator("occupation", mode="before")(_strip_string)


class VehicleCoverageInformationInput(BaseModel):
    collision_deductible: Optional[str] = Field(default=None, alias="CollisionDeductible")
    comprehensive_deductible: Optional[str] = Field(
        default=None, alias="ComprehensiveDeductible"
    )
    rental_limit: Optional[str] = Field(default=None, alias="RentalLimit")
    gap_coverage: Optional[bool] = Field(default=None, alias="GapCoverage")
    custom_equipment_value: Optional[int] = Field(
        default=None, alias="CustomEquipmentValue"
    )
    safety_glass_coverage: Optional[bool] = Field(
        default=None, alias="SafetyGlassCoverage"
    )
    towing_limit: Optional[str] = Field(default=None, alias="TowingLimit")

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    _strip_collision = field_validator(
        "collision_deductible", mode="before"
    )(_strip_string)
    _strip_comprehensive = field_validator(
        "comprehensive_deductible", mode="before"
    )(_strip_string)
    _strip_rental = field_validator("rental_limit", mode="before")(_strip_string)
    _strip_towing = field_validator("towing_limit", mode="before")(_strip_string)


class VehicleInput(BaseModel):
    vehicle_id: int = Field(..., alias="VehicleId")
    vin: Optional[str] = Field(default=None, alias="Vin")
    make: Optional[str] = Field(default=None, alias="Make")
    model: Optional[str] = Field(default=None, alias="Model")
    year: Optional[int] = Field(default=None, alias="Year")
    annual_miles: Optional[int] = Field(default=None, alias="AnnualMiles")
    assigned_driver_id: Optional[int] = Field(default=None, alias="AssignedDriverId")
    miles_to_work: Optional[int] = Field(default=None, alias="MilesToWork")
    odometer: Optional[int] = Field(default=None, alias="Odometer")
    leased_vehicle: Optional[bool] = Field(default=None, alias="LeasedVehicle")
    percent_to_work: Optional[int] = Field(default=None, alias="PercentToWork")
    purchase_type: Optional[str] = Field(default=None, alias="PurchaseType")
    ride_share: Optional[bool] = Field(default=None, alias="RideShare")
    salvaged: Optional[bool] = Field(default=None, alias="Salvaged")
    usage: Optional[str] = Field(default=None, alias="Usage")
    garaging_address: Optional[AddressInput] = Field(
        default=None, alias="GaragingAddress"
    )
    coverage_information: Optional[VehicleCoverageInformationInput] = Field(
        default=None, alias="CoverageInformation"
    )

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    _strip_vin = field_validator("vin", mode="before")(_strip_string)
    _strip_make = field_validator("make", mode="before")(_strip_string)
    _strip_model = field_validator("model", mode="before")(_strip_string)
    _strip_purchase_type = field_validator("purchase_type", mode="before")(
        _strip_string
    )
    _strip_usage = field_validator("usage", mode="before")(_strip_string)


class PolicyCoveragesInput(BaseModel):
    liability_bi_limit: Optional[str] = Field(default=None, alias="LiabilityBiLimit")
    liability_pd_limit: Optional[str] = Field(default=None, alias="LiabilityPdLimit")
    med_pay_limit: Optional[str] = Field(default=None, alias="MedPayLimit")
    uninsured_motorist_bi_limit: Optional[str] = Field(
        default=None, alias="UninsuredMotoristBiLimit"
    )
    accidental_death_limit: Optional[str] = Field(
        default=None, alias="AccidentalDeathLimit"
    )
    uninsured_motorist_pd_collision_damage_waiver: Optional[bool] = Field(
        default=None, alias="UninsuredMotoristPd/CollisionDamageWaiver"
    )

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    _strip_liability_bi = field_validator(
        "liability_bi_limit", mode="before"
    )(_strip_string)
    _strip_liability_pd = field_validator(
        "liability_pd_limit", mode="before"
    )(_strip_string)
    _strip_med_pay = field_validator("med_pay_limit", mode="before")(_strip_string)
    _strip_um_bi = field_validator(
        "uninsured_motorist_bi_limit", mode="before"
    )(_strip_string)
    _strip_accidental = field_validator(
        "accidental_death_limit", mode="before"
    )(_strip_string)


class CarrierProductQuestionInput(BaseModel):
    id: str = Field(..., alias="Id")
    value: str = Field(..., alias="Value")

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    _strip_id = field_validator("id", mode="before")(_strip_string)
    _strip_value = field_validator("value", mode="before")(_strip_string)


class CarrierProductInput(BaseModel):
    agency_id: Optional[str] = Field(default=None, alias="AgencyId")
    product_id: Optional[str] = Field(default=None, alias="ProductId")
    product_name: Optional[str] = Field(default=None, alias="ProductName")
    carrier_user_name: Optional[str] = Field(default=None, alias="CarrierUserName")
    carrier_password: Optional[str] = Field(default=None, alias="CarrierPassword")
    producer_code: Optional[str] = Field(default=None, alias="ProducerCode")
    carrier_login_user_name: Optional[str] = Field(
        default=None, alias="CarrierLoginUserName"
    )
    carrier_login_password: Optional[str] = Field(
        default=None, alias="CarrierLoginPassword"
    )
    carrier_id: Optional[str] = Field(default=None, alias="CarrierId")
    carrier_name: Optional[str] = Field(default=None, alias="CarrierName")
    product_questions: Optional[Dict[str, CarrierProductQuestionInput]] = Field(
        default=None, alias="ProductQuestions"
    )

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    _strip_agency = field_validator("agency_id", mode="before")(_strip_string)
    _strip_product_id = field_validator("product_id", mode="before")(_strip_string)
    _strip_product_name = field_validator("product_name", mode="before")(_strip_string)
    _strip_user = field_validator("carrier_user_name", mode="before")(_strip_string)
    _strip_password = field_validator("carrier_password", mode="before")(_strip_string)
    _strip_producer = field_validator("producer_code", mode="before")(_strip_string)
    _strip_login_user = field_validator(
        "carrier_login_user_name", mode="before"
    )(_strip_string)
    _strip_login_password = field_validator(
        "carrier_login_password", mode="before"
    )(_strip_string)
    _strip_carrier_id = field_validator("carrier_id", mode="before")(_strip_string)
    _strip_carrier_name = field_validator("carrier_name", mode="before")(_strip_string)


class CarrierInformationInput(BaseModel):
    use_exact_carrier_info: Optional[bool] = Field(
        default=None, alias="UseExactCarrierInfo"
    )
    products: List[CarrierProductInput] = Field(default_factory=list, alias="Products")

    model_config = ConfigDict(populate_by_name=True, extra="forbid")


def _default_ais_carrier_information() -> CarrierInformationInput:
    """Return the implicit AIS carrier configuration."""

    return CarrierInformationInput(
        use_exact_carrier_info=True,
        products=[
            CarrierProductInput(
                product_name="AIS",
                carrier_name="AIS",
            )
        ],
    )


class PersonalAutoCustomerIntake(BaseModel):
    customer: CustomerProfileInput = Field(..., alias="Customer")

    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class PersonalAutoDriverIntake(BaseModel):
    rated_drivers: List[RatedDriverInput] = Field(..., alias="RatedDrivers")

    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class PersonalAutoDriverRosterInput(BaseModel):
    driver_roster: List[DriverRosterEntryInput] = Field(
        ..., alias="DriverRoster"
    )

    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class PersonalAutoVehicleIntake(BaseModel):
    vehicles: List[VehicleInput] = Field(..., alias="Vehicles")

    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class PersonalAutoQuoteOptionsInput(BaseModel):
    identifier: str = Field(..., alias="Identifier")
    effective_date: str = Field(..., alias="EffectiveDate")
    customer_declined_credit: Optional[bool] = Field(
        default=None, alias="CustomerDeclinedCredit"
    )
    bump_limits: Optional[str] = Field(default=None, alias="BumpLimits")
    term: Optional[str] = Field(default=None, alias="Term")
    payment_method: Optional[str] = Field(default=None, alias="PaymentMethod")
    policy_type: Optional[str] = Field(default=None, alias="PolicyType")

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    _strip_identifier = field_validator("identifier", mode="before")(_strip_string)
    _strip_effective = field_validator("effective_date", mode="before")(_strip_string)
    _strip_bump = field_validator("bump_limits", mode="before")(_strip_string)
    _strip_term = field_validator("term", mode="before")(_strip_string)
    _strip_payment = field_validator("payment_method", mode="before")(_strip_string)
    _strip_policy_type = field_validator("policy_type", mode="before")(_strip_string)


class PersonalAutoRateRequest(BaseModel):
    identifier: str = Field(..., alias="Identifier")
    effective_date: str = Field(..., alias="EffectiveDate")
    customer_declined_credit: Optional[bool] = Field(
        default=None, alias="CustomerDeclinedCredit"
    )
    bump_limits: Optional[str] = Field(default=None, alias="BumpLimits")
    term: Optional[str] = Field(default=None, alias="Term")
    payment_method: Optional[str] = Field(default=None, alias="PaymentMethod")
    policy_type: Optional[str] = Field(default=None, alias="PolicyType")
    customer: CustomerProfileInput = Field(..., alias="Customer")
    policy_coverages: PolicyCoveragesInput = Field(
        default_factory=PolicyCoveragesInput, alias="PolicyCoverages"
    )
    rated_drivers: List[RatedDriverInput] = Field(..., alias="RatedDrivers")
    vehicles: List[VehicleInput] = Field(..., alias="Vehicles")
    carrier_information: Optional[CarrierInformationInput] = Field(
        default=None, alias="CarrierInformation"
    )

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    _strip_identifier = field_validator("identifier", mode="before")(_strip_string)
    _strip_effective = field_validator("effective_date", mode="before")(_strip_string)
    _strip_bump = field_validator("bump_limits", mode="before")(_strip_string)
    _strip_term = field_validator("term", mode="before")(_strip_string)
    _strip_payment = field_validator("payment_method", mode="before")(_strip_string)
    _strip_policy_type = field_validator("policy_type", mode="before")(_strip_string)


def _insurance_state_tool_handler(arguments: Mapping[str, Any]) -> ToolInvocationResult:
    payload = InsuranceStateInput.model_validate(arguments)
    state = payload.state
    if state:
        # State captured: return structured content but explicitly override meta
        # to suppress the widget in this response.
        return {
            "structured_content": {"state": state},
            "response_text": f"Captured {state} as the customer's state.",
            "meta": {
                # Turn off widget production for this result
                "openai/resultCanProduceWidget": False,
                "openai/widgetAccessible": False,
                # IMPORTANT: do NOT include "openai.com/widget" here
            },
        }

    # No state yet: return the widget meta so the client can render the picker
    widget = WIDGETS_BY_ID[INSURANCE_STATE_WIDGET_IDENTIFIER]
    return {
        "structured_content": {},
        "response_text": (
            "Let's confirm the customer's state so we can gather their driver and vehicle details for the quote."
        ),
        "meta": {
            **_tool_meta(widget),
            "openai.com/widget": _embedded_widget_resource(widget).model_dump(mode="json"),
        },
    }


def _collect_personal_auto_quote_options(
    arguments: Mapping[str, Any]
) -> ToolInvocationResult:
    try:
        payload = PersonalAutoQuoteOptionsInput.model_validate(arguments)
    except ValidationError as error:
        widget = WIDGETS_BY_ID[INSURANCE_QUOTE_OPTIONS_WIDGET_IDENTIFIER]
        errors = error.errors()
        message = (
            "Let's fill in the quote options using the widget so everything is normalized for the rating request."
        )
        if errors:
            first_error = errors[0]
            location = ".".join(str(part) for part in first_error.get("loc", []))
            details = first_error.get("msg")
            if location and details:
                message += f" ({location}: {details})"

        return {
            "structured_content": {"validationErrors": errors},
            "response_text": message,
            "meta": {
                **_tool_meta(widget),
                "openai.com/widget": _embedded_widget_resource(widget).model_dump(mode="json"),
            },
        }

    identifier = payload.identifier.strip()
    if identifier:
        message = f"Captured quote options for {identifier}."
    else:
        message = "Captured quote options."
    return {
        "structured_content": payload.model_dump(by_alias=True),
        "response_text": message,
        "meta": {
            "openai/resultCanProduceWidget": False,
            "openai/widgetAccessible": False,
        },
    }


def _collect_personal_auto_customer(arguments: Mapping[str, Any]) -> ToolInvocationResult:
    payload = PersonalAutoCustomerIntake.model_validate(arguments)
    customer = payload.customer
    full_name = " ".join(
        part
        for part in [customer.first_name, customer.middle_name, customer.last_name]
        if part
    )
    message = f"Captured customer profile for {full_name.strip()}.".strip()
    return {
        "structured_content": payload.model_dump(by_alias=True),
        "response_text": message,
    }


def _collect_personal_auto_driver_roster(
    arguments: Mapping[str, Any]
) -> ToolInvocationResult:
    payload = PersonalAutoDriverRosterInput.model_validate(arguments)
    entries = payload.driver_roster
    names = [
        " ".join(
            part
            for part in [entry.first_name, entry.middle_name, entry.last_name]
            if part
        )
        for entry in entries
    ]

    if not names:
        message = "Captured an empty driver roster."
    elif len(names) == 1:
        message = f"Captured driver roster entry for {names[0]}."
    else:
        listed = ", ".join(names)
        message = (
            f"Captured driver roster entries for {len(names)} drivers: {listed}."
        )

    return {
        "structured_content": payload.model_dump(by_alias=True),
        "response_text": message,
    }


def _collect_personal_auto_drivers(arguments: Mapping[str, Any]) -> ToolInvocationResult:
    payload = PersonalAutoDriverIntake.model_validate(arguments)
    driver_count = len(payload.rated_drivers)
    names = [
        " ".join(
            part
            for part in [driver.first_name, driver.middle_name, driver.last_name]
            if part
        )
        for driver in payload.rated_drivers
    ]
    if driver_count == 1:
        message = f"Captured driver profile for {names[0]}."
    else:
        listed = ", ".join(names)
        message = f"Captured driver profiles for {driver_count} drivers: {listed}."
    return {
        "structured_content": payload.model_dump(by_alias=True),
        "response_text": message,
    }


def _collect_personal_auto_vehicles(arguments: Mapping[str, Any]) -> ToolInvocationResult:
    payload = PersonalAutoVehicleIntake.model_validate(arguments)
    vehicle_count = len(payload.vehicles)
    summaries = []
    for vehicle in payload.vehicles:
        descriptor = f"{vehicle.year or ''} {vehicle.make or ''} {vehicle.model or ''}".strip()
        summaries.append(descriptor or f"Vehicle {vehicle.vehicle_id}")
    if vehicle_count == 1:
        message = f"Captured vehicle information for {summaries[0]}."
    else:
        listed = ", ".join(summaries)
        message = f"Captured vehicle information for {vehicle_count} vehicles: {listed}."
    return {
        "structured_content": payload.model_dump(by_alias=True),
        "response_text": message,
    }


PERSONAL_AUTO_RATE_ENDPOINT = (
    "https://gateway.zrater.io/api/v2/linesOfBusiness/personalAuto/states"
)

def _personal_auto_rate_headers() -> Dict[str, str]:
    api_key = os.getenv("PERSONAL_AUTO_RATE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Missing PERSONAL_AUTO_RATE_API_KEY environment variable for personal auto rate requests."
        )
    return {
        "Content-Type": "application/json",
        "User-Agent": "insomnia/11.6.1",
        "x-api-key": api_key,
    }


async def _request_personal_auto_rate(arguments: Mapping[str, Any]) -> ToolInvocationResult:
    payload = PersonalAutoRateRequest.model_validate(arguments)
    request_body = payload.model_dump(by_alias=True, exclude_none=True)
    request_body.setdefault(
        "CarrierInformation",
        _default_ais_carrier_information().model_dump(
            by_alias=True, exclude_none=True
        ),
    )
    state = payload.customer.address.state
    url = f"{PERSONAL_AUTO_RATE_ENDPOINT}/{state}/rates/latest?multiAgency=false"

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as client:
            response = await client.post(
                url,
                headers=_personal_auto_rate_headers(),
                json=request_body,
            )
    except httpx.HTTPError as exc:  # pragma: no cover - network error handling
        raise RuntimeError(f"Failed to request personal auto rate: {exc}") from exc

    status_code = response.status_code
    response_text = response.text
    parsed_response: Any = {}
    if response_text.strip():
        try:
            parsed_response = response.json()
        except (json.JSONDecodeError, ValueError) as exc:
            raise RuntimeError(
                f"Failed to parse personal auto rate response: {exc}"
            ) from exc

    if response.is_error:
        raise RuntimeError(
            f"Personal auto rate request failed with status {status_code}: {response_text}"
        )

    transaction_id = parsed_response.get("transactionId")
    message = (
        f"Received personal auto rate response (transaction {transaction_id})."
        if transaction_id
        else "Received personal auto rate response."
    )

    return {
        "structured_content": {
            "request": request_body,
            "response": parsed_response,
            "status": status_code,
        },
        "response_text": message,
    }


mcp = FastMCP(
    name="insurance-python",
    sse_path="/mcp",
    message_path="/mcp/messages",
    stateless_http=True,
)


def _resource_description(widget: WidgetDefinition) -> str:
    return f"{widget.title} widget markup"


def _tool_meta(widget: WidgetDefinition) -> Dict[str, Any]:
    return {
        "openai/outputTemplate": widget.template_uri,
        "openai/toolInvocation/invoking": widget.invoking,
        "openai/toolInvocation/invoked": widget.invoked,
        "openai/widgetAccessible": True,
        "openai/resultCanProduceWidget": True,
        "annotations": {
            "destructiveHint": False,
            "openWorldHint": False,
            "readOnlyHint": True,
        }
    }


def _embedded_widget_resource(widget: WidgetDefinition) -> types.EmbeddedResource:
    return types.EmbeddedResource(
        type="resource",
        resource=types.TextResourceContents(
            uri=widget.template_uri,
            mimeType=MIME_TYPE,
            text=widget.html,
            title=widget.title,
        ),
    )


def _register_default_tools() -> None:
    for widget in DEFAULT_WIDGETS:
        if widget.identifier in TOOL_REGISTRY:
            continue

        if widget.input_schema is None:
            msg = f"Widget '{widget.identifier}' must define an input schema to register its default tool."
            raise RuntimeError(msg)

        handler = _insurance_state_tool_handler

        meta = _tool_meta(widget)

        tool = types.Tool(
            name=widget.identifier,
            title=widget.title,
            description=widget.tool_description or widget.title,
            inputSchema=deepcopy(widget.input_schema),
            _meta=meta,
        )

        widget_resource = _embedded_widget_resource(widget)
        default_meta = {
            **meta,
            "openai.com/widget": widget_resource.model_dump(mode="json"),
        }

        register_tool(
            ToolRegistration(
                tool=tool,
                handler=handler,
                default_response_text=widget.response_text,
                default_meta=default_meta,
            )
        )

_register_default_tools()


def _register_personal_auto_intake_tools() -> None:
    register_tool(
        ToolRegistration(
            tool=types.Tool(
                name="collect-personal-auto-customer",
                title="Collect personal auto customer profile",
                description="Validate and capture the customer's personal information for a personal auto quote.",
                inputSchema=_model_schema(PersonalAutoCustomerIntake),
            ),
            handler=_collect_personal_auto_customer,
            default_response_text="Captured customer profile information.",
        )
    )

    quote_options_widget = WIDGETS_BY_ID[INSURANCE_QUOTE_OPTIONS_WIDGET_IDENTIFIER]
    quote_options_meta = _tool_meta(quote_options_widget)
    quote_options_default_meta = {
        **quote_options_meta,
        "openai.com/widget": _embedded_widget_resource(quote_options_widget).model_dump(mode="json"),
    }

    register_tool(
        ToolRegistration(
            tool=types.Tool(
                name="collect-personal-auto-quote-options",
                title="Collect personal auto quote options",
                description="Confirm quote-level options such as term, policy type, and payment method.",
                inputSchema=_model_schema(PersonalAutoQuoteOptionsInput),
                _meta=quote_options_meta,
            ),
            handler=_collect_personal_auto_quote_options,
            default_response_text="Captured personal auto quote options.",
            default_meta=quote_options_default_meta,
        )
    )

    register_tool(
        ToolRegistration(
            tool=types.Tool(
                name="collect-personal-auto-drivers",
                title="Collect personal auto driver profiles",
                description="Validate one or more rated drivers for a personal auto quote.",
                inputSchema=_model_schema(PersonalAutoDriverIntake),
            ),
            handler=_collect_personal_auto_drivers,
            default_response_text="Captured rated driver information.",
        )
    )

    register_tool(
        ToolRegistration(
            tool=types.Tool(
                name="collect-personal-auto-driver-roster",
                title="Collect personal auto driver roster",
                description=(
                    "Capture a lightweight roster of known drivers before gathering full profiles."
                ),
                inputSchema=_model_schema(PersonalAutoDriverRosterInput),
            ),
            handler=_collect_personal_auto_driver_roster,
            default_response_text="Captured driver roster entries.",
        )
    )

    register_tool(
        ToolRegistration(
            tool=types.Tool(
                name="collect-personal-auto-vehicles",
                title="Collect personal auto vehicle details",
                description="Validate the vehicles to be included on a personal auto quote.",
                inputSchema=_model_schema(PersonalAutoVehicleIntake),
            ),
            handler=_collect_personal_auto_vehicles,
            default_response_text="Captured vehicle information.",
        )
    )

    register_tool(
        ToolRegistration(
            tool=types.Tool(
                name="request-personal-auto-rate",
                title="Request personal auto rate",
                description="Submit a fully populated personal auto quote request and return the carrier response.",
                inputSchema=_model_schema(PersonalAutoRateRequest),
            ),
            handler=_request_personal_auto_rate,
            default_response_text="Submitted personal auto rating request.",
        )
    )


_register_personal_auto_intake_tools()


@mcp._mcp_server.list_tools()
async def _list_tools() -> List[types.Tool]:
    return [deepcopy(registration.tool) for registration in TOOL_REGISTRY.values()]


@mcp._mcp_server.list_resources()
async def _list_resources() -> List[types.Resource]:
    return [
        types.Resource(
            name=widget.title,
            title=widget.title,
            uri=widget.template_uri,
            description=_resource_description(widget),
            mimeType=MIME_TYPE,
            _meta=_tool_meta(widget),
        )
        for widget in widgets
    ]


@mcp._mcp_server.list_resource_templates()
async def _list_resource_templates() -> List[types.ResourceTemplate]:
    return [
        types.ResourceTemplate(
            name=widget.title,
            title=widget.title,
            uriTemplate=widget.template_uri,
            description=_resource_description(widget),
            mimeType=MIME_TYPE,
            _meta=_tool_meta(widget),
        )
        for widget in widgets
    ]


async def _handle_read_resource(req: types.ReadResourceRequest) -> types.ServerResult:
    widget = WIDGETS_BY_URI.get(str(req.params.uri))
    if widget is None:
        return types.ServerResult(
            types.ReadResourceResult(
                contents=[],
                _meta={"error": f"Unknown resource: {req.params.uri}"},
            )
        )

    contents = [
        types.TextResourceContents(
            uri=widget.template_uri,
            mimeType=MIME_TYPE,
            text=widget.html,
            _meta=_tool_meta(widget),
        )
    ]

    return types.ServerResult(types.ReadResourceResult(contents=contents))


async def _call_tool_request(req: types.CallToolRequest) -> types.ServerResult:
    registration = TOOL_REGISTRY.get(req.params.name)
    if registration is None:
        return types.ServerResult(
            types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=f"Unknown tool: {req.params.name}",
                    )
                ],
                isError=True,
            )
        )

    arguments: Mapping[str, Any] = req.params.arguments or {}

    try:
        handler_result = registration.handler(arguments)
        if inspect.isawaitable(handler_result):
            handler_result = await handler_result
    except ValidationError as exc:
        logger.exception(
            "Validation error while invoking tool '%s' with arguments %s",
            req.params.name,
            arguments,
        )
        return types.ServerResult(
            types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=f"Input validation error: {exc.errors()}",
                    )
                ],
                isError=True,
            )
        )
    except Exception as exc:  # pragma: no cover - defensive safety net
        logger.exception(
            "Unhandled exception while invoking tool '%s' with arguments %s",
            req.params.name,
            arguments,
        )
        return types.ServerResult(
            types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=f"Tool execution error: {exc}",
                    )
                ],
                isError=True,
            )
        )

    handler_payload: ToolInvocationResult = handler_result or {}
    structured_content = handler_payload.get("structured_content") or {}
    response_text = (
        handler_payload.get("response_text") or registration.default_response_text
    )
    content = handler_payload.get("content")
    if content is None:
        content = [types.TextContent(type="text", text=response_text)]
    meta = handler_payload.get("meta") or registration.default_meta

    return types.ServerResult(
        types.CallToolResult(
            content=list(content),
            structuredContent=structured_content,
            _meta=meta,
        )
    )
mcp._mcp_server.request_handlers[types.CallToolRequest] = _call_tool_request
mcp._mcp_server.request_handlers[types.ReadResourceRequest] = _handle_read_resource


app = mcp.streamable_http_app()


async def _legacy_call_tool_route(request: Request) -> JSONResponse:
    """Handle legacy ``callTool`` HTTP requests.

    Older MCP HTTP clients (including early Apps SDK builds) issue JSON-RPC
    requests using the pre-2024-10 method name ``callTool`` and expect a JSON
    response body rather than an SSE stream. The FastMCP transport now requires
    the newer ``tools/call`` method literal and enforces ``text/event-stream``
    negotiation, which causes the legacy clients to fail before the tool handler
    runs. This adapter normalizes those requests so the rest of the server can
    reuse the canonical handler logic.
    """

    try:
        payload = await request.json()
    except json.JSONDecodeError as exc:
        return JSONResponse(
            {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {exc}",
                },
            },
            status_code=400,
        )

    method = payload.get("method")
    if method != "callTool":
        return JSONResponse(
            {
                "jsonrpc": "2.0",
                "id": payload.get("id"),
                "error": {
                    "code": -32601,
                    "message": f"Unsupported method: {method}",
                },
            },
            status_code=405,
        )

    # Clone the payload but swap in the protocol-compliant method name so we
    # can delegate back to the shared handler.
    normalized_payload = {**payload, "method": "tools/call"}

    try:
        call_request = types.CallToolRequest.model_validate(normalized_payload)
    except ValidationError as exc:
        return JSONResponse(
            {
                "jsonrpc": "2.0",
                "id": payload.get("id"),
                "error": {
                    "code": -32602,
                    "message": "Invalid request parameters",
                    "data": exc.errors(),
                },
            },
            status_code=400,
        )

    server_result = await _call_tool_request(call_request)
    response_payload = server_result.model_dump(mode="json")

    # Legacy clients expect a JSON-RPC response envelope with either ``result``
    # or ``error``. ``ServerResult`` always wraps a ``CallToolResult`` so we
    # surface it as a ``result`` here.
    return JSONResponse({"jsonrpc": "2.0", "id": payload.get("id"), "result": response_payload})


app.add_route("/mcp/messages", _legacy_call_tool_route, methods=["POST"])

try:
    from starlette.middleware.cors import CORSMiddleware

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=False,
    )
except Exception:
    pass


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("insurance_server_python.main:app", host="0.0.0.0", port=8000)
