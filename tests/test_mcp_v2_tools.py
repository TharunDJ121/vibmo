"""
Tests for MCP v2 Tools and JSON-RPC Server in Vibmo.
"""

import pytest
import json
from vibmo.mcp.tools import (
    tool_list_components,
    tool_search_icons,
    tool_validate_scene,
    tool_inspect_storyboard,
    tool_get_frame_preview,
    tool_generate_scene_from_prompt,
    tool_ai_edit,
    tool_render_scene,
    tool_get_project_state,
)
from vibmo.mcp.server import MCPServer


SAMPLE_VALID_CODE = """from motio.agent_api import *

scene = Scene(width=1280, height=720, duration=2.0, background=colors.DARK_NAVY)
card = GlassCard(position=(100, 100))
scene.add(card)

@scene.animate
def main():
    yield card.pop_in()
    yield scene.wait(0.5)
"""


def test_mcp_list_components():
    res = tool_list_components()
    assert res["count"] > 10
    assert len(res["components"]) > 0
    assert len(res["motion_verbs"]) > 0


def test_mcp_search_icons():
    res = tool_search_icons("sparkles")
    assert len(res["results"]) > 0


def test_mcp_validate_scene():
    res = tool_validate_scene(SAMPLE_VALID_CODE)
    assert res["valid"]
    assert res["duration"] == 2.0


def test_mcp_inspect_storyboard():
    res = tool_inspect_storyboard(SAMPLE_VALID_CODE, rows=1, cols=2)
    assert res["success"]
    assert res["image_base64"] is not None
    assert len(res["image_base64"]) > 100


def test_mcp_get_frame_preview():
    res = tool_get_frame_preview(SAMPLE_VALID_CODE, time=0.5, scale=0.25)
    assert res["success"]
    assert res["image_base64"] is not None


def test_mcp_ai_edit():
    res = tool_ai_edit("Make duration 3.5 seconds", SAMPLE_VALID_CODE)
    assert res["success"]
    assert res["updated_code"] is not None


def test_mcp_json_rpc_server_dispatch():
    server = MCPServer()
    req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "get_frame_preview",
            "arguments": {"code": SAMPLE_VALID_CODE, "time": 0.5, "scale": 0.25},
        },
    }
    resp = server.handle_request(req)
    assert resp["id"] == 1
    content_text = resp["result"]["content"][0]["text"]
    parsed = json.loads(content_text)
    assert parsed["success"]
