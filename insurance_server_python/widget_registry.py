"""Widget definitions and tool registry for the insurance server."""

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple
import mcp.types as types

from .insurance_state_widget import INSURANCE_STATE_WIDGET_HTML
from .insurance_rate_results_widget import INSURANCE_RATE_RESULTS_WIDGET_HTML
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
        _collect_personal_auto_customer,
        _collect_personal_auto_drivers,
        _collect_personal_auto_vehicles,
        _request_personal_auto_rate,
        _retrieve_personal_auto_rate_results,
    )
    from .models import (
        CumulativeCustomerIntake,
        CumulativeDriverIntake,
        CumulativeVehicleIntake,
        PersonalAutoRateRequest,
        PersonalAutoRateResultsRequest,
    )
    from .utils import _model_schema
    from .constants import AIS_POLICY_COVERAGE_SUMMARY

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


# Initialize the registry
_register_default_tools()
_register_personal_auto_intake_tools()
