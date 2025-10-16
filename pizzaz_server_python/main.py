"""Pizzaz demo MCP server implemented with the Python FastMCP helper.

The server mirrors the Node example in this repository and exposes
widget-backed tools that render the Pizzaz UI bundle. Each handler returns the
HTML shell via an MCP resource and echoes the selected topping as structured
content so the ChatGPT client can hydrate the widget. The module also wires the
handlers into an HTTP/SSE stack so you can run the server with uvicorn on port
8000, matching the Node transport behavior."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    TypedDict,
)
import inspect
import json

import httpx
import mcp.types as types
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from .insurance_state_widget import INSURANCE_STATE_WIDGET_HTML


@dataclass(frozen=True)
class PizzazWidget:
    identifier: str
    title: str
    template_uri: str
    invoking: str
    invoked: str
    html: str
    response_text: str
    input_schema: Dict[str, Any]
    tool_description: Optional[str] = None


class ToolInvocationResult(TypedDict, total=False):
    """Result structure returned by tool handlers."""

    structured_content: Dict[str, Any]
    response_text: str
    content: Sequence[types.Content]
    meta: Dict[str, Any]


ToolHandler = Callable[[Mapping[str, Any]], ToolInvocationResult | Awaitable[ToolInvocationResult]]


@dataclass(frozen=True)
class ToolRegistration:
    """Registry entry for a tool."""

    tool: types.Tool
    handler: ToolHandler
    default_response_text: str
    default_meta: Optional[Dict[str, Any]] = None


TOOL_REGISTRY: Dict[str, ToolRegistration] = {}


def register_tool(registration: ToolRegistration) -> None:
    """Register a tool so it can be listed and invoked."""

    TOOL_REGISTRY[registration.tool.name] = registration


PIZZA_TOOL_INPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "pizzaTopping": {
            "type": "string",
            "description": "Topping to mention when rendering the widget.",
        }
    },
    "required": ["pizzaTopping"],
    "additionalProperties": False,
}


INSURANCE_STATE_INPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "state": {
            "type": "string",
            "description": "Two-letter U.S. state or District of Columbia abbreviation (for example, \"CA\").",
            "minLength": 2,
            "maxLength": 2,
            "pattern": "^[A-Za-z]{2}$",
        }
    },
    "required": [],
    "additionalProperties": False,
}


PERSONAL_AUTO_PRODUCTS_INPUT_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "state": {
            "type": "string",
            "description": (
                "Two-letter U.S. state or District of Columbia abbreviation (for example, \"CA\")."
            ),
            "minLength": 2,
            "maxLength": 2,
            "pattern": "^[A-Za-z]{2}$",
        }
    },
    "required": ["state"],
    "additionalProperties": False,
}


PERSONAL_AUTO_PRODUCTS_ENDPOINT = (
    "https://gateway.pre.zrater.io/api/v1/linesOfBusiness/personalAuto/states"
)

PERSONAL_AUTO_PRODUCTS_HEADERS = {
    "Accept": "application/json",
    "Cookie": "BCSI-CS-7883f85839ae9af9=1",
    "User-Agent": "insomnia/11.1.0",
    "x-api-key": "e57528b0-95b4-4efe-8870-caa0f8a95143",
}


WIDGETS: Tuple[PizzazWidget, ...] = (
    PizzazWidget(
        identifier="pizza-map",
        title="Show Pizza Map",
        template_uri="ui://widget/pizza-map.html",
        invoking="Hand-tossing a map",
        invoked="Served a fresh map",
        html=(
            "<div id=\"pizzaz-root\"></div>\n"
            "<link rel=\"stylesheet\" href=\"https://persistent.oaistatic.com/"
            "ecosystem-built-assets/pizzaz-0038.css\">\n"
            "<script type=\"module\" src=\"https://persistent.oaistatic.com/"
            "ecosystem-built-assets/pizzaz-0038.js\"></script>"
        ),
        response_text="Rendered a pizza map!",
        input_schema=PIZZA_TOOL_INPUT_SCHEMA,
    ),
    PizzazWidget(
        identifier="pizza-carousel",
        title="Show Pizza Carousel",
        template_uri="ui://widget/pizza-carousel.html",
        invoking="Carousel some spots",
        invoked="Served a fresh carousel",
        html=(
            "<div id=\"pizzaz-carousel-root\"></div>\n"
            "<link rel=\"stylesheet\" href=\"https://persistent.oaistatic.com/"
            "ecosystem-built-assets/pizzaz-carousel-0038.css\">\n"
            "<script type=\"module\" src=\"https://persistent.oaistatic.com/"
            "ecosystem-built-assets/pizzaz-carousel-0038.js\"></script>"
        ),
        response_text="Rendered a pizza carousel!",
        input_schema=PIZZA_TOOL_INPUT_SCHEMA,
    ),
    PizzazWidget(
        identifier="pizza-albums",
        title="Show Pizza Album",
        template_uri="ui://widget/pizza-albums.html",
        invoking="Hand-tossing an album",
        invoked="Served a fresh album",
        html=(
            "<div id=\"pizzaz-albums-root\"></div>\n"
            "<link rel=\"stylesheet\" href=\"https://persistent.oaistatic.com/"
            "ecosystem-built-assets/pizzaz-albums-0038.css\">\n"
            "<script type=\"module\" src=\"https://persistent.oaistatic.com/"
            "ecosystem-built-assets/pizzaz-albums-0038.js\"></script>"
        ),
        response_text="Rendered a pizza album!",
        input_schema=PIZZA_TOOL_INPUT_SCHEMA,
    ),
    PizzazWidget(
        identifier="pizza-list",
        title="Show Pizza List",
        template_uri="ui://widget/pizza-list.html",
        invoking="Hand-tossing a list",
        invoked="Served a fresh list",
        html=(
            "<div id=\"pizzaz-list-root\"></div>\n"
            "<link rel=\"stylesheet\" href=\"https://persistent.oaistatic.com/"
            "ecosystem-built-assets/pizzaz-list-0038.css\">\n"
            "<script type=\"module\" src=\"https://persistent.oaistatic.com/"
            "ecosystem-built-assets/pizzaz-list-0038.js\"></script>"
        ),
        response_text="Rendered a pizza list!",
        input_schema=PIZZA_TOOL_INPUT_SCHEMA,
    ),
    PizzazWidget(
        identifier="pizza-video",
        title="Show Pizza Video",
        template_uri="ui://widget/pizza-video.html",
        invoking="Hand-tossing a video",
        invoked="Served a fresh video",
        html=(
            "<div id=\"pizzaz-video-root\"></div>\n"
            "<link rel=\"stylesheet\" href=\"https://persistent.oaistatic.com/"
            "ecosystem-built-assets/pizzaz-video-0038.css\">\n"
            "<script type=\"module\" src=\"https://persistent.oaistatic.com/"
            "ecosystem-built-assets/pizzaz-video-0038.js\"></script>"
        ),
        response_text="Rendered a pizza video!",
        input_schema=PIZZA_TOOL_INPUT_SCHEMA,
    ),
    PizzazWidget(
        identifier="insurance-state-selector",
        title="Collect insurance state",
        template_uri="ui://widget/insurance-state.html",
        invoking="Collecting a customer's state",
        invoked="Captured the customer's state",
        html=INSURANCE_STATE_WIDGET_HTML,
        response_text="Let's confirm the customer's state before we continue with their insurance quote.",
        input_schema=INSURANCE_STATE_INPUT_SCHEMA,
        tool_description=
            "Collects the customer's U.S. state so the assistant can surface insurance options that apply there.",
    ),
)

widgets: Tuple[PizzazWidget, ...] = WIDGETS

INSURANCE_STATE_WIDGET_IDENTIFIER = "insurance-state-selector"
INSURANCE_STATE_WIDGET_TEMPLATE_URI = "ui://widget/insurance-state.html"


MIME_TYPE = "text/html+skybridge"


WIDGETS_BY_ID: Dict[str, PizzazWidget] = {widget.identifier: widget for widget in widgets}
WIDGETS_BY_URI: Dict[str, PizzazWidget] = {widget.template_uri: widget for widget in widgets}

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


class PizzaInput(BaseModel):
    """Schema for pizza tools."""

    pizza_topping: str = Field(
        ...,
        alias="pizzaTopping",
        description="Topping to mention when rendering the widget.",
    )

    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class InsuranceStateInput(BaseModel):
    """Schema for the insurance state selector tool."""

    state: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=2,
        pattern=r"^[A-Za-z]{2}$",
        description="Two-letter U.S. state or District of Columbia abbreviation (for example, \"CA\").",
    )

    model_config = ConfigDict(extra="forbid")

    @field_validator("state", mode="before")
    @classmethod
    def _strip_state(cls, value: Optional[str]) -> Optional[str]:
        if value is None or not isinstance(value, str):
            return value
        return value.strip()

    @field_validator("state")
    @classmethod
    def _normalize_state(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        if not isinstance(value, str):
            return value
        return value.upper()


class PersonalAutoProductsInput(BaseModel):
    """Schema for the personal auto products tool."""

    state: str = Field(
        min_length=2,
        max_length=2,
        pattern=r"^[A-Za-z]{2}$",
        description="Two-letter U.S. state or District of Columbia abbreviation (for example, \"CA\").",
    )

    model_config = ConfigDict(extra="forbid")

    @field_validator("state", mode="before")
    @classmethod
    def _strip_state(cls, value: Any) -> Any:
        if not isinstance(value, str):
            return value
        return value.strip()

    @field_validator("state")
    @classmethod
    def _normalize_state(cls, value: Any) -> Any:
        if not isinstance(value, str):
            return value
        return value.upper()


def _default_pizza_tool_handler(arguments: Mapping[str, Any]) -> ToolInvocationResult:
    payload = PizzaInput.model_validate(arguments)
    return {"structured_content": {"pizzaTopping": payload.pizza_topping}}


def _insurance_state_tool_handler(arguments: Mapping[str, Any]) -> ToolInvocationResult:
    payload = InsuranceStateInput.model_validate(arguments)
    state = payload.state
    if state:
        return {
            "structured_content": {"state": state},
            "response_text": f"Captured {state} as the customer's state.",
        }
    return {"structured_content": {}}


async def _fetch_personal_auto_products(arguments: Mapping[str, Any]) -> ToolInvocationResult:
    payload = PersonalAutoProductsInput.model_validate(arguments)
    state = payload.state
    url = (
        f"{PERSONAL_AUTO_PRODUCTS_ENDPOINT}/{state}/activeProducts"
    )

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
            response = await client.get(url, headers=PERSONAL_AUTO_PRODUCTS_HEADERS)
    except httpx.HTTPError as exc:
        raise RuntimeError(
            f"Failed to fetch personal auto products: {exc}"
        ) from exc

    status_code = response.status_code

    if status_code == 404:
        message = f"No active personal auto products found for {state}."
        return {
            "structured_content": {"state": state, "status": status_code, "products": []},
            "response_text": message,
        }

    if response.is_error:
        raise RuntimeError(
            f"Personal auto products request failed with status {status_code}"
        )

    raw_body = response.text
    parsed_body: Any = []
    if raw_body.strip():
        try:
            parsed_body = response.json()
        except (json.JSONDecodeError, ValueError) as exc:
            raise RuntimeError(
                f"Failed to parse personal auto products response: {exc}"
            ) from exc

    products = parsed_body if isinstance(parsed_body, list) else []
    message = (
        f"Found {len(products)} active personal auto product{'s' if len(products) != 1 else ''} for {state}."
        if products
        else f"No active personal auto products found for {state}."
    )

    return {
        "structured_content": {
            "state": state,
            "status": status_code,
            "products": products,
        },
        "response_text": message,
    }


mcp = FastMCP(
    name="pizzaz-python",
    sse_path="/mcp",
    message_path="/mcp/messages",
    stateless_http=True,
)


def _resource_description(widget: PizzazWidget) -> str:
    return f"{widget.title} widget markup"


def _tool_meta(widget: PizzazWidget) -> Dict[str, Any]:
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


def _embedded_widget_resource(widget: PizzazWidget) -> types.EmbeddedResource:
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
    for widget in widgets:
        handler = (
            _insurance_state_tool_handler
            if widget.identifier == INSURANCE_STATE_WIDGET_IDENTIFIER
            else _default_pizza_tool_handler
        )

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

        register_tool(
            ToolRegistration(
                tool=tool,
                handler=handler,
                default_response_text=widget.response_text,
                default_meta=default_meta,
            )
        )

    register_tool(
        ToolRegistration(
            tool=types.Tool(
                name="fetch-personal-auto-products",
                title="Fetch personal auto products",
                description="Retrieve active personal auto insurance products for a given state.",
                inputSchema=deepcopy(PERSONAL_AUTO_PRODUCTS_INPUT_SCHEMA),
            ),
            handler=_fetch_personal_auto_products,
            default_response_text="Retrieved personal auto product availability.",
        )
    )


_register_default_tools()


@mcp._mcp_server.list_tools()
async def _list_tools() -> List[types.Tool]:
    return [deepcopy(registration.tool) for registration in TOOL_REGISTRY.values()]


@mcp._mcp_server.list_resources()
async def _list_resources() -> List[types.Resource]:
    return [
        types.Resource(
            name=widget.title,
            title=widget.title,
            uri=widget.template_uri,
            description=_resource_description(widget),
            mimeType=MIME_TYPE,
            _meta=_tool_meta(widget),
        )
        for widget in widgets
    ]


@mcp._mcp_server.list_resource_templates()
async def _list_resource_templates() -> List[types.ResourceTemplate]:
    return [
        types.ResourceTemplate(
            name=widget.title,
            title=widget.title,
            uriTemplate=widget.template_uri,
            description=_resource_description(widget),
            mimeType=MIME_TYPE,
            _meta=_tool_meta(widget),
        )
        for widget in widgets
    ]


async def _handle_read_resource(req: types.ReadResourceRequest) -> types.ServerResult:
    widget = WIDGETS_BY_URI.get(str(req.params.uri))
    if widget is None:
        return types.ServerResult(
            types.ReadResourceResult(
                contents=[],
                _meta={"error": f"Unknown resource: {req.params.uri}"},
            )
        )

    contents = [
        types.TextResourceContents(
            uri=widget.template_uri,
            mimeType=MIME_TYPE,
            text=widget.html,
            _meta=_tool_meta(widget),
        )
    ]

    return types.ServerResult(types.ReadResourceResult(contents=contents))


async def _call_tool_request(req: types.CallToolRequest) -> types.ServerResult:
    registration = TOOL_REGISTRY.get(req.params.name)
    if registration is None:
        return types.ServerResult(
            types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=f"Unknown tool: {req.params.name}",
                    )
                ],
                isError=True,
            )
        )

    arguments: Mapping[str, Any] = req.params.arguments or {}

    try:
        handler_result = registration.handler(arguments)
        if inspect.isawaitable(handler_result):
            handler_result = await handler_result
    except ValidationError as exc:
        return types.ServerResult(
            types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=f"Input validation error: {exc.errors()}",
                    )
                ],
                isError=True,
            )
        )
    except Exception as exc:  # pragma: no cover - defensive safety net
        return types.ServerResult(
            types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=f"Tool execution error: {exc}",
                    )
                ],
                isError=True,
            )
        )

    handler_payload: ToolInvocationResult = handler_result or {}
    structured_content = handler_payload.get("structured_content") or {}
    response_text = (
        handler_payload.get("response_text") or registration.default_response_text
    )
    content = handler_payload.get("content")
    if content is None:
        content = [types.TextContent(type="text", text=response_text)]
    meta = handler_payload.get("meta") or registration.default_meta

    return types.ServerResult(
        types.CallToolResult(
            content=list(content),
            structuredContent=structured_content,
            _meta=meta,
        )
    )
mcp._mcp_server.request_handlers[types.CallToolRequest] = _call_tool_request
mcp._mcp_server.request_handlers[types.ReadResourceRequest] = _handle_read_resource


app = mcp.streamable_http_app()

try:
    from starlette.middleware.cors import CORSMiddleware

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=False,
    )
except Exception:
    pass


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("pizzaz_server_python.main:app", host="0.0.0.0", port=8000)
