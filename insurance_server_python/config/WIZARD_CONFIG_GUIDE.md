# Wizard Configuration Guide

## Overview

The wizard flow is **fully config-driven** - all 5 steps, fields, validation, and submission logic are defined in external JSON files that can be edited without code changes.

---

## Configuration Files

### 1. `wizard_fields.json` (77 fields)
Defines all fields used in the wizard:

```json
{
  "fields": {
    "firstName": {
      "name": "firstName",
      "field_type": "string",
      "required": true,
      "validation": {"min_length": 1, "max_length": 50},
      "prompt_text": "First Name",
      "example": "John",
      "contexts": ["wizard_customer"],
      "group": "personal"
    },
    ...
  }
}
```

**Field Properties**:
- `name` - Unique field identifier
- `field_type` - Data type (string, integer, boolean, date)
- `required` - Whether field is required
- `validation` - Validation rules (pattern, min_length, etc.)
- `prompt_text` - Label shown to user
- `example` - Placeholder text
- `contexts` - Where field is used (wizard_policy, wizard_customer, wizard_vehicle, wizard_driver)
- `group` - Visual grouping
- `enum_values` - Options for select fields
- `default` - Default value

### 2. `wizard_flow.json` (5 steps)
Defines the wizard structure:

```json
{
  "wizard": {
    "name": "personal_auto_wizard",
    "title": "Complete Your Insurance Application",
    "description": "We'll guide you through 5 quick steps",
    "trigger_after": "quick_quote",
    "steps": [
      {
        "id": 1,
        "name": "policy_setup",
        "title": "Policy Setup",
        "sections": [
          {
            "title": "Policy Details",
            "fields": [
              {"name": "effectiveDate", "required": true},
              {"name": "term", "required": true}
            ]
          }
        ]
      }
    ],
    "validation": {
      "required_fields": ["firstName", "lastName", ...]
    },
    "submission": {
      "tool_name": "request-personal-auto-rate",
      "payload_structure": {...}
    }
  }
}
```

---

## Wizard Flow Structure

### Steps 1-4: Collection Steps

Each step contains:
- `id` - Step number (1-5)
- `name` - Internal identifier
- `title` - Full title
- `label` - Short label for stepper
- `sections` - Array of field sections

**Section Structure**:
```json
{
  "title": "Section Title",
  "fields": [
    {
      "name": "fieldName",
      "required": true,
      "fullWidth": false
    }
  ]
}
```

### Step 5: Review Step

Special review step:
```json
{
  "id": 5,
  "name": "review",
  "title": "Review & Submit",
  "is_review": true,
  "review_sections": [
    {
      "title": "Policy Setup",
      "fields": ["effectiveDate", "term", ...],
      "edit_step": 1
    }
  ]
}
```

---

## User Flow

```
┌─────────────────────────────────────────────────────────┐
│ 1. Quick Quote (zip + drivers)                         │
│    → Shows quote range                                  │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ 2. User wants detailed quote                           │
│    → Wizard starts                                      │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ Step 1: Policy Setup (6 fields)                        │
│   - Effective Date                                      │
│   - Term, Payment Method, Policy Type                   │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ Step 2: Customer Information (18 fields)               │
│   - Personal: Name, months at residence                │
│   - Address: Street, city, state, zip                  │
│   - Contact: Phone, email                              │
│   - Insurance: Prior insurance info                    │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ Step 3: Vehicle Details (25 fields)                    │
│   - Vehicle: Make, model, year, mileage                │
│   - Garaging: Where vehicle is stored                  │
│   - Coverage: Deductibles, limits                      │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ Step 4: Driver Information (36 fields)                 │
│   - Details: Name, DOB, occupation                     │
│   - License: Status, state, experience                 │
│   - Attributes: Education, residency                   │
│   - Discounts: Good student, defensive driving         │
│   - SR-22: If applicable                               │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ Step 5: Review & Submit                                │
│   - Shows all collected data in sections               │
│   - Edit buttons to go back to any step               │
│   - Validation before submission                       │
│   - "Confirm & Submit" button                          │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ 3. Submit to request-personal-auto-rate tool           │
│    → Get full detailed quote                           │
└─────────────────────────────────────────────────────────┘
```

---

## Backend Usage

### Loading Configuration

