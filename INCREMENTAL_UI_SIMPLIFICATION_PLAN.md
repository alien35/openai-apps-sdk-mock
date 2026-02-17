# Incremental UI Simplification Plan

## Goal
Remove optional fields from the insurance widget to reduce cognitive load from 80-100 fields to 30-40 required fields.

## Strategy
Make small, testable changes to the EXISTING `insurance-state-selector` widget rather than building a new widget from scratch.

---

## Phase 1: Preparation (No UI Changes)
**Goal:** Set up infrastructure without touching the UI

### Step 1.1: Verify Backend Infrastructure ✅ DONE
- [x] Schema parser (`schema_parser.py`)
- [x] Field defaults (`field_defaults.py`)
- [x] Minimal fields config (`minimal_fields_config.json`)
- [x] All tests passing

### Step 1.2: Add Config Endpoint
**Files:** `insurance_server_python/main.py`

Add route to serve minimal fields config:
```python
@app.route("/api/minimal-fields-config", methods=["GET"])
async def get_minimal_fields_config():
    config_path = Path(__file__).parent.parent / "minimal_fields_config.json"
    with open(config_path) as f:
        return JSONResponse(json.load(f))
```

**Test:**
```bash
# Start server
uvicorn insurance_server_python.main:app --port 8000

# Test endpoint
curl http://localhost:8000/api/minimal-fields-config
```

**Acceptance:** Config returns JSON with customer/driver/vehicle required fields

---

## Phase 2: Add "Show Optional Fields" Toggle (Minimal UI Change)
**Goal:** Add UI control without removing any fields yet

### Step 2.1: Add Toggle Button to Widget
**File:** `insurance_server_python/insurance_state_widget.py`

Add after line ~500 (near the top of the form):
```javascript
<div style="margin-bottom: 20px; padding: 12px; background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 6px;">
  <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
    <input
      type="checkbox"
      id="showOptionalFields"
      checked
      style="width: 18px; height: 18px;"
    />
    <span style="font-weight: 500;">Show optional fields (recommended for best rates)</span>
  </label>
</div>
```

**Test:**
1. Start server
2. Invoke widget in ChatGPT
3. Verify checkbox appears and can be toggled
4. All fields still visible (nothing hidden yet)

**Acceptance:** Checkbox renders, can be clicked, no functionality yet

---

### Step 2.2: Load Minimal Config in Widget
**File:** `insurance_server_python/insurance_state_widget.py`

Add after the `DOMContentLoaded` listener (around line ~2200):
```javascript
let minimalFieldsConfig = null;

// Load minimal fields configuration
fetch('/api/minimal-fields-config')
  .then(res => res.json())
  .then(config => {
    minimalFieldsConfig = config;
    console.log('Loaded minimal fields config:', config);
  })
  .catch(err => {
    console.error('Failed to load minimal fields config:', err);
    // If config fails to load, just show all fields
  });
```

**Test:**
1. Restart server
2. Invoke widget
3. Open browser console
4. Verify log: "Loaded minimal fields config: {...}"

**Acceptance:** Config loads successfully, logged to console, no UI changes

---

### Step 2.3: Implement Field Visibility Logic
**File:** `insurance_server_python/insurance_state_widget.py`

Add helper function after config loading:
```javascript
function isFieldRequired(section, fieldPath) {
  if (!minimalFieldsConfig) return true; // Show all if config not loaded

  const sectionConfig = minimalFieldsConfig[section];
  if (!sectionConfig) return true;

  return sectionConfig.required.includes(fieldPath);
}

function updateFieldVisibility() {
  const showOptional = document.getElementById('showOptionalFields').checked;

  // Customer fields
  document.querySelectorAll('[data-field]').forEach(field => {
    const section = field.getAttribute('data-section');
    const fieldPath = field.getAttribute('data-field');
    const isRequired = isFieldRequired(section, fieldPath);

    if (!isRequired && !showOptional) {
      field.style.display = 'none';
    } else {
      field.style.display = '';
    }
  });
}

// Attach to checkbox
document.getElementById('showOptionalFields').addEventListener('change', updateFieldVisibility);

// Initial update when config loads
if (minimalFieldsConfig) {
  updateFieldVisibility();
}
```

