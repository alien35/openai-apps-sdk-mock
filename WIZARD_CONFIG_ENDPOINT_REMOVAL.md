# Removal of `/api/wizard-config` Endpoint

## Date: 2024

## Summary
Removed the `/api/wizard-config` HTTP endpoint and its fallback logic from the wizard widget. The wizard configuration is now exclusively passed via MCP tool's `structuredContent`, eliminating redundant code paths.

## Reason for Removal

### Primary Usage Pattern (Production)
The wizard always receives configuration through the MCP tool flow:

```python
# tool_handlers.py - _start_wizard_flow()
wizard_config = get_wizard_flow()
fields_config = get_wizard_fields()

return {
    "structured_content": {
        "wizard_config": wizard_config,    # ← Passed directly
        "fields_config": fields_config,    # ← Passed directly
        "server_url": server_base_url,
        "pre_fill_data": {...}
    }
}
```

### Redundant Fallback (Unused in Production)
The `/api/wizard-config` endpoint was only used as a fallback when:
- Widget HTML was opened directly (not via MCP)
- Development/testing without MCP integration
- Non-existent use cases in production

Since the wizard is **always** launched via MCP tools in production, the endpoint and fallback logic were dead code.

## Files Modified

### 1. `insurance_server_python/main.py`

**Removed OpenAPI spec entry (lines 321-352):**
```python
"/api/wizard-config": {
    "get": {
        "summary": "Get wizard configuration",
        "description": "Returns wizard flow and field definitions for frontend",
        "tags": ["Configuration"],
        # ... full spec
    }
}
```

**Removed endpoint route (lines 532-552):**
```python
@app.route("/api/wizard-config", methods=["GET"])
async def get_wizard_config(request: Request):
    """Serve wizard configuration to frontend."""
    from .wizard_config_loader import get_wizard_flow, get_wizard_fields

    try:
        wizard = get_wizard_flow()
        fields = get_wizard_fields()
        return JSONResponse(...)
    except Exception as e:
        logger.exception("Failed to load wizard configuration")
        return JSONResponse({"error": ...}, status_code=500)
```

### 2. `insurance_server_python/insurance_wizard_widget_html.py`

**Before (lines 235-289):**
```javascript
async function initWizard() {
    try {
        const structuredContent = window.structuredContent || ...;

        if (structuredContent.wizard_config && structuredContent.fields_config) {
            // Use config from structured content
            wizardConfig = structuredContent.wizard_config;
            fieldsConfig = structuredContent.fields_config;
        } else {
            // FALLBACK: Fetch from API (REMOVED)
            const serverUrls = [
                serverBaseUrl + '/api/wizard-config',
                '/api/wizard-config',
                window.location.origin + '/api/wizard-config'
            ];

            // Try each URL until one works...
            for (const url of serverUrls) {
                const response = await fetch(url);
                // ... fetch logic ...
            }
        }
        // ...
    }
}
```

**After (lines 235-253):**
```javascript
async function initWizard() {
    try {
        // Get config from structured content (passed from backend via MCP tool)
        const structuredContent = window.structuredContent || window.parent?.structuredContent || {};

        if (!structuredContent.wizard_config || !structuredContent.fields_config) {
            throw new Error('Wizard configuration not provided. This widget must be launched via MCP tool.');
        }

        // Config was passed from backend
        console.log('Using config from structured content');
        wizardConfig = structuredContent.wizard_config;
        fieldsConfig = structuredContent.fields_config;

        // Pre-fill data if available
        if (structuredContent.pre_fill_data) {
            formData = { ...structuredContent.pre_fill_data };
        }
        // ...
    }
}
```

**Key Changes:**
- ❌ Removed entire `else` block with API fallback (54 lines)
- ✅ Added early validation: throws error if config not provided
- ✅ Clear error message: "This widget must be launched via MCP tool"
- ✅ Simplified logic: single code path instead of two

### 3. `SWAGGER_OPENAPI_INTEGRATION.md`

**Removed from Configuration Endpoints section:**
```markdown
### Configuration Endpoints
- `GET /api/wizard-config` - Wizard flow and field definitions
```

Now the Configuration section is empty and only Quote endpoints remain.

## What Remains (Intentionally Kept)

### Core Wizard Functionality - NOT Removed

**Still Active and Used:**

#### 1. `wizard_config_loader.py` ✅
- Functions: `get_wizard_flow()`, `get_wizard_fields()`, `build_payload_from_form_data()`
- **Still used by:** `tool_handlers.py` for MCP tool integration
- **Purpose:** Load and parse wizard configuration from JSON files

#### 2. `config/wizard_flow.json` ✅
- Wizard step definitions and flow logic
- **Still used by:** `wizard_config_loader.py`

#### 3. `config/wizard_fields.json` ✅
- Field definitions, validation, enums
- **Still used by:** `wizard_config_loader.py`

#### 4. `insurance_wizard_widget_html.py` ✅
- Widget implementation (with simplified config loading)
- **Still used by:** MCP tools to render the wizard UI

#### 5. MCP Tool Integration ✅
```python
# tool_handlers.py - _start_wizard_flow()
wizard_config = get_wizard_flow()      # ← Still called
fields_config = get_wizard_fields()    # ← Still called

return {
    "structured_content": {
        "wizard_config": wizard_config,
        "fields_config": fields_config,
        # ...
    }
}
```

**This is the ONLY production code path** - and it still works perfectly.

## Impact Analysis

### ✅ No Breaking Changes in Production
- MCP tool flow unchanged
- Widget receives config the same way
- All 100 tests pass
- No functionality lost

