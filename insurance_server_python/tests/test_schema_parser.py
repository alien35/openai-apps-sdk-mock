"""Tests for schema parser and minimal fields functionality."""

import unittest
from unittest.mock import AsyncMock, patch
import json
import os


class TestSchemaParser(unittest.IsolatedAsyncioTestCase):
    """Tests for the SchemaParser class."""

    async def test_fetch_contract_success(self):
        """Test successful contract fetching."""
        from insurance_server_python.schema_parser import SchemaParser
        from unittest.mock import MagicMock

        # Mock the HTTP response
        contract_data = [{
            "id": "test-id",
            "lineOfBusiness": "PersonalAuto",
            "state": "CA",
            "version": "2023.03.01",
            "contract": {
                "$schema": "http://json-schema.org/draft/2020-12/schema#",
                "definitions": {
                    "Customer": {
                        "type": "object",
                        "required": ["FirstName", "LastName", "Address"],
                        "properties": {
                            "FirstName": {"type": "string"},
                            "LastName": {"type": "string"},
                            "Address": {"$ref": "#/definitions/Address"}
                        }
                    },
                    "Address": {
                        "type": "object",
                        "required": ["Street1", "City", "State", "ZipCode"],
                        "properties": {
                            "Street1": {"type": "string"},
                            "City": {"type": "string"},
                            "State": {"type": "string"},
                            "ZipCode": {"type": "string"}
                        }
                    }
                }
            }
        }]

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = contract_data
        mock_response.raise_for_status = MagicMock()

        parser = SchemaParser("test-api-key")

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            contract = await parser.fetch_contract("CA")

        self.assertIn("definitions", contract)
        self.assertIn("Customer", contract["definitions"])

    def test_get_required_fields(self):
        """Test extraction of required fields from schema."""
        from insurance_server_python.schema_parser import SchemaParser

        schema = {
            "type": "object",
            "required": ["FirstName", "LastName"],
            "properties": {
                "FirstName": {
                    "type": "string",
                    "description": "First name"
                },
                "LastName": {
                    "type": "string",
                    "description": "Last name"
                },
                "MiddleName": {
                    "type": "string",
                    "description": "Middle name"
                }
            }
        }

        parser = SchemaParser("test-api-key")
        required = parser.get_required_fields(schema)

        self.assertIn("FirstName", required)
        self.assertIn("LastName", required)
        self.assertNotIn("MiddleName", required)
        self.assertEqual(required["FirstName"]["type"], "string")
        self.assertEqual(required["FirstName"]["description"], "First name")


