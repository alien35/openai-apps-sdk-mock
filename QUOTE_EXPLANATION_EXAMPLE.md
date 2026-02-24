# Quote Explanation Examples

This document shows examples of the automatic quote explanations that are generated.

## Quick Quote Example

Every quick quote now starts with a clear summary table:

```markdown
# Quick Quote Calculation Breakdown

**Generated:** 2026-02-24 11:51:22

## Quote Summary

| Carrier | Monthly Premium | Annual Premium |
|---------|-----------------|----------------|
| Geico | $363 | $4,365 |
| Progressive | $400 | $4,809 |
| State Farm | $400 | $4,809 |
| Allstate | $400 | $4,809 |

**Best Quote:** Geico at **$363/month** ($4,365/year)

**Confidence Level:** medium (±30%)

---

## Input Summary

- **State:** CA
- **ZIP Code:** 90210
- **Driver Age:** 28
- **Marital Status:** Single
- **Vehicle:** 2018 Toyota Camry
- **Coverage Type:** full

... (detailed calculation breakdown follows)
```

## Full Rate API Example

Full rating API calls also start with a comprehensive summary table:

```markdown
# Full Rating API Calculation Breakdown

**Generated:** 2026-02-24 11:51:51
**Quote Identifier:** `TEST-QUOTE-12345`

## Quote Summary

| Carrier | Program | Total Premium | Term | Down Payment | Monthly Payment |
|---------|---------|---------------|------|--------------|------------------|
| Progressive | Gold Plan | $1,850.50 | 6 Months | $350.00 | $250.08 |
| Geico | Standard Auto | $1,725.00 | 6 Months | $300.00 | $237.50 |
| State Farm | Preferred | $1,950.00 | 6 Months | $400.00 | $258.33 |

**Best Quote:** Geico - $1,725.00

**Price Range:** $1,725.00 - $1,950.00

**Price Spread:** $225.00

---

## API Request Details

- **Endpoint:** `https://api.example.com/CA/rates/latest`
- **Quote Identifier:** `TEST-QUOTE-12345`

... (complete request/response details follow)
```

## Key Benefits

### At-a-Glance Comparison
- See all quotes in a clean table format
- Quickly identify the best quote
- Compare monthly vs. annual pricing
- View price ranges and confidence levels

### Matches UI Display
- Table format mirrors what users see in the widget
- Easy to cross-reference with the UI
- Professional presentation

### Clear Metrics
- **Best Quote** - Highlighted at the top
- **Price Range** - Min to max spread
- **Price Spread** - Dollar difference between best and worst
- **Confidence Level** - Data quality indicator

### Complete Breakdown
After the summary table, each file contains:
- Detailed input parameters
- Step-by-step calculations
- Risk factor analysis
- Carrier-specific multipliers
- Payment options

## File Locations

All explanations are saved in:
```
insurance_server_python/quote_explanations/
```

- Quick quotes: `quick_quote_{STATE}_{ZIP}_{TIMESTAMP}.md`
- Full ratings: `full_rate_{IDENTIFIER}_{TIMESTAMP}.md`

## Usage

These files are **automatically generated** every time a quote is created. Just check the `quote_explanations/` directory after running quotes!

Perfect for:
- Understanding pricing logic
- Debugging rate calculations
- Auditing historical quotes
- Training and documentation
- Regulatory compliance
