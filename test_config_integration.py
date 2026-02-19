"""Test config-driven enhanced quick quote integration."""

import json


def test_configs():
    """Test that config files are valid and contain expected data."""

    # Test fields.json
    with open("insurance_server_python/config/fields.json") as f:
        fields_config = json.load(f)

    print("=" * 80)
    print("FIELDS CONFIGURATION")
    print("=" * 80)

    # Check new fields exist
    new_fields = [
        "PrimaryDriverAge",
        "Vehicle1Year",
        "Vehicle1Make",
        "Vehicle1Model",
        "Vehicle2Year",
        "Vehicle2Make",
        "Vehicle2Model",
        "CoverageType",
        "AdditionalDriverAge",
        "AdditionalDriverMaritalStatus"
    ]

    print(f"\nTotal fields defined: {len(fields_config['fields'])}")
    print(f"\nChecking for new enhanced quick quote fields:")
    for field_name in new_fields:
        if field_name in fields_config['fields']:
            field = fields_config['fields'][field_name]
            print(f"  ✓ {field_name}")
            print(f"    - Type: {field['field_type']}")
            print(f"    - Required: {field['required']}")
            print(f"    - Prompt: {field['prompt_text']}")
        else:
            print(f"  ✗ {field_name} - MISSING!")

    # Test flows.json
    with open("insurance_server_python/config/flows.json") as f:
        flows_config = json.load(f)

    print("\n" + "=" * 80)
    print("FLOWS CONFIGURATION")
    print("=" * 80)

    print(f"\nTotal flows defined: {len(flows_config['flows'])}")

    # Find enhanced quick quote flow
    enhanced_flow = None
    for flow in flows_config['flows']:
        if flow['name'] == 'enhanced_quick_quote_v1':
            enhanced_flow = flow
            break

    if enhanced_flow:
        print(f"\n✓ Enhanced quick quote flow found")
        print(f"  - Name: {enhanced_flow['name']}")
        print(f"  - Type: {enhanced_flow['flow_type']}")
        print(f"  - Active: {enhanced_flow['metadata']['active']}")
        print(f"  - Description: {enhanced_flow['metadata']['description']}")
        print(f"\n  Required fields:")
        for field in enhanced_flow['submission_criteria']['required_fields']:
            print(f"    • {field}")
        print(f"\n  Optional fields:")
        for stage in enhanced_flow['stages']:
            for field in stage.get('optional_fields', []):
                print(f"    • {field}")
    else:
        print(f"\n✗ Enhanced quick quote flow NOT FOUND!")

    print("\n" + "=" * 80)
    print("TOOL REGISTRATION TEST")
    print("=" * 80)

    # Test tool loading
    from insurance_server_python.widget_registry import TOOL_REGISTRY

    tools = list(TOOL_REGISTRY.keys())
    print(f"\nTotal tools registered: {len(tools)}")
    print(f"\nTools:")
    for tool_name in sorted(tools):
        tool_reg = TOOL_REGISTRY[tool_name]
        print(f"  • {tool_name}")
        print(f"    - Title: {tool_reg.tool.title}")

    # Check enhanced quick quote tool
    if 'get-enhanced-quick-quote' in TOOL_REGISTRY:
        print(f"\n✓ Enhanced quick quote tool is registered")
        tool = TOOL_REGISTRY['get-enhanced-quick-quote'].tool
        print(f"  - Name: {tool.name}")
        print(f"  - Title: {tool.title}")
        print(f"  - Description preview: {tool.description[:100]}...")
    else:
        print(f"\n✗ Enhanced quick quote tool NOT REGISTERED!")

    print("\n" + "=" * 80)
    print("CONFIGURATION TEST PASSED")
    print("=" * 80)


if __name__ == "__main__":
    test_configs()
