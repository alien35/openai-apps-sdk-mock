"""Export the FastMCP app so uvicorn can auto-discover it."""

from .main import app, mcp

__all__ = ["app", "mcp"]
