# CTA URL Format Update

## Summary

Updated the CTA (Call-To-Action) URL format to match the correct path and parameter structure.

## Changes Made

### 1. Updated Base URL

**File:** `insurance_server_python/url_config.py`

**Before:**
```python
CTA_BASE_URL = "https://tst.aisinsurance.com"
```

**After:**
```python
CTA_BASE_URL = "https://tst.aisinsurance.com/auto-quote"
```

**Why:** The URL needs to include the `/auto-quote` path.

### 2. Updated Parameters

**Before:**
```python
CTA_PARAMS = {
    "sid": "chatgptapp",
    "refid3": "mercuryais",
}
```

**After:**
```python
CTA_PARAMS = {
    "refid5": "chatgptapp",
}
```

**Why:** Changed from `sid` and `refid3` to single `refid5` parameter as required.

### 3. Updated Tests

**File:** `insurance_server_python/tests/test_url_config.py`

Updated all tests to expect:
- `refid5=chatgptapp` instead of `sid=chatgptapp` and `refid3=mercuryais`
- `/auto-quote?` in the URL path
- At least 2 parameters (refid5 and zip) instead of 3

**Test Results:**
```
11 tests passed ✅
```

## New URL Format

### Basic URL (without carrier)
```
https://tst.aisinsurance.com/auto-quote?refid5=chatgptapp&zip=90210
```

### URL with Carrier
```
https://tst.aisinsurance.com/auto-quote?refid5=chatgptapp&carrier=Geico&zip=90210
```

## Components

| Component | Value |
|-----------|-------|
| Base URL | `https://tst.aisinsurance.com/auto-quote` |
| Tracking Param | `refid5=chatgptapp` |
| ZIP Param | `zip={user_zip}` |
| Optional Carrier | `carrier={carrier_name}` |

## Where This URL Is Used

### 1. Quick Quote Widget

**File:** `insurance_server_python/quick_quote_results_widget.py`

The "Get personalized quote" button uses this URL:
```javascript
function buildCtaUrl(zipCode, ctaConfig) {
    const config = ctaConfig || {};
    const baseUrl = config.base_url || "https://tst.aisinsurance.com/auto-quote";
    const params = config.params || { refid5: "chatgptapp" };

    // Build URL with refid5 and zip
}
```

### 2. Tool Handler

**File:** `insurance_server_python/tool_handlers.py`

The CTA configuration is passed to widgets via structured content:
```python
from .url_config import get_cta_params_json
cta_config = get_cta_params_json()

structured_content = {
    # ... other fields ...
    "cta_config": cta_config,
}
```

## Testing the Change

### Test URL Generation

```bash
python -c "
import sys
sys.path.insert(0, 'insurance_server_python')
from url_config import get_cta_url

print(get_cta_url('90210'))
# Output: https://tst.aisinsurance.com/auto-quote?refid5=chatgptapp&zip=90210

print(get_cta_url('90210', 'Geico'))
# Output: https://tst.aisinsurance.com/auto-quote?refid5=chatgptapp&carrier=Geico&zip=90210
"
```

### Run Tests

```bash
cd insurance_server_python
pytest tests/test_url_config.py -v
```

Should show all 11 tests passing.

### Test in Widget

1. Start server: `uvicorn insurance_server_python.main:app --port 8000`
2. Request a quote in ChatGPT
3. Click "Get personalized quote" button in widget
4. Should redirect to: `https://tst.aisinsurance.com/auto-quote?refid5=chatgptapp&zip={user_zip}`

## For Production

When switching to production, update the base URL in `url_config.py`:

```python
# For production
CTA_BASE_URL = "https://aisinsurance.com/auto-quote"

# Parameters stay the same
CTA_PARAMS = {
    "refid5": "chatgptapp",
}
```

This will generate URLs like:
```
https://aisinsurance.com/auto-quote?refid5=chatgptapp&zip=90210
```

## Files Modified

1. **`insurance_server_python/url_config.py`**
   - Updated `CTA_BASE_URL` to include `/auto-quote` path
   - Changed `CTA_PARAMS` from `sid`/`refid3` to `refid5`
   - Updated docstring examples

2. **`insurance_server_python/tests/test_url_config.py`**
   - Updated all test assertions to expect new format
   - Changed parameter count from 3 to 2 minimum
   - Updated parameter name checks

## Verification Checklist

- [x] Base URL includes `/auto-quote` path
- [x] Parameter changed from `sid` to `refid5`
- [x] Parameter `refid3` removed
- [x] ZIP code parameter still works
- [x] Carrier parameter still works (optional)
- [x] All tests pass
- [x] URL format matches requirement: `https://tst.aisinsurance.com/auto-quote?refid5=chatgptapp&zip=90210`

## Related Documentation

- `insurance_server_python/url_config.py` - URL configuration module
- `insurance_server_python/tests/test_url_config.py` - Tests
- `CTA_URL_CONFIG.md` - Original CTA URL documentation (may need update)
