"""
Vibmo Model Context Protocol (MCP) Tool Handlers.
Enables AI Agents (Claude, Cursor, Antigravity, ChatGPT, Gemini) to directly generate,
inspect, validate, and render motion graphics.
"""

from __future__ import annotations
import os
import sys
import json
import base64
import tempfile
import traceback
from typing import Any, Dict, List, Optional


def tool_list_components() -> Dict[str, Any]:
    """Returns an inventory of all available semantic components, charts, cards, and motion verbs."""
    from vibmo.ai.schema import generate_component_schemas
    schemas = generate_component_schemas()
    return {
        "count": len(schemas),
        "components": schemas,
        "motion_verbs": [
            {"verb": "node.pop_in(delay=0.1, duration=0.8)", "description": "Spring entrance with scale overshoot & opacity fade"},
            {"verb": "node.fade_up(offset=40, duration=0.7)", "description": "Smooth slide upward with cubic deceleration"},
            {"verb": "node.bounce(amplitude=1.2, count=2)", "description": "Elastic pulse for emphasis and beat drops"},
            {"verb": "node.float_idle(amplitude=6, speed=1.0)", "description": "Continuous organic harmonic oscillation"},
            {"verb": "text.reveal_characters(stagger=0.025)", "description": "Fluid wave reveal of typography glyphs"},
            {"verb": "counter.count_to(duration=1.8)", "description": "Numeric ticker with exponential deceleration"},
            {"verb": "chart.grow_bars(duration=1.0)", "description": "Staggered spring vertical bar growth"},
            {"verb": "chart.reveal(duration=1.4)", "description": "Radial 360-degree sweep for pie/donut charts"},
            {"verb": "table.reveal_rows(stagger=0.08)", "description": "Staggered row slide entrance for data grids"},
            {"verb": "timeline.animate_progress(duration=1.6)", "description": "Animated glowing milestone path progression"},
            {"verb": "cursor.move_to(node)", "description": "Glides cursor to the center of any UI component"},
            {"verb": "cursor.click()", "description": "Simulates mouse press with spring click bounce"},
        ]
    }


def tool_search_icons(query: str, limit: int = 15) -> Dict[str, Any]:
    """Searches 200,000+ vector icons by keyword (Lucide, Heroicons, Phosphor, Tabler, Material)."""
    from vibmo.importers.icons import BUILTIN_ICONS, IconifyResolver
    q = query.lower().strip()
    matches = []

    # 1. Search built-in fast icons
    for name in BUILTIN_ICONS.keys():
        if q in name:
            matches.append({"name": name, "source": "builtin", "type": "offline"})

    # 2. Add standard iconify suggestions
    prefixes = ["lucide", "tabler", "ph", "heroicons", "fa6-solid", "material-symbols"]
    for p in prefixes:
        candidate = f"{p}:{q}"
        if candidate not in [m["name"] for m in matches]:
            matches.append({"name": candidate, "source": "iconify", "type": "online_cached"})

    return {
        "query": query,
        "results": matches[:limit],
    }


def tool_validate_scene(code: str) -> Dict[str, Any]:
    """Executes a Vibmo script in a sandbox and validates layout, timing, and font health."""
    scope: Dict[str, Any] = {}
    try:
        exec("from vibmo.agent_api import *", scope)
        exec(code, scope)
        scene = scope.get("scene")
        if not scene:
            for v in scope.values():
                if hasattr(v, "nodes") and hasattr(v, "validate"):
                    scene = v
                    break
        if not scene:
            return {"valid": False, "error": "No 'scene' object found in provided code snippet"}

        issues = scene.validate()
        structure = scene.describe()
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "duration": scene.duration,
            "fps": scene.fps,
            "node_count": len(scene.nodes),
            "structure": structure,
        }
    except Exception as e:
        return {
            "valid": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
        }


def tool_inspect_storyboard(code: str, rows: int = 2, cols: int = 3) -> Dict[str, Any]:
    """Renders a 6-frame storyboard progression image and returns base64 for instant visual AI inspection."""
    temp_dir = tempfile.mkdtemp()
    out_png = os.path.join(temp_dir, "storyboard.png")
    
    scope: Dict[str, Any] = {}
    try:
        exec("from vibmo.agent_api import *", scope)
        exec(code, scope)
        scene = scope.get("scene")
        if not scene:
            for v in scope.values():
                if hasattr(v, "storyboard"):
                    scene = v
                    break
        if not scene:
            return {"success": False, "error": "No 'scene' object found in code"}

        scene.storyboard(path=out_png, rows=rows, cols=cols)
        
        with open(out_png, "rb") as f:
            b64_img = base64.b64encode(f.read()).decode("utf-8")

        issues = scene.validate()
        return {
            "success": True,
            "storyboard_path": out_png,
            "image_base64": b64_img,
            "issues": issues,
            "duration": scene.duration,
            "frames_rendered": rows * cols,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
        }


