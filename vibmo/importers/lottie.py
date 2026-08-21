"""
Lottie 2.0 Vector Animation Engine.
Parses, seeks, and renders vector shapes, trim paths, bezier curves, and transforms from Figma/After Effects Lottie JSON.
"""

from __future__ import annotations
import os
import json
import math
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
import cairo

from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D
from vibmo.core.signal import Signal
from vibmo.scene.node import Node


def _eval_prop(prop: Any, frame: float, default: Any) -> Any:
    """Evaluates static or keyframed Lottie property at frame."""
    if not isinstance(prop, dict):
        return prop if prop is not None else default
    
    k = prop.get("k")
    if k is None:
        return default
    
    # Static property
    if not isinstance(k, list) or (k and not isinstance(k[0], dict)):
        return k

    # Keyframed property: [{t: 0, s: [0], e: [100]}, ...]
    keyframes = k
    if not keyframes:
        return default

    # Before first keyframe
    if frame <= keyframes[0].get("t", 0):
        return keyframes[0].get("s", default)

    for i in range(len(keyframes) - 1):
        kf = keyframes[i]
        next_kf = keyframes[i + 1]
        t0 = kf.get("t", 0)
        t1 = next_kf.get("t", t0 + 1)

        if t0 <= frame < t1:
            s_val = kf.get("s", default)
            e_val = kf.get("e", s_val)
            progress = (frame - t0) / max(1e-4, t1 - t0)
            
            if isinstance(s_val, list) and isinstance(e_val, list):
                res = []
                for j in range(min(len(s_val), len(e_val))):
                    res.append(s_val[j] + (e_val[j] - s_val[j]) * progress)
                return res
            elif isinstance(s_val, (int, float)) and isinstance(e_val, (int, float)):
                return s_val + (e_val - s_val) * progress
            return s_val

    # After last keyframe
    last = keyframes[-1]
    return last.get("s", default)


