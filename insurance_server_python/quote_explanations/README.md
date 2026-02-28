# Quote Calculation Explanations

This directory contains detailed breakdowns of how insurance quote numbers are calculated.

## Purpose

Every time a quote is generated (either via quick quote or full rating API), a markdown file is automatically created here explaining:

- All input parameters (customer, vehicle, coverage details)
- Step-by-step calculation breakdown
- Risk factors and multipliers applied
- How each carrier's quote was derived
- Price ranges and confidence levels

## File Types

### Quick Quotes (`quick_quote_*.md`)
Generated when using the quick quote estimation engine. Shows:
- State base rates
- Demographic and vehicle risk factors
- Risk score calculation
- How each carrier multiplier is interpolated
- Final premium calculations

### Full Ratings (`full_rate_*.md`)
Generated when calling the external rating API. Shows:
- Complete request payload
- All customer, driver, and vehicle details
- Policy coverage selections
- Carrier results with payment options
- Quote IDs for reference

## File Naming Convention

- Quick quotes: `quick_quote_{STATE}_{ZIP}_{TIMESTAMP}.md`
- Full ratings: `full_rate_{IDENTIFIER}_{TIMESTAMP}.md`

Example: `quick_quote_CA_94105_20260224_143022.md`

## Retention

Files are automatically cleaned up after 7 days to prevent accumulation. You can adjust this in `quote_logger.py` by calling:

```python
from insurance_server_python.quote_logger import cleanup_old_explanations
cleanup_old_explanations(days_to_keep=30)  # Keep for 30 days
```

## Usage

These files are automatically generated - no action required! Just run your quote generation tools and check this directory for the explanations.

### Reading a Quick Quote Explanation

Open any `quick_quote_*.md` file to see:

1. **Input Summary** - What data was provided
2. **Calculation Steps** - How the baseline premium was calculated
3. **Risk Factors** - Age, vehicle, location, marital status multipliers
4. **Carrier Quotes** - How each carrier's quote differs from baseline
5. **Summary** - Price range and best options

### Reading a Full Rate Explanation

Open any `full_rate_*.md` file to see:

1. **API Request Details** - Endpoint and quote ID
2. **Customer Information** - Complete customer profile
3. **Rated Drivers** - All drivers with license info
4. **Vehicles** - All vehicles with coverage selections
5. **Policy Coverages** - Liability limits and optional coverages
6. **Rating Results** - All carrier quotes with payment plans
7. **Summary** - Best and worst quotes

## Benefits

- **Transparency**: Understand exactly how quotes are calculated
- **Debugging**: Trace issues in pricing logic
- **Auditing**: Review historical quote calculations
- **Learning**: See how different factors affect premiums
- **Testing**: Verify quotes are calculated correctly

## Example Insights

From these explanations, you can learn:

- Why a 25-year-old pays more than a 45-year-old (age multiplier)
- How ZIP code affects pricing (location risk)
- Why certain carriers are cheaper (carrier multiplier ranges)
- How vehicle age impacts premiums (vehicle factor)
- What "confidence band" means (data completeness)

## Disabling

To disable explanation logging, set environment variable:

```bash
export DISABLE_QUOTE_EXPLANATIONS=true
```

Or comment out the logging calls in `tool_handlers.py`.
