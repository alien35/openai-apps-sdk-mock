# Quick Widget Preview Testing

Fast iteration workflow for widget development without running the full server.

## Quick Start

```bash
# Generate preview with mock data
python insurance_server_python/test_widget_preview.py

# Opens preview.html in your browser automatically
```

## What It Does

1. **Loads the widget HTML** from `quick_quote_results_widget.py`
2. **Injects mock data** (3 carriers with realistic prices)
3. **Generates `preview.html`** in the project root
4. **Opens in browser** automatically

## Mock Data

The preview includes:
- **Location**: Brea, CA 93281
- **Drivers**: 1 driver (age 32)
- **Vehicles**: 1 vehicle
- **Carriers**: 3 carriers
  - Mercury Auto Insurance: $298/mo ($3,576/year)
  - Progressive Insurance: $320/mo ($3,840/year)
  - National General Insurance: $317/mo ($3,804/year)

## Development Workflow

### Fast Iteration
```bash
# 1. Edit the widget
vim insurance_server_python/quick_quote_results_widget.py

# 2. Regenerate preview
python insurance_server_python/test_widget_preview.py

# 3. Refresh browser (preview.html auto-updates)
```

### Testing Different Scenarios

Edit `test_widget_preview.py` to test different cases:

**Single driver, single vehicle:**
```python
return {
    "num_drivers": 1,
    "num_vehicles": 1,
    # ...
}
```

**Multiple drivers/vehicles:**
```python
return {
    "num_drivers": 2,
    "num_vehicles": 2,
    # ...
}
```

**Phone-only state (no quotes):**
```python
return {
    "state": "MA",  # or "AK", "HI"
    "lookup_failed": False,
    "carriers": [],  # Empty
    # ...
}
```

**Failed ZIP lookup:**
```python
return {
    "lookup_failed": True,
    "city": None,
    "state": None,
    "carriers": [],  # Empty
    # ...
}
```

## Files Generated

- **`preview.html`** - Standalone HTML file with widget and mock data
  - Located in project root
  - Can be opened directly in any browser
  - Includes "PREVIEW MODE" badge in top-right

## Benefits

✅ **Fast**: No server startup needed
✅ **Visual**: See changes immediately in browser
✅ **Isolated**: Test widget independently
✅ **Debuggable**: Use browser DevTools
✅ **Portable**: Share preview.html with team

## Browser DevTools

Open browser console to see:
- Mock data injection logs
- Widget hydration logs
- Carrier details
- Any JavaScript errors

## Cleanup

```bash
# Remove generated preview
rm preview.html
```

## Tips

1. **Keep browser open** - Just refresh after regenerating
2. **Use browser DevTools** - Inspect element, check console
3. **Test mobile** - Use responsive design mode in DevTools
4. **Compare layouts** - Open multiple browsers side-by-side
5. **Check logos** - Ensure all carrier logos load correctly

## Troubleshooting

**Preview doesn't open automatically:**
```bash
# Manually open the file
open preview.html
```

**Widget not rendering:**
- Check browser console for JavaScript errors
- Verify mock data structure matches expected format
- Look for "MOCK DATA PREVIEW MODE" in console

**Logos not showing:**
- Logos are base64 data URIs from `carrier_logos.py`
- If missing, check `get_carrier_logo()` function

## See Also

- `quick_quote_results_widget.py` - Widget source
- `carrier_logos.py` - Logo data
- `tool_handlers.py` - Real data structure reference
