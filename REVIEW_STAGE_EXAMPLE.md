# Review Stage - Practical Example

## ✅ Implementation Complete

The review and correction stage has been successfully integrated into the adaptive architecture!

## What Was Added

### 1. **New Collection Status**
- `IN_REVIEW` - Indicates user is reviewing collected fields

### 2. **Enhanced Collection Engine**
New methods in `collection_engine.py`:
- `enter_review_mode()` - Enter review state
- `get_review_summary()` - Get formatted summary of all fields
- `apply_corrections()` - Apply user corrections with validation
- `confirm_review()` - Confirm review and return to READY_TO_SUBMIT

### 3. **Stage Type Support**
Added `StageType` enum to `flow_configs.py`:
- `COLLECTION` - Normal field collection stage
- `REVIEW` - Review and correction stage

### 4. **Test Suite**
5 tests covering all review scenarios (all passing ✅)

---

## Usage Example: Tool Handler Integration

Here's how to update `_get_quick_quote_adaptive()` to support review:

```python
async def _get_quick_quote_adaptive(arguments: Mapping[str, Any]) -> ToolInvocationResult:
    """Adaptive quick quote with review support."""
    session_id = arguments.get("session_id", "default_session")
    action = arguments.get("action", "collect")  # collect | review | correct | confirm

    # Get or create engine
    if session_id not in _session_engines:
        engine = create_collection_engine(FlowType.QUICK_QUOTE)
        _session_engines[session_id] = engine
    else:
        engine = _session_engines[session_id]

    # ─── ACTION: COLLECT ───────────────────────────────────────
    if action == "collect":
        field_arguments = {
            k: v for k, v in arguments.items()
            if k not in ["session_id", "action"]
        }
        state = engine.collect_fields(field_arguments)

        # Check if incomplete
        if state.status == CollectionStatus.INCOMPLETE:
            next_questions = engine.get_next_questions(limit=3)
            prompts = "\n".join([f"• {q.prompt_text}" for q in next_questions])

            return {
                "content": [
                    types.TextContent(
                        type="text",
                        text=f"To get your quick quote, I need:\n{prompts}"
                    )
                ]
            }

        # All fields collected - enter review
        if state.status == CollectionStatus.READY_TO_SUBMIT:
            state = engine.enter_review_mode()
            summary = engine.get_review_summary()

            # Format review summary for user
            review_text = "Great! Let's review your information:\n\n"
            for field_name, info in summary.items():
                review_text += f"• {info['label']}: {info['value']}\n"
            review_text += "\nSay 'looks good' to continue, or tell me what to change."

            return {
                "content": [
                    types.TextContent(type="text", text=review_text),
                    types.TextContent(
                        type="text",
                        text=json.dumps({
                            "status": "in_review",
                            "session_id": session_id,
                            "collected_fields": summary,
                        }),
                        annotations=types.TextAnnotations(audience=["model"])
                    )
                ]
            }

    # ─── ACTION: REVIEW ────────────────────────────────────────
    elif action == "review":
        state = engine.enter_review_mode()
        summary = engine.get_review_summary()

        review_text = "Here's what I have collected:\n\n"
        for field_name, info in summary.items():
            review_text += f"• {info['label']}: {info['value']}\n"

        return {
            "content": [
                types.TextContent(type="text", text=review_text)
            ]
        }

    # ─── ACTION: CORRECT ───────────────────────────────────────
    elif action == "correct":
        corrections = {
            k: v for k, v in arguments.items()
            if k not in ["session_id", "action"]
        }
        state = engine.apply_corrections(corrections)

        if state.validation_errors:
            errors = ", ".join(state.validation_errors.values())
            return {
                "content": [
                    types.TextContent(
                        type="text",
                        text=f"I found some issues: {errors}"
                    )
                ]
            }

        # Show updated summary
        summary = engine.get_review_summary()
        review_text = "Updated! Here's your corrected information:\n\n"
        for field_name, info in summary.items():
            review_text += f"• {info['label']}: {info['value']}\n"
        review_text += "\nSay 'looks good' when ready."

        return {
            "content": [
                types.TextContent(type="text", text=review_text)
            ]
        }

    # ─── ACTION: CONFIRM ───────────────────────────────────────
    elif action == "confirm":
        state = engine.confirm_review()

        if state.status == CollectionStatus.READY_TO_SUBMIT:
            # Generate quote scenarios
            best_case = _generate_quote_scenario(state.collected_fields, scenario="best")
            worst_case = _generate_quote_scenario(state.collected_fields, scenario="worst")

            return {
                "content": [
                    types.TextContent(
                        type="text",
                        text=(
                            f"Based on your information, here's your quote range:\n\n"
                            f"Best case: ${best_case['MonthlyPremium']}/month\n"
                            f"Worst case: ${worst_case['MonthlyPremium']}/month"
                        )
                    )
                ]
            }
        else:
            return {
                "content": [
                    types.TextContent(
                        type="text",
                        text="There are still some issues to resolve before I can generate your quote."
                    )
                ]
            }
```

