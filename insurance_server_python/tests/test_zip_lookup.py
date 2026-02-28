"""Unit tests for zip code lookup functionality (ZIP 02141 fix).

Tests the fallback hierarchy for zip code resolution:
1. Primary: Look for "locality"
2. Fallback 1: Check "postcode_localities" array (multi-city zips)
3. Fallback 2: Use "neighborhood" if present
4. Fallback 3: Return None (triggers phone-only prompt)
"""

import unittest
from unittest.mock import patch, Mock
import os
from insurance_server_python.utils import _lookup_city_state_from_zip


class TestZipCodeLookup(unittest.TestCase):
    """Test cases for _lookup_city_state_from_zip function."""

    @patch.dict(os.environ, {'GOOGLE_MAPS_API_KEY': 'test_api_key'})
    @patch('httpx.get')
    def test_regular_zip_with_locality(self, mock_get):
        """Test regular zip code with 'locality' (primary path)."""

        # Mock Google API response for a regular zip (e.g., 02108 - Boston)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "OK",
            "results": [{
                "address_components": [
                    {"long_name": "02108", "types": ["postal_code"]},
                    {"long_name": "Boston", "types": ["locality", "political"]},
                    {"long_name": "Suffolk County", "types": ["administrative_area_level_2", "political"]},
                    {"long_name": "Massachusetts", "types": ["administrative_area_level_1", "political"]},
                    {"long_name": "United States", "types": ["country", "political"]}
                ],
                "formatted_address": "Boston, MA 02108, USA"
            }]
        }
        mock_get.return_value = mock_response

        result = _lookup_city_state_from_zip("02108")

        self.assertIsNotNone(result)
        self.assertEqual(result, ("Boston", "Massachusetts"))

    @patch.dict(os.environ, {'GOOGLE_MAPS_API_KEY': 'test_api_key'})
    @patch('httpx.get')
    def test_multi_city_zip_with_postcode_localities(self, mock_get):
        """Test multi-city zip code 02141 with 'postcode_localities' (fallback 1).

        This is the primary fix - 02141 spans Boston, Cambridge, and Somerville.
        Google returns postcode_localities array but NO locality field.
        """

        # Mock Google API response for 02141 (Cambridge/Boston multi-city zip)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "OK",
            "results": [{
                "address_components": [
                    {"long_name": "02141", "types": ["postal_code"]},
                    {"long_name": "East Cambridge", "types": ["neighborhood", "political"]},
                    {"long_name": "Massachusetts", "types": ["administrative_area_level_1", "political"]},
                    {"long_name": "United States", "types": ["country", "political"]}
                ],
                "postcode_localities": ["Boston", "Cambridge", "Somerville"],
                "formatted_address": "East Cambridge, MA 02141, USA"
            }]
        }
        mock_get.return_value = mock_response

        result = _lookup_city_state_from_zip("02141")

        self.assertIsNotNone(result)
        # Should use first city from postcode_localities
        self.assertEqual(result, ("Boston", "Massachusetts"))

    @patch.dict(os.environ, {'GOOGLE_MAPS_API_KEY': 'test_api_key'})
    @patch('httpx.get')
    def test_neighborhood_only_zip(self, mock_get):
        """Test zip code with only 'neighborhood' (fallback 2)."""

        # Mock response with only neighborhood, no locality or postcode_localities
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "OK",
            "results": [{
                "address_components": [
                    {"long_name": "99999", "types": ["postal_code"]},
                    {"long_name": "Test Neighborhood", "types": ["neighborhood", "political"]},
                    {"long_name": "Test State", "types": ["administrative_area_level_1", "political"]},
                    {"long_name": "United States", "types": ["country", "political"]}
                ],
                "formatted_address": "Test Neighborhood, Test State 99999, USA"
            }]
        }
        mock_get.return_value = mock_response

        result = _lookup_city_state_from_zip("99999")

        self.assertIsNotNone(result)
        # Should use neighborhood as city
        self.assertEqual(result, ("Test Neighborhood", "Test State"))

    @patch.dict(os.environ, {'GOOGLE_MAPS_API_KEY': 'test_api_key'})
    @patch('httpx.get')
    def test_invalid_zip_returns_none_via_fallback(self, mock_get):
        """Test truly invalid zip code falls back gracefully."""

        # Mock Google API response for invalid zip
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "ZERO_RESULTS",
            "results": []
        }
        mock_get.return_value = mock_response

        result = _lookup_city_state_from_zip("00000")

        # Should return None (triggers phone-only prompt with zip code)
        self.assertIsNone(result)

    @patch.dict(os.environ, {'GOOGLE_MAPS_API_KEY': 'test_api_key'})
    @patch('httpx.get')
    def test_api_timeout_uses_fallback(self, mock_get):
        """Test that API timeout gracefully falls back to hardcoded lookup."""

        # Mock timeout exception
        import httpx
        mock_get.side_effect = httpx.TimeoutException("Request timeout")

        result = _lookup_city_state_from_zip("90210")

        # Should fall back to hardcoded lookup (Beverly Hills in fallback table)
        self.assertIsNotNone(result)
        self.assertEqual(result, ("Beverly Hills", "California"))

    @patch.dict(os.environ, {'GOOGLE_MAPS_API_KEY': 'test_api_key'})
    @patch('httpx.get')
    def test_api_error_uses_fallback(self, mock_get):
        """Test that API errors gracefully fall back to hardcoded lookup."""

        # Mock 500 error
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        result = _lookup_city_state_from_zip("90001")

        # Should fall back to hardcoded lookup (Los Angeles in fallback table)
        self.assertIsNotNone(result)
        self.assertEqual(result, ("Los Angeles", "California"))

    @patch.dict(os.environ, {}, clear=True)
    def test_no_api_key_uses_fallback(self):
        """Test that missing API key uses hardcoded fallback."""

        result = _lookup_city_state_from_zip("94102")

        # Should use fallback lookup (San Francisco in fallback table)
        self.assertIsNotNone(result)
        self.assertEqual(result, ("San Francisco", "California"))

    @patch.dict(os.environ, {'GOOGLE_MAPS_API_KEY': 'test_api_key'})
    @patch('httpx.get')
    def test_multi_city_zip_prefers_postcode_localities_over_neighborhood(self, mock_get):
        """Test that postcode_localities is preferred over neighborhood for multi-city zips."""

        # Mock response with BOTH postcode_localities AND neighborhood
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "OK",
            "results": [{
                "address_components": [
                    {"long_name": "02141", "types": ["postal_code"]},
                    {"long_name": "East Cambridge", "types": ["neighborhood", "political"]},
                    {"long_name": "Massachusetts", "types": ["administrative_area_level_1", "political"]},
                    {"long_name": "United States", "types": ["country", "political"]}
                ],
                "postcode_localities": ["Boston", "Cambridge", "Somerville"],
                "formatted_address": "East Cambridge, MA 02141, USA"
            }]
        }
        mock_get.return_value = mock_response

        result = _lookup_city_state_from_zip("02141")

        self.assertIsNotNone(result)
        # Should use postcode_localities[0] ("Boston"), NOT neighborhood ("East Cambridge")
        self.assertEqual(result, ("Boston", "Massachusetts"))

    @patch.dict(os.environ, {'GOOGLE_MAPS_API_KEY': 'test_api_key'})
    @patch('httpx.get')
    def test_zip_with_locality_and_neighborhood_prefers_locality(self, mock_get):
        """Test that locality is preferred when both locality and neighborhood are present."""

        # Mock response with BOTH locality AND neighborhood
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "OK",
            "results": [{
                "address_components": [
                    {"long_name": "10001", "types": ["postal_code"]},
                    {"long_name": "Chelsea", "types": ["neighborhood", "political"]},
                    {"long_name": "New York", "types": ["locality", "political"]},
                    {"long_name": "New York County", "types": ["administrative_area_level_2", "political"]},
                    {"long_name": "New York", "types": ["administrative_area_level_1", "political"]},
                    {"long_name": "United States", "types": ["country", "political"]}
                ],
                "formatted_address": "New York, NY 10001, USA"
            }]
        }
        mock_get.return_value = mock_response

        result = _lookup_city_state_from_zip("10001")

        self.assertIsNotNone(result)
        # Should use locality ("New York"), NOT neighborhood ("Chelsea")
        self.assertEqual(result, ("New York", "New York"))


