# Unit Test Architecture - Insurance Server

## Overview
This document describes the unit testing architecture for the insurance quick quote functionality, with special focus on phone-only state handling (MA, AK, HI).

## Test Framework
- **Framework**: pytest
- **Location**: `insurance_server_python/tests/`
- **Async Support**: pytest-asyncio
- **Coverage Tool**: pytest-cov

## Test Organization

### Directory Structure
```
insurance_server_python/
├── tests/
│   ├── __init__.py
│   ├── test_phone_only_states.py       # ⭐ NEW: Comprehensive phone-only tests
│   ├── test_insurance_state_tool.py     # Existing: State widget tests
│   ├── test_rate_request_handler.py     # Existing: Rate handler tests
│   └── ...                              # Other existing tests
└── run_tests.py                         # ⭐ NEW: Master test runner
```

### Test File: `test_phone_only_states.py`

#### Test Suites (8 total)

##### 1. **State Normalization** (9 tests)
Tests that full state names convert to abbreviations:
- `test_massachusetts_full_name_to_abbreviation()`
- `test_alaska_full_name_to_abbreviation()`
- `test_hawaii_full_name_to_abbreviation()`
- `test_abbreviations_stay_unchanged()`
- `test_case_insensitive_normalization()`
- `test_normal_state_normalization()`
- `test_invalid_state_returns_none()`
- `test_whitespace_handling()`
- `test_state_abbreviation_function()`

##### 2. **Carrier Filtering** (10 tests)
Tests that phone-only states return empty carrier lists:
- `test_massachusetts_returns_empty_carriers()`
- `test_alaska_returns_empty_carriers()`
- `test_hawaii_returns_empty_carriers()`
- `test_massachusetts_full_name_returns_empty()`
- `test_alaska_full_name_returns_empty()`
- `test_hawaii_full_name_returns_empty()`
- `test_california_returns_carriers()`
- `test_texas_returns_carriers()`
- `test_new_york_returns_carriers()`
- `test_no_defaults_for_phone_only_states()`

##### 3. **Frontend State Detection** (4 tests)
Tests that frontend correctly identifies phone-only states:
- `test_phone_only_state_list_includes_abbreviations()`
- `test_phone_only_state_list_includes_full_names()`
- `test_normal_states_not_in_phone_only_list()`
- `test_defense_in_depth_both_formats_covered()`

##### 4. **Widget Rendering Logic** (7 tests)
Tests that widget HTML contains necessary elements:
- `test_widget_has_phone_section()`
- `test_widget_has_phone_call_text_element()`
- `test_widget_has_carriers_table()`
- `test_widget_has_phone_number()`
- `test_widget_has_phone_only_state_check()`
- `test_widget_forces_empty_carriers_for_phone_only()`
- `test_widget_has_orange_button_color()`

##### 5. **Tool Handler Integration** (2 tests)
Tests tool handler correctly processes phone-only states:
- `test_enhanced_quick_quote_normalizes_state()` (async)
- `test_enhanced_quick_quote_returns_empty_carriers_for_ma()` (async)

##### 6. **Edge Cases** (6 tests)
Tests edge cases and error conditions:
- `test_empty_string_state()`
- `test_none_state()`
- `test_numeric_state()`
- `test_special_characters_state()`
- `test_get_carriers_with_invalid_state()`
- `test_case_sensitivity_in_carrier_lookup()`

##### 7. **Regression Protection** (4 tests)
Tests to prevent regression of fixed bugs:
- `test_ma_does_not_return_default_carriers()`
- `test_massachusetts_full_name_also_returns_empty()`
- `test_frontend_checks_both_formats()`
- `test_button_color_is_orange_not_green()`

##### 8. **Integration Smoke Tests** (3 tests)
Quick smoke tests for complete flow:
- `test_complete_ma_flow()`
- `test_complete_ca_flow()`
- `test_all_phone_only_states_consistently_handled()`

### Total Tests: **45 tests**

## Running Tests

### Single File
```bash
# Run just the phone-only state tests
pytest insurance_server_python/tests/test_phone_only_states.py -v

# With coverage
pytest insurance_server_python/tests/test_phone_only_states.py --cov=insurance_server_python --cov-report=html
```

### All Tests
```bash
# Run all tests in the project
pytest insurance_server_python/tests/ -v

# With detailed output
pytest insurance_server_python/tests/ -vv --tb=long

# Run specific test class
pytest insurance_server_python/tests/test_phone_only_states.py::TestStateNormalization -v
```

### Master Test Runner (Recommended)
```bash
# Run the master test script
python run_tests.py

# Options:
python run_tests.py --verbose        # Detailed output
python run_tests.py --coverage       # With coverage report
python run_tests.py --fast          # Skip slow tests
```

## Test Patterns

### 1. Unit Tests (Pure Functions)
Test isolated functions with no external dependencies:
```python
def test_normalize_state():
    assert normalize_state("Massachusetts") == "MA"
```

### 2. Integration Tests (With Mocking)
Test functions that have external dependencies:
```python
@pytest.mark.asyncio
async def test_tool_handler():
    with patch("module.external_call") as mock:
        mock.return_value = "data"
        result = await handler()
        assert result["state"] == "MA"
```

### 3. Regression Tests
Tests for specific bugs that were fixed:
```python
def test_ma_does_not_return_default_carriers():
    """REGRESSION TEST: MA was returning defaults, should return empty."""
    carriers = get_carriers_for_state("MA")
    assert carriers == []
```

