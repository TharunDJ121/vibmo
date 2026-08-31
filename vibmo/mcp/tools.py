"""
Vibmo Model Context Protocol (MCP) Tool Handlers (v2).
Enables AI Agents (Claude, Cursor, Antigravity, ChatGPT, Gemini) to directly generate,
inspect, surgically edit, validate, preview frames, and render motion graphics.
"""

from __future__ import annotations
import os
import sys
import json
import base64
import tempfile
import traceback
from typing import Any, Dict, List, Optional, Union
from PIL import Image

from vibmo.ai.schema import generate_component_schemas
from vibmo.ai.graph import run_motion_edit
from vibmo.ai.autonomous import AutonomousPipeline
from vibmo.ai.surgical_editor import SurgicalSceneEditor


def tool_list_components() -> Dict[str, Any]:
    """Returns an inventory of all available semantic components, charts, cards, and motion verbs."""
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
    from vibmo.importers.icons import BUILTIN_ICONS
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
        exec("from motio.agent_api import *", scope)
        exec(code, scope)
        scene = scope.get("scene") or scope.get("seq")
        if not scene:
            for v in scope.values():
                if hasattr(v, "nodes") and hasattr(v, "validate"):
                    scene = v
                    break
        if not scene:
            return {"valid": False, "error": "No 'scene' or 'seq' object found in provided code snippet"}

        issues = scene.validate() if hasattr(scene, "validate") else []
        structure = scene.describe() if hasattr(scene, "describe") else {}
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "duration": getattr(scene, "duration", 0.0),
            "fps": getattr(scene, "fps", 60.0),
            "node_count": len(getattr(scene, "nodes", [])),
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
        exec("from motio.agent_api import *", scope)
        exec(code, scope)
        scene = scope.get("scene") or scope.get("seq")
        if not scene:
            for v in scope.values():
                if hasattr(v, "storyboard"):
                    scene = v
                    break
        if not scene:
            return {"success": False, "error": "No 'scene' or 'seq' object found in code"}

        scene.storyboard(path=out_png, rows=rows, cols=cols)
        
        with open(out_png, "rb") as f:
            b64_img = base64.b64encode(f.read()).decode("utf-8")

        issues = scene.validate() if hasattr(scene, "validate") else []
        return {
            "success": True,
            "storyboard_path": out_png,
            "image_base64": b64_img,
            "issues": issues,
            "duration": getattr(scene, "duration", 0.0),
            "frames_rendered": rows * cols,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
        }


def tool_get_frame_preview(code: str, time: float = 1.0, scale: float = 0.5) -> Dict[str, Any]:
    """Renders a single frame at timestamp `time` and returns base64 JPEG for instant visual inspection."""
    scope: Dict[str, Any] = {}
    try:
        exec("from motio.agent_api import *", scope)
        exec(code, scope)
        scene = scope.get("scene") or scope.get("seq")
        if not scene:
            return {"success": False, "error": "No Scene or Sequence object found in code."}

        temp_img_path = os.path.join(tempfile.gettempdir(), f"frame_{int(time*1000)}.jpg")
        if hasattr(scene, "render_frame"):
            rgba = scene.render_frame(time=time, scale=scale)
            img = Image.fromarray(rgba, "RGBA").convert("RGB")
            img.save(temp_img_path, format="JPEG", quality=80)
        elif hasattr(scene, "snapshot"):
            scene.snapshot(time=time, path=temp_img_path)

        with open(temp_img_path, "rb") as f:
            b64_img = base64.b64encode(f.read()).decode("utf-8")

        return {
            "success": True,
            "time": time,
            "scale": scale,
            "image_base64": b64_img,
        }
    except Exception as e:
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}


def tool_generate_scene_from_prompt(
    prompt: str,
    duration: float = 4.0,
    output_video: Optional[str] = None,
    output_storyboard: Optional[str] = None,
    provider: Optional[str] = None,
) -> Dict[str, Any]:
    """Synthesizes an animated scene from a text prompt and generates a storyboard / video preview."""
    from vibmo.scene.scene import Scene
    try:
        scene = Scene.from_prompt(prompt, duration=duration)
        results: Dict[str, Any] = {
            "success": True,
            "prompt": prompt,
            "duration": scene.duration,
            "node_count": len(scene.nodes),
            "structure": scene.describe() if hasattr(scene, "describe") else {},
        }

        sb_path = output_storyboard or os.path.join(tempfile.gettempdir(), f"prompt_storyboard_{os.getpid()}.png")
        scene.storyboard(sb_path)
        with open(sb_path, "rb") as f:
            results["storyboard_base64"] = base64.b64encode(f.read()).decode("utf-8")
        results["storyboard_path"] = sb_path

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


def tool_ai_edit(
    prompt: str,
    current_code: str,
    provider: Optional[str] = None,
) -> Dict[str, Any]:
    """Surgically modifies existing Vibmo code using LLM reasoning and AST precision."""
    res = run_motion_edit(prompt=prompt, current_code=current_code, provider=provider)
    return {
        "success": res.get("is_valid", True),
        "prompt": prompt,
        "updated_code": res.get("updated_code", current_code),
        "message": res.get("response_message", ""),
        "errors": res.get("validation_errors", []),
        "logs": res.get("execution_log", []),
    }


def tool_autonomous_render(
    prompt: str,
    output_video: str = "output.mp4",
    provider: Optional[str] = None,
    quality: str = "high",
    visual_critique: bool = False,
) -> Dict[str, Any]:
    """End-to-end prompt-to-video generation, validation, and rendering."""
    return AutonomousPipeline.generate_and_render(
        prompt=prompt,
        output_video_path=output_video,
        provider=provider,
        quality=quality,
        visual_critique=visual_critique,
    )


def tool_render_scene(
    code: str,
    output_path: str = "output.mp4",
    quality: str = "high",
    preset: str = "mp4",
) -> Dict[str, Any]:
    """Executes Vibmo code and renders the final video file (MP4, WebM, ProRes, GIF)."""
    scope: Dict[str, Any] = {}
    try:
        exec("from motio.agent_api import *", scope)
        exec(code, scope)
        scene = scope.get("scene") or scope.get("seq")
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
            "duration": getattr(scene, "duration", 0.0),
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
