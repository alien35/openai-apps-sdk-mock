# Debugging Guide: Request & Widget Tracking

This guide explains the comprehensive debugging tools added to track duplicate calls and widget rendering.

## 🔍 What Was Added

### 1. Enhanced Tool Handler Logging
**File:** `insurance_server_python/tool_handlers.py`

Added to `_get_enhanced_quick_quote()`:
- **Unique Call ID** - Each invocation gets a UUID for tracking through logs
- **Call Start/End Markers** - Clear boundaries in logs
- **Detailed Response Inspection** - Complete breakdown of:
  - Content array
  - Structured content keys and values
  - Carrier details (count, names, pricing)
  - Widget metadata
  - Output template information

**Log Format:**
```
🎯 CALL START [abc12345] ========================================
Tool: get-enhanced-quick-quote
Call ID: abc12345
...processing...
╔══════════════════════════════════════════════════════════════════════════╗
║ 📤 RESPONSE INSPECTION [abc12345]                                        ║
╠══════════════════════════════════════════════════════════════════════════╣
║ Content Array:
║   - Length: 1
║   - Item 0: type=text
║
║ Structured Content:
║   - Keys: ['success', 'quote_generated', 'zip_code', ...]
║   - Number of carriers: 3
║   - Carrier details:
║     [1] Mercury Auto Insurance: $4089/year ($340/month)
║     [2] Progressive Insurance: $4899/year ($408/month)
║     [3] National General: $5588/year ($465/month)
║
║ Meta:
║   - Keys: ['openai/outputTemplate', 'openai.com/widget', ...]
╚══════════════════════════════════════════════════════════════════════════╝
🏁 CALL END [abc12345] ==========================================
```

### 2. Widget Hydration Tracking
**File:** `insurance_server_python/quick_quote_results_widget.py`

Added comprehensive JavaScript logging in the widget:
- **Hydration counter** - Tracks how many times `hydrate()` is called
- **Timestamp tracking** - Records exact time of each hydration
- **Rapid hydration detection** - Warns if hydrations happen < 5 seconds apart
- **Data source tracking** - Shows where data was found (direct, toolResponseMetadata, widget)
- **Event listener tracking** - Counts and logs each `openai:set_globals` event

**Browser Console Output:**
```
🚀 Widget script loaded - Performing initial hydration
═══════════════════════════════════════════════════════════
🔄 WIDGET HYDRATION CALL #1
═══════════════════════════════════════════════════════════
Timestamp: 2026-02-27T11:08:25.123Z
Previous hydration calls: 0
Globals object: {...}
✅ Data found via: direct
Number of carriers: 3
🎨 Calling updateWidget...
✅ updateWidget completed
═══════════════════════════════════════════════════════════

📨 EVENT RECEIVED: openai:set_globals #1
...
```


## 🎯 How to Use

### Scenario 1: Debugging Duplicate Calls

1. **Start the server:**
   ```bash
   INSURANCE_LOG_LEVEL=INFO uvicorn insurance_server_python.main:app --port 8000
   ```

2. **Watch for duplicate detection in tool handler:**
   ```
   🔄 DUPLICATE CALL DETECTED - Same quote request was made 2 seconds ago.
   Rejecting to prevent repeated widget generation.
   ```

3. **Track call lifecycle:**
   - Look for `🎯 CALL START [call_id]` when tool is invoked
   - Then `📤 RESPONSE INSPECTION [call_id]` showing the response details
   - Finally `🏁 CALL END [call_id]` when complete

4. **Check for multiple call IDs:**
   If you see multiple different call IDs in quick succession, ChatGPT is calling the tool multiple times.

### Scenario 2: Debugging Widget Rendering

1. **Open ChatGPT's browser console** (F12 or Cmd+Option+I)

2. **Watch for widget logs:**
   ```
   🚀 Widget script loaded - Performing initial hydration
   🔄 WIDGET HYDRATION CALL #1
   ...
   ```

3. **Look for multiple hydrations:**
   If you see:
   ```
   🔄 WIDGET HYDRATION CALL #2
   ⚠️  Time since last hydration: 0.50 seconds
   ⚠️⚠️⚠️ RAPID HYDRATION DETECTED - Less than 5 seconds since last call!
   ```

   This indicates the widget is being re-rendered multiple times.