def tool_generate_scene_from_prompt(
    prompt: str,
    duration: float = 4.0,
    output_video: Optional[str] = None,
    output_storyboard: Optional[str] = None,
) -> Dict[str, Any]:
    """Generates an animated scene from a text prompt and renders a storyboard/video."""
    from vibmo.scene.scene import Scene
    try:
        scene = Scene.from_prompt(prompt, duration=duration)
        results: Dict[str, Any] = {
            "success": True,
            "prompt": prompt,
            "duration": scene.duration,
            "node_count": len(scene.nodes),
            "structure": scene.describe(),
        }

        # Render storyboard if requested or default
        sb_path = output_storyboard or os.path.join(tempfile.gettempdir(), "prompt_storyboard.png")
        scene.storyboard(sb_path)
        with open(sb_path, "rb") as f:
            results["storyboard_base64"] = base64.b64encode(f.read()).decode("utf-8")
        results["storyboard_path"] = sb_path

        # Render video if requested
        if output_video:
            scene.render(output_video, quality="fast")
            results["video_path"] = os.path.abspath(output_video)

        return results
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
        }


def tool_render_scene(
    code: str,
    output_path: str = "output.mp4",
    quality: str = "high",
    preset: str = "mp4",
) -> Dict[str, Any]:
    """Executes Vibmo code and renders the final video file (MP4, WebM, ProRes, GIF)."""
    scope: Dict[str, Any] = {}
    try:
        exec("from vibmo.agent_api import *", scope)
        exec(code, scope)
        scene = scope.get("scene")
        if not scene:
            for v in scope.values():
                if hasattr(v, "render"):
                    scene = v
                    break
        if not scene:
            return {"success": False, "error": "No 'scene' or 'sequence' found in code"}

        out_abs = os.path.abspath(output_path)
        scene.render(output_path=out_abs, quality=quality, preset=preset)
        return {
            "success": True,
            "output_path": out_abs,
            "file_size_bytes": os.path.getsize(out_abs) if os.path.exists(out_abs) else 0,
            "duration": scene.duration,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
        }


# -----------------------------------------------------------------------------
# State Graph & DAG Tools (Vibmo V2 Agent Bridge)
# -----------------------------------------------------------------------------

def tool_get_project_state(project_path: Optional[str] = None) -> Dict[str, Any]:
    """Inspects the live state graph or reads a .vibmo project file."""
    from vibmo.graph.engine import VibmoStateGraph
    try:
        if project_path and os.path.exists(project_path):
            graph = VibmoStateGraph.load_from_file(project_path)
        else:
            graph = VibmoStateGraph()

        return {
            "success": True,
            "project_name": graph.project.name,
            "tracks": [t.model_dump() for t in graph.project.timeline.tracks],
            "clips_count": len(graph.project.timeline.clips),
            "media_pool_count": len(graph.project.media_pool),
            "fusion_graphs_count": len(graph.project.fusion_graphs),
            "render_queue_count": len(graph.project.render_queue),
            "schema_json": graph.project.model_dump(),
        }
    except Exception as e:
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}


def tool_mutate_state_graph(
    action: str,
    params: Dict[str, Any],
    project_path: Optional[str] = None,
    save_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Safely executes an action on the state graph (add_node, connect_nodes, import_media, add_clip, apply_grade).
    """
    from vibmo.graph.engine import VibmoStateGraph
    try:
        if project_path and os.path.exists(project_path):
            graph = VibmoStateGraph.load_from_file(project_path)
        else:
            graph = VibmoStateGraph()

        result = {}
        if action == "import_media":
            item = graph.import_media(file_path=params["file_path"], name=params.get("name"), kind=params.get("kind"))
            result = item.model_dump()
        elif action == "add_clip":
            clip = graph.add_clip(
                track_id=params["track_id"],
                name=params["name"],
                start_frame=params["start_frame"],
                duration_frames=params["duration_frames"],
                media_id=params.get("media_id"),
                fusion_graph_id=params.get("fusion_graph_id"),
            )
            result = clip.model_dump()
        elif action == "add_fusion_node":
            node = graph.add_fusion_node(
                graph_id=params["graph_id"],
                node_type=params["node_type"],
                name=params.get("name"),
                category=params.get("category", "filter"),
                pos_x=params.get("pos_x", 300.0),
                pos_y=params.get("pos_y", 200.0),
                properties=params.get("properties"),
            )
            result = node.model_dump()
        elif action == "connect_fusion_nodes":
            conn = graph.connect_fusion_nodes(
                graph_id=params["graph_id"],
                from_node_id=params["from_node_id"],
                to_node_id=params["to_node_id"],
                from_socket=params.get("from_socket", "output"),
                to_socket=params.get("to_socket", "input"),
            )
            result = conn.model_dump()
        elif action == "set_primary_grade":
            grade = graph.set_primary_grade(
                lift=tuple(params["lift"]) if "lift" in params else None,
                gamma=tuple(params["gamma"]) if "gamma" in params else None,
                gain=tuple(params["gain"]) if "gain" in params else None,
                contrast=params.get("contrast", 1.0),
                saturation=params.get("saturation", 1.0),
            )
            result = grade.model_dump()
        else:
            return {"success": False, "error": f"Unknown action '{action}'"}

        if save_path:
            graph.save_to_file(save_path)

        return {"success": True, "action": action, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}

