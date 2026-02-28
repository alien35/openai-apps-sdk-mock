# Calibration Framework Guide

## Overview

The calibration framework provides a systematic way to:
1. **Add real-world quote data** as regression tests
2. **Prevent regressions** when making calibration changes
3. **Track accuracy improvements** over time
4. **Identify which scenarios need better calibration**

## Quick Start

### Running Calibration Tests

```bash
# Run all calibration tests with detailed output
pytest insurance_server_python/tests/test_calibration_scenarios.py -v

# Run only the main calibration test
pytest insurance_server_python/tests/test_calibration_scenarios.py::TestCalibrationScenarios::test_all_calibration_scenarios -v

# Run and see metrics
pytest insurance_server_python/tests/test_calibration_scenarios.py::TestCalibrationMetrics -v -s
```

### Adding a New Calibration Scenario

When you receive actual quotes from carriers, add them to `CALIBRATION_SCENARIOS` in `test_calibration_scenarios.py`:

```python
{
    "scenario_id": "75001_full_2024_02",  # Unique ID: ZIP_coverage_year_sequence
    "description": "Dallas TX - Age 35, Married, 2022 Camry, Full Coverage",
    "source": "Actual quotes from carrier websites, 2024-02-15",
    "date_collected": "2024-02-15",

    # The input profile
    "profile": {
        "state": "TX",
        "zip_code": "75001",
        "age": 35,
        "marital_status": "married",
        "vehicle": {
            "year": 2022,
            "make": "Toyota",
            "model": "Camry"
        },
        "coverage_type": "full"
    },

    # Actual monthly premiums from carriers
    "actual_quotes": {
        "Geico": 150,
        "Progressive Insurance": 165,
        "Safeco Insurance": 180
    },

    # Acceptable error margin (5% = excellent, 10% = good, 15% = acceptable)
    "tolerance_percent": 10.0
},
```

## How It Works

### 1. Tolerance-Based Testing

Instead of expecting exact matches, tests use percentage-based tolerances:

- **≤5% error**: Excellent accuracy
- **5-10% error**: Good accuracy
- **10-15% error**: Acceptable accuracy
- **>15% error**: Needs calibration

### 2. Regression Detection

Every calibration scenario becomes a regression test:

```python
# Before calibration change
Mercury: Estimated $183/mo, Actual $183/mo (0.0% error) ✅

# After making a config change
Mercury: Estimated $220/mo, Actual $183/mo (20.2% error) ❌
# ^ Test fails - regression detected!
```

### 3. Scenario Validation

The framework validates that scenarios are properly formatted:
- All required fields present
- Unique scenario IDs
- Reasonable tolerance values (0-20%)
- Valid profile data

## Workflow for Making Calibration Changes

### Step 1: Run Baseline Tests

Before making changes, verify current accuracy:

```bash
pytest insurance_server_python/tests/test_calibration_scenarios.py -v -s
```

Look at the output:
```
CALIBRATION ACCURACY SUMMARY
================================================================================

90210_liability_2024_01: Beverly Hills 90210 - Age 25, Single, 2020 Civic
--------------------------------------------------------------------------------
  ✅ Mercury Auto Insurance       Est: $189/mo  Actual: $183/mo  Error:   3.3%
  ✅ Progressive Insurance         Est: $216/mo  Actual: $214/mo  Error:   0.9%
  ✅ National General              Est: $247/mo  Actual: $247/mo  Error:   0.0%
```

### Step 2: Add New Real-World Data

When you get actual quotes, add them as a new scenario in `CALIBRATION_SCENARIOS`.

### Step 3: Run Tests - See What Fails

```bash
pytest insurance_server_python/tests/test_calibration_scenarios.py -v
```

New scenario will likely fail if not calibrated:
```
FAILED: 75001_full_2024_02: Geico
  Estimated: $200/mo
  Actual: $150/mo
  Error: 33.3% (tolerance: 10%)
```

### Step 4: Make Calibration Changes

Edit `insurance_server_python/pricing/config.py`:

```python
# Adjust carrier multipliers, state adjustments, etc.
CARRIER_STATE_ADJUSTMENTS: Dict[str, Dict[str, float]] = {
    "Geico": {
        "TX": -0.10,  # More competitive in Texas
    },
    # ...
}
```

### Step 5: Re-run Tests - Check for Regressions

```bash
pytest insurance_server_python/tests/test_calibration_scenarios.py -v -s
```

Verify:
- ✅ New scenario now passes (within tolerance)
- ✅ Old scenarios still pass (no regressions)

### Step 6: Document the Calibration

Create a markdown file documenting what changed and why:

```markdown
# CALIBRATION_TX_2024_02.md

## Changes
- Adjusted Geico TX multiplier from 0.0 to -0.10

## Reason
Based on actual quotes from Dallas 75001, Geico is 25% more competitive
in Texas than our model predicted.

## Impact
- Geico TX estimates: -10% across all scenarios
- No impact to other states or carriers
```

## Example: Full Calibration Session

### Scenario: Received New York Quotes

You got actual quotes from NYC (10001) for a 40-year-old married driver with a 2023 Tesla Model 3, full coverage:

- Geico: $320/mo
- Progressive: $350/mo
- National General: $410/mo

### 1. Add to test file

```python
{
    "scenario_id": "10001_full_2024_03",
    "description": "NYC Manhattan - Age 40, Married, 2023 Tesla Model 3, Full Coverage",
    "source": "Actual quotes via carrier websites, 2024-03-10",
    "date_collected": "2024-03-10",
    "profile": {
        "state": "NY",
        "zip_code": "10001",
        "age": 40,
        "marital_status": "married",
        "vehicle": {"year": 2023, "make": "Tesla", "model": "Model 3"},
        "coverage_type": "full"
    },
    "actual_quotes": {
        "Geico": 320,
        "Progressive Insurance": 350,
        "National General": 410
    },
    "tolerance_percent": 10.0
},
```

### 2. Run test - see failures

```bash
$ pytest insurance_server_python/tests/test_calibration_scenarios.py::TestCalibrationScenarios -v

FAILED: 10001_full_2024_03: Geico
  Estimated: $420/mo
  Actual: $320/mo
  Error: 31.3% (tolerance: 10%)
```

### 3. Analyze the problem

Our estimate is 31% too high. Check:
- Is our Tesla luxury multiplier too aggressive? (1.25x)
- Is our NYC ZIP multiplier too high? (1.50x)
- Is Geico particularly competitive for Teslas?

### 4. Make calibration changes

```python
# Option 1: Reduce Tesla luxury multiplier for newer models
VEHICLE_TYPE_FACTORS: Dict[str, Tuple[float, str]] = {
    "luxury": (1.15, "Luxury vehicle"),  # Was 1.25
    # ...
}

# Option 2: Add Tesla-specific handling
# (Teslas have lower theft and good safety, despite being luxury)

# Option 3: Adjust Geico NY pricing
CARRIER_STATE_ADJUSTMENTS: Dict[str, Dict[str, float]] = {
    "Geico": {
        "NY": -0.05,  # More competitive in NY than expected
    },
}
```

### 5. Iterate and verify

Re-run tests after each change:

```bash
$ pytest insurance_server_python/tests/test_calibration_scenarios.py -v -s

# After adjustment:
✅ 10001_full_2024_03: Geico - Est: $330/mo, Actual: $320/mo (3.1% error)
✅ 90210_liability_2024_01: Mercury - Still accurate (no regression)
```

## Tips for Success

### Choosing Tolerance Levels

- **5% tolerance**: Use for scenarios you've specifically calibrated against
- **10% tolerance**: Use for general scenarios, typical industry variation
- **15% tolerance**: Use for complex scenarios with many variables

### Scenario Diversity

Try to collect scenarios that vary:
- **Geographic**: Different states, urban vs rural ZIP codes
- **Age**: Young drivers (16-25), prime age (30-45), seniors (65+)
- **Vehicles**: Economy, luxury, performance, different ages
- **Coverage**: Liability-only, full coverage, different limits
- **Demographics**: Single, married, various occupations

### Naming Convention