4. **Check event count:**
   ```
   📨 EVENT RECEIVED: openai:set_globals #2
   ```

   If this counter keeps increasing, ChatGPT is sending multiple events.

### Scenario 3: Comparing Server vs Widget

**Server logs show:**
- How many times the tool is CALLED
- What data is being SENT in the response
- Each call gets unique ID

**Widget logs show:**
- How many times the widget is RENDERED
- What data is being RECEIVED
- Whether data is valid

**If they don't match:**
- Server called once, widget rendered 3 times → ChatGPT is re-rendering
- Server called 3 times, widget rendered once → ChatGPT is calling tool multiple times

## 🔧 Log Levels

Adjust logging verbosity:

```bash
# Maximum debugging
INSURANCE_LOG_LEVEL=DEBUG uvicorn insurance_server_python.main:app --port 8000

# Standard (recommended)
INSURANCE_LOG_LEVEL=INFO uvicorn insurance_server_python.main:app --port 8000

# Minimal
INSURANCE_LOG_LEVEL=WARNING uvicorn insurance_server_python.main:app --port 8000
```

## 📊 What to Look For

### Sign of Duplicate Tool Calls
- ⚠️ Multiple `CALL START` logs with different call IDs in quick succession
- ⚠️ `DUPLICATE CALL DETECTED` message from tool handler
- ⚠️ Tool handler rejecting duplicate calls with warning message

### Sign of Multiple Widget Renders
- Widget hydration count > 1
- Multiple `EVENT RECEIVED: openai:set_globals` logs
- Rapid hydration warnings in browser console

### Expected Behavior
- One `INCOMING REQUEST` with `tools/call`
- One `CALL START` → `RESPONSE INSPECTION` → `CALL END`
- One widget hydration (or two max: initial + event)
- No duplicate warnings

## 🐛 Common Issues

### Issue: "Displayed quick quote estimate" shown 3 times

**Possible causes:**
1. **ChatGPT calling tool 3 times**
   - Look for 3 separate `INCOMING REQUEST` logs
   - Look for 3 different call IDs
   - Check `/debug/requests` for multiple tool calls

2. **ChatGPT rendering widget 3 times**
   - Look for single `INCOMING REQUEST`
   - Look for widget hydration count = 3
   - Check browser console for multiple event fires

3. **Both**
   - Multiple requests AND multiple hydrations

### Issue: No widget rendering

**Check:**
- Is `structured_content` present in logs?
- Are carriers present? (count > 0)
- Is `openai.com/widget` in meta?
- Browser console - any JavaScript errors?
- Widget hydration - is data being found?

## 📝 Log Patterns to Search

```bash
# Find all quote tool calls
grep "QUICK QUOTE TOOL INVOKED" logs.txt

# Find all request IDs
grep "INCOMING REQUEST" logs.txt

# Find duplicate warnings
grep "DUPLICATE CALL DETECTED" logs.txt

# Find response details
grep "RESPONSE INSPECTION" logs.txt

# Count tool invocations
grep -c "CALL START" logs.txt
```

## 🔗 Related Files

- `insurance_server_python/tool_handlers.py` - Tool handler with call tracking and detailed logging
- `insurance_server_python/quick_quote_results_widget.py` - Widget with hydration tracking
- `insurance_server_python/duplicate_detection.py` - Duplicate call detection (used by tool handlers)
- `insurance_server_python/structured_logging.py` - Structured event logging
- `insurance_server_python/main.py` - MCP server and endpoints

## 💡 Tips

1. **Clear tracking between tests:**
   ```bash
   curl -X POST http://localhost:8000/debug/clear
   ```

2. **Save logs for analysis:**
   ```bash
   uvicorn ... 2>&1 | tee debug.log
   ```

3. **Filter ChatGPT console:**
   Use browser console filters to show only:
   - "WIDGET HYDRATION"
   - "EVENT RECEIVED"
   - "⚠️"

4. **Compare timestamps:**
   Server logs and browser console both show ISO timestamps - compare them to see timing differences.

## ✅ Next Steps

With these tools, you can now:
1. Determine if ChatGPT is calling the tool multiple times
2. Determine if the widget is being rendered multiple times
3. See exact data being sent vs received
4. Track the complete lifecycle of each request
5. Identify timing issues (rapid calls/renders)
