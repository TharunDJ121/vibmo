"""
SaaS Data Tables, Kanban Boards, and Product Roadmap Timelines.
"""

from __future__ import annotations
import math
from typing import Any, List, Optional, Sequence, Tuple, Union
import cairo

from vibmo.core.vector import Vector2D
from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.scene.node import Node
from vibmo.layout.container import FlexContainer
from vibmo.components.glass import GlassCard
from vibmo.typography.kinetic import KineticText


class DataTable(Node):
    """
    Frosted Glass SaaS Data Grid with column headers, formatted cells, status tags, and staggered row reveal.
    """

    def __init__(
        self,
        headers: Sequence[str] = ("Name", "Role", "Status", "MRR"),
        rows: Sequence[Sequence[Any]] = (
            ("Alex Rivera", "Founder", "Active", "$12,400"),
            ("Sarah Chen", "Engineer", "Active", "$8,200"),
            ("Marcus Vance", "Design", "Review", "$5,100"),
            ("Elena Rostova", "Marketing", "Pending", "$3,800"),
        ),
        width: float = 680.0,
        row_height: float = 48.0,
        header_height: float = 42.0,
        corner_radius: float = 16.0,
        fill: Optional[Union[Color, str]] = None,
        stroke: Optional[Union[Color, str]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.headers = list(headers)
        self.raw_rows = [list(r) for r in rows]
        self.width_val = float(width)
        self.row_height = float(row_height)
        self.header_height = float(header_height)
        self.corner_radius = float(corner_radius)

        self.fill_color = Color.from_any(fill) if fill else Color.hex("#0d1527").with_alpha(0.85)
        self.stroke_color = Color.from_any(stroke) if stroke else Color.hex("#1e293b").with_alpha(0.8)

        # Signals for staggered row fade/slide in
        self.row_opacities = [Signal(1.0, f"{self.name}.row_op_{i}") for i in range(len(self.raw_rows))]
        self.row_offsets = [Signal(0.0, f"{self.name}.row_off_{i}") for i in range(len(self.raw_rows))]

    def reveal_rows(
        self,
        duration: float = 0.6,
        stagger: float = 0.08,
        ease: Optional[EasingFunc] = None,
        delay: float = 0.0,
    ) -> Any:
        """Staggers table rows sliding up into view."""
        from vibmo.timeline.scheduler import ParallelGroup
        e = ease or Ease.out_cubic
        actions = []
        for i in range(len(self.raw_rows)):
            self.row_opacities[i].set(0.0)
            self.row_offsets[i].set(20.0)
            t_del = delay + i * stagger
            actions.append(self.row_opacities[i].to(1.0, duration=duration, ease=Ease.out_quad, delay=t_del))
            actions.append(self.row_offsets[i].to(0.0, duration=duration, ease=e, delay=t_del))
        return ParallelGroup(actions)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        h = self.header_height + len(self.raw_rows) * self.row_height + 10.0
        return (0.0, 0.0, self.width_val, h)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width_val
        total_h = self.header_height + len(self.raw_rows) * self.row_height + 10.0
        r = self.corner_radius
        num_cols = max(1, len(self.headers))
        col_w = w / num_cols

        # 1. Glass Container Card
        ctx.save()
        ctx.new_sub_path()
        ctx.arc(w - r, r, r, -math.pi / 2, 0)
        ctx.arc(w - r, total_h - r, r, 0, math.pi / 2)
        ctx.arc(r, total_h - r, r, math.pi / 2, math.pi)
        ctx.arc(r, r, r, math.pi, 3 * math.pi / 2)
        ctx.close_path()

        ctx.set_source_rgba(self.fill_color.r, self.fill_color.g, self.fill_color.b, self.fill_color.a)
        ctx.fill_preserve()
        ctx.set_source_rgba(self.stroke_color.r, self.stroke_color.g, self.stroke_color.b, self.stroke_color.a)
        ctx.set_line_width(1.5)
        ctx.stroke()
        ctx.restore()

        # 2. Table Header
        ctx.save()
        ctx.set_source_rgba(0.55, 0.62, 0.75, 0.9)
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(12.0)
        for c_idx, h_text in enumerate(self.headers):
            ctx.move_to(20.0 + c_idx * col_w, 26.0)
            ctx.show_text(str(h_text).upper())

        # Header divider line
        ctx.set_source_rgba(0.2, 0.25, 0.35, 0.6)
        ctx.set_line_width(1.0)
        ctx.move_to(12.0, self.header_height)
        ctx.line_to(w - 12.0, self.header_height)
        ctx.stroke()
        ctx.restore()

        # 3. Table Rows
        ctx.save()
        for r_idx, row_vals in enumerate(self.raw_rows):
            op = max(0.0, min(1.0, float(self.row_opacities[r_idx].get(time))))
            off_y = float(self.row_offsets[r_idx].get(time))
            if op <= 0.01:
                continue

            y_top = self.header_height + r_idx * self.row_height + off_y
            y_baseline = y_top + self.row_height * 0.62

            # Zebra striping
            if r_idx % 2 == 1:
                ctx.set_source_rgba(1.0, 1.0, 1.0, 0.02 * op)
                ctx.rectangle(8.0, y_top + 2.0, w - 16.0, self.row_height - 4.0)
                ctx.fill()

            # Row cells
            for c_idx, cell_val in enumerate(row_vals):
                cell_str = str(cell_val)
                x_cell = 20.0 + c_idx * col_w

                if cell_str in ("Active", "LIVE", "Paid", "Done"):
                    # Status Badge Tag
                    ctx.set_source_rgba(0.1, 0.8, 0.5, 0.15 * op)
                    ctx.rectangle(x_cell, y_top + 10.0, 60.0, 22.0)
                    ctx.fill()
                    ctx.set_source_rgba(0.2, 0.9, 0.6, 0.95 * op)
                    ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
                    ctx.set_font_size(11.0)
                    ctx.move_to(x_cell + 10.0, y_top + 25.0)
                    ctx.show_text(cell_str)
                elif cell_str in ("Pending", "Review"):
                    ctx.set_source_rgba(0.9, 0.6, 0.1, 0.15 * op)
                    ctx.rectangle(x_cell, y_top + 10.0, 65.0, 22.0)
                    ctx.fill()
                    ctx.set_source_rgba(1.0, 0.75, 0.2, 0.95 * op)
                    ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
                    ctx.set_font_size(11.0)
                    ctx.move_to(x_cell + 8.0, y_top + 25.0)
                    ctx.show_text(cell_str)
                else:
                    ctx.set_source_rgba(0.9, 0.95, 1.0, 0.9 * op)
                    ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                    ctx.set_font_size(13.0)
                    ctx.move_to(x_cell, y_baseline)
                    ctx.show_text(cell_str)

        ctx.restore()


class TimelineView(Node):
    """
    Product Roadmap Timeline with animated milestone completion nodes and progress tracks.
    """

    def __init__(
        self,
        milestones: Sequence[Tuple[str, str, bool]] = (
            ("Q1", "AI Engine Core", True),
            ("Q2", "Cloud Rendering", True),
            ("Q3", "Web Studio Pro", True),
            ("Q4", "Global Enterprise", False),
        ),
        width: float = 640.0,
        height: float = 120.0,
        color: Optional[Union[Color, str]] = colors.CYAN,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.milestones = list(milestones)
        self.width_val = float(width)
        self.height_val = float(height)
        self.active_color = Color.from_any(color) if color else colors.CYAN

        self.track_progress = Signal(1.0, f"{self.name}.track_progress")

    def animate_progress(
        self,
        duration: float = 1.6,
        ease: Optional[EasingFunc] = None,
        delay: float = 0.0,
    ) -> AnimationAction:
        """Animates timeline progress line connecting milestones."""
        self.track_progress.set(0.0)
        return self.track_progress.to(1.0, duration=duration, ease=ease or Ease.out_expo, delay=delay)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        n = len(self.milestones)
        if n == 0:
            return

        w = self.width_val
        y_center = 50.0
        x_step = (w - 60.0) / max(1, n - 1)
        prog = max(0.0, min(1.0, float(self.track_progress.get(time))))

        # 1. Inactive Background Track
        ctx.save()
        ctx.set_source_rgba(0.2, 0.25, 0.35, 0.6)
        ctx.set_line_width(4.0)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.move_to(30.0, y_center)
        ctx.line_to(w - 30.0, y_center)
        ctx.stroke()

        # 2. Active Glowing Track
        c = self.active_color
        active_len = (w - 60.0) * prog
        if active_len > 1.0:
            ctx.set_source_rgba(c.r, c.g, c.b, 0.95)
            ctx.set_line_width(4.0)
            ctx.move_to(30.0, y_center)
            ctx.line_to(30.0 + active_len, y_center)
            ctx.stroke()

        # 3. Milestone Nodes
        for i, (tag, title, done) in enumerate(self.milestones):
            nx = 30.0 + i * x_step
            node_reached = (nx - 30.0) <= active_len

            # Node disc
            ctx.arc(nx, y_center, 9.0, 0, math.pi * 2)
            if node_reached and done:
                ctx.set_source_rgba(c.r, c.g, c.b, 1.0)
                ctx.fill_preserve()
                ctx.set_source_rgba(1.0, 1.0, 1.0, 0.8)
                ctx.set_line_width(2.0)
                ctx.stroke()
            else:
                ctx.set_source_rgba(0.1, 0.15, 0.25, 1.0)
                ctx.fill_preserve()
                ctx.set_source_rgba(0.3, 0.4, 0.5, 0.8)
                ctx.set_line_width(2.0)
                ctx.stroke()

            # Quarter / Tag label above
            ctx.set_source_rgba(c.r, c.g, c.b, 0.9 if node_reached else 0.5)
            ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(11.0)
            ext_tag = ctx.text_extents(tag)
            ctx.move_to(nx - ext_tag.width * 0.5, y_center - 18.0)
            ctx.show_text(tag)

            # Milestone title below
            ctx.set_source_rgba(1.0, 1.0, 1.0, 0.9 if node_reached else 0.4)
            ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            ctx.set_font_size(12.0)
            ext_title = ctx.text_extents(title)
            ctx.move_to(nx - ext_title.width * 0.5, y_center + 30.0)
            ctx.show_text(title)

        ctx.restore()
