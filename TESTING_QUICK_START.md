# Testing Quick Start Guide

## 🚀 Run Tests in 30 Seconds

```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Run tests
python run_tests.py --smoke
```

That's it! ✅

---

## 📚 Common Commands

### Quick Smoke Test (3 tests, ~1 second)
```bash
python run_tests.py --smoke
```
**Use when**: Quick verification before commit

### Phone-Only State Tests (45 tests, ~5 seconds)
```bash
python run_tests.py --phone-only
```
**Use when**: Testing MA/AK/HI logic specifically

### All Tests (~15 seconds)
```bash
python run_tests.py
```
**Use when**: Full verification before PR

### With Coverage Report
```bash
python run_tests.py --phone-only --coverage
# View: open htmlcov/index.html
```
**Use when**: Checking test coverage

### Verbose Output
```bash
python run_tests.py --smoke --verbose
```
**Use when**: Debugging test failures

---

## 🎯 Test Suites

### 1. State Normalization (9 tests)
Tests: `Massachusetts` → `MA`, case handling, whitespace
```bash
pytest insurance_server_python/tests/test_phone_only_states.py::TestStateNormalization -v
```

### 2. Carrier Filtering (10 tests)
Tests: Phone-only states return `[]`, normal states return carriers
```bash
pytest insurance_server_python/tests/test_phone_only_states.py::TestCarrierFiltering -v
```

### 3. Frontend State Detection (4 tests)
Tests: Frontend checks both "MA" and "Massachusetts"
```bash
pytest insurance_server_python/tests/test_phone_only_states.py::TestFrontendStateDetection -v
```

### 4. Widget Rendering (7 tests)
Tests: HTML contains phone section, carrier table, orange button
```bash
pytest insurance_server_python/tests/test_phone_only_states.py::TestWidgetRendering -v
```

### 5. Tool Handler Integration (2 tests)
Tests: Tool normalizes state, returns empty carriers for MA
```bash
pytest insurance_server_python/tests/test_phone_only_states.py::TestToolHandlerIntegration -v
```

### 6. Edge Cases (6 tests)
Tests: Empty strings, None, invalid input
```bash
pytest insurance_server_python/tests/test_phone_only_states.py::TestEdgeCases -v
```

### 7. Regression Protection (4 tests)
Tests: Prevent re-introduction of fixed bugs
```bash
pytest insurance_server_python/tests/test_phone_only_states.py::TestRegressionProtection -v
```

### 8. Integration Smoke Tests (3 tests)
Tests: Complete end-to-end flows
```bash
pytest insurance_server_python/tests/test_phone_only_states.py::TestIntegrationSmokeTests -v
```

---

## 🔍 Run Individual Tests

### Single Test
```bash
pytest insurance_server_python/tests/test_phone_only_states.py::TestStateNormalization::test_massachusetts_full_name_to_abbreviation -v
```

### All Tests in a Class
```bash
pytest insurance_server_python/tests/test_phone_only_states.py::TestCarrierFiltering -v
```

### With Pattern Matching
```bash
pytest -k "massachusetts" -v
```

---

## 📊 Coverage Reports

### Generate HTML Coverage Report
```bash
python run_tests.py --phone-only --coverage
open htmlcov/index.html
```

### Terminal Coverage Summary
```bash
pytest insurance_server_python/tests/test_phone_only_states.py \
  --cov=insurance_server_python \
  --cov-report=term-missing
```

---

## 🐛 Debugging Failed Tests

### Show Print Statements
```bash
pytest -s insurance_server_python/tests/test_phone_only_states.py::TestStateNormalization
```

### Full Traceback
```bash
pytest --tb=long insurance_server_python/tests/test_phone_only_states.py
```

### Stop at First Failure
```bash
pytest -x insurance_server_python/tests/test_phone_only_states.py
```

### Run Last Failed Tests
```bash
pytest --lf
```

---

## ✅ Pre-Commit Checklist

Before committing code:

```bash
# 1. Quick smoke test (1 second)
python run_tests.py --smoke

# 2. Phone-only state tests (5 seconds)
python run_tests.py --phone-only

# 3. If both pass, you're good to commit!
```

---

## 🏗️ CI/CD Integration

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov
      - name: Run tests
        run: python run_tests.py --coverage
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## 📈 Test Metrics

### Current Status
- **Total Tests**: 45
- **Test Suites**: 8
- **Avg Run Time**: ~5 seconds (phone-only tests)
- **Target Coverage**: 90%+

### Test Breakdown
| Suite | Tests | Focus |
|-------|-------|-------|
| State Normalization | 9 | Full name → abbreviation |
| Carrier Filtering | 10 | Empty list for phone-only states |
| Frontend Detection | 4 | Both formats handled |
| Widget Rendering | 7 | HTML elements present |
| Tool Integration | 2 | Handler behavior |
| Edge Cases | 6 | Error conditions |
| Regression | 4 | Prevent bug reintroduction |
| Smoke Tests | 3 | End-to-end flows |

---

## 🆘 Troubleshooting

### ImportError: No module named 'pytest_asyncio'
```bash
pip install pytest-asyncio pytest-cov
```

### Tests Not Found
```bash
# Make sure you're in project root
cd /Users/alexanderleon/mi/openai-apps-sdk-examples
python run_tests.py
```

### Virtual Environment Issues
```bash
# Recreate venv
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -r insurance_server_python/requirements.txt
pip install pytest pytest-asyncio pytest-cov
```

### Tests Pass Locally But Fail in CI
- Check Python version match
- Verify all dependencies installed
- Check for environment variable differences

---

## 📚 Documentation

- **Full Test Architecture**: See `UNIT_TEST_ARCHITECTURE.md`
- **Integration Testing**: See `QUICK_QUOTE_TESTING_PLAN.md`
- **Quick Checklist**: See `QUICK_TEST_CHECKLIST.md`

---

## 💡 Tips

### Fast Feedback Loop
```bash
# Watch mode (re-run on file changes)
pip install pytest-watch
ptw insurance_server_python/tests/test_phone_only_states.py
```

### Only Failed Tests
```bash
pytest --lf --tb=short
```

### Quiet Output
```bash
pytest -q insurance_server_python/tests/test_phone_only_states.py
```

### Parallel Execution
```bash
pip install pytest-xdist
pytest -n auto insurance_server_python/tests/
```

---

**Last Updated**: 2024-02-24
