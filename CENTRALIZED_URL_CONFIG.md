# Centralized URL Configuration

## Summary

All base URLs are now configured in one place at the top of `widget_registry.py`. Change the `BASE_URL` variable to switch between environments (local/ngrok, staging, production).

## Quick Start

**To change the base URL:**

Edit `insurance_server_python/widget_registry.py` at line ~14:

```python
# ============================================================================
# BASE URL CONFIGURATION - Change this for testing/deployment
# ============================================================================
BASE_URL = "https://YOUR-URL-HERE"
```

## Configuration Options

### For Local/Ngrok Testing

```python
BASE_URL = "https://08e6-2601-985-4101-d2b0-53c-2a7-2aa4-cabf.ngrok-free.app"
```

### For Staging

```python
BASE_URL = "https://stg-api.mercuryinsurance.com"
```

### For Production

```python
BASE_URL = "https://api.mercuryinsurance.com"
```

## What Gets Updated Automatically

When you change `BASE_URL`, these are automatically derived:

### 1. Widget URLs
```python
WIDGET_BASE_URL = f"{BASE_URL}/assets/images"
```

Used for:
- `INSURANCE_STATE_WIDGET_TEMPLATE_URI`
- `QUICK_QUOTE_RESULTS_WIDGET_TEMPLATE_URI`
- `PHONE_ONLY_WIDGET_TEMPLATE_URI`

**Example:**
```
https://08e6-2601-985-4101-d2b0-53c-2a7-2aa4-cabf.ngrok-free.app/assets/images/quick-quote-results.html
```

### 2. API Domains
```python
API_DOMAINS = [BASE_URL]
```

Used in:
- MCP metadata `ui.csp.connectDomains`
- CSP headers in `/assets/images/{filename}` route

**Example:**
```python
"connectDomains": [
    "https://08e6-2601-985-4101-d2b0-53c-2a7-2aa4-cabf.ngrok-free.app"
]
```

### 3. MCP Metadata

Automatically updates `_tool_meta()` function:
```python
"ui": {
    "domain": WIDGET_BASE_URL,  # Derived from BASE_URL
    "csp": {
        "connectDomains": API_DOMAINS,  # Derived from BASE_URL
    },
}
```

### 4. CSP Headers

Automatically updates CSP in `main.py`:
```python
f"connect-src 'self' {BASE_URL};"
```

## Verification

After changing `BASE_URL`, verify the configuration:

```bash
python -c "
import sys
sys.path.insert(0, '.')
from insurance_server_python.widget_registry import (
    BASE_URL,
    WIDGET_BASE_URL,
    API_DOMAINS,
    QUICK_QUOTE_RESULTS_WIDGET_TEMPLATE_URI
)

print(f'BASE_URL: {BASE_URL}')
print(f'WIDGET_BASE_URL: {WIDGET_BASE_URL}')
print(f'API_DOMAINS: {API_DOMAINS}')
print(f'Example widget URL: {QUICK_QUOTE_RESULTS_WIDGET_TEMPLATE_URI}')
"
```

Expected output:
```
BASE_URL: https://08e6-2601-985-4101-d2b0-53c-2a7-2aa4-cabf.ngrok-free.app
WIDGET_BASE_URL: https://08e6-2601-985-4101-d2b0-53c-2a7-2aa4-cabf.ngrok-free.app/assets/images
API_DOMAINS: ['https://08e6-2601-985-4101-d2b0-53c-2a7-2aa4-cabf.ngrok-free.app']
Example widget URL: https://08e6-2601-985-4101-d2b0-53c-2a7-2aa4-cabf.ngrok-free.app/assets/images/quick-quote-results.html
```

## File Structure

All URL references are in these files:

### `widget_registry.py`
- **Lines ~14-25:** `BASE_URL` configuration (EDIT THIS)
- **Lines ~74-79:** Widget template URIs (automatically use `WIDGET_BASE_URL`)
- **Lines ~190-200:** `_tool_meta()` function (automatically uses `WIDGET_BASE_URL` and `API_DOMAINS`)

### `main.py`
- **Line ~572:** CSP header (automatically uses `BASE_URL` via import)

## Testing with Ngrok

