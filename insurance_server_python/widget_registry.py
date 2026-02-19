"""Widget definitions and tool registry for the insurance server."""

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple
import mcp.types as types

from .insurance_state_widget import INSURANCE_STATE_WIDGET_HTML
from .insurance_rate_results_widget import INSURANCE_RATE_RESULTS_WIDGET_HTML
from .quick_quote_results_widget import QUICK_QUOTE_RESULTS_WIDGET_HTML
from .insurance_wizard_widget_html import INSURANCE_WIZARD_WIDGET_HTML
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
INSURANCE_RATE_RESULTS_WIDGET_IDENTIFIER = "insurance-rate-results"
INSURANCE_RATE_RESULTS_WIDGET_TEMPLATE_URI = "ui://widget/insurance-rate-results.html"
QUICK_QUOTE_RESULTS_WIDGET_IDENTIFIER = "quick-quote-results"
QUICK_QUOTE_RESULTS_WIDGET_TEMPLATE_URI = "ui://widget/quick-quote-results.html"
INSURANCE_WIZARD_WIDGET_IDENTIFIER = "insurance-wizard"
INSURANCE_WIZARD_WIDGET_TEMPLATE_URI = "ui://widget/insurance-wizard.html"

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
        identifier=INSURANCE_RATE_RESULTS_WIDGET_IDENTIFIER,
        title="Review personal auto rate results",
        template_uri=INSURANCE_RATE_RESULTS_WIDGET_TEMPLATE_URI,
        invoking="Retrieving personal auto rate results",
        invoked="Displayed personal auto rate results",
        html=INSURANCE_RATE_RESULTS_WIDGET_HTML,
        response_text="Here are the carrier premiums returned for this quote.",
        input_schema=None,
        tool_description=(
            "Summarizes carrier premiums, payment plans, and shared coverages for a personal auto quote."
        ),
    ),
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
        identifier=INSURANCE_WIZARD_WIDGET_IDENTIFIER,
        title="Complete insurance application wizard",
        template_uri=INSURANCE_WIZARD_WIDGET_TEMPLATE_URI,
        invoking="Loading insurance application wizard",
        invoked="Displayed insurance application wizard",
        html=INSURANCE_WIZARD_WIDGET_HTML,
        response_text="Please complete the insurance application wizard to get your detailed quote.",
        input_schema=None,
        tool_description=(
            "Displays a multi-step wizard interface for collecting complete insurance application details. "
            "Guides users through 5 steps: Policy Setup, Customer Info, Vehicle Details, Driver Info, and Review & Submit."
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

if INSURANCE_RATE_RESULTS_WIDGET_IDENTIFIER not in WIDGETS_BY_ID:
    msg = (
        "Personal auto rate results widget must be registered; "
        f"expected identifier '{INSURANCE_RATE_RESULTS_WIDGET_IDENTIFIER}' in widgets"
    )
    raise RuntimeError(msg)

if INSURANCE_RATE_RESULTS_WIDGET_TEMPLATE_URI not in WIDGETS_BY_URI:
    msg = (
        "Personal auto rate results widget must expose the correct template URI; "
        f"expected '{INSURANCE_RATE_RESULTS_WIDGET_TEMPLATE_URI}' in widgets"
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

if INSURANCE_WIZARD_WIDGET_IDENTIFIER not in WIDGETS_BY_ID:
    msg = (
        "Insurance wizard widget must be registered; "
        f"expected identifier '{INSURANCE_WIZARD_WIDGET_IDENTIFIER}' in widgets"
    )
    raise RuntimeError(msg)

if INSURANCE_WIZARD_WIDGET_TEMPLATE_URI not in WIDGETS_BY_URI:
    msg = (
        "Insurance wizard widget must expose the correct template URI; "
        f"expected '{INSURANCE_WIZARD_WIDGET_TEMPLATE_URI}' in widgets"
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
        _get_quick_quote,
        _get_enhanced_quick_quote,
        _get_quick_quote_adaptive,
        _collect_personal_auto_customer,
        _collect_personal_auto_drivers,
        _collect_personal_auto_vehicles,
        _request_personal_auto_rate,
        _retrieve_personal_auto_rate_results,
        _start_wizard_flow,
        _submit_wizard_form,
    )
    from .models import (
        QuickQuoteIntake,
        EnhancedQuickQuoteIntake,
        CumulativeCustomerIntake,
        CumulativeDriverIntake,
        CumulativeVehicleIntake,
        PersonalAutoRateRequest,
        PersonalAutoRateResultsRequest,
    )
    from .utils import _model_schema
    from .constants import AIS_POLICY_COVERAGE_SUMMARY

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
                    "**STEP 3 - CALL THIS TOOL:**\n"
                    "Only after collecting ALL information from both steps, call this tool with the complete data.\n"
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

    # Register BASIC quick quote tool (fallback - minimal info only)
    register_tool(
        ToolRegistration(
            tool=types.Tool(
                name="get-quick-quote",
                title="Get basic auto insurance range (fallback)",
                description=(
                    "**FALLBACK TOOL** - Get a very rough quote range with minimal information (just zip code and number of drivers). "
                    "Returns broad placeholder premium ranges based only on location. "
                    "\n\n"
                    "⚠️ **Use enhanced-quick-quote instead for better accuracy!** Only use this tool if:\n"
                    "• User explicitly refuses to provide vehicle/driver details\n"
                    "• User wants the absolute fastest estimate with zero details\n"
                    "\n\n"
                    "The ranges are very wide and generic. After showing results, strongly encourage users to provide "
                    "actual details for a more accurate quote using get-enhanced-quick-quote."
                ),
                inputSchema=_model_schema(QuickQuoteIntake),
                _meta=quick_quote_meta,
            ),
            handler=_get_quick_quote,
            default_response_text="Generated rough quote range estimate. Consider using enhanced quote for better accuracy.",
            default_meta=quick_quote_default_meta,
        )
    )

    # Register ADAPTIVE quick quote tool (POC)
    register_tool(
        ToolRegistration(
            tool=types.Tool(
                name="get-quick-quote-adaptive",
                title="Get quick quote with adaptive field collection",
                description=(
                    "PROOF OF CONCEPT: Adaptive quick quote that uses configuration-driven field collection. "
                    "This tool can collect fields in any order based on the active flow configuration. "
                    "Supports multiple flow versions (v1: minimal, v2: with email, v3: with credit check). "
                    "Fields are validated against a centralized registry and collected progressively. "
                    "The tool will prompt for missing required fields dynamically."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "ZipCode": {"type": "string", "description": "5-digit zip code"},
                        "NumberOfDrivers": {"type": "integer", "description": "Number of drivers (1-10)"},
                        "EmailAddress": {"type": "string", "description": "Email address (optional)"},
                        "FirstName": {"type": "string", "description": "First name (for credit check flows)"},
                        "LastName": {"type": "string", "description": "Last name (for credit check flows)"},
                        "DateOfBirth": {"type": "string", "description": "Date of birth YYYY-MM-DD (for credit check flows)"},
                        "session_id": {"type": "string", "description": "Session ID for state tracking"},
                    },
                    "additionalProperties": False,
                },
            ),
            handler=_get_quick_quote_adaptive,
            default_response_text="Processing adaptive quick quote.",
        )
    )

    # Register customer collection tool (Batch 1)
    register_tool(
        ToolRegistration(
            tool=types.Tool(
                name="collect-personal-auto-customer",
                title="Collect personal auto customer information",
                description=(
                    "Collect and validate customer information for a personal auto quote. "
                    "This is Batch 1 of the conversational flow. Captures: name, address, "
                    "months at residence, and prior insurance status. "
                    "Returns validation status showing which required fields are still missing."
                ),
                inputSchema=_model_schema(CumulativeCustomerIntake),
            ),
            handler=_collect_personal_auto_customer,
            default_response_text="Captured customer information.",
        )
    )

    # Register driver collection tool (Batch 2)
    register_tool(
        ToolRegistration(
            tool=types.Tool(
                name="collect-personal-auto-drivers",
                title="Collect personal auto driver information",
                description=(
                    "Collect and validate driver information for a personal auto quote. "
                    "This is Batch 2 of the conversational flow. Captures: driver name, DOB, "
                    "gender, marital status, license info, and residency details. "
                    "Can also append missing customer fields from Batch 1 (forward-appending). "
                    "Returns validation status showing which required fields are still missing."
                ),
                inputSchema=_model_schema(CumulativeDriverIntake),
            ),
            handler=_collect_personal_auto_drivers,
            default_response_text="Captured driver information.",
        )
    )

    # Register vehicle collection tool (Batch 3)
    register_tool(
        ToolRegistration(
            tool=types.Tool(
                name="collect-personal-auto-vehicles",
                title="Collect personal auto vehicle information",
                description=(
                    "Collect and validate vehicle information for a personal auto quote. "
                    "This is Batch 3 of the conversational flow. Captures: VIN, year, make, model, "
                    "usage details, and coverage preferences. "
                    "Can also append missing customer or driver fields from earlier batches (forward-appending). "
                    "Returns validation status showing which required fields are still missing."
                ),
                inputSchema=_model_schema(CumulativeVehicleIntake),
            ),
            handler=_collect_personal_auto_vehicles,
            default_response_text="Captured vehicle information.",
        )
    )

    rate_results_widget = WIDGETS_BY_ID[INSURANCE_RATE_RESULTS_WIDGET_IDENTIFIER]
    rate_results_meta = {
        **_tool_meta(rate_results_widget),
        "openai/widgetAccessible": True,
    }
    rate_results_default_meta = {
        **rate_results_meta,
        "openai.com/widget": _embedded_widget_resource(rate_results_widget).model_dump(mode="json"),
    }

    rate_tool_description = (
        "Submit a fully populated personal auto quote request to the rating API and return the carrier response. "
        "Call this tool when the user provides complete rate request details (including customer, drivers, vehicles) "
        "or when the insurance widget sends you a structured rate request payload. "
        f"Coverage limits must match AIS enumerations ({AIS_POLICY_COVERAGE_SUMMARY}). "
        "The response will include a quote identifier that should be used for retrieving or comparing results."
    )

    rate_tool_meta = {
        "openai/widgetAccessible": True,
        "openai/resultCanProduceWidget": True,
        "openai.com/widget": _embedded_widget_resource(rate_results_widget).model_dump(
            mode="json"
        ),
        "annotations": {
            "destructiveHint": False,
            "openWorldHint": False,
            "readOnlyHint": False,
        },
    }

    register_tool(
        ToolRegistration(
            tool=types.Tool(
                name="request-personal-auto-rate",
                title="Request personal auto rate",
                description=rate_tool_description,
                inputSchema=_model_schema(PersonalAutoRateRequest),
                _meta=rate_tool_meta,
            ),
            handler=_request_personal_auto_rate,
            default_response_text="Submitted personal auto rating request.",
        )
    )

    register_tool(
        ToolRegistration(
            tool=types.Tool(
                name="retrieve-personal-auto-rate-results",
                title="Retrieve personal auto rate results",
                description=(
                    "Fetch carrier rate results for an existing personal auto quote using its identifier. "
                    "Use the quote identifier (Identifier field) from previous rate requests in this conversation. "
                    "When the user asks to 'compare quotes', 'show results', or 'get the latest quote', "
                    "use the most recent quote identifier from the conversation history."
                ),
                inputSchema=_model_schema(PersonalAutoRateResultsRequest),
                _meta=rate_results_meta,
            ),
            handler=_retrieve_personal_auto_rate_results,
            default_response_text="Retrieved personal auto rate results.",
            default_meta=rate_results_default_meta,
        )
    )

    # Register wizard flow tools
    wizard_widget = WIDGETS_BY_ID[INSURANCE_WIZARD_WIDGET_IDENTIFIER]
    wizard_meta = {
        **_tool_meta(wizard_widget),
        "openai/widgetAccessible": True,
    }
    wizard_default_meta = {
        **wizard_meta,
        "openai.com/widget": _embedded_widget_resource(wizard_widget).model_dump(mode="json"),
    }

    register_tool(
        ToolRegistration(
            tool=types.Tool(
                name="start-insurance-wizard",
                title="Start insurance application wizard",
                description=(
                    "Launch the multi-step insurance application wizard after presenting a quick quote. "
                    "This wizard guides users through 5 steps to collect complete policy, customer, vehicle, and driver information. "
                    "The wizard is fully config-driven and provides a structured form experience. "
                    "Use this tool when the user wants to proceed with a detailed quote after seeing quick quote results."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "zip_code": {
                            "type": "string",
                            "description": "Pre-fill zip code from quick quote"
                        },
                        "number_of_drivers": {
                            "type": "integer",
                            "description": "Pre-fill number of drivers from quick quote"
                        }
                    },
                    "additionalProperties": False,
                },
                _meta=wizard_meta,
            ),
            handler=_start_wizard_flow,
            default_response_text="Started insurance application wizard.",
            default_meta=wizard_default_meta,
        )
    )

    register_tool(
        ToolRegistration(
            tool=types.Tool(
                name="submit-wizard-form",
                title="Submit completed wizard form",
                description=(
                    "Process a completed wizard form submission and request personal auto rate. "
                    "This tool receives all collected data from the wizard and submits it to the rating API. "
                    "The wizard frontend will call this tool automatically when the user completes all steps and clicks submit."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "form_data": {
                            "type": "object",
                            "description": "Complete form data collected from wizard steps"
                        }
                    },
                    "required": ["form_data"],
                    "additionalProperties": False,
                },
            ),
            handler=_submit_wizard_form,
            default_response_text="Submitted wizard form for rating.",
        )
    )


# Initialize the registry
_register_default_tools()
_register_personal_auto_intake_tools()