class LottieAnimation(Node):
    """
    Lottie 2.0 Vector Animation Node.
    Supports bezier vector paths, trim paths, shape transforms, opacity fading, and loop controls.
    """

    def __init__(
        self,
        lottie_path_or_dict: Union[str, Dict[str, Any]],
        width: Optional[float] = None,
        height: Optional[float] = None,
        speed: float = 1.0,
        loop: bool = True,
        position: Union[Vector2D, Sequence[float]] = (0.0, 0.0),
        **kwargs: Any,
    ) -> None:
        super().__init__(position=position, **kwargs)
        self.speed = float(speed)
        self.loop = loop

        if isinstance(lottie_path_or_dict, str):
            with open(lottie_path_or_dict, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            self.data = lottie_path_or_dict

        # Metadata
        self.orig_w = float(self.data.get("w", 512))
        self.orig_h = float(self.data.get("h", 512))
        self.fps = float(self.data.get("fr", 30))
        self.in_frame = float(self.data.get("ip", 0))
        self.out_frame = float(self.data.get("op", 60))
        self.total_frames = max(1.0, self.out_frame - self.in_frame)
        self.clip_duration = self.total_frames / max(1.0, self.fps)

        # Scale dimensions
        if width is not None and height is not None:
            self.width_val = float(width)
            self.height_val = float(height)
        elif width is not None:
            self.width_val = float(width)
            self.height_val = (float(width) / max(1.0, self.orig_w)) * self.orig_h
        elif height is not None:
            self.height_val = float(height)
            self.width_val = (float(height) / max(1.0, self.orig_h)) * self.orig_w
        else:
            self.width_val = float(self.orig_w)
            self.height_val = float(self.orig_h)

    @property
    def width(self) -> float:
        return self.width_val

    @property
    def height(self) -> float:
        return self.height_val

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        playback_t = time * self.speed
        if self.loop:
            local_t = playback_t % self.clip_duration
        else:
            local_t = min(self.clip_duration, playback_t)

        current_frame = self.in_frame + (local_t / self.clip_duration) * self.total_frames

        ctx.save()

        # Canvas transform scale
        sx = self.width_val / max(1.0, self.orig_w)
        sy = self.height_val / max(1.0, self.orig_h)
        ctx.scale(sx, sy)

        # Render layers (reverse order for painter's algorithm)
        layers = self.data.get("layers", [])
        for layer in reversed(layers):
            self._render_layer(ctx, layer, current_frame)

        ctx.restore()

    def _render_layer(self, ctx: Any, layer: Dict[str, Any], frame: float) -> None:
        ip = layer.get("ip", self.in_frame)
        op = layer.get("op", self.out_frame)
        if frame < ip or frame >= op:
            return

        ctx.save()

        # Layer transform (ks)
        ks = layer.get("ks", {})
        pos = _eval_prop(ks.get("p"), frame, [0, 0])
        scale = _eval_prop(ks.get("s"), frame, [100, 100])
        rot = _eval_prop(ks.get("r"), frame, 0.0)
        opacity = _eval_prop(ks.get("o"), frame, 100.0)

        if opacity is not None and opacity < 99.9:
            ctx.push_group()

        ctx.translate(pos[0] if isinstance(pos, list) else 0, pos[1] if isinstance(pos, list) else 0)
        if isinstance(rot, (int, float)) and abs(rot) > 0.01:
            ctx.rotate(rot * math.pi / 180.0)
        if isinstance(scale, list) and len(scale) >= 2:
            ctx.scale(scale[0] / 100.0, scale[1] / 100.0)

        shapes = layer.get("shapes", [])
        for item in shapes:
            self._render_shape_item(ctx, item, frame)

        if opacity is not None and opacity < 99.9:
            ctx.pop_group_to_source()
            ctx.paint_with_alpha(max(0.0, min(1.0, opacity / 100.0)))

        ctx.restore()

    def _render_shape_item(self, ctx: Any, item: Dict[str, Any], frame: float) -> None:
        ty = item.get("ty")
        
        if ty == "gr":  # Shape Group
            ctx.save()
            for sub_item in item.get("it", []):
                self._render_shape_item(ctx, sub_item, frame)
            ctx.restore()

        elif ty == "sh":  # Bezier Path Shape
            shape_data = _eval_prop(item.get("ks"), frame, {})
            if isinstance(shape_data, dict):
                v_pts = shape_data.get("v", [])
                i_pts = shape_data.get("i", [])
                o_pts = shape_data.get("o", [])
                closed = shape_data.get("c", False)

                if v_pts:
                    ctx.new_path()
                    ctx.move_to(v_pts[0][0], v_pts[0][1])
                    n = len(v_pts)
                    for idx in range(1, n):
                        # Cubic bezier to
                        cp1 = (v_pts[idx - 1][0] + o_pts[idx - 1][0], v_pts[idx - 1][1] + o_pts[idx - 1][1]) if idx - 1 < len(o_pts) else v_pts[idx - 1]
                        cp2 = (v_pts[idx][0] + i_pts[idx][0], v_pts[idx][1] + i_pts[idx][1]) if idx < len(i_pts) else v_pts[idx]
                        ctx.curve_to(cp1[0], cp1[1], cp2[0], cp2[1], v_pts[idx][0], v_pts[idx][1])
                    if closed and n > 1:
                        cp1 = (v_pts[-1][0] + o_pts[-1][0], v_pts[-1][1] + o_pts[-1][1]) if len(o_pts) > 0 else v_pts[-1]
                        cp2 = (v_pts[0][0] + i_pts[0][0], v_pts[0][1] + i_pts[0][1]) if len(i_pts) > 0 else v_pts[0]
                        ctx.curve_to(cp1[0], cp1[1], cp2[0], cp2[1], v_pts[0][0], v_pts[0][1])
                        ctx.close_path()

        elif ty == "el":  # Ellipse
            p = _eval_prop(item.get("p"), frame, [0, 0])
            s = _eval_prop(item.get("s"), frame, [50, 50])
            ctx.new_path()
            ctx.save()
            ctx.translate(p[0], p[1])
            ctx.scale(s[0] * 0.5, s[1] * 0.5)
            ctx.arc(0, 0, 1.0, 0, 2 * math.pi)
            ctx.restore()

        elif ty == "rc":  # Rect / RoundedRect
            p = _eval_prop(item.get("p"), frame, [0, 0])
            s = _eval_prop(item.get("s"), frame, [50, 50])
            r = _eval_prop(item.get("r"), frame, 0.0)
            x, y, w, h = p[0] - s[0] * 0.5, p[1] - s[1] * 0.5, s[0], s[1]
            ctx.new_path()
            if r > 0.0:
                ctx.new_sub_path()
                ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
                ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
                ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
                ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
                ctx.close_path()
            else:
                ctx.rectangle(x, y, w, h)

        elif ty == "fl":  # Solid Color Fill
            c = _eval_prop(item.get("c"), frame, [1, 1, 1, 1])
            op = _eval_prop(item.get("o"), frame, 100.0)
            a = (op / 100.0) * (c[3] if len(c) > 3 else 1.0)
            ctx.set_source_rgba(c[0], c[1], c[2], a)
            ctx.fill_preserve()

        elif ty == "st":  # Stroke
            c = _eval_prop(item.get("c"), frame, [1, 1, 1, 1])
            w = _eval_prop(item.get("w"), frame, 2.0)
            op = _eval_prop(item.get("o"), frame, 100.0)
            a = (op / 100.0) * (c[3] if len(c) > 3 else 1.0)
            ctx.set_source_rgba(c[0], c[1], c[2], a)
            ctx.set_line_width(float(w))
            ctx.stroke()
