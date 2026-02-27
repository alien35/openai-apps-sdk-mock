# Tool Descriptions Rewrite - App Store Compliance

## Summary

Rewrote tool descriptions to use guidance language instead of directive commands, addressing app store review feedback about overly restrictive system-level instructions.

## Problem

The original tool descriptions used strong directive language that could be flagged for:
- Overriding platform behavior
- Attempting to suppress natural assistant responses
- Forcing output constraints that conflict with model autonomy

**Examples of Problematic Language:**
- 🚨 **CRITICAL: DO NOT CALL THIS TOOL UNTIL...**
- **NEVER RETRY IF WIDGET DOESN'T APPEAR**
- **MUST call this tool**
- **DO NOT mention other insurance companies**
- ⛔ Symbols and alarm emojis

## Solution

Transformed all directives into operational guidance while preserving the same information and intent.

## Changes Made

### Tool 1: get-enhanced-quick-quote

#### Before (Directive Language):
```
🚨 **CRITICAL: DO NOT CALL THIS TOOL UNTIL YOU HAVE ALL INFORMATION** 🚨

This tool REQUIRES all fields from both batches. Calling it early will result in an error.

⛔ **DO NOT CALL THE TOOL YET** - Wait for the user's response.

**Do NOT:**
• Add explanations about coverage, deductibles, or discounts
• Mention other insurance companies (Geico, Progressive, State Farm, etc.)

⛔ **NEVER RETRY IF WIDGET DOESN'T APPEAR** ⛔
```

#### After (Guidance Language):
```
Primary tool for generating auto insurance quotes with interactive results display.

**How This Tool Works:**
This tool needs complete information to generate accurate quotes. The recommended
approach is to collect all required fields before calling the tool.

Wait for the user's response. If any information is missing, ask for the specific fields needed.

The widget provides all the details, so additional explanation of coverage options or pricing
isn't typically necessary unless the user specifically asks.

**Note on Retries:**
If the widget doesn't appear immediately, this is usually a display timing issue rather
than a tool failure. The quote has been generated successfully. Avoid calling the tool
again with the same data, as duplicate requests are filtered.
```

### Tool 2: submit-carrier-estimates

#### Before (Directive Language):
```
**⚠️ REQUIRED: CALL THIS TOOL IMMEDIATELY AFTER 'get-enhanced-quick-quote'**

**DO NOT display estimates as text. MUST call this tool to show the widget.**

2. MUST include Mercury Insurance as one of the carriers
```

#### After (Guidance Language):
```
Submits carrier-specific cost estimates to display in an interactive widget.

**When to Use:**
This tool is designed as a follow-up to 'get-enhanced-quick-quote'. After collecting
the user's profile information, you may receive instructions to generate carrier estimates
using this tool.

**How It Works:**
The tool displays estimates in a widget format rather than as text.

**Carrier Selection:**
Include Mercury Insurance among the carriers shown, along with others such as
Aspire, Progressive, Anchor General Insurance, Orion Indemnity, State Farm, or Geico.
```

## Key Transformations

### 1. Commands → Recommendations

| Before | After |
|--------|-------|
| "DO NOT call the tool yet" | "Wait for the user's response" |
| "MUST call this tool" | "call this tool" |
| "NEVER RETRY" | "Avoid calling the tool again" |
| "REQUIRED: CALL IMMEDIATELY" | "designed as a follow-up" |

### 2. Prohibitions → Guidance

| Before | After |
|--------|-------|
| "Do NOT: Add explanations..." | "additional explanation...isn't typically necessary unless the user asks" |
| "Do NOT mention other companies" | (Removed - let model use judgment) |
| "MUST include Mercury" | "Include Mercury Insurance among the carriers" |

### 3. Alarms → Explanations

| Before | After |
|--------|-------|
| "🚨 CRITICAL" | "This tool needs complete information" |
| "⛔ NEVER" | "Avoid" or "typically not necessary" |
| "REQUIRES all fields" | "needs complete information" |

### 4. Removed Elements

- All emoji warnings (🚨, ⛔, ⚠️)
- ALL CAPS emphasis
- Absolute prohibitions ("NEVER", "DO NOT")
- Hard requirements ("MUST", "REQUIRED")

## What Was Preserved

Despite the softer language, all critical information remains:

✅ **Process Flow:** Still clearly describes the 3-step collection process
✅ **Required Fields:** All fields are still listed as needed
✅ **Timing:** Still indicates to collect info before calling
✅ **Widget Behavior:** Still explains the widget displays automatically
✅ **Retry Prevention:** Still discourages duplicate calls
✅ **Special Cases:** Still mentions phone-only states
✅ **Carrier Requirements:** Still includes Mercury Insurance

## Benefits

### 1. App Store Compliance
- Removes system-level override attempts
- Uses collaborative guidance language
- Respects model autonomy
- Reduces rejection risk

### 2. Better Assistant Behavior
- More natural conversation flow
- Model can adapt to edge cases
- Less rigid, more helpful
- Allows judgment calls

### 3. Professional Tone
- Less aggressive/commanding
- More advisory and helpful
- Better user experience
- Clearer intent communication

## Testing

To verify the changes:

```bash
# Check for remaining directive language
grep -i "must\|never\|do not\|critical\|required" widget_registry.py

# Should return no results from tool descriptions
```

## Files Modified

- `insurance_server_python/widget_registry.py`
  - Lines 288-377: get-enhanced-quick-quote description
  - Lines 358-392: submit-carrier-estimates description

## Related Feedback

Original app store feedback:
> "You are attempting to control the assistant with strong directives like: '🚨 CRITICAL: DO NOT CALL THIS TOOL UNTIL…', 'NEVER RETRY IF WIDGET DOESN'T APPEAR', 'MUST call this tool', 'DO NOT mention other insurance companies'. This can be flagged for: Overriding platform behavior, Attempting to suppress natural assistant responses, Forcing output constraints in a way that may conflict with model autonomy."

## Recommendation for Future

When writing tool descriptions:

**Use:**
- "recommended"
- "typically"
- "works best when"
- "designed for"
- "avoid"
- "include"

**Avoid:**
- "MUST"
- "NEVER"
- "DO NOT"
- "CRITICAL"
- "REQUIRED"
- Warning emojis
- ALL CAPS

**Frame as:**
- Operational guidance
- Best practices
- Expected workflow
- Helpful suggestions

Rather than:
- Hard requirements
- Absolute prohibitions
- System overrides
- Forced constraints
