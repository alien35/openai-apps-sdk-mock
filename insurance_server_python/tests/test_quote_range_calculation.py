"""
Unit tests for insurance quote range calculations.

Tests validate that specific inputs produce expected range outputs,
based on the calculation breakdown for the quote estimation system.
"""

import unittest
from insurance_server_python.pricing.estimator import InsuranceQuoteEstimator


class TestQuoteRangeCalculation(unittest.TestCase):
    """Test quote range calculations match expected values."""

    def setUp(self):
        """Initialize the estimator for each test."""
        self.estimator = InsuranceQuoteEstimator()

    def test_ca_90210_25yo_single_2020_civic_full_coverage_ranges(self):
        """
        Test range calculation for specific scenario:
        - State: CA
        - ZIP: 90210 (Beverly Hills)
        - Driver: 25 years old, single
        - Vehicle: 2020 Honda Civic
        - Coverage: Full

        Expected ranges (calibrated from actual 90210 quote data - CALIBRATION_90210_UPDATES.md):
        - Mercury Auto Insurance: $238-$443/mo, $2,856-$5,316/yr
        - Progressive Insurance: $270-$503/mo, $3,240-$6,036/yr
        - National General: $327-$608/mo, $3,924-$7,296/yr

        Note: These values reflect the 2024 calibration based on real-world quotes.
        Mercury is 7% lower than before due to increased CA competitiveness (-0.15 adjustment).
        Progressive is slightly higher due to CA pricing adjustment (+0.10).
        National General is higher due to increased base multipliers.
        """
        # Input parameters
        state = "CA"
        zip_code = "90210"
        age = 25
        marital_status = "single"
        vehicle = {
            "year": 2020,
            "make": "Honda",
            "model": "Civic"
        }
        coverage_type = "full"
        carriers = [
            "Mercury Auto Insurance",
            "Progressive Insurance",
            "National General"
        ]

        # Expected ranges for each carrier (post-calibration)
        expected_ranges = {
            "Mercury Auto Insurance": {
                "monthly": [238, 443],
                "annual": [2856, 5316]
            },
            "Progressive Insurance": {
                "monthly": [285, 530],
                "annual": [3420, 6360]
            },
            "National General": {
                "monthly": [326, 605],
                "annual": [3912, 7260]
            }
        }

        # Execute estimation
        result = self.estimator.estimate_quotes(
            state=state,
            zip_code=zip_code,
            age=age,
            marital_status=marital_status,
            vehicle=vehicle,
            coverage_type=coverage_type,
            carriers=carriers
        )

        # Validate structure
        self.assertIn("quotes", result)
        self.assertEqual(len(result["quotes"]), 3)

        # Validate each carrier's ranges
        for quote in result["quotes"]:
            carrier = quote["carrier"]
            self.assertIn(carrier, expected_ranges, f"Unexpected carrier: {carrier}")

            expected = expected_ranges[carrier]
            actual_monthly = quote["range_monthly"]
            actual_annual = quote["range_annual"]

            # Validate monthly range
            self.assertEqual(
                actual_monthly,
                expected["monthly"],
                f"{carrier} monthly range mismatch: expected {expected['monthly']}, got {actual_monthly}"
            )

            # Validate annual range
            self.assertEqual(
                actual_annual,
                expected["annual"],
                f"{carrier} annual range mismatch: expected {expected['annual']}, got {actual_annual}"
            )

    def test_range_values_are_within_bounds(self):
        """Test that range calculations produce reasonable bounds."""
        # Use same inputs as above
        result = self.estimator.estimate_quotes(
            state="CA",
            zip_code="90210",
            age=25,
            marital_status="single",
            vehicle={"year": 2020, "make": "Honda", "model": "Civic"},
            coverage_type="full",
            carriers=["Mercury Auto Insurance", "Progressive Insurance", "National General"]
        )

        for quote in result["quotes"]:
            carrier = quote["carrier"]
            monthly_low, monthly_high = quote["range_monthly"]
            annual_low, annual_high = quote["range_annual"]

            # Validate range ordering
            self.assertLess(
                monthly_low,
                monthly_high,
                f"{carrier}: monthly low should be less than high"
            )
            self.assertLess(
                annual_low,
                annual_high,
                f"{carrier}: annual low should be less than high"
            )

            # Validate annual is 12x monthly
            self.assertEqual(
                annual_low,
                monthly_low * 12,
                f"{carrier}: annual low should be 12x monthly low"
            )
            self.assertEqual(
                annual_high,
                monthly_high * 12,
                f"{carrier}: annual high should be 12x monthly high"
            )

            # Validate ranges are positive
            self.assertGreater(monthly_low, 0, f"{carrier}: monthly low should be positive")
            self.assertGreater(annual_low, 0, f"{carrier}: annual low should be positive")

    def test_baseline_confidence_assessment(self):
        """Test that confidence level is correctly assessed based on input completeness."""
        result = self.estimator.estimate_quotes(
            state="CA",
            zip_code="90210",
            age=25,
            marital_status="single",
            vehicle={"year": 2020, "make": "Honda", "model": "Civic"},
            coverage_type="full",
            carriers=["Mercury Auto Insurance"]
        )

        # Validate baseline includes confidence metadata
        self.assertIn("baseline", result)
        self.assertIn("confidence", result["baseline"])
        self.assertIn("band", result["baseline"])

        # With 5 core inputs (age, zip, vehicle, coverage, marital), should be "medium"
        self.assertEqual(result["baseline"]["confidence"], "medium")
        self.assertEqual(result["baseline"]["band"], 0.30)

    def test_carrier_ordering(self):
        """Test that carriers are sorted by monthly premium (lowest first)."""
        result = self.estimator.estimate_quotes(
            state="CA",
            zip_code="90210",
            age=25,
            marital_status="single",
            vehicle={"year": 2020, "make": "Honda", "model": "Civic"},
            coverage_type="full",
            carriers=["National General", "Mercury Auto Insurance", "Progressive Insurance"]
        )

        quotes = result["quotes"]

        # Verify they're sorted by monthly price ascending
        for i in range(len(quotes) - 1):
            self.assertLessEqual(
                quotes[i]["monthly"],
                quotes[i + 1]["monthly"],
                f"Quotes should be sorted by monthly premium: {quotes[i]['carrier']} "
                f"(${quotes[i]['monthly']}) should be <= {quotes[i+1]['carrier']} "
                f"(${quotes[i+1]['monthly']})"
            )

        # Based on expected ranges, Mercury should be first (lowest), National General last
        self.assertEqual(quotes[0]["carrier"], "Mercury Auto Insurance")
        self.assertEqual(quotes[-1]["carrier"], "National General")


if __name__ == "__main__":
    unittest.main()
