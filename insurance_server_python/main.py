"""Insurance MCP server implemented with the Python FastMCP helper.

The server focuses exclusively on insurance workflows. It registers tools for
collecting quoting details and exposes the insurance state selector widget as a
reusable resource so the ChatGPT client can render it inline."""

from __future__ import annotations

import inspect
import json
import logging
import os
from copy import deepcopy
from typing import Any, List, Mapping

import mcp.types as types
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from pydantic import ValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse

from .widget_registry import (
    TOOL_REGISTRY,
    WIDGETS_BY_URI,
    widgets,
    _resource_description,
    _tool_meta,
)

# Configure logging
logger = logging.getLogger(__name__)

load_dotenv()

_configured_log_level = (
    os.getenv("INSURANCE_LOG_LEVEL")
    or os.getenv("LOG_LEVEL")
    or os.getenv("UVICORN_LOG_LEVEL")
    or "INFO"
)
try:
    _log_level_value = getattr(logging, _configured_log_level.upper(), logging.INFO)
except AttributeError:  # pragma: no cover - defensive guard for unexpected values
    _log_level_value = logging.INFO

root_logger = logging.getLogger()
if not root_logger.handlers:
    logging.basicConfig(level=_log_level_value)

logger.setLevel(_log_level_value)

# Initialize FastMCP server
mcp = FastMCP(
    name="insurance-python",
    sse_path="/mcp",
    message_path="/mcp/messages",
    stateless_http=True,
)


# MCP protocol handlers
@mcp._mcp_server.list_tools()
async def _list_tools() -> List[types.Tool]:
    """List all available tools."""
    return [deepcopy(registration.tool) for registration in TOOL_REGISTRY.values()]


@mcp._mcp_server.list_resources()
async def _list_resources() -> List[types.Resource]:
    """List all available widget resources."""
    return [
        types.Resource(
            name=widget.title,
            title=widget.title,
            uri=widget.template_uri,
            description=_resource_description(widget),
            mimeType="text/html+skybridge",
            _meta=_tool_meta(widget),
        )
        for widget in widgets
    ]


@mcp._mcp_server.list_resource_templates()
async def _list_resource_templates() -> List[types.ResourceTemplate]:
    """List all available resource templates."""
    return [
        types.ResourceTemplate(
            name=widget.title,
            title=widget.title,
            uriTemplate=widget.template_uri,
            description=_resource_description(widget),
            mimeType="text/html+skybridge",
            _meta=_tool_meta(widget),
        )
        for widget in widgets
    ]


async def _handle_read_resource(req: types.ReadResourceRequest) -> types.ServerResult:
    """Handle resource read requests."""
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
            mimeType="text/html+skybridge",
            text=widget.html,
            _meta=_tool_meta(widget),
        )
    ]

    return types.ServerResult(types.ReadResourceResult(contents=contents))


async def _call_tool_request(req: types.CallToolRequest) -> types.ServerResult:
    """Handle tool call requests."""
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
        logger.exception(
            "Validation error while invoking tool '%s' with arguments %s",
            req.params.name,
            arguments,
        )
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
        logger.exception(
            "Unhandled exception while invoking tool '%s' with arguments %s",
            req.params.name,
            arguments,
        )
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

    handler_payload = handler_result or {}
    structured_content = handler_payload.get("structured_content") or {}
    response_text = handler_payload.get("response_text")
    if response_text is None:
        response_text = registration.default_response_text
    content = handler_payload.get("content")
    if content is None:
        if response_text is not None:
            content = [types.TextContent(type="text", text=response_text)]
        else:
            content = []
    meta = handler_payload.get("meta") or registration.default_meta

    # Log what we're sending for key tools
    if req.params.name in ["request-personal-auto-rate", "retrieve-personal-auto-rate-results"]:
        logger.info("=== TOOL HANDLER SENDING RESPONSE FOR %s ===", req.params.name)
        logger.info("Content array length: %s", len(content))
        for idx, item in enumerate(content):
            logger.info("Content[%s] type: %s", idx, item.type)
            if hasattr(item, 'text'):
                logger.info("Content[%s] text preview: %s", idx, item.text[:200] if item.text else "None")
            if hasattr(item, 'annotations') and item.annotations:
                logger.info("Content[%s] annotations: %s", idx, item.annotations.model_dump(mode="json"))
        logger.info("Structured content keys: %s", list(structured_content.keys()))
        if "rate_results" in structured_content:
            rate_results = structured_content["rate_results"]
            logger.info("rate_results type: %s", type(rate_results))
            if isinstance(rate_results, dict):
                logger.info("rate_results keys: %s", list(rate_results.keys()))
        logger.info("Meta keys: %s", list(meta.keys()) if meta else "None")
        logger.info("=== END TOOL HANDLER RESPONSE ===")

    return types.ServerResult(
        types.CallToolResult(
            content=list(content),
            structuredContent=structured_content,
            _meta=meta,
        )
    )


