# Quick Quote - Quick Reference

## TL;DR

✅ **What it is:** Instant insurance premium estimates based on zip code + driver count
✅ **How it works:** Returns placeholder ranges (no API calls)
✅ **Status:** Production ready

## Usage

### Input
```json
{
  "ZipCode": "90210",
  "NumberOfDrivers": 2
}
```

### Output
```
Best Case: $1,040 - $1,560 / 6 months
Worst Case: $3,120 - $4,680 / 6 months

"Ready for personalized quotes?" →
[Continue to detailed collection]
```

## Test It

```bash
# Run tests
source .venv/bin/activate
PYTHONPATH=. python insurance_server_python/test_placeholder_quick_quote.py

# Expected: ✅ ALL TESTS PASSED
```

## Files

```
insurance_server_python/
├── quick_quote_ranges.py          # Range calculation
├── tool_handlers.py               # Handler (updated)
├── widget_registry.py             # Tool registration (updated)
└── test_placeholder_quick_quote.py # Tests ✅
```

## California Regions (1 Driver, 6 Months)

| Region | Best | Worst |
|--------|------|-------|
| LA Metro | $800-$1,200 | $2,400-$3,600 |
| SF Bay | $900-$1,400 | $2,600-$4,000 |
| San Diego | $750-$1,100 | $2,200-$3,400 |
| Sacramento | $700-$1,000 | $2,000-$3,000 |

*+30% per additional driver*

## MCP Tool

```
Tool: get-quick-quote
Input: {ZipCode: string, NumberOfDrivers: integer}
Output: Formatted message with placeholder ranges
Handler: _get_quick_quote() in tool_handlers.py
```

## Flow Integration

```
1. User requests insurance quote
     ↓
2. get-quick-quote (instant placeholders)
     ↓
3. User decides to continue
     ↓
4. collect-personal-auto-customer
     ↓
5. collect-personal-auto-drivers
     ↓
6. collect-personal-auto-vehicles
     ↓
7. request-personal-auto-rate (real quotes!)
```

## Key Points

- ⚡ **Instant** - No API latency
- 🎯 **Reliable** - No carrier rejections
- 📊 **Realistic** - Based on CA market data
- 🔄 **Smooth** - Natural transition to real quotes
- ⚠️ **Placeholders** - User knows these are estimates

## Updating Ranges

Edit `quick_quote_ranges.py`:

```python
REGION_BASE_RANGES = {
    "Los Angeles Metro": (800, 1200, 2400, 3600),
    #                     ^^^^^^^^^^  ^^^^^^^^^^^
    #                     best case   worst case
}
```

## Documentation

- 📘 **Implementation:** `PLACEHOLDER_QUICK_QUOTE.md`
- 📗 **Technical:** `MINIMUM_QUICK_QUOTE.md`
- 📙 **Limitations:** `QUICK_QUOTE_LIMITATIONS.md`
- 📕 **Summary:** `QUICK_QUOTE_FINAL_IMPLEMENTATION.md`

## Status

✅ **Production Ready**
- Code complete
- Tests passing
- Documentation complete
- MCP tool registered
- Integration verified

---

*Last updated: 2026-02-18*
