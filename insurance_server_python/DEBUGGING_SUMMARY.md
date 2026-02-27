# Debugging Tools Summary

This is a quick reference for the debugging capabilities built into the insurance server.

## 🔍 Available Debugging

### 1. Tool Handler Logs
**Location:** Console output when running the server
**Level:** Set with `INSURANCE_LOG_LEVEL=INFO`

**What it shows:**
- ✅ Unique call ID for each tool invocation
- ✅ Tool start and end markers
- ✅ All arguments received
- ✅ Duplicate call detection
- ✅ Complete response breakdown (carriers, pricing, metadata)
- ✅ Widget configuration being sent

**Example:**
```
🎯 CALL START [abc12345] ========================================
Tool: get-enhanced-quick-quote
...
╔══════════════════════════════════════════════════════════════╗
║ 📤 RESPONSE INSPECTION [abc12345]                            ║
║   - Number of carriers: 3
║     [1] Mercury Auto Insurance: $4089/year ($340/month)
╚══════════════════════════════════════════════════════════════╝
🏁 CALL END [abc12345] ==========================================
```

### 2. Widget Console Logs
**Location:** Browser console (F12 or Cmd+Option+I)
**Level:** Always on

**What it shows:**
- ✅ Widget script load events
- ✅ Hydration call counter
- ✅ Time between hydrations (detects rapid re-renders)
- ✅ Data source (where data was found)
- ✅ Number of carriers received
- ✅ Event listener triggers

**Example:**
```
🔄 WIDGET HYDRATION CALL #1
✅ Data found via: direct
Number of carriers: 3
🎨 Calling updateWidget...
```

### 3. Duplicate Detection
**Location:** Tool handler (in console logs)
**What it does:** Prevents the same quote from being generated multiple times

**Example:**
```
🔄 DUPLICATE CALL DETECTED - Same quote request was made 2 seconds ago.
Rejecting to prevent repeated widget generation.
```

## 🎯 Common Debugging Scenarios

### "Widget not showing"

**Check:**
1. Server logs - Do you see `CALL START` and `RESPONSE INSPECTION`?
2. Check carriers count in logs - Is it > 0?
3. Browser console - Any JavaScript errors?
4. Browser console - Do you see hydration logs?

### "Widget shown multiple times"

**Check:**
1. Server logs - Multiple `CALL START` with different IDs = ChatGPT calling tool multiple times
2. Browser console - Hydration count > 1 = Widget being re-rendered
3. Browser console - Rapid hydration warnings = Re-rendering happening too fast

### "Wrong URL in button"

**Check:**
1. Server logs - Look for `cta_config` in response inspection
2. Edit `insurance_server_python/url_config.py` to change URL
3. Restart server

## 📝 Log Patterns to Search

```bash
# Find all tool invocations
grep "CALL START" logs.txt

# Find duplicate call warnings
grep "DUPLICATE CALL" logs.txt

# Find response details
grep "RESPONSE INSPECTION" logs.txt

# Count how many times tool was called
grep -c "CALL START" logs.txt
```

## 🔧 Log Levels

```bash
# Full debugging
INSURANCE_LOG_LEVEL=INFO uvicorn insurance_server_python.main:app --port 8000

# Minimal (warnings only)
INSURANCE_LOG_LEVEL=WARNING uvicorn insurance_server_python.main:app --port 8000
```

## ⚠️ What's NOT Included

- ❌ HTTP request/response middleware (removed - was interfering with SSE)
- ❌ Debug endpoints like `/debug/requests` (removed with middleware)
- ❌ Request body logging for MCP endpoints (would break streaming)

**Why removed?**
The middleware was causing SSE streaming errors. The tool handler logging is more useful anyway since it shows the actual business logic.

## 💡 Tips

1. **Always check both:**
   - Server console (tool handler logs)
   - Browser console (widget logs)

2. **Compare call IDs:**
   - Same call ID = same tool invocation
   - Different call IDs = separate invocations

3. **Compare timestamps:**
   - Server logs show when tool was called
   - Browser logs show when widget was rendered

4. **Save logs:**
   ```bash
   uvicorn insurance_server_python.main:app --port 8000 2>&1 | tee debug.log
   ```

## 📚 Full Documentation

See `DEBUGGING_GUIDE.md` for complete details on all debugging features.
