"""Widget definitions and tool registry for the insurance server."""

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple
import mcp.types as types

from .insurance_state_widget import INSURANCE_STATE_WIDGET_HTML
from .quick_quote_results_widget import QUICK_QUOTE_RESULTS_WIDGET_HTML
from .constants import MIME_TYPE
from .models import ToolHandler


@dataclass(frozen=True)
class WidgetDefinition:
    """Definition of a UI widget with its metadata."""

    identifier: str
    title: str
    template_uri: str
    invoking: str
    invoked: str
    html: str
    response_text: Optional[str]
    input_schema: Optional[Dict[str, Any]]
    tool_description: Optional[str] = None


@dataclass(frozen=True)
class ToolRegistration:
    """Registry entry for a tool with its handler and metadata."""

    tool: types.Tool
    handler: ToolHandler
    default_response_text: Optional[str]
    default_meta: Optional[Dict[str, Any]] = None


# Tool registry
TOOL_REGISTRY: Dict[str, ToolRegistration] = {}


def register_tool(registration: ToolRegistration) -> None:
    """Register a tool so it can be listed and invoked."""
    TOOL_REGISTRY[registration.tool.name] = registration


# Widget identifiers and URIs
INSURANCE_STATE_WIDGET_IDENTIFIER = "insurance-state-selector"
INSURANCE_STATE_WIDGET_TEMPLATE_URI = "ui://widget/insurance-state.html"
QUICK_QUOTE_RESULTS_WIDGET_IDENTIFIER = "quick-quote-results"
QUICK_QUOTE_RESULTS_WIDGET_TEMPLATE_URI = "ui://widget/quick-quote-results.html"

# Input schema for insurance state selector
INSURANCE_STATE_INPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "state": {
            "type": "string",
            "description": "Optional state code (e.g., CA, NY)"
        }
    },
    "additionalProperties": False,
}

# Widget definitions
DEFAULT_WIDGETS: Tuple[WidgetDefinition, ...] = (
    WidgetDefinition(
        identifier=INSURANCE_STATE_WIDGET_IDENTIFIER,
        title="Collect insurance state",
        template_uri=INSURANCE_STATE_WIDGET_TEMPLATE_URI,
        invoking="Collecting a customer's state",
        invoked="Captured the customer's state",
        html=INSURANCE_STATE_WIDGET_HTML,
        response_text=None,
        input_schema=INSURANCE_STATE_INPUT_SCHEMA,
        tool_description=
            "Collects the customer's U.S. state so the assistant can continue gathering driver and vehicle information for their AIS auto quote.",
    ),
)

ADDITIONAL_WIDGETS: Tuple[WidgetDefinition, ...] = (
    WidgetDefinition(
        identifier=QUICK_QUOTE_RESULTS_WIDGET_IDENTIFIER,
        title="Display quick quote estimate",
        template_uri=QUICK_QUOTE_RESULTS_WIDGET_TEMPLATE_URI,
        invoking="Generating quick quote estimate",
        invoked="Displayed quick quote estimate",
        html=QUICK_QUOTE_RESULTS_WIDGET_HTML,
        response_text="Here's your quick quote estimate based on your location and driver count.",
        input_schema=None,
        tool_description=(
            "Displays instant premium range estimates for auto insurance with visual cards showing best and worst case scenarios."
        ),
    ),
)

# All widgets
widgets: Tuple[WidgetDefinition, ...] = DEFAULT_WIDGETS + ADDITIONAL_WIDGETS

# Widget lookup dictionaries
WIDGETS_BY_ID: Dict[str, WidgetDefinition] = {
    widget.identifier: widget for widget in widgets
}
WIDGETS_BY_URI: Dict[str, WidgetDefinition] = {
    widget.template_uri: widget for widget in widgets
}

# Validation checks
if INSURANCE_STATE_WIDGET_IDENTIFIER not in WIDGETS_BY_ID:
    msg = (
        "Insurance state selector widget must be registered; "
        f"expected identifier '{INSURANCE_STATE_WIDGET_IDENTIFIER}' in widgets"
    )
    raise RuntimeError(msg)

if INSURANCE_STATE_WIDGET_TEMPLATE_URI not in WIDGETS_BY_URI:
    msg = (
        "Insurance state selector widget must expose the correct template URI; "
        f"expected '{INSURANCE_STATE_WIDGET_TEMPLATE_URI}' in widgets"
    )
    raise RuntimeError(msg)

if QUICK_QUOTE_RESULTS_WIDGET_IDENTIFIER not in WIDGETS_BY_ID:
    msg = (
        "Quick quote results widget must be registered; "
        f"expected identifier '{QUICK_QUOTE_RESULTS_WIDGET_IDENTIFIER}' in widgets"
    )
    raise RuntimeError(msg)

