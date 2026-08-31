"""
Intelligent Flexbox, Auto-Resizing, and Grid Layout Containers for UI and Infographics.
"""

from __future__ import annotations
import math
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
from vibmo.core.vector import Vector2D
from vibmo.core.color import Color, LinearGradient, RadialGradient, colors
from vibmo.core.signal import Signal
from vibmo.scene.node import Node
from vibmo.primitives.rect import Rect


class FlexContainer(Rect):
    """
    Auto-layout container arranging child nodes in rows or columns with padding and gap.
    Eliminates manual coordinate math for UI components, notification pills, and badges.
    """

    def __init__(
        self,
        direction: str = "row",  # "row" or "column"
        gap: float = 16.0,
        padding: Union[float, Sequence[float]] = 20.0,
        justify_content: str = "start",  # "start", "center", "end", "space_between"
        justify: Optional[str] = None,
        align_items: str = "center",  # "start", "center", "end", "stretch"
        align: Optional[str] = None,
        wrap: bool = False,
        align_content: str = "start",
        width: Optional[float] = None,
        height: Optional[float] = None,
        corner_radius: float = 16.0,
        fill: Optional[Union[Color, str]] = None,
        stroke: Optional[Union[Color, str]] = None,
        stroke_width: float = 1.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            width=width if width is not None else 0.0,
            height=height if height is not None else 0.0,
            corner_radius=corner_radius,
            fill=fill,
            stroke=stroke,
            stroke_width=stroke_width,
            **kwargs,
        )
        self.direction = direction.lower()
        self.gap = Signal(float(gap), f"{self.name}.gap")
        self.padding = padding
        self.justify_content = (justify or justify_content).lower().replace("-", "_")
        self.align_items = (align or align_items).lower().replace("-", "_")
        self.wrap = wrap
        self.align_content = align_content.lower().replace("-", "_")
        self._fixed_width = width is not None
        self._fixed_height = height is not None

    def _get_padding(self) -> Tuple[float, float, float, float]:
        """Returns (top, right, bottom, left) padding."""
        p = self.padding
        if isinstance(p, (int, float)):
            return (float(p), float(p), float(p), float(p))
        elif isinstance(p, (tuple, list)):
            if len(p) == 2:
                return (float(p[0]), float(p[1]), float(p[0]), float(p[1]))
            elif len(p) == 4:
                return (float(p[0]), float(p[1]), float(p[2]), float(p[3]))
        return (0.0, 0.0, 0.0, 0.0)

    def compute_layout(self, time: float = 0.0) -> Tuple[float, float]:
        """Arranges children and computes total intrinsic dimensions, supporting flex-wrap."""
        p_top, p_right, p_bottom, p_left = self._get_padding()
        gap_val = max(0.0, self.gap.get(time))

        child_boxes: List[Tuple[float, float, float, float]] = []
        for child in self.children:
            if not child.visible:
                child_boxes.append((0.0, 0.0, 0.0, 0.0))
                continue
            # If child is a flex container, compute its internal layout first
            if hasattr(child, "compute_layout"):
                child.compute_layout(time)
            bx, by, bw, bh = child.local_bounds(time)
            sc = child.scale.get(time)
            child_boxes.append((bx, by, bw * sc.x, bh * sc.y))

        visible_indices = [i for i, c in enumerate(self.children) if c.visible]
        is_row = self.direction == "row"
        time_width = self.width.get(time) if self._fixed_width else 0.0
        time_height = self.height.get(time) if self._fixed_height else 0.0

        max_main_avail = time_width - p_left - p_right if is_row else time_height - p_top - p_bottom

        lines = []
        current_line = []
        current_main_size = 0.0
        current_cross_size = 0.0

        for i in visible_indices:
            bx, by, bw, bh = child_boxes[i]
            c_main = bw if is_row else bh
            c_cross = bh if is_row else bw

            if self.wrap and max_main_avail > 0 and (self._fixed_width if is_row else self._fixed_height):
                if current_line and current_main_size + gap_val + c_main > max_main_avail:
                    lines.append((current_line, current_main_size, current_cross_size))
                    current_line = []
                    current_main_size = 0.0
                    current_cross_size = 0.0

            if current_line:
                current_main_size += gap_val
            current_main_size += c_main
            current_cross_size = max(current_cross_size, c_cross)
            current_line.append((i, bx, by, bw, bh))

        if current_line:
            lines.append((current_line, current_main_size, current_cross_size))

        total_cross = sum(line_cross for _, _, line_cross in lines) + max(0, len(lines) - 1) * gap_val
        max_main = max((line_main for _, line_main, _ in lines), default=0.0)

        content_w = max_main if is_row else total_cross
        content_h = total_cross if is_row else max_main

        total_w = time_width if self._fixed_width else (content_w + p_left + p_right)
        total_h = time_height if self._fixed_height else (content_h + p_top + p_bottom)

        inner_w = total_w - p_left - p_right
        inner_h = total_h - p_top - p_bottom
        cross_avail = inner_h if is_row else inner_w

        free_cross = max(0.0, cross_avail - total_cross)
        cross_start = 0.0
        cross_gap = gap_val

        if self.align_content == "center":
            cross_start = free_cross * 0.5
        elif self.align_content == "end":
            cross_start = free_cross
        elif self.align_content == "space_between" and len(lines) > 1:
            cross_gap = free_cross / (len(lines) - 1) + gap_val
        elif self.align_content == "space_around" and len(lines) > 0:
            unit = free_cross / (len(lines) * 2)
            cross_start = unit
            cross_gap = gap_val + unit * 2

        curr_cross = p_top if is_row else p_left
        curr_cross += cross_start

        for line_items, line_main, line_cross in lines:
            main_avail = inner_w if is_row else inner_h
            free_main = max(0.0, main_avail - line_main)
            main_start = 0.0
            main_gap = gap_val

            if self.justify_content == "center":
                main_start = free_main * 0.5
            elif self.justify_content == "end":
                main_start = free_main
            elif self.justify_content == "space_between" and len(line_items) > 1:
                main_gap = free_main / (len(line_items) - 1) + gap_val
            elif self.justify_content == "space_around" and len(line_items) > 0:
                unit = free_main / (len(line_items) * 2)
                main_start = unit
                main_gap = gap_val + unit * 2

            curr_main = (p_left if is_row else p_top) + main_start

            for i, bx, by, bw, bh in line_items:
                c_main = bw if is_row else bh
                c_cross = bh if is_row else bw

                item_cross_offset = 0.0
                if self.align_items == "center":
                    item_cross_offset = (line_cross - c_cross) * 0.5
                elif self.align_items == "end":
                    item_cross_offset = line_cross - c_cross

                child_x = curr_main if is_row else (curr_cross + item_cross_offset)
                child_y = (curr_cross + item_cross_offset) if is_row else curr_main

                self.children[i].position.set(Vector2D(child_x - bx, child_y - by))
                curr_main += c_main + main_gap

            curr_cross += line_cross + cross_gap

        if not self._fixed_width:
            self.width.set(total_w)
        if not self._fixed_height:
            self.height.set(total_h)

        return (total_w, total_h)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        self.compute_layout(time)
        super().draw(ctx, time)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        self.compute_layout(time)
        return super().local_bounds(time)


