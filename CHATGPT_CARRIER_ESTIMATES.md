# ChatGPT-Generated Carrier Estimates - Implementation Summary

## Overview

Implemented a multi-step tool flow where ChatGPT generates insurance carrier cost estimates based on user profiles, rather than using hard-coded calculations or external APIs.

## Architecture

### Two-Step Flow

**Step 1: Profile Collection (`get-enhanced-quick-quote`)**
- Collects user's insurance profile (vehicle, driver, coverage details)
- Calculates baseline rate ranges
- Returns profile summary to user
- Returns model-only instructions to ChatGPT with:
  - User profile data
  - Estimated rate ranges
  - Instructions to generate carrier estimates
  - Requirement to include Mercury Insurance

**Step 2: Carrier Estimates (`submit-carrier-estimates`)**
- ChatGPT generates 3-5 carrier estimates based on profile
- ChatGPT calls this tool with generated estimates
- Tool validates estimates (ensures Mercury Insurance included)
- Tool adds logos to each carrier
- Returns final widget with carrier quotes

## Implementation Details

### New Models (`insurance_server_python/models.py`)

```python
class CarrierEstimate(BaseModel):
    """Individual carrier cost estimate."""
    name: str = Field(..., alias="Carrier Name")
    annual_cost: int = Field(..., alias="Annual Cost", ge=0)
    monthly_cost: int = Field(..., alias="Monthly Cost", ge=0)
    notes: str = Field(..., alias="Notes")

class CarrierEstimatesSubmission(BaseModel):
    """ChatGPT-generated estimates with profile reference."""
    zip_code: str = Field(..., alias="Zip Code")
    primary_driver_age: int = Field(..., alias="Age")
    carriers: List[CarrierEstimate] = Field(
        ..., alias="Carriers", min_length=3, max_length=10
    )

    @model_validator(mode="after")
    def validate_mercury_included(self):
        """Ensure Mercury Insurance is included."""
        carrier_names = [c.name.lower() for c in self.carriers]
        if not any("mercury" in name for name in carrier_names):
            raise ValueError("Carriers list must include Mercury Insurance")
        return self
```

### New Tool Handler (`insurance_server_python/tool_handlers.py`)

```python
async def _submit_carrier_estimates(arguments: Mapping[str, Any]) -> ToolInvocationResult:
    """Accept ChatGPT-generated carrier estimates and render the final quote widget."""
    # Validates submission
    # Adds carrier logos
    # Returns structured_content with widget metadata
```

### Modified Tool Handler

**`_get_enhanced_quick_quote` changes:**
- Removed hard-coded carrier generation
- Added model-only instructions for ChatGPT
- Returns profile data with instructions to generate estimates
- Stage changed to "awaiting_carrier_estimates"

### Tool Registration (`insurance_server_python/widget_registry.py`)

Registered new tool `submit-carrier-estimates` with:
- Clear description of its role in the flow
- Instructions for ChatGPT on how to generate estimates
- Example carrier estimates
- Schema validation via `CarrierEstimatesSubmission`

## User Experience Flow

1. **User**: "I need auto insurance"
2. **ChatGPT**: Asks vehicle questions (STEP 1)
3. **User**: Provides vehicle details
4. **ChatGPT**: Asks driver questions (STEP 2)
5. **User**: Provides driver details
6. **ChatGPT**: Calls `get-enhanced-quick-quote`
7. **Tool**: Returns profile + hidden instructions for ChatGPT
8. **ChatGPT**: Generates carrier estimates using knowledge
9. **ChatGPT**: Calls `submit-carrier-estimates` with generated data
10. **Tool**: Returns widget with carrier quotes + logos
11. **User**: Sees carrier table widget with quotes

## Model-Only Instructions Format

```
INTERNAL INSTRUCTIONS (not shown to user):

You have collected the user's insurance profile. Now generate carrier cost estimates based on this profile:
- Location: Beverly Hills, California 90210
- Driver: Age 25, married
- Vehicle: 2022 Honda Civic
- Coverage: full_coverage
- Estimated range: $1192-$2012 per 6 months ($198-$335 per month)

Generate 3-5 carrier estimates including:
1. Mercury Insurance (REQUIRED - must be included)
2. 2-4 other carriers (e.g., Aspire, Progressive, Anchor General, etc.)

For each carrier, estimate:
- Annual cost (reasonable variation around $X annually)
- Monthly cost (annual / 12)
- Brief notes about their value proposition

Then immediately call the 'submit-carrier-estimates' tool with your generated estimates.
```

## Testing

**Test file:** `test_chatgpt_carrier_flow.py`

Simulates the complete two-step flow:
1. Profile collection → Returns instructions
2. Carrier submission → Returns widget

**Run test:**
```bash
python test_chatgpt_carrier_flow.py
```

## Validation

- Mercury Insurance MUST be included (enforced by Pydantic validator)
- 3-10 carriers required
- Annual/monthly costs must be positive integers
- All carriers get logos automatically added
- Human-friendly field aliases (e.g., "Carrier Name" not "carrier_name")

## Benefits

✅ **No external API needed** - Uses ChatGPT's existing knowledge
✅ **Flexible estimates** - ChatGPT can adjust based on profile
✅ **Natural language** - ChatGPT explains estimates contextually
✅ **Low latency** - No waiting for external API calls
✅ **Cost-effective** - No per-request API fees

## Limitations

⚠️ **Not real-time data** - Based on ChatGPT's training data (pre-2025)
⚠️ **Estimate quality** - Depends on ChatGPT's insurance knowledge
⚠️ **Consistency** - Estimates may vary slightly between runs
⚠️ **Accuracy** - Less accurate than real insurance rating APIs

## Production Recommendations

For production use with real customers:
- Consider using a real insurance rating API for accurate quotes
- Use this approach for demos, MVPs, or rough estimates
- Clearly label estimates as "approximate" or "for illustration"

## Files Changed

1. **insurance_server_python/models.py**
   - Added `CarrierEstimate` model
   - Added `CarrierEstimatesSubmission` model with Mercury validation

2. **insurance_server_python/tool_handlers.py**
   - Modified `_get_enhanced_quick_quote` to return instructions
   - Added `_submit_carrier_estimates` handler

3. **insurance_server_python/widget_registry.py**
   - Added imports for new models/handler
   - Registered `submit-carrier-estimates` tool

4. **test_chatgpt_carrier_flow.py** (new)
   - End-to-end test of two-step flow

## Example Output

```
STEP 1: Profile collected
User sees: "Next Step: I need to generate carrier cost estimates..."

STEP 2: Estimates submitted
User sees widget with:
- Mercury Insurance: $3,200/year ($267/month)
- Aspire: $3,360/year ($280/month)
- Progressive: $4,064/year ($339/month)
- Anchor General: $4,192/year ($349/month)
```

## Next Steps

To use in ChatGPT:
1. Restart MCP server: `uvicorn insurance_server_python.main:app --port 8000`
2. Expose via ngrok: `ngrok http 8000`
3. Add to ChatGPT connectors
4. Test: "I need auto insurance" → Follow prompts → See carrier quotes