if QUICK_QUOTE_RESULTS_WIDGET_TEMPLATE_URI not in WIDGETS_BY_URI:
    msg = (
        "Quick quote results widget must expose the correct template URI; "
        f"expected '{QUICK_QUOTE_RESULTS_WIDGET_TEMPLATE_URI}' in widgets"
    )
    raise RuntimeError(msg)


# Helper functions
def _resource_description(widget: WidgetDefinition) -> str:
    """Generate a resource description for a widget."""
    return f"{widget.title} widget markup"


def _tool_meta(widget: WidgetDefinition) -> Dict[str, Any]:
    """Generate tool metadata for a widget."""
    return {
        "openai/outputTemplate": widget.template_uri,
        "openai/toolInvocation/invoking": widget.invoking,
        "openai/toolInvocation/invoked": widget.invoked,
        "openai/widgetAccessible": True,
        "openai/resultCanProduceWidget": True,
        "annotations": {
            "destructiveHint": False,
            "openWorldHint": False,
            "readOnlyHint": True,
        }
    }


def _embedded_widget_resource(widget: WidgetDefinition) -> types.EmbeddedResource:
    """Create an embedded widget resource for a widget."""
    return types.EmbeddedResource(
        type="resource",
        resource=types.TextResourceContents(
            uri=widget.template_uri,
            mimeType=MIME_TYPE,
            text=widget.html,
            title=widget.title,
        ),
    )


def _register_default_tools() -> None:
    """Register default widget tools."""
    from .tool_handlers import _insurance_state_tool_handler

    for widget in DEFAULT_WIDGETS:
        if widget.identifier in TOOL_REGISTRY:
            continue

        if widget.input_schema is None:
            msg = f"Widget '{widget.identifier}' must define an input schema to register its default tool."
            raise RuntimeError(msg)

        meta = _tool_meta(widget)

        tool = types.Tool(
            name=widget.identifier,
            title=widget.title,
            description=widget.tool_description or widget.title,
            inputSchema=deepcopy(widget.input_schema),
            _meta=meta,
        )

        widget_resource = _embedded_widget_resource(widget)
        default_meta = {
            **meta,
            "openai.com/widget": widget_resource.model_dump(mode="json"),
        }

        # Create a closure to capture widget-specific data
        def make_handler(w_id: str, w_meta: dict, w_resource: dict):
            def handler(arguments):
                return _insurance_state_tool_handler(arguments, w_id, w_meta, w_resource)
            return handler

        register_tool(
            ToolRegistration(
                tool=tool,
                handler=make_handler(widget.identifier, meta, widget_resource.model_dump(mode="json")),
                default_response_text=widget.response_text,
                default_meta=default_meta,
            )
        )


