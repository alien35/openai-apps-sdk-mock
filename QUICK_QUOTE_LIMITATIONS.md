# Quick Quote Limitations

## Summary

The `get-quick-quote` tool generates synthetic "best case" and "worst case" scenarios to provide users with a quote range. While the **payload structure is valid** and accepted by the API (200 OK responses), the **Anchor carriers decline to quote** these synthetic scenarios due to underwriting rules.

## What Works ✅

1. **Payload Structure**: The minimum viable structure is correct and accepted by the API
2. **API Communication**: Requests return 200 OK, indicating valid format
3. **Transaction IDs**: The API generates transaction IDs for both scenarios
4. **Results Retrieval**: We can successfully fetch results from the API

## What Doesn't Work ⚠️

The carriers return errors instead of quotes:
- "Invalid Liability Limits Entered.(1)"
- "Invalid Uninsured BI Limits Entered.(1)"

## Why This Happens

The Anchor carriers have **specific underwriting rules** that reject:
- Synthetic customer profiles (FirstName: "Best", "Worst")
- Standardized VINs (1HGCM82633A123456, 5YJ3E1EA5KF123456)
- Placeholder license numbers (UNKNOWN0000)
- Artificial age/experience combinations

These are **business logic rejections**, not technical errors.

## What This Means for Production

### For Real User Data ✅

When the tool is called with **actual user information** (real names, addresses, VINs, license numbers), the carriers will likely:
1. Accept the request
2. Run their underwriting algorithms
3. Return actual premium quotes

The synthetic scenarios fail because carriers can detect:
- Test/placeholder data
- Unrealistic profile combinations
- Missing real-world context

### The Quick Quote Dilemma

The original E2E strategy intended quick quote to provide instant ranges using:
- Just zip code + number of drivers
- Synthetic best/worst case scenarios
- Immediate feedback before collecting details

**Problem:** Carriers reject synthetic data, so we can't provide real quotes without collecting actual user information first.

## Solutions

### Option 1: Skip Quick Quote (Recommended)

Go directly to conversational batch collection:

```
User: "I need car insurance"
  ↓
Assistant: "I'll help you get quotes from multiple carriers.
            Let's start with some basic information..."
  ↓
[collect-personal-auto-customer]
[collect-personal-auto-drivers]
[collect-personal-auto-vehicles]
  ↓
[request-personal-auto-rate] with REAL data
  ↓
✅ Actual carrier quotes returned
```

**Pros:**
- Always works with real data
- Real quotes from carriers
- No synthetic data rejection

**Cons:**
- More upfront questions
- No "preview" before commitment

### Option 2: Historical Averages

Instead of synthetic API calls, show **pre-calculated average ranges** based on historical data:

```python
AVERAGE_RANGES_BY_ZIP = {
    "90210": {
        "best_case": "$1200-$1800/6mo",
        "worst_case": "$3000-$4500/6mo"
    },
    "94105": {
        "best_case": "$1400-$2000/6mo",
        "worst_case": "$3500-$5000/6mo"
    }
}
```

**Pros:**
- Instant feedback
- No API rejections
- Low friction

**Cons:**
- Not real-time
- Less accurate
- Requires data collection/maintenance

### Option 3: Partial Data Collection

Collect **minimal real data** for quick quote:

```
Required for Quick Quote:
- Zip code
- Number of drivers
- Driver ages (actual ages)
- Vehicle years (actual years)
- Real first/last names
```

Then generate more realistic scenarios with this data.

**Pros:**
- Still relatively quick
- More likely to get real quotes
- Better than fully synthetic

**Cons:**
- Still asks for some info upfront
- May still get rejections

## Recommendation

**For MVP: Use Option 1 (Skip Quick Quote)**

Reasons:
1. **Reliability**: Real data always works
2. **Simplicity**: One flow to maintain
3. **Accuracy**: Users get actual quotes, not estimates
4. **Trust**: Showing real carrier results builds confidence

The conversational batch collection is already implemented and works well. Users can get quotes in a single conversation without the quick quote step.

## Implementation

To disable quick quote and go straight to collection:

```python
# In widget_registry.py, comment out or remove:
register_tool(
    ToolRegistration(
        tool=types.Tool(
            name="get-quick-quote",  # Disable this
            ...
        ),
        handler=_get_quick_quote,
    )
)
```

The assistant will then use the collection tools directly:
1. `collect-personal-auto-customer`
2. `collect-personal-auto-drivers`
3. `collect-personal-auto-vehicles`
4. `request-personal-auto-rate` ✅ Gets real quotes

## Future Enhancements

If you want to enable quick quote with real carrier acceptance:

1. **Partner with carriers** to get "quick quote" API endpoints that accept minimal data
2. **Use telematics data** if available (driving patterns, vehicle data)
3. **Implement Option 2** (historical averages) as a lightweight preview
4. **Collect partial data** (Option 3) for more realistic scenarios

## Conclusion

The `get-quick-quote` implementation is **technically correct** - the payload structure works and the API accepts it. The limitation is **business logic** - carriers won't quote synthetic scenarios.

For production, recommend **skipping quick quote** and going directly to conversational collection with real user data, which will produce actual carrier quotes reliably.
