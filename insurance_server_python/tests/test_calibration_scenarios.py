"""
Real-world calibration test suite.

This test file validates our estimation engine against actual quotes from real carriers.
Each scenario represents real-world data that can be used to:
1. Verify current estimation accuracy
2. Detect regressions when making calibration changes
3. Track improvements over time

ADDING NEW SCENARIOS:
When you receive actual quotes from carriers, add them to CALIBRATION_SCENARIOS below.
This creates a regression test that ensures future calibrations don't break existing accuracy.

TOLERANCE LEVELS:
- Excellent: ±5% error
- Good: ±10% error
- Acceptable: ±15% error
- Needs Calibration: >15% error
"""

import unittest
from typing import Dict, List
from insurance_server_python.pricing.estimator import InsuranceQuoteEstimator


# ============================================================================
# CALIBRATION SCENARIOS (Real-world quotes)
# ============================================================================

CALIBRATION_SCENARIOS = [
    {
        "scenario_id": "90210_liability_2024_01",
        "description": "Beverly Hills 90210 - Age 25, Single, 2020 Civic, Liability Only",
        "source": "Actual quotes received 2024 (see CALIBRATION_90210_UPDATES.md)",
        "date_collected": "2024",

        # Input profile
        "profile": {
            "state": "CA",
            "zip_code": "90210",
            "age": 25,
            "marital_status": "single",
            "vehicle": {
                "year": 2020,
                "make": "Honda",
                "model": "Civic"
            },
            "coverage_type": "liability"
        },

        # Actual quotes (monthly premiums)
        "actual_quotes": {
            "Mercury Auto Insurance": 183,
            "Progressive Insurance": 214,
            "National General": 247
        },

        # Tolerance: ±15% is acceptable for liability-only (more carrier-specific variance)
        # Liability-only pricing has more variance across carriers than full coverage
        # because different carriers have different appetites for minimum coverage buyers
        "tolerance_percent": 15.0
    },

    # ADD NEW SCENARIOS HERE:
    # {
    #     "scenario_id": "unique_id",
    #     "description": "Brief description of scenario",
    #     "source": "Where the quotes came from",
    #     "date_collected": "YYYY-MM-DD",
    #     "profile": {
    #         "state": "TX",
    #         "zip_code": "75001",
    #         "age": 35,
    #         "marital_status": "married",
    #         "vehicle": {"year": 2022, "make": "Toyota", "model": "Camry"},
    #         "coverage_type": "full"
    #     },
    #     "actual_quotes": {
    #         "Geico": 150,
    #         "Progressive Insurance": 165,
    #     },
    #     "tolerance_percent": 10.0
    # },
]


# ============================================================================
# TEST SUITE
# ============================================================================