class AutoResizeBox(FlexContainer):
    """Container that dynamically morphs its bounding box to fit changing kinetic child nodes."""
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(width=None, height=None, **kwargs)


class GridContainer(Rect):
    """
    CSS-style Grid Layout arranging items into a fixed number of columns.
    """

    def __init__(
        self,
        columns: int = 2,
        gap: Union[float, Tuple[float, float]] = 16.0,
        padding: Union[float, Sequence[float]] = 20.0,
        width: float = 800.0,
        height: Optional[float] = None,
        corner_radius: float = 16.0,
        fill: Optional[Union[Color, str]] = None,
        stroke: Optional[Union[Color, str]] = None,
        stroke_width: float = 1.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            width=width,
            height=height if height is not None else 0.0,
            corner_radius=corner_radius,
            fill=fill,
            stroke=stroke,
            stroke_width=stroke_width,
            **kwargs,
        )
        self.columns = max(1, int(columns))
        self.gap_x = Signal(float(gap[0]) if isinstance(gap, tuple) else float(gap), f"{self.name}.gap_x")
        self.gap_y = Signal(float(gap[1]) if isinstance(gap, tuple) else float(gap), f"{self.name}.gap_y")
        self.padding = padding
        self._fixed_height = height is not None

    def _get_padding(self) -> Tuple[float, float, float, float]:
        p = self.padding
        if isinstance(p, (int, float)):
            return (float(p), float(p), float(p), float(p))
        elif isinstance(p, (tuple, list)):
            if len(p) == 2:
                return (float(p[0]), float(p[1]), float(p[0]), float(p[1]))
            elif len(p) == 4:
                return (float(p[0]), float(p[1]), float(p[2]), float(p[3]))
        return (0.0, 0.0, 0.0, 0.0)

    def compute_layout(self, time: float = 0.0) -> Tuple[float, float]:
        p_top, p_right, p_bottom, p_left = self._get_padding()
        gap_x = max(0.0, self.gap_x.get(time))
        gap_y = max(0.0, self.gap_y.get(time))

        child_boxes: List[Tuple[float, float, float, float]] = []
        for child in self.children:
            if not child.visible:
                child_boxes.append((0.0, 0.0, 0.0, 0.0))
                continue
            if hasattr(child, "compute_layout"):
                child.compute_layout(time)
            bx, by, bw, bh = child.local_bounds(time)
            sc = child.scale.get(time)
            child_boxes.append((bx, by, bw * sc.x, bh * sc.y))

        visible_indices = [i for i, c in enumerate(self.children) if c.visible]
        total_w = self.width.get(time)

        inner_w = max(0.0, total_w - p_left - p_right)
        col_w = max(0.0, (inner_w - (self.columns - 1) * gap_x) / self.columns)

        rows = []
        current_row_h = 0.0
        for idx, i in enumerate(visible_indices):
            _, _, _, bh = child_boxes[i]
            current_row_h = max(current_row_h, bh)
            
            if (idx + 1) % self.columns == 0 or idx == len(visible_indices) - 1:
                rows.append(current_row_h)
                current_row_h = 0.0

        total_h = self.height.get(time) if self._fixed_height else (p_top + p_bottom + sum(rows) + max(0, len(rows) - 1) * gap_y)

        curr_y = p_top
        for r_idx, r_h in enumerate(rows):
            curr_x = p_left
            for c in range(self.columns):
                idx = r_idx * self.columns + c
                if idx >= len(visible_indices):
                    break
                i = visible_indices[idx]
                bx, by, bw, bh = child_boxes[i]
                
                # Center within cell
                x = curr_x + (col_w - bw) * 0.5
                y = curr_y + (r_h - bh) * 0.5
                
                self.children[i].position.set(Vector2D(x - bx, y - by))
                curr_x += col_w + gap_x
                
            curr_y += r_h + gap_y

        if not self._fixed_height:
            self.height.set(total_h)

        return (total_w, total_h)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        self.compute_layout(time)
        super().draw(ctx, time)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        self.compute_layout(time)
        return super().local_bounds(time)
