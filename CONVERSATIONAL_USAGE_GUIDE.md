# Conversational Batch Collection - Usage Guide

## Overview

The insurance quote system now uses **pure conversational batch collection** - no form widgets, just natural conversation where Claude asks questions and users respond in chat.

## How It Works

### 1. Three Batch Collection Tools

**Batch 1: Customer Information**
- Tool: `collect-personal-auto-customer`
- Collects: Name, address, months at residence, prior insurance
- Required fields: 8

**Batch 2: Driver Information**
- Tool: `collect-personal-auto-drivers`
- Collects: Driver name, DOB, gender, marital status, license info, residency details
- Required fields per driver: 10
- Can append missing customer fields (forward-appending)

**Batch 3: Vehicle Information**
- Tool: `collect-personal-auto-vehicles`
- Collects: VIN, year, make, model, usage, coverage preferences
- Required fields per vehicle: 15
- Can append missing customer/driver fields (forward-appending)

### 2. Validation & Forward-Appending

Each tool:
- Validates required fields
- Returns list of missing fields
- Can accept fields from earlier batches to fill gaps
- Only proceeds to rate request when ALL required fields collected

### 3. Typical Conversation Flow

```
User: "I need car insurance"

Claude: "I'd be happy to help! Let's start with your basic information.
What's your name, address, how long you've lived there, and do you currently have insurance?"

User: "John Smith, 123 Main St, San Francisco CA 94102, 2 years, yes"

Claude: [Calls collect-personal-auto-customer]
✓ Response: "Captured customer profile for John Smith."

Claude: "Great! Now tell me about the drivers. For each driver I need:
- Full name, date of birth
- Gender and marital status
- License status
- Whether you have property insurance
- Your relationship to the primary insured
- Residency details"

User: "Just me - DOB 1/1/1980, male, married, valid license,
I have home insurance, I'm the primary, US citizen, I own my home"

Claude: [Calls collect-personal-auto-drivers with driver data]
✓ Response: "Captured driver profile for John Smith."

Claude: "Perfect! Any other drivers?"

User: "No, just me"

Claude: "Got it. Now tell me about your vehicle..."

User: "2020 Honda Accord sedan, VIN 1HGCV1F3XLA123456, I use it for commuting,
$500 collision and comprehensive deductibles, $50/day rental coverage,
$100 towing, 12,000 miles/year, 20 miles to work, 80% commuting"

Claude: [Calls collect-personal-auto-vehicles]
✓ Response: "Captured vehicle information for 2020 Honda Accord."

Claude: "Excellent! I have everything I need. Let me get your quotes..."
[Calls request-personal-auto-rate]
[Displays rate results widget]
```

## Forward-Appending Example

If a field was missed in earlier batches, Claude appends it to the next batch:

```
Batch 1 (Customer): User forgets to mention their state

Claude: [collect-personal-auto-customer]
Response: "Still need: Address.State"

Batch 2 (Drivers): Claude asks for driver info + missing state

Claude: "Now tell me about the drivers. Also, what state is your address in?"

User: "California. For drivers: John Smith, DOB 1/1/1980..."

Claude: [collect-personal-auto-drivers with customer.address.state = "CA" + driver data]
✓ Response: "Captured driver profile for John Smith."
[Customer.Address.State now filled in]
```

## API Response Format

### Tool Input (Example: collect-personal-auto-customer)

```json
{
  "Customer": {
    "FirstName": "John",
    "LastName": "Smith",
    "Address": {
      "Street1": "123 Main St",
      "City": "San Francisco",
      "State": "CA",
      "ZipCode": "94102"
    },
    "MonthsAtResidence": 24,
    "PriorInsuranceInformation": {
      "PriorInsurance": true
    }
  }
}
```

### Tool Response

```json
{
  "structured_content": {
    "customer": { ... },
    "validation": {
      "customer_complete": true,
      "missing_fields": []
    }
  },
  "response_text": "Captured customer profile for John Smith."
}
```

## Required Fields Reference

### Customer (8 required)
- FirstName
- LastName
- Address.Street1
- Address.City
- Address.State
- Address.ZipCode
- MonthsAtResidence
- PriorInsuranceInformation.PriorInsurance

### Driver (10 required per driver)
- FirstName
- LastName
- DateOfBirth
- Gender
- MaritalStatus
- LicenseInformation.LicenseStatus
- Attributes.PropertyInsurance
- Attributes.Relation
- Attributes.ResidencyStatus
- Attributes.ResidencyType

### Vehicle (15 required per vehicle)
- Vin
- Year
- Make
- Model
- BodyType
- UseType
- AssignedDriverId
- CoverageInformation.CollisionDeductible
- CoverageInformation.ComprehensiveDeductible
- CoverageInformation.RentalLimit
- CoverageInformation.TowingLimit
- CoverageInformation.SafetyGlassCoverage
- PercentToWork
- MilesToWork
- AnnualMiles

## Testing

### Start the server:
```bash
source .venv/bin/activate
INSURANCE_LOG_LEVEL=DEBUG uvicorn insurance_server_python.main:app --port 8000
```

### Test in ChatGPT:
1. Expose server via ngrok: `ngrok http 8000`
2. Add connector in ChatGPT Settings: `https://<your-ngrok>.ngrok-free.app/mcp`
3. Start conversation: "I need car insurance"
4. Follow conversational flow, providing information in natural language

### Monitor validation:
Watch server logs for validation status:
```
INFO: Captured customer profile for John Smith. Still need: Address.State
INFO: Captured driver profile for John Smith.
INFO: Captured vehicle information for 2020 Honda Accord.
```

## Benefits

✅ **No Form Complexity**: Users just type naturally in chat
✅ **Forward-Only Flow**: Missing fields appended to next batch (reduces fatigue)
✅ **Flexible Input**: Users can provide info in any format/order
✅ **Clear Validation**: Tools return exactly what's missing
✅ **Conversational**: Can ask questions, clarify, handle edge cases

## Next Steps

1. **Prompt Engineering**: Optimize Claude's batch questions for clarity and brevity
2. **Error Handling**: Add conversational error recovery for invalid data
3. **Optional Fields**: Support optional fields with defaults
4. **Multi-Driver/Vehicle**: Test with multiple drivers and vehicles