```python
from insurance_server_python.wizard_config_loader import (
    get_wizard_flow,
    get_wizard_fields,
    get_wizard_step,
    get_field_definition,
    build_payload_from_form_data
)

# Get full wizard config
wizard = get_wizard_flow()

# Get specific step
step_1 = get_wizard_step(1)

# Get field definition
first_name_field = get_field_definition("firstName")

# Build API payload from form data
form_data = {
    "firstName": "John",
    "lastName": "Smith",
    ...
}
payload = build_payload_from_form_data(form_data)
```

### Serving Config to Frontend

Add API endpoint:

```python
@app.get("/api/wizard-config")
async def get_wizard_config():
    """Serve wizard configuration to frontend."""
    from insurance_server_python.wizard_config_loader import (
        get_wizard_flow,
        get_wizard_fields
    )

    return {
        "wizard": get_wizard_flow(),
        "fields": get_wizard_fields()
    }
```

### Hot Reload

```python
from insurance_server_python.wizard_config_loader import reload_wizard_config

@app.post("/admin/reload-wizard-config")
async def reload_wizard():
    """Reload wizard config without restart."""
    reload_wizard_config()
    return {"status": "success"}
```

---

## Frontend Usage

### Fetching Configuration

```javascript
// Fetch wizard config from backend
const response = await fetch('/api/wizard-config');
const { wizard, fields } = await response.json();

// Now render wizard dynamically based on config
```

### Rendering Steps

```javascript
wizard.steps.forEach(step => {
  if (step.is_review) {
    // Render review step
    renderReviewStep(step);
  } else {
    // Render collection step
    renderCollectionStep(step, fields);
  }
});
```

### Building Form from Config

```javascript
function renderCollectionStep(step, fields) {
  step.sections.forEach(section => {
    // Render section title
    const sectionEl = document.createElement('div');
    sectionEl.innerHTML = `<h3>${section.title}</h3>`;

    // Render fields
    section.fields.forEach(fieldConfig => {
      const fieldDef = fields[fieldConfig.name];
      const input = createInput(fieldDef, fieldConfig);
      sectionEl.appendChild(input);
    });
  });
}

function createInput(fieldDef, fieldConfig) {
  const type = fieldDef.field_type;

  switch(type) {
    case 'string':
      return createTextInput(fieldDef, fieldConfig);
    case 'date':
      return createDateInput(fieldDef, fieldConfig);
    case 'boolean':
      return createCheckbox(fieldDef, fieldConfig);
    case 'integer':
      return createNumberInput(fieldDef, fieldConfig);
  }
}
```

### Validation

```javascript
function validateForm(formData, wizard) {
  const errors = [];
  const required = wizard.validation.required_fields;

  required.forEach(fieldName => {
    if (!formData[fieldName]) {
      errors.push(`${fieldName} is required`);
    }
  });

  return errors;
}
```

### Submission

```javascript
async function submitWizard(formData, wizard) {
  // Frontend sends form data
  // Backend builds payload using build_payload_from_form_data()

  const response = await fetch('/api/wizard-submit', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(formData)
  });

  return response.json();
}
```

---

## Editing the Configuration

### Add a New Field

1. **Add to `wizard_fields.json`**:
```json
{
  "phoneNumber": {
    "name": "phoneNumber",
    "field_type": "string",
    "required": false,
    "validation": {"pattern": "^[0-9]{10}$"},
    "prompt_text": "Phone Number",
    "example": "5551234567",
    "contexts": ["wizard_customer"],
    "group": "contact"
  }
}
```

2. **Add to wizard step** in `wizard_flow.json`:
```json
{
  "sections": [
    {
      "title": "Contact Information",
      "fields": [
        ...existing fields...,
        {"name": "phoneNumber", "required": false}
      ]
    }
  ]
}
```

3. **Add to payload mapping** (if needed):
```json
{
  "submission": {
    "payload_structure": {
      "Customer": {
        "ContactInformation": {
          ...
          "PhoneNumber": "phoneNumber"
        }
      }
    }
  }
}
```

4. **Validate**:
```bash
python -c "from insurance_server_python.wizard_config_loader import validate_wizard_config; validate_wizard_config()"
```

### Reorder Fields

Just change the order in the `fields` array:

```json
{
  "fields": [
    {"name": "lastName", "required": true},   // Moved up
    {"name": "firstName", "required": true}   // Moved down
  ]
}
```

### Change Field to Optional

Update in `wizard_fields.json`:
```json
{
  "emailAddress": {
    ...
    "required": false  // Changed from true
  }
}
```

