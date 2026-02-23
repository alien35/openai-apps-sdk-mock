# Logo Rendering Issue - Debugging Action Plan

## Problem Summary
Logos are not rendering in the quick quote widget. Carriers display as text and the navbar logo shows a broken image. This document provides a complete action plan to diagnose and fix the issue.

## Root Cause Analysis

The widget JavaScript expects a `server_url` or `serverUrl` field to construct image paths:

```javascript
const serverUrl = data.server_url || data.serverUrl || "";
const logoPath = serverUrl ? getLogoPath(carrier.name, serverUrl) : "";
```

**If `serverUrl` is empty or missing, carriers display as text instead of logos.**

The backend provides this field from an environment variable:
```python
server_base_url = os.getenv("SERVER_BASE_URL", "http://localhost:8000")
```

## Known Working Setup (Pre-Stash)

Based on git stash analysis, the working version:
- ✅ Passes `server_url: server_base_url` in structured content (line 585)
- ✅ Has the same widget JavaScript logic
- ✅ Uses the same environment variable pattern

## Diagnostic Steps

### Step 1: Verify Image Assets Exist

```bash
ls -la insurance_server_python/assets/images/
```

**Expected output:**
```
mercury-logo.png
orion.png
progressive.png
```

**Status:** ✅ Verified - all images exist

---

### Step 2: Check Environment Variable

```bash
# In your terminal or .env file
echo $SERVER_BASE_URL
# or
grep SERVER_BASE_URL insurance_server_python/.env
```

**Expected values:**
- Local testing: `http://localhost:8000`
- ngrok testing: `https://your-id.ngrok-free.app`

**Common issue:** When using ngrok with ChatGPT, the environment variable must be set to the ngrok URL, not localhost.

---

### Step 3: Verify Server Serves Images

With the server running:
```bash
# Start server
uvicorn insurance_server_python.main:app --port 8000

# Test image endpoints (in another terminal)
curl -I http://localhost:8000/assets/images/mercury-logo.png
curl -I http://localhost:8000/assets/images/orion.png
curl -I http://localhost:8000/assets/images/progressive.png
```

**Expected:** HTTP 200 OK responses

**If 404:** Check that main.py mounts the static assets directory correctly.

---

### Step 4: Inspect Structured Content

Add logging to see what data is being sent to the widget:

```python
# In tool_handlers.py, around line 590
logger.info(f"=== STRUCTURED CONTENT DEBUG ===")
logger.info(f"server_url value: {server_base_url}")
logger.info(f"Full structured content: {json.dumps(structured_content, indent=2)}")
logger.info(f"=== END STRUCTURED CONTENT ===")
```

Then run with debug logging:
```bash
INSURANCE_LOG_LEVEL=DEBUG uvicorn insurance_server_python.main:app --port 8000
```

**Look for:** The `server_url` field in the logged structured content

---

### Step 5: Check ChatGPT Data Passing

Use browser DevTools when testing in ChatGPT:

1. Open ChatGPT and trigger the quote flow
2. Open DevTools Console (F12)
3. Look for widget logs:
   ```
   Quick quote widget: Server URL: <value>
   ```

**If empty string `""`:** The `server_url` field is not reaching the widget

**If `http://localhost:8000`:** This won't work in ChatGPT (need ngrok URL)

**If correct ngrok URL:** Check network tab for image request failures

---

### Step 6: Verify Widget HTML Structure

The widget HTML (quick_quote_results_widget.py) should have:

1. **Header logo element:**
   ```html
   <img id="mercury-logo" src="" alt="Mercury Insurance">
   ```

2. **Logo setter in updateWidget():**
   ```javascript
   if (mercuryHeaderLogoEl && serverUrl) {
     mercuryHeaderLogoEl.src = `${serverUrl}/assets/images/mercury-logo.png`;
   }
   ```

3. **Carrier logo rendering:**
   ```javascript
   const logoPath = serverUrl ? getLogoPath(carrier.name, serverUrl) : "";
   row.innerHTML = `
     <div class="carrier-left">
       ${logoPath ? `<img class="carrier-logo" src="${logoPath}" ...>` : `<div>${carrier.name}</div>`}
     </div>
   `;
   ```

---

### Step 7: Test Widget Standalone

Use the test file to isolate widget rendering from the full flow:

```bash
# 1. Start server
uvicorn insurance_server_python.main:app --port 8000

# 2. Open test file
open test-quick-quote-widget.html

# 3. Check DevTools console for:
# - "Quick quote widget: Server URL: http://localhost:8000"
# - Any 404 errors in Network tab
```

**This tests the widget independently of ChatGPT/MCP integration.**

---

## Common Issues & Solutions

### Issue 1: Empty `server_url` in ChatGPT

**Symptom:** Widget logs show `Server URL: ""`

**Cause:** Environment variable not set when using ngrok

