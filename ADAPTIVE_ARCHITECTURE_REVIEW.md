# Review & Correction Stage - Adaptive Architecture Extension

## Overview

This document extends the adaptive architecture to support a **review and correction stage** where users can view all their collected inputs and make changes before final submission.

## Design Principles

1. **Non-disruptive**: Fits into existing adaptive architecture
2. **Optional**: Flows can include or exclude review stage
3. **Full editing**: Users can modify any previously collected field
4. **Validation**: Corrections are validated like initial collection
5. **State preservation**: Review doesn't lose collected data

---

## Architecture Changes

### 1. New Collection Status

Add `IN_REVIEW` status to track review mode:

```python
class CollectionStatus(Enum):
    """Status of collection process."""
    INCOMPLETE = "incomplete"
    STAGE_COMPLETE = "stage_complete"
    READY_TO_SUBMIT = "ready_to_submit"
    IN_REVIEW = "in_review"              # NEW: User reviewing inputs
    SUBMITTED = "submitted"
```

### 2. Enhanced Stage Configuration

Add `stage_type` to distinguish review stages:

```python
from enum import Enum

class StageType(Enum):
    """Type of collection stage."""
    COLLECTION = "collection"  # Normal field collection
    REVIEW = "review"           # Review and correction stage

@dataclass
class StageConfig:
    """Configuration for a single collection stage."""
    name: str
    fields: List[str]
    optional_fields: List[str] = field(default_factory=list)
    description: str = ""
    stage_type: StageType = StageType.COLLECTION  # NEW
    allow_corrections: bool = True                 # NEW: Allow editing in review
```

### 3. Collection Engine Extensions

Add methods to support review mode:

```python
class CollectionEngine:
    """Engine for dynamic, order-agnostic field collection."""

    def enter_review_mode(self) -> CollectionState:
        """Enter review mode - user can see and correct all collected fields.

        Returns:
            Updated collection state with IN_REVIEW status
        """
        if not self.is_ready_to_submit():
            # Can't review incomplete collection
            return self.state

        self.state.status = CollectionStatus.IN_REVIEW
        return self.state

    def get_review_summary(self) -> Dict[str, Any]:
        """Get summary of all collected fields for review.

        Returns:
            Dictionary with field names, values, and metadata for display
        """
        summary = {}
        for field_name, value in self.state.collected_fields.items():
            field_def = get_field(field_name)
            summary[field_name] = {
                "value": value,
                "label": field_def.prompt_text if field_def else field_name,
                "group": field_def.group if field_def else None,
                "editable": True,
            }
        return summary

    def apply_corrections(self, corrections: Dict[str, Any]) -> CollectionState:
        """Apply user corrections during review.

        Args:
            corrections: Dictionary of field_name -> new_value

        Returns:
            Updated collection state with corrections applied
        """
        if self.state.status != CollectionStatus.IN_REVIEW:
            self.state.validation_errors["_review"] = "Not in review mode"
            return self.state

        # Validate and apply corrections
        for field_name, new_value in corrections.items():
            if field_name not in self.state.collected_fields:
                # Skip fields that weren't collected
                continue

            # Validate new value
            is_valid, error = validate_field_value(field_name, new_value)
            if not is_valid:
                self.state.validation_errors[field_name] = error
                continue

            # Apply correction
            self.state.collected_fields[field_name] = new_value
            self.state.validation_errors.pop(field_name, None)

        return self.state

    def confirm_review(self) -> CollectionState:
        """Confirm review is complete and ready to submit.

        Returns:
            Updated collection state with READY_TO_SUBMIT status
        """
        if self.state.status != CollectionStatus.IN_REVIEW:
            return self.state

        # Check if still valid after corrections
        if self._check_submission_criteria() and not self.state.validation_errors:
            self.state.status = CollectionStatus.READY_TO_SUBMIT
        else:
            self.state.status = CollectionStatus.INCOMPLETE

        return self.state
```

---

## Flow Configuration Examples

### Flow WITH Review Stage

```python
QUICK_QUOTE_V1_WITH_REVIEW = FlowConfig(
    name="quick_quote_v1_review",
    flow_type=FlowType.QUICK_QUOTE,
    stages=[
        StageConfig(
            name="initial",
            fields=["ZipCode", "NumberOfDrivers"],
            optional_fields=[],
            description="Minimal info for quote range",
            stage_type=StageType.COLLECTION,
        ),
        StageConfig(
            name="review",
            fields=["ZipCode", "NumberOfDrivers"],  # All collected fields
            optional_fields=[],
            description="Review and confirm your information",
            stage_type=StageType.REVIEW,
            allow_corrections=True,
        ),
    ],
    submission_criteria={
        "required_fields": ["ZipCode", "NumberOfDrivers"],
        "review_required": True,  # NEW: Require review before submit
    },
    metadata={
        "version": "1.1",
        "active": True,
        "includes_review": True,
    }
)
```

### Flow WITHOUT Review (Existing Pattern)

