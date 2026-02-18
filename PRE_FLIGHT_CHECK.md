# Pre-Flight Checklist ✈️

Run through this checklist before starting Stage 1 testing to ensure everything is ready.

---

## ✅ Prerequisites

### 1. Python Environment
```bash
source .venv/bin/activate
python --version
# Should show: Python 3.11+ or 3.12+
```
- [ ] Python virtual environment activates
- [ ] Python version is 3.11 or higher

### 2. Dependencies Installed
```bash
pip list | grep -E "(fastmcp|pydantic|httpx|uvicorn)"
```
Expected output:
```
fastmcp           X.X.X
pydantic          2.X.X
httpx             0.X.X
uvicorn           0.X.X
```
- [ ] All dependencies are installed
- [ ] Pydantic version is 2.x

### 3. Environment Variables
```bash
cat insurance_server_python/.env | grep PERSONAL_AUTO_RATE_API_KEY
```
- [ ] .env file exists
- [ ] PERSONAL_AUTO_RATE_API_KEY is set (not empty)

### 4. Backend Tests Pass
```bash
pytest insurance_server_python/tests/test_conversational_batch.py -v
```
Expected: `6 passed`
- [ ] All 6 conversational batch tests pass
- [ ] No errors in test output

---

## ✅ Server Verification

### 5. Server Starts
```bash
# In Terminal 1
uvicorn insurance_server_python.main:app --port 8000 &
sleep 3
```
- [ ] Server starts without errors
- [ ] See: "Uvicorn running on http://127.0.0.1:8000"

### 6. Tools Are Registered
```bash
curl -s http://localhost:8000/mcp/tools | python3 -m json.tool | grep '"name"' | wc -l
```
Expected: `6` (six tools)
- [ ] Six tools are registered

### 7. Verify Specific Tools
```bash
curl -s http://localhost:8000/mcp/tools | grep -o '"collect-personal-auto-[^"]*"'
```
Expected output:
```
"collect-personal-auto-customer"
"collect-personal-auto-drivers"
"collect-personal-auto-vehicles"
```
- [ ] Customer collection tool exists
- [ ] Driver collection tool exists
- [ ] Vehicle collection tool exists

### 8. Test Customer Tool Schema
```bash
curl -s http://localhost:8000/mcp/tools | python3 -c "
import sys, json
tools = json.load(sys.stdin)['tools']
customer_tool = next(t for t in tools if t['name'] == 'collect-personal-auto-customer')
print('✓ Customer tool found')
print(f'✓ Has inputSchema: {\"inputSchema\" in customer_tool}')
print(f'✓ Description: {customer_tool[\"description\"][:60]}...')
"
```
- [ ] Customer tool has inputSchema
- [ ] Description mentions "Batch 1" and "conversational"

---

## ✅ Network Setup

### 9. Ngrok Installed
```bash
which ngrok || echo "❌ ngrok not found - install from ngrok.com"
```
- [ ] ngrok is installed
- [ ] Can run `ngrok http 8000`

### 10. Ngrok Works
```bash
# In Terminal 2
ngrok http 8000 > /dev/null 2>&1 &
NGROK_PID=$!
sleep 3
curl -s http://localhost:4040/api/tunnels | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    tunnel = data['tunnels'][0]['public_url']
    print(f'✓ Ngrok tunnel: {tunnel}')
except:
    print('❌ Ngrok not running')
"
kill $NGROK_PID 2>/dev/null
```
- [ ] Ngrok creates tunnel
- [ ] Can access ngrok dashboard at http://localhost:4040

---

## ✅ ChatGPT Access

### 11. ChatGPT Account
- [ ] Have access to chatgpt.com
- [ ] Can access Settings
- [ ] Can see "Connectors" section in Settings

### 12. MCP Connector Support
- [ ] ChatGPT account supports MCP connectors
- [ ] Can click "Add connector" button

---

## ✅ Validation Utilities

### 13. Required Fields Config
```bash
test -f insurance_server_python/minimal_fields_config.json && echo "✓ Config exists" || echo "❌ Config missing"
```
- [ ] minimal_fields_config.json exists

### 14. Validation Function Works
```bash
python3 -c "
from insurance_server_python.utils import validate_required_fields
data = {'FirstName': 'John', 'Address': {'City': 'SF'}}
required = ['FirstName', 'Address.State']
missing = validate_required_fields(data, required)
assert 'Address.State' in missing, 'Validation failed'
print('✓ Validation function works')
"
```
- [ ] Validation function works correctly

---

## ✅ Documentation

### 15. Testing Docs Exist
```bash
ls -1 *.md | grep -E "(START_HERE|TESTING_QUICK|INCREMENTAL_TEST)"
```
Expected:
```
START_HERE.md
TESTING_QUICK_REFERENCE.md
INCREMENTAL_TEST_PLAN.md
```
- [ ] All testing documentation exists

---

## 🎯 Pre-Flight Complete!

### Final Checklist Summary

Count your checkmarks:
- **Minimum to proceed**: 13/15 (at least)
- **Ideal**: 15/15

### If Everything Passes ✅

You're ready to start! Next steps:
1. Kill the test server: `pkill -f "uvicorn.*insurance_server_python"`
2. Open **START_HERE.md**
3. Follow the 5-minute first test

### If Anything Fails ❌

**Common Issues**:

**Dependencies not installed?**
```bash
pip install -r insurance_server_python/requirements.txt
```

**No API key?**
```bash
cp insurance_server_python/.env.example insurance_server_python/.env
# Edit .env and add your API key
```

**Tests failing?**
```bash
# Run with verbose output to see what's failing
pytest insurance_server_python/tests/test_conversational_batch.py -vv
```

**Server won't start?**
```bash
# Check for port conflicts
lsof -i :8000
# Kill any existing process
pkill -f "uvicorn.*insurance"
```

**Ngrok not working?**
- Download from https://ngrok.com/download
- Or: `brew install ngrok` (on macOS)

---

## 📋 Quick Smoke Test

Want to do a quick end-to-end smoke test before ChatGPT?

```bash
# Start server
uvicorn insurance_server_python.main:app --port 8000 &
SERVER_PID=$!
sleep 2

# Test customer tool
curl -X POST http://localhost:8000/mcp/tools/collect-personal-auto-customer \
  -H "Content-Type: application/json" \
  -d '{
    "Customer": {
      "FirstName": "John",
      "LastName": "Smith",
      "Address": {
        "Street1": "123 Main St",
        "City": "SF",
        "State": "CA",
        "ZipCode": "94102"
      },
      "MonthsAtResidence": 24,
      "PriorInsuranceInformation": {
        "PriorInsurance": true
      }
    }
  }' | python3 -m json.tool

# Cleanup
kill $SERVER_PID
```

Expected: Response with `"customer_complete": true`

---

## ✈️ Ready for Takeoff!

If you passed the pre-flight check, you're ready to:
1. Open **START_HERE.md**
2. Follow the 5-minute setup
3. Run your first test!

**Good luck! 🚀**