**Solution:**
```bash
# Option A: Set in .env file
echo "SERVER_BASE_URL=https://your-id.ngrok-free.app" >> insurance_server_python/.env

# Option B: Set in shell
export SERVER_BASE_URL=https://your-id.ngrok-free.app
uvicorn insurance_server_python.main:app --port 8000

# Option C: Inline with uvicorn
SERVER_BASE_URL=https://your-id.ngrok-free.app uvicorn insurance_server_python.main:app --port 8000
```

**Important:** Update the ngrok URL every time you restart ngrok (they change unless you have a paid plan).

---

### Issue 2: CORS Errors

**Symptom:** Network tab shows CORS policy errors when loading images

**Cause:** Server not configured to allow requests from ChatGPT's origin

**Solution:** Check main.py has CORS middleware:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specific ChatGPT origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### Issue 3: Images 404 but File Exists

**Symptom:** `curl http://localhost:8000/assets/images/mercury-logo.png` returns 404

**Cause:** Static files not mounted in FastAPI app

**Solution:** Check main.py has static mount:
```python
from fastapi.staticfiles import StaticFiles

app.mount("/assets", StaticFiles(directory="insurance_server_python/assets"), name="assets")
```

---

### Issue 4: Wrong Tool Being Called

**Symptom:** Widget shows but without proper data

**Cause:** ChatGPT may be calling `get-enhanced-quick-quote` but not `submit-carrier-estimates`

**Solution:** Check which tools are being invoked in ChatGPT's flow. The stashed changes show a two-step process:
1. `get-enhanced-quick-quote` - collects profile
2. `submit-carrier-estimates` - displays widget with estimates

Ensure both tools pass `server_url` in their structured content.

---

## Testing Checklist

Use this checklist to verify the fix:

- [ ] Images exist in `insurance_server_python/assets/images/`
- [ ] Server serves images at `/assets/images/*` endpoints
- [ ] `SERVER_BASE_URL` environment variable is set correctly
- [ ] Server logs show correct `server_url` in structured content
- [ ] Standalone test file (`test-quick-quote-widget.html`) renders logos
- [ ] ChatGPT DevTools console shows correct `server_url` value
- [ ] ChatGPT DevTools Network tab shows successful image loads (200 OK)
- [ ] Widget displays logos for all carriers
- [ ] Navbar Mercury logo displays correctly

---

## Quick Debug Commands

```bash
# 1. Check images exist
ls -la insurance_server_python/assets/images/

# 2. Check environment variable
cat insurance_server_python/.env | grep SERVER_BASE_URL

# 3. Start server with debug logging
INSURANCE_LOG_LEVEL=DEBUG uvicorn insurance_server_python.main:app --port 8000

# 4. Test image endpoint
curl -I http://localhost:8000/assets/images/mercury-logo.png

# 5. Start ngrok (separate terminal)
ngrok http 8000

# 6. Update .env with ngrok URL
# Copy the HTTPS URL from ngrok output
echo "SERVER_BASE_URL=https://abc123.ngrok-free.app" > insurance_server_python/.env

# 7. Restart server to pick up new env var
# (Ctrl+C the uvicorn process, then restart)
```

---

## Comparison: Working vs. Broken

### Working Version (Current Code)
```python
# tool_handlers.py line 585
structured_content = {
    "server_url": server_base_url,  # ✅ Passes server URL
    "carriers": carriers,
    # ...
}
```

### If Broken in Stashed Changes
The stashed diff shows `server_url` was **removed** from `_get_enhanced_quick_quote` but **added** to `_submit_carrier_estimates`. This means:

- The refactored flow splits quote generation into two steps
- Step 1 (`get-enhanced-quick-quote`): Collect profile (no widget)
- Step 2 (`submit-carrier-estimates`): Display widget with estimates

**Both tools must pass `server_url`** if they return widget metadata.

---

## Resolution Strategy

If logos still don't render after following this plan:

1. **Start simple:** Use standalone test file to confirm widget code works
2. **Add logging:** Log `server_url` at every stage (backend → structured content → widget JS)
3. **Check network:** Use DevTools to see actual HTTP requests and responses
4. **Compare git diff:** If stashed changes caused the issue, identify what changed
5. **Verify data flow:** Ensure `server_url` makes it from Python → MCP response → OpenAI globals → widget

---

## Key Files Reference

- **Widget HTML:** `insurance_server_python/quick_quote_results_widget.py`
- **Tool Handlers:** `insurance_server_python/tool_handlers.py`
- **Environment Config:** `insurance_server_python/.env`
- **Image Assets:** `insurance_server_python/assets/images/`
- **Standalone Test:** `test-quick-quote-widget.html`
- **Server Entry:** `insurance_server_python/main.py`

---

## Next Steps

1. Run through diagnostic steps 1-7 in order
2. Document findings at each step
3. Apply the appropriate solution from the "Common Issues" section
4. Verify with the testing checklist
5. If issue persists, review git stash diff to identify architectural changes