# Register custom handlers
mcp._mcp_server.request_handlers[types.CallToolRequest] = _call_tool_request
mcp._mcp_server.request_handlers[types.ReadResourceRequest] = _handle_read_resource

# Create the ASGI app
app = mcp.streamable_http_app()


# Initialize schema parser on startup
@app.on_event("startup")
async def startup_event():
    """Initialize schema parser and fetch contracts on server startup."""
    from .schema_parser import initialize_schema_parser

    api_key = os.getenv("PERSONAL_AUTO_RATE_API_KEY")
    if api_key:
        try:
            await initialize_schema_parser(api_key, states=["CA"])
            logger.info("Schema parser initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize schema parser: {e}")
            logger.warning("Server will continue without schema-based minimal fields")
    else:
        logger.warning("PERSONAL_AUTO_RATE_API_KEY not set, schema parser not initialized")


async def _legacy_call_tool_route(request: Request) -> JSONResponse:
    """Handle legacy ``callTool`` HTTP requests.

    Older MCP HTTP clients (including early Apps SDK builds) issue JSON-RPC
    requests using the pre-2024-10 method name ``callTool`` and expect a JSON
    response body rather than an SSE stream. The FastMCP transport now requires
    the newer ``tools/call`` method literal and enforces ``text/event-stream``
    negotiation, which causes the legacy clients to fail before the tool handler
    runs. This adapter normalizes those requests so the rest of the server can
    reuse the canonical handler logic.
    """

    try:
        payload = await request.json()
    except json.JSONDecodeError as exc:
        return JSONResponse(
            {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {exc}",
                },
            },
            status_code=400,
        )

    method = payload.get("method")
    if method != "callTool":
        return JSONResponse(
            {
                "jsonrpc": "2.0",
                "id": payload.get("id"),
                "error": {
                    "code": -32601,
                    "message": f"Unsupported method: {method}",
                },
            },
            status_code=405,
        )

    # Clone the payload but swap in the protocol-compliant method name so we
    # can delegate back to the shared handler.
    normalized_payload = {**payload, "method": "tools/call"}

    try:
        call_request = types.CallToolRequest.model_validate(normalized_payload)
    except ValidationError as exc:
        return JSONResponse(
            {
                "jsonrpc": "2.0",
                "id": payload.get("id"),
                "error": {
                    "code": -32602,
                    "message": "Invalid request parameters",
                    "data": exc.errors(),
                },
            },
            status_code=400,
        )

    server_result = await _call_tool_request(call_request)
    response_payload = server_result.model_dump(mode="json")

    # Legacy clients expect a JSON-RPC response envelope with either ``result``
    # or ``error``. ``ServerResult`` always wraps a ``CallToolResult`` so we
    # surface it as a ``result`` here.
    return JSONResponse({"jsonrpc": "2.0", "id": payload.get("id"), "result": response_payload})


# Add legacy route
app.add_route("/mcp/messages", _legacy_call_tool_route, methods=["POST"])


# Serve minimal fields config
from pathlib import Path

@app.route("/api/minimal-fields-config", methods=["GET"])
async def get_minimal_fields_config(request: Request):
    """Serve the minimal fields configuration."""
    config_path = Path(__file__).parent.parent / "minimal_fields_config.json"
    if config_path.exists():
        with open(config_path) as f:
            config_data = json.load(f)
        return JSONResponse(
            config_data,
            headers={"Access-Control-Allow-Origin": "*"}
        )
    logger.error(f"Config file not found at: {config_path}")
    return JSONResponse({"error": "Config file not found"}, status_code=404)

# Add CORS middleware
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


# Entry point
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("insurance_server_python.main:app", host="0.0.0.0", port=8000)
