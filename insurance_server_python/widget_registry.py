"""Widget definitions and tool registry for the insurance server."""

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple
import mcp.types as types

from .insurance_state_widget import INSURANCE_STATE_WIDGET_HTML
from .quick_quote_results_widget import QUICK_QUOTE_RESULTS_WIDGET_HTML
from .phone_only_widget import PHONE_ONLY_WIDGET_HTML
from .constants import MIME_TYPE
from .models import ToolHandler


# ============================================================================
# BASE URL CONFIGURATION - Change this for testing/deployment
# ============================================================================
# For local/ngrok testing, set to your ngrok URL:
# BASE_URL = "https://08e6-2601-985-4101-d2b0-53c-2a7-2aa4-cabf.ngrok-free.app"
# For staging:
# BASE_URL = "https://stg-api.mercuryinsurance.com"
# For production:
# BASE_URL = "https://api.mercuryinsurance.com"

BASE_URL = "https://08e6-2601-985-4101-d2b0-53c-2a7-2aa4-cabf.ngrok-free.app"

# Derived URLs
WIDGET_BASE_URL = f"{BASE_URL}/assets/images"
API_DOMAINS = [BASE_URL]  # Domains widgets can connect to
# ============================================================================


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
INSURANCE_STATE_WIDGET_TEMPLATE_URI = f"{WIDGET_BASE_URL}/insurance-state.html"
QUICK_QUOTE_RESULTS_WIDGET_IDENTIFIER = "quick-quote-results"
QUICK_QUOTE_RESULTS_WIDGET_TEMPLATE_URI = f"{WIDGET_BASE_URL}/quick-quote-results.html"
PHONE_ONLY_WIDGET_IDENTIFIER = "phone-only"
PHONE_ONLY_WIDGET_TEMPLATE_URI = f"{WIDGET_BASE_URL}/phone-only.html"

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
    WidgetDefinition(
        identifier=PHONE_ONLY_WIDGET_IDENTIFIER,
        title="Phone-only state message",
        template_uri=PHONE_ONLY_WIDGET_TEMPLATE_URI,
        invoking="Checking if phone-only state",
        invoked="Phone-only state detected",
        html=PHONE_ONLY_WIDGET_HTML,
        response_text="This state requires a phone call for quotes.",
        input_schema=None,
        tool_description=(
            "Displays a phone call prompt for states that require speaking with a licensed agent (AK, HI, MA)."
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
        },
        "ui": {
            "domain": WIDGET_BASE_URL,
            "prefersBorder": False,
            "csp": {
                "connectDomains": API_DOMAINS,
            },
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
        QuickQuoteIntake,
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

    # Register quick quote tool (PRIMARY - streamlined crisp questions)
    register_tool(
        ToolRegistration(
            tool=types.Tool(
                name="get-enhanced-quick-quote",
                title="Get Quote",
                description=(
                    "Primary tool for generating auto insurance quotes with interactive results display.\n"
                    "\n"
                    "**How This Tool Works:**\n"
                    "This tool needs complete information to generate accurate quotes. The recommended "
                    "approach is to collect all required fields before calling the tool.\n"
                    "\n"
                    "**Step 1: Collect Vehicle Information**\n"
                    "Start by asking: \"To provide insurance estimates, please share:\"\n"
                    "• ZIP code\n"
                    "• Number of vehicles (1 or 2)\n"
                    "• Year, make, and model for each vehicle\n"
                    "• Coverage preference (full coverage or liability only)\n"
                    "\n"
                    "Wait for the user's response. If any information is missing, ask for the specific fields needed.\n"
                    "\n"
                    "**Step 2: Collect Driver Information**\n"
                    "Once you have vehicle details, continue with: \"Thanks! Now I need a few driver details:\"\n"
                    "• Number of drivers (1 or 2)\n"
                    "• Age of each driver\n"
                    "• Marital status (single, married, divorced, or widowed)\n"
                    "\n"
                    "Wait for the user's response. If any information is missing, ask for the specific fields needed.\n"
                    "\n"
                    "**Step 3: Generate Quote**\n"
                    "When you have all required information:\n"
                    "- ZIP code\n"
                    "- Number of vehicles and their details (year, make, model)\n"
                    "- Coverage preference\n"
                    "- Number of drivers and their details (age, marital status)\n"
                    "\n"
                    "Call this tool with the complete data. The tool will automatically display an interactive "
                    "widget with quote results.\n"
                    "\n"
                    "**After the Tool Runs:**\n"
                    "The widget displays automatically with the quote results. A simple follow-up like "
                    "\"Let me know if you have any questions!\" works well. The widget provides all the details, "
                    "so additional explanation of coverage options or pricing isn't typically necessary unless "
                    "the user specifically asks.\n"
                    "\n"
                    "**Note on Retries:**\n"
                    "If the widget doesn't appear immediately, this is usually a display timing issue rather "
                    "than a tool failure. The quote has been generated successfully. Avoid calling the tool "
                    "again with the same data, as duplicate requests are filtered.\n"
                    "\n"
                    "**Special Cases:**\n"
                    "For phone-only states (AK, HI, MA), the tool displays a widget with contact information "
                    "instead of quotes, as these states require speaking with a licensed agent.\n"
                    "\n"
                    "**Formatting Tips:**\n"
                    "• Use markdown **bold** for field labels\n"
                    "• Say 'full coverage' rather than 'full_coverage'\n"
                    "• Say 'liability only' rather than 'liability'\n"
                    "• Keep the conversation natural and friendly\n"
                ),
                inputSchema=_model_schema(QuickQuoteIntake),
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
                    "Submits carrier-specific cost estimates to display in an interactive widget.\n"
                    "\n"
                    "**When to Use:**\n"
                    "This tool is designed as a follow-up to 'get-enhanced-quick-quote'. After collecting "
                    "the user's profile information, you may receive instructions to generate carrier estimates "
                    "using this tool.\n"
                    "\n"
                    "**How It Works:**\n"
                    "The tool displays estimates in a widget format rather than as text. Generate 3-5 carrier "
                    "estimates based on:\n"
                    "- User's location, age, vehicle, and coverage type\n"
                    "- The rate range estimate provided\n"
                    "- Typical market positioning of carriers\n"
                    "\n"
                    "**Carrier Selection:**\n"
                    "Include Mercury Insurance among the carriers shown, along with others such as "
                    "Aspire, Progressive, Anchor General Insurance, Orion Indemnity, State Farm, or Geico.\n"
                    "\n"
                    "**For Each Carrier Provide:**\n"
                    "- Carrier Name\n"
                    "- Annual Cost (integer, in dollars)\n"
                    "- Monthly Cost (integer, calculated as annual/12)\n"
                    "- Notes (brief value proposition like 'Strong digital tools' or 'Best for multiple cars')\n"
                    "\n"
                    "**Pricing Guidance:**\n"
                    "Vary the costs realistically to reflect different carrier pricing. Include the user's "
                    "zip code and age from their profile.\n"
                    "\n"
                    "**Example carrier estimates:**\n"
                    "- Mercury Insurance: $3,200/year ($267/month) - 'Strong digital tools & mobile app'\n"
                    "- Aspire: $3,360/year ($280/month) - 'Savings for multiple cars'\n"
                    "- Progressive: $4,064/year ($339/month) - 'Best balance of cost & claims'\n"
                    "\n"
                    "The tool displays results in an interactive widget that shows all carrier options."
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
