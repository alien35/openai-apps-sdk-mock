# End-to-End Quote Strategy: Quick Quote + Conversational Batch

## Executive Summary

This document outlines the complete end-to-end insurance quoting flow that combines:
1. **Quick Quote** - Minimal input (zip + drivers) for instant range
2. **Conversational Batch Collection** - Progressive detail gathering for accurate quote

---

## Table of Contents

1. [Overview](#overview)
2. [Complete User Journey](#complete-user-journey)
3. [Technical Architecture](#technical-architecture)
4. [Implementation Phases](#implementation-phases)
5. [Tool Orchestration](#tool-orchestration)
6. [User Experience Examples](#user-experience-examples)
7. [Testing Strategy](#testing-strategy)

---

## Overview

### The Problem

Traditional insurance quoting requires 20+ fields upfront before showing any pricing:
- High abandonment rate
- Poor user experience
- No early engagement
- Users don't know if they're in the right ballpark

### The Solution

**Two-Stage Progressive Disclosure:**

```
Stage 1: QUICK QUOTE (Engagement)
├─ Input: Zip code + Number of drivers
├─ Output: Best/worst case range
└─ Decision: Continue for accurate quote?

Stage 2: CONVERSATIONAL BATCH (Accuracy)
├─ Batch 1: Customer info
├─ Batch 2: Driver details
├─ Batch 3: Vehicle info
└─ Output: Accurate quote
```

### Benefits

- ✅ **Immediate Value** - Quote range in <10 seconds
- ✅ **Low Friction** - Only 2 fields to start
- ✅ **Progressive** - Collect details only if interested
- ✅ **Contextual** - User knows approximate cost before investing time
- ✅ **Flexible** - Can skip to detailed quote for power users

---

## Complete User Journey

### Journey Map

```
┌──────────────────────────────────────────────────────────────────┐
│                        USER ENTRY POINT                          │
│                    "I need car insurance"                        │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│  STAGE 1: QUICK QUOTE                                            │
│  ────────────────────────────────────────────────────────────    │
│  Tool: get-quick-quote                                           │
│                                                                   │
│  Collect:                                                         │
│    • Zip code (5 digits)                                         │
│    • Number of drivers (1-10)                                    │
│                                                                   │
│  Generate:                                                        │
│    • Best case scenario (35yo, Honda, clean record)             │
│    • Worst case scenario (18yo, Tesla, new driver)              │
│                                                                   │
│  Submit:                                                          │
│    • 2 rating API requests in parallel                          │
│                                                                   │
│  Display:                                                         │
│    ┌─────────────────────────────────────────┐                  │
│    │ Quick Quote Range: San Francisco, CA    │                  │
│    │                                          │                  │
│    │ BEST CASE:   $800-$1,200/6mo           │                  │
│    │ WORST CASE:  $2,400-$3,600/6mo         │                  │
│    │                                          │                  │
│    │ Your rate will fall in this range      │                  │
│    └─────────────────────────────────────────┘                  │
│                                                                   │
│  Prompt: "Want a more accurate quote?"                          │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ├─── User says "No" ──→ END
                         │
                         ├─── User says "Yes" ──→ Continue
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│  STAGE 2: CONVERSATIONAL BATCH COLLECTION                        │
│  ────────────────────────────────────────────────────────────    │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ BATCH 1: Customer Information                              │ │
│  │ Tool: collect-personal-auto-customer                       │ │
│  │                                                            │ │
│  │ Required Fields:                                           │ │
│  │   • FirstName, LastName                                   │ │
│  │   • Address (Street, City, State, Zip)                   │ │
│  │   • MonthsAtResidence                                     │ │
│  │   • PriorInsuranceInformation                             │ │
│  │                                                            │ │
│  │ Strategy:                                                  │ │
│  │   - Ask conversationally, not a form                      │ │
│  │   - Pre-fill zip/state from Stage 1                       │ │
│  │   - Validate as you go                                    │ │
│  │                                                            │ │
│  │ Output:                                                    │ │
│  │   ✓ Customer data captured                                │ │
│  │   ✓ Validation status                                     │ │
│  │   ✓ Missing fields (if any)                               │ │
│  └────────────────────────────────────────────────────────────┘ │
│                         │                                         │
│                         ▼                                         │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ BATCH 2: Driver Information                                │ │
│  │ Tool: collect-personal-auto-drivers                        │ │
│  │                                                            │ │
│  │ Required Per Driver:                                       │ │
│  │   • FirstName, LastName, DateOfBirth                      │ │
│  │   • Gender, MaritalStatus                                 │ │
│  │   • LicenseInformation                                    │ │
│  │   • Attributes (Relation, Residency, etc)                 │ │
│  │                                                            │ │
│  │ Strategy:                                                  │ │
│  │   - One driver at a time                                  │ │
│  │   - Number of drivers from Stage 1                        │ │
│  │   - Forward-append: Can add missing customer fields       │ │
│  │                                                            │ │
│  │ Output:                                                    │ │
│  │   ✓ Drivers array populated                               │ │
│  │   ✓ Customer fields updated (if provided)                 │ │
│  │   ✓ Validation status                                     │ │
│  └────────────────────────────────────────────────────────────┘ │
│                         │                                         │
│                         ▼                                         │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ BATCH 3: Vehicle Information                               │ │
│  │ Tool: collect-personal-auto-vehicles                       │ │
│  │                                                            │ │
│  │ Required Per Vehicle:                                      │ │
│  │   • VIN or Year/Make/Model                                │ │
│  │   • BodyType, UseType                                     │ │
│  │   • AssignedDriverId                                      │ │
│  │   • Mileage info (Annual, ToWork, PercentToWork)          │ │
│  │   • CoverageInformation                                   │ │
│  │                                                            │ │
│  │ Strategy:                                                  │ │
│  │   - One vehicle at a time                                 │ │
│  │   - Suggest VIN lookup for accuracy                       │ │
│  │   - Forward-append: Can add missing customer/driver       │ │
│  │                                                            │ │
│  │ Output:                                                    │ │
│  │   ✓ Vehicles array populated                              │ │
│  │   ✓ Customer/driver fields updated (if provided)          │ │
│  │   ✓ Validation status                                     │ │
│  └────────────────────────────────────────────────────────────┘ │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│  STAGE 3: ACCURATE QUOTE                                         │
│  ────────────────────────────────────────────────────────────    │
│  Tool: request-personal-auto-rate                                │
│                                                                   │
│  Process:                                                         │
│    1. Validate all required fields collected                     │
│    2. Apply field defaults for optional values                   │
│    3. Submit to rating API                                       │
│    4. Retrieve carrier results                                   │
│                                                                   │
│  Display:                                                         │
│    ┌─────────────────────────────────────────┐                  │
│    │ Your Personalized Quote                 │                  │
│    │                                          │                  │
│    │ 🏢 Carrier A: $1,245/6mo               │                  │
│    │    • Payment: $207/mo x 6                │                  │
│    │    • BI: 100/300, PD: 50                │                  │
│    │                                          │                  │
│    │ 🏢 Carrier B: $1,180/6mo               │                  │
│    │    • Payment: $196/mo x 6                │                  │
│    │    • BI: 100/300, PD: 50                │                  │
│    │                                          │                  │
│    │ 🏢 Carrier C: $1,320/6mo               │                  │
│    │    • Payment: $220/mo x 6                │                  │
│    │    • BI: 100/300, PD: 50                │                  │
│    └─────────────────────────────────────────┘                  │
│                                                                   │
│  Next Actions:                                                    │
│    • Compare quotes                                              │
│    • Adjust coverages                                            │
│    • Bind policy                                                 │
└──────────────────────────────────────────────────────────────────┘
```

---

## Technical Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                        MCP SERVER                            │
│                 (insurance_server_python)                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              TOOL REGISTRY                            │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │  1. get-quick-quote              [STAGE 1]          │  │
│  │  2. collect-personal-auto-customer [STAGE 2.1]      │  │
│  │  3. collect-personal-auto-drivers  [STAGE 2.2]      │  │
│  │  4. collect-personal-auto-vehicles [STAGE 2.3]      │  │
│  │  5. request-personal-auto-rate     [STAGE 3]        │  │
│  │  6. retrieve-personal-auto-rate-results              │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              DATA MODELS                              │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │  • QuickQuoteIntake                                  │  │
│  │  • CumulativeCustomerIntake                          │  │
│  │  • CumulativeDriverIntake                            │  │
│  │  • CumulativeVehicleIntake                           │  │
│  │  • PersonalAutoRateRequest                           │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              BUSINESS LOGIC                           │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │  • Scenario generators (best/worst case)             │  │
│  │  • Field validation                                   │  │
│  │  • Forward-appending logic                            │  │
│  │  • Default value application                          │  │
│  │  • API client (httpx)                                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              UTILITIES                                │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │  • Zip code lookup                                    │  │
│  │  • State normalization                                │  │
│  │  • Field validators                                   │  │
│  │  • Rate results formatter                             │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/MCP
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    RATING API                                │
│              (Personal Auto Rate Service)                    │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
User Input → ChatGPT → MCP Server → Tool Handler → Rating API
                  ▲                        │
                  │                        ▼
                  └────── Response ────────┘
```

---

## Implementation Phases

### Phase 1: Quick Quote Foundation

**Files to modify:**
- `insurance_server_python/models.py`
- `insurance_server_python/utils.py`
- `insurance_server_python/tool_handlers.py`
- `insurance_server_python/widget_registry.py`

**Implementation:**

#### 1.1: Add QuickQuoteIntake Model

```python
# File: insurance_server_python/models.py

class QuickQuoteIntake(BaseModel):
    """Quick quote intake for initial quote range."""
    zip_code: str = Field(
        ...,
        alias="ZipCode",
        min_length=5,
        max_length=5,
        description="5-digit US zip code"
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

    @field_validator("zip_code")
    @classmethod
    def validate_zip_code(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError("Zip code must contain only digits")
        return v
```

#### 1.2: Add Zip Code Lookup Utility

```python
# File: insurance_server_python/utils.py

def _lookup_city_state_from_zip(zip_code: str) -> Optional[tuple[str, str]]:
    """Look up city and state from a zip code.

    For production, integrate with:
    - USPS Address API
    - Google Geocoding API
    - Local database (zips.db)

    For MVP: Static mapping of common zips.
    """
    # California zips (90000-96999)
    ZIP_MAP = {
        # Los Angeles Metro
        "90001": ("Los Angeles", "California"),
        "90210": ("Beverly Hills", "California"),
        "91101": ("Pasadena", "California"),

        # San Francisco Bay Area
        "94102": ("San Francisco", "California"),
        "94103": ("San Francisco", "California"),
        "94104": ("San Francisco", "California"),
        "94105": ("San Francisco", "California"),
        "95110": ("San Jose", "California"),

        # San Diego
        "92101": ("San Diego", "California"),
        "92102": ("San Diego", "California"),

        # Sacramento
        "95814": ("Sacramento", "California"),
        "95815": ("Sacramento", "California"),
    }

    # Try exact match first
    result = ZIP_MAP.get(zip_code)
    if result:
        return result

    # Fallback: Infer state from zip prefix
    # 90-96 = California
    if zip_code.startswith("9"):
        return ("California City", "California")

    # For unsupported states in MVP, return None
    return None
```

#### 1.3: Add Scenario Generators

```python
# File: insurance_server_python/tool_handlers.py

def _generate_best_case_quote_data(
    zip_code: str,
    city: str,
    state: str,
    num_drivers: int
) -> dict:
    """Generate best case scenario quote data.

    Best Case Profile (Low Risk):
    ─────────────────────────────────
    Driver:
      • Age: 35 years old (mature, experienced)
      • Marital: Married (statistically safer)
      • License: 10+ years experience
      • Residence: Homeowner, stable (5+ years)
      • Insurance History: Continuous coverage

    Vehicle:
      • Type: Mid-size sedan (Honda Accord)
      • Age: 5 years old (not new, not old)
      • Value: Moderate (~$18k)
      • Safety: High safety ratings

    Usage:
      • Commute: Short (10 miles)
      • Annual: Average (12k miles)
      • Purpose: Commute only
    """
    from datetime import datetime, timedelta

    # Customer profile
    customer = {
        "FirstName": "Best",
        "LastName": "Case",
        "Address": {
            "Street1": "123 Main St",
            "City": city,
            "State": state,
            "ZipCode": zip_code,
        },
        "MonthsAtResidence": 60,  # 5 years = stability
        "PriorInsuranceInformation": {
            "PriorInsurance": True  # Continuous coverage = discount
        },
    }

    # Driver profiles
    drivers = []
    for i in range(num_drivers):
        # Calculate birth date for 35-year-old
        birth_date = (datetime.now() - timedelta(days=35*365)).strftime("%Y-%m-%d")

        driver = {
            "DriverId": i + 1,
            "FirstName": f"Driver{i+1}",
            "LastName": "Best",
            "DateOfBirth": birth_date,
            "Gender": "Male" if i % 2 == 0 else "Female",
            "MaritalStatus": "Married",  # Discount factor
            "LicenseInformation": {
                "LicenseStatus": "Valid",
                "MonthsLicensed": 216,  # 18 years licensed
                "MonthsStateLicensed": 120,  # 10 years in state
            },
            "Attributes": {
                "PropertyInsurance": True,  # Bundle discount
                "Relation": "Insured" if i == 0 else "Spouse",
                "ResidencyStatus": "Own",  # Homeowner
                "ResidencyType": "Home",
            }
        }
        drivers.append(driver)

    # Vehicle profile (reliable, safe, moderate value)
    vehicle = {
        "VehicleId": 1,
        "Year": 2019,  # 5 years old
        "Make": "Honda",
        "Model": "Accord",
        "BodyType": "Sedan",
        "UseType": "Commute",
        "AssignedDriverId": 1,
        "MilesToWork": 10,  # Short commute
        "PercentToWork": 50,
        "AnnualMiles": 12000,  # Average
        "CoverageInformation": {
            "CollisionDeductible": "$500",
            "ComprehensiveDeductible": "$500",
            "RentalLimit": "None",
            "TowingLimit": "None",
            "SafetyGlassCoverage": False,
        }
    }

    return {
        "customer": customer,
        "drivers": drivers,
        "vehicle": vehicle
    }


def _generate_worst_case_quote_data(
    zip_code: str,
    city: str,
    state: str,
    num_drivers: int
) -> dict:
    """Generate worst case scenario quote data.

    Worst Case Profile (High Risk):
    ─────────────────────────────────
    Driver:
      • Age: 18 years old (young, inexperienced)
      • Marital: Single (higher risk statistically)
      • License: 2 years experience (minimum)
      • Residence: Renter, recent move (1 year)
      • Insurance History: None (new driver)

    Vehicle:
      • Type: Performance sedan (Tesla Model 3)
      • Age: Brand new (2024)
      • Value: High (~$45k)
      • Perception: Performance/sporty

    Usage:
      • Commute: Long (30 miles)
      • Annual: High (18k miles)
      • Purpose: Heavy commute
    """
    from datetime import datetime, timedelta

    # Customer profile
    customer = {
        "FirstName": "Worst",
        "LastName": "Case",
        "Address": {
            "Street1": "123 Main St",
            "City": city,
            "State": state,
            "ZipCode": zip_code,
        },
        "MonthsAtResidence": 12,  # 1 year = instability
        "PriorInsuranceInformation": {
            "PriorInsurance": False,  # No history
            "ReasonForNoInsurance": "New Driver"
        },
    }

    # Driver profiles
    drivers = []
    for i in range(num_drivers):
        # Calculate birth date for 18-year-old
        birth_date = (datetime.now() - timedelta(days=18*365 + 180)).strftime("%Y-%m-%d")

        driver = {
            "DriverId": i + 1,
            "FirstName": f"Driver{i+1}",
            "LastName": "Worst",
            "DateOfBirth": birth_date,
            "Gender": "Male",  # Young male = highest risk
            "MaritalStatus": "Single",
            "LicenseInformation": {
                "LicenseStatus": "Valid",
                "MonthsLicensed": 24,  # 2 years = minimum
                "MonthsStateLicensed": 24,
            },
            "Attributes": {
                "PropertyInsurance": False,  # No bundle
                "Relation": "Insured" if i == 0 else "Child",
                "ResidencyStatus": "Rent",  # Renter
                "ResidencyType": "Apartment",
            }
        }
        drivers.append(driver)

    # Vehicle profile (expensive, new, performance)
    vehicle = {
        "VehicleId": 1,
        "Year": 2024,  # Brand new
        "Make": "Tesla",
        "Model": "Model 3",
        "BodyType": "Sedan",
        "UseType": "Commute",
        "AssignedDriverId": 1,
        "MilesToWork": 30,  # Long commute
        "PercentToWork": 80,
        "AnnualMiles": 18000,  # High mileage
        "CoverageInformation": {
            "CollisionDeductible": "$500",
            "ComprehensiveDeductible": "$500",
            "RentalLimit": "None",
            "TowingLimit": "None",
            "SafetyGlassCoverage": False,
        }
    }

    return {
        "customer": customer,
        "drivers": drivers,
        "vehicle": vehicle
    }
```

#### 1.4: Add Quick Quote Handler

```python
# File: insurance_server_python/tool_handlers.py

async def _get_quick_quote(arguments: Mapping[str, Any]) -> ToolInvocationResult:
    """Get quick quote range with minimal input.

    Process Flow:
    ─────────────
    1. Validate inputs (zip + number of drivers)
    2. Lookup city/state from zip code
    3. Generate best case scenario data
    4. Generate worst case scenario data
    5. Build complete payloads with defaults
    6. Submit both to rating API (parallel)
    7. Retrieve both result sets
    8. Format and return range with CTA
    """
    from .field_defaults import build_minimal_payload_with_defaults
    from .utils import _lookup_city_state_from_zip
    from datetime import datetime, timedelta

    # Step 1: Validate
    payload = QuickQuoteIntake.model_validate(arguments)
    zip_code = payload.zip_code
    num_drivers = payload.number_of_drivers

    logger.info(f"Quick quote request: zip={zip_code}, drivers={num_drivers}")

    # Step 2: Lookup location
    city_state = _lookup_city_state_from_zip(zip_code)
    if not city_state:
        return {
            "response_text": (
                f"I couldn't find location information for zip code {zip_code}. "
                "Please provide a valid US zip code, or let me know your city and state."
            ),
        }

    city, state = city_state
    effective_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    logger.info(f"Resolved location: {city}, {state}")

    # Step 3 & 4: Generate scenarios
    best_data = _generate_best_case_quote_data(zip_code, city, state, num_drivers)
    worst_data = _generate_worst_case_quote_data(zip_code, city, state, num_drivers)

    # Step 5: Build payloads
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

    best_payload = build_minimal_payload_with_defaults(
        customer=best_data["customer"],
        drivers=best_data["drivers"],
        vehicles=[best_data["vehicle"]],
        policy_coverages={},
        identifier=f"QUICK_BEST_{zip_code}_{timestamp}",
        effective_date=effective_date,
        state=state,
    )

    worst_payload = build_minimal_payload_with_defaults(
        customer=worst_data["customer"],
        drivers=worst_data["drivers"],
        vehicles=[worst_data["vehicle"]],
        policy_coverages={},
        identifier=f"QUICK_WORST_{zip_code}_{timestamp}",
        effective_date=effective_date,
        state=state,
    )

    # Sanitize and add carrier info
    _sanitize_personal_auto_rate_request(best_payload)
    best_payload["CarrierInformation"] = DEFAULT_CARRIER_INFORMATION

    _sanitize_personal_auto_rate_request(worst_payload)
    worst_payload["CarrierInformation"] = DEFAULT_CARRIER_INFORMATION

    # Step 6 & 7: Submit to API
    state_code = state_abbreviation(state) or state
    url = f"{PERSONAL_AUTO_RATE_ENDPOINT}/{state_code}/rates/latest?multiAgency=false"
    headers = _personal_auto_rate_headers()

    best_results = None
    worst_results = None

    try:
        # Submit best case
        logger.info("Submitting best case scenario")
        async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as client:
            best_response = await client.post(url, headers=headers, json=best_payload)

        if not best_response.is_error:
            best_parsed = best_response.json()
            best_tx_id = best_parsed.get("transactionId")

            if best_tx_id:
                logger.info(f"Best case transaction ID: {best_tx_id}")
                async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as client:
                    results_resp = await client.get(
                        PERSONAL_AUTO_RATE_RESULTS_ENDPOINT,
                        headers=headers,
                        params={"Id": best_tx_id}
                    )
                if not results_resp.is_error:
                    best_results = results_resp.json()
                    logger.info("Best case results retrieved")

        # Submit worst case
        logger.info("Submitting worst case scenario")
        async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as client:
            worst_response = await client.post(url, headers=headers, json=worst_payload)

        if not worst_response.is_error:
            worst_parsed = worst_response.json()
            worst_tx_id = worst_parsed.get("transactionId")

            if worst_tx_id:
                logger.info(f"Worst case transaction ID: {worst_tx_id}")
                async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as client:
                    results_resp = await client.get(
                        PERSONAL_AUTO_RATE_RESULTS_ENDPOINT,
                        headers=headers,
                        params={"Id": worst_tx_id}
                    )
                if not results_resp.is_error:
                    worst_results = results_resp.json()
                    logger.info("Worst case results retrieved")

    except httpx.HTTPError as exc:
        logger.exception("Quick quote request failed")
        return {
            "response_text": (
                f"I'm having trouble getting quotes right now. Error: {exc}\n\n"
                "Would you like to try again, or provide your details for a manual quote?"
            ),
        }

    # Step 8: Format response
    message = f"**Quick Quote Range for {city}, {state}** (Zip: {zip_code})\n\n"

    if not best_results and not worst_results:
        message += "I wasn't able to get quotes from any carriers at the moment. "
        message += "Let's collect your information and try again.\n\n"
    else:
        if best_results:
            best_summary = format_rate_results_summary(best_results)
            if best_summary:
                message += (
                    f"**BEST CASE SCENARIO**\n"
                    f"(Experienced driver, reliable vehicle, clean record)\n\n"
                    f"{best_summary}\n\n"
                )

        if worst_results:
            worst_summary = format_rate_results_summary(worst_results)
            if worst_summary:
                message += (
                    f"**WORST CASE SCENARIO**\n"
                    f"(New driver, newer vehicle, limited history)\n\n"
                    f"{worst_summary}\n\n"
                )

        message += "───────────────────────────────────\n\n"
        message += "Your actual rate will depend on your specific details:\n"
        message += "• Driver ages and experience\n"
        message += "• Vehicle year, make, and model\n"
        message += "• Driving history and claims\n"
        message += "• Coverage selections\n\n"

    message += (
        "**Ready for your personalized quote?**\n\n"
        "I can collect your actual driver and vehicle information to give you "
        "an accurate premium from multiple carriers."
    )

    import mcp.types as types
    return {
        "structured_content": {
            "zip_code": zip_code,
            "number_of_drivers": num_drivers,
            "city": city,
            "state": state,
            "best_case_results": best_results,
            "worst_case_results": worst_results,
            "stage": "quick_quote_complete",
        },
        "content": [types.TextContent(type="text", text=message)],
    }
```

#### 1.5: Register Tool

```python
# File: insurance_server_python/widget_registry.py

def _register_personal_auto_intake_tools() -> None:
    """Register personal auto insurance intake tools."""
    from .tool_handlers import (
        _get_quick_quote,  # NEW
        _collect_personal_auto_customer,
        _collect_personal_auto_drivers,
        _collect_personal_auto_vehicles,
        _request_personal_auto_rate,
        _retrieve_personal_auto_rate_results,
    )
    from .models import (
        QuickQuoteIntake,  # NEW
        CumulativeCustomerIntake,
        CumulativeDriverIntake,
        CumulativeVehicleIntake,
        PersonalAutoRateRequest,
        PersonalAutoRateResultsRequest,
    )
    from .utils import _model_schema
    from .constants import AIS_POLICY_COVERAGE_SUMMARY

    # ═══════════════════════════════════════════════════════════
    # STAGE 1: QUICK QUOTE (Engagement)
    # ═══════════════════════════════════════════════════════════
    register_tool(
        ToolRegistration(
            tool=types.Tool(
                name="get-quick-quote",
                title="Get quick auto insurance quote range",
                description=(
                    "STAGE 1: Get an instant quote range with just zip code and number of drivers. "
                    "This tool generates best case and worst case scenarios to show the user "
                    "a premium range within seconds. "
                    "\n\n"
                    "Best case assumes: 35-year-old experienced driver, reliable mid-size sedan, "
                    "clean driving record, homeowner. "
                    "\n\n"
                    "Worst case assumes: 18-year-old new driver, newer performance vehicle, "
                    "limited history, renter. "
                    "\n\n"
                    "USE THIS FIRST when a user asks about car insurance quotes. "
                    "After showing the range, prompt them to continue with detailed collection "
                    "for an accurate quote."
                ),
                inputSchema=_model_schema(QuickQuoteIntake),
            ),
            handler=_get_quick_quote,
            default_response_text="Generated quick quote range.",
        )
    )

    # ═══════════════════════════════════════════════════════════
    # STAGE 2: CONVERSATIONAL BATCH COLLECTION (Accuracy)
    # ═══════════════════════════════════════════════════════════

    # BATCH 1: Customer Information
    register_tool(
        ToolRegistration(
            tool=types.Tool(
                name="collect-personal-auto-customer",
                title="Collect customer information",
                description=(
                    "STAGE 2 - BATCH 1: Collect customer profile information. "
                    "Required: name, address, residence duration, prior insurance status. "
                    "Use this after quick quote when user wants accurate pricing. "
                    "Collect conversationally, not as a form."
                ),
                inputSchema=_model_schema(CumulativeCustomerIntake),
            ),
            handler=_collect_personal_auto_customer,
            default_response_text="Captured customer information.",
        )
    )

    # BATCH 2: Driver Information
    register_tool(
        ToolRegistration(
            tool=types.Tool(
                name="collect-personal-auto-drivers",
                title="Collect driver information",
                description=(
                    "STAGE 2 - BATCH 2: Collect rated driver information. "
                    "Required per driver: name, DOB, gender, marital status, license details. "
                    "This tool supports forward-appending: can include missing customer fields. "
                    "Collect one driver at a time conversationally."
                ),
                inputSchema=_model_schema(CumulativeDriverIntake),
            ),
            handler=_collect_personal_auto_drivers,
            default_response_text="Captured driver information.",
        )
    )

    # BATCH 3: Vehicle Information
    register_tool(
        ToolRegistration(
            tool=types.Tool(
                name="collect-personal-auto-vehicles",
                title="Collect vehicle information",
                description=(
                    "STAGE 2 - BATCH 3: Collect vehicle information. "
                    "Required per vehicle: VIN or year/make/model, usage, assigned driver, coverage preferences. "
                    "This tool supports forward-appending: can include missing customer/driver fields. "
                    "Collect one vehicle at a time conversationally."
                ),
                inputSchema=_model_schema(CumulativeVehicleIntake),
            ),
            handler=_collect_personal_auto_vehicles,
            default_response_text="Captured vehicle information.",
        )
    )

    # ═══════════════════════════════════════════════════════════
    # STAGE 3: ACCURATE QUOTE (Final)
    # ═══════════════════════════════════════════════════════════

    rate_results_widget = WIDGETS_BY_ID[INSURANCE_RATE_RESULTS_WIDGET_IDENTIFIER]
    rate_results_meta = {
        **_tool_meta(rate_results_widget),
        "openai/widgetAccessible": True,
    }
    rate_results_default_meta = {
        **rate_results_meta,
        "openai.com/widget": _embedded_widget_resource(rate_results_widget).model_dump(mode="json"),
    }

    rate_tool_description = (
        "STAGE 3: Submit complete personal auto quote request to get accurate carrier rates. "
        "Use this after collecting customer, driver, and vehicle information through "
        "the conversational batch flow (Stage 2). "
        f"Coverage limits must match AIS enumerations ({AIS_POLICY_COVERAGE_SUMMARY}). "
        "Returns carrier premiums, payment plans, and quote identifier."
    )

    rate_tool_meta = {
        "openai/widgetAccessible": True,
        "openai/resultCanProduceWidget": True,
        "openai.com/widget": _embedded_widget_resource(rate_results_widget).model_dump(mode="json"),
        "annotations": {
            "destructiveHint": False,
            "openWorldHint": False,
            "readOnlyHint": False,
        },
    }

    register_tool(
        ToolRegistration(
            tool=types.Tool(
                name="request-personal-auto-rate",
                title="Request personal auto rate",
                description=rate_tool_description,
                inputSchema=_model_schema(PersonalAutoRateRequest),
                _meta=rate_tool_meta,
            ),
            handler=_request_personal_auto_rate,
            default_response_text="Submitted personal auto rating request.",
        )
    )

    register_tool(
        ToolRegistration(
            tool=types.Tool(
                name="retrieve-personal-auto-rate-results",
                title="Retrieve personal auto rate results",
                description=(
                    "Fetch carrier rate results for an existing quote using its identifier. "
                    "Use when user wants to review quotes again or compare options."
                ),
                inputSchema=_model_schema(PersonalAutoRateResultsRequest),
                _meta=rate_results_meta,
            ),
            handler=_retrieve_personal_auto_rate_results,
            default_response_text="Retrieved personal auto rate results.",
            default_meta=rate_results_default_meta,
        )
    )
```

---

### Phase 2: Conversational Batch Strategy

**No code changes needed!** The existing tools already support this:
- `collect-personal-auto-customer`
- `collect-personal-auto-drivers`
- `collect-personal-auto-vehicles`

**Key features already implemented:**
- ✅ Forward-appending (can add customer fields in driver/vehicle batches)
- ✅ Validation with missing field tracking
- ✅ Flexible JSON schemas
- ✅ Progressive disclosure

---

### Phase 3: Integration & Flow Control

The ChatGPT assistant will orchestrate the flow:

```
User: "I need car insurance"
  ↓
Assistant detects: Quick quote opportunity
  ↓
Assistant: "Let me get you an instant quote range!
            What's your zip code and how many drivers?"
  ↓
User: "94103, 2 drivers"
  ↓
[Tool: get-quick-quote]
  ↓
Assistant: Shows range ($800-$3600)
           "Want a more accurate quote?"
  ↓
User: "Yes"
  ↓
[Tool: collect-personal-auto-customer]
[Tool: collect-personal-auto-drivers]
[Tool: collect-personal-auto-vehicles]
  ↓
[Tool: request-personal-auto-rate]
  ↓
Assistant: Shows accurate quotes from carriers
```

---

## Tool Orchestration

### Tool Call Sequence

```
STAGE 1: QUICK QUOTE
┌─────────────────────────────────────────┐
│ get-quick-quote                         │
│   Input: {ZipCode, NumberOfDrivers}    │
│   Output: Range, CTA                    │
└─────────────────────────────────────────┘
              ↓
        User decision
              ↓
STAGE 2: BATCH COLLECTION
┌─────────────────────────────────────────┐
│ collect-personal-auto-customer          │
│   Input: {Customer: {...}}             │
│   Output: Validation, missing fields    │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ collect-personal-auto-drivers           │
│   Input: {Customer?, RatedDrivers}      │
│   Output: Validation, missing fields    │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ collect-personal-auto-vehicles          │
│   Input: {Customer?, RatedDrivers?,     │
│           Vehicles}                      │
│   Output: Validation, missing fields    │
└─────────────────────────────────────────┘
              ↓
STAGE 3: ACCURATE QUOTE
┌─────────────────────────────────────────┐
│ request-personal-auto-rate              │
│   Input: Complete quote request         │
│   Output: Carrier results, widget       │
└─────────────────────────────────────────┘
```

### State Management

Each tool returns structured_content that includes:
- Data collected so far
- Validation status
- Missing fields
- Current stage

```python
{
    "structured_content": {
        "customer": {...},
        "rated_drivers": [...],
        "vehicles": [...],
        "validation": {
            "customer_complete": true/false,
            "drivers_complete": true/false,
            "vehicles_complete": true/false,
            "missing_fields": [...]
        },
        "stage": "customer" | "drivers" | "vehicles" | "ready"
    }
}
```

---

## User Experience Examples

### Example 1: Full Quick-to-Detailed Flow

```
User: I need car insurance quotes