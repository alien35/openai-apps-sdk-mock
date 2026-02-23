# Quick Calibration Guide

## 🎯 Adjusting Estimates - Quick Reference

All configuration lives in **one file**: `insurance_server_python/pricing/config.py`

---

## Common Adjustments

### 1. Estimates Too High/Low for a State

**Location:** Lines 18-90

```python
STATE_BASE_FULL_COVERAGE_ANNUAL = {
    "CA": 2800,  # ← Adjust this number
}
```

**How to adjust:**
- Look up state average annual premium online
- Adjust the number up/down by 10-20% increments
- Test with `python3 test_estimation_engine.py`

---

### 2. Specific Carrier Too Expensive/Cheap

**Location:** Lines 230-245

```python
CARRIER_BASE_MULTIPLIERS = {
    "Geico": (0.88, 1.05),  # ← Adjust these
    #         ^^^^  ^^^^
    #         low   high
}
```

**How to adjust:**
- `low` = multiplier for best (lowest-risk) customers
- `high` = multiplier for worst (highest-risk) customers
- Lower both numbers → cheaper quotes
- Raise both numbers → more expensive quotes
- Widen the gap → more variation by risk

**Examples:**
```python
# Make Geico more competitive
"Geico": (0.82, 1.00),  # Was (0.88, 1.05)

# Make Progressive more expensive
"Progressive Insurance": (1.00, 1.20),  # Was (0.92, 1.12)
```

---

### 3. Age Group Paying Too Much/Little

**Location:** Lines 31-41

```python
AGE_FACTOR_CURVES = [
    (25, 29, 1.15, "Age 25-29 description"),
    #        ^^^^ ← Adjust this multiplier
]
```

**Examples:**
```python
# Young drivers paying too much? Lower the multiplier
(18, 20, 1.80, "..."),  # Was 2.00

# Seniors paying too little? Raise the multiplier
(66, 75, 1.15, "..."),  # Was 1.05
```

---

### 4. High-Cost City Not Expensive Enough

**Location:** Lines 104-200

```python
ZIP_BUCKET_MULTIPLIERS = {
    "902": 1.40,  # Beverly Hills ← Adjust this
}
```

**How to add new cities:**
```python
# Add San Jose (ZIP 951xx)
"951": 1.30,  # High-cost Silicon Valley area

# Add your city's 3-digit ZIP prefix
"XXX": 1.25,  # Your high-cost area
```

**Multiplier guidelines:**
- **1.40-1.50**: Extremely high (Miami fraud zones, Manhattan)
- **1.25-1.35**: Very high (LA, SF, Chicago downtown)
- **1.10-1.20**: Moderately high (mid-size cities)
- **0.85-0.95**: Low (rural areas)

---

### 5. Ranges Too Wide/Narrow

**Location:** Lines 266-270

```python
CONFIDENCE_BANDS = [
    (8, 0.20, "high"),    # ± 20% ← Adjust these
    (5, 0.30, "medium"),  # ± 30%
    (0, 0.40, "low"),     # ± 40%
]
```

**Examples:**
```python
# Tighter ranges (more confident)
(8, 0.15, "high"),    # Was 0.20
(5, 0.25, "medium"),  # Was 0.30

# Wider ranges (more conservative)
(8, 0.25, "high"),    # Was 0.20
(5, 0.35, "medium"),  # Was 0.30
```

---

### 6. Married Discount Too Small/Large

**Location:** Lines 50-58

```python
MARITAL_STATUS_FACTORS = {
    "married": (0.94, "Description"),
    #           ^^^^ ← Adjust this
}
```

**Examples:**
```python
# Bigger married discount
"married": (0.90, "..."),  # Was 0.94 (10% discount)

# Smaller discount
"married": (0.97, "..."),  # Was 0.94 (3% discount)
```

---

### 7. Luxury Cars Not Expensive Enough

**Location:** Lines 71-79 and 115-122

