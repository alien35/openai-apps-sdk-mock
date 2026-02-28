"""Insurance MCP server implemented with the Python FastMCP helper.

The server focuses exclusively on insurance workflows. It registers tools for
collecting quoting details and exposes the insurance state selector widget as a
reusable resource so the ChatGPT client can render it inline."""

from __future__ import annotations

import inspect
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
    if req.params.name in ["request-personal-auto-rate", "retrieve-personal-auto-rate-results", "get-enhanced-quick-quote"]:
        logger.info("=== TOOL HANDLER SENDING RESPONSE FOR %s ===", req.params.name)
        logger.info("Content array length: %s", len(content))
        for idx, item in enumerate(content):
            logger.info("Content[%s] type: %s", idx, item.type)
            if hasattr(item, 'text'):
                logger.info("Content[%s] text preview: %s", idx, item.text[:200] if item.text else "None")
            if hasattr(item, 'annotations') and item.annotations:
                logger.info("Content[%s] annotations: %s", idx, item.annotations.model_dump(mode="json"))
        logger.info("Structured content keys: %s", list(structured_content.keys()))

        # Log carriers if present
        if "carriers" in structured_content:
            carriers = structured_content["carriers"]
            logger.info("!!! CARRIERS IN STRUCTURED_CONTENT: %s", len(carriers))
            for i, carrier in enumerate(carriers):
                logger.info("  Carrier %s: %s - $%s/year ($%s/month)",
                           i+1, carrier.get('name'), carrier.get('annual_cost'), carrier.get('monthly_cost'))
        else:
            logger.warning("!!! NO CARRIERS IN STRUCTURED_CONTENT !!!")

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


# Health check endpoint
@app.route("/health", methods=["GET"])
def health_check(request: Request):
    """Health check endpoint for container orchestration."""
    return JSONResponse({"status": "healthy"})


# Root endpoint
@app.route("/", methods=["GET"])
def root(request: Request):
    """Root endpoint."""
    return JSONResponse({"service": "insurance-mcp-server", "status": "running"})


