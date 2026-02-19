"""Pydantic models and type definitions for the insurance server."""

from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Literal,
    Mapping,
    Optional,
    Sequence,
    TypedDict,
)
from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)
import mcp.types as types

from .constants import (
    LiabilityBiLimit,
    PropertyDamageLimit,
    MedicalPaymentsLimit,
    UninsuredMotoristBiLimit,
    AccidentalDeathLimit,
    AIS_LIABILITY_BI_LIMITS,
    AIS_LIABILITY_PD_LIMITS,
    AIS_MED_PAY_LIMITS,
    AIS_UNINSURED_MOTORIST_BI_LIMITS,
    AIS_ACCIDENTAL_DEATH_LIMITS,
)


def _strip_string(value: Any) -> Any:
    if isinstance(value, str):
        return value.strip()
    return value


def _coverage_description(label: str, options: Sequence[str]) -> str:
    joined = ", ".join(options)
    return f"Use one of the AIS accepted {label} options: {joined}."


# Base input models
class InsuranceStateInput(BaseModel):
    """Schema for the insurance state selector tool."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)


class AddressInput(BaseModel):
    street1: str = Field(..., alias="Street1")
    street2: Optional[str] = Field(default=None, alias="Street2")
    city: str = Field(..., alias="City")
    state: str = Field(
        ...,
        alias="State",
        min_length=2,
        description=(
            "Full U.S. state or District of Columbia name. Abbreviations are accepted and normalized."
        ),
    )
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
        from .utils import normalize_state_name
        normalized = normalize_state_name(value)
        return normalized if isinstance(normalized, str) else value


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
    prior_insurance: bool = Field(default=False, alias="PriorInsurance")
    reason_for_no_insurance: Optional[str] = Field(
        default=None, alias="ReasonForNoInsurance"
    )

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    _strip_reason = field_validator(
        "reason_for_no_insurance", mode="before"
    )(_strip_string)

    @model_validator(mode="after")
    def _ensure_reason(self) -> "PriorInsuranceInformationInput":
        if not self.prior_insurance and not self.reason_for_no_insurance:
            self.reason_for_no_insurance = "Other"
        return self


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
        from .utils import normalize_state_name
        return normalize_state_name(value)


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


def _default_driver_attributes() -> DriverAttributesInput:
    return DriverAttributesInput(
        residency_status="Own",
        residency_type="Home",
        relation="Insured",
        occasional_operator=False,
        property_insurance=False,
    )


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
        from .utils import normalize_state_name
        return normalize_state_name(value)


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
    attributes: DriverAttributesInput = Field(
        default_factory=_default_driver_attributes, alias="Attributes"
    )
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


def _default_vehicle_coverage_information() -> VehicleCoverageInformationInput:
    return VehicleCoverageInformationInput(
        collision_deductible="None",
        comprehensive_deductible="None",
        rental_limit="None",
        towing_limit="None",
        gap_coverage=False,
        custom_equipment_value=0,
        safety_glass_coverage=False,
    )


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
    coverage_information: VehicleCoverageInformationInput = Field(
        default_factory=_default_vehicle_coverage_information,
        alias="CoverageInformation",
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
    liability_bi_limit: Optional[LiabilityBiLimit] = Field(
        default=None,
        alias="LiabilityBiLimit",
        description=_coverage_description("bodily injury liability", AIS_LIABILITY_BI_LIMITS),
    )
    liability_pd_limit: Optional[PropertyDamageLimit] = Field(
        default=None,
        alias="LiabilityPdLimit",
        description=_coverage_description("property damage liability", AIS_LIABILITY_PD_LIMITS),
    )
    med_pay_limit: Optional[MedicalPaymentsLimit] = Field(
        default=None,
        alias="MedPayLimit",
        description=_coverage_description("medical payments", AIS_MED_PAY_LIMITS),
    )
    uninsured_motorist_bi_limit: Optional[UninsuredMotoristBiLimit] = Field(
        default=None,
        alias="UninsuredMotoristBiLimit",
        description=_coverage_description(
            "uninsured motorist bodily injury", AIS_UNINSURED_MOTORIST_BI_LIMITS
        ),
    )
    accidental_death_limit: Optional[AccidentalDeathLimit] = Field(
        default=None,
        alias="AccidentalDeathLimit",
        description=_coverage_description(
            "accidental death", AIS_ACCIDENTAL_DEATH_LIMITS
        ),
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

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    _strip_identifier = field_validator("identifier", mode="before")(_strip_string)
    _strip_effective = field_validator("effective_date", mode="before")(_strip_string)
    _strip_bump = field_validator("bump_limits", mode="before")(_strip_string)
    _strip_term = field_validator("term", mode="before")(_strip_string)
    _strip_payment = field_validator("payment_method", mode="before")(_strip_string)
    _strip_policy_type = field_validator("policy_type", mode="before")(_strip_string)


class PersonalAutoRateResultsRequest(BaseModel):
    identifier: str = Field(
        ...,
        alias="Identifier",
        validation_alias=AliasChoices("Identifier", "Id"),
    )

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    _strip_identifier = field_validator("identifier", mode="before")(_strip_string)


# Cumulative intake models for conversational batch collection
# These use flexible JSON schemas that allow partial/incomplete data
class CumulativeCustomerIntake(BaseModel):
    """Cumulative intake for customer information batch."""
    customer: Optional[Dict[str, Any]] = Field(default=None, alias="Customer")

    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class CumulativeDriverIntake(BaseModel):
    """Cumulative intake for driver information batch (can append customer fields)."""
    customer: Optional[Dict[str, Any]] = Field(default=None, alias="Customer")
    rated_drivers: Optional[List[Dict[str, Any]]] = Field(default=None, alias="RatedDrivers")

    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class CumulativeVehicleIntake(BaseModel):
    """Cumulative intake for vehicle information batch (can append customer/driver fields)."""
    customer: Optional[Dict[str, Any]] = Field(default=None, alias="Customer")
    rated_drivers: Optional[List[Dict[str, Any]]] = Field(default=None, alias="RatedDrivers")
    vehicles: Optional[List[Dict[str, Any]]] = Field(default=None, alias="Vehicles")

    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class QuickQuoteIntake(BaseModel):
    """Quick quote intake for initial quote range (just zip code and number of drivers)."""
    zip_code: str = Field(
        ...,
        alias="ZipCode",
        description="5-digit zip code for the insurance quote"
    )
    number_of_drivers: int = Field(
        ...,
        alias="NumberOfDrivers",
        ge=1,
        le=10,
        description="Number of drivers (1-10)"
    )

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    _strip_zip = field_validator("zip_code", mode="before")(_strip_string)


class VehicleInfo(BaseModel):
    """Vehicle information for enhanced quick quote."""
    year: int = Field(..., ge=1900, le=2030, description="Vehicle year (1900-2030)")
    make: str = Field(..., min_length=1, description="Vehicle make (e.g., Toyota, Honda)")
    model: str = Field(..., min_length=1, description="Vehicle model (e.g., Camry, Accord)")

    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class AdditionalDriverInfo(BaseModel):
    """Additional driver information for enhanced quick quote."""
    age: int = Field(..., ge=16, le=100, description="Driver age (16-100)")
    marital_status: Literal["single", "married", "divorced", "widowed"] = Field(
        ...,
        description="Marital status of the additional driver"
    )

    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class EnhancedQuickQuoteIntake(BaseModel):
    """Enhanced quick quote with detailed information for better rate estimates."""
    zip_code: str = Field(
        ...,
        alias="ZipCode",
        description="5-digit zip code for the insurance quote"
    )
    primary_driver_age: int = Field(
        ...,
        alias="PrimaryDriverAge",
        ge=16,
        le=100,
        description="Age of the primary driver (16-100)"
    )
    vehicle_1: VehicleInfo = Field(
        ...,
        alias="Vehicle1",
        description="Primary vehicle information (year, make, model)"
    )
    vehicle_2: Optional[VehicleInfo] = Field(
        default=None,
        alias="Vehicle2",
        description="Second vehicle information (optional)"
    )
    coverage_type: Literal["liability", "full_coverage"] = Field(
        ...,
        alias="CoverageType",
        description="Coverage type: 'liability' for liability-only or 'full_coverage' for liability + comprehensive/collision"
    )
    additional_driver: Optional[AdditionalDriverInfo] = Field(
        default=None,
        alias="AdditionalDriver",
        description="Additional driver information (optional)"
    )

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    _strip_zip = field_validator("zip_code", mode="before")(_strip_string)


# TypedDicts for tool handling
class ToolInvocationResult(TypedDict, total=False):
    """Result structure returned by tool handlers."""

    structured_content: Dict[str, Any]
    response_text: str
    content: Sequence[types.TextContent]
    meta: Dict[str, Any]


ToolHandler = Callable[[Mapping[str, Any]], ToolInvocationResult | Awaitable[ToolInvocationResult]]
