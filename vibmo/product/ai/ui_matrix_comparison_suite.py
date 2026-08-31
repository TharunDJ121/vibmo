"""
Feature Comparison Matrix UI Suite for Vibmo / Motio.
Components:
- FeatureComparisonMatrix (InteractiveFeatureMatrix)
- CheckmarkCell
- CompetitorComparisonRow
- TooltipFeatureExplanation
- StickyHeaderColumn
"""

from __future__ import annotations
import math
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
import cairo

from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.scene.node import Node
from vibmo.spatial.shadows import DropShadow


class CheckmarkCell(Node):
    """Grid cell displaying checkmark (✓), cross (✕), or custom badge with pop animations."""

    def __init__(self, value: Union[bool, str] = True, is_highlight: bool = False, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.val = value
        self.is_highlight = is_highlight
        self.scale_sig = Signal(1.0, f"{self.name}.scale_sig")
        self.opacity = Signal(1.0, f"{self.name}.opacity")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        sc = self.scale_sig.get(time)
        op = max(0.0, min(1.0, self.opacity.get(time)))
        if op <= 0.0 or sc <= 0.0:
            return

        ctx.save()
        ctx.scale(sc, sc)

        if isinstance(self.val, bool):
            if self.val:
                ctx.set_source_rgba(0.1, 0.85, 0.45, 0.95 * op)
                ctx.arc(0, 0, 7.0, 0, 2 * math.pi)
                ctx.fill()

                ctx.set_source_rgba(1.0, 1.0, 1.0, op)
                ctx.set_line_width(1.5)
                ctx.move_to(-3.5, 0)
                ctx.line_to(-1.0, 2.5)
                ctx.line_to(3.5, -2.5)
                ctx.stroke()
            else:
                ctx.set_source_rgba(0.35, 0.4, 0.5, 0.5 * op)
                ctx.arc(0, 0, 6.0, 0, 2 * math.pi)
                ctx.fill()

                ctx.set_source_rgba(0.7, 0.75, 0.85, 0.7 * op)
                ctx.set_line_width(1.2)
                ctx.move_to(-2.5, -2.5)
                ctx.line_to(2.5, 2.5)
                ctx.move_to(2.5, -2.5)
                ctx.line_to(-2.5, 2.5)
                ctx.stroke()
        else:
            ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if self.is_highlight else cairo.FONT_WEIGHT_NORMAL)
            ctx.set_font_size(11.0)
            if self.is_highlight:
                ctx.set_source_rgba(0.2, 0.85, 1.0, 0.95 * op)
            else:
                ctx.set_source_rgba(0.7, 0.8, 0.9, 0.85 * op)
            text = str(self.val)
            ext = ctx.text_extents(text)
            ctx.move_to(-ext.width * 0.5, ext.height * 0.35)
            ctx.show_text(text)

        ctx.restore()


