"""Constants, mappings, and enumerations for the insurance server."""

from typing import Any, Dict, Mapping, Tuple, Literal, get_args
import re

# State mappings
STATE_ABBREVIATION_TO_NAME: Dict[str, str] = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "DC": "District of Columbia",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming",
}

STATE_NAME_TO_CANONICAL: Dict[str, str] = {
    name.upper(): name for name in STATE_ABBREVIATION_TO_NAME.values()
}

STATE_NAME_TO_ABBREVIATION: Dict[str, str] = {
    name: code for code, name in STATE_ABBREVIATION_TO_NAME.items()
}

# Insurance type mappings
INSURANCE_TYPE_ALLOWED_VALUES: Dict[str, str] = {
    "personal-auto": "Personal auto",
    "homeowners": "Homeowners",
    "renters": "Renters",
}

INSURANCE_TYPE_MAPPINGS: Dict[str, str] = {
    "auto": "personal-auto",
    "car": "personal-auto",
    "personalauto": "personal-auto",
    "personalautos": "personal-auto",
    "personal-auto": "personal-auto",
    "home": "homeowners",
    "homeowner": "homeowners",
    "homeowners": "homeowners",
    "property": "homeowners",
    "rent": "renters",
    "renter": "renters",
    "renters": "renters",
}

# Relation mappings
RELATION_ALLOWED_VALUES: Tuple[str, ...] = (
    "Insured",
    "Spouse",
    "Child",
    "Parent",
    "Other Related",
    "Other Non Related",
)

RELATION_MAPPINGS: Mapping[str, str] = {
    "self": "Insured",
    "namedinsured": "Insured",
    "policyholder": "Insured",
    "insured": "Insured",
    "spouse": "Spouse",
    "partner": "Spouse",
    "domesticpartner": "Spouse",
    "husband": "Spouse",
    "wife": "Spouse",
    "child": "Child",
    "son": "Child",
    "daughter": "Child",
    "dependent": "Child",
    "parent": "Parent",
    "mother": "Parent",
    "father": "Parent",
    "guardian": "Parent",
    "sibling": "Other Related",
    "brother": "Other Related",
    "sister": "Other Related",
    "cousin": "Other Related",
    "relative": "Other Related",
    "family": "Other Related",
    "otherrelated": "Other Related",
    "grandparent": "Other Related",
    "grandmother": "Other Related",
    "grandfather": "Other Related",
    "inlaw": "Other Related",
    "friend": "Other Non Related",
    "roommate": "Other Non Related",
    "coworker": "Other Non Related",
    "colleague": "Other Non Related",
    "othernonrelated": "Other Non Related",
    "nonrelative": "Other Non Related",
    "other": "Other Non Related",
}

# License status mappings
LICENSE_STATUS_MAPPINGS: Mapping[str, str] = {
    "valid": "Valid",
    "licensed": "Valid",
    "licenseddriver": "Valid",
    "validlicense": "Valid",
    "full": "Valid",
    "fulllicense": "Valid",
    "active": "Valid",
    "activelicense": "Valid",
    "unlicensed": "Unlicensed",
    "nolicense": "Unlicensed",
    "permit": "Permit",
    "learnerpermit": "Permit",
    "expired": "Expired",
    "revoked": "Revoked",
    "suspended": "Suspended",
}

# Residency mappings
RESIDENCY_STATUS_MAPPINGS: Mapping[str, str] = {
    "resident": "Own",
    "householdresident": "Own",
    "owner": "Own",
    "own": "Own",
    "nonresident": "Rent",
    "notresident": "Rent",
    "rent": "Rent",
    "renter": "Rent",
    "lease": "Lease",
    "leased": "Lease",
}

RESIDENCY_TYPE_MAPPINGS: Mapping[str, str] = {
    # Detached homes / ownership scenarios
    "owner": "Home",
    "owned": "Home",
    "home": "Home",
    "house": "Home",
    "singlefamily": "Home",
    "singlefamilyhome": "Home",
    "primaryresidence": "Home",
    # Multi-unit rentals
    "apartment": "Apartment",
    "apt": "Apartment",
    "apartmentunit": "Apartment",
    "flat": "Apartment",
    # Condominiums
    "condo": "Condo",
    "condominium": "Condo",
    # Mobile homes
    "mobilehome": "Mobile Home",
    "mobile": "Mobile Home",
    "trailer": "Mobile Home",
    "manufacturedhome": "Mobile Home",
    # Fixed mobile homes
    "fixedmobilehome": "Fixed Mobile Home",
    "fixedmanufacturedhome": "Fixed Mobile Home",
    "permanentmobilehome": "Fixed Mobile Home",
}

