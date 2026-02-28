# Batched Quick Quote - Implementation Summary

## Overview

Implemented a batched information collection system for the enhanced quick quote. Questions are organized into two logical batches for better user experience.

## Batch Structure

### BATCH 1: Vehicle Information
Ask all these questions together:
1. **Vehicle 1**: Year, Make, Model
2. **Vehicle 2** (optional): Year, Make, Model
3. **Coverage Type**: Liability or Full Coverage

### BATCH 2: Driver Information
Ask all these questions together:
1. **Primary Driver Age**
2. **Primary Driver Marital Status** (single/married/divorced/widowed)
3. **Additional Driver** (optional): Age and Marital Status
4. **Zip Code**

## What Changed

### 1. Added Primary Driver Marital Status Field (insurance_server_python/config/fields.json)
```json
{
  "PrimaryDriverMaritalStatus": {
    "name": "PrimaryDriverMaritalStatus",
    "field_type": "string",
    "required": true,
    "enum_values": ["single", "married", "divorced", "widowed"],
    "prompt_text": "What's the primary driver's marital status?"
  }
}
```

### 2. Updated Flow to Two Stages (insurance_server_python/config/flows.json)
The `enhanced_quick_quote_v1` flow now has 2 stages:
- **Stage 1 (vehicles_batch)**: Collects Vehicle1, Vehicle2 (opt), CoverageType
- **Stage 2 (drivers_batch)**: Collects PrimaryDriverAge, PrimaryDriverMaritalStatus, AdditionalDriver (opt), ZipCode

### 3. Updated Model (insurance_server_python/models.py:577-617)
Reorganized `EnhancedQuickQuoteIntake` model:
- Fields ordered to match batch structure
- Added `primary_driver_marital_status` field
- Updated docstring to explain batch collection

### 4. Enhanced Rate Calculation (insurance_server_python/quick_quote_ranges.py:147-246)
Added marital status factors:
- **Married**: 10% discount (0.9x multiplier)
- **Divorced/Widowed**: 5% discount (0.95x multiplier)
- **Single**: No discount (1.0x multiplier)
- **Married couple**: Additional 5% discount when both married

### 5. Updated Tool Description (insurance_server_python/widget_registry.py:314-346)
Tool description now clearly explains:
- Two-batch collection approach
- Which questions belong in each batch
- Optional vs required fields
- Emphasis on asking batch questions together

### 6. Updated Tool Handler (insurance_server_python/tool_handlers.py:465-560)
Handler now:
- Accepts primary driver marital status
- Passes marital status to rate calculation
- Formats output to show batches clearly:
  - **VEHICLES:** section
  - **DRIVERS:** section
- Includes marital status in structured content

## Configuration Summary

**Total Fields**: 17 (added 1 for marital status)

**Flow Structure**:
- Name: `enhanced_quick_quote_v1`
- Active: `true`
- Stages: 2
  - Stage 1 (vehicles_batch): 4 required, 3 optional
  - Stage 2 (drivers_batch): 3 required, 2 optional

## Test Results

All tests passing with realistic rate variations:

### Test 1: Married driver (35), single vehicle, full coverage
- Location: Beverly Hills, CA
- Best: $993 - $1,676 per 6 months
- Worst: $4,098 - $7,265 per 6 months

### Test 2: Single young driver (22), newer vehicle, full coverage
- Location: San Francisco, CA
- Best: $2,106 - $3,685 per 6 months
- Worst: $8,365 - $15,210 per 6 months
- **Notice**: Single young driver pays significantly more

### Test 3: Married couple (40 & 38), two vehicles, liability only
- Location: San Diego, CA
- Best: $653 - $1,078 per 6 months
- Worst: $2,636 - $4,814 per 6 months
- **Notice**: Married couple with liability-only gets great rates

### Test 4: Divorced driver (50), older vehicle, liability only
- Location: Sacramento, CA
- Best: $372 - $598 per 6 months
- Worst: $1,462 - $2,593 per 6 months
- **Notice**: Older driver with liability-only gets lowest rates

## How ChatGPT Will Behave

When a user says "I need to buy insurance", ChatGPT will:

**BATCH 1 - Ask all vehicle questions:**
> Let me get some information about your vehicle(s).
>
> 1. What year, make, and model is your primary vehicle?
> 2. Do you have a second vehicle? If so, what year, make, and model?
> 3. What type of coverage do you need - liability only or full coverage?

**BATCH 2 - Ask all driver questions:**
> Great! Now I need some information about the driver(s).
>
> 1. How old is the primary driver?
> 2. What's the primary driver's marital status?
> 3. Do you have an additional driver? If so, what's their age and marital status?
> 4. What's your zip code?

Then displays the personalized quote with:
- **VEHICLES** section showing all vehicle info
- **DRIVERS** section showing all driver info
- Best and worst case rate ranges

## Benefits of Batched Approach

1. **Better UX**: Logically grouped questions are easier to answer
2. **Clearer Context**: Users understand what category of info they're providing
3. **Efficient**: All related questions asked at once
4. **Accurate Rates**: Marital status significantly impacts pricing
5. **Config-Driven**: Easy to modify batch structure without code changes

## Running Tests

```bash
# Test batched quick quote
python test_batched_quick_quote.py

# Validate configs
python -c "import json; print(json.load(open('insurance_server_python/config/flows.json'))['flows'][4])"
```

## Next Steps

To use in production:

1. **Restart MCP Server**: `uvicorn insurance_server_python.main:app --port 8000`
2. **Connect ChatGPT** to your MCP endpoint
3. **Test**: Say "I need to buy insurance"
4. **Observe**: ChatGPT should ask questions in two clear batches

To customize:

- **Add fields**: Edit `insurance_server_python/config/fields.json`
- **Change batch structure**: Edit `insurance_server_python/config/flows.json`
- **Adjust rate factors**: Edit `insurance_server_python/quick_quote_ranges.py`
- **Modify batch descriptions**: Edit `insurance_server_python/widget_registry.py` tool description