Use descriptive scenario IDs:
```
{ZIP}_{coverage}_{year}_{sequence}

Examples:
90210_liability_2024_01    (First liability scenario from 90210 in 2024)
10001_full_2024_01          (First full coverage from 10001 in 2024)
75001_full_2024_02          (Second full coverage from 75001 in 2024)
```

### When Tests Fail

If calibration tests fail:

1. **Analyze the pattern**
   - Is it one carrier? → Adjust carrier multipliers
   - Is it one state? → Adjust state factors
   - Is it one vehicle type? → Adjust vehicle factors
   - Is it across the board? → Check base rates

2. **Make targeted changes**
   - Change one thing at a time
   - Re-run tests after each change
   - Document what you changed and why

3. **Watch for regressions**
   - Verify old scenarios still pass
   - If old scenario fails, you may need to compromise or add more granular factors

## Monitoring Over Time

### Accuracy Metrics

Run the metrics test periodically:

```bash
pytest insurance_server_python/tests/test_calibration_scenarios.py::TestCalibrationMetrics -v -s
```

Output:
```
OVERALL CALIBRATION METRICS
================================================================================
Total Carrier Estimates: 9
Average Error: 1.4%
Min Error: 0.0%
Max Error: 3.3%

Error Distribution:
  Excellent (≤5%):     9 (100.0%)
  Good (5-10%):        0 (0.0%)
  Acceptable (10-15%): 0 (0.0%)
  Needs Work (>15%):   0 (0.0%)
================================================================================
```

### Tracking Progress

Keep a log of calibration improvements:

```markdown
# Calibration History

## 2024-02-24: Beverly Hills Calibration
- Added 90210_liability_2024_01 scenario
- Average error reduced from 6.7% to 1.4%
- All estimates now within 5% tolerance

## 2024-03-10: NYC Calibration (planned)
- Will add Manhattan scenarios for luxury EVs
- Expected to improve NY market accuracy
```

## Integration with Development Workflow

### Pre-Commit Hook (Optional)

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Run calibration tests before committing pricing changes

if git diff --cached --name-only | grep -q "insurance_server_python/pricing/"; then
    echo "Pricing changes detected - running calibration tests..."
    pytest insurance_server_python/tests/test_calibration_scenarios.py
    if [ $? -ne 0 ]; then
        echo "❌ Calibration tests failed - regression detected!"
        exit 1
    fi
fi
```

### CI/CD Integration

Add to your CI pipeline:

```yaml
- name: Run Calibration Tests
  run: |
    pytest insurance_server_python/tests/test_calibration_scenarios.py -v
    pytest insurance_server_python/tests/test_calibration_scenarios.py::TestCalibrationMetrics -v -s
```

## FAQ

**Q: What if I can't achieve the tolerance level?**

A: You have three options:
1. Collect more granular data to identify the issue
2. Adjust the tolerance for that specific scenario (document why)
3. Add more factors to the pricing model (e.g., occupation, credit tier)

**Q: Should I delete old scenarios?**

A: No! Keep them as regression tests. Even if rates change over time, the relative relationships between carriers should remain stable.

**Q: How many scenarios do I need?**

A: Start with 3-5 diverse scenarios. Add more as you discover edge cases or problem areas. Quality over quantity - diverse scenarios are more valuable than many similar ones.

**Q: What if two scenarios conflict?**

A: This indicates you need more granular factors. For example:
- Scenario A: Geico cheap in TX for young drivers
- Scenario B: Geico expensive in TX for luxury cars
→ Solution: Add vehicle-type-specific carrier adjustments

**Q: Can I use estimate ranges instead of point estimates?**

A: The framework currently tests against point estimates (actual quotes). You could extend it to test that actual quotes fall within predicted ranges.

## Summary

The calibration framework turns every real-world quote you receive into a permanent regression test. This ensures that as you improve accuracy for new scenarios, you don't accidentally break accuracy for existing scenarios.

**Key Benefits:**
1. ✅ Systematic improvement over time
2. ✅ Regression detection before deployment
3. ✅ Clear metrics for model performance
4. ✅ Easy to add new scenarios
5. ✅ Self-documenting calibration history