# OpenAPI spec generation
def generate_openapi_spec():
    """Generate OpenAPI 3.0 specification for the API."""
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "Insurance MCP Server API",
            "version": "1.0.0",
            "description": "Insurance quoting and data collection API with MCP integration",
            "contact": {
                "name": "API Support",
                "url": "https://github.com/anthropics/openai-apps-sdk-examples"
            }
        },
        "servers": [
            {
                "url": "http://localhost:8000",
                "description": "Local development server"
            }
        ],
        "paths": {
            "/": {
                "get": {
                    "summary": "Root endpoint",
                    "description": "Returns service information and status",
                    "tags": ["Health"],
                    "responses": {
                        "200": {
                            "description": "Service information",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "service": {"type": "string", "example": "insurance-mcp-server"},
                                            "status": {"type": "string", "example": "running"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/health": {
                "get": {
                    "summary": "Health check",
                    "description": "Health check endpoint for container orchestration",
                    "tags": ["Health"],
                    "responses": {
                        "200": {
                            "description": "Service is healthy",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string", "example": "healthy"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/quick-quote-carriers": {
                "get": {
                    "summary": "Get carrier estimates",
                    "description": "Returns carrier estimates for quick quote widget based on state",
                    "tags": ["Quotes"],
                    "parameters": [
                        {
                            "name": "state",
                            "in": "query",
                            "description": "State code (e.g., CA, TX, NY)",
                            "schema": {
                                "type": "string",
                                "default": "CA"
                            }
                        },
                        {
                            "name": "zip_code",
                            "in": "query",
                            "description": "ZIP code",
                            "schema": {
                                "type": "string",
                                "default": "90210"
                            }
                        },
                        {
                            "name": "city",
                            "in": "query",
                            "description": "City name",
                            "schema": {
                                "type": "string",
                                "default": "Beverly Hills"
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Carrier estimates",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "carriers": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "name": {"type": "string"},
                                                        "logo": {"type": "string"},
                                                        "annual_cost": {"type": "integer"},
                                                        "monthly_cost": {"type": "integer"},
                                                        "notes": {"type": "string"}
                                                    }
                                                }
                                            },
                                            "zip_code": {"type": "string"},
                                            "city": {"type": "string"},
                                            "state": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/assets/images/{filename}": {
                "get": {
                    "summary": "Serve static images",
                    "description": "Serves static images from assets/images directory",
                    "tags": ["Assets"],
                    "parameters": [
                        {
                            "name": "filename",
                            "in": "path",
                            "required": True,
                            "description": "Image filename",
                            "schema": {
                                "type": "string"
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Image file",
                            "content": {
                                "image/*": {
                                    "schema": {
                                        "type": "string",
                                        "format": "binary"
                                    }
                                }
                            }
                        },
                        "404": {
                            "description": "Image not found"
                        }
                    }
                }
            }
        },
        "tags": [
            {
                "name": "Health",
                "description": "Health check and service status endpoints"
            },
            {
                "name": "Quotes",
                "description": "Insurance quote and carrier information"
            },
            {
                "name": "Assets",
                "description": "Static asset serving"
            }
        ]
    }


# OpenAPI spec endpoint
@app.route("/openapi.json", methods=["GET"])
def openapi_spec(request: Request):
    """Serve OpenAPI specification."""
    return JSONResponse(generate_openapi_spec())


# Swagger UI endpoint
@app.route("/docs", methods=["GET"])
def swagger_ui(request: Request):
    """Serve Swagger UI for API documentation."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Insurance MCP API - Swagger UI</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.10.5/swagger-ui.css">
        <style>
            body { margin: 0; padding: 0; }
        </style>
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.10.5/swagger-ui-bundle.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.10.5/swagger-ui-standalone-preset.js"></script>
        <script>
            window.onload = function() {
                SwaggerUIBundle({
                    url: "/openapi.json",
                    dom_id: '#swagger-ui',
                    presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIStandalonePreset
                    ],
                    layout: "BaseLayout",
                    deepLinking: true
                });
            };
        </script>
    </body>
    </html>
    """
    from starlette.responses import HTMLResponse
    return HTMLResponse(html)


# ReDoc endpoint (alternative documentation UI)
@app.route("/redoc", methods=["GET"])
def redoc_ui(request: Request):
    """Serve ReDoc UI for API documentation."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Insurance MCP API - ReDoc</title>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { margin: 0; padding: 0; }
        </style>
    </head>
    <body>
        <redoc spec-url="/openapi.json"></redoc>
        <script src="https://cdn.jsdelivr.net/npm/redoc@2.1.3/bundles/redoc.standalone.js"></script>
    </body>
    </html>
    """
    from starlette.responses import HTMLResponse
    return HTMLResponse(html)


@app.route("/api/quick-quote-carriers", methods=["GET"])
async def get_quick_quote_carriers(request: Request):
    """Serve carrier estimates for quick quote widget based on state."""
    from .carrier_logos import get_carrier_logo
    from .carrier_mapping import get_carriers_for_state

    # Get state from query params (default to California)
    state = request.query_params.get("state", "CA")

    # Get state-specific carriers
    carrier_names = get_carriers_for_state(state)

    # Build carrier list with logos and sample pricing
    carriers = []
    base_prices = [3200, 3600, 4000]  # Sample pricing tiers

    for i, carrier_name in enumerate(carrier_names):
        annual_cost = base_prices[i] if i < len(base_prices) else 3500
        carriers.append({
            "name": carrier_name,
            "logo": get_carrier_logo(carrier_name),
            "annual_cost": annual_cost,
            "monthly_cost": annual_cost // 12,
            "notes": "Competitive rates and service"
        })

    return JSONResponse(
        {
            "carriers": carriers,
            "zip_code": request.query_params.get("zip_code", "90210"),
            "city": request.query_params.get("city", "Beverly Hills"),
            "state": state
        },
        headers={"Access-Control-Allow-Origin": "*"}
    )


@app.route("/assets/images/{filename}", methods=["GET"])
async def serve_image(request: Request):
    """Serve static images and widget HTML from assets/images directory."""
    from pathlib import Path
    from starlette.responses import FileResponse, HTMLResponse
    from .widget_registry import BASE_URL

    filename = request.path_params["filename"]
    file_path = Path(__file__).parent / "assets" / "images" / filename

    if not file_path.exists():
        return JSONResponse({"error": "File not found"}, status_code=404)

    # Serve HTML files with CSP headers for ChatGPT compatibility
    if filename.endswith('.html'):
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        return HTMLResponse(
            html_content,
            headers={
                "Content-Security-Policy": (
                    f"default-src 'none'; "
                    f"script-src 'self' 'unsafe-inline'; "
                    f"style-src 'self' 'unsafe-inline'; "
                    f"img-src 'self' data:; "
                    f"font-src 'self'; "
                    f"connect-src 'self' {BASE_URL}; "
                    f"frame-ancestors https://chatgpt.com https://chat.openai.com;"
                ),
                "Access-Control-Allow-Origin": "https://chatgpt.com",
                "X-Content-Type-Options": "nosniff",
                "Cache-Control": "public, max-age=3600",
            }
        )

    # Serve images normally
    return FileResponse(
        file_path,
        headers={"Access-Control-Allow-Origin": "*"}
    )


@app.route("/test-widget", methods=["GET"])
async def test_widget(request: Request):
    """Serve the quick quote widget HTML for testing."""
    from starlette.responses import HTMLResponse
    from .quick_quote_results_widget import QUICK_QUOTE_RESULTS_WIDGET_HTML

    return HTMLResponse(
        QUICK_QUOTE_RESULTS_WIDGET_HTML,
        headers={"Access-Control-Allow-Origin": "*"}
    )


@app.route("/preview", methods=["GET"])
async def preview_widget(request: Request):
    """Serve a comprehensive widget preview page with embedded data."""
    from starlette.responses import HTMLResponse
    from .quick_quote_results_widget import QUICK_QUOTE_RESULTS_WIDGET_HTML

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Quick Quote Widget - Live Preview</title>
        <style>
            body {{
                margin: 0;
                padding: 20px;
                background: #f5f5f5;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }}
            .preview-container {{
                max-width: 1400px;
                margin: 0 auto;
            }}
            h1 {{
                text-align: center;
                margin-bottom: 30px;
                color: #333;
            }}
        </style>
    </head>
    <body>
        <div class="preview-container">
            <h1>Quick Quote Widget - Live Preview (Normal State)</h1>
            {QUICK_QUOTE_RESULTS_WIDGET_HTML}
        </div>

        <script>
            // Set up the OpenAI globals object with sample data
            window.openai = {{
                toolOutput: {{
                    carriers: [
                        {{
                            name: "Geico",
                            logo: "/assets/images/mercury-logo.png",
                            annual_cost: 3100,
                            monthly_cost: 258
                        }},
                        {{
                            name: "Progressive Insurance",
                            logo: "/assets/images/progressive.png",
                            annual_cost: 3600,
                            monthly_cost: 300
                        }},
                        {{
                            name: "Safeco Insurance",
                            logo: "/assets/images/orion.png",
                            annual_cost: 3800,
                            monthly_cost: 317
                        }}
                    ],
                    zip_code: "92821",
                    city: "Brea",
                    state: "CA",
                    num_drivers: 1,
                    num_vehicles: 1
                }}
            }};

            // Trigger hydration after a brief delay
            setTimeout(() => {{
                console.log('Triggering widget hydration with data:', window.openai.toolOutput);
                const event = new CustomEvent('openai:set_globals', {{
                    detail: {{
                        globals: window.openai
                    }}
                }});
                window.dispatchEvent(event);
            }}, 100);
        </script>
    </body>
    </html>
    """

    return HTMLResponse(html)


@app.route("/preview-phone", methods=["GET"])
async def preview_phone_widget(request: Request):
    """Serve a preview of the phone-only state widget."""
    from starlette.responses import HTMLResponse
    from .quick_quote_results_widget import QUICK_QUOTE_RESULTS_WIDGET_HTML

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Quick Quote Widget - Phone-Only State Preview</title>
        <style>
            body {{
                margin: 0;
                padding: 20px;
                background: #f5f5f5;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }}
            .preview-container {{
                max-width: 1400px;
                margin: 0 auto;
            }}
            h1 {{
                text-align: center;
                margin-bottom: 30px;
                color: #333;
            }}
        </style>
    </head>
    <body>
        <div class="preview-container">
            <h1>Quick Quote Widget - Phone-Only State (Alaska)</h1>
            {QUICK_QUOTE_RESULTS_WIDGET_HTML}
        </div>

        <script>
            // Set up the OpenAI globals object with phone-only state (Alaska)
            window.openai = {{
                toolOutput: {{
                    carriers: [],  // Empty carriers array for phone-only states
                    zip_code: "99501",
                    city: "Anchorage",
                    state: "AK",
                    num_drivers: 1,
                    num_vehicles: 1,
                    lookup_failed: false
                }}
            }};

            // Trigger hydration after a brief delay
            setTimeout(() => {{
                console.log('Triggering phone-only widget hydration with data:', window.openai.toolOutput);
                const event = new CustomEvent('openai:set_globals', {{
                    detail: {{
                        globals: window.openai
                    }}
                }});
                window.dispatchEvent(event);
            }}, 100);
        </script>
    </body>
    </html>
    """

    return HTMLResponse(html)


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

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
