# Incremental Testing Plan - Conversational Batch Collection

## Overview
This plan starts with a minimal proof-of-concept (Batch 1 only) and builds up incrementally with manual validation checkpoints at each stage.

---

## Prerequisites

### Setup
```bash
# 1. Start the server
source .venv/bin/activate
INSURANCE_LOG_LEVEL=DEBUG uvicorn insurance_server_python.main:app --port 8000

# 2. Expose via ngrok (in another terminal)
ngrok http 8000

# 3. Add to ChatGPT
# Settings → Connectors → Add connector
# URL: https://<your-ngrok>.ngrok-free.app/mcp
```

### Verification
Before testing, verify tools are registered:
```bash
curl http://localhost:8000/mcp/tools | jq '.tools[] | .name'
```

Expected output:
```
"insurance-state-selector"
"collect-personal-auto-customer"
"collect-personal-auto-drivers"
"collect-personal-auto-vehicles"
"request-personal-auto-rate"
"retrieve-personal-auto-rate-results"
```

---

## Stage 1: Proof of Concept - Customer Batch Only

**Goal**: Verify that Batch 1 (customer collection) works end-to-end with validation.

### Test 1.1: Complete Customer Data (Happy Path)

**Conversation**:
```
You: "I need car insurance"

Expected: Claude should ask for customer information (name, address, months at residence, prior insurance)

You: "John Smith, 123 Main St, San Francisco CA 94102, lived here 24 months, yes I have insurance"

Expected: Claude calls collect-personal-auto-customer
```

**Validation Checklist**:
- [ ] Claude recognized the request for insurance
- [ ] Claude asked for customer information
- [ ] Claude called `collect-personal-auto-customer` tool
- [ ] Tool response says "Captured customer profile for John Smith"
- [ ] Tool response validation shows `customer_complete: true`
- [ ] Tool response validation shows `missing_fields: []`

**Check Server Logs**:
```bash
# Look for these log lines:
grep "collect-personal-auto-customer" /tmp/server.log
grep "customer_complete" /tmp/server.log
```

**If it fails**: Stop here and debug before proceeding.

---

### Test 1.2: Incomplete Customer Data

**Conversation**:
```
You: "I need insurance. My name is Jane Doe and I live in Los Angeles"

Expected: Claude calls collect-personal-auto-customer
```

**Validation Checklist**:
- [ ] Tool response says "Still need: Address.Street1, Address.ZipCode, MonthsAtResidence, PriorInsuranceInformation.PriorInsurance"
- [ ] Tool response validation shows `customer_complete: false`
- [ ] Tool response validation lists exactly which fields are missing
- [ ] Claude asks follow-up questions for missing fields

**Manual Test**:
Provide the missing information:
```
You: "456 Sunset Blvd, ZIP 90028, lived here 12 months, no prior insurance"
```

**Expected**:
- Claude calls tool again with updated data
- Validation shows `customer_complete: true`

---

### Test 1.3: Minimal Customer Data

**Conversation**:
```
You: "Get me a quote. I'm Bob at 789 Oak St, NYC 10001"

Expected: Claude extracts what it can, calls tool
```

**Validation Checklist**:
- [ ] Tool extracts: FirstName (Bob), Address.Street1, Address.City (NYC), Address.ZipCode (10001)
- [ ] Tool response lists missing: LastName, Address.State, MonthsAtResidence, PriorInsurance
- [ ] Claude asks specifically for the missing fields

**Success Criteria for Stage 1**:
✅ All 3 tests pass
✅ Tool correctly identifies complete vs incomplete data
✅ Claude follows up on missing fields
✅ Server logs show proper tool invocations

**If Stage 1 passes**: Proceed to Stage 2

---

## Stage 2: Driver Batch Collection

**Goal**: Add driver collection (Batch 2), ensure it works independently and with forward-appending.

### Test 2.1: Complete Driver Data

**Conversation**:
```
You: "I need insurance"
Claude: [asks for customer info]
You: "John Smith, 123 Main St, SF CA 94102, 24 months, yes insurance"
Claude: [captures customer, asks for driver info]
You: "Driver is me, John Smith, DOB 1/1/1980, male, married, valid California license, I have homeowners insurance, I'm the primary insured, US citizen, I own my home"

Expected: Claude calls collect-personal-auto-drivers
```

**Validation Checklist**:
- [ ] Customer batch completed first
- [ ] Claude then asked for driver information
- [ ] Tool response says "Captured driver profile for John Smith"
- [ ] Tool response validation shows `drivers_complete: true`
- [ ] Tool response validation shows `customer_complete: true` (customer data passed through)
- [ ] Claude asks "Any other drivers?"