```python
QUICK_QUOTE_V1 = FlowConfig(
    name="quick_quote_v1",
    flow_type=FlowType.QUICK_QUOTE,
    stages=[
        StageConfig(
            name="initial",
            fields=["ZipCode", "NumberOfDrivers"],
            optional_fields=[],
            description="Minimal info for quote range",
            stage_type=StageType.COLLECTION,
        ),
    ],
    submission_criteria={
        "required_fields": ["ZipCode", "NumberOfDrivers"],
        "review_required": False,  # No review needed
    },
    metadata={"version": "1.0", "active": False}
)
```

---

## Tool Handler Integration

Update `_get_quick_quote_adaptive()` to support review:

```python
async def _get_quick_quote_adaptive(arguments: Mapping[str, Any]) -> ToolInvocationResult:
    """Adaptive quick quote with review support."""
    session_id = arguments.get("session_id", "default_session")
    action = arguments.get("action", "collect")  # NEW: collect | review | correct | confirm

    # Get or create engine
    if session_id not in _session_engines:
        engine = create_collection_engine(FlowType.QUICK_QUOTE)
        _session_engines[session_id] = engine
    else:
        engine = _session_engines[session_id]

    # Handle different actions
    if action == "collect":
        # Normal field collection
        field_arguments = {k: v for k, v in arguments.items() if k not in ["session_id", "action"]}
        state = engine.collect_fields(field_arguments)

        if state.status == CollectionStatus.READY_TO_SUBMIT:
            # Check if review is required
            if engine.flow.submission_criteria.get("review_required", False):
                # Enter review mode
                state = engine.enter_review_mode()
                review_summary = engine.get_review_summary()

                return {
                    "content": [
                        types.TextContent(
                            type="text",
                            text="Great! Let's review your information before getting your quote."
                        ),
                        types.TextContent(
                            type="text",
                            text=json.dumps({
                                "status": "in_review",
                                "collected_fields": review_summary,
                                "instructions": "Please review your information. Say 'looks good' to continue, or tell me what to change."
                            }),
                            annotations=types.TextAnnotations(audience=["model"])
                        )
                    ]
                }

        # Continue with normal flow...

    elif action == "review":
        # Show review summary
        state = engine.enter_review_mode()
        review_summary = engine.get_review_summary()

        return {
            "content": [
                types.TextContent(
                    type="text",
                    text="Here's what I have collected:"
                ),
                types.TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "in_review",
                        "collected_fields": review_summary,
                    }),
                    annotations=types.TextAnnotations(audience=["model"])
                )
            ]
        }

    elif action == "correct":
        # Apply corrections
        corrections = {k: v for k, v in arguments.items() if k not in ["session_id", "action"]}
        state = engine.apply_corrections(corrections)

        if state.validation_errors:
            # Show validation errors
            return {
                "content": [
                    types.TextContent(
                        type="text",
                        text=f"I found some issues: {', '.join(state.validation_errors.values())}"
                    )
                ]
            }
        else:
            # Show updated summary
            review_summary = engine.get_review_summary()
            return {
                "content": [
                    types.TextContent(
                        type="text",
                        text="Updated! Here's your corrected information:"
                    ),
                    types.TextContent(
                        type="text",
                        text=json.dumps({"collected_fields": review_summary}),
                        annotations=types.TextAnnotations(audience=["model"])
                    )
                ]
            }

    elif action == "confirm":
        # Confirm review and submit
        state = engine.confirm_review()

        if state.status == CollectionStatus.READY_TO_SUBMIT:
            # Generate quote scenarios...
            best_case = _generate_quote_scenario(state.collected_fields, scenario="best")
            worst_case = _generate_quote_scenario(state.collected_fields, scenario="worst")

            return {
                "content": [
                    types.TextContent(
                        type="text",
                        text=f"Based on your information, here's your quote range:\n\nBest case: ${best_case['MonthlyPremium']}/month\nWorst case: ${worst_case['MonthlyPremium']}/month"
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

## User Experience Examples

### Scenario 1: Flow WITH Review Required

```
User: "Get me a quote for 94103 with 2 drivers"

→ Tool call: get-quick-quote-adaptive
{
  "ZipCode": "94103",
  "NumberOfDrivers": 2
}

→ Response: "Great! Let's review your information before getting your quote:
             • Zip code: 94103
             • Number of drivers: 2

             Say 'looks good' to continue, or tell me what to change."

User: "Actually, I have 3 drivers"

→ Tool call: get-quick-quote-adaptive
{
  "action": "correct",
  "NumberOfDrivers": 3
}

→ Response: "Updated! Here's your corrected information:
             • Zip code: 94103
             • Number of drivers: 3

             Say 'looks good' when ready."

User: "looks good"

→ Tool call: get-quick-quote-adaptive
{
  "action": "confirm"
}

→ Response: "Based on your information, here's your quote range:
             Best case: $85/month
             Worst case: $210/month"
```

### Scenario 2: Flow WITHOUT Review (Original Behavior)

```
User: "Get me a quote for 94103 with 2 drivers"

→ Tool call: get-quick-quote-adaptive
{
  "ZipCode": "94103",
  "NumberOfDrivers": 2
}

→ Response: "Based on your information, here's your quote range:
             Best case: $75/month
             Worst case: $180/month"

