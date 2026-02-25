# Calibration System Summary

## What We Built

A systematic framework for continuously improving quote estimation accuracy while preventing regressions.

## Key Components

### 1. Calibration Test Suite
**File:** `insurance_server_python/tests/test_calibration_scenarios.py`

- **Real-world scenario tests**: Each actual quote becomes a permanent regression test
- **Tolerance-based validation**: Accepts reasonable variance (5-15%) instead of demanding exact matches
- **Automatic metrics**: Tracks average error, error distribution, and quality tiers
- **Self-validating**: Ensures test data is properly formatted

### 2. Documentation
**File:** `insurance_server_python/tests/CALIBRATION_FRAMEWORK.md`

- Complete guide on adding new scenarios
- Workflow for making calibration changes
- Best practices and tips
- Integration with CI/CD

### 3. Calibration History
**Files:**
- `CALIBRATION_90210_UPDATES.md` - Beverly Hills calibration (February 2024)
- Future calibration files as we add more scenarios

## How to Use It

### When You Get New Quote Data

1. **Add scenario to test file:**
   ```python
   {
       "scenario_id": "75001_full_2024_03",
       "description": "Dallas - Age 35, 2022 Camry, Full Coverage",
       "actual_quotes": {
           "Geico": 150,
           "Progressive Insurance": 165
       },
       "tolerance_percent": 10.0
   }
   ```

2. **Run tests to see current accuracy:**
   ```bash
   pytest insurance_server_python/tests/test_calibration_scenarios.py -v -s
   ```

3. **Make calibration changes** in `config.py`

4. **Re-run tests to verify:**
   - New scenario improves ✅
   - Old scenarios don't regress ✅

### Quick Commands

```bash
# Run all calibration tests
pytest insurance_server_python/tests/test_calibration_scenarios.py -v

# See detailed metrics
pytest insurance_server_python/tests/test_calibration_scenarios.py::TestCalibrationMetrics -v -s

# Run just the regression tests
pytest insurance_server_python/tests/test_calibration_scenarios.py::TestCalibrationScenarios -v -s
```

## Current Status

### Scenarios Tracked
1. **90210_liability_2024_01** - Beverly Hills, liability-only, age 25, Honda Civic

### Current Accuracy (Liability-Only)
- Mercury: 8.7% error ✅
- Progressive: 12.1% error ✅
- National General: 10.9% error ✅
- **Average: 10.6% error** (all within acceptable 15% tolerance)

### Quality Metrics
- Excellent (≤5%): 0 (0%)
- Good (5-10%): 1 (33.3%)
- Acceptable (10-15%): 2 (66.7%)
- Needs Work (>15%): 0 (0%)

## Benefits

### 1. Systematic Improvement
Every new quote you receive makes the system better by:
- Adding a permanent test case
- Identifying areas needing calibration
- Validating calibration changes

### 2. Regression Prevention
Changes to pricing config automatically tested against all known scenarios:
```bash
# Make change to config.py
vim insurance_server_python/pricing/config.py

# Verify no regressions
pytest insurance_server_python/tests/test_calibration_scenarios.py
```

### 3. Transparent Progress
Clear metrics show improvement over time:
- Error percentages per carrier
- Overall accuracy distribution
- Quality tier tracking (excellent/good/acceptable)

### 4. Low Maintenance
Adding new scenarios is just data entry:
- Copy the template
- Fill in profile and actual quotes
- Set tolerance level
- Done!

## Example Workflow

### Scenario: Received Texas Quotes

```python
# 1. Add to CALIBRATION_SCENARIOS
{
    "scenario_id": "75001_full_2024_03",
    "description": "Dallas TX - Age 35, Married, 2022 Camry",
    "profile": {"state": "TX", "zip_code": "75001", ...},
    "actual_quotes": {"Geico": 150, "Progressive Insurance": 165},
    "tolerance_percent": 10.0
}

# 2. Run tests - see failure
$ pytest test_calibration_scenarios.py -v
FAILED: Geico - Est $200, Actual $150 (33% error)

# 3. Adjust config.py
CARRIER_STATE_ADJUSTMENTS = {
    "Geico": {"TX": -0.15}  # More competitive in TX
}

# 4. Re-run tests - verify fix
$ pytest test_calibration_scenarios.py -v
✅ Geico - Est $155, Actual $150 (3% error)
✅ 90210_liability_2024_01 - Still passing (no regression)
```

## Integration Points

### With Existing Tests
The calibration suite runs alongside existing unit tests:
```bash
pytest insurance_server_python/tests/  # Runs all tests including calibration
```

### With CI/CD (Optional)
Add to your pipeline:
```yaml
- name: Calibration Tests
  run: pytest insurance_server_python/tests/test_calibration_scenarios.py --junitxml=calibration-results.xml
```

### With Git Hooks (Optional)
Prevent committing pricing changes that cause regressions:
```bash
# .git/hooks/pre-commit
if git diff --cached | grep "pricing/config.py"; then
    pytest insurance_server_python/tests/test_calibration_scenarios.py || exit 1
fi
```

## Next Steps

### 1. Collect More Diverse Scenarios
Priority areas:
- **Full coverage quotes** (currently only have liability-only)
- **Different age brackets** (currently only age 25)
- **Other states** (currently only California)
- **Different vehicle types** (luxury, performance, older cars)
- **Different demographics** (married, female drivers, etc.)

### 2. Refine Tolerance Levels
As we calibrate more:
- Tighten tolerances for well-calibrated scenarios (15% → 10% → 5%)
- Identify systematic issues causing high errors
- Add more granular factors if needed

### 3. Track Progress Over Time
Create a calibration log:
```markdown
# Calibration History

## 2024-02-24: Initial Framework
- Created calibration test suite
- Added 90210 liability scenario
- Average error: 10.6%

## 2024-03-15: Texas Expansion (planned)
- Add Dallas/Houston scenarios
- Expected to improve TX accuracy

## 2024-04-01: Full Coverage Focus (planned)
- Add full coverage scenarios across multiple states
- Target: <8% average error
```

## Files Reference

**Test Suite:**
- `insurance_server_python/tests/test_calibration_scenarios.py` - Main test file

**Documentation:**
- `insurance_server_python/tests/CALIBRATION_FRAMEWORK.md` - Complete guide
- `CALIBRATION_90210_UPDATES.md` - Beverly Hills calibration details
- `CALIBRATION_SYSTEM_SUMMARY.md` - This file (quick reference)

**Configuration:**
- `insurance_server_python/pricing/config.py` - Pricing factors and multipliers
- `insurance_server_python/pricing/factors.py` - Factor calculation functions

## Success Criteria

**Short Term (Next 3 Scenarios):**
- ✅ Framework operational and easy to use
- 🎯 Collect 5-10 diverse scenarios
- 🎯 Average error < 10% across all scenarios

**Medium Term (3-6 Months):**
- 🎯 20+ scenarios covering diverse profiles
- 🎯 Average error < 8%
- 🎯 80% of estimates in "Good" or "Excellent" tier

**Long Term (6-12 Months):**
- 🎯 50+ scenarios
- 🎯 Average error < 5%
- 🎯 90% of estimates in "Excellent" tier (≤5% error)