**Test:**
1. Restart server
2. Invoke widget
3. Toggle checkbox
4. Nothing happens yet (fields don't have data attributes)

**Acceptance:** No errors in console, logic ready for next step

---

### Step 2.4: Add Data Attributes to Customer Fields ONLY
**File:** `insurance_server_python/insurance_state_widget.py`

Wrap each customer field group in a div with data attributes:

**Example for FirstName (required):**
```html
<div data-section="customer" data-field="FirstName">
  <label>First Name <span style="color: red">*</span></label>
  <input type="text" id="firstName" required />
</div>
```

**Example for MiddleName (optional):**
```html
<div data-section="customer" data-field="MiddleName">
  <label>Middle Name</label>
  <input type="text" id="middleName" />
</div>
```

Only do customer section (~10 fields). Leave drivers/vehicles unchanged.

**Test:**
1. Restart server
2. Invoke widget
3. Toggle checkbox
4. Verify customer optional fields hide/show
5. Verify driver/vehicle sections unchanged

**Acceptance:**
- Customer optional fields hide when checkbox unchecked
- Customer required fields always visible
- Driver/vehicle sections unaffected
- Form still submits successfully

---

### Step 2.5: Add Data Attributes to Driver Fields
**File:** `insurance_server_python/insurance_state_widget.py`

Apply same pattern to driver fields:
- Wrap each field group in `<div data-section="driver" data-field="...">`
- Reference `minimal_fields_config.json` for which are required
- Test each field individually

**Test:**
1. Add a driver
2. Toggle checkbox
3. Verify driver optional fields hide/show
4. Add second driver, verify works for both
5. Remove driver, verify no errors

**Acceptance:**
- Driver optional fields hide when checkbox unchecked
- Multiple drivers work correctly
- No console errors

---

### Step 2.6: Add Data Attributes to Vehicle Fields
**File:** `insurance_server_python/insurance_state_widget.py`

Apply same pattern to vehicle fields.

**Test:** Same as driver testing

**Acceptance:** Same as driver acceptance

---

## Phase 3: Default to Minimal View
**Goal:** Change default to show only required fields

### Step 3.1: Change Checkbox Default
**File:** `insurance_server_python/insurance_state_widget.py`

Change:
```html
<input type="checkbox" id="showOptionalFields" checked />
```

To:
```html
<input type="checkbox" id="showOptionalFields" />
```

Change label text:
```html
<span>Show optional fields (helps us find better rates)</span>
```

**Test:**
1. Restart server
2. Invoke widget
3. Verify only ~30-40 required fields visible by default
4. Toggle checkbox to show all fields
5. Complete form with minimal fields only
6. Verify quote submits successfully

**Acceptance:**
- Only required fields visible by default
- Can toggle to see all fields
- Form validation works
- Submission successful

---

## Phase 4: Polish & UX Improvements

### Step 4.1: Add Field Count Indicator
Show user how many fields they're filling vs total:

```html
<span id="fieldCount" style="color: #64748b; font-size: 14px;">
  Showing 35 of 87 fields
</span>
```

Update count when toggling.

### Step 4.2: Add Progress Indicator
Show % complete as user fills fields:

```javascript
function updateProgress() {
  const required = document.querySelectorAll('[data-section][data-field]:not([style*="display: none"]) input[required]');
  const filled = Array.from(required).filter(input => input.value.trim() !== '').length;
  const total = required.length;
  const percent = Math.round((filled / total) * 100);

  document.getElementById('progress').textContent = `${percent}% complete`;
}
```

### Step 4.3: Improve Field Descriptions
Add helper text for required fields:
```html
<small style="color: #64748b;">We need this to calculate your rate accurately</small>
```

### Step 4.4: Add "Why is this required?" Tooltips
For confusing required fields like "MonthsAtResidence":
```html
<span style="cursor: help;" title="Length of residence affects your rate stability">ℹ️</span>
```

---

## Phase 5: Backend Integration

### Step 5.1: Apply Defaults on Submission
**File:** `insurance_server_python/tool_handlers.py`

Modify `_request_personal_auto_rate` to enrich payload:

```python
from .field_defaults import build_minimal_payload_with_defaults

# In handler:
if is_minimal_submission(payload):
    payload = build_minimal_payload_with_defaults(
        customer=payload['Customer'],
        drivers=payload['RatedDrivers'],
        vehicles=payload['Vehicles'],
        policy_coverages=payload['PolicyCoverages'],
        identifier=payload['Identifier'],
        effective_date=payload['EffectiveDate'],
        state=payload['Customer']['Address']['State']
    )
```

**Test:**
1. Submit quote with only required fields
2. Verify backend enriches with defaults
3. Verify API call succeeds
4. Compare with full-field submission

**Acceptance:**
- Minimal submission works
- Defaults applied correctly
- API accepts enriched payload
- Results match full submission

---

## Rollback Plan

If anything breaks at any step:

1. **During Phase 2:** Remove toggle button, remove data attributes
2. **During Phase 3:** Change checkbox back to `checked`
3. **During Phase 4:** Remove new UI elements
4. **During Phase 5:** Remove backend enrichment logic

Each step is independently revertible.

---

## Testing Checklist (After Each Step)

- [ ] Widget loads without errors
- [ ] All existing functionality works
- [ ] Console has no errors
- [ ] Form validation works
- [ ] Submission succeeds
- [ ] Quote ID captured correctly
- [ ] Results display correctly

---

## Success Metrics

**Before:**
- 80-100 fields visible
- 10-15 minute completion time
- High abandonment rate

**After:**
- 30-40 required fields by default
- 5-7 minute completion time
- Optional fields accessible via toggle
- Same quote quality
- No loss of functionality

---

## Timeline Estimate

Each step ~15-30 minutes:
- Phase 1: Already complete ✅
- Phase 2: 2-3 hours (6 steps × 20-30 min)
- Phase 3: 30 minutes (1 step with thorough testing)
- Phase 4: 1-2 hours (4 polish steps)
- Phase 5: 1 hour (backend integration)

**Total: 4-6 hours** of incremental, testable work

---

## Key Principles

1. **One change at a time** - Test after every modification
2. **Preserve existing functionality** - Never remove, only hide
3. **Progressive enhancement** - Toggle makes it optional
4. **Backend safety** - Defaults fill in missing data
5. **Easy rollback** - Each step independently revertible

---

## Notes

- Keep existing widget registration (`insurance-state-selector`)
- Don't create new widgets
- Don't change tool names or schemas
- All changes are additive (hiding, not removing)
- Backend enrichment ensures API always gets complete data
