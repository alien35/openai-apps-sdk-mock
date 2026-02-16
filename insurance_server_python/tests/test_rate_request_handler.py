import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import json

from insurance_server_python.tool_handlers import _request_personal_auto_rate

class TestRateRequestHandler(unittest.IsolatedAsyncioTestCase):
    @patch("insurance_server_python.tool_handlers.httpx.AsyncClient")
    @patch("insurance_server_python.tool_handlers._log_network_request")
    @patch("insurance_server_python.tool_handlers._log_network_response")
    async def test_request_personal_auto_rate_includes_identifier(
        self, mock_log_resp, mock_log_req, mock_client_cls
    ):
        # Setup mocks
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        
        # Mock submission response (transaction ID)
        mock_submit_response = MagicMock()
        mock_submit_response.status_code = 200
        mock_submit_response.text = '{"transactionId": "txn-123"}'
        mock_submit_response.json.return_value = {"transactionId": "txn-123"}
        mock_submit_response.is_error = False

        # Mock results retrieval response (rate results)
        mock_results_response = MagicMock()
        mock_results_response.status_code = 200
        mock_results_response.text = '{"carrierResults": []}'
        mock_results_response.json.return_value = {"carrierResults": []}
        mock_results_response.is_error = False

        # Configure client to return submission then results
        mock_client.post.return_value = mock_submit_response
        mock_client.get.return_value = mock_results_response

        # Input arguments
        arguments = {
            "Identifier": "quote-123456789",
            "EffectiveDate": "2026-06-01T00:00:00",
            "Customer": {
                "Identifier": "cust-1",
                "FirstName": "John",
                "LastName": "Doe",
                "Address": {
                    "Street1": "123 Main St",
                    "City": "San Francisco",
                    "State": "CA",
                    "ZipCode": "94105"
                }
            },
            "PolicyCoverages": {},
            "Vehicles": [
                {
                    "VehicleId": 1
                }
            ],
            "RatedDrivers": [
                {
                    "DriverId": 1,
                    "FirstName": "John",
                    "LastName": "Doe",
                    "DateOfBirth": "1990-01-01",
                    "Gender": "Male",
                    "MaritalStatus": "Single",
                    "LicenseInformation": {
                        "LicenseStatus": "Valid"
                    }
                }
            ]
        }

        # Execute handler
        result = await _request_personal_auto_rate(arguments)

        # Verify result structure
        self.assertIn("content", result)
        self.assertIn("structured_content", result)

        # Verify content includes user-visible message
        content = result["content"]
        self.assertTrue(len(content) >= 1)

        # First content item should be the user-visible message
        user_message = content[0].text
        self.assertIn("quote-123456789", user_message)
        self.assertIn("txn-123", user_message)

        # Second content item should be model-only annotation with IDs
        self.assertEqual(len(content), 2)
        model_content = json.loads(content[1].text)
        self.assertEqual(model_content["quoteId"], "quote-123456789")
        self.assertEqual(model_content["transactionId"], "txn-123")
        self.assertEqual(content[1].annotations.audience, ["assistant"])

        # Verify structured content
        self.assertEqual(result["structured_content"]["identifier"], "quote-123456789")

if __name__ == "__main__":
    unittest.main()