class TestFieldDefaults(unittest.TestCase):
    """Tests for field defaults functionality."""

    def test_apply_customer_defaults(self):
        """Test applying defaults to customer data."""
        from insurance_server_python.field_defaults import apply_customer_defaults

        customer = {
            "FirstName": "John",
            "LastName": "Doe",
            "Address": {
                "Street1": "123 Main St",
                "City": "San Francisco",
                "State": "CA",
                "ZipCode": "94105"
            },
            "MonthsAtResidence": 24
        }

        result = apply_customer_defaults(customer)

        self.assertEqual(result["FirstName"], "John")
        self.assertEqual(result["DeclinedEmail"], False)
        self.assertEqual(result["CustomerDeclinedCredit"], False)
        self.assertIn("ContactInformation", result)

    def test_apply_driver_defaults(self):
        """Test applying defaults to driver data."""
        from insurance_server_python.field_defaults import apply_driver_defaults

        driver = {
            "FirstName": "Jane",
            "LastName": "Doe",
            "DateOfBirth": "1990-01-01",
            "Gender": "Female",
            "MaritalStatus": "Single",
            "LicenseInformation": {
                "LicenseStatus": "Valid",
                "MonthsLicensed": 120,
                "StateLicensed": "CA"
            },
            "Attributes": {
                "PropertyInsurance": True,
                "Relation": "Insured",
                "ResidencyStatus": "Own",
                "ResidencyType": "Home"
            }
        }

        result = apply_driver_defaults(driver)

        self.assertEqual(result["FirstName"], "Jane")
        self.assertIn("Discounts", result)
        self.assertIn("FinancialResponsibilityInformation", result)
        self.assertIn("Violations", result)
        self.assertEqual(result["Discounts"]["DriversTraining"], False)
        self.assertEqual(result["FinancialResponsibilityInformation"]["Sr22"], False)

    def test_apply_vehicle_defaults(self):
        """Test applying defaults to vehicle data."""
        from insurance_server_python.field_defaults import apply_vehicle_defaults

        vehicle = {
            "VehicleId": 1,
            "Vin": "1HGCM82633A123456",
            "Year": 2020,
            "Make": "Honda",
            "Model": "Accord",
            "BodyType": "Sedan",
            "UseType": "Commute",
            "AssignedDriverId": 1,
            "MilesToWork": 10,
            "AnnualMiles": 12000
        }

        result = apply_vehicle_defaults(vehicle)

        self.assertEqual(result["Vin"], "1HGCM82633A123456")
        self.assertIn("CoverageInformation", result)
        self.assertEqual(result["CoverageInformation"]["CollisionDeductible"], "None")
        # Verify essential vehicle defaults
        self.assertEqual(result["LeasedVehicle"], False)
        self.assertEqual(result["RideShare"], False)
        self.assertEqual(result["Salvaged"], False)

    def test_build_minimal_payload_with_defaults(self):
        """Test building complete payload with defaults."""
        from insurance_server_python.field_defaults import build_minimal_payload_with_defaults

        customer = {
            "FirstName": "John",
            "LastName": "Doe",
            "Address": {
                "Street1": "123 Main St",
                "City": "San Francisco",
                "State": "CA",
                "ZipCode": "94105"
            },
            "MonthsAtResidence": 24,
            "PriorInsuranceInformation": {
                "PriorInsurance": False,
                "ReasonForNoInsurance": "No Reason Given"
            }
        }

        drivers = [{
            "DriverId": 1,
            "FirstName": "John",
            "LastName": "Doe",
            "DateOfBirth": "1980-01-01",
            "Gender": "Male",
            "MaritalStatus": "Married",
            "LicenseInformation": {
                "LicenseStatus": "Valid",
                "MonthsLicensed": 300,
                "StateLicensed": "CA"
            },
            "Attributes": {
                "PropertyInsurance": True,
                "Relation": "Insured",
                "ResidencyStatus": "Own",
                "ResidencyType": "Home"
            }
        }]

        vehicles = [{
            "VehicleId": 1,
            "Vin": "1HGCM82633A123456",
            "Year": 2020,
            "Make": "Honda",
            "Model": "Accord",
            "BodyType": "Sedan",
            "UseType": "Commute",
            "AssignedDriverId": 1,
            "MilesToWork": 10,
            "AnnualMiles": 12000,
            "PercentToWork": 50,
            "CoverageInformation": {
                "CollisionDeductible": "500",
                "ComprehensiveDeductible": "500",
                "RentalLimit": "30",
                "TowingLimit": "50",
                "SafetyGlassCoverage": True
            }
        }]

        policy_coverages = {
            "LiabilityBiLimit": "50000/100000",
            "LiabilityPdLimit": "50000",
            "MedPayLimit": "5000",
            "UninsuredMotoristBiLimit": "50000/100000",
            "UninsuredMotoristPd/CollisionDamageWaiver": False,
            "AccidentalDeathLimit": "10000"
        }

        payload = build_minimal_payload_with_defaults(
            customer=customer,
            drivers=drivers,
            vehicles=vehicles,
            policy_coverages=policy_coverages,
            identifier="quote-test-123",
            effective_date="2026-03-01T00:00:00",
            state="CA"
        )

        # Verify top-level fields
        self.assertEqual(payload["Identifier"], "quote-test-123")
        self.assertEqual(payload["EffectiveDate"], "2026-03-01T00:00:00")

        # Verify customer with defaults
        self.assertEqual(payload["Customer"]["FirstName"], "John")
        self.assertEqual(payload["Customer"]["DeclinedEmail"], False)
        self.assertIn("ContactInformation", payload["Customer"])

        # Verify drivers with defaults
        self.assertEqual(len(payload["RatedDrivers"]), 1)
        self.assertIn("Discounts", payload["RatedDrivers"][0])
        self.assertIn("Violations", payload["RatedDrivers"][0])

        # Verify vehicles with defaults
        self.assertEqual(len(payload["Vehicles"]), 1)
        self.assertEqual(payload["Vehicles"][0]["LeasedVehicle"], False)
        self.assertEqual(payload["Vehicles"][0]["RideShare"], False)
        self.assertEqual(payload["Vehicles"][0]["Salvaged"], False)

        # Verify policy coverages
        self.assertEqual(payload["PolicyCoverages"]["LiabilityBiLimit"], "50000/100000")

        # Verify policy defaults
        self.assertEqual(payload["BumpLimits"], "No Bumping")
        self.assertEqual(payload["Term"], "Semi Annual")


if __name__ == "__main__":
    unittest.main()
