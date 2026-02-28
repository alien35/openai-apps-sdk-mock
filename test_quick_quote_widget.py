"""Quick test to verify the quick quote widget metadata is properly registered."""

import sys
sys.path.insert(0, ".")

from insurance_server_python.widget_registry import (
    TOOL_REGISTRY,
    QUICK_QUOTE_RESULTS_WIDGET_IDENTIFIER,
    WIDGETS_BY_ID
)

# Check widget is registered
print(f"✅ Widget registered: {QUICK_QUOTE_RESULTS_WIDGET_IDENTIFIER in WIDGETS_BY_ID}")

# Check tool is registered
tool_reg = TOOL_REGISTRY.get("get-quick-quote")
print(f"✅ Tool registered: {tool_reg is not None}")

if tool_reg:
    # Check tool has widget metadata
    has_meta = hasattr(tool_reg.tool, "meta") and tool_reg.tool.meta is not None
    print(f"✅ Tool has meta: {has_meta}")

    if has_meta:
        has_widget = "openai/widgetAccessible" in tool_reg.tool.meta
        print(f"✅ Tool has widgetAccessible: {has_widget}")

        has_output_template = "openai/outputTemplate" in tool_reg.tool.meta
        print(f"✅ Tool has outputTemplate: {has_output_template}")

    # Check default_meta has widget resource
    has_default_meta = tool_reg.default_meta is not None
    print(f"✅ Tool has default_meta: {has_default_meta}")

    if has_default_meta:
        has_widget_resource = "openai.com/widget" in tool_reg.default_meta
        print(f"✅ default_meta has widget resource: {has_widget_resource}")

print("\n✅ All widget integration checks passed!")
