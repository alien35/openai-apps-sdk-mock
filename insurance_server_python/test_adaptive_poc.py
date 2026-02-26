"""Proof of Concept: Adaptive Architecture Test

This script demonstrates the adaptive architecture working with:
1. Order-agnostic field collection
2. Progressive state building
3. Configuration-driven flows
4. Field validation
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from insurance_server_python.field_registry import (
    get_field,
    validate_field_value,
    get_fields_by_context,
    FieldContext,
)
from insurance_server_python.flow_configs import (
    get_active_flow,
    list_flows_by_type,
    FlowType,
)
from insurance_server_python.collection_engine import (
    create_collection_engine,
)


def test_field_registry():
    """Test 1: Field Registry"""
    print("=" * 70)
    print("TEST 1: Field Registry")
    print("=" * 70)

    # Get a field definition
    zip_field = get_field("ZipCode")
    print(f"\n✓ Field: {zip_field.name}")
    print(f"  Type: {zip_field.field_type.value}")
    print(f"  Required: {zip_field.required}")
    print(f"  Prompt: '{zip_field.prompt_text}'")
    print(f"  Example: {zip_field.example}")

    # Test validation
    valid, _ = validate_field_value("ZipCode", "94103")
    print(f"\n✓ Validation for '94103': {valid}")

    invalid, error = validate_field_value("ZipCode", "ABC")
    print(f"✗ Validation for 'ABC': {invalid} ({error})")

    # List fields by context
    quick_quote_fields = get_fields_by_context(FieldContext.QUICK_QUOTE)
    print(f"\n✓ Quick Quote fields: {[f.name for f in quick_quote_fields]}")

    return True


def test_flow_configuration():
    """Test 2: Flow Configuration"""
    print("\n" + "=" * 70)
    print("TEST 2: Flow Configuration")
    print("=" * 70)

    # List all quick quote flows
    flows = list_flows_by_type(FlowType.QUICK_QUOTE)
    print(f"\n✓ Available quick quote flows: {[f.name for f in flows]}")

    for flow in flows:
        active = "ACTIVE" if flow.metadata.get("active") else "inactive"
        print(f"  • {flow.name} (v{flow.metadata.get('version')}) - {active}")
        print(f"    Fields: {flow.stages[0].fields}")
        print(f"    Optional: {flow.stages[0].optional_fields}")

    # Get active flow
    active_flow = get_active_flow(FlowType.QUICK_QUOTE)
    print(f"\n✓ Active flow: {active_flow.name}")
    print(f"  Required fields: {active_flow.submission_criteria['required_fields']}")

    return True


def test_collection_engine_complete():
    """Test 3: Collection Engine - Complete Flow"""
    print("\n" + "=" * 70)
    print("TEST 3: Collection Engine - Complete Flow")
    print("=" * 70)

    # Create engine
    engine = create_collection_engine(FlowType.QUICK_QUOTE)
    print(f"\n✓ Created engine for flow: {engine.flow.name}")

    # Collect fields all at once
    print("\n→ Collecting all fields at once...")
    state = engine.collect_fields({
        "ZipCode": "94103",
        "NumberOfDrivers": 2,
    })

    progress = engine.get_progress()
    print(f"✓ Status: {state.status.value}")
    print(f"✓ Progress: {progress['percent_complete']}%")
    print(f"✓ Collected: {list(state.collected_fields.keys())}")
    print(f"✓ Missing: {state.missing_fields}")
    print(f"✓ Ready to submit: {engine.is_ready_to_submit()}")

    return engine.is_ready_to_submit()


def test_collection_engine_incremental():
    """Test 4: Collection Engine - Incremental (Order-Agnostic)"""
    print("\n" + "=" * 70)
    print("TEST 4: Collection Engine - Incremental Collection")
    print("=" * 70)

    # Create engine
    engine = create_collection_engine(FlowType.QUICK_QUOTE)

    # Collect fields ONE AT A TIME in ANY ORDER
    print("\n→ Collecting NumberOfDrivers first...")
    state = engine.collect_fields({"NumberOfDrivers": 2})
    print(f"✓ Status: {state.status.value}")
    print(f"✓ Collected: {list(state.collected_fields.keys())}")
    print(f"✓ Missing: {state.missing_fields}")

    next_questions = engine.get_next_questions(limit=2)
    print(f"✓ Next questions: {[q.prompt_text for q in next_questions]}")

    print("\n→ Now collecting ZipCode...")
    state = engine.collect_fields({"ZipCode": "94103"})
    print(f"✓ Status: {state.status.value}")
    print(f"✓ Collected: {list(state.collected_fields.keys())}")
    print(f"✓ Missing: {state.missing_fields}")
    print(f"✓ Ready to submit: {engine.is_ready_to_submit()}")

    return engine.is_ready_to_submit()


def test_validation_errors():
    """Test 5: Validation Errors"""
    print("\n" + "=" * 70)
    print("TEST 5: Validation Errors")
    print("=" * 70)

    engine = create_collection_engine(FlowType.QUICK_QUOTE)

    # Try to collect invalid data
    print("\n→ Attempting to collect invalid zip code...")
    state = engine.collect_fields({
        "ZipCode": "INVALID",
        "NumberOfDrivers": 2,
    })

    if state.validation_errors:
        print("✓ Validation errors caught:")
        for field, error in state.validation_errors.items():
            print(f"  • {field}: {error}")

    print(f"\n✓ Status: {state.status.value}")
    print(f"✓ Collected valid fields: {list(state.collected_fields.keys())}")
    print(f"✓ Ready to submit: {engine.is_ready_to_submit()}")

    return len(state.validation_errors) > 0


def test_flow_switching():
    """Test 6: Flow Switching (Configuration Change)"""
    print("\n" + "=" * 70)
    print("TEST 6: Flow Switching (Simulating Config Change)")
    print("=" * 70)

    # Simulate switching active flow
    from insurance_server_python.flow_configs import QUICK_QUOTE_V1, QUICK_QUOTE_V2

    print("\n→ Current active flow: v1 (minimal)")
    print(f"  Fields: {QUICK_QUOTE_V1.stages[0].fields}")

    print("\n→ Simulating switch to v2 (with email)...")
    # In production, this would be a config change
    QUICK_QUOTE_V1.metadata["active"] = False
    QUICK_QUOTE_V2.metadata["active"] = True

    # Create engine with new active flow
    engine = create_collection_engine(FlowType.QUICK_QUOTE)
    print(f"✓ New engine using flow: {engine.flow.name}")
    print(f"  Fields: {engine.flow.stages[0].fields}")
    print(f"  Optional: {engine.flow.stages[0].optional_fields}")

    # Collect with new flow
    state = engine.collect_fields({
        "ZipCode": "94103",
        "NumberOfDrivers": 2,
        "EmailAddress": "john@example.com",
    })

    print(f"\n✓ Status: {state.status.value}")
    print(f"✓ Collected: {list(state.collected_fields.keys())}")
    print(f"✓ Email collected: {'EmailAddress' in state.collected_fields}")

    # Restore original state
    QUICK_QUOTE_V1.metadata["active"] = True
    QUICK_QUOTE_V2.metadata["active"] = False

    return "EmailAddress" in state.collected_fields


def run_all_tests():
    """Run all POC tests"""
    print("\n" + "=" * 70)
    print("ADAPTIVE ARCHITECTURE - PROOF OF CONCEPT")
    print("=" * 70)

    tests = [
        ("Field Registry", test_field_registry),
        ("Flow Configuration", test_flow_configuration),
        ("Complete Collection", test_collection_engine_complete),
        ("Incremental Collection", test_collection_engine_incremental),
        ("Validation Errors", test_validation_errors),
        ("Flow Switching", test_flow_switching),
    ]

    results = []
    for name, test_fn in tests:
        try:
            result = test_fn()
            results.append((name, result, None))
        except Exception as e:
            results.append((name, False, str(e)))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = 0
    failed = 0

    for name, result, error in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
        if error:
            print(f"  Error: {error}")

        if result:
            passed += 1
        else:
            failed += 1

    print(f"\n{passed}/{len(tests)} tests passed")

    if failed == 0:
        print("\n🎉 All tests passed! Adaptive architecture is working correctly.")
    else:
        print(f"\n⚠️  {failed} test(s) failed.")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