class TestCalibrationScenarios(unittest.TestCase):
    """
    Validates estimation engine against real-world quote data.

    This test suite ensures:
    1. Our estimates match actual quotes within acceptable tolerance
    2. New calibrations don't break existing accuracy (regression detection)
    3. We track performance across different scenarios
    """

    def setUp(self):
        """Initialize the estimator for each test."""
        self.estimator = InsuranceQuoteEstimator()

    def test_all_calibration_scenarios(self):
        """
        Test all real-world calibration scenarios.

        This is the main regression test - it verifies that our engine produces
        accurate estimates for all known real-world quote data.
        """
        if not CALIBRATION_SCENARIOS:
            self.skipTest("No calibration scenarios defined yet")

        all_results = []

        for scenario in CALIBRATION_SCENARIOS:
            scenario_id = scenario["scenario_id"]
            description = scenario["description"]
            profile = scenario["profile"]
            actual_quotes = scenario["actual_quotes"]
            tolerance = scenario["tolerance_percent"]

            # Get carrier list from actual quotes
            carriers = list(actual_quotes.keys())

            # Execute estimation
            result = self.estimator.estimate_quotes(
                state=profile["state"],
                zip_code=profile["zip_code"],
                age=profile["age"],
                marital_status=profile["marital_status"],
                vehicle=profile["vehicle"],
                coverage_type=profile["coverage_type"],
                carriers=carriers
            )

            # Validate each carrier
            scenario_errors = []
            for quote in result["quotes"]:
                carrier = quote["carrier"]
                estimated_monthly = quote["monthly"]
                actual_monthly = actual_quotes[carrier]

                # Calculate error percentage
                error_pct = abs(estimated_monthly - actual_monthly) / actual_monthly * 100

                scenario_errors.append({
                    "carrier": carrier,
                    "estimated": estimated_monthly,
                    "actual": actual_monthly,
                    "error_pct": error_pct,
                    "within_tolerance": error_pct <= tolerance
                })

            # Record results for summary
            all_results.append({
                "scenario_id": scenario_id,
                "description": description,
                "errors": scenario_errors
            })

            # Assert all carriers within tolerance
            for error in scenario_errors:
                self.assertLessEqual(
                    error["error_pct"],
                    tolerance,
                    f"\n{scenario_id}: {error['carrier']}\n"
                    f"  Estimated: ${error['estimated']}/mo\n"
                    f"  Actual: ${error['actual']}/mo\n"
                    f"  Error: {error['error_pct']:.1f}% (tolerance: {tolerance}%)\n"
                    f"  Description: {description}"
                )

        # Print summary (visible when running with -v)
        self._print_calibration_summary(all_results)

    def test_scenario_by_scenario(self):
        """
        Individual test for each scenario.

        This generates separate test results for each scenario, making it easier
        to identify which specific scenario failed.
        """
        for scenario in CALIBRATION_SCENARIOS:
            with self.subTest(scenario_id=scenario["scenario_id"]):
                self._validate_scenario(scenario)

    def _validate_scenario(self, scenario: Dict):
        """Validate a single calibration scenario."""
        profile = scenario["profile"]
        actual_quotes = scenario["actual_quotes"]
        tolerance = scenario["tolerance_percent"]

        carriers = list(actual_quotes.keys())

        result = self.estimator.estimate_quotes(
            state=profile["state"],
            zip_code=profile["zip_code"],
            age=profile["age"],
            marital_status=profile["marital_status"],
            vehicle=profile["vehicle"],
            coverage_type=profile["coverage_type"],
            carriers=carriers
        )

        for quote in result["quotes"]:
            carrier = quote["carrier"]
            estimated_monthly = quote["monthly"]
            actual_monthly = actual_quotes[carrier]
            error_pct = abs(estimated_monthly - actual_monthly) / actual_monthly * 100

            self.assertLessEqual(
                error_pct,
                tolerance,
                f"{carrier}: ${estimated_monthly}/mo vs actual ${actual_monthly}/mo "
                f"({error_pct:.1f}% error, tolerance: {tolerance}%)"
            )

    def _print_calibration_summary(self, results: List[Dict]):
        """Print a summary of calibration accuracy across all scenarios."""
        print("\n" + "="*80)
        print("CALIBRATION ACCURACY SUMMARY")
        print("="*80)

        for result in results:
            print(f"\n{result['scenario_id']}: {result['description']}")
            print("-" * 80)

            for error in result['errors']:
                status = "✅" if error['within_tolerance'] else "❌"
                print(
                    f"  {status} {error['carrier']:30s} "
                    f"Est: ${error['estimated']:3d}/mo  "
                    f"Actual: ${error['actual']:3d}/mo  "
                    f"Error: {error['error_pct']:5.1f}%"
                )

        print("\n" + "="*80)


