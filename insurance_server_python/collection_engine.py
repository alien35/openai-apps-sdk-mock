"""Collection Engine: Orchestrates field collection based on configuration.

This engine enables order-agnostic field collection, validates against the
field registry, tracks state progressively, and supports flexible flows.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

from .field_registry import (
    FieldDefinition,
    FieldContext,
    get_field,
    validate_field_value,
)
from .flow_configs import (
    FlowConfig,
    StageConfig,
    get_active_flow,
    FlowType,
)


class CollectionStatus(Enum):
    """Status of collection process."""
    INCOMPLETE = "incomplete"
    STAGE_COMPLETE = "stage_complete"
    READY_TO_SUBMIT = "ready_to_submit"
    IN_REVIEW = "in_review"
    SUBMITTED = "submitted"


@dataclass
class CollectionState:
    """Tracks collection progress."""
    flow_name: str
    collected_fields: Dict[str, Any] = field(default_factory=dict)
    current_stage: int = 0
    status: CollectionStatus = CollectionStatus.INCOMPLETE
    missing_fields: List[str] = field(default_factory=list)
    validation_errors: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class CollectionEngine:
    """Engine for dynamic, order-agnostic field collection."""

    def __init__(self, flow_config: FlowConfig):
        """Initialize collection engine with a flow configuration.

        Args:
            flow_config: Flow configuration to use
        """
        self.flow = flow_config
        self.state = CollectionState(flow_name=flow_config.name)

    def collect_fields(self, fields: Dict[str, Any]) -> CollectionState:
        """Collect a batch of fields in any order.

        This method is order-agnostic: fields can be provided in any sequence.
        It validates each field, checks dependencies, and updates state.

        Args:
            fields: Dictionary of field_name -> value

        Returns:
            Updated collection state
        """
        # Validate and collect each field
        for field_name, value in fields.items():
            # Get field definition
            field_def = get_field(field_name)
            if not field_def:
                self.state.validation_errors[field_name] = f"Unknown field: {field_name}"
                continue

            # Validate value
            is_valid, error = validate_field_value(field_name, value)
            if not is_valid:
                self.state.validation_errors[field_name] = error
                continue

            # Check dependencies
            missing_deps = self._check_dependencies(field_def)
            if missing_deps:
                self.state.validation_errors[field_name] = (
                    f"Missing dependencies: {', '.join(missing_deps)}"
                )
                continue

            # Store field
            self.state.collected_fields[field_name] = value

            # Clear any previous errors for this field
            self.state.validation_errors.pop(field_name, None)

        # Update state
        self._update_status()

        return self.state

    def _check_dependencies(self, field_def: FieldDefinition) -> List[str]:
        """Check if field dependencies are met.

        Args:
            field_def: Field definition to check

        Returns:
            List of missing dependency field names
        """
        missing = []
        for dep in field_def.depends_on:
            if dep not in self.state.collected_fields:
                missing.append(dep)
        return missing

    def _update_status(self):
        """Update collection status based on collected fields."""
        # Get current stage configuration
        if self.state.current_stage >= len(self.flow.stages):
            # All stages complete
            self.state.status = CollectionStatus.READY_TO_SUBMIT
            self.state.missing_fields = []
            return

        current_stage_config = self.flow.stages[self.state.current_stage]

        # Get required fields for current stage
        required = [
            f for f in current_stage_config.fields
            if f not in current_stage_config.optional_fields
        ]

        # Check what's missing
        stage_missing = [f for f in required if f not in self.state.collected_fields]
        self.state.missing_fields = stage_missing

        if not stage_missing:
            # Current stage complete
            if self.state.current_stage < len(self.flow.stages) - 1:
                # More stages remain
                self.state.status = CollectionStatus.STAGE_COMPLETE
            else:
                # All stages complete, check submission criteria
                if self._check_submission_criteria():
                    self.state.status = CollectionStatus.READY_TO_SUBMIT
                else:
                    self.state.status = CollectionStatus.STAGE_COMPLETE
        else:
            self.state.status = CollectionStatus.INCOMPLETE

    def _check_submission_criteria(self) -> bool:
        """Check if submission criteria are met.

        Returns:
            True if ready to submit, False otherwise
        """
        criteria = self.flow.submission_criteria

        # Check all required fields
        if "required_fields" in criteria:
            for field_name in criteria["required_fields"]:
                if field_name not in self.state.collected_fields:
                    return False

        return True

    def advance_stage(self) -> bool:
        """Move to next stage if current stage is complete.

        Returns:
            True if advanced, False if cannot advance
        """
        if self.state.status != CollectionStatus.STAGE_COMPLETE:
            return False

        if self.state.current_stage >= len(self.flow.stages) - 1:
            return False  # Already at last stage

        self.state.current_stage += 1
        self._update_status()
        return True

    def get_next_questions(self, limit: int = 3) -> List[FieldDefinition]:
        """Get the next questions to ask user.

        Smart ordering: dependencies first, required before optional, grouped fields together.

        Args:
            limit: Max number of questions to return

        Returns:
            List of field definitions to collect next
        """
        if self.state.current_stage >= len(self.flow.stages):
            return []

        current_stage = self.flow.stages[self.state.current_stage]
        collected = set(self.state.collected_fields.keys())

        # Get uncollected required fields
        uncollected = [
            f for f in current_stage.fields
            if f not in collected
        ]

        # Sort by priority
        def sort_key(field_name: str) -> tuple:
            field_def = get_field(field_name)
            if not field_def:
                return (999, 0, "", field_name)

            # Priority: required > optional
            priority = 0 if field_def.required else 1

            # Secondary: fields with satisfied dependencies first
            unsatisfied_deps = len(self._check_dependencies(field_def))

            return (priority, unsatisfied_deps, field_def.group or "", field_name)

        uncollected.sort(key=sort_key)

        # Return field definitions
        return [
            get_field(name) for name in uncollected[:limit]
            if get_field(name) is not None
        ]

    def get_progress(self) -> Dict[str, Any]:
        """Get collection progress summary.

        Returns:
            Dictionary with progress information
        """
        total_fields = sum(len(stage.fields) for stage in self.flow.stages)
        collected_count = len(self.state.collected_fields)

        return {
            "flow": self.flow.name,
            "current_stage": self.state.current_stage + 1,
            "total_stages": len(self.flow.stages),
            "stage_name": self.flow.stages[self.state.current_stage].name if self.state.current_stage < len(self.flow.stages) else "complete",
            "fields_collected": collected_count,
            "total_fields": total_fields,
            "percent_complete": int((collected_count / total_fields) * 100) if total_fields > 0 else 0,
            "status": self.state.status.value,
            "missing_fields": self.state.missing_fields,
            "validation_errors": self.state.validation_errors,
        }

    def is_ready_to_submit(self) -> bool:
        """Check if engine is ready to submit.

        Returns:
            True if ready to submit, False otherwise
        """
        return self.state.status == CollectionStatus.READY_TO_SUBMIT

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


def create_collection_engine(
    flow_type: FlowType,
    state: Optional[str] = None,
    ab_test: Optional[str] = None,
    flow_name: Optional[str] = None,
) -> Optional[CollectionEngine]:
    """Create a collection engine for a flow.

    Args:
        flow_type: Type of flow (quick_quote, detailed_quote, etc.)
        state: Optional state for state-specific flows
        ab_test: Optional A/B test name
        flow_name: Optional explicit flow name

    Returns:
        CollectionEngine instance or None if no matching flow
    """
    # Try explicit flow name first
    if flow_name:
        from .flow_configs import get_flow
        flow = get_flow(flow_name)
        if flow:
            return CollectionEngine(flow)

    # Try A/B test
    if ab_test:
        from .flow_configs import get_ab_test_variant
        flow = get_ab_test_variant(ab_test)
        if flow:
            return CollectionEngine(flow)

    # Get active flow for type/state
    flow = get_active_flow(flow_type, state)
    if not flow:
        return None

    return CollectionEngine(flow)
