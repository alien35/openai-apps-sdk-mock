# Testing Quick Reference Card

## Stage 1: Customer Batch Only (Proof of Concept)

### Quick Start
```bash
# Terminal 1: Start server
source .venv/bin/activate
INSURANCE_LOG_LEVEL=DEBUG uvicorn insurance_server_python.main:app --port 8000

# Terminal 2: Expose via ngrok
ngrok http 8000

# Add to ChatGPT: https://<your-ngrok>.ngrok-free.app/mcp
```

### Test 1.1: Complete Customer (Happy Path)
**Say in ChatGPT**:
```
"I need car insurance. I'm John Smith at 123 Main St, San Francisco CA 94102.
I've lived here 24 months and yes I have insurance."
```

**✅ Success looks like**:
- Claude calls `collect-personal-auto-customer`
- Response: "Captured customer profile for John Smith"
- Server log: `"customer_complete": true`
- Server log: `"missing_fields": []`

**❌ Failure looks like**:
- Claude doesn't call the tool
- Response shows missing fields when all were provided
- Server error in logs

---

### Test 1.2: Incomplete Customer
**Say in ChatGPT**:
```
"I need insurance. My name is Jane Doe and I live in Los Angeles"
```

**✅ Success looks like**:
- Claude calls tool
- Response: "Still need: Address.Street1, Address.ZipCode, MonthsAtResidence, PriorInsurance"
- Server log: `"customer_complete": false`
- Claude asks follow-up questions

**Then provide missing info**:
```
"456 Sunset Blvd, ZIP 90028, lived here 12 months, no prior insurance"
```

**✅ Success looks like**:
- Claude calls tool again
- Response: Customer complete
- Server log: `"customer_complete": true`

---

### Test 1.3: Minimal Customer
**Say in ChatGPT**:
```
"Get me a quote. I'm Bob at 789 Oak St, NYC 10001"
```

**✅ Success looks like**:
- Tool extracts: Bob, 789 Oak St, NYC, 10001
- Response lists missing: LastName, State, MonthsAtResidence, PriorInsurance
- Claude asks specifically for missing fields

---

## 🎯 Stage 1 Pass Criteria

Before moving to Stage 2, verify:
- [ ] Test 1.1 passes (complete customer)
- [ ] Test 1.2 passes (incomplete then complete)
- [ ] Test 1.3 passes (minimal extraction)
- [ ] Server logs show correct validation
- [ ] No errors in server logs

---

## Stage 2: Driver Batch

### Test 2.1: Complete Driver
**Say after customer is captured**:
```
"Driver is me, John Smith, DOB 1/1/1980, male, married,
valid California license, I have homeowners insurance,
I'm the primary insured, US citizen, I own my home"
```

**✅ Success looks like**:
- Claude calls `collect-personal-auto-drivers`
- Response: "Captured driver profile for John Smith"
- Server log: `"drivers_complete": true`
- Claude asks: "Any other drivers?"

---

### Test 2.2: Forward-Appending
**Say for customer (incomplete)**:
```
"John Smith, 123 Main St, San Francisco 94102"
```
(Missing: state, months, prior insurance)

**Then say for driver + missing customer fields**:
```
"California is my state. Driver is me, DOB 1/1/1980, male, married,
valid license, homeowners insurance, primary insured, US citizen,
own home. Lived here 36 months, no prior insurance"
```

**✅ Success looks like**:
- Second tool call includes customer.address.state = "California"
- Second tool call includes monthsAtResidence = 36
- Server log: `"customer_complete": true` AND `"drivers_complete": true`
- Forward-appending worked!

---

## 🎯 Stage 2 Pass Criteria

Before moving to Stage 3, verify:
- [ ] Test 2.1 passes (complete driver)
- [ ] Test 2.2 passes (forward-appending)
- [ ] Multiple drivers work (if tested)
- [ ] No regressions in customer batch
- [ ] Server logs show correct validation

---

## Stage 3: Vehicle Batch