And remove from validation:
```json
{
  "validation": {
    "required_fields": [
      // Remove "emailAddress" from this list
    ]
  }
}
```

### Add New Step

```json
{
  "steps": [
    ...existing steps...,
    {
      "id": 6,
      "name": "additional_info",
      "title": "Additional Information",
      "label": "Additional",
      "sections": [
        {
          "title": "Extra Details",
          "fields": [...]
        }
      ]
    }
  ]
}
```

---

## Testing

### Validate Configuration

```bash
python insurance_server_python/wizard_config_loader.py
```

Expected output:
```
✓ Loaded 77 wizard field definitions
✓ Loaded wizard: personal_auto_wizard
✓ Found 5 wizard steps
✓ All wizard field references are valid
✓ All 14 required fields are defined
✅ Wizard configuration is valid!
```

### Test Data

Built-in test data available:

```python
from insurance_server_python.wizard_config_loader import get_test_data

test_data = get_test_data()
# Returns pre-filled form data for testing
```

Test data includes:
- Customer: John Smith, Beverly Hills CA
- Vehicle: 2018 Honda Civic
- Driver: Matches customer, born 1990-01-15

---

## Benefits of Config-Driven Approach

### ✅ No Code Changes for Field Modifications
- Add/remove fields: Edit JSON
- Reorder fields: Change array order
- Change validation: Update validation rules
- Update labels: Change prompt_text

### ✅ Easy A/B Testing
Create multiple wizard configs:
- `wizard_flow_short.json` - Minimal fields
- `wizard_flow_detailed.json` - All fields
- Toggle between them via config

### ✅ Hot Reload
Change config → reload → no restart needed

### ✅ Version Control
- Track config changes in git
- Easy rollback
- PR reviews for config changes

### ✅ Non-Developer Friendly
Business users can:
- Edit field labels
- Change field order
- Add optional fields
- Update defaults

---

## Frontend Widget Generation

The same config can generate:

1. **React Component**
```javascript
import WizardRenderer from './WizardRenderer';

<WizardRenderer
  config={wizardConfig}
  fields={fieldsConfig}
  onSubmit={handleSubmit}
/>
```

2. **HTML Widget** (like original)
- Generate stepper from `wizard.steps`
- Generate forms from `step.sections`
- Generate inputs from `fields[fieldName]`
- Wire up validation from `wizard.validation`
- Handle submission per `wizard.submission`

3. **Mobile App**
- Use same JSON config
- Render native inputs
- Same validation logic
- Same API payload

---

## Files Reference

### Configuration Files
- `insurance_server_python/config/wizard_fields.json` - All 77 field definitions
- `insurance_server_python/config/wizard_flow.json` - 5-step wizard structure

### Backend Code
- `insurance_server_python/wizard_config_loader.py` - Config loader and validator
- `insurance_server_python/tool_handlers.py` - Wizard submission handler (to add)
- `insurance_server_python/widget_registry.py` - Tool registration (to add)

### Documentation
- `WIZARD_FLOW_SPECIFICATION.md` - Original wizard spec from commit a013415
- `insurance_server_python/config/WIZARD_CONFIG_GUIDE.md` - This file

---

## Next Steps

1. **Add API Endpoint** to serve config:
   ```python
   @app.get("/api/wizard-config")
   async def get_wizard_config():
       return {
           "wizard": get_wizard_flow(),
           "fields": get_wizard_fields()
       }
   ```

2. **Create Wizard Widget** that fetches config and renders dynamically

3. **Add Wizard Tool Handler** that:
   - Receives form data
   - Validates using config
   - Builds payload using `build_payload_from_form_data()`
   - Submits to `request-personal-auto-rate`

4. **Register Wizard Tool** in widget_registry.py

5. **Test End-to-End**:
   - Quick quote → wizard trigger
   - Fill all steps
   - Review
   - Submit
   - Get detailed quote

---

## Summary

The wizard is now **100% config-driven**:

- ✅ 77 fields defined in `wizard_fields.json`
- ✅ 5 steps defined in `wizard_flow.json`
- ✅ Validation rules in config
- ✅ Payload mapping in config
- ✅ Test data in config
- ✅ Backend loader implemented
- ✅ Hot reload support
- ✅ Config validation tool

**No code changes needed** to:
- Add/remove/reorder fields
- Change validation
- Update labels/placeholders
- Modify steps
- Change submission logic

Ready to build the frontend wizard renderer! 🎉
