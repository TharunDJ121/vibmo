"""
Vibmo Model Context Protocol (MCP) Server and Tool integration.
"""

from vibmo.mcp.server import MCPServer, run_mcp_server, MCP_TOOLS_DEFINITIONS
from vibmo.mcp.tools import (
    tool_list_components,
    tool_search_icons,
    tool_validate_scene,
    tool_inspect_storyboard,
    tool_generate_scene_from_prompt,
    tool_render_scene,
)

__all__ = [
    "MCPServer",
    "run_mcp_server",
    "MCP_TOOLS_DEFINITIONS",
    "tool_list_components",
    "tool_search_icons",
    "tool_validate_scene",
    "tool_inspect_storyboard",
    "tool_generate_scene_from_prompt",
    "tool_render_scene",
]