### ✅ Benefits
- **Cleaner code:** Removed 54+ lines of fallback logic
- **Single code path:** Easier to maintain and debug
- **Clear expectations:** Widget explicitly requires MCP integration
- **Accurate docs:** OpenAPI spec reflects actual API
- **No confusion:** Developers won't try to use removed endpoint

### ⚠️ Development Impact
- **Cannot open widget HTML directly** anymore
- Must use MCP tool flow for testing
- Error message clearly explains requirement

**Workaround for Development:**
If you need to test the widget standalone, mock the `structuredContent`:
```javascript
// Add this before including the widget
window.structuredContent = {
    wizard_config: { /* paste from wizard_flow.json */ },
    fields_config: { /* paste from wizard_fields.json */ },
    pre_fill_data: {}
};
```

## Testing Results

### All Tests Pass ✅
```bash
pytest insurance_server_python/tests/
# 100 passed, 8 warnings in 1.37s
```

### OpenAPI Spec Valid ✅
```bash
python -c "from insurance_server_python.main import generate_openapi_spec; ..."
# OpenAPI spec valid: True
# Total endpoints: 4
```

### No Orphaned References ✅
```bash
grep -r "/api/wizard-config" insurance_server_python/ --include="*.py"
# (no results)
```

## Current API Endpoints

After removal, the API has these endpoints:

### Health
- `GET /` - Service information and status
- `GET /health` - Health check for orchestration

### Quotes
- `GET /api/quick-quote-carriers` - Carrier estimates by state

### Assets
- `GET /assets/images/{filename}` - Static image serving

### Documentation (Not in OpenAPI)
- `GET /openapi.json` - OpenAPI 3.0 specification
- `GET /docs` - Swagger UI
- `GET /redoc` - ReDoc UI

**Note:** MCP endpoints are handled by FastMCP and not exposed as REST APIs.

## Code Path Comparison

### Before Removal (2 Code Paths)
```
User Request → MCP Tool → structuredContent → Widget
                            ↓ (if missing)
                      /api/wizard-config → fetch → Widget
```

### After Removal (1 Code Path)
```
User Request → MCP Tool → structuredContent → Widget
                            ↓ (if missing)
                          Error (clear message)
```

## Lines of Code Removed

| File | Lines Removed | Description |
|------|---------------|-------------|
| `main.py` | 31 | OpenAPI spec entry |
| `main.py` | 22 | Endpoint route definition |
| `insurance_wizard_widget_html.py` | 54 | API fallback fetch logic |
| **Total** | **107** | **All dead code** |

## Architecture Rationale

### Why This Makes Sense

1. **MCP-First Design**
   - The widget is designed for MCP integration
   - Direct HTTP access was never a requirement
   - Fallback was speculative "just in case" code

2. **Configuration Coupling**
   - Wizard config is tightly coupled with backend state
   - Pre-fill data comes from backend (ZIP, drivers)
   - Server URL needed for submissions
   - All of this requires MCP context

3. **Simpler = Better**
   - One code path is easier to reason about
   - Fewer edge cases to handle
   - Clear error messages guide developers
   - Less maintenance burden

4. **Security**
   - No public endpoint exposing internal config
   - Configuration only accessible via authenticated MCP tools
   - Reduced attack surface

## Migration Guide (If Needed)

If you need to restore the endpoint in the future:

### Option 1: Restore from Git
```bash
git log --all --oneline | grep -i "wizard-config"
git show <commit-hash>
```

### Option 2: Add New Endpoint
```python
@app.route("/api/wizard-config", methods=["GET"])
async def get_wizard_config(request: Request):
    from .wizard_config_loader import get_wizard_flow, get_wizard_fields

    return JSONResponse({
        "wizard": get_wizard_flow(),
        "fields": get_wizard_fields()
    })
```

### Option 3: Use Existing Functions
```python
from insurance_server_python.wizard_config_loader import (
    get_wizard_flow,
    get_wizard_fields
)

config = {
    "wizard": get_wizard_flow(),
    "fields": get_wizard_fields()
}
```

## Related Changes

This removal follows the pattern established in:
- `MINIMAL_FIELDS_REMOVAL.md` - Removed unused `/api/minimal-fields-config`

Both endpoints were:
- Documented but not actively used
- Had fallback logic that was never triggered
- Maintained "just in case" without real need
- Removed to simplify codebase

## Lessons Learned

1. **Don't build fallbacks speculatively** - YAGNI principle applies
2. **Remove unused code early** - Before it spreads throughout the codebase
3. **Single responsibility** - MCP tools should own their widget configuration
4. **Clear error messages** - Better than silent fallbacks to unexpected behavior
5. **Documentation should match reality** - Remove from OpenAPI when removed from code

## Future Considerations

### If You Need Public Configuration Access

Don't add a fallback to the widget. Instead:

1. **Create explicit public endpoint** if truly needed:
   ```python
   @app.route("/api/public/wizard-schema", methods=["GET"])
   async def get_public_wizard_schema():
       """Public endpoint for wizard schema (read-only)."""
       # Return sanitized version without internal details
   ```

2. **Use separate config** for public vs internal
   - Public: Field schemas, validation rules
   - Internal: Backend URLs, pre-fill logic, MCP context

3. **Require authentication** for sensitive configuration

## Summary

Removed 107 lines of unused fallback code from the wizard configuration system. The wizard now explicitly requires MCP tool integration, with a clear error message if launched incorrectly. All production flows unchanged, all tests passing, and codebase is cleaner and more maintainable.

**Result:** Single, clear code path for wizard initialization via MCP tools. ✅
