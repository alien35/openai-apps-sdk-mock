"""Tests for CTA URL configuration."""

from insurance_server_python.url_config import (
    get_cta_url,
    get_cta_base_url,
    get_cta_params_json,
    CTA_BASE_URL,
    CTA_PARAMS,
)


def test_get_cta_url_default():
    """Test default CTA URL generation."""
    url = get_cta_url("90210")
    assert url.startswith("https://")
    assert "sid=chatgptapp" in url
    assert "refid3=mercuryais" in url
    assert "zip=90210" in url


def test_get_cta_url_with_carrier():
    """Test CTA URL with carrier parameter."""
    url = get_cta_url("90210", carrier_name="Geico")
    assert "carrier=Geico" in url
    assert "zip=90210" in url


def test_get_cta_base_url():
    """Test getting base URL without parameters."""
    base_url = get_cta_base_url()
    assert base_url.startswith("https://")
    assert "?" not in base_url


def test_get_cta_params_json():
    """Test getting parameters as JSON."""
    params = get_cta_params_json()
    assert "base_url" in params
    assert "params" in params
    assert "sid" in params["params"]
    assert "refid3" in params["params"]
    assert params["params"]["sid"] == "chatgptapp"
    assert params["params"]["refid3"] == "mercuryais"


def test_url_format():
    """Test that URL is properly formatted."""
    url = get_cta_url("12345")

    # Should have exactly one question mark
    assert url.count("?") == 1

    # Parameters should be separated by &
    query_string = url.split("?")[1]
    params = query_string.split("&")
    assert len(params) >= 3  # At least sid, refid3, zip

    # Each parameter should have key=value format
    for param in params:
        assert "=" in param
        key, value = param.split("=", 1)
        assert key
        assert value


def test_zip_code_variations():
    """Test different ZIP code formats."""
    # 5-digit zip
    url1 = get_cta_url("90210")
    assert "zip=90210" in url1

    # ZIP+4 format
    url2 = get_cta_url("90210-1234")
    assert "zip=90210-1234" in url2

    # Different zip
    url3 = get_cta_url("10001")
    assert "zip=10001" in url3


def test_default_params_present():
    """Test that default parameters are always present."""
    url = get_cta_url("90210")
    assert "sid=chatgptapp" in url
    assert "refid3=mercuryais" in url


def test_cta_base_url_defined():
    """Test that base URL is defined."""
    assert CTA_BASE_URL
    assert CTA_BASE_URL.startswith("https://")
    assert "aisinsurance.com" in CTA_BASE_URL


def test_cta_params_defined():
    """Test that CTA parameters are defined."""
    assert "sid" in CTA_PARAMS
    assert "refid3" in CTA_PARAMS
    assert CTA_PARAMS["sid"]  # Not empty
    assert CTA_PARAMS["refid3"]  # Not empty


def test_carrier_in_middle_of_params():
    """Test that carrier parameter is inserted before zip."""
    url = get_cta_url("90210", carrier_name="Progressive")
    # Ensure zip is at the end
    assert url.endswith("zip=90210")
    # Ensure carrier is present
    assert "carrier=Progressive" in url


def test_multiple_zip_codes():
    """Test URL generation with different zip codes."""
    zips = ["10001", "90210", "60601", "77001", "98101"]
    for zip_code in zips:
        url = get_cta_url(zip_code)
        assert f"zip={zip_code}" in url
        assert url.startswith(CTA_BASE_URL)
