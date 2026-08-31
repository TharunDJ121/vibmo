"""
Studio Session State, Scene Synchronization, Dynamic Bounds Evaluator & Python Exporter.
"""

from __future__ import annotations
import os
import traceback
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np

from vibmo.core.vector import Vector2D
from vibmo.core.color import Color


DEFAULT_STARTER_SCRIPT = """from vibmo.agent_api import *

# Initialize Scene (1080p @ 60 FPS, Dark Navy aesthetic)
scene = Scene(
    width=1920,
    height=1080,
    fps=60,
    duration=4.5,
    background=colors.DARK_NAVY,
)

# Assemble Semantic Components with Auto-Layout
card = GlassCard(direction="column", gap=16, padding=32, corner_radius=24, position=(200, 200))
icon = Icon("lucide:sparkles", size=36, color=colors.INDIGO)
title = KineticText("Vibmo Studio Pro", font_size=32, bold=True)
counter = MetricCounter(start_val=0, end_val=148000, prefix="$", suffix=" MRR", font_size=52, bold=True, color=colors.EMERALD)

card.add(icon, title, counter)
scene.add(card)

# Add Cinematic Post-FX
scene.add_post_fx(Vignette(intensity=0.25), FilmGrain(amount=0.02))

# Choreograph with Natural Verbs
@scene.animate
def main():
    yield card.pop_in(duration=0.8)
    yield scene.all(
        title.reveal_characters(stagger=0.025),
        counter.count_to(duration=1.8, ease=Ease.out_expo),
    )
    card.float_idle(amplitude=6, speed=1.2)
    yield scene.wait(1.5)
"""


def create_default_scene() -> Any:
    """Creates a production starter scene when studio is launched without any script."""
    from vibmo.scene.scene import Scene
    from vibmo.components.glass import GlassCard
    from vibmo.components.counter import MetricCounter
    from vibmo.typography.kinetic import KineticText
    from vibmo.importers.icons import Icon
    from vibmo.fx.filters import Vignette, FilmGrain
    from vibmo.core.color import colors
    from vibmo.core.easing import Ease

    scene = Scene(width=1920, height=1080, fps=60.0, duration=4.5, background=colors.DARK_NAVY)
    card = GlassCard(direction="column", gap=16, padding=32, corner_radius=24, position=(200, 200))
    icon = Icon("lucide:sparkles", size=36, color=colors.INDIGO)
    title = KineticText("Vibmo Studio Pro", font_size=32, bold=True)
    counter = MetricCounter(start_val=0, end_val=148000, prefix="$", suffix=" MRR", font_size=52, bold=True, color=colors.EMERALD)

    card.add(icon, title, counter)
    scene.add(card)
    scene.add_post_fx(Vignette(intensity=0.25), FilmGrain(amount=0.02))

    @scene.animate
    def main():
        yield card.pop_in(duration=0.8)
        yield scene.all(
            title.reveal_characters(stagger=0.025),
            counter.count_to(duration=1.8, ease=Ease.out_expo),
        )
        card.float_idle(amplitude=6.0, speed=1.2)
        yield scene.wait(1.5)

    return scene


def collect_all_nodes(nodes: List[Any]) -> List[Any]:
    """Recursively flattens node tree for layer inspection, filtering internal sub-glyphs."""
    flat: List[Any] = []
    for n in nodes:
        cls_name = n.__class__.__name__
        if cls_name != "GlyphNode":
            flat.append(n)
        if hasattr(n, "children") and n.children:
            flat.extend(collect_all_nodes(n.children))
    return flat