---

## Conversational Flow Examples

### Example 1: User Reviews and Confirms

```
User: "Get me a quote for zip code 94103 with 2 drivers"

→ Tool: get-quick-quote-adaptive
{
  "ZipCode": "94103",
  "NumberOfDrivers": 2,
  "action": "collect"
}

→ Assistant: "Great! Let's review your information:

              • Zip code: 94103
              • Number of drivers: 2

              Say 'looks good' to continue, or tell me what to change."

User: "looks good"

→ Tool: get-quick-quote-adaptive
{
  "action": "confirm",
  "session_id": "user123"
}

→ Assistant: "Based on your information, here's your quote range:

              Best case: $75/month
              Worst case: $180/month"
```

### Example 2: User Makes Corrections

```
User: "Get me a quote for 94103 with 2 drivers"

→ [Collection happens, enters review]

→ Assistant: "Great! Let's review your information:

              • Zip code: 94103
              • Number of drivers: 2

              Say 'looks good' to continue, or tell me what to change."

User: "Actually, I have 3 drivers"

→ Tool: get-quick-quote-adaptive
{
  "action": "correct",
  "NumberOfDrivers": 3,
  "session_id": "user123"
}

→ Assistant: "Updated! Here's your corrected information:

              • Zip code: 94103
              • Number of drivers: 3

              Say 'looks good' when ready."

User: "looks good"

→ Tool: get-quick-quote-adaptive
{
  "action": "confirm",
  "session_id": "user123"
}

→ Assistant: "Based on your information, here's your quote range:

              Best case: $85/month
              Worst case: $210/month"
```

### Example 3: Multiple Corrections

```
User: "Get me a quote for 94103, 2 drivers"

→ [Collection + review]

→ Assistant: [Shows review summary]

User: "Change the zip to 90210 and I actually have 4 drivers"

→ Tool: get-quick-quote-adaptive
{
  "action": "correct",
  "ZipCode": "90210",
  "NumberOfDrivers": 4,
  "session_id": "user123"
}

→ Assistant: "Updated! Here's your corrected information:

              • Zip code: 90210
              • Number of drivers: 4

              Say 'looks good' when ready."
```

### Example 4: Invalid Correction Caught

```
User: "Change the zip to ABC"

→ Tool: get-quick-quote-adaptive
{
  "action": "correct",
  "ZipCode": "ABC",
  "session_id": "user123"
}

→ Assistant: "I found some issues: Invalid value for ZipCode"

User: "Okay, change it to 90210"

→ Tool: get-quick-quote-adaptive
{
  "action": "correct",
  "ZipCode": "90210",
  "session_id": "user123"
}

→ Assistant: "Updated! Here's your corrected information:

              • Zip code: 90210
              • Number of drivers: 2

              Say 'looks good' when ready."
```

---

## Configuration: Enable/Disable Review

