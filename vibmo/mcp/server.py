"""
Official Model Context Protocol (MCP) JSON-RPC 2.0 Server for Vibmo.
Communicates via standard I/O (stdin/stdout) with AI Clients (Claude Desktop, Cursor, Antigravity, Cline).
"""

from __future__ import annotations
import sys
import os
import json
import traceback
from typing import Any, Dict, List, Optional

from vibmo.mcp.tools import (
    tool_list_components,
    tool_search_icons,
    tool_validate_scene,
    tool_inspect_storyboard,
    tool_generate_scene_from_prompt,
    tool_render_scene,
    tool_get_project_state,
    tool_mutate_state_graph,
)
from vibmo.mcp.resources import (
    get_mcp_resources,
    read_mcp_resource,
    get_mcp_prompts,
)

MCP_TOOLS_DEFINITIONS = [
    {
        "name": "list_components",
        "description": "Lists all available Vibmo design primitives, charts, UI controls, and motion verbs with documentation.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "search_icons",
        "description": "Searches 200,000+ vector icons (Lucide, Tabler, Phosphor, Heroicons, Material) with offline local caching.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search keyword (e.g. 'rocket', 'zap', 'sparkles', 'github')"},
                "limit": {"type": "integer", "description": "Maximum number of results to return", "default": 10},
            },
            "required": ["query"],
        },
    },
    {
        "name": "validate_scene",
        "description": "Pre-flight checks a Python Vibmo script for layout overlaps, timing overflows, and missing assets.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Python code snippet containing a Vibmo Scene"},
            },
            "required": ["code"],
        },
    },
    {
        "name": "inspect_storyboard",
        "description": "Executes a Vibmo script and renders a 6-frame storyboard contact sheet image (base64) for visual AI inspection.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Python code snippet containing a Vibmo Scene"},
                "rows": {"type": "integer", "description": "Storyboard grid rows", "default": 2},
                "cols": {"type": "integer", "description": "Storyboard grid columns", "default": 3},
            },
            "required": ["code"],
        },
    },
    {
        "name": "generate_scene_from_prompt",
        "description": "Synthesizes an animated motion graphic scene from a text prompt and generates a storyboard / video preview.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Natural language description of the video or product animation"},
                "duration": {"type": "number", "description": "Scene duration in seconds", "default": 4.0},
                "output_video": {"type": "string", "description": "Optional filepath to save rendered MP4"},
                "output_storyboard": {"type": "string", "description": "Optional filepath to save storyboard PNG"},
            },
            "required": ["prompt"],
        },
    },
    {
        "name": "render_scene",
        "description": "Executes a Vibmo script and renders the full video (MP4, WebM, ProRes, GIF).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Python code snippet containing a Vibmo Scene"},
                "output_path": {"type": "string", "description": "Destination file path (.mp4, .webm, .mov, .gif)", "default": "output.mp4"},
                "quality": {"type": "string", "description": "Render quality: 'draft', 'fast', 'high', '4k'", "default": "high"},
                "preset": {"type": "string", "description": "Codec preset: 'mp4', 'webm', 'prores', 'gif'", "default": "mp4"},
            },
            "required": ["code"],
        },
    },
    {
        "name": "get_project_state",
        "description": "Returns the complete V2 State Graph (Timeline, Fusion DAG, Color, Fairlight, Media Pool) of a project.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {"type": "string", "description": "Optional .vibmo project file path"},
            },
            "required": [],
        },
    },
    {
        "name": "mutate_state_graph",
        "description": "Executes a safe structural action on the state graph (import_media, add_clip, add_fusion_node, connect_fusion_nodes, set_primary_grade).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "description": "Action name: 'import_media', 'add_clip', 'add_fusion_node', 'connect_fusion_nodes', 'set_primary_grade'"},
                "params": {"type": "object", "description": "Action parameters dictionary"},
                "project_path": {"type": "string", "description": "Optional input project path"},
                "save_path": {"type": "string", "description": "Optional output path to save updated .vibmo project"},
            },
            "required": ["action", "params"],
        },
    },
]


class MCPServer:
    """Model Context Protocol stdio server for Vibmo."""

    def __init__(self) -> None:
        self.running = True

    def handle_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        req_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Notifications without ID
        if req_id is None:
            return None

        try:
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {},
                            "resources": {},
                            "prompts": {},
                        },
                        "serverInfo": {
                            "name": "vibmo-mcp",
                            "version": "1.0.0",
                        },
                    },
                }

            elif method == "ping":
                return {"jsonrpc": "2.0", "id": req_id, "result": {}}

            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "tools": MCP_TOOLS_DEFINITIONS,
                    },
                }

            elif method == "tools/call":
                tool_name = params.get("name")
                args = params.get("arguments", {})
                res = self._dispatch_tool(tool_name, args)
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(res, indent=2),
                            }
                        ],
                    },
                }

            elif method == "resources/list":
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "resources": get_mcp_resources(),
                    },
                }

            elif method == "resources/read":
                uri = params.get("uri")
                content = read_mcp_resource(uri)
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "contents": [content],
                    },
                }

            elif method == "prompts/list":
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "prompts": get_mcp_prompts(),
                    },
                }

            else:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}",
                    },
                }

        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32603,
                    "message": str(e),
                    "data": traceback.format_exc(),
                },
            }

    def _dispatch_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        if name == "list_components":
            return tool_list_components()
        elif name == "search_icons":
            return tool_search_icons(args.get("query", ""), limit=args.get("limit", 10))
        elif name == "validate_scene":
            return tool_validate_scene(args.get("code", ""))
        elif name == "inspect_storyboard":
            return tool_inspect_storyboard(args.get("code", ""), rows=args.get("rows", 2), cols=args.get("cols", 3))
        elif name == "generate_scene_from_prompt":
            return tool_generate_scene_from_prompt(
                args.get("prompt", ""),
                duration=args.get("duration", 4.0),
                output_video=args.get("output_video"),
                output_storyboard=args.get("output_storyboard"),
            )
        elif name == "render_scene":
            return tool_render_scene(
                args.get("code", ""),
                output_path=args.get("output_path", "output.mp4"),
                quality=args.get("quality", "high"),
                preset=args.get("preset", "mp4"),
            )
        elif name == "get_project_state":
            return tool_get_project_state(args.get("project_path"))
        elif name == "mutate_state_graph":
            return tool_mutate_state_graph(
                action=args.get("action", ""),
                params=args.get("params", {}),
                project_path=args.get("project_path"),
                save_path=args.get("save_path"),
            )
        else:
            raise ValueError(f"Unknown tool: {name}")

    def run_stdio(self) -> None:
        """Main stdio loop reading JSON-RPC lines from stdin and writing to stdout."""
        # Ensure utf-8
        if sys.platform == "win32":
            sys.stdin.reconfigure(encoding="utf-8", errors="replace")
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")

        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                req = json.loads(line)
                resp = self.handle_request(req)
                if resp is not None:
                    sys.stdout.write(json.dumps(resp) + "\n")
                    sys.stdout.flush()
            except Exception as e:
                err_resp = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": f"Parse error: {str(e)}"},
                }
                sys.stdout.write(json.dumps(err_resp) + "\n")
                sys.stdout.flush()


def run_mcp_server() -> None:
    server = MCPServer()
    server.run_stdio()


if __name__ == "__main__":
    run_mcp_server()
