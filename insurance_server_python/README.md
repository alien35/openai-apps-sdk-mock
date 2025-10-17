# Insurance MCP server (Python)

This directory packages a Python implementation of the insurance demo server using the `FastMCP` helper from the official Model Context Protocol SDK. It focuses on insurance intake flows by exposing the insurance state selector alongside tools that validate customer, driver, vehicle, coverage, carrier, roster, and rating details.

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

This boots a FastAPI app with uvicorn on `http://127.0.0.1:8000` (equivalently `uvicorn insurance_server_python.main:app --host 0.0.0.0 --port 8000`). The endpoints mirror the Node demo:

- `GET /mcp` exposes the SSE stream.
- `POST /mcp/messages?sessionId=...` accepts follow-up messages for an active session.

Cross-origin requests are allowed so you can drive the server from local tooling or the MCP Inspector. Each tool returns structured content and metadata that point to the insurance widget shell so the Apps SDK can hydrate the UI alongside assistant responses.

## Insurance state selector checklist

Follow this quick validation list if the insurance picker does not appear in your client:

1. **Confirm the widget is registered.** `list_tools`, `list_resources`, or `list_resource_templates` should include `insurance-state-selector` with the template URI `ui://widget/insurance-state.html`.
2. **Restart the Python server.** Run `uvicorn insurance_server_python.main:app --host 0.0.0.0 --port 8000` after pulling changes so the updated handlers and HTML load.
3. **Point the client at the Python endpoint.** Update your MCP client configuration to use the `insurance-python` server you just restarted, then reload the session so the tool list refreshes.
4. **Invoke the tool manually.** Issue a `call_tool` request with `{"name": "insurance-state-selector", "arguments": {}}` to bring up the dropdown UI. Passing `{ "state": "CA" }` should pre-select California and return the normalized code in `structuredContent`.

If those steps succeed but the picker still fails to render during normal conversations, verify your client isn't caching an older tool schema and that the request identifier matches `insurance-state-selector` exactly.

## Next steps

Use these handlers as a starting point when wiring in real data, authentication, or localization support. The structure demonstrates how to:

1. Register reusable UI resources that load static HTML bundles.
2. Associate tools with those widgets via `_meta.openai/outputTemplate`.
3. Ship structured JSON alongside human-readable confirmation text.


### Auto quoting flow overview

The personal auto quoting tools now support a staged approach for gathering driver information:

1. **`collect-personal-auto-driver-roster`** accepts a lightweight roster containing driver identifiers and names. This provides a quick confirmation of who should be rated before the assistant dives into full profile collection.
2. **`collect-personal-auto-drivers`** remains available for validating the complete rated driver payload once the broader intake conversation is underway.

Pair the roster tool with the existing customer, vehicle, coverage, carrier, and rating handlers to flexibly capture the details needed for a quote while still keeping the assistant's responses concise and confirmatory.

### Intake plan

When walking through the personal auto intake plan, the assistant can now capture quote-level selections independently before submitting the full rating package. Use **`collect-personal-auto-quote-options`** to confirm the quote identifier, effective date, policy type, term, payment method, and related options alongside the existing customer, driver, vehicle, and carrier tools.