### Test 3.1: Complete Vehicle
**Say after customer and driver captured**:
```
"2020 Honda Accord sedan, VIN 1HGCV1F3XLA123456,
I use it for commuting, I'm the primary driver,
$500 collision deductible, $500 comprehensive,
$50/day rental coverage, $100 towing,
yes to glass coverage, 12000 miles per year,
20 miles to work each way, 80% used for commuting"
```

**✅ Success looks like**:
- Claude calls `collect-personal-auto-vehicles`
- Response: "Captured vehicle information for 2020 Honda Accord"
- Server log: `"vehicles_complete": true`
- Claude asks: "Any other vehicles?"

---

## 🎯 Stage 3 Pass Criteria

Before moving to Stage 4, verify:
- [ ] Test 3.1 passes (complete vehicle)
- [ ] Forward-appending from earlier batches works
- [ ] Multiple vehicles work (if tested)
- [ ] All three validation flags can be true

---

## Stage 4: End-to-End Rate Request

### Test 4.1: Complete Flow
**Provide all info across the three batches**

**✅ Success looks like**:
- All three batches complete
- Claude calls `request-personal-auto-rate`
- Rate request succeeds (status 200)
- Results widget displays
- Can see carrier premiums

---

## 🎯 Stage 4 Pass Criteria

- [ ] Full flow works end-to-end
- [ ] Rate request succeeds
- [ ] Results display correctly
- [ ] Can retrieve results with identifier

---

## Quick Debug Commands

### Check if tools are registered:
```bash
curl http://localhost:8000/mcp/tools | jq '.tools[] | .name'
```

### Watch server logs:
```bash
tail -f /tmp/server.log | grep -E "(collect-personal-auto|validation|missing_fields)"
```

### Test validation function directly:
```python
from insurance_server_python.utils import validate_required_fields

data = {"FirstName": "John", "LastName": "Smith"}
required = ["FirstName", "LastName", "Address.State"]
missing = validate_required_fields(data, required)
print(missing)  # Should show: ['Address.State']
```

### Quick response check:
```python
# In Python shell
import json
response = '''{"structured_content": {"validation": {"customer_complete": true}}}'''
data = json.loads(response)
print(data["structured_content"]["validation"])
```

---

## Common Issues

### Claude doesn't call the tool
- **Fix**: Check connector is active in ChatGPT settings
- **Fix**: Try saying explicitly: "Use the collect-personal-auto-customer tool"
- **Fix**: Verify ngrok URL is correct

### Wrong validation results
- **Fix**: Check server logs for actual validation output
- **Fix**: Verify field names match minimal_fields_config.json
- **Fix**: Test validate_required_fields function directly

### Forward-appending doesn't work
- **Fix**: Check if customer data is in driver tool call (server logs)
- **Fix**: Verify CumulativeDriverIntake model accepts customer field
- **Fix**: Check tool handler passes customer data through

### Server crashes
- **Fix**: Check .env has PERSONAL_AUTO_RATE_API_KEY
- **Fix**: Look for Python exceptions in server logs
- **Fix**: Verify all dependencies installed: `pip install -r requirements.txt`

---

## Success Indicators

### Stage 1 ✅
- Customer batch works with complete and incomplete data
- Validation correctly identifies missing fields
- Claude follows up appropriately

### Stage 2 ✅
- Driver batch works independently
- Forward-appending fills customer gaps
- Multiple drivers supported

### Stage 3 ✅
- Vehicle batch works
- Can forward-append from both earlier batches
- Multiple vehicles supported

### Stage 4 ✅
- End-to-end flow completes
- Rate request succeeds
- Results display correctly

---

## Emergency Stop

If anything goes wrong:
1. Stop the server (Ctrl+C)
2. Check logs: `tail -100 /tmp/server.log`
3. Run tests: `pytest insurance_server_python/tests/test_conversational_batch.py -v`
4. Document the issue
5. Roll back if needed

---

## Next Test Checklist

After completing a stage, update this checklist:

- [ ] Stage 1: Customer Batch Only - READY TO TEST
- [ ] Stage 2: Driver Batch
- [ ] Stage 3: Vehicle Batch
- [ ] Stage 4: End-to-End
- [ ] Stage 5: Edge Cases

**Current Stage**: Start with Stage 1, Test 1.1