(No review step - goes straight to quote)
```

---

## UI Widget Considerations

For a visual review form widget, you could create:

```typescript
// Review widget structure
interface ReviewField {
  name: string;
  label: string;
  value: any;
  type: 'text' | 'number' | 'date' | 'select';
  editable: boolean;
  group?: string;
}

interface ReviewFormProps {
  fields: ReviewField[];
  onCorrect: (corrections: Record<string, any>) => void;
  onConfirm: () => void;
  onCancel: () => void;
}

// Widget would display fields grouped by category
// Allow inline editing
// Show validation errors
// Confirm/cancel buttons
```

---

## Configuration Flexibility

### A/B Testing Review Flows

```python
# Group A: With review (higher accuracy, more friction)
QUICK_QUOTE_A = FlowConfig(
    name="quick_quote_a",
    flow_type=FlowType.QUICK_QUOTE,
    stages=[
        StageConfig(name="collect", fields=["ZipCode", "NumberOfDrivers"]),
        StageConfig(name="review", fields=["ZipCode", "NumberOfDrivers"],
                   stage_type=StageType.REVIEW),
    ],
    submission_criteria={"review_required": True},
    metadata={"ab_test": "review_test", "variant": "A", "active": True}
)

# Group B: No review (lower friction, faster flow)
QUICK_QUOTE_B = FlowConfig(
    name="quick_quote_b",
    flow_type=FlowType.QUICK_QUOTE,
    stages=[
        StageConfig(name="collect", fields=["ZipCode", "NumberOfDrivers"]),
    ],
    submission_criteria={"review_required": False},
    metadata={"ab_test": "review_test", "variant": "B", "active": True}
)
```

### Conditional Review

Review only when collecting sensitive data:

```python
DETAILED_QUOTE_WITH_CONDITIONAL_REVIEW = FlowConfig(
    name="detailed_quote_conditional",
    flow_type=FlowType.DETAILED_QUOTE,
    stages=[
        StageConfig(name="basic", fields=["ZipCode", "NumberOfDrivers"]),
        StageConfig(name="personal", fields=["FirstName", "LastName", "DateOfBirth", "SSN"]),
        StageConfig(
            name="review_sensitive",
            fields=["FirstName", "LastName", "DateOfBirth", "SSN"],
            stage_type=StageType.REVIEW,
            description="Review your personal information"
        ),
    ],
    submission_criteria={
        "review_required": True,
        "review_fields": ["SSN", "DateOfBirth"],  # Only review these fields
    },
    metadata={"review_policy": "sensitive_only"}
)
```

---

## Benefits

### 1. Data Accuracy
- Users catch and correct mistakes
- Reduces downstream errors
- Improves quote accuracy

### 2. User Confidence
- Users see exactly what's being submitted
- Transparency builds trust
- Reduces support inquiries

### 3. Compliance
- Audit trail of user confirmations
- Explicit consent for data collection
- TCPA/compliance friendly

### 4. Flexibility
- Enable/disable via configuration
- A/B test with vs without review
- Customize per flow or state

---

## Implementation Checklist

- [ ] Update `CollectionStatus` enum with `IN_REVIEW`
- [ ] Add `StageType` enum
- [ ] Update `StageConfig` with `stage_type` and `allow_corrections`
- [ ] Add review methods to `CollectionEngine`:
  - [ ] `enter_review_mode()`
  - [ ] `get_review_summary()`
  - [ ] `apply_corrections()`
  - [ ] `confirm_review()`
- [ ] Update flow configurations with review stages
- [ ] Update `_get_quick_quote_adaptive()` with action parameter
- [ ] Create tests for review flow
- [ ] Optional: Create review widget UI component
- [ ] Update documentation

---

## Testing Strategy

```python
def test_review_flow():
    """Test collection with review stage."""
    # Create engine with review flow
    engine = create_collection_engine(FlowType.QUICK_QUOTE, flow_name="quick_quote_v1_review")

    # Collect fields
    state = engine.collect_fields({"ZipCode": "94103", "NumberOfDrivers": 2})
    assert state.status == CollectionStatus.READY_TO_SUBMIT

    # Enter review
    state = engine.enter_review_mode()
    assert state.status == CollectionStatus.IN_REVIEW

    # Get review summary
    summary = engine.get_review_summary()
    assert "ZipCode" in summary
    assert summary["ZipCode"]["value"] == "94103"

    # Apply correction
    state = engine.apply_corrections({"NumberOfDrivers": 3})
    assert state.collected_fields["NumberOfDrivers"] == 3
    assert state.status == CollectionStatus.IN_REVIEW

    # Confirm review
    state = engine.confirm_review()
    assert state.status == CollectionStatus.READY_TO_SUBMIT
```

---

## Conclusion

The review stage fits naturally into the adaptive architecture:

- ✅ Configuration-driven (enable/disable per flow)
- ✅ Non-breaking (existing flows work unchanged)
- ✅ Order-agnostic (corrections work like initial collection)
- ✅ Flexible (optional, conditional, A/B testable)
- ✅ User-friendly (clear UX pattern)

**Next Steps**: Implement changes in collection engine and test with POC.
