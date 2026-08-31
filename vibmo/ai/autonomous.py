"""
Autonomous End-to-End AI Motion Graphics Pipeline.
Transforms natural language prompts directly into validated motion graphics scripts,
storyboard contact sheets, visual feedback iterations, and final rendered videos.
"""

from __future__ import annotations
import os
import json
import base64
import tempfile
import traceback
from typing import Any, Dict, List, Optional, Tuple

from vibmo.ai.graph import run_motion_edit
from vibmo.ai.llm_bridge import LLMBridge
from vibmo.ai.prompts import build_system_prompt
from vibmo.ai.memory import get_global_memory
from vibmo.scene.scene import Scene


class AutonomousPipeline:
    """
    Orchestrates the complete autonomous prompt-to-video workflow.
    """

    @classmethod
    def generate_and_render(
        cls,
        prompt: str,
        output_video_path: str = "output.mp4",
        output_storyboard_path: Optional[str] = None,
        provider: Optional[str] = None,
        quality: str = "high",
        auto_repair: bool = True,
        visual_critique: bool = False,
    ) -> Dict[str, Any]:
        """
        Executes end-to-end autonomous motion generation:
        1. Synthesizes script using LLM / LangGraph
        2. Executes in sandbox and validates timeline & layout bounds
        3. Renders 6-frame storyboard contact sheet
        4. (Optional) Performs multimodal visual self-critique
        5. Renders master MP4 video
        """
        result: Dict[str, Any] = {
            "prompt": prompt,
            "success": False,
            "code": "",
            "storyboard_path": None,
            "storyboard_base64": None,
            "video_path": None,
            "errors": [],
            "logs": [],
        }

        # 1. Generate / Edit Code via LangGraph
        graph_result = run_motion_edit(prompt=prompt, current_code="", provider=provider)
        code = graph_result.get("updated_code", "")
        result["code"] = code
        result["logs"].extend(graph_result.get("execution_log", []))

        if not code or not graph_result.get("is_valid", False):
            result["errors"].extend(graph_result.get("validation_errors", ["Code generation failed"]))
            return result

        # 2. Execute code in memory to obtain scene
        scope: Dict[str, Any] = {}
        try:
            exec("from motio.agent_api import *", scope)
            exec(code, scope)
            scene = scope.get("scene") or scope.get("seq")
            if not scene:
                for v in scope.values():
                    if hasattr(v, "render") and (hasattr(v, "nodes") or hasattr(v, "scenes")):
                        scene = v
                        break

            if not scene:
                result["errors"].append("No valid Scene or Sequence instance found in generated code.")
                return result

            # 3. Generate Storyboard
            sb_path = output_storyboard_path or os.path.join(tempfile.gettempdir(), f"storyboard_{os.getpid()}.png")
            if hasattr(scene, "storyboard"):
                scene.storyboard(sb_path, rows=2, cols=3)
                result["storyboard_path"] = sb_path
                if os.path.exists(sb_path):
                    with open(sb_path, "rb") as f:
                        result["storyboard_base64"] = base64.b64encode(f.read()).decode("utf-8")

            # 4. Optional Multimodal Visual Critique
            if visual_critique and result.get("storyboard_base64"):
                critique_prompt = (
                    "Inspect this 6-frame motion graphics storyboard. "
                    "Are the typography, layout balance, cards, and pacing well-proportioned? "
                    "Provide a 1-sentence design rating."
                )
                success, critique, _ = LLMBridge.call(
                    prompt=critique_prompt,
                    provider=provider,
                    images_base64=[result["storyboard_base64"]],
                )
                if success:
                    result["logs"].append(f"Visual critique: {critique}")

            # 5. Render Master Video
            out_abs = os.path.abspath(output_video_path)
            os.makedirs(os.path.dirname(out_abs) if os.path.dirname(out_abs) else ".", exist_ok=True)
            if hasattr(scene, "render"):
                scene.render(output_path=out_abs, quality=quality, show_progress=False)
                result["video_path"] = out_abs
                result["success"] = True
                result["duration"] = getattr(scene, "duration", 0.0)

        except Exception as e:
            result["errors"].append(f"Pipeline execution error: {str(e)}")
            result["logs"].append(traceback.format_exc())

        return result
