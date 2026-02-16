import unittest
from insurance_server_python.utils import format_rate_results_summary

class TestQuoteContext(unittest.TestCase):
    def test_format_rate_results_summary_pascal_case(self):
        mock_results = {
            "CarrierResults": [
                {
                    "CarrierName": "SafeAuto",
                    "ProgramName": "Gold Plan",
                    "TotalPremium": 1200.50,
                    "Term": "6 Months",
                    "BodilyInjuryLimit": "100/300",
                    "PropertyDamageLimit": "50000",
                    "Installments": [
                        {
                            "DownPayment": 200.00,
                            "InstallmentAmount": 166.75,
                            "InstallmentCount": 6
                        }
                    ]
                },
                {
                    "CarrierName": "BudgetInsure",
                    "ProductName": "Basic",
                    "TotalPremium": 800.00,
                    "TermDescription": "6 Months",
                    "BodilyInjuryLimit": "25/50",
                    "UninsuredMotoristLimit": None
                }
            ]
        }

        summary = format_rate_results_summary(mock_results)
        print(f"\nGenerated Summary (PascalCase):\n{summary}")

        self.assertIn("- SafeAuto (Gold Plan): $1,200.50 / 6 Months", summary)
        self.assertIn("Coverages: BI: 100/300, PD: 50000", summary)
        self.assertIn("Payment Options: $200.00 down + $166.75 x 6", summary)
        
        self.assertIn("- BudgetInsure (Basic): $800.00 / 6 Months", summary)
        self.assertIn("Coverages: BI: 25/50", summary)

    def test_format_rate_results_summary_camel_case(self):
        mock_results = {
            "carrierResults": [
                {
                    "carrierName": "SafeAuto",
                    "programName": "Gold Plan",
                    "totalPremium": 1200.50,
                    "term": "6 Months",
                    "bodilyInjuryLimit": "100/300",
                    "propertyDamageLimit": "50000",
                    "installments": [
                        {
                            "downPayment": 200.00,
                            "installmentAmount": 166.75,
                            "installmentCount": 6
                        }
                    ]
                },
                {
                    "carrierName": "BudgetInsure",
                    "productName": "Basic",
                    "totalPremium": 800.00,
                    "termDescription": "6 Months",
                    "bodilyInjuryLimit": "25/50",
                    "uninsuredMotoristLimit": None
                }
            ]
        }

        summary = format_rate_results_summary(mock_results)
        print(f"\nGenerated Summary (camelCase):\n{summary}")

        self.assertIn("- SafeAuto (Gold Plan): $1,200.50 / 6 Months", summary)
        self.assertIn("Coverages: BI: 100/300, PD: 50000", summary)
        self.assertIn("Payment Options: $200.00 down + $166.75 x 6", summary)

if __name__ == '__main__':
    unittest.main()
