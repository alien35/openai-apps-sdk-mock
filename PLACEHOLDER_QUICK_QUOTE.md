# Placeholder Quick Quote Implementation

## Overview

The `get-quick-quote` tool now returns **placeholder premium ranges** based on typical rates in the user's area, providing instant feedback without making API calls with synthetic data.

## How It Works

### Input
- **Zip Code**: 5-digit US zip code
- **Number of Drivers**: 1-10 drivers

### Output
Two premium ranges (6-month policy):

**BEST CASE** - Assumes:
- Experienced drivers (35+ years old)
- Clean driving records
- Reliable vehicles (mid-size sedans)
- Homeowners with property insurance
- Continuous insurance history

**WORST CASE** - Assumes:
- Young drivers (18-25 years old)
- Limited driving experience
- Newer/higher-value vehicles
- Renters without property insurance
- Minimal insurance history

### Example Response

```
Quick Quote Range for Beverly Hills, California (Zip: 90210)

Based on typical rates in your area:

BEST CASE SCENARIO
(Experienced driver, clean record, reliable vehicle)
💰 $800 - $1,200 per 6 months
   ≈ $133 - $200 per month

WORST CASE SCENARIO
(New driver, newer vehicle, limited history)
💰 $2,400 - $3,600 per 6 months
   ≈ $400 - $600 per month

Your actual rate will depend on:
• Driver ages and experience
• Vehicle year, make, and model
• Driving history and claims
• Coverage selections

Ready for your personalized quote?
I can collect your actual driver and vehicle information to get you
precise quotes from multiple carriers.
```

## Regional Ranges

Base ranges vary by California region:

| Region | Best Case (6mo) | Worst Case (6mo) |
|--------|----------------|------------------|
| Los Angeles Metro | $800 - $1,200 | $2,400 - $3,600 |
| San Francisco Bay | $900 - $1,400 | $2,600 - $4,000 |
| San Diego | $750 - $1,100 | $2,200 - $3,400 |
| Sacramento | $700 - $1,000 | $2,000 - $3,000 |
| Orange County | $850 - $1,250 | $2,500 - $3,800 |
| Inland Empire | $650 - $950 | $1,900 - $2,800 |
| Central Valley | $600 - $900 | $1,800 - $2,700 |

### Scaling for Multiple Drivers

Rates increase by ~30% for each additional driver:
- 1 driver: Base rates
- 2 drivers: Base × 1.3
- 3 drivers: Base × 1.6
- 4 drivers: Base × 1.9

## Benefits

### ✅ Instant Feedback
- No API latency
- No network errors
- Always available

### ✅ No Carrier Rejections
- Doesn't submit synthetic data
- No underwriting errors
- Reliable user experience

### ✅ Sets Expectations
- Users know approximate cost range
- Can decide if they want to continue
- Lower abandonment rate

### ✅ Low Friction
- Only 2 fields required
- Quick engagement
- Smooth transition to detailed collection

## Implementation Files

### Core Modules

**`quick_quote_ranges.py`**
- Zip code to region mapping
- Base range definitions
- Multi-driver scaling logic
- Message formatting

**`tool_handlers.py`**
- `_get_quick_quote()` handler
- Uses placeholder ranges instead of API calls
- Lightweight and fast

**`widget_registry.py`**
- Tool registration
- Updated description noting placeholder estimates

### Tests

**`test_placeholder_quick_quote.py`**
- Tests multiple zip codes
- Verifies range calculations
- Tests driver count scaling
- All tests passing ✅

## Usage Flow

```
User: "I need car insurance"
  ↓
Assistant: "Let me get you a quote range!
            What's your zip code and how many drivers?"
  ↓
User: "94105, 2 drivers"
  ↓
[get-quick-quote]
  ↓
Assistant: Shows placeholder ranges
           ($1,170 - $1,820 best case, $3,380 - $5,200 worst case)
           "Want accurate quotes?"
  ↓
User: "Yes"
  ↓
[collect-personal-auto-customer]
[collect-personal-auto-drivers]
[collect-personal-auto-vehicles]
  ↓
[request-personal-auto-rate]
  ↓
✅ Actual carrier quotes returned
```

## Structured Content

The tool returns:

```json
{
  "structured_content": {
    "zip_code": "90210",
    "number_of_drivers": 1,
    "city": "Beverly Hills",
    "state": "California",
    "best_case_range": {
      "min": 800,
      "max": 1200,
      "per_month_min": 133,
      "per_month_max": 200
    },
    "worst_case_range": {
      "min": 2400,
      "max": 3600,
      "per_month_min": 400,
      "per_month_max": 600
    },
    "stage": "quick_quote_complete",
    "is_placeholder": true
  }
}
```

## Updating Ranges

To update the placeholder ranges, edit `quick_quote_ranges.py`:

```python
REGION_BASE_RANGES = {
    "Los Angeles Metro": (800, 1200, 2400, 3600),
    # Format: (best_min, best_max, worst_min, worst_max)
}
```

Ranges can be updated based on:
- Market research
- Historical quote data
- Competitive analysis
- Regional insurance reports

## Testing

Run the test suite:

```bash
source .venv/bin/activate
PYTHONPATH=. python insurance_server_python/test_placeholder_quick_quote.py
```

Expected output:
```
✅ ALL TESTS PASSED
✅ Driver scaling test complete
```

## Comparison: Placeholder vs. Synthetic API Calls

| Aspect | Placeholder Ranges | Synthetic API Calls |
|--------|-------------------|---------------------|
| Speed | ⚡ Instant | 🐌 5-10 seconds |
| Reliability | ✅ Always works | ⚠️ Carrier rejections |
| Accuracy | 📊 Typical ranges | ❌ No valid quotes |
| Maintenance | 📝 Update ranges periodically | 🔧 Complex synthetic data |
| User Experience | 👍 Smooth | 👎 Potential errors |

## Future Enhancements

### Data-Driven Ranges

Instead of static ranges, calculate from historical data:

```python
# Pull from database of past quotes
ranges = calculate_percentiles(
    zip_code=zip_code,
    num_drivers=num_drivers,
    period="last_90_days"
)
```

### More Granular Factors

Add optional inputs for better estimates:
- Driver ages
- Vehicle types
- Homeowner status

### A/B Testing

Track conversion rates:
- Quick quote → detailed collection
- Range accuracy vs. final quote
- User satisfaction

## Conclusion

The placeholder quick quote approach provides:
- ✅ Instant user engagement
- ✅ Reliable experience
- ✅ Smooth transition to detailed collection
- ✅ No carrier rejection issues

It achieves the original goal of the E2E strategy (quick preview before commitment) without the technical limitations of synthetic data submission.
