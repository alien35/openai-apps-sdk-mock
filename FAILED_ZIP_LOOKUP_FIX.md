# Failed Zip Lookup Fix

## Problem

When Google's geocoding API fails to resolve a zip code (e.g., Cambridge, MA zip 02141), the widget was rendering a broken page showing:
- Default carriers (Geico, Progressive, Safeco)
- Location: "Los Angeles area" (hardcoded fallback)
- Wrong experience for users in valid zip codes that fail lookup

## Solution

Changed the behavior to **show the phone-only prompt** when zip lookup fails, rather than showing an error or broken carrier data.

### Backend Changes (`tool_handlers.py`)

1. **No longer return early on lookup failure:**
   - Previous: Returned error message and stopped
   - New: Continue processing with `lookup_failed=True` flag

2. **Skip quote generation when lookup fails:**
   - Don't call pricing engine
   - Don't try to get state-specific carriers
   - Return empty carriers list

3. **Include `lookup_failed` flag in structured_content:**
   ```python
   structured_content = {
       "zip_code": payload.zip_code,
       "city": None,
       "state": None,
       "carriers": [],
       "lookup_failed": True,  # New flag
       # ...
   }
   ```

### Frontend Changes (`quick_quote_results_widget.py`)

1. **Check for `lookup_failed` flag:**
   ```javascript
   const lookupFailed = data.lookup_failed || false;
   const isPhoneOnlyState = (state && phoneOnlyStates.includes(state)) || lookupFailed;
   ```

2. **Use zip code instead of "Los Angeles area":**
   ```javascript
   // Old: const locationText = city || "the Los Angeles area";
   // New:
   const locationText = city ? `the ${city} area` : `zip code ${zipCode}`;
   ```

3. **Personalized phone prompt for failed lookups:**
   ```javascript
   if (lookupFailed) {
       phoneCallTextEl.textContent =
           `We're ready to help you get the best insurance rates for zip code ${zipCode}.
            Our licensed agents can provide personalized quotes and answer any questions you have.`;
   }
   ```

## Test Results

### Cambridge, MA (02141) - Failed Lookup
- ✅ Returns `lookup_failed: true`
- ✅ Returns 0 carriers
- ✅ Returns widget with phone-only prompt
- ✅ Text says "zip code 02141" (not "Los Angeles area")
- ✅ Shows "Call Now" button

### Other States
- ✅ Alaska (99501) - Works correctly (phone-only state)
- ✅ Hawaii (96813) - Works correctly (phone-only state)
- ✅ Other MA zips - Work correctly (Boston, Natick, etc.)

## User Experience

**Before (Broken):**
```
[Carrier Table showing Geico, Progressive, Safeco]
"Assuming you're in the Los Angeles area..."
```

**After (Fixed):**
```
📞 Speak with a Licensed Agent

We're ready to help you get the best insurance rates for zip code 02141.
Our licensed agents can provide personalized quotes and answer any questions you have.

(888) 772-4247

[Call Now] (orange button)
```

## Edge Cases Handled

1. **Failed Google API lookup** → Phone prompt with zip code
2. **Phone-only states (MA, AK, HI)** → Phone prompt with city/state
3. **Normal states** → Carrier table with quotes
4. **No city/state but valid lookup** → Uses zip code in description

## Files Modified

- `insurance_server_python/tool_handlers.py` (Backend logic)
- `insurance_server_python/quick_quote_results_widget.py` (Frontend widget)

## Testing

Run this test to verify the fix:
```bash
python /tmp/test_failed_lookup.py
```

Expected output:
- Cambridge zip 02141 returns 0 carriers with `lookup_failed: true`
- Widget shows phone prompt with "zip code 02141"
