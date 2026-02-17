"""Default values for optional fields in insurance quotes.

This module provides sensible defaults for all optional fields to minimize
user input while still creating valid rating requests.
"""

from typing import Any, Dict


# Customer defaults
CUSTOMER_DEFAULTS = {
    "DeclinedEmail": False,
    "DeclinedPhone": False,
    "CustomerDeclinedCredit": False,
    "NumberOfResidentsInHousehold": 1,
}

# Driver defaults
DRIVER_DEFAULTS = {
    "MiddleName": "",
    "MonthsEmployed": 0,
    "IndustryOccupation": "Other",
}

# Driver license defaults
DRIVER_LICENSE_DEFAULTS = {
    "MonthsForeignLicense": 0,
    "MonthsSuspended": 0,
    "CountryOfOrigin": "None",
    "ForeignNational": False,
    "InternationalDriversLicense": False,
}

# Driver attributes defaults
DRIVER_ATTRIBUTES_DEFAULTS = {
    "EducationLevel": "High School Diploma",
    "OccasionalOperator": False,
    "MilesToWork": 0,
    "AnnualMiles": 0,
}

# Driver discounts defaults
DRIVER_DISCOUNTS_DEFAULTS = {
    "CompanionPolicies": [],
    "DistantStudent": "None",
    "DriversTraining": False,
    "GoodStudent": False,
    "SingleParent": False,
    "AccidentPrevention": False,
    "SeniorDriverDiscount": False,
    "MultiplePolicies": False,
}

# Driver financial responsibility defaults
FINANCIAL_RESPONSIBILITY_DEFAULTS = {
    "Sr22": False,
    "Sr1P": False,
}

# Driver violations default (empty list)
DRIVER_VIOLATIONS_DEFAULT = []

# Vehicle defaults
VEHICLE_DEFAULTS = {
    "CustomEquipmentValue": 0,
    "GrayMarket": False,
    "HomingDevice": False,
    "HoodLock": False,
    "LeasedVehicle": False,
    "LienholderInformation": [],
    "PercentToWork": 50,  # Assume 50% driving is for work by default
}

# Vehicle coverage defaults (no coverage by default)
VEHICLE_COVERAGE_DEFAULTS = {
    "CustomEquipmentValue": 0,
    "CollisionDeductible": "None",
    "ComprehensiveDeductible": "None",
    "RentalLimit": "None",
    "TowingLimit": "None",
    "SafetyGlassCoverage": False,
}

# Policy defaults
POLICY_DEFAULTS = {
    "BumpLimits": "No Bumping",
    "Term": "Semi Annual",  # 6-month term
    "PaymentMethod": "Standard",
    "PolicyType": "New Business",
}

# CA state minimum coverages (recommended: slightly above minimum)
CA_MINIMUM_COVERAGES = {
    "LiabilityBiLimit": "25000/50000",  # CA min is 15/30
    "LiabilityPdLimit": "25000",  # CA min is 5
    "MedPayLimit": "None",
    "UninsuredMotoristBiLimit": "25000/50000",
    "UninsuredMotoristPd/CollisionDamageWaiver": False,
    "AccidentalDeathLimit": "None",
}


def apply_customer_defaults(customer: Dict[str, Any]) -> Dict[str, Any]:
    """Apply default values to customer data.

    Args:
        customer: Customer data dictionary

    Returns:
        Customer data with defaults applied
    """
    result = {**CUSTOMER_DEFAULTS, **customer}

    # Apply contact info defaults if not provided
    if "ContactInformation" not in result:
        result["ContactInformation"] = {}

    # Apply address defaults
    if "Address" in result and isinstance(result["Address"], dict):
        if "County" not in result["Address"]:
            result["Address"]["County"] = ""
        if "Street2" not in result["Address"]:
            result["Address"]["Street2"] = ""

    # Apply prior address defaults (not required, so make it empty if missing)
    if "PriorAddress" not in result:
        result["PriorAddress"] = None

    return result


