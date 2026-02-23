"""
Test script for the insurance quote estimation engine.
"""

from insurance_server_python.pricing import InsuranceQuoteEstimator

def test_basic_quote():
    """Test basic quote generation."""
    estimator = InsuranceQuoteEstimator()

    # Test case: 25-year-old married in Beverly Hills with 2020 Honda Civic
    result = estimator.estimate_quotes(
        state="CA",
        zip_code="90210",
        age=25,
        marital_status="married",
        vehicle={
            "year": 2020,
            "make": "Honda",
            "model": "Civic"
        },
        coverage_type="full",
        carriers=[
            "Geico",
            "Progressive Insurance",
            "Mercury Auto Insurance"
        ]
    )

    print("=" * 80)
    print("TEST: 25-year-old married, 90210, 2020 Honda Civic, full coverage")
    print("=" * 80)

    print(f"\nBaseline:")
    print(f"  Annual: ${result['baseline']['annual']:,}")
    print(f"  Monthly: ${result['baseline']['monthly']:,}")
    print(f"  Confidence: {result['baseline']['confidence']} (±{result['baseline']['band']*100:.0f}%)")

    print(f"\nCarrier Quotes ({len(result['quotes'])} total):")
    for quote in result['quotes']:
        print(f"\n  {quote['carrier']}:")
        print(f"    Monthly: ${quote['monthly']:,}")
        print(f"    Range: ${quote['range_monthly'][0]:,} - ${quote['range_monthly'][1]:,}")
        print(f"    Confidence: {quote['confidence']}")
        print(f"    Factors:")
        for exp in quote['explanations']:
            print(f"      • {exp}")

def test_high_risk_quote():
    """Test high-risk profile."""
    estimator = InsuranceQuoteEstimator()

    # Test case: 19-year-old single in Miami with 2024 BMW M3
    result = estimator.estimate_quotes(
        state="FL",
        zip_code="33101",
        age=19,
        marital_status="single",
        vehicle={
            "year": 2024,
            "make": "BMW",
            "model": "M3"
        },
        coverage_type="full",
        carriers=[
            "Progressive Insurance",
            "National General",
            "Geico"
        ],
        accidents=1,
        tickets=2
    )

    print("\n" + "=" * 80)
    print("TEST: 19-year-old single, Miami, 2024 BMW M3, 1 accident, 2 tickets")
    print("=" * 80)

    print(f"\nBaseline:")
    print(f"  Annual: ${result['baseline']['annual']:,}")
    print(f"  Monthly: ${result['baseline']['monthly']:,}")
    print(f"  Confidence: {result['baseline']['confidence']} (±{result['baseline']['band']*100:.0f}%)")

    print(f"\nCarrier Quotes ({len(result['quotes'])} total):")
    for quote in result['quotes']:
        print(f"\n  {quote['carrier']}:")
        print(f"    Monthly: ${quote['monthly']:,}")
        print(f"    Range: ${quote['range_monthly'][0]:,} - ${quote['range_monthly'][1]:,}")

def test_low_cost_quote():
    """Test low-cost rural scenario."""
    estimator = InsuranceQuoteEstimator()

    # Test case: 45-year-old married in Iowa with 2015 Toyota Corolla
    result = estimator.estimate_quotes(
        state="IA",
        zip_code="50001",
        age=45,
        marital_status="married",
        vehicle={
            "year": 2015,
            "make": "Toyota",
            "model": "Corolla"
        },
        coverage_type="full",
        carriers=[
            "Geico",
            "Progressive Insurance",
            "Safeco Insurance"
        ]
    )

    print("\n" + "=" * 80)
    print("TEST: 45-year-old married, Iowa, 2015 Toyota Corolla")
    print("=" * 80)

    print(f"\nBaseline:")
    print(f"  Annual: ${result['baseline']['annual']:,}")
    print(f"  Monthly: ${result['baseline']['monthly']:,}")

    print(f"\nCarrier Quotes ({len(result['quotes'])} total):")
    for quote in result['quotes']:
        print(f"  {quote['carrier']}: ${quote['monthly']:,}/mo")

if __name__ == "__main__":
    test_basic_quote()
    test_high_risk_quote()
    test_low_cost_quote()

    print("\n" + "=" * 80)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 80)
