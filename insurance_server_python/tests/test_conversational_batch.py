"""Tests for conversational batch collection tools."""

import pytest
from insurance_server_python.tool_handlers import (
    _collect_personal_auto_customer,
    _collect_personal_auto_drivers,
    _collect_personal_auto_vehicles,
)


def test_collect_customer_complete():
    """Test customer collection with all required fields."""
    arguments = {
        "Customer": {
            "FirstName": "John",
            "LastName": "Smith",
            "Address": {
                "Street1": "123 Main St",
                "City": "San Francisco",
                "State": "CA",
                "ZipCode": "94102",
            },
            "MonthsAtResidence": 24,
            "PriorInsuranceInformation": {
                "PriorInsurance": True,
            },
        }
    }

    result = _collect_personal_auto_customer(arguments)

    assert "structured_content" in result
    assert "validation" in result["structured_content"]
    assert result["structured_content"]["validation"]["customer_complete"] is True
    assert len(result["structured_content"]["validation"]["missing_fields"]) == 0
    assert "John Smith" in result["response_text"]


def test_collect_customer_missing_fields():
    """Test customer collection with missing required fields."""
    arguments = {
        "Customer": {
            "FirstName": "John",
            "LastName": "Smith",
            "Address": {
                "City": "San Francisco",
                "State": "CA",
            },
            # Missing: Street1, ZipCode, MonthsAtResidence, PriorInsurance
        }
    }

    result = _collect_personal_auto_customer(arguments)

    assert "structured_content" in result
    assert "validation" in result["structured_content"]
    assert result["structured_content"]["validation"]["customer_complete"] is False

    missing = result["structured_content"]["validation"]["missing_fields"]
    assert "Address.Street1" in missing
    assert "Address.ZipCode" in missing
    assert "MonthsAtResidence" in missing
    assert "PriorInsuranceInformation.PriorInsurance" in missing
    assert "Still need:" in result["response_text"]


def test_collect_driver_complete():
    """Test driver collection with all required fields."""
    arguments = {
        "RatedDrivers": [
            {
                "FirstName": "John",
                "LastName": "Smith",
                "DateOfBirth": "1980-01-01",
                "Gender": "Male",
                "MaritalStatus": "Married",
                "LicenseInformation": {
                    "LicenseStatus": "Valid",
                },
                "Attributes": {
                    "PropertyInsurance": True,
                    "Relation": "Insured",
                    "ResidencyStatus": "Own",
                    "ResidencyType": "Home",
                },
            }
        ]
    }

    result = _collect_personal_auto_drivers(arguments)

    assert "structured_content" in result
    assert "validation" in result["structured_content"]
    assert result["structured_content"]["validation"]["drivers_complete"] is True
    assert len(result["structured_content"]["validation"]["missing_fields"]) == 0
    assert "John Smith" in result["response_text"]


def test_collect_driver_with_customer_append():
    """Test driver collection with customer field appending."""
    arguments = {
        "Customer": {
            "FirstName": "John",
            "LastName": "Smith",
            "Address": {
                "Street1": "123 Main St",
                "City": "San Francisco",
                "State": "CA",
                "ZipCode": "94102",
            },
            # Missing: MonthsAtResidence, PriorInsurance
        },
        "RatedDrivers": [
            {
                "FirstName": "John",
                "LastName": "Smith",
                "DateOfBirth": "1980-01-01",
                "Gender": "Male",
                "MaritalStatus": "Married",
                "LicenseInformation": {
                    "LicenseStatus": "Valid",
                },
                "Attributes": {
                    "PropertyInsurance": True,
                    "Relation": "Insured",
                    "ResidencyStatus": "Own",
                    "ResidencyType": "Home",
                },
            }
        ],
    }

    result = _collect_personal_auto_drivers(arguments)

    assert "structured_content" in result
    assert "customer" in result["structured_content"]
    assert "validation" in result["structured_content"]

    # Driver is complete, but customer fields are missing
    assert result["structured_content"]["validation"]["drivers_complete"] is True
    assert result["structured_content"]["validation"]["customer_complete"] is False

    missing = result["structured_content"]["validation"]["missing_fields"]
    assert "MonthsAtResidence" in missing
    assert "PriorInsuranceInformation.PriorInsurance" in missing


def test_collect_vehicle_complete():
    """Test vehicle collection with all required fields."""
    arguments = {
        "Vehicles": [
            {
                "Vin": "1HGCV1F3XLA123456",
                "Year": 2020,
                "Make": "Honda",
                "Model": "Accord",
                "BodyType": "Sedan",
                "UseType": "Commute",
                "AssignedDriverId": "driver-1",
                "CoverageInformation": {
                    "CollisionDeductible": "500",
                    "ComprehensiveDeductible": "500",
                    "RentalLimit": "50",
                    "TowingLimit": "100",
                    "SafetyGlassCoverage": True,
                },
                "PercentToWork": 80,
                "MilesToWork": 20,
                "AnnualMiles": 12000,
            }
        ]
    }

    result = _collect_personal_auto_vehicles(arguments)

    assert "structured_content" in result
    assert "validation" in result["structured_content"]
    assert result["structured_content"]["validation"]["vehicles_complete"] is True
    assert len(result["structured_content"]["validation"]["missing_fields"]) == 0
    assert "Honda Accord" in result["response_text"]


def test_collect_vehicle_missing_coverage():
    """Test vehicle collection with missing coverage fields."""
    arguments = {
        "Vehicles": [
            {
                "Vin": "1HGCV1F3XLA123456",
                "Year": 2020,
                "Make": "Honda",
                "Model": "Accord",
                "BodyType": "Sedan",
                "UseType": "Commute",
                "AssignedDriverId": "driver-1",
                "CoverageInformation": {
                    "CollisionDeductible": "500",
                    # Missing: ComprehensiveDeductible, RentalLimit, TowingLimit, SafetyGlassCoverage
                },
                "PercentToWork": 80,
                "MilesToWork": 20,
                "AnnualMiles": 12000,
            }
        ]
    }

    result = _collect_personal_auto_vehicles(arguments)

    assert "structured_content" in result
    assert "validation" in result["structured_content"]
    assert result["structured_content"]["validation"]["vehicles_complete"] is False

    missing = result["structured_content"]["validation"]["missing_fields"]
    assert any("ComprehensiveDeductible" in m for m in missing)
    assert any("RentalLimit" in m for m in missing)
