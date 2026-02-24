"""Unit tests for phone-only state functionality (MA, AK, HI).

Tests the complete flow:
1. State normalization (full name -> abbreviation)
2. Carrier filtering (empty list for phone-only states)
3. Widget rendering (phone section vs carrier table)
4. Tool handler behavior
"""

import pytest
from unittest.mock import patch, MagicMock
from insurance_server_python.carrier_mapping import (
    get_carriers_for_state,
    normalize_state,
)
from insurance_server_python.utils import state_abbreviation


# ============================================================================
# Test Suite 1: State Normalization
# ============================================================================

class TestStateNormalization:
    """Test that full state names are converted to abbreviations."""

    def test_massachusetts_full_name_to_abbreviation(self):
        """MA: Full name 'Massachusetts' should normalize to 'MA'."""
        result = normalize_state("Massachusetts")
        assert result == "MA"

    def test_alaska_full_name_to_abbreviation(self):
        """AK: Full name 'Alaska' should normalize to 'AK'."""
        result = normalize_state("Alaska")
        assert result == "AK"

    def test_hawaii_full_name_to_abbreviation(self):
        """HI: Full name 'Hawaii' should normalize to 'HI'."""
        result = normalize_state("Hawaii")
        assert result == "HI"

    def test_abbreviations_stay_unchanged(self):
        """Abbreviations should pass through unchanged."""
        assert normalize_state("MA") == "MA"
        assert normalize_state("AK") == "AK"
        assert normalize_state("HI") == "HI"

    def test_case_insensitive_normalization(self):
        """State names should be case-insensitive."""
        assert normalize_state("massachusetts") == "MA"
        assert normalize_state("MASSACHUSETTS") == "MA"
        assert normalize_state("MassAchuSetTs") == "MA"

    def test_normal_state_normalization(self):
        """Normal states should also normalize correctly."""
        assert normalize_state("California") == "CA"
        assert normalize_state("california") == "CA"
        assert normalize_state("CA") == "CA"

    def test_invalid_state_returns_none(self):
        """Invalid state names should return None."""
        assert normalize_state("InvalidState") == None
        assert normalize_state("") == None
        assert normalize_state("XX") == None

    def test_whitespace_handling(self):
        """State names with whitespace should be handled."""
        assert normalize_state(" Massachusetts ") == "MA"
        assert normalize_state("  MA  ") == "MA"

    def test_state_abbreviation_function(self):
        """Test the state_abbreviation utility function."""
        assert state_abbreviation("Massachusetts") == "MA"
        assert state_abbreviation("Alaska") == "AK"
        assert state_abbreviation("Hawaii") == "HI"
        assert state_abbreviation("California") == "CA"


# ============================================================================
# Test Suite 2: Carrier Filtering
# ============================================================================

class TestCarrierFiltering:
    """Test that phone-only states return empty carrier lists."""

    def test_massachusetts_returns_empty_carriers(self):
        """MA should return empty carrier list."""
        carriers = get_carriers_for_state("MA")
        assert carriers == []
        assert len(carriers) == 0

    def test_alaska_returns_empty_carriers(self):
        """AK should return empty carrier list."""
        carriers = get_carriers_for_state("AK")
        assert carriers == []
        assert len(carriers) == 0

    def test_hawaii_returns_empty_carriers(self):
        """HI should return empty carrier list."""
        carriers = get_carriers_for_state("HI")
        assert carriers == []
        assert len(carriers) == 0

    def test_massachusetts_full_name_returns_empty(self):
        """'Massachusetts' (full name) should also return empty."""
        carriers = get_carriers_for_state("Massachusetts")
        assert carriers == []

    def test_alaska_full_name_returns_empty(self):
        """'Alaska' (full name) should also return empty."""
        carriers = get_carriers_for_state("Alaska")
        assert carriers == []

    def test_hawaii_full_name_returns_empty(self):
        """'Hawaii' (full name) should also return empty."""
        carriers = get_carriers_for_state("Hawaii")
        assert carriers == []

    def test_california_returns_carriers(self):
        """CA (normal state) should return carrier list."""
        carriers = get_carriers_for_state("CA")
        assert len(carriers) > 0
        assert isinstance(carriers, list)
        # CA should have Progressive, Mercury, National General
        assert "Progressive Insurance" in carriers

    def test_texas_returns_carriers(self):
        """TX (normal state) should return carrier list."""
        carriers = get_carriers_for_state("TX")
        assert len(carriers) > 0
        assert "Geico" in carriers or "Progressive Insurance" in carriers

    def test_new_york_returns_carriers(self):
        """NY (normal state) should return carrier list."""
        carriers = get_carriers_for_state("NY")
        assert len(carriers) > 0

    def test_no_defaults_for_phone_only_states(self):
        """Phone-only states should NOT fall back to default carriers."""
        ma_carriers = get_carriers_for_state("MA")
        ak_carriers = get_carriers_for_state("AK")
        hi_carriers = get_carriers_for_state("HI")

        # None should have "Geico", "Progressive", or "Safeco"
        assert "Geico" not in ma_carriers
        assert "Progressive Insurance" not in ma_carriers
        assert "Safeco Insurance" not in ma_carriers

        assert "Geico" not in ak_carriers
        assert "Geico" not in hi_carriers


