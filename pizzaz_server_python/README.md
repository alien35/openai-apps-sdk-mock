# Pizzaz MCP server (Python)

This directory packages a Python implementation of the Pizzaz demo server using the `FastMCP` helper from the official Model Context Protocol SDK. It mirrors the Node example and exposes each pizza widget as both a resource and a tool. The insurance state selector is registered alongside the pizza demos so the assistant can reliably prompt for the customer's location before quoting coverage.

## Prerequisites

- Python 3.10+
- A virtual environment (recommended)

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> **Heads up:** There is a similarly named package named `modelcontextprotocol`
> on PyPI that is unrelated to the official MCP SDK. The requirements file
> installs the official `mcp` distribution with its FastAPI extra so that the
> `mcp.server.fastmcp` module is available. If you previously installed the
> other project, run `pip uninstall modelcontextprotocol` before reinstalling
> the requirements.

## Run the server

```bash
python main.py
```

This boots a FastAPI app with uvicorn on `http://127.0.0.1:8000` (equivalently `uvicorn pizzaz_server_python.main:app --host 0.0.0.0 --port 8000`). The endpoints mirror the Node demo:

- `GET /mcp` exposes the SSE stream.
- `POST /mcp/messages?sessionId=...` accepts follow-up messages for an active session.

Cross-origin requests are allowed so you can drive the server from local tooling or the MCP Inspector. Each tool returns structured content that echoes the requested topping plus metadata that points to the correct Skybridge widget shell, matching the original Pizzaz documentation.

## Insurance state selector checklist

Follow this quick validation list if the insurance picker does not appear in your client:

1. **Confirm the widget is registered.** `list_tools`, `list_resources`, or `list_resource_templates` should include `insurance-state-selector` with the template URI `ui://widget/insurance-state.html`.
2. **Restart the Python server.** Run `uvicorn pizzaz_server_python.main:app --host 0.0.0.0 --port 8000` after pulling changes so the updated handlers and HTML load.
3. **Point the client at the Python endpoint.** Update your MCP client configuration to use the `pizzaz-python` server you just restarted, then reload the session so the tool list refreshes.
4. **Invoke the tool manually.** Issue a `call_tool` request with `{"name": "insurance-state-selector", "arguments": {}}` to bring up the dropdown UI. Passing `{ "state": "CA" }` should pre-select California and return the normalized code in `structuredContent`.

If those steps succeed but the picker still fails to render during normal conversations, verify your client isn't caching an older tool schema and that the request identifier matches `insurance-state-selector` exactly.

## Next steps

Use these handlers as a starting point when wiring in real data, authentication, or localization support. The structure demonstrates how to:

1. Register reusable UI resources that load static HTML bundles.
2. Associate tools with those widgets via `_meta.openai/outputTemplate`.
3. Ship structured JSON alongside human-readable confirmation text.
