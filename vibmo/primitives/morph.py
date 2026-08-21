"""
Vector Path Morphing & Shape Interpolation Engine.
Enables fluid, organic shape transformations between arbitrary SVG paths and geometric shapes.
"""

from __future__ import annotations
import math
import numpy as np
from typing import Any, List, Optional, Sequence, Tuple, Union
import svgelements
import cairo

from vibmo.core.vector import Vector2D
from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.scene.node import Node
from vibmo.primitives.path import Path


class PathSampler:
    """Samples equidistant points along arbitrary SVG paths for point-matching morphing."""

    @staticmethod
    def sample_path(path_obj: Union[svgelements.Path, str, Path], num_points: int = 120) -> np.ndarray:
        if isinstance(path_obj, Path):
            svg_p = path_obj._svg_path
        elif isinstance(path_obj, str):
            svg_p = svgelements.Path(path_obj)
        else:
            svg_p = path_obj

        try:
            total_len = float(svg_p.length())
        except Exception:
            total_len = 100.0

        if total_len <= 1e-4:
            angles = np.linspace(0, 2 * math.pi, num_points, endpoint=False)
            return np.column_stack([50.0 * np.cos(angles), 50.0 * np.sin(angles)])

        pts = []
        for i in range(num_points):
            t = float(i) / max(1, num_points)
            try:
                p = svg_p.point(t)
                pts.append([float(p.x), float(p.y)])
            except Exception:
                pts.append([0.0, 0.0])

        arr = np.array(pts, dtype=np.float32)

        # Center points around origin
        center = np.mean(arr, axis=0)
        return arr - center


class Shape:
    """Preset shape generators returning SVG path strings for instant morphing."""

    @staticmethod
    def circle(radius: float = 50.0) -> str:
        r = float(radius)
        return f"M {r} 0 A {r} {r} 0 1 0 {-r} 0 A {r} {r} 0 1 0 {r} 0 Z"

    @staticmethod
    def star(outer_radius: float = 50.0, inner_radius: float = 22.0, points: int = 5) -> str:
        d_parts = []
        for i in range(points * 2):
            angle = (i * math.pi / points) - math.pi * 0.5
            r = outer_radius if i % 2 == 0 else inner_radius
            x = r * math.cos(angle)
            y = r * math.sin(angle)
            cmd = "M" if i == 0 else "L"
            d_parts.append(f"{cmd} {x:.2f} {y:.2f}")
        d_parts.append("Z")
        return " ".join(d_parts)

    @staticmethod
    def play(size: float = 50.0) -> str:
        s = float(size)
        x0 = -s * 0.4
        x1 = s * 0.6
        y0 = -s * 0.5
        y1 = s * 0.5
        return f"M {x0} {y0} L {x1} 0 L {x0} {y1} Z"

    @staticmethod
    def pause(size: float = 50.0) -> str:
        s = float(size)
        w = s * 0.25
        h = s * 0.9
        g = s * 0.15
        x1 = -g - w
        x2 = g
        y = -h * 0.5
        return f"M {x1} {y} L {x1+w} {y} L {x1+w} {y+h} L {x1} {y+h} Z M {x2} {y} L {x2+w} {y} L {x2+w} {y+h} L {x2} {y+h} Z"

    @staticmethod
    def check(size: float = 50.0) -> str:
        s = float(size)
        return f"M {-s*0.5} 0 L {-s*0.1} {s*0.4} L {s*0.6} {-s*0.4}"

    @staticmethod
    def heart(size: float = 50.0) -> str:
        s = float(size) * 0.03
        return f"M 0 {-10*s} C {-20*s} {-30*s} {-50*s} {-10*s} {-50*s} {15*s} C {-50*s} {40*s} {-20*s} {65*s} 0 {85*s} C {20*s} {65*s} {50*s} {40*s} {50*s} {15*s} C {50*s} {-10*s} {20*s} {-30*s} 0 {-10*s} Z"

    @staticmethod
    def gear(radius: float = 50.0, teeth: int = 8, tooth_depth: float = 12.0) -> str:
        d_parts = []
        n = teeth * 4
        for i in range(n):
            angle = (i * 2 * math.pi / n) - math.pi * 0.5
            is_outer = (i % 4 in (1, 2))
            r = radius + (tooth_depth if is_outer else 0.0)
            x = r * math.cos(angle)
            y = r * math.sin(angle)
            cmd = "M" if i == 0 else "L"
            d_parts.append(f"{cmd} {x:.2f} {y:.2f}")
        d_parts.append("Z")
        return " ".join(d_parts)


class _MorphSegment:
    def __init__(self, start_t: float, end_t: float, pts_a: np.ndarray, pts_b: np.ndarray, ease: EasingFunc):
        self.start_t = start_t
        self.end_t = end_t
        self.pts_a = pts_a
        self.pts_b = pts_b
        self.ease = ease

    def evaluate(self, t: float) -> np.ndarray:
        if t <= self.start_t:
            return self.pts_a
        if t >= self.end_t:
            return self.pts_b
        dur = max(1e-4, self.end_t - self.start_t)
        p = self.ease((t - self.start_t) / dur)
        return (1.0 - p) * self.pts_a + p * self.pts_b