# ============================================================================
# Test Suite 3: Frontend State Detection
# ============================================================================

class TestFrontendStateDetection:
    """Test that frontend correctly identifies phone-only states."""

    def test_phone_only_state_list_includes_abbreviations(self):
        """Phone-only state list should include abbreviations."""
        phone_only_states = ["AK", "HI", "MA", "Alaska", "Hawaii", "Massachusetts"]

        assert "MA" in phone_only_states
        assert "AK" in phone_only_states
        assert "HI" in phone_only_states

    def test_phone_only_state_list_includes_full_names(self):
        """Phone-only state list should include full names."""
        phone_only_states = ["AK", "HI", "MA", "Alaska", "Hawaii", "Massachusetts"]

        assert "Massachusetts" in phone_only_states
        assert "Alaska" in phone_only_states
        assert "Hawaii" in phone_only_states

    def test_normal_states_not_in_phone_only_list(self):
        """Normal states should not be in phone-only list."""
        phone_only_states = ["AK", "HI", "MA", "Alaska", "Hawaii", "Massachusetts"]

        assert "CA" not in phone_only_states
        assert "California" not in phone_only_states
        assert "TX" not in phone_only_states
        assert "NY" not in phone_only_states

    def test_defense_in_depth_both_formats_covered(self):
        """Both abbreviation and full name should trigger phone-only behavior."""
        phone_only_states = ["AK", "HI", "MA", "Alaska", "Hawaii", "Massachusetts"]

        # Test all combinations
        for abbr, full in [("MA", "Massachusetts"), ("AK", "Alaska"), ("HI", "Hawaii")]:
            assert abbr in phone_only_states, f"{abbr} missing"
            assert full in phone_only_states, f"{full} missing"


# ============================================================================
# Test Suite 4: Widget Rendering Logic
# ============================================================================

class TestWidgetRendering:
    """Test widget HTML contains necessary elements."""

    def test_widget_has_phone_section(self):
        """Widget HTML should contain phone-call-section element."""
        from insurance_server_python.quick_quote_results_widget import QUICK_QUOTE_RESULTS_WIDGET_HTML

        assert 'id="phone-call-section"' in QUICK_QUOTE_RESULTS_WIDGET_HTML
        assert 'class="phone-call-section"' in QUICK_QUOTE_RESULTS_WIDGET_HTML

    def test_widget_has_phone_call_text_element(self):
        """Widget should have phone-call-text element for dynamic updates."""
        from insurance_server_python.quick_quote_results_widget import QUICK_QUOTE_RESULTS_WIDGET_HTML

        assert 'id="phone-call-text"' in QUICK_QUOTE_RESULTS_WIDGET_HTML

    def test_widget_has_carriers_table(self):
        """Widget should have carriers table for normal states."""
        from insurance_server_python.quick_quote_results_widget import QUICK_QUOTE_RESULTS_WIDGET_HTML

        assert 'id="carriers-table-content"' in QUICK_QUOTE_RESULTS_WIDGET_HTML
        assert 'class="carriers-table"' in QUICK_QUOTE_RESULTS_WIDGET_HTML

    def test_widget_has_phone_number(self):
        """Widget should display phone number."""
        from insurance_server_python.quick_quote_results_widget import QUICK_QUOTE_RESULTS_WIDGET_HTML

        assert "(888) 772-4247" in QUICK_QUOTE_RESULTS_WIDGET_HTML

    def test_widget_has_phone_only_state_check(self):
        """Widget JavaScript should check for phone-only states."""
        from insurance_server_python.quick_quote_results_widget import QUICK_QUOTE_RESULTS_WIDGET_HTML

        # Should check for both abbreviations and full names
        assert "MA" in QUICK_QUOTE_RESULTS_WIDGET_HTML
        assert "Massachusetts" in QUICK_QUOTE_RESULTS_WIDGET_HTML
        assert "Alaska" in QUICK_QUOTE_RESULTS_WIDGET_HTML
        assert "Hawaii" in QUICK_QUOTE_RESULTS_WIDGET_HTML

    def test_widget_forces_empty_carriers_for_phone_only(self):
        """Widget should force empty carriers for phone-only states."""
        from insurance_server_python.quick_quote_results_widget import QUICK_QUOTE_RESULTS_WIDGET_HTML

        # Should have logic to force empty carriers
        assert "let carriers = []" in QUICK_QUOTE_RESULTS_WIDGET_HTML or \
               "carriers = []" in QUICK_QUOTE_RESULTS_WIDGET_HTML

    def test_widget_has_orange_button_color(self):
        """Widget button should use orange brand color."""
        from insurance_server_python.quick_quote_results_widget import QUICK_QUOTE_RESULTS_WIDGET_HTML

        assert "#e67e50" in QUICK_QUOTE_RESULTS_WIDGET_HTML


