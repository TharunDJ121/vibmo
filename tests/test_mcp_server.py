"""
Unit tests for the Vibmo Model Context Protocol (MCP) JSON-RPC Server & Tools.
"""

import os
import json
import pytest
from vibmo.mcp.server import MCPServer
from vibmo.mcp.tools import (
    tool_list_components,
    tool_search_icons,
    tool_validate_scene,
    tool_inspect_storyboard,
    tool_generate_scene_from_prompt,
    tool_render_scene,
)


@pytest.fixture
def mcp_server():
    return MCPServer()


def test_mcp_initialize(mcp_server):
    req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "clientInfo": {"name": "test-client", "version": "1.0.0"},
        },
    }
    resp = mcp_server.handle_request(req)
    assert resp["id"] == 1
    assert resp["result"]["protocolVersion"] == "2024-11-05"
    assert resp["result"]["serverInfo"]["name"] == "vibmo-mcp"
    assert "tools" in resp["result"]["capabilities"]


def test_mcp_tools_list(mcp_server):
    req = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {},
    }
    resp = mcp_server.handle_request(req)
    assert resp["id"] == 2
    tools = resp["result"]["tools"]
    tool_names = [t["name"] for t in tools]
    assert "list_components" in tool_names
    assert "search_icons" in tool_names
    assert "validate_scene" in tool_names
    assert "inspect_storyboard" in tool_names
    assert "generate_scene_from_prompt" in tool_names
    assert "render_scene" in tool_names


def test_mcp_tool_list_components():
    res = tool_list_components()
    assert res["count"] >= 15
    assert len(res["motion_verbs"]) >= 8


def test_mcp_tool_search_icons():
    res = tool_search_icons("zap", limit=5)
    assert res["query"] == "zap"
    assert len(res["results"]) > 0
    assert any("zap" in r["name"] for r in res["results"])


def test_mcp_tool_validate_scene():
    valid_code = """
scene = Scene(width=1920, height=1080, duration=2.0)
card = GlassCard(position=(100, 100))
scene.add(card)
"""
    res = tool_validate_scene(valid_code)
    assert res["valid"] is True
    assert res["node_count"] == 1

    invalid_code = "import syntax_error_foo"
    res_err = tool_validate_scene(invalid_code)
    assert res_err["valid"] is False
    assert "error" in res_err


def test_mcp_tool_inspect_storyboard():
    code = """
scene = Scene(width=640, height=360, duration=2.0, background=colors.DARK_NAVY)
card = GlassCard(position=(50, 50))
scene.add(card)
@scene.animate
def main():
    yield card.pop_in()
"""
    res = tool_inspect_storyboard(code, rows=2, cols=2)
    assert res["success"] is True
    assert "image_base64" in res
    assert len(res["image_base64"]) > 500


def test_mcp_tool_generate_from_prompt():
    prompt = "A SaaS launch graphic for Apex AI with $250K MRR"
    res = tool_generate_scene_from_prompt(prompt, duration=2.0)
    assert res["success"] is True
    assert "storyboard_base64" in res
    assert res["duration"] == 2.0


def test_mcp_tool_render_scene(tmp_path):
    code = """
scene = Scene(width=320, height=180, duration=0.5, fps=24)
card = GlassCard(position=(20, 20))
scene.add(card)
"""
    out_video = str(tmp_path / "test_mcp_render.mp4")
    res = tool_render_scene(code, output_path=out_video, quality="fast")
    assert res["success"] is True
    assert res["output_path"] == out_video


def test_mcp_resources_and_prompts(mcp_server):
    # Resources List
    req_res = {"jsonrpc": "2.0", "id": 3, "method": "resources/list", "params": {}}
    resp_res = mcp_server.handle_request(req_res)
    assert len(resp_res["result"]["resources"]) >= 2

    # Prompts List
    req_prompts = {"jsonrpc": "2.0", "id": 4, "method": "prompts/list", "params": {}}
    resp_prompts = mcp_server.handle_request(req_prompts)
    assert len(resp_prompts["result"]["prompts"]) >= 2


def test_mcp_state_graph_tools(mcp_server, tmp_path):
    # 1. Get project state
    req_state = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
            "name": "get_project_state",
            "arguments": {},
        },
    }
    resp = mcp_server.handle_request(req_state)
    assert resp["id"] == 5
    data = json.loads(resp["result"]["content"][0]["text"])
    assert data["success"] is True
    assert "tracks" in data
    assert len(data["tracks"]) >= 2

    # 2. Mutate state graph: add track and add fusion node
    proj_file = str(tmp_path / "test_agent_project.vibmo")
    req_mutate = {
        "jsonrpc": "2.0",
        "id": 6,
        "method": "tools/call",
        "params": {
            "name": "mutate_state_graph",
            "arguments": {
                "action": "set_primary_grade",
                "params": {"contrast": 1.25, "saturation": 1.1},
                "save_path": proj_file,
            },
        },
    }
    resp_mut = mcp_server.handle_request(req_mutate)
    assert resp_mut["id"] == 6
    res_data = json.loads(resp_mut["result"]["content"][0]["text"])
    assert res_data["success"] is True
    assert res_data["result"]["contrast"] == 1.25
    assert os.path.exists(proj_file)