class TestZipCodeLookupIntegration(unittest.TestCase):
    """Integration tests to verify the fix in context."""

    @patch.dict(os.environ, {'GOOGLE_MAPS_API_KEY': 'test_api_key'})
    @patch('httpx.get')
    def test_02141_cambridge_scenario_before_and_after_fix(self, mock_get):
        """Integration test for the original 02141 bug.

        Before fix: Would return (None, None) because no 'locality' found
        After fix: Returns ('Boston', 'Massachusetts') using postcode_localities
        """

        # Exact Google API response for 02141
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "OK",
            "results": [{
                "address_components": [
                    {"long_name": "02141", "types": ["postal_code"]},
                    {"long_name": "East Cambridge", "types": ["neighborhood", "political"]},
                    {"long_name": "Massachusetts", "types": ["administrative_area_level_1", "political"]},
                    {"long_name": "United States", "types": ["country", "political"]}
                ],
                "postcode_localities": ["Boston", "Cambridge", "Somerville"],
                "formatted_address": "East Cambridge, MA 02141, USA"
            }]
        }
        mock_get.return_value = mock_response

        result = _lookup_city_state_from_zip("02141")

        # After fix: Should successfully resolve
        self.assertIsNotNone(result, "Fix failed: 02141 still returns None")
        self.assertEqual(result[0], "Boston", "Fix failed: City should be 'Boston'")
        self.assertEqual(result[1], "Massachusetts", "Fix failed: State should be 'Massachusetts'")


if __name__ == '__main__':
    unittest.main()
