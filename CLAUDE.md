# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a gallery of example UI components built with the Apps SDK, designed to work with the Model Context Protocol (MCP). The repo demonstrates how to build rich UI widgets that ChatGPT can render inline when calling MCP server tools. It includes both the frontend widget components (React/TypeScript) and Python MCP servers that expose these widgets as tools.

## Key Concepts

**MCP + Apps SDK Architecture:**
- MCP servers expose tools that return structured content + `_meta.openai/outputTemplate` metadata
- The Apps SDK uses this metadata to render rich UI widgets alongside assistant messages
- Widgets are bundled into standalone HTML/JS/CSS files that MCP servers serve as reusable resources
- Each widget entry point lives in `src/{widget-name}/index.tsx` or `src/{widget-name}/index.jsx`

**Build System:**
- `build-all.mts` orchestrates the Vite build for all widget entry points
- Each widget is bundled with its CSS into versioned `.html`, `.js`, and `.css` files in `assets/`
- Bundles are hashed based on `package.json` version to enable caching
- Final HTML bundles inline both CSS and JS for easy serving

## Common Commands

### Frontend Development
```bash
# Install dependencies (uses pnpm)
pnpm install

# Build all widget bundles (produces hashed files in assets/)
pnpm run build

# Dev mode with hot reload
pnpm run dev

# Serve static assets (for testing bundles without MCP)
pnpm run serve

# TypeScript checks
pnpm run tsc           # Check all TS
pnpm run tsc:app       # Check app code
pnpm run tsc:node      # Check node scripts
```

### Python MCP Servers

**Insurance Server:**
```bash
# Setup (one-time)
python -m venv .venv
source .venv/bin/activate
pip install -r insurance_server_python/requirements.txt
cp insurance_server_python/.env.example insurance_server_python/.env

# Run server
uvicorn insurance_server_python.main:app --port 8000

# Run with debug logging
INSURANCE_LOG_LEVEL=DEBUG uvicorn insurance_server_python.main:app --port 8000

# Run tests
pytest insurance_server_python/tests/
```

**Solar System Server:**
```bash
# Setup (can reuse same venv)
source .venv/bin/activate
pip install -r solar-system_server_python/requirements.txt

# Run server
uvicorn solar-system_server_python.main:app --port 8000
```

## Architecture

### Frontend Widget Structure

Widgets live in `src/{widget-name}/`:
- `index.tsx` or `index.jsx` - Entry point, must export a default component
- `*.css` files - Widget-specific styles (auto-bundled with the widget)
- `src/index.css` - Global styles (included in all widgets)

The build system:
1. Finds all `src/**/index.{tsx,jsx}` entry points
2. For each widget, bundles it with global CSS + per-widget CSS
3. Produces `{widget-name}-{hash}.html`, `.js`, and `.css` in `assets/`
4. HTML bundles inline both CSS and JS for single-file deployment

### MCP Server Structure

Python servers in `{server-name}_server_python/`:
- `main.py` - FastMCP server with tool definitions and widget resource registration
- `{widget-name}_widget.py` - Widget HTML templates (usually imported from `assets/`)
- `requirements.txt` - Python dependencies (FastMCP, FastAPI, uvicorn, httpx)
- `tests/` - pytest test suite
- `.env.example` - Template for environment variables

**Tool Response Pattern:**
Each tool returns both human-readable text and structured JSON, plus `_meta.openai/outputTemplate` pointing to the widget resource:
```python
return {
    "content": [
        types.TextContent(type="text", text="Human readable confirmation"),
        types.TextContent(
            type="text",
            text=json.dumps({"structured": "data"}),
            annotations=types.TextAnnotations(audience=["model"])
        )
    ],
    "_meta": {
        "openai/outputTemplate": {
            "type": "resource",
            "uri": "ui://widget/insurance-state.html"
        }
    }
}
```

### Repository Layout

- `src/` - React widget source code
- `assets/` - Built widget bundles (git-tracked, versioned by hash)
- `insurance_server_python/` - Insurance intake MCP server with multi-step flow tools
- `solar-system_server_python/` - 3D solar system viewer MCP server
- `build-all.mts` - Build orchestrator that produces hashed bundles
- `vite.config.mts` - Dev server config with multi-entry support

## Testing in ChatGPT

1. Enable developer mode in ChatGPT
2. Start your MCP server locally (port 8000)
3. Use ngrok to expose it: `ngrok http 8000`
4. Add the ngrok URL + `/mcp` endpoint in ChatGPT Settings > Connectors
   - Example: `https://<custom_endpoint>.ngrok-free.app/mcp`

## Development Workflow

**Adding a new widget:**
1. Create `src/{widget-name}/index.tsx` with a default export
2. Add any widget-specific CSS in the same directory
3. Run `pnpm run build` - it will auto-discover and bundle the new widget
4. In your MCP server, register the widget as a resource and reference it in tool responses

**Modifying an existing widget:**
1. Edit files in `src/{widget-name}/`
2. Use `pnpm run dev` for hot reload during development
3. Run `pnpm run build` to produce production bundles
4. Update the widget HTML in the corresponding Python server file if needed

**Working on MCP server logic:**
1. Modify tool handlers in `{server}_server_python/main.py`
2. Update widget templates in `{widget}_widget.py` files
3. Restart the server: `uvicorn {server}_server_python.main:app --port 8000`
4. Test with MCP Inspector or ChatGPT

## Important Notes

- Assets are git-tracked and versioned - commit them after builds
- Widget bundles are hashed based on `package.json` version
- MCP servers expect widget assets to be pre-built in `assets/`
- Use FastMCP's `FastMCP` class from `mcp.server.fastmcp` (not the unrelated `modelcontextprotocol` package)
- Insurance server requires `PERSONAL_AUTO_RATE_API_KEY` in `.env` for rating tool
- Dev server runs on port 4444, MCP servers typically run on port 8000
