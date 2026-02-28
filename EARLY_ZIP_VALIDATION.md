# Early ZIP Code Validation

## Overview

The insurance quote flow now supports **early ZIP code validation** to provide a better user experience. When a user provides only their ZIP code, the system immediately checks if it's in a phone-only state (AK, HI, MA) or if the lookup fails. If so, it shows the phone widget immediately without asking for additional information.

## How It Works

### 1. User Provides Only ZIP Code

When the user provides just their ZIP code (and no other fields), the `get-enhanced-quick-quote` tool:

1. **Validates the ZIP code** by looking up the city and state
2. **Checks if it's a phone-only state** (Alaska, Hawaii, Massachusetts)
3. **Returns the phone widget immediately** if:
   - The state is AK, HI, or MA
   - The ZIP code lookup fails
4. **Asks for more information** if it's a normal state where we can provide quotes

### 2. Flow Examples

#### Example 1: Phone-Only State (Alaska)

```
User: "My zip code is 99501"
Assistant: [Calls get-enhanced-quick-quote with just ZIP Code: "99501"]
System: Returns phone widget immediately
Assistant: "I'd be happy to help you get a quote in Anchorage, Alaska.
           Since we require a call for quotes in Alaska, please contact us..."
[Shows phone-only widget with phone number]
```

#### Example 2: Normal State (California)

```
User: "My zip code is 92821"
Assistant: [Calls get-enhanced-quick-quote with just ZIP Code: "92821"]
System: Returns message asking for more info
Assistant: "Thanks! To provide your insurance quote, I'll need:
           • Number of vehicles
           • Year, make, and model for each vehicle
           • Coverage preference (full coverage or liability only)
           • Number of drivers..."
```

## Technical Implementation

### Modified Files

1. **`models.py`** - Updated `QuickQuoteIntake` model:
   - Made all fields optional except `zip_code`
   - Allows the tool to be called with just a ZIP code
   - Updated validator to handle optional fields

2. **`tool_handlers.py`** - Updated `_get_enhanced_quick_quote` handler:
   - Added early validation check (`has_only_zip`)
   - Added phone-only state detection
   - Returns phone widget immediately for phone-only states
   - Returns error message asking for more info for normal states
   - Validates all required fields are present before generating quotes

3. **`widget_registry.py`** - Updated tool description:
   - Added instructions for early ZIP code validation
   - Explains when to call the tool with just ZIP code
   - Instructs assistant to skip follow-up questions if phone-only state detected

### Phone-Only States

The following states require a phone call instead of online quotes:

- **AK** - Alaska
- **HI** - Hawaii
- **MA** - Massachusetts

### Widget Display

When a phone-only state is detected, the widget displays:

- **Header**: Phone background image (instead of car)
- **Branding**: Mercury Insurance logo with "Powered by AIS"
- **Message**: "We're here to help" with explanation
- **Phone number**: (888) 772-4247
- **Hours**: Business hours displayed
- **CTA button**: "Call for a quote" (links to tel: URI)

## Benefits

1. **Faster user experience**: Users in phone-only states don't need to answer multiple questions
2. **Reduces friction**: Saves time by not collecting unnecessary information
3. **Clear communication**: Immediately shows the phone option when online quotes aren't available
4. **Better UX**: No wasted effort filling out forms that can't be completed online

## Testing

Run the test script to verify early validation:

```bash
python test_early_validation.py
```

This tests:
- California (normal state - should ask for more info)
- Alaska (phone-only - should show phone widget)
- Hawaii (phone-only - should show phone widget)
- Massachusetts (phone-only - should show phone widget)

## Assistant Instructions

The assistant (ChatGPT) is instructed to:

1. **If user provides only ZIP code**: Call `get-enhanced-quick-quote` with just the ZIP code
2. **If phone-only widget returned**: Don't ask follow-up questions, just show the widget
3. **If more info needed**: Ask for remaining Batch 1 fields (vehicles, coverage)
4. **If Batch 1 complete**: Proceed to Batch 2 (driver information)

This creates a smooth, adaptive flow that responds to the user's location.