# Term and payment mappings
TERM_MAPPINGS: Mapping[str, str] = {
    "6months": "Semi Annual",
    "sixmonths": "Semi Annual",
    "sixmonth": "Semi Annual",
    "six": "Semi Annual",
    "sixmonthterm": "Semi Annual",
    "sixmonthspolicy": "Semi Annual",
    "6month": "Semi Annual",
    "6monthterm": "Semi Annual",
    "6monthspolicy": "Semi Annual",
    "semiannual": "Semi Annual",
    "semiannualterm": "Semi Annual",
    "semi": "Semi Annual",
    "12months": "Annual",
    "twelvemonths": "Annual",
    "twelvemonth": "Annual",
    "annual": "Annual",
    "yearly": "Annual",
}

PAYMENT_METHOD_MAPPINGS: Mapping[str, str] = {
    "eft": "Electronic Funds Transfer",
    "electronicfundstransfer": "Electronic Funds Transfer",
    "electronicfundtransfer": "Electronic Funds Transfer",
    "electronicfundtransfers": "Electronic Funds Transfer",
    "electronicfundstransfers": "Electronic Funds Transfer",
    "bankdraft": "Electronic Funds Transfer",
    "ach": "Electronic Funds Transfer",
    "autopay": "Electronic Funds Transfer",
    "monthlyautopay": "Electronic Funds Transfer",
    "default": "Default",
    "standard": "Standard",
    "invoice": "Standard",
    "paper": "Standard",
    "mail": "Standard",
    "card": "Standard",
    "credit": "Standard",
    "creditcard": "Standard",
    "debit": "Standard",
    "debitcard": "Standard",
    "cash": "Standard",
    "moneyorder": "Standard",
    "check": "Standard",
    "agencybill": "Standard",
    "quarterly": "Standard",
    "full": "Paid In Full",
    "fullpay": "Paid In Full",
    "onepay": "Paid In Full",
    "singlepay": "Paid In Full",
    "paidinfull": "Paid In Full",
    "payinfull": "Paid In Full",
}

POLICY_TYPE_MAPPINGS: Mapping[str, str] = {
    "personalauto": "Standard",
    "standard": "Standard",
    "standardauto": "Standard",
    "preferred": "Preferred",
    "nonstandard": "Non-Standard",
}

BUMP_LIMIT_MAPPINGS: Mapping[str, str] = {
    "nobumping": "No Bumping",
    "nobump": "No Bumping",
    "none": "No Bumping",
    "bumpup": "Bump Up",
    "raisetorecommended": "Bump Up",
    "bumpdown": "Bump Down",
    "matchpriorpolicy": "Bump Down",
    "matchprior": "Bump Down",
    "matchprevious": "Bump Down",
    "matchpreviouspolicy": "Bump Down",
}

PURCHASE_TYPE_MAPPINGS: Mapping[str, str] = {
    "own": "Owned",
    "owned": "Owned",
    "ownedoutright": "Owned",
    "owner": "Owned",
    "finance": "Financed",
    "financed": "Financed",
    "loan": "Financed",
    "lease": "Leased",
    "leased": "Leased",
}

# Coverage limit mappings
LIABILITY_BI_LIMIT_MAPPINGS: Mapping[str, str] = {
    "1530": "15000/30000",
    "2550": "25000/50000",
    "3060": "30000/60000",
    "50100": "50000/100000",
    "100300": "100000/300000",
    "250500": "250000/500000",
    "500500": "500/500",
    "1500030000": "15000/30000",
    "2500050000": "25000/50000",
    "3000060000": "30000/60000",
    "50000100000": "50000/100000",
    "100000300000": "100000/300000",
    "250000500000": "250000/500000",
    "300000300000": "300000/300000",
}

PROPERTY_DAMAGE_LIMIT_MAPPINGS: Mapping[str, str] = {
    "5": "5000",
    "10": "10000",
    "15": "15000",
    "20": "20000",
    "25": "25000",
    "50": "50000",
    "100": "100000",
    "5000": "5000",
    "10000": "10000",
    "15000": "15000",
    "20000": "20000",
    "25000": "25000",
    "50000": "50000",
    "100000": "100000",
}

ACCIDENTAL_DEATH_LIMIT_MAPPINGS: Mapping[str, str] = {
    "0": "None",
    "none": "None",
    "5000": "5000",
    "10000": "10000",
    "15000": "15000",
    "25000": "25000",
}

MED_PAY_LIMIT_MAPPINGS: Mapping[str, str] = {
    "0": "None",
    "none": "None",
    "500": "500",
    "1000": "1000",
    "2000": "2000",
    "5000": "5000",
    "10000": "10000",
    "25000": "25000",
    "50000": "50000",
}

