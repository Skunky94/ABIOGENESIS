"""
Scarlet Tools Package

Custom tools for Scarlet agent:
- memory_tool: Conscious memory retrieval (ADR-005 Phase 6)
"""

from .memory_tool import (
    remember,
    get_memory_tool,
    get_tool_definition,
    register_with_agent,
    TOOL_SCHEMA
)

__all__ = [
    "remember",
    "get_memory_tool", 
    "get_tool_definition",
    "register_with_agent",
    "TOOL_SCHEMA"
]
