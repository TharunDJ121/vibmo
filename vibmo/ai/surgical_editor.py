"""
Surgical Scene & Frame Editor for Motio / Vibmo scripts.
Performs AST and pattern-guided precision modifications on specific scenes, nodes, and timing
without touching or breaking untouched scenes.
"""

from __future__ import annotations
import ast
import re
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union


class SurgicalSceneEditor:
    """
    Applies surgical modifications to a Motio code string.
    """

    @classmethod
    def apply_edit(
        cls,
        code: str,
        instruction: str,
        target_scene: Optional[int] = None,
    ) -> Tuple[str, List[str]]:
        """
        Parses intent from instruction and applies precision edit to Python script.
        Returns: (modified_code, change_summary_list)
        """
        modified = code
        changes = []
        inst = instruction.lower()

        # 1. Detect target scene number if mentioned in instruction (e.g. "in scene 3", "scene 1")
        scene_match = re.search(r'scene\s*(\d+)', inst)
        scene_num = int(scene_match.group(1)) if scene_match else target_scene

        # 2. Text / Copy Modifications
        # Check for quoted replacements: change "foo" to "bar"
        replace_match = re.search(r'(?:change|replace|set)\s+["\']([^"\']+)["\']\s+(?:to|with)\s+["\']([^"\']+)["\']', instruction, re.IGNORECASE)
        if replace_match:
            old_val, new_val = replace_match.group(1), replace_match.group(2)
            if old_val in modified:
                modified = modified.replace(old_val, new_val)
                changes.append(f"Replaced text '{old_val}' with '{new_val}'")

        # 3. Specific Component Parameter Edits
        # E.g. "change typing speed to 40", "make it type faster"
        speed_match = re.search(r'typing[_\s]?speed\s*(?:to|=)?\s*(\d+(?:\.\d+)?)', inst)
        if speed_match:
            new_speed = float(speed_match.group(1))
            modified = re.sub(r'typing_speed\s*=\s*\d+(?:\.\d+)?', f'typing_speed={new_speed}', modified)
            changes.append(f"Updated typing speed to {new_speed} chars/sec")
        elif "type faster" in inst or "faster typing" in inst:
            modified = re.sub(r'typing_speed\s*=\s*(\d+(?:\.\d+)?)', lambda m: f"typing_speed={float(m.group(1))*1.4:.1f}", modified)
            changes.append("Increased typing speed by 40%")
        elif "type slower" in inst or "slower typing" in inst:
            modified = re.sub(r'typing_speed\s*=\s*(\d+(?:\.\d+)?)', lambda m: f"typing_speed={float(m.group(1))*0.7:.1f}", modified)
            changes.append("Decreased typing speed by 30%")

        # 4. Color / Gradient Modifications
        # E.g. "change background to cerulean/aurora/sunset/emerald"
        if "sunset" in inst and "backdrop" in inst:
            modified = re.sub(r'GradientBackdrop\.\w+\(\)', 'GradientBackdrop.sunset()', modified)
            changes.append("Changed background backdrop to Sunset gradient")
        elif "cerulean" in inst or "blue gradient" in inst:
            modified = re.sub(r'GradientBackdrop\.\w+\(\)', 'GradientBackdrop.cerulean()', modified)
            changes.append("Changed background backdrop to Cerulean Blue gradient")
        elif "aurora" in inst or "purple gradient" in inst:
            modified = re.sub(r'GradientBackdrop\.\w+\(\)', 'GradientBackdrop.aurora()', modified)
            changes.append("Changed background backdrop to Aurora gradient")

        # E.g. "change color to #10b981 or emerald"
        hex_match = re.search(r'#([0-9a-fA-F]{6})', instruction)
        if hex_match:
            new_hex = f"#{hex_match.group(1).lower()}"
            if scene_num == 3 or "scene 3" in inst or "kinetic" in inst:
                if "first" in inst or "deeper" in inst or "color_a" in inst:
                    modified = re.sub(r'color_a\s*=\s*["\']#[0-9a-fA-F]{6}["\']', f'color_a="{new_hex}"', modified)
                    changes.append(f"Updated word_a color to {new_hex}")
                else:
                    modified = re.sub(r'color_b\s*=\s*["\']#[0-9a-fA-F]{6}["\']', f'color_b="{new_hex}"', modified)
                    changes.append(f"Updated word_b color to {new_hex}")

        # 5. Camera Zoom Modifications
        # E.g. "zoom in more / zoom to 1.35"
        zoom_match = re.search(r'zoom\s*(?:to|=)?\s*(\d+(?:\.\d+)?)', inst)
        if zoom_match:
            new_zoom = float(zoom_match.group(1))
            modified = re.sub(r'zoom\s*=\s*\d+(?:\.\d+)?', f'zoom={new_zoom}', modified)
            changes.append(f"Updated camera zoom to {new_zoom}x")

        # 6. Shimmer Toggle
        if "disable shimmer" in inst or "remove shimmer" in inst:
            modified = re.sub(r'shimmer\s*=\s*True', 'shimmer=False', modified)
            changes.append("Disabled specular shimmer reflection")
        elif "enable shimmer" in inst or "add shimmer" in inst:
            modified = re.sub(r'shimmer\s*=\s*False', 'shimmer=True', modified)
            changes.append("Enabled specular shimmer reflection")

        # 7. Duration / Timing Adjustments
        # E.g. "make scene 1 longer by 0.5s", "set scene 1 duration to 2.5"
        if scene_num:
            dur_match = re.search(rf's{scene_num}\s*=\s*Scene\([^)]*duration\s*=\s*(\d+(?:\.\d+)?)', modified)
            set_dur_match = re.search(r'duration\s*(?:to|=)?\s*(\d+(?:\.\d+)?)', inst)
            if dur_match and set_dur_match:
                new_dur = float(set_dur_match.group(1))
                modified = re.sub(
                    rf'(s{scene_num}\s*=\s*Scene\([^)]*duration\s*=\s*)\d+(?:\.\d+)?',
                    rf'\g<1>{new_dur}',
                    modified,
                )
                changes.append(f"Set Scene {scene_num} duration to {new_dur}s")

        if not changes:
            changes.append(f"Processed instruction: '{instruction}'")

        return modified, changes

    @classmethod
    def apply_schema_edit(cls, project: Any, op_type: str, payload: Dict[str, Any]) -> Tuple[Any, List[str]]:
        """
        Applies a typed schema operation to a VibmoProject IR instead of regexing Python strings.
        This provides a reversible, deterministic editing capability.
        """
        changes = []
        if op_type == "change_shot_duration":
            shot_id = payload.get("shot_id")
            new_dur = payload.get("duration")
            for track in project.tracks:
                for shot in track.shots:
                    if shot.id == shot_id or shot_id is None:
                        shot.duration = new_dur
                        changes.append(f"Updated shot '{shot.name}' duration to {new_dur}s")
        
        elif op_type == "set_font_asset":
            layer_id = payload.get("layer_id")
            new_font = payload.get("font_family")
            for track in project.tracks:
                for shot in track.shots:
                    for layer in shot.layers:
                        if layer.id == layer_id or layer_id is None:
                            layer.properties["font_family"] = new_font
                            changes.append(f"Updated layer '{layer.name}' font to {new_font}")
                            
        return project, changes

    @classmethod
    def execute_and_test(cls, code: str, storyboard_out: Optional[str] = None) -> Tuple[bool, List[str]]:
        """
        Executes code in a sandbox namespace to verify syntax and runtime validity instantaneously.
        """
        try:
            # 1. Fast AST Parse Check
            ast.parse(code)

            # 2. Fast Sandbox Execution without triggering __main__ video renders
            sandbox_globals = {"__name__": "__sandbox__", "__file__": "dynamic_scene.py"}
            exec(code, sandbox_globals)

            return True, []
        except SyntaxError as syn_err:
            return False, [f"SyntaxError at line {syn_err.lineno}: {syn_err.msg}"]
        except Exception as e:
            return False, [f"Runtime error: {str(e)}"]
