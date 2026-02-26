"""
Quote calculation logging and explanation generator.

Writes detailed breakdowns of how insurance quotes are calculated to markdown files.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# Directory for storing quote explanations
QUOTE_EXPLANATIONS_DIR = Path(__file__).parent / "quote_explanations"
QUOTE_EXPLANATIONS_DIR.mkdir(exist_ok=True)


def log_quick_quote_calculation(
    state: str,
    zip_code: str,
    age: int,
    marital_status: str,
    vehicle: Dict[str, Any],
    coverage_type: str,
    baseline: Dict[str, Any],
    quotes: List[Dict[str, Any]],
    risk_score: float,
    **optional_inputs,
) -> str:
    """
    Log a detailed explanation of quick quote calculations to a markdown file.

    Args:
        state: State abbreviation
        zip_code: ZIP code
        age: Driver age
        marital_status: Marital status
        vehicle: Vehicle information dict
        coverage_type: Coverage type
        baseline: Baseline calculation dict
        quotes: List of carrier quotes
        risk_score: Calculated risk score
        **optional_inputs: Additional inputs like accidents, tickets, etc.

    Returns:
        Path to the generated explanation file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"quick_quote_{state}_{zip_code}_{timestamp}.md"
    filepath = QUOTE_EXPLANATIONS_DIR / filename

    with open(filepath, "w") as f:
        f.write("# Quick Quote Calculation Breakdown\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # Summary Table at the top
        f.write("## Quote Summary\n\n")
        f.write("| Carrier | Monthly Premium | Annual Premium |\n")
        f.write("|---------|-----------------|----------------|\n")
        for quote in quotes:
            carrier = quote["carrier"]
            monthly = f"${quote['monthly']:,}"
            annual = f"${quote['annual']:,}"
            f.write(f"| {carrier} | {monthly} | {annual} |\n")

        f.write(f"\n**Best Quote:** {quotes[0]['carrier']} at **${quotes[0]['monthly']:,}/month** (${quotes[0]['annual']:,}/year)\n")
        f.write(f"\n**Confidence Level:** {baseline['confidence']} (±{baseline['band']*100:.0f}%)\n\n")
        f.write("---\n\n")

        # Input Summary
        f.write("## Input Summary\n\n")
        f.write(f"- **State:** {state}\n")
        f.write(f"- **ZIP Code:** {zip_code}\n")
        f.write(f"- **Driver Age:** {age}\n")
        f.write(f"- **Marital Status:** {marital_status}\n")
        f.write(f"- **Vehicle:** {vehicle.get('year', 'N/A')} {vehicle.get('make', 'N/A')} {vehicle.get('model', 'N/A')}\n")
        f.write(f"- **Coverage Type:** {coverage_type}\n")

        # Optional inputs
        if optional_inputs:
            f.write("\n**Additional Inputs:**\n")
            for key, value in optional_inputs.items():
                f.write(f"- **{key}:** {value}\n")

        f.write("\n---\n\n")

        # Calculation Steps
        f.write("## Calculation Steps\n\n")

        # Step 1: Base Rate
        from insurance_server_python.pricing.config import STATE_BASE_FULL_COVERAGE_ANNUAL
        base_annual = STATE_BASE_FULL_COVERAGE_ANNUAL.get(
            state,
            STATE_BASE_FULL_COVERAGE_ANNUAL["DEFAULT"]
        )
        f.write("### 1. State Base Rate\n\n")
        f.write(f"- **Base Annual Premium for {state}:** ${base_annual:,}\n")
        f.write("- This is the average full coverage rate for the state\n\n")

        # Step 2: Calculate multipliers
        from insurance_server_python.pricing.factors import (
            calculate_age_factor,
            calculate_marital_factor,
            calculate_vehicle_factor,
            get_zip_multiplier,
            get_zip_description,
            calculate_coverage_factor,
        )

        age_mult, age_exp = calculate_age_factor(age)
        marital_mult, marital_exp = calculate_marital_factor(marital_status)
        vehicle_mult, vehicle_exp = calculate_vehicle_factor(
            year=vehicle.get("year", 2020),
            make=vehicle.get("make", "Honda"),
            model=vehicle.get("model", "Civic"),
        )
        zip_mult = get_zip_multiplier(zip_code)
        zip_desc = get_zip_description(zip_mult)
        coverage_mult, coverage_exp = calculate_coverage_factor(coverage_type)

        f.write("### 2. Risk Factors\n\n")
        f.write(f"#### Age Factor: **{age_mult:.2f}x**\n")
        f.write(f"- {age_exp}\n\n")

        f.write(f"#### Marital Status Factor: **{marital_mult:.2f}x**\n")
        f.write(f"- {marital_exp}\n\n")

        f.write(f"#### Vehicle Factor: **{vehicle_mult:.2f}x**\n")
        f.write(f"- {vehicle_exp}\n\n")

        f.write(f"#### ZIP Code Factor: **{zip_mult:.2f}x**\n")
        f.write(f"- ZIP {zip_code} - {zip_desc}\n\n")

        f.write(f"#### Coverage Factor: **{coverage_mult:.2f}x**\n")
        f.write(f"- {coverage_exp}\n\n")

        # Step 3: Baseline Calculation
        f.write("### 3. Baseline Premium Calculation\n\n")
        f.write("```\n")
        f.write("Baseline Annual = Base Rate × Age × Marital × Vehicle × ZIP × Coverage\n")
        f.write(f"                = ${base_annual:,} × {age_mult:.2f} × {marital_mult:.2f} × {vehicle_mult:.2f} × {zip_mult:.2f} × {coverage_mult:.2f}\n")
        f.write(f"                = ${baseline['annual']:,}\n")
        f.write("```\n\n")
        f.write(f"**Baseline Monthly:** ${baseline['monthly']:,}\n\n")

        # Step 4: Risk Score
        f.write("### 4. Overall Risk Score\n\n")
        f.write(f"- **Risk Score:** {risk_score:.3f} (scale: 0.0 = lowest risk, 1.0 = highest risk)\n")
        f.write("- This score is used to interpolate carrier-specific multipliers\n")
        f.write("- Lower risk profiles get better rates from each carrier\n\n")

        # Step 5: Confidence Band
        f.write("### 5. Confidence Band\n\n")
        f.write(f"- **Confidence Level:** {baseline['confidence']}\n")
        f.write(f"- **Band:** ±{baseline['band']*100:.0f}%\n")
        f.write("- Based on completeness of provided information\n\n")

        # Step 6: Carrier Quotes
        f.write("### 6. Carrier-Specific Quotes\n\n")

        from insurance_server_python.pricing.config import CARRIER_BASE_MULTIPLIERS, CARRIER_STATE_ADJUSTMENTS

        for i, quote in enumerate(quotes, 1):
            carrier = quote["carrier"]
            f.write(f"#### {i}. {carrier}\n\n")

            # Get carrier multiplier info
            multiplier_range = CARRIER_BASE_MULTIPLIERS.get(carrier, (1.00, 1.15))
            low_mult, high_mult = multiplier_range
            state_adj = CARRIER_STATE_ADJUSTMENTS.get(carrier, {}).get(state, 0.0)

            # Calculate actual multiplier used
            carrier_mult = low_mult + (high_mult - low_mult) * risk_score + state_adj

            f.write("**Carrier Multiplier Calculation:**\n")
            f.write("```\n")
            f.write(f"Base Range: {low_mult:.2f}x to {high_mult:.2f}x\n")
            f.write(f"Risk Interpolation: {low_mult:.2f} + ({high_mult:.2f} - {low_mult:.2f}) × {risk_score:.3f} = {low_mult + (high_mult - low_mult) * risk_score:.3f}x\n")
            if state_adj != 0.0:
                f.write(f"State Adjustment ({state}): {state_adj:+.3f}x\n")
            f.write(f"Final Multiplier: {carrier_mult:.3f}x\n")
            f.write("```\n\n")

            f.write("**Premium Calculation:**\n")
            f.write("```\n")
            f.write("Carrier Annual = Baseline × Carrier Multiplier\n")
            f.write(f"               = ${baseline['annual']:,} × {carrier_mult:.3f}\n")
            f.write(f"               = ${quote['annual']:,}\n")
            f.write(f"Carrier Monthly = ${quote['monthly']:,}\n")
            f.write("```\n\n")

            f.write("**Estimated Range:**\n")
            f.write(f"- Monthly: ${quote['range_monthly'][0]:,} - ${quote['range_monthly'][1]:,}\n")
            f.write(f"- Annual: ${quote['range_annual'][0]:,} - ${quote['range_annual'][1]:,}\n\n")

            f.write(f"**Explanation:** {quote['explanations'][-1]}\n\n")

        # Footer
        f.write("---\n\n")
        f.write("## Notes\n\n")
        f.write("All calculations are estimates based on typical market rates and risk factors. ")
        f.write("Actual rates from carriers may vary based on additional underwriting criteria.\n\n")
        f.write(f"**Price Spread:** ${quotes[-1]['monthly'] - quotes[0]['monthly']:,}/month ")
        f.write("(difference between highest and lowest quote)\n")

    logger.info(f"Quote explanation written to: {filepath}")
    return str(filepath)


def log_full_rate_calculation(
    request_payload: Dict[str, Any],
    response_data: Dict[str, Any],
    api_endpoint: str,
) -> str:
    """
    Log a detailed explanation of full rating API calculations to a markdown file.

    Args:
        request_payload: The full request sent to the rating API
        response_data: The response received from the rating API
        api_endpoint: The API endpoint used

    Returns:
        Path to the generated explanation file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Extract identifier if present
    identifier = request_payload.get("Identifier", "unknown")
    filename = f"full_rate_{identifier}_{timestamp}.md"
    filepath = QUOTE_EXPLANATIONS_DIR / filename

    with open(filepath, "w") as f:
        f.write("# Full Rating API Calculation Breakdown\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Quote Identifier:** `{identifier}`\n\n")

        # Summary Table at the top
        carrier_results = response_data.get("CarrierResults", [])
        if carrier_results:
            f.write("## Quote Summary\n\n")
            f.write("| Carrier | Program | Total Premium | Term | Down Payment | Monthly Payment |\n")
            f.write("|---------|---------|---------------|------|--------------|------------------|\n")

            for result in carrier_results:
                carrier_name = result.get("CarrierName", "Unknown")
                program_name = result.get("ProgramName") or result.get("ProductName", "Auto Program")
                total_premium = result.get("TotalPremium", 0)
                term = result.get("Term", "Term")

                # Get first installment option if available
                installments = result.get("Installments", [])
                down_payment = "N/A"
                monthly_payment = "N/A"
                if installments:
                    first_inst = installments[0]
                    down = first_inst.get("DownPayment", 0)
                    amount = first_inst.get("InstallmentAmount", 0)
                    down_payment = f"${down:,.2f}"
                    monthly_payment = f"${amount:,.2f}"

                f.write(f"| {carrier_name} | {program_name} | ${total_premium:,.2f} | {term} | {down_payment} | {monthly_payment} |\n")

            # Best quote highlight
            sorted_results = sorted(carrier_results, key=lambda x: x.get('TotalPremium', float('inf')))
            if sorted_results:
                lowest = sorted_results[0]
                highest = sorted_results[-1]
                f.write(f"\n**Best Quote:** {lowest.get('CarrierName')} - ${lowest.get('TotalPremium', 0):,.2f}\n")
                f.write(f"\n**Price Range:** ${lowest.get('TotalPremium', 0):,.2f} - ${highest.get('TotalPremium', 0):,.2f}\n")
                f.write(f"\n**Price Spread:** ${highest.get('TotalPremium', 0) - lowest.get('TotalPremium', 0):,.2f}\n\n")

            f.write("---\n\n")

        # API Info
        f.write("## API Request Details\n\n")
        f.write(f"- **Endpoint:** `{api_endpoint}`\n")
        f.write(f"- **Quote Identifier:** `{identifier}`\n\n")

        # Customer Info
        customer = request_payload.get("Customer", {})
        f.write("## Customer Information\n\n")
        f.write(f"- **Name:** {customer.get('FirstName', 'N/A')} {customer.get('LastName', 'N/A')}\n")

        address = customer.get("Address", {})
        if address:
            f.write(f"- **Address:** {address.get('Street1', 'N/A')}, {address.get('City', 'N/A')}, {address.get('State', 'N/A')} {address.get('ZipCode', 'N/A')}\n")

        f.write(f"- **Months at Residence:** {customer.get('MonthsAtResidence', 'N/A')}\n\n")

        # Prior Insurance
        prior = customer.get("PriorInsuranceInformation", {})
        if prior:
            f.write("**Prior Insurance:**\n")
            f.write(f"- Had Prior Insurance: {prior.get('PriorInsurance', 'N/A')}\n")
            if not prior.get('PriorInsurance'):
                f.write(f"- Reason: {prior.get('ReasonForNoInsurance', 'N/A')}\n")
        f.write("\n")

        # Drivers
        rated_drivers = request_payload.get("RatedDrivers", [])
        f.write(f"## Rated Drivers ({len(rated_drivers)})\n\n")
        for i, driver in enumerate(rated_drivers, 1):
            f.write(f"### Driver {i}\n\n")
            f.write(f"- **Name:** {driver.get('FirstName', 'N/A')} {driver.get('LastName', 'N/A')}\n")
            f.write(f"- **DOB:** {driver.get('DateOfBirth', 'N/A')}\n")
            f.write(f"- **Gender:** {driver.get('Gender', 'N/A')}\n")
            f.write(f"- **Marital Status:** {driver.get('MaritalStatus', 'N/A')}\n")

            license_info = driver.get("LicenseInformation", {})
            if license_info:
                f.write(f"- **License Status:** {license_info.get('LicenseStatus', 'N/A')}\n")
                f.write(f"- **Months Licensed:** {license_info.get('MonthsLicensed', 'N/A')}\n")
                f.write(f"- **State Licensed:** {license_info.get('StateLicensed', 'N/A')}\n")

            attributes = driver.get("Attributes", {})
            if attributes:
                f.write(f"- **Relation:** {attributes.get('Relation', 'N/A')}\n")
                f.write(f"- **Property Insurance:** {attributes.get('PropertyInsurance', 'N/A')}\n")
            f.write("\n")

        # Vehicles
        vehicles = request_payload.get("Vehicles", [])
        f.write(f"## Vehicles ({len(vehicles)})\n\n")
        for i, vehicle in enumerate(vehicles, 1):
            f.write(f"### Vehicle {i}\n\n")
            f.write(f"- **Year:** {vehicle.get('Year', 'N/A')}\n")
            f.write(f"- **Make:** {vehicle.get('Make', 'N/A')}\n")
            f.write(f"- **Model:** {vehicle.get('Model', 'N/A')}\n")
            f.write(f"- **VIN:** {vehicle.get('Vin', 'N/A')}\n")
            f.write(f"- **Usage:** {vehicle.get('Usage', 'N/A')}\n")

            coverage = vehicle.get("CoverageInformation", {})
            if coverage:
                f.write(f"- **Collision Deductible:** {coverage.get('CollisionDeductible', 'N/A')}\n")
                f.write(f"- **Comprehensive Deductible:** {coverage.get('ComprehensiveDeductible', 'N/A')}\n")
            f.write("\n")

        # Policy Coverages
        policy_coverages = request_payload.get("PolicyCoverages", {})
        f.write("## Policy Coverages\n\n")
        f.write(f"- **Bodily Injury Limit:** {policy_coverages.get('LiabilityBiLimit', 'N/A')}\n")
        f.write(f"- **Property Damage Limit:** {policy_coverages.get('LiabilityPdLimit', 'N/A')}\n")
        f.write(f"- **Med Pay Limit:** {policy_coverages.get('MedPayLimit', 'N/A')}\n")
        f.write(f"- **Uninsured Motorist BI Limit:** {policy_coverages.get('UninsuredMotoristBiLimit', 'N/A')}\n\n")

        # Policy Details
        f.write("## Policy Details\n\n")
        f.write(f"- **Effective Date:** {request_payload.get('EffectiveDate', 'N/A')}\n")
        f.write(f"- **Term:** {request_payload.get('Term', 'N/A')}\n")
        f.write(f"- **Payment Method:** {request_payload.get('PaymentMethod', 'N/A')}\n")
        f.write(f"- **Policy Type:** {request_payload.get('PolicyType', 'N/A')}\n\n")

        # Response - Carrier Results
        f.write("---\n\n")
        f.write("## Rating Results\n\n")

        carrier_results = response_data.get("CarrierResults", [])
        if carrier_results:
            f.write(f"### Carrier Quotes ({len(carrier_results)})\n\n")

            for i, result in enumerate(carrier_results, 1):
                carrier_name = result.get("CarrierName", "Unknown")
                program_name = result.get("ProgramName") or result.get("ProductName", "Auto Program")

                f.write(f"#### {i}. {carrier_name} - {program_name}\n\n")
                f.write(f"**Total Premium:** ${result.get('TotalPremium', 0):,.2f} / {result.get('Term', 'Term')}\n\n")

                # Coverage details
                f.write("**Coverage Limits:**\n")
                f.write(f"- Bodily Injury: {result.get('BodilyInjuryLimit', 'N/A')}\n")
                f.write(f"- Property Damage: {result.get('PropertyDamageLimit', 'N/A')}\n")
                if result.get('UninsuredMotoristLimit'):
                    f.write(f"- Uninsured Motorist: {result.get('UninsuredMotoristLimit')}\n")
                f.write("\n")

                # Payment options
                installments = result.get("Installments", [])
                if installments:
                    f.write("**Payment Options:**\n")
                    for inst in installments:
                        down = inst.get("DownPayment", 0)
                        amount = inst.get("InstallmentAmount", 0)
                        count = inst.get("InstallmentCount", 0)
                        f.write(f"- ${down:,.2f} down + ${amount:,.2f} × {count} payments\n")
                    f.write("\n")

                # Quote ID
                if result.get("QuoteId"):
                    f.write(f"**Quote ID:** `{result.get('QuoteId')}`\n\n")
        else:
            f.write("*No carrier results returned*\n\n")

        # Errors
        if response_data.get("Errors"):
            f.write("### Errors\n\n")
            for error in response_data.get("Errors", []):
                f.write(f"- {error}\n")
            f.write("\n")

        # Footer
        f.write("---\n\n")
        f.write("## Notes\n\n")
        f.write("This breakdown shows the complete request and response from the rating API. ")
        f.write("The actual premium calculations are performed by the carrier's rating engine based on ")
        f.write("their proprietary algorithms and risk models.\n")

    logger.info(f"Full rate explanation written to: {filepath}")
    return str(filepath)


def cleanup_old_explanations(days_to_keep: int = 7):
    """
    Clean up old quote explanation files.

    Args:
        days_to_keep: Number of days to keep files (default: 7)
    """
    import time

    now = time.time()
    cutoff = now - (days_to_keep * 86400)  # 86400 seconds in a day

    deleted_count = 0
    for filepath in QUOTE_EXPLANATIONS_DIR.glob("*.md"):
        if filepath.stat().st_mtime < cutoff:
            filepath.unlink()
            deleted_count += 1

    if deleted_count > 0:
        logger.info(f"Cleaned up {deleted_count} old quote explanation files")