# Coverage limit type literals
LiabilityBiLimit = Literal[
    "15/30",
    "25/50",
    "30/60",
    "50/100",
    "100/300",
    "250/500",
    "500/500",
    "15000/30000",
    "25000/50000",
    "30000/60000",
    "50000/100000",
    "100000/300000",
    "250000/500000",
    "300000/300000",
]
PropertyDamageLimit = Literal[
    "5",
    "10",
    "15",
    "20",
    "25",
    "50",
    "100",
    "5000",
    "10000",
    "15000",
    "20000",
    "25000",
    "50000",
    "100000",
]
MedicalPaymentsLimit = Literal[
    "None",
    "500",
    "1000",
    "2000",
    "5000",
    "10000",
    "25000",
    "50000",
]
UninsuredMotoristBiLimit = LiabilityBiLimit
AccidentalDeathLimit = Literal["None", "5000", "10000", "15000", "25000"]

AIS_LIABILITY_BI_LIMITS: Tuple[str, ...] = tuple(get_args(LiabilityBiLimit))
AIS_LIABILITY_PD_LIMITS: Tuple[str, ...] = tuple(get_args(PropertyDamageLimit))
AIS_MED_PAY_LIMITS: Tuple[str, ...] = tuple(get_args(MedicalPaymentsLimit))
AIS_UNINSURED_MOTORIST_BI_LIMITS: Tuple[str, ...] = tuple(
    get_args(UninsuredMotoristBiLimit)
)
AIS_ACCIDENTAL_DEATH_LIMITS: Tuple[str, ...] = tuple(get_args(AccidentalDeathLimit))

AIS_POLICY_COVERAGE_SUMMARY = (
    "Liability BI: "
    + ", ".join(AIS_LIABILITY_BI_LIMITS)
    + "; Liability PD: "
    + ", ".join(AIS_LIABILITY_PD_LIMITS)
    + "; MedPay: "
    + ", ".join(AIS_MED_PAY_LIMITS)
    + "; UM BI: "
    + ", ".join(AIS_UNINSURED_MOTORIST_BI_LIMITS)
    + "; Accidental death: "
    + ", ".join(AIS_ACCIDENTAL_DEATH_LIMITS)
    + "."
)

# API endpoints
PERSONAL_AUTO_RATE_ENDPOINT = (
    "https://gateway.zrater.io/api/v2/linesOfBusiness/personalAuto/states"
)
PERSONAL_AUTO_RATE_RESULTS_ENDPOINT = (
    "https://gateway.zrater.io/api/v2/linesOfBusiness/personalAuto/getRateResultsById"
)

# Default carrier information
DEFAULT_CARRIER_INFORMATION: Dict[str, Any] = {
    "UseExactCarrierInfo": False,
    "Products": [
        {
            "AgencyId": "456494ef-0742-499c-92e0-db9fc8c78941",
            "ProductId": "9c0220c6-49c4-4358-aefc-d5bc51630fe5",
            "ProductName": "Anchor Gemini",
            "CarrierUserName": "autoinsspec",
            "CarrierPassword": "character99",
            "ProducerCode": "92000",
            "CarrierLoginUserName": "",
            "CarrierLoginPassword": "",
            "CarrierId": "0b0ab021-dd46-4d60-8cd5-e22901030008",
            "CarrierName": "Anchor General Ins",
        },
        {
            "AgencyId": "456494ef-0742-499c-92e0-db9fc8c78941",
            "ProductId": "5e9d28df-214d-4dfc-b723-2f2abd3f5ee5",
            "ProductName": "Anchor Motor Club",
            "CarrierUserName": "autoinsspec",
            "CarrierPassword": "charachter99",
            "ProducerCode": "92002",
            "CarrierLoginUserName": "",
            "CarrierLoginPassword": "",
            "CarrierId": "0b0ab021-dd46-4d60-8cd5-e22901030008",
            "CarrierName": "Anchor General Ins",
            "ProductQuestions": {
                "AnchorMotorClubV3RTCollBuyback": {
                    "Id": "0-AnchorMotorClubV3RTCollBuyback",
                    "Value": "Yes",
                }
            },
        },
        {
            "AgencyId": "456494ef-0742-499c-92e0-db9fc8c78941",
            "ProductId": "bdd4c0f9-7c50-45dc-a5df-deac8ac717fe",
            "ProductName": "Anchor Premier",
            "CarrierUserName": "autoinsspec",
            "CarrierPassword": "charachter99",
            "ProducerCode": "92840",
            "CarrierLoginUserName": "",
            "CarrierLoginPassword": "",
            "CarrierId": "0b0ab021-dd46-4d60-8cd5-e22901030008",
            "CarrierName": "Anchor General Ins",
            "ProductQuestions": {
                "AnchorPremierV3MPP": {
                    "Id": "0-AnchorPremierV3MPP",
                    "Value": "Yes",
                },
                "AnchorPremierV3RTCollBuyback": {
                    "Id": "0-AnchorPremierV3RTCollBuyback",
                    "Value": "Yes",
                },
            },
        },
    ],
}

# Patterns
ZIP_CODE_NORMALIZATION_PATTERN = re.compile(r"\D")

# MIME type for MCP Apps
MIME_TYPE = "text/html;profile=mcp-app"