class TestCalibrationFramework(unittest.TestCase):
    """
    Tests for the calibration framework itself.

    These tests ensure the calibration test suite is working correctly.
    """

    def test_scenarios_have_required_fields(self):
        """Validate that all scenarios have required fields."""
        required_fields = [
            "scenario_id",
            "description",
            "source",
            "date_collected",
            "profile",
            "actual_quotes",
            "tolerance_percent"
        ]

        for scenario in CALIBRATION_SCENARIOS:
            for field in required_fields:
                self.assertIn(
                    field,
                    scenario,
                    f"Scenario {scenario.get('scenario_id', 'UNKNOWN')} missing field: {field}"
                )

    def test_scenario_profiles_have_required_fields(self):
        """Validate that all profile sections have required fields."""
        required_profile_fields = [
            "state",
            "zip_code",
            "age",
            "marital_status",
            "vehicle",
            "coverage_type"
        ]

        for scenario in CALIBRATION_SCENARIOS:
            profile = scenario.get("profile", {})
            for field in required_profile_fields:
                self.assertIn(
                    field,
                    profile,
                    f"Scenario {scenario.get('scenario_id')} profile missing: {field}"
                )

    def test_scenario_ids_are_unique(self):
        """Ensure all scenario IDs are unique."""
        ids = [s["scenario_id"] for s in CALIBRATION_SCENARIOS]
        self.assertEqual(
            len(ids),
            len(set(ids)),
            f"Duplicate scenario IDs found: {[id for id in ids if ids.count(id) > 1]}"
        )

    def test_tolerance_values_are_reasonable(self):
        """Ensure tolerance values are within reasonable bounds."""
        for scenario in CALIBRATION_SCENARIOS:
            tolerance = scenario["tolerance_percent"]
            self.assertGreater(
                tolerance,
                0,
                f"Scenario {scenario['scenario_id']} has invalid tolerance: {tolerance}%"
            )
            self.assertLessEqual(
                tolerance,
                20,
                f"Scenario {scenario['scenario_id']} tolerance too high: {tolerance}% "
                f"(if >20% error is acceptable, consider recalibrating instead)"
            )


class TestCalibrationMetrics(unittest.TestCase):
    """
    Calculate and report calibration metrics.

    These tests measure overall engine performance across all scenarios.
    """

    def setUp(self):
        """Initialize the estimator."""
        self.estimator = InsuranceQuoteEstimator()

    def test_overall_accuracy_metrics(self):
        """
        Calculate overall accuracy metrics across all scenarios.

        This doesn't assert/fail - it reports metrics for monitoring.
        """
        if not CALIBRATION_SCENARIOS:
            self.skipTest("No calibration scenarios defined yet")

        all_errors = []

        for scenario in CALIBRATION_SCENARIOS:
            profile = scenario["profile"]
            actual_quotes = scenario["actual_quotes"]
            carriers = list(actual_quotes.keys())

            result = self.estimator.estimate_quotes(
                state=profile["state"],
                zip_code=profile["zip_code"],
                age=profile["age"],
                marital_status=profile["marital_status"],
                vehicle=profile["vehicle"],
                coverage_type=profile["coverage_type"],
                carriers=carriers
            )

            for quote in result["quotes"]:
                carrier = quote["carrier"]
                estimated = quote["monthly"]
                actual = actual_quotes[carrier]
                error_pct = abs(estimated - actual) / actual * 100
                all_errors.append(error_pct)

        # Calculate metrics
        avg_error = sum(all_errors) / len(all_errors)
        max_error = max(all_errors)
        min_error = min(all_errors)

        # Count by quality tier
        excellent = sum(1 for e in all_errors if e <= 5)
        good = sum(1 for e in all_errors if 5 < e <= 10)
        acceptable = sum(1 for e in all_errors if 10 < e <= 15)
        needs_work = sum(1 for e in all_errors if e > 15)

        total = len(all_errors)

        print("\n" + "="*80)
        print("OVERALL CALIBRATION METRICS")
        print("="*80)
        print(f"Total Carrier Estimates: {total}")
        print(f"Average Error: {avg_error:.2f}%")
        print(f"Min Error: {min_error:.2f}%")
        print(f"Max Error: {max_error:.2f}%")
        print()
        print("Error Distribution:")
        print(f"  Excellent (≤5%):   {excellent:3d} ({excellent/total*100:.1f}%)")
        print(f"  Good (5-10%):      {good:3d} ({good/total*100:.1f}%)")
        print(f"  Acceptable (10-15%): {acceptable:3d} ({acceptable/total*100:.1f}%)")
        print(f"  Needs Work (>15%): {needs_work:3d} ({needs_work/total*100:.1f}%)")
        print("="*80 + "\n")

        # This test always passes - it's just for reporting
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
