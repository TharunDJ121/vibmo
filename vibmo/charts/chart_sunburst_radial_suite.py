"""
Radial Sunburst Hierarchy Chart Suite.
"""

from __future__ import annotations
import math
from typing import Any, Dict, List, Optional, Tuple, Union
import cairo

from vibmo.scene.node import Node
from vibmo.core.signal import Signal
from vibmo.core.color import Color, colors
from vibmo.core.easing import Ease
from vibmo.typography.text import Text


class ExpandingRingArc(Node):
    """Smooth expanding arc segment animated from center outward on scene entrance."""

    def __init__(
        self,
        inner_radius: float = 50.0,
        outer_radius: float = 100.0,
        start_angle: float = 0.0,
        end_angle: float = math.pi / 2,
        fill: Optional[Union[Color, str]] = colors.CYAN,
        stroke: Optional[Union[Color, str]] = colors.WHITE,
        stroke_width: float = 1.0,
        expand_progress: float = 1.0,
        gap_angle: float = 0.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.inner_radius = Signal(float(inner_radius), f"{self.name}.inner_radius")
        self.outer_radius = Signal(float(outer_radius), f"{self.name}.outer_radius")
        self.start_angle = Signal(float(start_angle), f"{self.name}.start_angle")
        self.end_angle = Signal(float(end_angle), f"{self.name}.end_angle")
        self.gap_angle = Signal(float(gap_angle), f"{self.name}.gap_angle")

        self.fill = Signal(Color.from_any(fill) if fill else None, f"{self.name}.fill")
        self.stroke = Signal(Color.from_any(stroke) if stroke else None, f"{self.name}.stroke")
        self.stroke_width = Signal(float(stroke_width), f"{self.name}.stroke_width")

        # 0.0 means radius is collapsed to inner_radius, 1.0 means expanded to outer_radius
        self.expand_progress = Signal(float(expand_progress), f"{self.name}.expand_progress")

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        r = max(0.0, self.outer_radius.get(time))
        return (-r, -r, 2.0 * r, 2.0 * r)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ir = max(0.0, self.inner_radius.get(time))
        or_target = max(0.0, self.outer_radius.get(time))
        prog = max(0.0, min(1.0, self.expand_progress.get(time)))

        if prog <= 0.0:
            return

        cur_or = ir + (or_target - ir) * prog
        if cur_or <= ir:
            return

        base_sa = self.start_angle.get(time)
        base_ea = self.end_angle.get(time)
        gap = self.gap_angle.get(time)

        # Apply gap non-destructively for rendering only
        sa = base_sa
        ea = base_ea
        if base_ea - base_sa > gap * 2:
            sa += gap
            ea -= gap

        if abs(ea - sa) < 1e-6:
            return

        ctx.new_path()
        # Outer arc
        ctx.arc(0, 0, cur_or, sa, ea)
        # Inner arc (reverse direction)
        ctx.arc_negative(0, 0, ir, ea, sa)
        ctx.close_path()

        fill_val = self.fill.get(time)
        if fill_val is not None:
            ctx.save()
            ctx.set_source_rgba(fill_val.r, fill_val.g, fill_val.b, fill_val.a)
            if self.stroke.get(time) is not None:
                ctx.fill_preserve()
            else:
                ctx.fill()
            ctx.restore()

        stroke_val = self.stroke.get(time)
        sw = self.stroke_width.get(time)
        if stroke_val is not None and sw > 0:
            ctx.save()
            ctx.set_source_rgba(stroke_val.r, stroke_val.g, stroke_val.b, stroke_val.a)
            ctx.set_line_width(sw)
            ctx.stroke()
            ctx.restore()


class RadialSliceHighlight(Node):
    """Glowing hover highlight outline around focused wedge."""

    def __init__(
        self,
        inner_radius: float = 50.0,
        outer_radius: float = 100.0,
        start_angle: float = 0.0,
        end_angle: float = math.pi / 2,
        color: Union[Color, str] = colors.CYAN,
        glow_width: float = 6.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.inner_radius = Signal(float(inner_radius), f"{self.name}.inner_radius")
        self.outer_radius = Signal(float(outer_radius), f"{self.name}.outer_radius")
        self.start_angle = Signal(float(start_angle), f"{self.name}.start_angle")
        self.end_angle = Signal(float(end_angle), f"{self.name}.end_angle")

        self.color = Signal(Color.from_any(color), f"{self.name}.color")
        self.glow_width = Signal(float(glow_width), f"{self.name}.glow_width")

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        # Maximum outer bounds is radius + 1.5 * glow_width since we draw up to glow_width * 3
        # and a stroke grows out equally from the center line.
        r = max(0.0, self.outer_radius.get(time)) + 1.5 * self.glow_width.get(time)
        return (-r, -r, 2.0 * r, 2.0 * r)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ir = max(0.0, self.inner_radius.get(time))
        cur_or = max(0.0, self.outer_radius.get(time))
        sa = self.start_angle.get(time)
        ea = self.end_angle.get(time)
        gw = self.glow_width.get(time)
        col = self.color.get(time)

        if gw <= 0 or cur_or <= ir or abs(ea - sa) < 1e-6:
            return

        ctx.save()
        ctx.new_path()
        ctx.arc(0, 0, cur_or, sa, ea)
        ctx.arc_negative(0, 0, ir, ea, sa)
        ctx.close_path()

        # Render layered stroke for glow effect
        for i in range(3, 0, -1):
            ctx.set_source_rgba(col.r, col.g, col.b, col.a * (0.3 / i))
            ctx.set_line_width(gw * i)
            ctx.stroke_preserve()

        ctx.set_source_rgba(col.r, col.g, col.b, col.a)
        ctx.set_line_width(2.0)
        ctx.stroke()
        ctx.restore()


class BreadcrumbPathTrail(Node):
    """Breadcrumb text trail displaying current drill-down path."""

    def __init__(
        self,
        path_items: List[str],
        font_size: float = 24.0,
        font_family: str = "Inter",
        color: Union[Color, str] = colors.SLATE_200,
        separator: str = " > ",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.path_items = path_items
        self.font_size = Signal(float(font_size), f"{self.name}.font_size")
        self.color = Signal(Color.from_any(color), f"{self.name}.color")
        self.separator = separator
        self.font_family = font_family

        self.progress = Signal(1.0, f"{self.name}.progress")  # For reveal animation

        self._text_node = Text(
            text=self.separator.join(self.path_items),
            font_size=font_size,
            font_family=font_family,
            color=color,
            align="left"
        )
        self.add(self._text_node)

        # Link internal text properties via expression bindings instead of mutating in draw()
        self._text_node.font_size.bind(lambda t: self.font_size.get(t))
        self._text_node.color.bind(
            lambda t: self.color.get(t).with_alpha(self.color.get(t).a * self.progress.get(t))
        )

    def update_path(self, new_path: List[str]) -> None:
        self.path_items = new_path
        self._text_node.text.set(self.separator.join(self.path_items))


class SunburstRadialHierarchy(Node):
    """Multi-tiered concentric ring chart showing nested parent-child hierarchical proportions."""

    def __init__(
        self,
        data: Dict[str, Any],  # Nested dict structure with 'value' and 'children'
        center_radius: float = 60.0,
        ring_width: float = 40.0,
        gap_angle: float = 0.02, # Radians gap between slices
        palette: Optional[List[Color]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.data = data
        self.center_radius = Signal(float(center_radius), f"{self.name}.center_radius")
        self.ring_width = Signal(float(ring_width), f"{self.name}.ring_width")
        self.gap_angle = Signal(float(gap_angle), f"{self.name}.gap_angle")

        self.palette = palette or [
            colors.CYAN_500, colors.INDIGO_500, colors.PURPLE_500,
            colors.ROSE_500, colors.ORANGE_500, colors.EMERALD_500
        ]

        self._arcs: List[ExpandingRingArc] = []
        self._build_arcs()

    def _calculate_total_value(self, node: Dict[str, Any]) -> float:
        if "children" in node and node["children"]:
            return sum(self._calculate_total_value(c) for c in node["children"])
        return float(node.get("value", 1.0))

    def _build_arcs(self) -> None:
        self.clear()
        self._arcs = []

        total_val = self._calculate_total_value(self.data)
        if total_val <= 0:
            return

        # Recursive layout builder
        def _layout_node(node: Dict[str, Any], depth: int, start_angle: float, end_angle: float) -> None:
            if depth > 0:
                # Assign color based on depth and position
                col = node.get("color")
                if not col:
                    col = self.palette[len(self._arcs) % len(self.palette)]
                else:
                    col = Color.from_any(col)

                arc = ExpandingRingArc(
                    inner_radius=self.center_radius.get() + (depth - 1) * self.ring_width.get(),
                    outer_radius=self.center_radius.get() + depth * self.ring_width.get(),
                    start_angle=start_angle,
                    end_angle=end_angle,
                    fill=col,
                    stroke=colors.SLATE_900,
                    stroke_width=2.0,
                    gap_angle=self.gap_angle.get(),
                )

                # Bind dynamic properties to the parent component
                arc.inner_radius.bind(lambda t, d=depth: self.center_radius.get(t) + (d - 1) * self.ring_width.get(t))
                arc.outer_radius.bind(lambda t, d=depth: self.center_radius.get(t) + d * self.ring_width.get(t))
                arc.gap_angle.bind(lambda t: self.gap_angle.get(t))

                self._arcs.append(arc)
                self.add(arc)

            children = node.get("children", [])
            if children:
                node_total = self._calculate_total_value(node)
                current_angle = start_angle
                angle_range = end_angle - start_angle

                for child in children:
                    child_val = self._calculate_total_value(child)
                    sweep = (child_val / node_total) * angle_range
                    _layout_node(child, depth + 1, current_angle, current_angle + sweep)
                    current_angle += sweep

        # Root layout uses full 360 degrees (0 to 2*pi)
        _layout_node(self.data, 0, 0.0, 2 * math.pi)