### 1. Start Ngrok

```bash
ngrok http 8000
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok-free.app`)

### 2. Update Configuration

Edit `widget_registry.py`:
```python
BASE_URL = "https://abc123.ngrok-free.app"
```

### 3. Start Server

```bash
uvicorn insurance_server_python.main:app --port 8000
```

### 4. Test Widget Endpoint

```bash
curl -I https://abc123.ngrok-free.app/assets/images/quick-quote-results.html
```

Should show CSP headers with your ngrok domain:
```
content-security-policy: default-src 'none'; ... connect-src 'self' https://abc123.ngrok-free.app; ...
```

### 5. Configure ChatGPT

In ChatGPT settings, add MCP endpoint:
```
https://abc123.ngrok-free.app/mcp
```

### 6. Test Quote Flow

Request a quote in ChatGPT and verify:
- Widget loads from ngrok URL
- No CSP violations in console
- Widget displays correctly

## Switching Between Environments

### Quick Environment Switching

Keep commented versions in `widget_registry.py`:

```python
# ============================================================================
# BASE URL CONFIGURATION - Change this for testing/deployment
# ============================================================================
# For local/ngrok testing:
# BASE_URL = "https://08e6-2601-985-4101-d2b0-53c-2a7-2aa4-cabf.ngrok-free.app"

# For staging:
# BASE_URL = "https://stg-api.mercuryinsurance.com"

# For production:
# BASE_URL = "https://api.mercuryinsurance.com"

# Currently active:
BASE_URL = "https://08e6-2601-985-4101-d2b0-53c-2a7-2aa4-cabf.ngrok-free.app"
```

Just uncomment the one you need and comment out the others.

### Using Environment Variables (Advanced)

If you want to use environment variables instead:

```python
import os

BASE_URL = os.getenv(
    "BASE_URL",
    "https://stg-api.mercuryinsurance.com"  # Default
)
```

Then:
```bash
# For testing with ngrok
export BASE_URL=https://abc123.ngrok-free.app
uvicorn insurance_server_python.main:app --port 8000

# For production
export BASE_URL=https://api.mercuryinsurance.com
uvicorn insurance_server_python.main:app --port 8000
```

## Troubleshooting

### Widget Not Loading

**Check URL consistency:**
```bash
# All should match your BASE_URL
grep -n "BASE_URL" insurance_server_python/widget_registry.py
```

**Check server is reachable:**
```bash
curl -I https://YOUR-BASE-URL/assets/images/quick-quote-results.html
```

### CSP Violations

**Check domains match:**
```bash
# Should show your BASE_URL in connect-src
curl -I https://YOUR-BASE-URL/assets/images/quick-quote-results.html | grep -i "content-security-policy"
```

### Ngrok URL Changed

When ngrok restarts, it gives you a new URL:
1. Copy new ngrok URL
2. Edit `widget_registry.py` → update `BASE_URL`
3. Restart server: `uvicorn insurance_server_python.main:app --port 8000`
4. Update ChatGPT MCP endpoint if needed

## Benefits

### Single Source of Truth
- Change URL in one place
- All references update automatically
- No risk of missing a reference

### Easy Testing
- Switch between environments quickly
- Test with ngrok without modifying multiple files
- Quick rollback if needed

### Clear Documentation
- Comments show available options
- Easy to understand what each URL is for
- Reduces configuration errors

## Files Modified

1. **`insurance_server_python/widget_registry.py`**
   - Added `BASE_URL` configuration variable
   - Added `WIDGET_BASE_URL` derived variable
   - Added `API_DOMAINS` derived list
   - Updated widget template URIs to use `WIDGET_BASE_URL`
   - Updated `_tool_meta()` to use `WIDGET_BASE_URL` and `API_DOMAINS`

2. **`insurance_server_python/main.py`**
   - Updated `/assets/images/{filename}` route to import `BASE_URL`
   - Updated CSP header to use `BASE_URL` dynamically

## Related Documentation

- `MCP_METADATA_IMPLEMENTATION.md` - How MCP metadata works
- `ASSETS_WIDGET_HOSTING.md` - Widget hosting details
- `URL_STRATEGY.md` - Original URL strategy discussion
