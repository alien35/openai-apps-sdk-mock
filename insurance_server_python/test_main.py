"""Unit tests for insurance server helpers."""

import unittest

from insurance_server_python.main import (
    PURCHASE_TYPE_MAPPINGS,
    _sanitize_personal_auto_rate_request,
)


class PurchaseTypeNormalizationTests(unittest.TestCase):
    """Verify vehicle purchase type normalization behavior."""

    def test_owned_outright_alias_present(self) -> None:
        """The owned outright alias should normalize to the canonical value."""

        self.assertEqual(PURCHASE_TYPE_MAPPINGS["ownedoutright"], "Owned")

    def test_sanitize_applies_owned_outright_alias(self) -> None:
        """Sanitizing a request should normalize the owned outright alias."""

        request_body = {"Vehicles": [{"PurchaseType": "OwnedOutright"}]}

        _sanitize_personal_auto_rate_request(request_body)

        vehicles = request_body["Vehicles"]
        self.assertIsInstance(vehicles, list)
        self.assertGreater(len(vehicles), 0)
        self.assertEqual(vehicles[0]["PurchaseType"], "Owned")


if __name__ == "__main__":
    unittest.main()
