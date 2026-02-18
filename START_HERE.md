# 🚀 Start Here - First Test (5 minutes)

## Goal
Get Stage 1, Test 1.1 working: Complete customer data capture

## Step 1: Start the Server (1 min)

Open Terminal 1:
```bash
cd /Users/alexanderleon/mi/openai-apps-sdk-examples
source .venv/bin/activate
INSURANCE_LOG_LEVEL=DEBUG uvicorn insurance_server_python.main:app --port 8000
```

**✅ You should see**:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**❌ If you see errors**: Check .env file exists and has PERSONAL_AUTO_RATE_API_KEY

---

## Step 2: Verify Tools (1 min)

Open Terminal 2:
```bash
curl http://localhost:8000/mcp/tools 2>/dev/null | grep -o '"name":"[^"]*"' | head -6
```

**✅ You should see**:
```
"name":"insurance-state-selector"
"name":"collect-personal-auto-customer"
"name":"collect-personal-auto-drivers"
"name":"collect-personal-auto-vehicles"
"name":"request-personal-auto-rate"
"name":"retrieve-personal-auto-rate-results"
```

**❌ If you don't see these**: Server didn't start correctly, check Terminal 1 for errors

---

## Step 3: Expose via Ngrok (1 min)

In Terminal 2:
```bash
ngrok http 8000
```

**✅ You should see**:
```
Forwarding  https://xxxx-xx-xx-xx-xx.ngrok-free.app -> http://localhost:8000
```

**Copy that https:// URL** - you'll need it in the next step

---

## Step 4: Add to ChatGPT (1 min)

1. Open ChatGPT (chatgpt.com)
2. Click Settings (bottom left)
3. Go to "Connectors"
4. Click "Add connector"
5. Paste: `https://YOUR-NGROK-URL.ngrok-free.app/mcp`
6. Click "Add"

**✅ You should see**: Green checkmark next to the connector

**❌ If connection fails**:
- Check ngrok is still running
- Check server is still running
- Verify URL ends with `/mcp`

---

## Step 5: First Test! (2 min)

Go back to ChatGPT main chat and type:

```
I need car insurance. I'm John Smith at 123 Main St, San Francisco CA 94102.
I've lived here 24 months and yes I have insurance.
```

### What Should Happen:

1. **Claude should respond** with something like:
   - "I'll help you get a car insurance quote..."
   - May call `insurance-state-selector` first
   - Then calls `collect-personal-auto-customer`

2. **Watch Terminal 1** (server logs):
   ```
   INFO: Tool invoked: collect-personal-auto-customer
   ```

3. **Claude should confirm**:
   - "Captured customer profile for John Smith"
   - May ask about drivers next

### Success Indicators ✅:
- Claude called `collect-personal-auto-customer` tool
- Response mentions "John Smith"
- No errors in server logs
- Claude proceeds to ask about drivers

### If It Doesn't Work ❌:

**Claude doesn't call the tool?**
- Say explicitly: "Use the collect-personal-auto-customer tool"
- Check connector is enabled in ChatGPT settings
- Refresh ChatGPT page

**Server errors?**
- Check Terminal 1 for error messages
- Verify .env file has API key
- Run tests: `pytest insurance_server_python/tests/test_conversational_batch.py -v`

**Claude calls wrong tool?**
- That's okay! As long as it eventually calls collect-personal-auto-customer
- The flow may vary slightly

---

## Step 6: Verify Validation (1 min)

In Terminal 1 (server logs), search for:
```bash
grep -i "customer_complete"
```

**✅ You should see**:
```
"customer_complete": true
```

**And**:
```
"missing_fields": []
```

---

## 🎉 Success!

If you got here, you've completed Stage 1, Test 1.1!

### Next Steps:

1. **Try Test 1.2** (incomplete customer data)
   - See `TESTING_QUICK_REFERENCE.md`

2. **If Test 1.1 failed**:
   - Check `INCREMENTAL_TEST_PLAN.md` → Debugging Tips
   - Review server logs in Terminal 1
   - Run unit tests to verify backend works

3. **Continue to Stage 2**:
   - Only after all Stage 1 tests pass
   - See `INCREMENTAL_TEST_PLAN.md` → Stage 2

---

## Quick Reference Files:

- **START_HERE.md** ← You are here (first test)
- **TESTING_QUICK_REFERENCE.md** ← Quick lookup during testing
- **INCREMENTAL_TEST_PLAN.md** ← Full detailed test plan
- **IMPLEMENTATION_SUMMARY.md** ← What was built
- **CONVERSATIONAL_USAGE_GUIDE.md** ← How it works

---

## Emergency Commands

**Stop server**: Ctrl+C in Terminal 1

**Stop ngrok**: Ctrl+C in Terminal 2

**Restart server**:
```bash
source .venv/bin/activate
INSURANCE_LOG_LEVEL=DEBUG uvicorn insurance_server_python.main:app --port 8000
```

**Check if still working**:
```bash
curl http://localhost:8000/mcp/tools 2>/dev/null | grep collect-personal-auto-customer
```

---

## Support

If stuck, check:
1. Terminal 1 (server logs) for errors
2. Run: `pytest insurance_server_python/tests/ -v` to verify backend
3. Check ngrok is still running (Terminal 2)
4. Verify ChatGPT connector is enabled

**Still stuck?** Document:
- What you typed in ChatGPT
- What Claude responded
- Any errors in Terminal 1
- What you expected vs what happened