---

### Test 2.2: Forward-Appending Customer Fields

**Conversation**:
```
You: "I need insurance"
Claude: [asks for customer info]
You: "John Smith, 123 Main St, San Francisco 94102"
  [Note: Missing state, months, prior insurance]

Claude: [calls tool, notes missing fields, asks for driver info + missing customer fields]
You: "California is my state. Driver is me, DOB 1/1/1980, male, married, valid license, homeowners, primary, citizen, own home. Lived here 36 months, no prior insurance"

Expected: Claude calls collect-personal-auto-drivers with BOTH customer missing fields AND driver data
```

**Validation Checklist**:
- [ ] First call: customer_complete = false
- [ ] Second call includes customer.address.state = "California"
- [ ] Second call includes customer.monthsAtResidence = 36
- [ ] Second call includes customer.priorInsurance = false
- [ ] Tool response validation shows both customer_complete = true AND drivers_complete = true
- [ ] Forward-appending worked!

---

### Test 2.3: Multiple Drivers

**Conversation**:
```
[After customer info is captured]
Claude: [asks for driver info]
You: "Driver 1 is me, John Smith, DOB 1/1/1980, male, married, valid license..."
Claude: "Any other drivers?"
You: "Yes, my spouse Jane Smith, DOB 5/15/1982, female, married, valid license..."
Claude: "Any other drivers?"
You: "No"

Expected: RatedDrivers array has 2 entries
```

**Validation Checklist**:
- [ ] First driver captured successfully
- [ ] Claude explicitly asked "Any other drivers?"
- [ ] Second driver captured successfully
- [ ] Tool response shows 2 drivers
- [ ] Both drivers have complete required fields

**Success Criteria for Stage 2**:
✅ All 3 tests pass
✅ Forward-appending works correctly
✅ Multiple drivers handled properly
✅ No regressions in customer batch

**If Stage 2 passes**: Proceed to Stage 3

---

## Stage 3: Vehicle Batch Collection

**Goal**: Add vehicle collection (Batch 3), ensure it works with forward-appending from both earlier batches.

### Test 3.1: Complete Vehicle Data

**Conversation**:
```
[After customer and driver info captured]
Claude: [asks for vehicle info]
You: "2020 Honda Accord sedan, VIN 1HGCV1F3XLA123456, I use it for commuting, I'm the primary driver, $500 collision deductible, $500 comprehensive, $50/day rental coverage, $100 towing, yes to glass coverage, 12000 miles per year, 20 miles to work each way, 80% used for commuting"

Expected: Claude calls collect-personal-auto-vehicles
```

**Validation Checklist**:
- [ ] Tool response says "Captured vehicle information for 2020 Honda Accord"
- [ ] Tool response validation shows `vehicles_complete: true`
- [ ] All 15 required vehicle fields captured
- [ ] Claude asks "Any other vehicles?"

---

### Test 3.2: Forward-Appending from Multiple Batches

**Conversation**:
```
You: "I need insurance"
Claude: [asks for customer]
You: "John Smith, 123 Main St, SF"
  [Missing: state, zip, months, prior insurance]

Claude: [asks for driver + missing customer fields]
You: "Driver is me, DOB 1/1/1980, male, married, valid license..."
  [Missing: property insurance, residency details]
  [Also provide: CA, 94102 for customer]

Claude: [asks for vehicle + missing driver/customer fields]
You: "2020 Honda Accord, VIN 1HGCV1F3XLA123456..."
  [Also provide: "yes homeowners insurance, US citizen, own home, lived there 24 months, yes prior insurance"]

Expected: All three batches completed in vehicle tool call
```

**Validation Checklist**:
- [ ] Vehicle tool call includes updated customer data
- [ ] Vehicle tool call includes updated driver data
- [ ] Vehicle tool call includes complete vehicle data
- [ ] All three validations show complete: true
- [ ] missing_fields = []

---

### Test 3.3: Multiple Vehicles

**Conversation**:
```
[After customer and driver info captured]
Claude: [asks for vehicle]
You: "2020 Honda Accord, VIN 1HGCV1F3XLA123456, commute..."
Claude: "Any other vehicles?"
You: "Yes, 2018 Toyota Camry, VIN 2T1BURHE0JC123456, pleasure..."
Claude: "Any other vehicles?"
You: "No"

Expected: Vehicles array has 2 entries
```

**Validation Checklist**:
- [ ] First vehicle captured
- [ ] Claude asked "Any other vehicles?"
- [ ] Second vehicle captured
- [ ] Both vehicles have all 15 required fields

