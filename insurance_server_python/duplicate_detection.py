"""Duplicate tool call detection to prevent repeated calls with identical data."""

import hashlib
import json
import time
from typing import Any, Dict, Optional

# In-memory cache of recent tool calls (in production, use Redis or similar)
_recent_calls: Dict[str, float] = {}

# Time window to consider calls as duplicates (5 minutes)
DUPLICATE_WINDOW_SECONDS = 300


def _hash_arguments(args: Dict[str, Any]) -> str:
    """Create a stable hash of tool arguments."""
    # Sort keys to ensure consistent hashing
    sorted_json = json.dumps(args, sort_keys=True)
    return hashlib.sha256(sorted_json.encode()).hexdigest()


def is_duplicate_call(tool_name: str, arguments: Dict[str, Any]) -> bool:
    """Check if this tool call is a duplicate of a recent call.

    Args:
        tool_name: Name of the tool being called
        arguments: Arguments passed to the tool

    Returns:
        True if this is a duplicate call within the time window
    """
    # Create unique key for this specific call
    args_hash = _hash_arguments(arguments)
    call_key = f"{tool_name}:{args_hash}"

    current_time = time.time()

    # Clean up old entries (older than window)
    expired_keys = [
        key for key, timestamp in _recent_calls.items()
        if current_time - timestamp > DUPLICATE_WINDOW_SECONDS
    ]
    for key in expired_keys:
        del _recent_calls[key]

    # Check if this call was made recently
    if call_key in _recent_calls:
        time_since_last = current_time - _recent_calls[call_key]
        if time_since_last < DUPLICATE_WINDOW_SECONDS:
            return True

    # Record this call
    _recent_calls[call_key] = current_time
    return False


def get_duplicate_info(tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Get information about when a duplicate call was made.

    Returns:
        Dict with duplicate info if found, None otherwise
    """
    args_hash = _hash_arguments(arguments)
    call_key = f"{tool_name}:{args_hash}"

    if call_key in _recent_calls:
        timestamp = _recent_calls[call_key]
        seconds_ago = time.time() - timestamp
        return {
            "timestamp": timestamp,
            "seconds_ago": seconds_ago,
            "call_key": call_key,
        }

    return None
