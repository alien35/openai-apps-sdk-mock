"""Request tracking middleware for debugging duplicate calls."""

import json
import logging
import time
import uuid
from datetime import datetime
from typing import Dict, List

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)

# Track all requests
request_history: List[Dict] = []


class RequestTrackingMiddleware(BaseHTTPMiddleware):
    """Middleware to track and log all incoming requests."""

    async def dispatch(self, request: Request, call_next):
        """Track request and response."""
        request_id = str(uuid.uuid4())[:8]
        start_time = time.time()
        timestamp = datetime.now().isoformat()

        # Read the request body for logging (but preserve it for the handler)
        # IMPORTANT: Don't read body for SSE endpoints - it breaks streaming
        body = None
        if request.method == "POST" and not request.url.path.startswith('/mcp'):
            # Only read body for non-MCP endpoints to avoid breaking SSE
            try:
                body_bytes = await request.body()
                # Restore the body for the actual handler
                async def receive():
                    return {"type": "http.request", "body": body_bytes}
                request._receive = receive

                try:
                    body = json.loads(body_bytes.decode('utf-8'))
                except:
                    body = body_bytes.decode('utf-8', errors='ignore')[:500]
            except:
                # If body reading fails, just skip it
                pass

        # Log the incoming request
        logger.info("=" * 80)
        logger.info("🔵 INCOMING REQUEST [%s] at %s", request_id, timestamp)
        logger.info("=" * 80)
        logger.info("Method: %s", request.method)
        logger.info("URL: %s", request.url)
        logger.info("Path: %s", request.url.path)
        logger.info("Headers:")
        for key, value in request.headers.items():
            # Don't log sensitive headers
            if key.lower() in ['authorization', 'cookie']:
                logger.info("  %s: [REDACTED]", key)
            else:
                logger.info("  %s: %s", key, value)

        # Check if this is an MCP request
        is_mcp_request = request.url.path.startswith('/mcp')

        # Note: For MCP/SSE endpoints, we don't read the body to avoid breaking streaming
        if is_mcp_request:
            logger.info("MCP/SSE Request - Body not logged to preserve streaming")
        elif body:
            logger.info("Request Body: %s", body)

        logger.info("=" * 80)

        # Store request info
        request_info = {
            'request_id': request_id,
            'timestamp': timestamp,
            'method': request.method,
            'path': request.url.path,
            'is_mcp': is_mcp_request,
            'body_preview': str(body)[:200] if body else None,
        }
        request_history.append(request_info)

        # Keep only last 50 requests
        if len(request_history) > 50:
            request_history.pop(0)

        # Process the request
        response = await call_next(request)

        duration = time.time() - start_time

        # Log the response
        logger.info("=" * 80)
        logger.info("🟢 RESPONSE [%s] - %.2fms", request_id, duration * 1000)
        logger.info("=" * 80)
        logger.info("Status: %s", response.status_code)
        logger.info("Duration: %.2fms", duration * 1000)
        logger.info("=" * 80)

        return response


def get_request_summary() -> Dict:
    """Get a summary of recent requests."""
    return {
        'total_requests': len(request_history),
        'recent_requests': request_history[-10:],
    }


def clear_tracking():
    """Clear all tracking data."""
    request_history.clear()
    logger.info("Request tracking data cleared")
