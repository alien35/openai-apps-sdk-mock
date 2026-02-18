# Quick Quote Strategy - Implementation Plan

## Overview

Update the conversational batch strategy to collect minimal information first (zip code + number of drivers), provide a quote range (best case to worst case), then allow users to continue with detailed information for accurate quotes.

## Current State

### Existing Flow
1. User starts quote process
2. Tool: `collect-personal-auto-customer` - Collects full customer profile
3. Tool: `collect-personal-auto-drivers` - Collects detailed driver information
4. Tool: `collect-personal-auto-vehicles` - Collects vehicle details
5. Tool: `request-personal-auto-rate` - Submits complete quote request
6. Tool: `retrieve-personal-auto-rate-results` - Shows final results

### Problems with Current Flow
- Requires extensive information upfront
- User doesn't see pricing until the end
- High abandonment risk (too many questions)
- No immediate value/engagement

## Desired State

### New Quick Quote Flow
1. **Step 1: Quick Quote** (NEW)
   - Collect: Zip code + Number of drivers
   - Generate: Best case scenario quote
   - Generate: Worst case scenario quote
   - Show: Premium range immediately
   - Prompt: "Want a more accurate quote? Let's continue..."

2. **Step 2: Detailed Collection** (if user continues)
   - Use existing tools for detailed information
   - Provide accurate quote based on actual details

### Benefits
- Immediate engagement with quote range
- Lower barrier to entry
- User sees value before committing time
- Natural progression to detailed quote
- Can still support full detailed flow

---

## Implementation Plan

### Phase 1: Data Models

#### File: `insurance_server_python/models.py`

**Add new model:**
```python
class QuickQuoteIntake(BaseModel):
    """Quick quote intake for initial quote range."""
    zip_code: str = Field(
        ...,
        alias="ZipCode",
        description="5-digit zip code"
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
```

**Purpose:** Minimal input schema for quick quotes

---

### Phase 2: Utility Functions

#### File: `insurance_server_python/utils.py`

**Add zip code lookup:**
```python
def _lookup_city_state_from_zip(zip_code: str) -> Optional[tuple[str, str]]:
    """Look up city and state from zip code.

    Returns:
        Tuple of (city, state) or None if not found
    """
    # Implementation options:
    # 1. Static mapping for demo (CA zip codes)
    # 2. Call external API (zipcodeapi.com, etc.)
    # 3. Use local database (zips.db)

    # For MVP: Static mapping of common CA zips
    ZIP_MAP = {
        "94103": ("San Francisco", "California"),
        "90210": ("Beverly Hills", "California"),
        "92101": ("San Diego", "California"),
        # ... more zips
    }
    return ZIP_MAP.get(zip_code)
```

**Purpose:** Convert zip code to city/state for quote generation

---

### Phase 3: Scenario Generation

#### File: `insurance_server_python/tool_handlers.py`

**Add scenario builder functions:**