def _register_personal_auto_intake_tools() -> None:
    """Register personal auto insurance intake tools."""
    from .tool_handlers import (
        _get_enhanced_quick_quote,
        _submit_carrier_estimates,
    )
    from .models import (
        EnhancedQuickQuoteIntake,
        CarrierEstimatesSubmission,
    )
    from .utils import _model_schema

    # Register quick quote tool (Initial step)
    quick_quote_widget = WIDGETS_BY_ID[QUICK_QUOTE_RESULTS_WIDGET_IDENTIFIER]
    quick_quote_meta = {
        **_tool_meta(quick_quote_widget),
        "openai/widgetAccessible": True,
    }
    quick_quote_default_meta = {
        **quick_quote_meta,
        "openai.com/widget": _embedded_widget_resource(quick_quote_widget).model_dump(mode="json"),
    }

    # Register ENHANCED quick quote tool (PRIMARY - with detailed driver/vehicle info)
    register_tool(
        ToolRegistration(
            tool=types.Tool(
                name="get-enhanced-quick-quote",
                title="Get auto insurance quote with detailed information [PRIMARY]",
                description=(
                    "**PRIMARY TOOL FOR INSURANCE QUOTES** - Get an accurate auto insurance quote using a TWO-STEP conversation flow: "
                    "\n\n"
                    "**CRITICAL: DO NOT ASK ALL QUESTIONS AT ONCE!** Follow this exact flow:\n"
                    "\n"
                    "**STEP 1 - ASK VEHICLE QUESTIONS ONLY (ask these 3 questions together, then STOP and WAIT for user response):**\n"
                    "Say something like 'Let's start with your vehicle information:'\n"
                    "1. What's the year, make, and model of your vehicle? (don't say 'Vehicle 1')\n"
                    "2. Do you have a second vehicle to include? If so, what's the year, make, and model?\n"
                    "3. Are you looking for Liability or Full coverage?\n"
                    "\n"
                    "⚠️ STOP HERE - WAIT FOR USER TO RESPOND WITH VEHICLE INFO BEFORE PROCEEDING\n"
                    "\n"
                    "**STEP 2 - ONLY AFTER USER RESPONDS, ASK DRIVER QUESTIONS (ask these 4 questions together):**\n"
                    "Say something like 'Great! Now I need some driver details:' or 'Now I'll need some information about the driver(s):'\n"
                    "4. What is the primary driver's age?\n"
                    "5. What is their marital status? (single, married, divorced, or widowed)\n"
                    "6. Will there be an additional driver? If yes, what is their age and marital status?\n"
                    "7. What is your 5-digit zip code?\n"
                    "\n"
                    "⚠️ WAIT FOR USER TO RESPOND WITH DRIVER INFO\n"
                    "\n"
                    "**STEP 3 - CALL THIS TOOL ONCE:**\n"
                    "Only after collecting ALL information from both steps, call this tool with the complete data.\n"
                    "\n"
                    "**⚠️ CRITICAL: AFTER CALLING THIS TOOL, THE QUOTE IS COMPLETE. DO NOT CALL THIS TOOL AGAIN.**\n"
                    "The widget will display all carrier quotes. The conversation is done after this tool returns.\n"
                    "\n"
                    "**LANGUAGE STYLE:**\n"
                    "• Use natural, conversational language\n"
                    "• Don't say 'Vehicle 1', 'Vehicle 2', or 'full_coverage'\n"
                    "• Say 'your vehicle' or 'primary vehicle', not 'Vehicle 1'\n"
                    "• Say 'Full coverage' (capitalized, with space), not 'full_coverage'\n"
                    "• Don't use the word 'batch'\n"
                    "\n\n"
                    "This is the RECOMMENDED TOOL for providing users with insurance quotes. Only use the basic quick quote if the user "
                    "explicitly refuses to provide detailed information."
                ),
                inputSchema=_model_schema(EnhancedQuickQuoteIntake),
                _meta=quick_quote_meta,
            ),
            handler=_get_enhanced_quick_quote,
            default_response_text="Generated personalized quote range based on your specific details.",
            default_meta=quick_quote_default_meta,
        )
    )

    # Register carrier estimates submission tool (Step 2 of enhanced quote flow)
    register_tool(
        ToolRegistration(
            tool=types.Tool(
                name="submit-carrier-estimates",
                title="Submit ChatGPT-generated carrier cost estimates",
                description=(
                    "**⚠️ REQUIRED: CALL THIS TOOL IMMEDIATELY AFTER 'get-enhanced-quick-quote'** "
                    "\n\n"
                    "This is STEP 2 of the enhanced quote flow. After 'get-enhanced-quick-quote' collects the user's profile, "
                    "you will receive model-only instructions telling you to call THIS tool with carrier estimates. "
                    "\n\n"
                    "**DO NOT display estimates as text. MUST call this tool to show the widget.**"
                    "\n\n"
                    "**Your task:**\n"
                    "1. Generate 3-5 realistic carrier estimates based on:\n"
                    "   - User's location, age, vehicle, coverage type\n"
                    "   - The provided rate range estimate\n"
                    "   - Typical market positioning of carriers\n"
                    "\n"
                    "2. MUST include Mercury Insurance as one of the carriers\n"
                    "\n"
                    "3. Other carriers to consider: Aspire, Progressive, Anchor General Insurance, Orion Indemnity, State Farm, Geico, etc.\n"
                    "\n"
                    "4. For each carrier provide:\n"
                    "   - Carrier Name\n"
                    "   - Annual Cost (integer, in dollars)\n"
                    "   - Monthly Cost (integer, annual/12)\n"
                    "   - Notes (brief value proposition, e.g., 'Strong digital tools', 'Best for multiple cars')\n"
                    "\n"
                    "5. Vary the costs realistically - don't make them all the same\n"
                    "\n"
                    "6. Include the user's zip code and age from the profile\n"
                    "\n"
                    "**Example carrier estimates:**\n"
                    "- Mercury Insurance: $3,200/year ($267/month) - 'Strong digital tools & mobile app'\n"
                    "- Aspire: $3,360/year ($280/month) - 'Savings for multiple cars'\n"
                    "- Progressive: $4,064/year ($339/month) - 'Best balance of cost & claims'\n"
                    "\n"
                    "After calling this tool, the user will see a widget with the carrier quotes displayed."
                ),
                inputSchema=_model_schema(CarrierEstimatesSubmission),
                _meta=quick_quote_meta,
            ),
            handler=_submit_carrier_estimates,
            default_response_text="Compiled carrier estimates for your profile.",
            default_meta=quick_quote_default_meta,
        )
    )


# Initialize the registry
# _register_default_tools()  # DISABLED - insurance state selector form not used in simplified flow
_register_personal_auto_intake_tools()