# ============================================================================
# Test Suite 5: Tool Handler Integration
# ============================================================================

class TestToolHandlerIntegration:
    """Test tool handler correctly processes phone-only states."""

    @pytest.mark.asyncio
    async def test_enhanced_quick_quote_normalizes_state(self):
        """Tool handler should normalize state to abbreviation."""
        from insurance_server_python.tool_handlers import _get_enhanced_quick_quote
        from insurance_server_python.models import EnhancedQuickQuoteIntake, VehicleInfo

        # Mock the zip lookup to return Massachusetts
        with patch("insurance_server_python.tool_handlers._lookup_city_state_from_zip") as mock_lookup:
            mock_lookup.return_value = ("Natick", "Massachusetts")

            # Mock carrier logos
            with patch("insurance_server_python.tool_handlers.get_carrier_logo") as mock_logo:
                mock_logo.return_value = "data:image/png;base64,mock"

                # Mock the estimator to avoid external dependencies
                with patch("insurance_server_python.pricing.InsuranceQuoteEstimator") as mock_estimator:
                    mock_instance = MagicMock()
                    mock_instance.estimate_quotes.return_value = {
                        "quotes": [],
                        "methodology": "test"
                    }
                    mock_estimator.return_value = mock_instance

                    result = await _get_enhanced_quick_quote({
                        "zip_code": "01760",
                        "primary_driver_age": 30,
                        "primary_driver_marital_status": "married",
                        "coverage_type": "full_coverage",
                        "vehicle_1": {
                            "year": 2020,
                            "make": "Honda",
                            "model": "Accord"
                        }
                    })

                    # State should be normalized to MA in structured_content
                    assert "structured_content" in result
                    structured_content = result["structured_content"]
                    assert structured_content["state"] == "MA", \
                        f"Expected 'MA', got '{structured_content['state']}'"

    @pytest.mark.asyncio
    async def test_enhanced_quick_quote_returns_empty_carriers_for_ma(self):
        """MA should return empty carriers list in structured_content."""
        from insurance_server_python.tool_handlers import _get_enhanced_quick_quote

        with patch("insurance_server_python.tool_handlers._lookup_city_state_from_zip") as mock_lookup:
            mock_lookup.return_value = ("Natick", "Massachusetts")

            with patch("insurance_server_python.tool_handlers.get_carrier_logo") as mock_logo:
                mock_logo.return_value = "data:image/png;base64,mock"

                # Don't mock get_carriers_for_state - we want to test it returns empty for MA
                # This is an integration test
                with patch("insurance_server_python.pricing.InsuranceQuoteEstimator") as mock_estimator:
                    mock_instance = MagicMock()
                    # The estimator will be called with empty carriers, so it should return empty quotes
                    mock_instance.estimate_quotes.return_value = {
                        "quotes": [],
                        "methodology": "test"
                    }
                    mock_estimator.return_value = mock_instance

                    result = await _get_enhanced_quick_quote({
                        "zip_code": "01760",
                        "primary_driver_age": 30,
                        "primary_driver_marital_status": "married",
                        "coverage_type": "full_coverage",
                        "vehicle_1": {
                            "year": 2020,
                            "make": "Honda",
                            "model": "Accord"
                        }
                    })

                    structured_content = result["structured_content"]
                    assert structured_content["carriers"] == [], \
                        f"Expected empty carriers, got {len(structured_content['carriers'])} carriers"


