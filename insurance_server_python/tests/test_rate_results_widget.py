import json
import subprocess
from pathlib import Path
from typing import Any, Dict

import pytest


WIDGET_PATH = Path(__file__).resolve().parent.parent / "insurance_rate_results_widget.py"


def _run_aggregator(sample: Dict[str, Any]) -> Dict[str, Any]:
    script = f"""
const fs = require('fs');
const vm = require('vm');
const source = fs.readFileSync({json.dumps(str(WIDGET_PATH))}, 'utf8');
const start = source.indexOf('<script>');
const end = source.indexOf('</script>');
if (start === -1 || end === -1) throw new Error('Script tag not found');
const code = source.slice(start + '<script>'.length, end);
const sandbox = {{
  window: {{
    openai: {{}},
    addEventListener: () => {{}},
  }},
  document: {{
    getElementById: () => null,
  }},
  console: console,
  Intl: Intl,
  setTimeout: () => {{}},
  clearTimeout: () => {{}},
}};
sandbox.window.dispatchEvent = () => {{}};
sandbox.global = sandbox;
sandbox.globalThis = sandbox;
sandbox.self = sandbox;
vm.createContext(sandbox);
vm.runInContext(code, sandbox);
const api = sandbox.window.__RATE_RESULTS_WIDGET_TESTING__;
if (!api) throw new Error('Testing API unavailable');
const result = api.aggregateRatePrograms({json.dumps(sample)});
console.log(JSON.stringify(result));
"""
    completed = subprocess.run(
        ["node", "-e", script],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def _sample_rate_results() -> Dict[str, Any]:
    def program_records(program: str, total: float, down: float, monthly: float, invoice: float, add_on: float | None, miles: int) -> list[Dict[str, Any]]:
        base = {
            "CarrierName": "Anchor",
            "ProgramName": program,
            "TermMonths": 6,
            "TotalPremium": total,
            "BodilyInjuryLimit": "30/60",
            "PropertyDamageLimit": "15",
            "UninsuredMotoristLimit": "30/60",
            "PolicyFee": 39.6,
            "BodilyInjuryPremium": round(total * 0.29, 2),
            "PropertyDamagePremium": round(total * 0.64, 2),
            "UninsuredMotoristPremium": round(total * 0.04, 2),
            "Warnings": [f"Assumes {miles:,} miles"],
        }
        if add_on:
            base["TravelClubPremium" if "Gemini" in program else "MotoristProtectionPremium"] = add_on
        records = [
            {
                **base,
                "PlanName": "Full Pay",
                "PaymentMethod": "Invoice",
                "DownPayment": total,
                "InstallmentCount": 0,
            },
            {
                **base,
                "PlanName": "Monthly Card",
                "PaymentMethod": "Credit Card",
                "DownPayment": down,
                "InstallmentCount": 5,
                "InstallmentAmount": monthly,
            },
            {
                **base,
                "PlanName": "Monthly EFT",
                "PaymentMethod": "Electronic Funds Transfer",
                "DownPayment": down,
                "InstallmentCount": 5,
                "InstallmentAmount": monthly,
            },
            {
                **base,
                "PlanName": "Monthly Invoice",
                "PaymentMethod": "Invoice",
                "DownPayment": down,
                "InstallmentCount": 5,
                "InstallmentAmount": invoice,
            },
        ]
        return records

    results: list[Dict[str, Any]] = []
    results.extend(program_records("Anchor Premier", 1993.48, 366.03, 335.09, 341.09, None, 3500))
    results.extend(program_records("Anchor Gemini RT", 2103.48, 384.38, 353.42, 359.42, 24.0, 8000))
    results.extend(program_records("Anchor Motor Club", 2275.48, 413.03, 382.09, 388.09, 54.0, 8000))
    return {"rate_results": results}


@pytest.mark.skipif(subprocess.run(["node", "-v"], capture_output=True, text=True).returncode != 0, reason="Node required")
def test_aggregator_groups_products_and_calculates_fees() -> None:
    data = _sample_rate_results()
    result = _run_aggregator(data)
    products = result["products"]

    assert len(products) == 3

    premier = next(product for product in products if product["programName"] == "Anchor Premier")
    monthly_card = premier["plans"]["monthly_card"]
    monthly_invoice = premier["plans"]["monthly_invoice"]

    assert pytest.approx(monthly_card["installmentFees"], rel=1e-4) == 48.0
    assert pytest.approx(monthly_invoice["installmentFees"], rel=1e-4) == 78.0
    assert len(premier["planOrder"]) == 4

    shared = result["shared"]
    assert shared["coverage"]["bi"] == "30/60"
    assert shared["coverage"]["pd"] == "15"
    assert shared["coverage"]["um"] == "30/60"

    gemini = next(product for product in products if product["programName"] == "Anchor Gemini RT")
    assert gemini["summary"]["monthlySavings"] == pytest.approx(30.0, rel=1e-4)

    assert premier["planOrder"].count("monthly_card") == 1
