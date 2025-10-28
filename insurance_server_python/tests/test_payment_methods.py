import unittest

from insurance_server_python.main import (
    _sanitize_personal_auto_rate_request,
    _normalize_enum_value,
    PAYMENT_METHOD_MAPPINGS,
)


class PaymentMethodMappingsTests(unittest.TestCase):
    def test_aliases_normalize_to_electronic_funds_transfer(self) -> None:
        aliases = [
            "Electronic Fund Transfer",
            "electronic fund transfer",
            "ELECTRONIC FUND TRANSFER",
            "Electronic Fund Transfers",
            "Electronic Funds Transfers",
            "ElectronicFundsTransfer",
        ]

        for alias in aliases:
            with self.subTest(alias=alias):
                normalized = _normalize_enum_value(alias, PAYMENT_METHOD_MAPPINGS)
                self.assertEqual(normalized, "Electronic Funds Transfer")

    def test_sanitize_defaults_payment_method_when_missing(self) -> None:
        request_body = {
            "EffectiveDate": "2025-01-01",
            "Customer": {},
            "RatedDrivers": [],
            "Vehicles": [],
        }

        _sanitize_personal_auto_rate_request(request_body)

        self.assertEqual(request_body["PaymentMethod"], "Default")

    def test_invoice_like_values_normalize_to_standard(self) -> None:
        aliases = [
            "Invoice",
            "invoice",
            "Paper",
            "Card",
            "Agency Bill",
        ]

        for alias in aliases:
            with self.subTest(alias=alias):
                normalized = _normalize_enum_value(alias, PAYMENT_METHOD_MAPPINGS)
                self.assertEqual(normalized, "Standard")


if __name__ == "__main__":
    unittest.main()
