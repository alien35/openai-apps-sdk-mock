# Configuration Files

This directory contains **external JSON configuration** for the adaptive architecture, allowing non-developers to modify flows and fields without touching code.

## 📁 Files

### `fields.json`
**Single source of truth for all collectable fields**

Defines:
- Field names and types
- Validation rules (regex patterns, min/max, lengths)
- User-facing prompts and help text
- Examples
- Contexts (which flows can use this field)
- API mappings

### `flows.json`
**Flow configurations for different collection strategies**

Defines:
- Flow names and versions
- Stages (collection vs review)
- Required and optional fields per stage
- Submission criteria
- Active/inactive status
- A/B test variants
- Metadata

---

## 🎯 Use Cases

### 1. Enable/Disable Flows
Toggle flows on/off by changing the `active` flag:

```json
{
  "name": "quick_quote_v1",
  "metadata": {
    "active": true   // ← Change to false to disable
  }
}
```

### 2. Add New Fields to a Flow
Edit the `fields` array in a stage:

```json
{
  "stages": [
    {
      "fields": ["ZipCode", "NumberOfDrivers", "PhoneNumber"]
      //                                        ^^^^^^^^^^^^^ Added
    }
  ]
}
```

### 3. Create A/B Test Variants
Create two flows with same `ab_test` metadata:

```json
{
  "name": "quick_quote_variant_a",
  "metadata": {
    "active": true,
    "ab_test": "review_test",
    "variant": "A"
  }
},
{
  "name": "quick_quote_variant_b",
  "metadata": {
    "active": true,
    "ab_test": "review_test",
    "variant": "B"
  }
}
```

### 4. Enable Review Stage
Add a review stage and set `review_required`:

```json
{
  "stages": [
    {
      "name": "collect",
      "stage_type": "collection",
      "fields": ["ZipCode", "NumberOfDrivers"]
    },
    {
      "name": "review",
      "stage_type": "review",
      "fields": ["ZipCode", "NumberOfDrivers"],
      "description": "Review your information"
    }
  ],
  "submission_criteria": {
    "review_required": true
  }
}
```

### 5. Add New Field Definition
Add a new field to `fields.json`:

```json
{
  "PhoneNumber": {
    "name": "PhoneNumber",
    "alias": "PhoneNumber",
    "field_type": "string",
    "required": false,
    "validation": {
      "pattern": "^[0-9]{10}$",
      "error_message": "Invalid phone number (10 digits required)"
    },
    "prompt_text": "What's your phone number?",
    "help_text": "10 digits, no spaces or dashes",
    "example": "5551234567",
    "contexts": ["customer"],
    "group": "contact",
    "api_path": "Customer.PhoneNumber"
  }
}
```

---

## 🔄 Hot Reload

Changes to JSON files can be loaded without restarting the server:

```python
from insurance_server_python.config_loader import reload_config

# Force reload of all configuration
reload_config()
```

Or via API endpoint (if implemented):
```bash
curl -X POST http://localhost:8000/admin/reload-config
```

---

## ✅ Validation

Validate configuration files:

```bash
python -c "
import sys
sys.path.insert(0, '.')
from insurance_server_python.config_loader import validate_config
validate_config()
"
```

Output:
```
✓ Loaded 6 field definitions
✓ Loaded 4 flow configurations
✓ All flow field references are valid
✓ Active flows: {'quick_quote': 1}
✅ Configuration is valid!
```

---

## 📋 Field Types

Supported `field_type` values:
- `"string"` - Text fields
- `"integer"` - Whole numbers
- `"decimal"` - Decimal numbers
- `"boolean"` - True/false
- `"date"` - Date values (YYYY-MM-DD)
- `"array"` - Lists
- `"object"` - Nested objects

---

## 🔒 Validation Rules

### Pattern (Regex)
```json
{
  "validation": {
    "pattern": "^[0-9]{5}$",
    "error_message": "Must be 5 digits"
  }
}
```