### 4. Smoke Tests
Quick end-to-end tests:
```python
def test_complete_ma_flow():
    """Test complete flow: MA zip -> normalize -> empty carriers."""
    state = normalize_state("Massachusetts")
    carriers = get_carriers_for_state(state)
    assert state == "MA" and carriers == []
```

## Assertions

### Common Patterns

**Empty List Assertions:**
```python
assert carriers == []
assert len(carriers) == 0
```

**State Equality:**
```python
assert result == "MA"
assert state in ["MA", "AK", "HI"]
```

**Negative Assertions:**
```python
assert "Geico" not in carriers
assert state not in phone_only_states
```

**HTML Content:**
```python
assert 'id="phone-call-section"' in html
assert "#e67e50" in html  # Orange button color
```

## Mocking Strategy

### When to Mock
1. **External APIs**: Geocoding, rating APIs
2. **File I/O**: Reading/writing files
3. **Network Calls**: HTTP requests
4. **Slow Operations**: Database queries, complex calculations

### Mock Examples

**Mock Zip Lookup:**
```python
with patch("insurance_server_python.tool_handlers._lookup_city_state_from_zip") as mock:
    mock.return_value = ("Natick", "Massachusetts")
    # Test code
```

**Mock Carrier Estimator:**
```python
with patch("insurance_server_python.tool_handlers.InsuranceQuoteEstimator") as mock_estimator:
    mock_instance = MagicMock()
    mock_instance.estimate_quotes.return_value = {"quotes": []}
    mock_estimator.return_value = mock_instance
    # Test code
```

## Coverage Goals

### Target Coverage
- **Critical Paths**: 100% (phone-only state logic, carrier filtering)
- **Feature Code**: 90%+ (tool handlers, utilities)
- **Edge Cases**: 80%+ (error handling, validation)
- **UI Components**: 70%+ (widget HTML, JavaScript snippets)

### Generate Coverage Report
```bash
pytest insurance_server_python/tests/ --cov=insurance_server_python --cov-report=html --cov-report=term

# View HTML report
open htmlcov/index.html
```

## Continuous Integration

### Pre-commit Checks
```bash
# Run before committing
pytest insurance_server_python/tests/test_phone_only_states.py -v --tb=short

# Quick smoke test (< 5 seconds)
pytest insurance_server_python/tests/test_phone_only_states.py::TestIntegrationSmokeTests -v
```

### CI Pipeline
```yaml
# Example GitHub Actions workflow
- name: Run Unit Tests
  run: |
    pytest insurance_server_python/tests/ -v --cov=insurance_server_python --cov-report=xml

- name: Upload Coverage
  uses: codecov/codecov-action@v3
```

## Test Data

### Phone-Only States
```python
PHONE_ONLY_STATES = {
    "MA": "Massachusetts",
    "AK": "Alaska",
    "HI": "Hawaii"
}
```

### Test Zip Codes
```python
TEST_ZIPS = {
    "MA": ["01760", "02108", "01420"],  # Natick, Boston, Fitchburg
    "CA": ["90210", "94102"],           # Beverly Hills, San Francisco
    "TX": ["75001", "78701"],           # Dallas, Austin
}
```

### Expected Carriers
```python
EXPECTED_CARRIERS = {
    "CA": ["Progressive Insurance", "Mercury Auto Insurance", "National General"],
    "TX": ["Geico", "Progressive Insurance", "Mercury Auto Insurance"],
    "NY": ["Progressive Insurance", "Mercury Auto Insurance"],
}
```

## Debugging Failed Tests

### Verbose Output
```bash
pytest insurance_server_python/tests/test_phone_only_states.py -vv --tb=long
```

### Run Single Test
```bash
pytest insurance_server_python/tests/test_phone_only_states.py::TestCarrierFiltering::test_massachusetts_returns_empty_carriers -v
```

### Add Print Debugging
```python
def test_something():
    result = function()
    print(f"DEBUG: result = {result}")  # Will show in pytest output
    assert result == expected
```

### Use pytest's `-s` flag
```bash
pytest -s  # Show print statements and logging
```

## Best Practices

### ✅ Do
- Write descriptive test names
- Test both success and failure cases
- Use meaningful assertion messages
- Keep tests independent (no shared state)
- Mock external dependencies
- Test edge cases
- Document regression tests

### ❌ Don't
- Test implementation details
- Share state between tests
- Make tests depend on execution order
- Skip tests without good reason
- Write tests that require manual setup
- Test external APIs directly
- Ignore failing tests

## Maintenance

### Adding New Tests
1. Create test in appropriate suite (or new suite if needed)
2. Follow naming convention: `test_<what>_<when>_<expected>()`
3. Add docstring explaining purpose
4. Update this document if adding new suite

### Removing Tests
1. Document why test is being removed
2. Consider if functionality is covered elsewhere
3. Update coverage metrics

### Refactoring Tests
1. Keep tests passing during refactor
2. Update test documentation
3. Ensure coverage doesn't decrease

## Troubleshooting

### Import Errors
```bash
# Ensure package is in PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest
```

### Async Test Failures
```bash
# Install pytest-asyncio
pip install pytest-asyncio

# Mark async tests
@pytest.mark.asyncio
async def test_async_function():
    ...
```

### Mock Not Working
```python
# Use full path to function
with patch("insurance_server_python.module.function") as mock:
    # Not patch("module.function")
```

## Resources

- **pytest Documentation**: https://docs.pytest.org/
- **pytest-asyncio**: https://pytest-asyncio.readthedocs.io/
- **unittest.mock**: https://docs.python.org/3/library/unittest.mock.html
- **pytest-cov**: https://pytest-cov.readthedocs.io/

---

**Last Updated**: 2024-02-24
**Owner**: Engineering Team
**Status**: Active