**Success Criteria for Stage 3**:
✅ All 3 tests pass
✅ Vehicle collection works correctly
✅ Forward-appending from both earlier batches works
✅ Multiple vehicles handled properly

**If Stage 3 passes**: Proceed to Stage 4

---

## Stage 4: End-to-End Flow with Rate Request

**Goal**: Complete full flow from customer → driver → vehicle → rate request → results display.

### Test 4.1: Complete Happy Path

**Conversation**:
```
You: "I need car insurance"
[Provide complete customer info]
[Provide complete driver info]
[Provide complete vehicle info]

Expected: Claude calls request-personal-auto-rate
```

**Validation Checklist**:
- [ ] All three batches completed
- [ ] Claude called `request-personal-auto-rate` with full payload
- [ ] Rate request succeeded (or failed with clear error)
- [ ] If succeeded: Results widget displayed
- [ ] If succeeded: Can see carrier premiums

---

### Test 4.2: Minimal Path with Defaults

**Conversation**:
```
You: "Get me a quote"
[Provide ONLY the required fields - nothing extra]
[Customer: name, address, months, prior insurance]
[Driver: name, DOB, gender, marital, license, property, relation, residency]
[Vehicle: VIN, year, make, model, body, use, driver, coverages, miles]

Expected: Tool applies defaults for optional fields
```

**Validation Checklist**:
- [ ] Rate request payload includes defaults for optional fields
- [ ] Check server logs: "Detected minimal submission, applying defaults"
- [ ] Rate request succeeds
- [ ] Results displayed

---

## Stage 5: Edge Cases and Error Handling

**Goal**: Test error scenarios and edge cases.

### Test 5.1: Invalid Data

**Conversation**:
```
You: "John Smith, invalid address"
```

**Expected**:
- Claude handles gracefully
- Asks for clarification
- Doesn't crash

### Test 5.2: Out-of-Order Information

**Conversation**:
```
You: "I need insurance. I have a 2020 Honda Accord"
  [User provides vehicle info before customer info]
```

**Expected**:
- Claude redirects to customer info first
- Doesn't lose vehicle info

### Test 5.3: Changing Answers

**Conversation**:
```
You: "John Smith, 123 Main St..."
Claude: [captures customer]
You: "Actually, I live at 456 Oak St"
```

**Expected**:
- Claude updates customer info
- Can re-call tool with corrected data

---

## Success Criteria - Full Implementation

✅ **Stage 1**: Customer batch works (3/3 tests)
✅ **Stage 2**: Driver batch works with forward-appending (3/3 tests)
✅ **Stage 3**: Vehicle batch works (3/3 tests)
✅ **Stage 4**: End-to-end rate request works (2/2 tests)
✅ **Stage 5**: Edge cases handled gracefully (3/3 tests)

**Total**: 14 test scenarios

---

## Debugging Tips

### If Claude doesn't call the tools:
1. Check tool descriptions are clear
2. Verify connector is active in ChatGPT
3. Try explicitly: "Use the collect-personal-auto-customer tool"

### If validation is incorrect:
1. Check server logs for validation output
2. Verify minimal_fields_config.json has correct field paths
3. Test validation function directly in Python

### If forward-appending doesn't work:
1. Check server logs - is customer data being passed to driver tool?
2. Verify CumulativeDriverIntake accepts customer field
3. Check tool response structure

### Server logs to monitor:
```bash
# Watch server logs in real-time
tail -f /tmp/server.log | grep -E "(collect-personal-auto|validation|missing_fields)"

# Or with debug logging
INSURANCE_LOG_LEVEL=DEBUG uvicorn insurance_server_python.main:app --port 8000 2>&1 | tee /tmp/server.log
```

### Quick validation test:
```python
# Test validation function directly
from insurance_server_python.utils import validate_required_fields

data = {
    "FirstName": "John",
    "LastName": "Smith",
    "Address": {"City": "SF"}
}

required = ["FirstName", "LastName", "Address.Street1", "Address.State"]
missing = validate_required_fields(data, required)
print(f"Missing: {missing}")  # Should show: ['Address.Street1', 'Address.State']
```

---

## Rollback Plan

If any stage fails and can't be debugged quickly:
1. Stop at the last successful stage
2. Document the failure
3. Roll back code changes if needed
4. Debug in isolation before proceeding

---

## Next Steps After All Tests Pass

1. **Performance Testing**: Multiple users, concurrent requests
2. **Prompt Optimization**: Make Claude's questions more natural
3. **Error Messages**: Improve clarity of validation messages
4. **Optional Fields**: Add support for optional fields
5. **Production Deploy**: Move to production environment
