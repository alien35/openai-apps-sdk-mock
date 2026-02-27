# Widget CTA URL Parameter Fix

## Issue

The widget JavaScript code had hardcoded references to old URL parameters (`sid` and `refid3`) that didn't match the updated `url_config.py` which uses `refid5`.

## Problem Areas Found

1. **Hardcoded fallback URL** (line 550)
   - Used old format: `https://tst.aisinsurance.com?sid=chatgptapp&refid3=mercuryais&zip=90210`

2. **JavaScript buildCtaUrl() function** (lines 588-595)
   - Expected old parameters: `sid` and `refid3`
   - Used old base URL without `/auto-quote` path

## Changes Made

### 1. Updated Fallback URL

**File:** `quick_quote_results_widget.py` (line 550)

**Before:**
```html
<a class="cta-button" id="cta-button" href="https://tst.aisinsurance.com?sid=chatgptapp&refid3=mercuryais&zip=90210">
```

**After:**
```html
<a class="cta-button" id="cta-button" href="https://tst.aisinsurance.com/auto-quote?refid5=chatgptapp&zip=90210">
```

### 2. Updated JavaScript Function

**File:** `quick_quote_results_widget.py` (lines 588-601)

**Before:**
```javascript
function buildCtaUrl(zipCode, ctaConfig) {
  const config = ctaConfig || {};
  const baseUrl = config.base_url || "https://tst.aisinsurance.com";
  const sid = config.sid || "chatgptapp";
  const refid3 = config.refid3 || "mercuryais";

  return `${baseUrl}?sid=${sid}&refid3=${refid3}&zip=${zipCode}`;
}
```

**After:**
```javascript
function buildCtaUrl(zipCode, ctaConfig) {
  const config = ctaConfig || {};
  const baseUrl = config.base_url || "https://tst.aisinsurance.com/auto-quote";
  const params = config.params || { refid5: "chatgptapp" };

  // Build query string from params
  const queryParams = [];
  for (const [key, value] of Object.entries(params)) {
    queryParams.push(`${key}=${value}`);
  }
  queryParams.push(`zip=${zipCode}`);

  return `${baseUrl}?${queryParams.join("&")}`;
}
```

### 3. Regenerated Static HTML

**File:** `assets/images/quick-quote-results.html`

Regenerated from updated Python widget to include all changes.

## Verification

```bash
# Check for old parameters
grep -c "refid3\|sid.*chatgpt" assets/images/quick-quote-results.html
# Output: 0 (none found ✅)

# Check for new parameters
grep -c "refid5" assets/images/quick-quote-results.html
# Output: multiple matches ✅
```

## Why This Matters

### 1. **Fallback URL**
If the widget can't receive data from the tool handler (e.g., JavaScript fails), the button falls back to the hardcoded URL. It needs to match the correct format.

### 2. **JavaScript Function**
The `buildCtaUrl()` function receives configuration from the Python backend via `cta_config` in structured content. The function needs to:
- Expect the right parameter structure (`params.refid5` instead of `sid`/`refid3`)
- Use the correct base URL with `/auto-quote` path
- Build the query string correctly

### 3. **Configuration Flow**

```
url_config.py
    ↓ (get_cta_params_json)
tool_handlers.py
    ↓ (cta_config in structured_content)
widget JavaScript
    ↓ (buildCtaUrl function)
Final CTA URL
```

All parts of this chain need to use the same parameter format.

## Testing

### Test in Widget

1. Start server: `uvicorn insurance_server_python.main:app --port 8000`
2. Generate quote in ChatGPT
3. Check button URL in browser DevTools:
   ```
   https://tst.aisinsurance.com/auto-quote?refid5=chatgptapp&zip=90210
   ```

### Test Fallback

Simulate JavaScript failure and verify fallback URL is correct:
```bash
curl http://localhost:8000/assets/images/quick-quote-results.html | grep 'href=.*chatgptapp'
```

Should show:
```html
href="https://tst.aisinsurance.com/auto-quote?refid5=chatgptapp&zip=90210"
```

## Files Modified

1. **`quick_quote_results_widget.py`**
   - Line 550: Updated fallback URL
   - Lines 588-601: Updated JavaScript buildCtaUrl() function

2. **`assets/images/quick-quote-results.html`**
   - Regenerated with updated code

## Related Changes

These fixes complement the earlier changes to `url_config.py`:
- Base URL changed to include `/auto-quote` path
- Parameters changed from `sid`/`refid3` to `refid5`
- Carrier parameter removed

Now all parts of the system use the same URL format consistently.