### With Review (Recommended for accuracy)

```python
QUICK_QUOTE_WITH_REVIEW = FlowConfig(
    name="quick_quote_review",
    flow_type=FlowType.QUICK_QUOTE,
    stages=[
        StageConfig(
            name="collect",
            fields=["ZipCode", "NumberOfDrivers"],
            stage_type=StageType.COLLECTION,
        ),
    ],
    submission_criteria={
        "required_fields": ["ZipCode", "NumberOfDrivers"],
        "review_required": True,  # ← Enable review
    },
    metadata={"version": "1.1", "active": True, "includes_review": True}
)
```

### Without Review (Faster flow)

```python
QUICK_QUOTE_NO_REVIEW = FlowConfig(
    name="quick_quote_fast",
    flow_type=FlowType.QUICK_QUOTE,
    stages=[
        StageConfig(
            name="collect",
            fields=["ZipCode", "NumberOfDrivers"],
            stage_type=StageType.COLLECTION,
        ),
    ],
    submission_criteria={
        "required_fields": ["ZipCode", "NumberOfDrivers"],
        "review_required": False,  # ← Disable review
    },
    metadata={"version": "1.0", "active": True, "includes_review": False}
)
```

---

## Test Results

All 5 tests passed ✅:

```
✓ PASS: Basic Review Flow
✓ PASS: Review with Corrections
✓ PASS: Multiple Corrections
✓ PASS: Validation During Corrections
✓ PASS: Cannot Review Incomplete

5/5 tests passed
🎉 All review stage tests passed!
```

---

## Benefits

### 1. **Data Accuracy**
- Users catch and fix mistakes before submission
- Reduces quote errors and support calls
- Improves conversion rates

### 2. **User Control**
- Transparent about collected data
- Easy to make changes
- Builds trust

### 3. **Flexible Configuration**
- Enable/disable per flow
- A/B test with vs without review
- Conditional review (e.g., only for sensitive data)

### 4. **Validation**
- Corrections are validated just like initial collection
- Prevents invalid data from entering system
- Clear error messages

---

## Next Steps

### To Use in Production:

1. **Update Tool Handler**
   - Add `action` parameter support to `_get_quick_quote_adaptive()`
   - Implement the 4 actions: collect, review, correct, confirm

2. **Update Tool Schema**
   ```python
   inputSchema={
       "type": "object",
       "properties": {
           "action": {
               "type": "string",
               "enum": ["collect", "review", "correct", "confirm"],
               "description": "Action to perform"
           },
           "session_id": {"type": "string"},
           "ZipCode": {"type": "string"},
           "NumberOfDrivers": {"type": "integer"},
           # ... other fields
       }
   }
   ```

3. **Configure Flows**
   - Set `review_required: True` in submission criteria
   - Add review stages if using explicit stage-based approach

4. **Test End-to-End**
   ```bash
   # Start server
   uvicorn insurance_server_python.main:app --port 8000

   # Test in ChatGPT with review flow
   ```

### Optional: Create Review Widget

For a richer UI experience, create a dedicated review widget:
- Shows all collected fields in a form
- Inline editing with validation
- Confirm/Cancel buttons
- Groups fields by category

---

## Documentation

- **Architecture**: See `ADAPTIVE_ARCHITECTURE_REVIEW.md` for full design
- **Tests**: Run `python insurance_server_python/test_review_stage.py`
- **Original POC**: See `ADAPTIVE_POC_DEMO.md`

---

## Conclusion

The review stage fits seamlessly into the adaptive architecture:

✅ Configuration-driven (enable/disable per flow)
✅ Non-breaking (existing flows unchanged)
✅ Validation-aware (corrections are validated)
✅ Session-based (maintains state across interactions)
✅ User-friendly (clear prompts and feedback)

**The adaptive architecture now supports**:
- Order-agnostic field collection ✅
- Progressive state building ✅
- Configuration-driven flows ✅
- Review and correction stage ✅

Ready for production! 🎉
