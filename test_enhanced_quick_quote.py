"""Test the enhanced quick quote tool."""

import asyncio
from insurance_server_python.tool_handlers import _get_enhanced_quick_quote


async def test_enhanced_quick_quote():
    """Test enhanced quick quote with sample data."""

    # Test case 1: Young driver with new car, full coverage
    test_data_1 = {
        "ZipCode": "90210",  # Beverly Hills
        "PrimaryDriverAge": 22,
        "Vehicle1": {
            "year": 2024,
            "make": "Toyota",
            "model": "Camry"
        },
        "CoverageType": "full_coverage"
    }

    print("Test 1: Young driver (22), new car, full coverage")
    result = await _get_enhanced_quick_quote(test_data_1)
    print(f"Result: {result['content'][0].text}\n")
    print(f"Structured content: {result['structured_content']}\n")
    print("=" * 80)

    # Test case 2: Experienced driver, older car, liability only
    test_data_2 = {
        "ZipCode": "94102",  # San Francisco
        "PrimaryDriverAge": 45,
        "Vehicle1": {
            "year": 2015,
            "make": "Honda",
            "model": "Accord"
        },
        "CoverageType": "liability"
    }

    print("\nTest 2: Experienced driver (45), older car, liability only")
    result = await _get_enhanced_quick_quote(test_data_2)
    print(f"Result: {result['content'][0].text}\n")
    print(f"Structured content: {result['structured_content']}\n")
    print("=" * 80)

    # Test case 3: Two drivers, two vehicles, full coverage
    test_data_3 = {
        "ZipCode": "92101",  # San Diego
        "PrimaryDriverAge": 35,
        "Vehicle1": {
            "year": 2022,
            "make": "Tesla",
            "model": "Model 3"
        },
        "Vehicle2": {
            "year": 2020,
            "make": "Mazda",
            "model": "CX-5"
        },
        "CoverageType": "full_coverage",
        "AdditionalDriver": {
            "age": 33,
            "marital_status": "married"
        }
    }

    print("\nTest 3: Two drivers, two vehicles, full coverage")
    result = await _get_enhanced_quick_quote(test_data_3)
    print(f"Result: {result['content'][0].text}\n")
    print(f"Structured content: {result['structured_content']}\n")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_enhanced_quick_quote())