**Step 1:** Add makes to luxury list
```python
LUXURY_MAKES = [
    "BMW", "MERCEDES", "AUDI",
    "GENESIS",  # ← Add your make here
]
```

**Step 2:** Adjust luxury multiplier
```python
VEHICLE_TYPE_FACTORS = {
    "luxury": (1.25, "Description"),
    #          ^^^^ ← Raise this (e.g., 1.35)
}
```

---

### 8. Full Coverage vs Liability Pricing

**Location:** Lines 200-207

```python
COVERAGE_TYPE_FACTORS = {
    "full": (1.00, "Full coverage"),
    "liability": (0.60, "Liability only"),
    #             ^^^^ ← Adjust this
}
```

**Examples:**
```python
# Make liability cheaper (bigger discount)
"liability": (0.50, "..."),  # Was 0.60 (50% vs 60% of full)

# Make liability more expensive
"liability": (0.70, "..."),  # Was 0.60
```

---

## Testing Your Changes

After making changes to `config.py`:

```bash
# Run the test script
python3 test_estimation_engine.py

# Restart the server
uvicorn insurance_server_python.main:app --port 8000
```

---

## Quick Validation Checklist

✅ Estimates match your state's average premiums (±20%)
✅ High-risk scenarios (young + luxury + violations) are 2-3x baseline
✅ Low-risk scenarios (prime age + economy + rural) are 0.5-0.7x baseline
✅ Carrier order makes sense (competitive carriers should be cheapest)
✅ Ranges feel achievable (not too wide or too narrow)

---

## Common Calibration Scenarios

### "California estimates are too high"
1. Lower `STATE_BASE_FULL_COVERAGE_ANNUAL["CA"]` by 10-15%
2. Check Mercury multiplier (should be competitive in CA)
3. Test with `python3 test_estimation_engine.py`

### "Geico always cheapest, but shouldn't be"
1. Raise Geico multipliers: `(0.95, 1.12)` instead of `(0.88, 1.05)`
2. Or lower competitor multipliers

### "Young drivers not expensive enough"
1. Raise `(18, 20, X, ...)` multiplier (try 2.2 or 2.4)
2. Raise `(21, 24, X, ...)` multiplier (try 1.6 or 1.7)

### "Manhattan not showing high costs"
1. Add ZIP: `"100": 1.50,  # Manhattan`
2. Raise NYC base rate: `"NY": 2900,  # Was 2700`

---

## When to Calibrate

- **Launch**: Compare against 3-5 real quotes, adjust base rates
- **Quarterly**: Review state averages, adjust as market changes
- **After Complaints**: If users say "too high/low", investigate and tune
- **New Carriers**: Research market positioning, set initial multipliers

---

## Pro Tips

1. **Start Conservative**: It's better to quote slightly high than too low
2. **Test Edge Cases**: Always test high-risk and low-risk extremes
3. **Document Changes**: Note why you made adjustments
4. **Incremental Tuning**: Make 10-15% changes, not 50% jumps
5. **Regional Variations**: Cities within states can vary significantly

---

## Getting Real-World Data

To calibrate accurately:

1. **State Averages**: Search "[State] average car insurance cost 2026"
2. **Carrier Comparisons**: Use aggregator sites (Zebra, QuoteWizard)
3. **User Feedback**: Track "too high" vs "too low" reports
4. **A/B Testing**: Try different multipliers, measure conversion

---

## Need Help?

Common issues:

**Q: All estimates look the same**
A: Increase spread in carrier multipliers (wider gap between low/high)

**Q: Estimates way too low for everyone**
A: Raise state base rates by 20-30%

**Q: Luxury cars same price as economy**
A: Raise vehicle type multipliers for luxury/performance

**Q: ZIP doesn't affect price**
A: Add more ZIP prefixes to `ZIP_BUCKET_MULTIPLIERS`

---

**Remember**: The config is designed to be adjusted! Don't be afraid to experiment and tune. 🎯
