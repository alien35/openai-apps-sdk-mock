import unittest
from copy import deepcopy
from uuid import UUID

from insurance_server_python.main import (
    PersonalAutoRateResultsRequest,
    _sanitize_personal_auto_rate_request,
    generate_quote_identifier,
)


class GenerateQuoteIdentifierTests(unittest.TestCase):
    def test_returns_uuid_uppercase_string(self) -> None:
        identifier = generate_quote_identifier()

        parsed = UUID(identifier)
        self.assertEqual(identifier, identifier.upper())
        self.assertEqual(str(parsed), identifier.lower())

    def test_accepts_optional_now_parameter(self) -> None:
        """The optional ``now`` parameter remains for compatibility."""

        identifier = generate_quote_identifier(now=None)
        self.assertEqual(identifier, identifier.upper())
        UUID(identifier)


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

    def test_normalizes_all_license_status_enums(self) -> None:
        statuses = {
            "Valid": ("Valid", "valid", "ACTIVE"),
            "Unlicensed": ("Unlicensed", "unlicensed", "no license"),
            "Permit": ("Permit", "permit", "learner permit"),
            "Expired": ("Expired", "expired"),
            "Revoked": ("Revoked", "revoked"),
            "Suspended": ("Suspended", "suspended"),
        }

        for expected, inputs in statuses.items():
            for status in inputs:
                with self.subTest(status=status, expected=expected):
                    request_body = {
                        "RatedDrivers": [
                            {"LicenseInformation": {"LicenseStatus": status}},
                        ]
                    }

                    _sanitize_personal_auto_rate_request(request_body)

                    license_info = request_body["RatedDrivers"][0]["LicenseInformation"]
                    self.assertEqual(license_info["LicenseStatus"], expected)

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
            {"Identifier": "550e8400-e29b-41d4-a716-446655440000"}
        )
        self.assertEqual(
            request.identifier, "550e8400-e29b-41d4-a716-446655440000"
        )

        alternate = PersonalAutoRateResultsRequest.model_validate(
            {"Id": "8a1d6956-5c43-4a0d-9b5d-9058f36502cd"}
        )
        self.assertEqual(
            alternate.identifier, "8a1d6956-5c43-4a0d-9b5d-9058f36502cd"
        )

    def test_strips_identifier_value(self) -> None:
        request = PersonalAutoRateResultsRequest.model_validate(
            {"Identifier": "  0de7c3bd-1b6a-4cda-8f6c-715f9c03d0be  "}
        )
        self.assertEqual(
            request.identifier, "0de7c3bd-1b6a-4cda-8f6c-715f9c03d0be"
        )


if __name__ == "__main__":  # pragma: no cover - convenience for direct execution
    unittest.main()
