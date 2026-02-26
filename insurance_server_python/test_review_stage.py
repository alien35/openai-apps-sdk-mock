"""Test: Review and Correction Stage

This test demonstrates the review stage functionality where users can:
1. Collect fields normally
2. Enter review mode to see all collected data
3. Apply corrections to any field
4. Confirm review to proceed with submission
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from insurance_server_python.collection_engine import (
    CollectionStatus,
    CollectionEngine,
)
from insurance_server_python.flow_configs import (
    FlowConfig,
    StageConfig,
    StageType,
    FlowType,
)


def test_review_flow_basic():
    """Test 1: Basic Review Flow"""
    print("=" * 70)
    print("TEST 1: Basic Review Flow")
    print("=" * 70)

    # Create a simple flow with review stage
    flow_with_review = FlowConfig(
        name="quick_quote_review_test",
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
        },
        metadata={"version": "test", "active": True}
    )

    engine = CollectionEngine(flow_with_review)

    # Step 1: Collect fields
    print("\n→ Step 1: Collecting fields...")
    state = engine.collect_fields({
        "ZipCode": "94103",
        "NumberOfDrivers": 2,
    })
    print(f"✓ Status after collection: {state.status.value}")
    print(f"✓ Collected: {list(state.collected_fields.keys())}")
    assert state.status == CollectionStatus.READY_TO_SUBMIT

    # Step 2: Enter review mode
    print("\n→ Step 2: Entering review mode...")
    state = engine.enter_review_mode()
    print(f"✓ Status in review: {state.status.value}")
    assert state.status == CollectionStatus.IN_REVIEW

    # Step 3: Get review summary
    print("\n→ Step 3: Getting review summary...")
    summary = engine.get_review_summary()
    print("✓ Review summary:")
    for field_name, field_info in summary.items():
        print(f"  • {field_info['label']}: {field_info['value']}")
    assert "ZipCode" in summary
    assert "NumberOfDrivers" in summary

    # Step 4: Confirm review (no corrections)
    print("\n→ Step 4: Confirming review...")
    state = engine.confirm_review()
    print(f"✓ Status after confirmation: {state.status.value}")
    assert state.status == CollectionStatus.READY_TO_SUBMIT

    return True


def test_review_with_corrections():
    """Test 2: Review with Corrections"""
    print("\n" + "=" * 70)
    print("TEST 2: Review with Corrections")
    print("=" * 70)

    flow_with_review = FlowConfig(
        name="quick_quote_corrections_test",
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
        },
        metadata={"version": "test", "active": True}
    )

    engine = CollectionEngine(flow_with_review)

    # Collect initial data
    print("\n→ Initial collection...")
    state = engine.collect_fields({
        "ZipCode": "94103",
        "NumberOfDrivers": 2,
    })
    print(f"✓ Initial: ZipCode={state.collected_fields['ZipCode']}, "
          f"NumberOfDrivers={state.collected_fields['NumberOfDrivers']}")

    # Enter review
    print("\n→ Entering review...")
    state = engine.enter_review_mode()
    assert state.status == CollectionStatus.IN_REVIEW

    # Apply corrections
    print("\n→ User says: 'Actually, I have 3 drivers'")
    state = engine.apply_corrections({"NumberOfDrivers": 3})
    print(f"✓ After correction: NumberOfDrivers={state.collected_fields['NumberOfDrivers']}")
    assert state.collected_fields["NumberOfDrivers"] == 3
    assert state.status == CollectionStatus.IN_REVIEW

    # Show updated summary
    summary = engine.get_review_summary()
    print("\n✓ Updated review summary:")
    for field_name, field_info in summary.items():
        print(f"  • {field_info['label']}: {field_info['value']}")

    # Confirm review
    print("\n→ User says: 'looks good'")
    state = engine.confirm_review()
    print(f"✓ Status after confirmation: {state.status.value}")
    assert state.status == CollectionStatus.READY_TO_SUBMIT
    assert state.collected_fields["NumberOfDrivers"] == 3

    return True


def test_review_with_multiple_corrections():
    """Test 3: Multiple Corrections in Review"""
    print("\n" + "=" * 70)
    print("TEST 3: Multiple Corrections")
    print("=" * 70)

    flow_with_review = FlowConfig(
        name="quick_quote_multi_corrections_test",
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
        },
        metadata={"version": "test", "active": True}
    )

    engine = CollectionEngine(flow_with_review)

    # Collect initial data
    print("\n→ Initial collection...")
    engine.collect_fields({
        "ZipCode": "94103",
        "NumberOfDrivers": 2,
    })

    # Enter review
    engine.enter_review_mode()

    # Apply multiple corrections
    print("\n→ User corrects both zip code and number of drivers...")
    state = engine.apply_corrections({
        "ZipCode": "90210",
        "NumberOfDrivers": 4,
    })

    print("✓ After corrections:")
    print(f"  • ZipCode: 94103 → {state.collected_fields['ZipCode']}")
    print(f"  • NumberOfDrivers: 2 → {state.collected_fields['NumberOfDrivers']}")

    assert state.collected_fields["ZipCode"] == "90210"
    assert state.collected_fields["NumberOfDrivers"] == 4

    # Confirm
    state = engine.confirm_review()
    assert state.status == CollectionStatus.READY_TO_SUBMIT

    return True


def test_review_with_invalid_correction():
    """Test 4: Validation During Corrections"""
    print("\n" + "=" * 70)
    print("TEST 4: Validation During Corrections")
    print("=" * 70)

    flow_with_review = FlowConfig(
        name="quick_quote_validation_test",
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
        },
        metadata={"version": "test", "active": True}
    )

    engine = CollectionEngine(flow_with_review)

    # Collect initial data
    engine.collect_fields({
        "ZipCode": "94103",
        "NumberOfDrivers": 2,
    })

    # Enter review
    engine.enter_review_mode()

    # Try invalid correction
    print("\n→ User tries to correct zip code to 'INVALID'...")
    state = engine.apply_corrections({"ZipCode": "INVALID"})

    if state.validation_errors:
        print("✓ Validation error caught:")
        for field, error in state.validation_errors.items():
            print(f"  • {field}: {error}")

    assert "ZipCode" in state.validation_errors
    assert state.collected_fields["ZipCode"] == "94103"  # Original value preserved
    assert state.status == CollectionStatus.IN_REVIEW

    # Try valid correction
    print("\n→ User corrects zip code to valid value '90210'...")
    state = engine.apply_corrections({"ZipCode": "90210"})
    print(f"✓ Valid correction applied: {state.collected_fields['ZipCode']}")

    assert "ZipCode" not in state.validation_errors
    assert state.collected_fields["ZipCode"] == "90210"

    return True


def test_cannot_review_incomplete_collection():
    """Test 5: Cannot Review Incomplete Collection"""
    print("\n" + "=" * 70)
    print("TEST 5: Cannot Review Incomplete Collection")
    print("=" * 70)

    flow_with_review = FlowConfig(
        name="quick_quote_incomplete_test",
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
        },
        metadata={"version": "test", "active": True}
    )

    engine = CollectionEngine(flow_with_review)

    # Collect only partial data
    print("\n→ Collecting only ZipCode (incomplete)...")
    state = engine.collect_fields({"ZipCode": "94103"})
    print(f"✓ Status: {state.status.value}")
    print(f"✓ Missing: {state.missing_fields}")
    assert state.status == CollectionStatus.INCOMPLETE

    # Try to enter review
    print("\n→ Attempting to enter review mode...")
    state = engine.enter_review_mode()
    print(f"✓ Status remains: {state.status.value}")
    assert state.status == CollectionStatus.INCOMPLETE  # Should not change

    return True


def run_all_tests():
    """Run all review stage tests"""
    print("\n" + "=" * 70)
    print("REVIEW & CORRECTION STAGE - TEST SUITE")
    print("=" * 70)

    tests = [
        ("Basic Review Flow", test_review_flow_basic),
        ("Review with Corrections", test_review_with_corrections),
        ("Multiple Corrections", test_review_with_multiple_corrections),
        ("Validation During Corrections", test_review_with_invalid_correction),
        ("Cannot Review Incomplete", test_cannot_review_incomplete_collection),
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
        print("\n🎉 All review stage tests passed! Feature is working correctly.")
    else:
        print(f"\n⚠️  {failed} test(s) failed.")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
