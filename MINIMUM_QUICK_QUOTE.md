# Minimum Quick Quote Requirements

This document explains the **absolute minimum data** required to get a successful insurance quote from the Personal Auto Rate API.

## Test Verification

Run the test to verify you can get a success response:
```bash
source .venv/bin/activate
PYTHONPATH=. python insurance_server_python/test_minimum_quick_quote.py
```

## Minimum Required Fields

### 1. Customer Data

```python
{
    "Identifier": "cust-123",          # Required: Unique customer ID
    "FirstName": "John",
    "LastName": "Doe",
    "Address": {
        "Street1": "123 Main St",
        "City": "Beverly Hills",
        "State": "California",
        "ZipCode": "90210"
    },
    "MonthsAtResidence": 24,           # How long at current address
    "PriorInsuranceInformation": {
        "PriorInsurance": False,       # Boolean
        "ReasonForNoInsurance": "Other" # Required when PriorInsurance is False
    }
}
```

**Important Notes:**
- `Customer.Identifier` is **required** by the API
- If `PriorInsurance` is `False`, you **must** include `ReasonForNoInsurance`
- Valid values for `ReasonForNoInsurance`: `"Other"`, `"New Driver"`, etc.
- Do **not** include `PriorAddress` unless you have data - the API rejects `null` values

### 2. Driver Data

```python
{
    "DriverId": 1,
    "FirstName": "John",
    "LastName": "Doe",
    "DateOfBirth": "1985-06-15",       # Format: YYYY-MM-DD
    "Gender": "Male",                  # "Male" or "Female"
    "MaritalStatus": "Married",        # "Single", "Married", etc.
    "LicenseInformation": {
        "LicenseStatus": "Valid",
        "LicenseNumber": "UNKNOWN0000", # Use this placeholder if unknown
        "MonthsLicensed": 240,          # Time with license
        "MonthsMvrExperience": 240,     # MVR experience
        "MonthsStateLicensed": 240,     # Time licensed in state
        "StateLicensed": "California"   # Must match customer state
    },
    "Attributes": {
        "PropertyInsurance": True,      # Has property insurance
        "Relation": "Insured",          # Relationship to policyholder
        "ResidencyStatus": "Own",       # "Own" or "Rent"
        "ResidencyType": "Home"         # "Home", "Apartment", etc.
    }
}
```

**Important Notes:**
- `LicenseInformation` requires detailed fields - the API won't accept minimal license data
- Use `"UNKNOWN0000"` as a placeholder for `LicenseNumber` if not available
- `StateLicensed` should match the customer's state

### 3. Vehicle Data

```python
{
    "VehicleId": 1,
    "Vin": "1HGCM82633A123456",        # 17-character VIN
    "AssignedDriverId": 1,              # Must match a DriverId
    "Usage": "Work School",             # How the vehicle is used
    "GaragingAddress": {                # Where vehicle is kept
        "Street1": "123 Main St",
        "City": "Beverly Hills",
        "State": "California",
        "ZipCode": "90210"
    },
    "CoverageInformation": {
        "CollisionDeductible": "None",
        "ComprehensiveDeductible": "None",
        "RentalLimit": "None",
        "TowingLimit": "None",
        "SafetyGlassCoverage": False
    }
}
```

**Important Notes:**
- Use `Usage` (not `UseType`) - valid values: `"Work School"`, `"Commute"`, etc.
- `GaragingAddress` is **required** (often same as customer address)
- The API will decode Year/Make/Model from the VIN automatically

### 4. Policy-Level Data

```python
{
    "Identifier": "TEST_MIN_20260218113642",  # Unique quote ID
    "EffectiveDate": "2026-02-19",            # Format: YYYY-MM-DD
    "PolicyType": "Standard",                  # "Standard" (NOT "New Business")
    "Term": "Semi Annual",                     # 6-month term
    "PaymentMethod": "Default",                # Payment method
    "BumpLimits": "No Bumping",
    "PolicyCoverages": {
        "LiabilityBiLimit": "25000/50000",     # Above CA minimum
        "LiabilityPdLimit": "25000",
        "MedPayLimit": "None",
        "UninsuredMotoristBiLimit": "25000/50000",
        "UninsuredMotoristPd/CollisionDamageWaiver": False,
        "AccidentalDeathLimit": "None"
    }
}
```

