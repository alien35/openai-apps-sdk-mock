# Config-Driven Architecture - Complete Guide

## 🎯 Overview

The adaptive architecture is now **truly config-driven** - all flows and fields are defined in external JSON files that can be edited by non-developers without code changes.

---

## 📍 Configuration Location

### Primary Config Files:
```
insurance_server_python/config/
├── README.md          ← Complete usage guide
├── fields.json        ← Field definitions (validation, prompts, etc.)
└── flows.json         ← Flow configurations (stages, submission criteria)
```

### Supporting Code:
```
insurance_server_python/
├── config_loader.py      ← Loads JSON configs into Python objects
├── field_registry.py     ← Field definition classes (used by loader)
├── flow_configs.py       ← Flow configuration classes (used by loader)
└── collection_engine.py  ← Engine that uses the configs
```

---

## 🔄 How It Works

```
┌─────────────────┐
│  fields.json    │  ← Business users edit JSON
│  flows.json     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ config_loader.py│  ← Loads and validates JSON
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Python Objects  │  ← FieldDefinition, FlowConfig
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ collection_     │  ← Uses configs for field collection
│    engine.py    │
└─────────────────┘
```

---

## ✅ What You Can Do Without Code Changes

### 1. Enable/Disable Flows
Edit `flows.json`:
```json
{
  "name": "quick_quote_v1",
  "metadata": {
    "active": true   // Change to false to disable this flow
  }
}
```

### 2. Reorder Fields
Change the order in the `fields` array:
```json
{
  "stages": [
    {
      "fields": ["NumberOfDrivers", "ZipCode"]  // Reversed order
    }
  ]
}
```

### 3. Add Optional Fields
Add to `optional_fields` array:
```json
{
  "stages": [
    {
      "fields": ["ZipCode", "NumberOfDrivers", "EmailAddress"],
      "optional_fields": ["EmailAddress"]  // New optional field
    }
  ]
}
```

### 4. Change Validation Rules
Edit field validation in `fields.json`:
```json
{
  "NumberOfDrivers": {
    "validation": {
      "min": 1,
      "max": 15    // Changed from 10 to 15
    }
  }
}
```

### 5. Update User-Facing Text
Edit prompts and help text:
```json
{
  "ZipCode": {
    "prompt_text": "What is your ZIP code?",  // Changed
    "help_text": "5-digit postal code"        // Changed
  }
}
```

### 6. Add New Fields
Add to `fields.json`:
```json
{
  "PhoneNumber": {
    "name": "PhoneNumber",
    "field_type": "string",
    "required": false,
    "validation": {
      "pattern": "^[0-9]{10}$"
    },
    "prompt_text": "What's your phone number?",
    "contexts": ["customer"]
  }
}
```

Then reference in a flow:
```json
{
  "stages": [
    {
      "fields": ["ZipCode", "NumberOfDrivers", "PhoneNumber"]
    }
  ]
}
```

### 7. Enable Review Stage
Add review stage in `flows.json`:
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
      "fields": ["ZipCode", "NumberOfDrivers"]
    }
  ],
  "submission_criteria": {
    "review_required": true
  }
}
```

### 8. Create A/B Test Variants
Create two flows with same `ab_test` tag:
```json
[
  {
    "name": "quick_quote_control",
    "metadata": {
      "active": true,
      "ab_test": "email_test",
      "variant": "control"
    }
  },
  {
    "name": "quick_quote_with_email",
    "metadata": {
      "active": true,
      "ab_test": "email_test",
      "variant": "treatment"
    }
  }
]
```

---

## 🚀 Quick Start

### 1. View Current Configuration
```bash
# See all fields
cat insurance_server_python/config/fields.json | python -m json.tool

# See all flows
cat insurance_server_python/config/flows.json | python -m json.tool
```

### 2. Validate Configuration
```bash
python -c "
import sys
sys.path.insert(0, '.')
from insurance_server_python.config_loader import validate_config
validate_config()
"
```

Expected output:
```
✓ Loaded 6 field definitions
✓ Loaded 4 flow configurations
✓ All flow field references are valid
✓ Active flows: {'quick_quote': 1}
```

### 3. Make Changes
Edit `fields.json` or `flows.json` with any text editor

### 4. Validate Again
```bash
python -c "from insurance_server_python.config_loader import validate_config; validate_config()"
```

### 5. Reload (Optional Hot Reload)
```python
from insurance_server_python.config_loader import reload_config
reload_config()
```

Or restart server:
```bash
uvicorn insurance_server_python.main:app --port 8000
```

---

## 📋 Current Configuration

### Fields (6 defined):
1. **ZipCode** - 5-digit zip code (required)
2. **NumberOfDrivers** - 1-10 drivers (required)
3. **EmailAddress** - Email for quotes (optional)
4. **FirstName** - Legal first name (required for credit flows)
5. **LastName** - Legal last name (required for credit flows)
6. **DateOfBirth** - YYYY-MM-DD format (required for credit flows)

### Flows (4 defined):

#### quick_quote_v1 ✅ ACTIVE
- **Fields**: ZipCode, NumberOfDrivers
- **Review**: No
- **Use case**: Fastest path, minimal friction

#### quick_quote_v2 (inactive)
- **Fields**: ZipCode, NumberOfDrivers, EmailAddress (optional)
- **Review**: No
- **Use case**: Lead capture

#### quick_quote_v3 (inactive)
- **Fields**: ZipCode, NumberOfDrivers, FirstName, LastName, DateOfBirth
- **Review**: No
- **Use case**: Credit-based pricing

#### quick_quote_v1_with_review (inactive)
- **Fields**: ZipCode, NumberOfDrivers
- **Review**: Yes
- **Use case**: Higher accuracy with user verification

---

## 🎨 Example: Switch Active Flow

### Scenario: Enable email collection

**Before** (`flows.json`):
```json
{
  "name": "quick_quote_v1",
  "metadata": { "active": true }
},
{
  "name": "quick_quote_v2",
  "metadata": { "active": false }
}
```

**After** (`flows.json`):
```json
{
  "name": "quick_quote_v1",
  "metadata": { "active": false }   // ← Changed
},
{
  "name": "quick_quote_v2",
  "metadata": { "active": true }    // ← Changed
}
```

**Result**: System now collects email address as optional field!

---

## 🛠️ Advanced Usage

### Hot Reload API (Optional Implementation)

Add to your FastAPI server:

```python
from insurance_server_python.config_loader import reload_config