class StudioState:
    """Manages the live session state and bi-directional scene synchronization."""

    def __init__(self, scene: Optional[Any] = None, script_path: Optional[str] = None) -> None:
        self.script_path = script_path
        self.current_code = DEFAULT_STARTER_SCRIPT

        if script_path and os.path.exists(script_path):
            try:
                with open(script_path, "r", encoding="utf-8") as f:
                    self.current_code = f.read()
            except Exception:
                pass

        if scene is not None:
            self.scene = scene
        elif script_path and os.path.exists(script_path):
            ok, err, _ = self.execute_python_code(self.current_code)
            if not ok or self.scene is None:
                self.scene = create_default_scene()
        else:
            self.scene = create_default_scene()

        self.active_page: str = "motion"  # motion, fusion, color, fairlight, deliver
        self.selected_node_id: Optional[str] = None
        self.user_overrides: Dict[str, Dict[str, Any]] = {}  # node_id -> {prop: val}
        self.param_overrides: Dict[str, Any] = {}
        self.color_grade_override: Optional[Dict[str, Any]] = None

    def execute_python_code(self, code: str) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """Executes arbitrary Python Vibmo code dynamically in the studio."""
        scope: Dict[str, Any] = {}
        try:
            exec("from vibmo.agent_api import *", scope)
            exec(code, scope)

            new_scene = scope.get("scene")
            if not new_scene:
                for v in scope.values():
                    if hasattr(v, "nodes") and hasattr(v, "duration"):
                        new_scene = v
                        break

            if not new_scene:
                return False, "No 'scene' or 'comp' instance found in Python script", None

            self.scene = new_scene
            self.current_code = code
            self.user_overrides.clear()
            self.param_overrides.clear()
            self.color_grade_override = None
            meta = self.get_metadata(current_time=0.0)
            return True, None, meta
        except Exception as e:
            return False, f"{type(e).__name__}: {str(e)}\n\n{traceback.format_exc()}", None

    def load_python_code(self, code: str) -> Tuple[bool, Optional[str]]:
        """Loads and applies new Python code to live studio session."""
        ok, err, _ = self.execute_python_code(code)
        if ok:
            self.current_code = code
        return ok, err



    def get_metadata(self, current_time: float = 0.0) -> Dict[str, Any]:
        """Returns comprehensive scene, node, layer, and track metadata at timestamp current_time."""
        params_dict = {}
        if hasattr(self.scene, "params"):
            for k, p in self.scene.params.items():
                val = p.get()
                params_dict[k] = {
                    "value": val.to_hex() if hasattr(val, "to_hex") else val,
                    "type": p.param_type,
                    "min": p.min_val,
                    "max": p.max_val,
                    "description": p.description,
                }

        raw_nodes = []
        if hasattr(self.scene, "nodes"):
            raw_nodes = self.scene.nodes
        elif hasattr(self.scene, "scenes"):
            for sub_s in self.scene.scenes:
                if hasattr(sub_s, "nodes"):
                    raw_nodes.extend(sub_s.nodes)

        all_nodes = collect_all_nodes(raw_nodes)
        nodes_list = []
        for n in all_nodes:
            pos = n.position.get(current_time)
            scale = n.scale.get(current_time)
            bx, by, bw, bh = n.world_bounds(current_time) if hasattr(n, "world_bounds") else n.local_bounds(current_time)
            
            nodes_list.append({
                "id": n.id,
                "name": n.name,
                "type": n.__class__.__name__,
                "x": pos.x if hasattr(pos, "x") else float(pos[0]),
                "y": pos.y if hasattr(pos, "y") else float(pos[1]),
                "bounds_x": bx,
                "bounds_y": by,
                "width": bw,
                "height": bh,
                "scale_x": scale.x if hasattr(scale, "x") else float(scale[0]),
                "scale_y": scale.y if hasattr(scale, "y") else float(scale[1]),
                "rotation": float(n.rotation.get(current_time)),
                "rotate_x": float(n.rotate_x.get(current_time)) if hasattr(n, "rotate_x") else 0.0,
                "rotate_y": float(n.rotate_y.get(current_time)) if hasattr(n, "rotate_y") else 0.0,
                "z": float(n.z.get(current_time)) if hasattr(n, "z") else 0.0,
                "opacity": float(n.opacity.get(current_time)),
                "in_point": getattr(n, "in_point", 0.0),
                "out_point": getattr(n, "out_point", None),
                "parent_id": n.parent.id if n.parent else None,
            })

        # Foley cues and audio metadata
        sfx_cues = []
        if hasattr(self.scene, "sfx") and hasattr(self.scene.sfx, "cues"):
            for cue_time, sound_name, volume in self.scene.sfx.cues:
                sfx_cues.append({
                    "time": cue_time,
                    "sound": sound_name,
                    "volume": volume,
                })

        return {
            "type": "meta",
            "duration": self.scene.duration,
            "fps": self.scene.fps,
            "width": self.scene.width,
            "height": self.scene.height,
            "background": self.scene.background.to_hex() if hasattr(self.scene.background, "to_hex") else "#030712",
            "has_audio": bool(self.scene.audio_path or (hasattr(self.scene, "sfx") and len(self.scene.sfx.cues) > 0)),
            "params": params_dict,
            "nodes": nodes_list,
            "sfx_cues": sfx_cues,
            "post_fx": [fx.__class__.__name__ for fx in self.scene.post_fx],
        }

    def set_param(self, name: str, value: Any) -> None:
        if name in self.scene.params:
            if isinstance(value, str) and value.startswith("#"):
                self.scene.params[name].set(Color.hex(value))
            else:
                self.scene.params[name].set(value)
            self.param_overrides[name] = value

    def set_node_property(self, node_id: str, prop: str, value: Any) -> None:
        all_nodes = collect_all_nodes(self.scene.nodes)
        target_node = None
        for n in all_nodes:
            if n.id == node_id:
                target_node = n
                break
        if not target_node:
            return

        if node_id not in self.user_overrides:
            self.user_overrides[node_id] = {}
        self.user_overrides[node_id][prop] = value

        if prop == "position_x":
            curr_y = target_node.position.get(0.0).y
            target_node.position.set(Vector2D(float(value), curr_y))
        elif prop == "position_y":
            curr_x = target_node.position.get(0.0).x
            target_node.position.set(Vector2D(curr_x, float(value)))
        elif prop == "scale":
            target_node.scale.set(Vector2D(float(value), float(value)))
        elif prop == "rotation":
            target_node.rotation.set(float(value))
        elif prop == "rotate_x":
            if hasattr(target_node, "rotate_x"):
                target_node.rotate_x.set(float(value))
        elif prop == "rotate_y":
            if hasattr(target_node, "rotate_y"):
                target_node.rotate_y.set(float(value))
        elif prop == "opacity":
            target_node.opacity.set(float(value))
        elif prop == "z":
            if hasattr(target_node, "z"):
                target_node.z.set(float(value))
        elif prop == "color":
            if hasattr(target_node, "color"):
                from vibmo.core.color import Color
                target_node.color = Color.from_any(value)
        elif prop == "font_size":
            if hasattr(target_node, "font_size"):
                target_node.font_size = float(value)

        self.color_grade_override: Optional[Dict[str, Any]] = None

    def set_color_grade(
        self,
        lift: Optional[Tuple[float, float, float]] = None,
        gamma: Optional[Tuple[float, float, float]] = None,
        gain: Optional[Tuple[float, float, float]] = None,
        exposure: Optional[float] = None,
        contrast: Optional[float] = None,
        saturation: Optional[float] = None,
        temperature: Optional[float] = None,
        tint: Optional[float] = None,
    ) -> None:
        """Applies or updates a ColorCorrection post-fx filter dynamically."""
        from vibmo.fx.filters import ColorCorrection

        # Find existing ColorCorrection filter or instantiate a new one
        cc = None
        for fx in self.scene.post_fx:
            if isinstance(fx, ColorCorrection):
                cc = fx
                break
        
        if cc is None:
            cc = ColorCorrection()
            self.scene.post_fx.append(cc)

        if lift is not None:
            cc.lift = np.array(lift, dtype=np.float32)
        if gamma is not None:
            cc.gamma = np.array(gamma, dtype=np.float32)
        if gain is not None:
            cc.gain = np.array(gain, dtype=np.float32)
        if exposure is not None:
            cc.exposure = float(exposure)
        if contrast is not None:
            cc.contrast = float(contrast)
        if saturation is not None:
            cc.saturation = float(saturation)
        if temperature is not None:
            cc.temperature = float(temperature)
        if tint is not None:
            cc.tint = float(tint)

        if self.color_grade_override is None:
            self.color_grade_override = {}
        if lift is not None: self.color_grade_override["lift"] = lift
        if gamma is not None: self.color_grade_override["gamma"] = gamma
        if gain is not None: self.color_grade_override["gain"] = gain
        if exposure is not None: self.color_grade_override["exposure"] = exposure
        if contrast is not None: self.color_grade_override["contrast"] = contrast
        if saturation is not None: self.color_grade_override["saturation"] = saturation
        if temperature is not None: self.color_grade_override["temperature"] = temperature
        if tint is not None: self.color_grade_override["tint"] = tint

    def export_python_code(self) -> str:
        """Generates exact, clean Python code for all modified parameters, transforms, and color grades."""
        lines = [
            "# ✦ Vibmo Studio Overrides",
            "# Paste into your motion script or scene setup:",
            "",
        ]

        if self.param_overrides:
            lines.append("# Scene Parameters")
            for k, v in self.param_overrides.items():
                if isinstance(v, str) and v.startswith("#"):
                    lines.append(f'scene.param("{k}", Color.hex("{v}"))')
                else:
                    lines.append(f'scene.param("{k}", {v})')
            lines.append("")

        if self.color_grade_override:
            lines.append("# Cinematic Color Grade")
            args = []
            for k, v in self.color_grade_override.items():
                args.append(f"{k}={v}")
            lines.append(f"scene.add_post_fx(ColorCorrection({', '.join(args)}))")
            lines.append("")

        if self.user_overrides:
            lines.append("# Node Transform Adjustments")
            all_nodes = {n.id: n for n in collect_all_nodes(self.scene.nodes)}
            for nid, props in self.user_overrides.items():
                node = all_nodes.get(nid)
                name = node.name if node else nid
                var_name = name.lower().replace("-", "_").replace(" ", "_")
                for p, v in props.items():
                    if p == "position_x":
                        lines.append(f"{var_name}.position.x.set({v})")
                    elif p == "position_y":
                        lines.append(f"{var_name}.position.y.set({v})")
                    elif p == "scale":
                        lines.append(f"{var_name}.scale.set(({v}, {v}))")
                    elif p == "rotation":
                        lines.append(f"{var_name}.rotation.set({v})")
                    elif p == "rotate_x":
                        lines.append(f"{var_name}.rotate_x.set({v})")
                    elif p == "rotate_y":
                        lines.append(f"{var_name}.rotate_y.set({v})")
                    elif p == "opacity":
                        lines.append(f"{var_name}.opacity.set({v})")
            lines.append("")

        return "\n".join(lines)

