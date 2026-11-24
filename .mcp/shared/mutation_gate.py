"""Operator-approval gate for tools that mutate state or execute programs."""

import os
from typing import Any, Dict, Mapping, Optional

ALLOW_MUTATIONS_ENV = "MCP_ALLOW_MUTATIONS"

APPROVED_PROPERTY: Dict[str, Any] = {
    "type": "boolean",
    "description": "Explicit operator approval for this action.",
}


def mutation_denial(
    tool_name: str, arguments: Optional[Mapping[str, Any]]
) -> Optional[Dict[str, Any]]:
    """Deny unless MCP_ALLOW_MUTATIONS=1 is set and arguments include approved=True."""
    approved = (arguments or {}).get("approved") is True
    if os.getenv(ALLOW_MUTATIONS_ENV) == "1" and approved:
        return None
    return {
        "error": "explicit_approval_required",
        "tool": tool_name,
        "message": f"Set {ALLOW_MUTATIONS_ENV}=1 and pass approved=true for this call.",
    }