def apply_driver_defaults(driver: Dict[str, Any]) -> Dict[str, Any]:
    """Apply default values to driver data.

    Args:
        driver: Driver data dictionary

    Returns:
        Driver data with defaults applied
    """
    result = {**DRIVER_DEFAULTS, **driver}

    # Apply license defaults
    if "LicenseInformation" in result and isinstance(result["LicenseInformation"], dict):
        result["LicenseInformation"] = {
            **DRIVER_LICENSE_DEFAULTS,
            **result["LicenseInformation"]
        }

    # Apply attributes defaults
    if "Attributes" in result and isinstance(result["Attributes"], dict):
        result["Attributes"] = {
            **DRIVER_ATTRIBUTES_DEFAULTS,
            **result["Attributes"]
        }

    # Apply discounts defaults
    if "Discounts" not in result:
        result["Discounts"] = DRIVER_DISCOUNTS_DEFAULTS.copy()
    else:
        result["Discounts"] = {**DRIVER_DISCOUNTS_DEFAULTS, **result["Discounts"]}

    # Apply financial responsibility defaults
    if "FinancialResponsibilityInformation" not in result:
        result["FinancialResponsibilityInformation"] = FINANCIAL_RESPONSIBILITY_DEFAULTS.copy()
    else:
        result["FinancialResponsibilityInformation"] = {
            **FINANCIAL_RESPONSIBILITY_DEFAULTS,
            **result["FinancialResponsibilityInformation"]
        }

    # Apply violations defaults
    if "Violations" not in result:
        result["Violations"] = DRIVER_VIOLATIONS_DEFAULT.copy()

    return result


def apply_vehicle_defaults(vehicle: Dict[str, Any]) -> Dict[str, Any]:
    """Apply default values to vehicle data.

    Args:
        vehicle: Vehicle data dictionary

    Returns:
        Vehicle data with defaults applied
    """
    result = {**VEHICLE_DEFAULTS, **vehicle}

    # Apply coverage defaults
    if "CoverageInformation" in result and isinstance(result["CoverageInformation"], dict):
        result["CoverageInformation"] = {
            **VEHICLE_COVERAGE_DEFAULTS,
            **result["CoverageInformation"]
        }
    elif "CoverageInformation" not in result:
        result["CoverageInformation"] = VEHICLE_COVERAGE_DEFAULTS.copy()

    return result


def apply_policy_coverages_defaults(coverages: Dict[str, Any], state: str = "CA") -> Dict[str, Any]:
    """Apply default values to policy coverages.

    Args:
        coverages: Policy coverages dictionary
        state: State code for state-specific minimums

    Returns:
        Policy coverages with defaults applied
    """
    # Start with state minimums
    if state == "CA":
        defaults = CA_MINIMUM_COVERAGES.copy()
    else:
        defaults = CA_MINIMUM_COVERAGES.copy()  # Fallback to CA

    # Override with provided values
    result = {**defaults, **coverages}

    return result


def apply_policy_defaults(policy: Dict[str, Any]) -> Dict[str, Any]:
    """Apply default values to policy-level fields.

    Args:
        policy: Policy data dictionary

    Returns:
        Policy data with defaults applied
    """
    return {**POLICY_DEFAULTS, **policy}


def build_minimal_payload_with_defaults(
    customer: Dict[str, Any],
    drivers: list[Dict[str, Any]],
    vehicles: list[Dict[str, Any]],
    policy_coverages: Dict[str, Any],
    identifier: str,
    effective_date: str,
    state: str = "CA",
    **policy_options
) -> Dict[str, Any]:
    """Build a complete rating payload with defaults applied.

    Args:
        customer: Customer data (required fields only)
        drivers: List of driver data (required fields only)
        vehicles: List of vehicle data (required fields only)
        policy_coverages: Policy coverages (required fields only)
        identifier: Quote identifier
        effective_date: Policy effective date
        state: State code
        **policy_options: Additional policy-level options

    Returns:
        Complete rating payload with all defaults applied
    """
    # Apply defaults to each section
    enriched_customer = apply_customer_defaults(customer)
    enriched_drivers = [apply_driver_defaults(driver) for driver in drivers]
    enriched_vehicles = [apply_vehicle_defaults(vehicle) for vehicle in vehicles]
    enriched_coverages = apply_policy_coverages_defaults(policy_coverages, state)
    enriched_policy = apply_policy_defaults(policy_options)

    # Build the complete payload
    payload = {
        "Identifier": identifier,
        "EffectiveDate": effective_date,
        "Customer": enriched_customer,
        "PolicyCoverages": enriched_coverages,
        "RatedDrivers": enriched_drivers,
        "Vehicles": enriched_vehicles,
        **enriched_policy
    }

    return payload