```python
def _generate_best_case_quote_data(
    zip_code: str,
    city: str,
    state: str,
    num_drivers: int
) -> dict:
    """Generate best case scenario data.

    Best Case Profile:
    - Age: 35 years old (mature driver)
    - Marital Status: Married
    - License: Valid, 10+ years experience
    - Residence: Owns home, 5+ years at address
    - Vehicle: 5-year-old reliable sedan (Honda Accord)
    - Prior Insurance: Yes
    - Violations: None
    - Credit: Good
    """
    customer = {
        "FirstName": "Best",
        "LastName": "Case",
        "Address": {
            "Street1": "123 Main St",
            "City": city,
            "State": state,
            "ZipCode": zip_code,
        },
        "MonthsAtResidence": 60,
        "PriorInsuranceInformation": {"PriorInsurance": True},
    }

    drivers = []
    for i in range(num_drivers):
        driver = {
            "DriverId": i + 1,
            "FirstName": f"Driver{i+1}",
            "LastName": "Best",
            "DateOfBirth": "1989-01-01",  # 35 years old
            "Gender": "Male" if i % 2 == 0 else "Female",
            "MaritalStatus": "Married",
            "LicenseInformation": {
                "LicenseStatus": "Valid",
                "MonthsLicensed": 120,  # 10 years
            },
            "Attributes": {
                "PropertyInsurance": True,
                "Relation": "Insured" if i == 0 else "Spouse",
                "ResidencyStatus": "Own",
                "ResidencyType": "Home",
            }
        }
        drivers.append(driver)

    vehicle = {
        "VehicleId": 1,
        "Year": 2019,
        "Make": "Honda",
        "Model": "Accord",
        "BodyType": "Sedan",
        "UseType": "Commute",
        "AssignedDriverId": 1,
        "MilesToWork": 10,
        "AnnualMiles": 12000,
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
    """Generate worst case scenario data.

    Worst Case Profile:
    - Age: 18 years old (young driver)
    - Marital Status: Single
    - License: Valid, 2 years experience
    - Residence: Rents, 1 year at address
    - Vehicle: Brand new luxury/sporty (Tesla Model 3)
    - Prior Insurance: No
    - Violations: None (but inexperienced)
    - Credit: Limited history
    """
    customer = {
        "FirstName": "Worst",
        "LastName": "Case",
        "Address": {
            "Street1": "123 Main St",
            "City": city,
            "State": state,
            "ZipCode": zip_code,
        },
        "MonthsAtResidence": 12,
        "PriorInsuranceInformation": {
            "PriorInsurance": False,
            "ReasonForNoInsurance": "New Driver"
        },
    }

    drivers = []
    for i in range(num_drivers):
        driver = {
            "DriverId": i + 1,
            "FirstName": f"Driver{i+1}",
            "LastName": "Worst",
            "DateOfBirth": "2006-01-01",  # 18 years old
            "Gender": "Male",
            "MaritalStatus": "Single",
            "LicenseInformation": {
                "LicenseStatus": "Valid",
                "MonthsLicensed": 24,  # 2 years
            },
            "Attributes": {
                "PropertyInsurance": False,
                "Relation": "Insured" if i == 0 else "Child",
                "ResidencyStatus": "Rent",
                "ResidencyType": "Apartment",
            }
        }
        drivers.append(driver)

    vehicle = {
        "VehicleId": 1,
        "Year": 2024,
        "Make": "Tesla",
        "Model": "Model 3",
        "BodyType": "Sedan",
        "UseType": "Commute",
        "AssignedDriverId": 1,
        "MilesToWork": 30,
        "AnnualMiles": 18000,
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

**Purpose:** Generate realistic best/worst case quote scenarios

---

### Phase 4: Main Tool Handler

#### File: `insurance_server_python/tool_handlers.py`

**Add quick quote handler:**

```python
async def _get_quick_quote(arguments: Mapping[str, Any]) -> ToolInvocationResult:
    """Get quick quote range with just zip code and number of drivers.

    Process:
    1. Validate inputs
    2. Lookup city/state from zip
    3. Generate best case scenario
    4. Generate worst case scenario
    5. Submit both to rating API
    6. Format and return range
    """
    from .field_defaults import build_minimal_payload_with_defaults
    from .utils import _lookup_city_state_from_zip

    # 1. Validate
    payload = QuickQuoteIntake.model_validate(arguments)
    zip_code = payload.zip_code
    num_drivers = payload.number_of_drivers

    # 2. Lookup location
    city_state = _lookup_city_state_from_zip(zip_code)
    if not city_state:
        return {
            "response_text": (
                f"Unable to find location for zip code {zip_code}. "
                "Please provide a valid US zip code."
            ),
        }

    city, state = city_state
    effective_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    # 3. Generate scenarios
    best_data = _generate_best_case_quote_data(zip_code, city, state, num_drivers)
    worst_data = _generate_worst_case_quote_data(zip_code, city, state, num_drivers)

    # 4. Build payloads
    best_payload = build_minimal_payload_with_defaults(
        customer=best_data["customer"],
        drivers=best_data["drivers"],
        vehicles=[best_data["vehicle"]],
        policy_coverages={},
        identifier=f"QUICK_BEST_{zip_code}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        effective_date=effective_date,
        state=state,
    )

    worst_payload = build_minimal_payload_with_defaults(
        customer=worst_data["customer"],
        drivers=worst_data["drivers"],
        vehicles=[worst_data["vehicle"]],
        policy_coverages={},
        identifier=f"QUICK_WORST_{zip_code}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        effective_date=effective_date,
        state=state,
    )

    # 5. Submit to API
    _sanitize_personal_auto_rate_request(best_payload)
    best_payload["CarrierInformation"] = DEFAULT_CARRIER_INFORMATION
    _sanitize_personal_auto_rate_request(worst_payload)
    worst_payload["CarrierInformation"] = DEFAULT_CARRIER_INFORMATION

    state_code = state_abbreviation(state) or state
    url = f"{PERSONAL_AUTO_RATE_ENDPOINT}/{state_code}/rates/latest?multiAgency=false"
    headers = _personal_auto_rate_headers()

    best_results = None
    worst_results = None

    try:
        # Submit best case
        async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as client:
            best_response = await client.post(url, headers=headers, json=best_payload)

        if not best_response.is_error:
            best_parsed = best_response.json()
            best_tx_id = best_parsed.get("transactionId")

            if best_tx_id:
                async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as client:
                    results_resp = await client.get(
                        PERSONAL_AUTO_RATE_RESULTS_ENDPOINT,
                        headers=headers,
                        params={"Id": best_tx_id}
                    )
                if not results_resp.is_error:
                    best_results = results_resp.json()

        # Submit worst case
        async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as client:
            worst_response = await client.post(url, headers=headers, json=worst_payload)

        if not worst_response.is_error:
            worst_parsed = worst_response.json()
            worst_tx_id = worst_parsed.get("transactionId")

            if worst_tx_id:
                async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as client:
                    results_resp = await client.get(
                        PERSONAL_AUTO_RATE_RESULTS_ENDPOINT,
                        headers=headers,
                        params={"Id": worst_tx_id}
                    )
                if not results_resp.is_error:
                    worst_results = results_resp.json()

    except httpx.HTTPError as exc:
        logger.exception("Quick quote request failed")
        return {
            "response_text": f"Failed to get quotes: {exc}",
        }

    # 6. Format response
    message = f"**Quick Quote Range for {city}, {state}** (Zip: {zip_code})\n\n"

    if best_results:
        best_summary = format_rate_results_summary(best_results)
        if best_summary:
            message += (
                f"**BEST CASE** (experienced driver, reliable vehicle):\n"
                f"{best_summary}\n\n"
            )

    if worst_results:
        worst_summary = format_rate_results_summary(worst_results)
        if worst_summary:
            message += (
                f"**WORST CASE** (new driver, newer vehicle):\n"
                f"{worst_summary}\n\n"
            )

    message += (
        "\nYour actual rate will fall within this range based on your specific details.\n\n"
        "**Ready for a more accurate quote?** I can collect your actual driver and "
        "vehicle information to give you a precise premium."
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
        },
        "content": [types.TextContent(type="text", text=message)],
    }
```

**Purpose:** Main entry point for quick quote flow

---

### Phase 5: Tool Registration

#### File: `insurance_server_python/widget_registry.py`

**Add to `_register_personal_auto_intake_tools()`:**

```python
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

    # Register quick quote tool FIRST
    register_tool(
        ToolRegistration(
            tool=types.Tool(
                name="get-quick-quote",
                title="Get quick auto insurance quote range",
                description=(
                    "Get an instant quote range with just zip code and number of drivers. "
                    "Returns best case (experienced driver, reliable car) and worst case "
                    "(new driver, newer car) premium estimates. Use this FIRST before "
                    "collecting detailed information. After showing the range, offer to "
                    "collect detailed information for an accurate quote."
                ),
                inputSchema=_model_schema(QuickQuoteIntake),
            ),
            handler=_get_quick_quote,
            default_response_text="Generated quick quote range.",
        )
    )

    # ... rest of existing tools
```

**Purpose:** Make quick quote available as MCP tool

---

## User Experience Flow

### Example Conversation

**Quick Quote Path:**

```
User: I need car insurance