class MorphAction(AnimationAction):
    """Schedules a morph transition segment into MorphPath's timeline."""

    def __init__(
        self,
        morph_node: MorphPath,
        target_pts: np.ndarray,
        duration: float,
        ease: EasingFunc,
        delay: float = 0.0,
    ) -> None:
        self.morph_node = morph_node
        self.target_pts = target_pts
        self.duration = duration
        self.ease = ease
        self.delay = delay
        # Dummy signal for scheduler compatibility
        super().__init__(
            signal=morph_node.dummy_signal,
            target_value=1.0,
            duration=duration,
            ease=ease,
            delay=delay,
        )

    def apply_at(self, current_time: float) -> float:
        start_t = current_time + self.delay
        end_t = start_t + self.duration
        pts_a = self.morph_node.get_points_at(start_t)
        seg = _MorphSegment(start_t, end_t, pts_a, self.target_pts, self.ease)
        self.morph_node._segments.append(seg)
        # Keep segments sorted
        self.morph_node._segments.sort(key=lambda s: s.start_t)
        return end_t


class MorphPath(Node):
    """
    Animatable vector node that smoothly morphs its geometry into any target shape or SVG path.
    """

    def __init__(
        self,
        shape: Union[str, Path] = "",
        num_points: int = 120,
        fill: Optional[Union[Color, str]] = None,
        stroke: Optional[Union[Color, str]] = colors.WHITE,
        stroke_width: float = 3.0,
        position: Union[Vector2D, Sequence[float]] = (960.0, 540.0),
        **kwargs: Any,
    ) -> None:
        super().__init__(position=position, **kwargs)
        self.num_points = num_points
        
        initial_shape = shape or Shape.circle(50.0)
        self._initial_pts = PathSampler.sample_path(initial_shape, num_points)
        self._segments: List[_MorphSegment] = []

        resolved_fill = Color.from_any(fill) if isinstance(fill, (str, Color)) else fill
        self.fill = Signal(resolved_fill, f"{self.name}.fill")
        resolved_stroke = Color.from_any(stroke) if isinstance(stroke, (str, Color)) else stroke
        self.stroke = Signal(resolved_stroke, f"{self.name}.stroke")
        self.stroke_width = Signal(float(stroke_width), f"{self.name}.stroke_width")

        self.dummy_signal = Signal(0.0, f"{self.name}.dummy")

    def get_points_at(self, t: float) -> np.ndarray:
        if not self._segments:
            return self._initial_pts

        if t < self._segments[0].start_t:
            return self._initial_pts

        for seg in self._segments:
            if seg.start_t <= t <= seg.end_t:
                return seg.evaluate(t)

        val = self._initial_pts
        for seg in self._segments:
            if t >= seg.end_t:
                val = seg.pts_b
            elif t < seg.start_t:
                break
        return val

    def morph_to(
        self,
        target_shape: Union[str, Path],
        duration: float = 1.0,
        ease: EasingFunc = Ease.in_out_cubic,
        delay: float = 0.0,
    ) -> AnimationAction:
        """
        Smoothly transforms this path into the target shape or SVG path string.
        """
        pts_b = PathSampler.sample_path(target_shape, self.num_points)
        return MorphAction(self, pts_b, duration=duration, ease=ease, delay=delay)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        pts = self.get_points_at(time)
        min_x, min_y = np.min(pts, axis=0)
        max_x, max_y = np.max(pts, axis=0)
        return (float(min_x), float(min_y), float(max_x - min_x), float(max_y - min_y))

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        pts = self.get_points_at(time)
        if len(pts) < 3:
            return

        ctx.save()

        # Draw path connecting perimeter points
        ctx.new_path()
        ctx.move_to(float(pts[0, 0]), float(pts[0, 1]))
        
        for i in range(1, len(pts)):
            ctx.line_to(float(pts[i, 0]), float(pts[i, 1]))

        ctx.close_path()

        # Fill
        fill_val = self.fill.get(time)
        if fill_val is not None:
            ctx.save()
            ctx.set_source_rgba(fill_val.r, fill_val.g, fill_val.b, fill_val.a)
            if self.stroke.get(time) is not None:
                ctx.fill_preserve()
            else:
                ctx.fill()
            ctx.restore()

        # Stroke
        stroke_val = self.stroke.get(time)
        if stroke_val is not None:
            ctx.save()
            sw = max(0.1, self.stroke_width.get(time))
            ctx.set_source_rgba(stroke_val.r, stroke_val.g, stroke_val.b, stroke_val.a)
            ctx.set_line_width(sw)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.set_line_join(cairo.LINE_JOIN_ROUND)
            ctx.stroke()
            ctx.restore()

        ctx.restore()
