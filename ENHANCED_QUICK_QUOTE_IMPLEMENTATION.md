# Enhanced Quick Quote - Config-Driven Implementation

## Overview

Implemented a comprehensive config-driven enhanced quick quote system that collects detailed information upfront for more accurate insurance rate estimates.

## What Changed

### 1. Config-Driven Fields (insurance_server_python/config/fields.json)

Added 10 new fields to the centralized field registry:

**Required Fields:**
- `PrimaryDriverAge` - Age of primary driver (16-100)
- `Vehicle1Year` - Year of primary vehicle (1900-2030)
- `Vehicle1Make` - Make of primary vehicle
- `Vehicle1Model` - Model of primary vehicle
- `CoverageType` - "liability" or "full_coverage"

**Optional Fields:**
- `Vehicle2Year` - Year of second vehicle
- `Vehicle2Make` - Make of second vehicle
- `Vehicle2Model` - Model of second vehicle
- `AdditionalDriverAge` - Age of additional driver
- `AdditionalDriverMaritalStatus` - Marital status (single/married/divorced/widowed)

### 2. Config-Driven Flow (insurance_server_python/config/flows.json)

Added `enhanced_quick_quote_v1` flow:
- Flow type: `enhanced_quick_quote`
- Status: **Active** (set as default)
- Single collection stage with all required/optional fields
- Generates enhanced scenarios with detailed rate calculations

### 3. Enhanced Models (insurance_server_python/models.py)

Created three new Pydantic models:
- `VehicleInfo` - Nested model for vehicle details (year, make, model)
- `AdditionalDriverInfo` - Nested model for additional driver (age, marital status)
- `EnhancedQuickQuoteIntake` - Main model for enhanced quick quote tool

### 4. Enhanced Rate Calculation (insurance_server_python/quick_quote_ranges.py)

Added `calculate_enhanced_quote_range()` function with multiple factors:
- **Age Factor**: Young drivers (<25) get 1.5-1.8x, seniors (60+) get 1.1x
- **Vehicle Age Factor**: Newer cars (<3 years) cost 30% more for full coverage
- **Coverage Factor**: Full coverage costs 1.5x vs liability only
- **Additional Driver Factor**: Young additional drivers add 1.4-1.6x
- **Multiple Vehicle Factor**: 2nd vehicle adds 1.4x multiplier

### 5. Enhanced Tool Handler (insurance_server_python/tool_handlers.py)

Added `_get_enhanced_quick_quote()` handler that:
- Validates input against `EnhancedQuickQuoteIntake` model
- Looks up city/state from zip code
- Calculates enhanced rate ranges using detailed factors
- Returns structured content with all collected information
- Displays results in the quick quote widget

### 6. Updated Tool Registration (insurance_server_python/widget_registry.py)

**Enhanced Quick Quote (PRIMARY):**
- Title: "Get auto insurance quote with detailed information [PRIMARY]"
- Marked as **PRIMARY TOOL FOR INSURANCE QUOTES**
- Description emphasizes this should be used by default
- Clear explanation of required and optional fields

**Basic Quick Quote (FALLBACK):**
- Title: "Get basic auto insurance range (fallback)"
- Marked as **FALLBACK TOOL**
- Description warns to use enhanced version instead
- Only for users who refuse to provide details

## How It Works

### For ChatGPT

When a user asks "I need to buy insurance":

1. ChatGPT sees `get-enhanced-quick-quote` marked as **[PRIMARY]**
2. ChatGPT asks for the required information:
   - Zip code
   - Primary driver age
   - Vehicle year, make, model
   - Coverage type (liability or full coverage)
3. ChatGPT optionally asks for:
   - Second vehicle details
   - Additional driver information
4. ChatGPT calls the tool with collected data
5. User sees accurate rate ranges based on their specific situation

### For Developers

To modify the quote flow:

1. **Add new fields** → Edit `insurance_server_python/config/fields.json`
2. **Change what's collected** → Edit `insurance_server_python/config/flows.json`
3. **Adjust rate calculations** → Edit `insurance_server_python/quick_quote_ranges.py`
4. **No code changes needed** for field collection order or requirements!

## Testing

Run the test suite:

```bash
# Test enhanced quote functionality
python test_enhanced_quick_quote.py

# Test config integration
python test_config_integration.py
```

Example test results show realistic rate variations:
- Young driver (22), new car, full coverage: $1,872-$3,159 (best) to $7,722-$13,689 (worst)
- Experienced driver (45), old car, liability: $504-$881 (best) to $2,002-$3,640 (worst)
- Two drivers, two vehicles, full coverage: $1,883-$3,108 (best) to $7,597-$13,876 (worst)

## Widget Integration

The enhanced quick quote uses the same `quick_quote_results_widget` which:
- Displays best-case and worst-case scenarios
- Shows monthly and 6-month premium ranges
- Includes "Continue to Personalized Quote" button
- Links to aisinsurance.com with zip code pre-filled

## Configuration Files

```
insurance_server_python/config/
├── fields.json         # 16 field definitions (10 new)
└── flows.json          # 5 flows (1 new enhanced flow)
```

## Benefits

1. **More Accurate Quotes** - Rates reflect actual driver/vehicle details
2. **Config-Driven** - Change fields without touching code
3. **Flexible** - Easy to add/remove fields or adjust flows
4. **User-Friendly** - ChatGPT naturally asks for relevant details
5. **Prioritized** - Enhanced version is clearly marked as primary tool

## Next Steps

To activate in production:

1. Restart the MCP server to load new configs
2. Connect ChatGPT to your MCP server endpoint
3. Test with: "I need auto insurance"
4. ChatGPT should now ask for detailed information by default

To customize:

- Adjust rate calculation factors in `quick_quote_ranges.py`
- Add more optional fields in `fields.json`
- Create flow variations in `flows.json` (e.g., with/without vehicle 2)
- A/B test different field combinations by toggling `active` flag