**Important Notes:**
- Use `"Standard"` for `PolicyType` - **not** `"New Business"`
- Use `"Default"` for `PaymentMethod` - **not** `"Standard"`
- Policy coverages shown are slightly above CA state minimums

## Automatic Defaults

The `build_minimal_payload_with_defaults()` function automatically adds these fields if missing:

### Customer Defaults
- `DeclinedEmail`: `False`
- `DeclinedPhone`: `False`
- `NumberOfResidentsInHousehold`: `1`
- `ContactInformation`: `{}`

### Driver Defaults
- `Discounts`: All set to `False` or empty arrays
- `Violations`: Empty array
- `FinancialResponsibilityInformation`: All `False`
- `MiddleName`: `""`
- `MonthsEmployed`: `0`

### Vehicle Defaults
- `LeasedVehicle`: `False`
- `RideShare`: `False`
- `Salvaged`: `False`
- `CoverageInformation.GapCoverage`: `False`

## Common Mistakes

### ❌ Don't Do This:
```python
# Wrong: PolicyType as "New Business"
"PolicyType": "New Business"  # API rejects this

# Wrong: PaymentMethod as "Standard"
"PaymentMethod": "Standard"   # API rejects this

# Wrong: PriorAddress as null
"PriorAddress": None          # API rejects null

# Wrong: UseType instead of Usage
"UseType": "Commute"          # API expects "Usage"

# Wrong: Missing Customer.Identifier
{
    "FirstName": "John",
    # No Identifier field - API rejects
}
```

### ✅ Do This Instead:
```python
# Correct: PolicyType as "Standard"
"PolicyType": "Standard"

# Correct: PaymentMethod as "Default"
"PaymentMethod": "Default"

# Correct: Omit PriorAddress if not available
# Don't include the field at all

# Correct: Usage field
"Usage": "Work School"

# Correct: Include Customer.Identifier
{
    "Identifier": "cust-123",
    "FirstName": "John",
    ...
}
```

## Summary

The absolute minimum to get a quote requires:

1. **Customer**: Name, address, residence info, prior insurance status, **and Customer.Identifier**
2. **At least 1 Driver**: Full details including comprehensive license information
3. **At least 1 Vehicle**: VIN, usage, garaging address, and coverage preferences
4. **Policy Info**: Effective date, term, coverages, and policy type

Use the `build_minimal_payload_with_defaults()` helper function - it handles all the optional fields automatically!

## Production Usage

The `get-quick-quote` MCP tool now uses this verified minimum approach:

```python
# In tool_handlers.py
async def _get_quick_quote(arguments: Mapping[str, Any]) -> ToolInvocationResult:
    """Get a quick quote range with just zip code and number of drivers."""
    # ... generates best case and worst case using minimum viable structure
```

The tool is registered in `widget_registry.py` and available through the MCP server:
- Tool name: `get-quick-quote`
- Input: `{ZipCode: string, NumberOfDrivers: integer}`
- Output: Best case and worst case quote ranges

## Testing

The test suite includes:
1. **`test_minimum_quick_quote.py`** - Standalone test demonstrating minimum viable data
2. **`test_quick_quote_handler.py`** - Tests the actual MCP tool handler

Run either test to verify:
```bash
source .venv/bin/activate
PYTHONPATH=. python insurance_server_python/test_minimum_quick_quote.py
# OR
PYTHONPATH=. python insurance_server_python/test_quick_quote_handler.py
```

Both tests should show:
- ✅ Successfully submit rate requests
- ✅ Get transaction IDs back
- ✅ Retrieve carrier quote results for both best and worst case scenarios
