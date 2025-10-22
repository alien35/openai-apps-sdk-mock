import unittest
from copy import deepcopy

from insurance_server_python.main import (
    PersonalAutoRateResultsRequest,
    _sanitize_personal_auto_rate_request,
)


class PersonalAutoRateRequestSanitizationTests(unittest.TestCase):
    def test_normalizes_license_status_synonyms(self) -> None:
        for status in ("licensed", "full", "full license", "Valid"):
            with self.subTest(status=status):
                request_body = {
                    "RatedDrivers": [
                        {"LicenseInformation": {"LicenseStatus": status}},
                    ]
                }

                _sanitize_personal_auto_rate_request(request_body)

                license_info = request_body["RatedDrivers"][0]["LicenseInformation"]
                self.assertEqual(license_info["LicenseStatus"], "Valid")

    def test_defaults_license_status_when_missing(self) -> None:
        cases = (
            {"LicenseInformation": {}},
            {"LicenseInformation": {"LicenseStatus": None}},
            {"LicenseInformation": {"LicenseStatus": "   "}},
        )

        for case in cases:
            with self.subTest(case=case):
                request_body = {"RatedDrivers": [deepcopy(case)]}

                _sanitize_personal_auto_rate_request(request_body)

                license_info = request_body["RatedDrivers"][0]["LicenseInformation"]
                self.assertEqual(license_info["LicenseStatus"], "Valid")


class PersonalAutoRateResultsRequestTests(unittest.TestCase):
    def test_accepts_identifier_aliases(self) -> None:
        request = PersonalAutoRateResultsRequest.model_validate(
            {"Identifier": "QUOTE-001"}
        )
        self.assertEqual(request.identifier, "QUOTE-001")

        alternate = PersonalAutoRateResultsRequest.model_validate({"Id": "QUOTE-002"})
        self.assertEqual(alternate.identifier, "QUOTE-002")

    def test_strips_identifier_value(self) -> None:
        request = PersonalAutoRateResultsRequest.model_validate(
            {"Identifier": "  QUOTE-003  "}
        )
        self.assertEqual(request.identifier, "QUOTE-003")


if __name__ == "__main__":  # pragma: no cover - convenience for direct execution
    unittest.main()