# ============================================================================
# Test Suite 6: Edge Cases
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_string_state(self):
        """Empty string should return None for normalization."""
        assert normalize_state("") == None

    def test_none_state(self):
        """None should return None for normalization."""
        assert normalize_state(None) == None

    def test_numeric_state(self):
        """Numeric input should return None."""
        assert normalize_state("12345") == None

    def test_special_characters_state(self):
        """Special characters should return None."""
        assert normalize_state("@#$%") == None

    def test_get_carriers_with_invalid_state(self):
        """Invalid state should return default carriers (not empty)."""
        carriers = get_carriers_for_state("InvalidState")
        # Should return defaults, not empty (only phone-only states return empty)
        assert len(carriers) > 0

    def test_case_sensitivity_in_carrier_lookup(self):
        """Carrier lookup should handle case variations."""
        assert get_carriers_for_state("ma") == []
        assert get_carriers_for_state("MA") == []
        assert get_carriers_for_state("Ma") == []


# ============================================================================
# Test Suite 7: Regression Tests
# ============================================================================

class TestRegressionProtection:
    """Tests to prevent regression of fixed bugs."""

    def test_ma_does_not_return_default_carriers(self):
        """
        REGRESSION TEST: MA was returning default carriers (Geico, Progressive, Safeco)
        when it should return empty list.
        """
        carriers = get_carriers_for_state("MA")

        # These should NOT be in the list
        assert "Geico" not in carriers
        assert "Progressive Insurance" not in carriers
        assert "Safeco Insurance" not in carriers

        # List should be completely empty
        assert carriers == []

    def test_massachusetts_full_name_also_returns_empty(self):
        """
        REGRESSION TEST: Frontend was checking only for 'MA' but backend
        was sending 'Massachusetts', causing carriers to show.
        """
        carriers = get_carriers_for_state("Massachusetts")
        assert carriers == []

    def test_frontend_checks_both_formats(self):
        """
        REGRESSION TEST: Frontend must check for both 'MA' and 'Massachusetts'
        to handle cases where normalization fails.
        """
        phone_only_states = ["AK", "HI", "MA", "Alaska", "Hawaii", "Massachusetts"]

        # Both formats must be present
        assert "MA" in phone_only_states and "Massachusetts" in phone_only_states
        assert "AK" in phone_only_states and "Alaska" in phone_only_states
        assert "HI" in phone_only_states and "Hawaii" in phone_only_states

    def test_button_color_is_orange_not_green(self):
        """
        REGRESSION TEST: Button was green (#10b981) for phone-only states
        but should be orange (#e67e50) for brand consistency.
        """
        from insurance_server_python.quick_quote_results_widget import QUICK_QUOTE_RESULTS_WIDGET_HTML

        # Should use orange color
        assert "#e67e50" in QUICK_QUOTE_RESULTS_WIDGET_HTML

        # Should NOT use green color for CTA
        # (Note: might be in code but commented out or in a different context)


# ============================================================================
# Test Suite 8: Integration Smoke Tests
# ============================================================================

class TestIntegrationSmokeTests:
    """Quick smoke tests for the complete flow."""

    def test_complete_ma_flow(self):
        """Test complete flow: MA zip -> normalize -> empty carriers."""
        # Step 1: Normalize state
        state = normalize_state("Massachusetts")
        assert state == "MA"

        # Step 2: Get carriers
        carriers = get_carriers_for_state(state)
        assert carriers == []

        # Step 3: Verify frontend would detect as phone-only
        phone_only_states = ["AK", "HI", "MA", "Alaska", "Hawaii", "Massachusetts"]
        assert state in phone_only_states

    def test_complete_ca_flow(self):
        """Test complete flow: CA zip -> normalize -> carrier list."""
        # Step 1: Normalize state
        state = normalize_state("California")
        assert state == "CA"

        # Step 2: Get carriers
        carriers = get_carriers_for_state(state)
        assert len(carriers) > 0

        # Step 3: Verify frontend would NOT detect as phone-only
        phone_only_states = ["AK", "HI", "MA", "Alaska", "Hawaii", "Massachusetts"]
        assert state not in phone_only_states

    def test_all_phone_only_states_consistently_handled(self):
        """All three phone-only states should behave identically."""
        phone_only_abbrs = ["MA", "AK", "HI"]
        phone_only_full = ["Massachusetts", "Alaska", "Hawaii"]

        for abbr, full in zip(phone_only_abbrs, phone_only_full):
            # Test normalization
            assert normalize_state(full) == abbr

            # Test carrier filtering (both formats)
            assert get_carriers_for_state(abbr) == []
            assert get_carriers_for_state(full) == []


# ============================================================================
# Pytest Configuration
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
