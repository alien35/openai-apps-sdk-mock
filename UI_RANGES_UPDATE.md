# UI Ranges Update

## What Changed

The quick quote UI now displays **price ranges** for both monthly and annual premiums, showing the confidence band for each estimate.

## Visual Example

### Before (showing point estimates):
```
┌─────────────────────────────────────────────┐
│ Geico                                       │
│                                             │
│ Est. Monthly Cost    Est. Annual Cost      │
│     $446                 $5,355            │
└─────────────────────────────────────────────┘
```

### After (showing only ranges):
```
┌─────────────────────────────────────────────┐
│ Geico                                       │
│                                             │
│ Est. Monthly Cost    Est. Annual Cost      │
│  $312 - $580          $3,744 - $6,960      │
└─────────────────────────────────────────────┘
```

## Data Structure

Each carrier now includes range fields:

```javascript
{
  name: "Geico",
  logo: "...",
  monthly_cost: 446,
  annual_cost: 5355,
  range_monthly_low: 312,    // NEW
  range_monthly_high: 580,   // NEW
  range_annual_low: 3744,    // NEW
  range_annual_high: 6960,   // NEW
  confidence: "medium",
  explanations: [...]
}
```

## UI Implementation

### HTML Structure
```html
<div class="cost-column">
  <div class="cost-label">Est. Monthly Cost</div>
  <div class="cost-range">$312 - $580</div>
</div>
```

### CSS Styling
```css
.cost-range {
  font-size: 20px;        /* Readable on desktop */
  color: #2563eb;         /* Blue for emphasis */
  margin-top: 4px;
  font-weight: 700;       /* Bold for prominence */
}

/* Mobile responsive */
@media (max-width: 480px) {
  .cost-range {
    font-size: 16px;      /* Smaller for mobile screens */
  }
}
```

## Confidence Bands

The ranges represent the confidence band based on data completeness:

| Confidence | Band  | Example (for $400/mo) |
|------------|-------|-----------------------|
| High       | ±20%  | $320 - $480          |
| Medium     | ±30%  | $280 - $520          |
| Low        | ±40%  | $240 - $560          |

## Benefits

1. **Transparency** - Users see the full price range, not a false point estimate
2. **Honest Communication** - Shows we provide ranges, not fake precision
3. **Better Expectations** - Users understand quotes may vary within the range
4. **Mobile Friendly** - 16px font size ensures readability on small screens
5. **Clean Design** - Single range value instead of cluttered point + range

## Display Sizes

| Device Type | Font Size | Visual Example |
|-------------|-----------|----------------|
| Desktop     | 20px      | **$312 - $580** |
| Mobile      | 16px      | **$312 - $580** |

The range text is:
- **Bold (700 weight)** for prominence
- **Blue (#2563eb)** to match cost emphasis
- **20px on desktop** for easy reading
- **16px on mobile** to fit comfortably on small screens

## Example Display

From a real test run (showing ranges only):

```
📊 Mercury Insurance (BEST QUOTE)
   Est. Monthly Cost:  $256 - $475
   Est. Annual Cost:   $3,072 - $5,700

📊 Progressive
   Est. Monthly Cost:  $263 - $489
   Est. Annual Cost:   $3,156 - $5,868

📊 National General
   Est. Monthly Cost:  $313 - $582
   Est. Annual Cost:   $3,756 - $6,984
```

## Files Modified

1. **`insurance_server_python/tool_handlers.py`**
   - Added `range_monthly_low`, `range_monthly_high`
   - Added `range_annual_low`, `range_annual_high`
   - Updated to pass annual ranges to widget

2. **`insurance_server_python/quick_quote_results_widget.py`**
   - Added HTML for range display
   - Added CSS styling for `.cost-range` class
   - Added mobile responsive styles

## Testing

The feature automatically works with existing quote generation:
- Quick quotes via `insurance_state_tool`
- All carrier quotes include ranges
- Ranges calculated based on confidence bands
- No changes needed to quote generation logic

## Backwards Compatibility

The range display is conditional - if range data is missing, nothing breaks:

```javascript
${carrier.range_monthly_low && carrier.range_monthly_high ?
  `<div class="cost-range">$${formatCurrency(carrier.range_monthly_low)} - $${formatCurrency(carrier.range_monthly_high)}</div>` :
  ''}
```

This means old data without ranges will still display correctly (just without the range line).