@app.post("/admin/reload-config")
async def reload_configuration():
    """Reload configuration from JSON files without restart."""
    try:
        reload_config()
        return {"status": "success", "message": "Configuration reloaded"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

Usage:
```bash
curl -X POST http://localhost:8000/admin/reload-config
```

### Version Control Integration

Track config changes:
```bash
# Before changes
git diff insurance_server_python/config/flows.json

# Commit changes
git add insurance_server_python/config/*.json
git commit -m "Enable email collection in quick quote v2"

# Deploy
git push origin main
```

### Rollback Changes

If something goes wrong:
```bash
# Rollback to previous version
git checkout HEAD~1 -- insurance_server_python/config/flows.json

# Validate
python -c "from insurance_server_python.config_loader import validate_config; validate_config()"

# Reload
curl -X POST http://localhost:8000/admin/reload-config
```

---

## ✅ Benefits

### For Business Users
- ✅ Change flows without developer help
- ✅ A/B test different variants easily
- ✅ Quick rollback if issues occur
- ✅ See all flows in one place

### For Developers
- ✅ No code changes for flow modifications
- ✅ Configuration versioned with git
- ✅ Easy to review changes in PRs
- ✅ Validation catches errors early

### For Operations
- ✅ Hot reload without downtime
- ✅ Audit trail of all changes
- ✅ Easy rollback procedures
- ✅ No deployment required for config changes

---

## 📊 Testing

### Unit Test with Config
```python
from insurance_server_python.config_loader import load_field_registry, load_flow_configs

def test_config_loading():
    fields = load_field_registry()
    assert "ZipCode" in fields
    assert fields["ZipCode"].field_type == FieldType.STRING

    flows = load_flow_configs()
    assert len(flows) >= 4

    active_flows = [f for f in flows if f.metadata.get("active")]
    assert len(active_flows) >= 1
```

### Integration Test
```python
from insurance_server_python.collection_engine import create_collection_engine
from insurance_server_python.flow_configs import FlowType

def test_collection_with_config():
    engine = create_collection_engine(FlowType.QUICK_QUOTE)

    state = engine.collect_fields({
        "ZipCode": "94103",
        "NumberOfDrivers": 2
    })

    assert state.status == CollectionStatus.READY_TO_SUBMIT
```

---

## 🔍 Troubleshooting

### Config Not Loading
**Problem**: Changes to JSON not reflected
**Solution**:
1. Validate JSON syntax: `python -m json.tool config/flows.json`
2. Reload config: `reload_config()` or restart server
3. Check for caching issues

### Field Not Found
**Problem**: "Unknown field: PhoneNumber"
**Solution**:
1. Ensure field defined in `fields.json`
2. Check exact spelling (case-sensitive)
3. Validate config: `validate_config()`

### No Active Flow
**Problem**: System uses fallback behavior
**Solution**:
1. Set one flow to `"active": true`
2. Validate: `validate_config()` shows active flows
3. Reload config

---

## 📚 Documentation

- **config/README.md** - Detailed config file usage
- **ADAPTIVE_ARCHITECTURE.md** - Overall architecture
- **ADAPTIVE_ARCHITECTURE_REVIEW.md** - Review stage design
- **REVIEW_STAGE_EXAMPLE.md** - Practical examples

---

## 🎯 Next Steps

### Immediate:
1. Review current config: `cat config/*.json`
2. Validate: `validate_config()`
3. Make a test change to inactive flow
4. Validate again

### Short-term:
1. Implement hot reload API endpoint
2. Add config change notifications
3. Create config editing UI (optional)
4. Set up automated config validation in CI/CD

### Long-term:
1. Move config to database for multi-tenant support
2. Add config versioning and audit log
3. Create config management dashboard
4. Implement gradual rollout for config changes

---

## ✨ Summary

**Configuration is now truly external!**

- ✅ **fields.json** - All field definitions
- ✅ **flows.json** - All flow configurations
- ✅ **config_loader.py** - Loads configs dynamically
- ✅ Hot reload support
- ✅ Validation built-in
- ✅ No code changes needed for flow modifications

**Business users can now:**
- Change question order
- Add/remove fields
- Enable/disable flows
- Create A/B tests
- Update validation rules
- Modify user-facing text

**All without touching a single line of Python code!** 🎉