class CompetitorComparisonRow(Node):
    """Single row comparing one feature across multiple providers."""

    def __init__(
        self,
        feature_name: str = "Real-time Zero Latency Rendering",
        values: Optional[List[Union[bool, str]]] = None,
        is_striped: bool = False,
        width: float = 780.0,
        height: float = 40.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.feature_name = feature_name
        self.values = values or [True, False, False, True]
        self.is_striped = is_striped
        self.width_val = float(width)
        self.height_val = float(height)

        self.opacity = Signal(1.0, f"{self.name}.opacity")
        self.offset_y = Signal(0.0, f"{self.name}.offset_y")

        self.cells: List[CheckmarkCell] = []
        for i, val in enumerate(self.values):
            cell = CheckmarkCell(value=val, is_highlight=(i == 0))
            self.cells.append(cell)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        op = max(0.0, min(1.0, self.opacity.get(time)))
        off_y = self.offset_y.get(time)

        if op <= 0.0:
            return

        ctx.save()
        ctx.translate(0, off_y)

        # Background
        if self.is_striped:
            ctx.set_source_rgba(0.06, 0.09, 0.14, 0.5 * op)
            ctx.rectangle(0, 0, w, h)
            ctx.fill()

        # Feature Name
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(12.0)
        ctx.set_source_rgba(0.85, 0.9, 0.96, 0.95 * op)
        ctx.move_to(20.0, h * 0.5 + 4.0)
        ctx.show_text(self.feature_name)

        # Render cells for columns
        col_start = 280.0
        col_step = (w - col_start - 20.0) / len(self.values)

        for i, cell in enumerate(self.cells):
            cx = col_start + i * col_step + col_step * 0.5
            cy = h * 0.5
            ctx.save()
            ctx.translate(cx, cy)
            cell.opacity.set(op)
            cell.draw(ctx, time)
            ctx.restore()

        # Divider line
        ctx.set_source_rgba(0.18, 0.24, 0.35, 0.3 * op)
        ctx.set_line_width(1.0)
        ctx.move_to(10.0, h)
        ctx.line_to(w - 10.0, h)
        ctx.stroke()

        ctx.restore()


class TooltipFeatureExplanation(Node):
    """Interactive tooltip popover explaining technical nuances of a feature."""

    def __init__(self, text: str = "Hardware accelerated WebGL pipeline", width: float = 200.0, height: float = 32.0, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.text = text
        self.width_val = float(width)
        self.height_val = float(height)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        ctx.save()
        r = 6.0
        ctx.new_path()
        ctx.arc(w - r, r, r, -math.pi * 0.5, 0)
        ctx.arc(w - r, h - r, r, 0, math.pi * 0.5)
        ctx.arc(r, h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(r, r, r, math.pi, math.pi * 1.5)
        ctx.close_path()

        ctx.set_source_rgba(0.08, 0.12, 0.2, 0.95)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.3, 0.5, 0.8, 0.7)
        ctx.set_line_width(1.0)
        ctx.stroke()

        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(10.0)
        ctx.set_source_rgba(0.85, 0.92, 1.0, 0.95)
        ext = ctx.text_extents(self.text)
        ctx.move_to((w - ext.width) * 0.5, h * 0.5 + ext.height * 0.35)
        ctx.show_text(self.text)
        ctx.restore()


class StickyHeaderColumn(Node):
    """Header row of matrix showing provider names ('Vibmo / Motio', 'Competitor A', etc.)."""

    def __init__(self, headers: Optional[List[str]] = None, width: float = 780.0, height: float = 46.0, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.headers = headers or ["Features", "Vibmo (Ours)", "After Effects", "Remotion", "Framer Motion"]
        self.width_val = float(width)
        self.height_val = float(height)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        ctx.save()

        # Features header
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(12.5)
        ctx.set_source_rgba(0.6, 0.7, 0.8, 0.85)
        ctx.move_to(20.0, 28.0)
        ctx.show_text(self.headers[0])

        # Competitor columns
        col_start = 280.0
        col_step = (w - col_start - 20.0) / (len(self.headers) - 1)

        for i, hdr in enumerate(self.headers[1:]):
            cx = col_start + i * col_step + col_step * 0.5
            is_us = i == 0
            ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if is_us else cairo.FONT_WEIGHT_NORMAL)
            ctx.set_font_size(12.5 if is_us else 11.5)
            if is_us:
                ctx.set_source_rgba(0.2, 0.85, 1.0, 1.0)
            else:
                ctx.set_source_rgba(0.65, 0.72, 0.85, 0.8)
            ext = ctx.text_extents(hdr)
            ctx.move_to(cx - ext.width * 0.5, 28.0)
            ctx.show_text(hdr)

        # Divider
        ctx.set_source_rgba(0.2, 0.28, 0.4, 0.6)
        ctx.set_line_width(1.5)
        ctx.move_to(10.0, h)
        ctx.line_to(w - 10.0, h)
        ctx.stroke()

        ctx.restore()


class FeatureComparisonMatrix(Node):
    """
    Feature Comparison Matrix Suite.
    Renders structured comparison table with sticky headers, striped feature rows,
    checkmark indicators, and staggered row reveal animations.
    """

    def __init__(
        self,
        features: Optional[List[Dict[str, Any]]] = None,
        competitors: Optional[List[str]] = None,
        width: float = 840.0,
        height: float = 520.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.width_val = float(width)
        self.height_val = float(height)
        self.shadow = DropShadow(color=Color(0.0, 0.0, 0.0, 0.5), blur=32.0, offset=(0.0, 16.0))

        headers = ["Features", "Vibmo / Motio"] + (competitors or ["Competitor A", "Competitor B", "Competitor C"])
        self.header_row = StickyHeaderColumn(headers=headers, width=self.width_val - 48.0)
        self.header_row.position.set(Vector2D(24.0, 70.0))
        self.add(self.header_row)

        raw_features = features or [
            {"name": "Zero-Boilerplate Agent API", "values": [True, False, False, False]},
            {"name": "Hardware Accelerated Shaders", "values": [True, True, False, False]},
            {"name": "60 FPS 1080p Headless Export", "values": [True, False, True, False]},
            {"name": "Autonomous Storyboard Grid", "values": [True, False, False, False]},
            {"name": "Procedural Audio Synthesis", "values": [True, False, False, False]},
            {"name": "Spring Physics & Signal Reactivity", "values": [True, True, True, True]},
        ]

        self.rows: List[CompetitorComparisonRow] = []
        for i, f_data in enumerate(raw_features):
            row = CompetitorComparisonRow(
                feature_name=f_data.get("name", f"Feature {i+1}"),
                values=f_data.get("values", [True, False, False, False]),
                is_striped=(i % 2 == 1),
                width=self.width_val - 48.0,
                height=42.0,
            )
            row.position.set(Vector2D(24.0, 120.0 + i * 44.0))
            self.add(row)
            self.rows.append(row)

    def reveal_rows(self, duration: float = 1.5, stagger: float = 0.1, ease: EasingFunc = Ease.out_quad) -> List[AnimationAction]:
        """
        Fluent generator animation verb to sequentially reveal matrix feature rows.
        """
        actions: List[AnimationAction] = []
        step_dur = max(0.3, duration / max(1, len(self.rows)))
        for i, row in enumerate(self.rows):
            delay = i * stagger
            row.opacity.set(0.0)
            row.offset_y.set(20.0)
            actions.append(row.opacity.to(1.0, duration=step_dur, delay=delay, ease=ease))
            actions.append(row.offset_y.to(0.0, duration=step_dur, delay=delay, ease=Ease.out_back))
            for cell in row.cells:
                cell.scale_sig.set(0.4)
                actions.append(cell.scale_sig.to(1.0, duration=step_dur, delay=delay + 0.05, ease=Ease.out_back))
        return actions

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        ctx.save()

        # Canvas card
        r = 16.0
        ctx.new_path()
        ctx.arc(w - r, r, r, -math.pi * 0.5, 0)
        ctx.arc(w - r, h - r, r, 0, math.pi * 0.5)
        ctx.arc(r, h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(r, r, r, math.pi, math.pi * 1.5)
        ctx.close_path()

        ctx.set_source_rgba(0.04, 0.06, 0.1, 0.95)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.18, 0.25, 0.38, 0.8)
        ctx.set_line_width(1.5)
        ctx.stroke()

        # Header Title
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(15.0)
        ctx.set_source_rgba(0.95, 0.98, 1.0, 0.95)
        ctx.move_to(24.0, 42.0)
        ctx.show_text("Competitive Capability & Feature Matrix")

        super().draw(ctx, time)
        ctx.restore()


InteractiveFeatureMatrix = FeatureComparisonMatrix