### Min/Max (Numbers)
```json
{
  "validation": {
    "min": 1,
    "max": 10,
    "error_message": "Must be between 1 and 10"
  }
}
```

### Length (Strings)
```json
{
  "validation": {
    "min_length": 1,
    "max_length": 50,
    "error_message": "Must be 1-50 characters"
  }
}
```

---

## 🎨 Stage Types

### `"collection"` (Default)
Normal field collection stage where users provide information.

### `"review"`
Review and correction stage where users can see and modify collected data before submission.

---

## 📖 Contexts

Fields can be used in multiple contexts:

- `"quick_quote"` - Quick quote flows
- `"customer"` - Customer data collection
- `"driver"` - Driver information
- `"vehicle"` - Vehicle details

Example:
```json
{
  "contexts": ["quick_quote", "customer"]
}
```

---

## 🚀 Example: Create New Flow

1. **Add fields** (if needed) to `fields.json`
2. **Create flow** in `flows.json`:

```json
{
  "name": "quick_quote_california",
  "flow_type": "quick_quote",
  "stages": [
    {
      "name": "initial",
      "stage_type": "collection",
      "fields": ["ZipCode", "NumberOfDrivers", "EarthquakeInsurance"],
      "optional_fields": ["EarthquakeInsurance"],
      "description": "California-specific quick quote"
    }
  ],
  "submission_criteria": {
    "required_fields": ["ZipCode", "NumberOfDrivers"],
    "generate_scenarios": true,
    "state_specific": "CA"
  },
  "metadata": {
    "version": "1.0",
    "active": false,
    "state_specific": "CA",
    "description": "Quick quote for California residents"
  }
}
```

3. **Validate**:
```bash
python -c "from insurance_server_python.config_loader import validate_config; validate_config()"
```

4. **Activate**:
Change `"active": false` to `"active": true`

5. **Reload** (optional):
```python
from insurance_server_python.config_loader import reload_config
reload_config()
```

---

## 🛡️ Best Practices

### 1. Version Control
Commit config files to git:
```bash
git add insurance_server_python/config/*.json
git commit -m "Update quick quote flow to include email"
```

### 2. Validate Before Deployment
Always validate config before deploying:
```bash
python -c "from insurance_server_python.config_loader import validate_config; validate_config()"
```

### 3. Use Descriptive Names
```json
{
  "name": "quick_quote_v2_email_capture",  // Good
  "name": "qqv2",                          // Bad
}
```

### 4. Document Changes in Metadata
```json
{
  "metadata": {
    "version": "2.1",
    "description": "Added email collection for lead capture",
    "changed_by": "Product Team",
    "changed_date": "2024-02-18"
  }
}
```

### 5. Test in Non-Production First
- Create flow with `"active": false`
- Test thoroughly
- Then set `"active": true`

---

## 📝 Schema Documentation

Both JSON files follow JSON Schema standards. You can use JSON Schema validators in your editor for autocomplete and validation:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema"
}
```

---

## 🔍 Troubleshooting

### "Field not found" Error
Check that field name in `flows.json` matches exactly (case-sensitive) with `fields.json`

### "Flow not loading"
Ensure JSON syntax is valid:
```bash
python -m json.tool insurance_server_python/config/flows.json
```

### "No active flow"
At least one flow per type should have `"active": true`

---

## 📚 Related Documentation

- **ADAPTIVE_ARCHITECTURE.md** - Architecture overview
- **ADAPTIVE_POC_DEMO.md** - POC demonstration
- **REVIEW_STAGE_EXAMPLE.md** - Review stage usage

---

## 💡 Tips

- Use a JSON editor with schema validation (VS Code, IntelliJ)
- Keep flows simple - start with minimal fields
- Use A/B testing to compare different flows
- Monitor active flag - only one flow per type should be active (unless A/B testing)
- Document business logic in metadata descriptions
