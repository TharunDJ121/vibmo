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
        align_items: str = "center",  # "start", "center", "end", "stretch"
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
        self.justify_content = justify_content.lower()
        self.align_items = align_items.lower()
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
        """Arranges children and computes total intrinsic dimensions."""
        p_top, p_right, p_bottom, p_left = self._get_padding()
        gap_val = max(0.0, self.gap.get(time))

        child_boxes: List[Tuple[float, float, float, float]] = []
        for child in self.children:
            if not child.visible:
                child_boxes.append((0.0, 0.0, 0.0, 0.0))
                continue
            # If child is a flex container, compute its internal layout first
            if isinstance(child, FlexContainer):
                child.compute_layout(time)
            bx, by, bw, bh = child.local_bounds(time)
            # Apply child scale
            sc = child.scale.get(time)
            bw *= sc.x
            bh *= sc.y
            child_boxes.append((bx, by, bw, bh))

        visible_indices = [i for i, c in enumerate(self.children) if c.visible]

        if self.direction == "row":
            total_children_w = sum(child_boxes[i][2] for i in visible_indices)
            total_gaps = gap_val * max(0, len(visible_indices) - 1)
            content_w = total_children_w + total_gaps
            max_h = max((child_boxes[i][3] for i in visible_indices), default=0.0)

            total_w = self.width.get(time) if self._fixed_width else (content_w + p_left + p_right)
            total_h = self.height.get(time) if self._fixed_height else (max_h + p_top + p_bottom)

            curr_x = p_left
            step_gap = gap_val
            if self.justify_content == "center" and self._fixed_width:
                curr_x = p_left + (total_w - p_left - p_right - content_w) * 0.5
            elif self.justify_content == "end" and self._fixed_width:
                curr_x = total_w - p_right - content_w
            elif self.justify_content == "space_between" and self._fixed_width and len(visible_indices) > 1:
                curr_x = p_left
                step_gap = ((total_w - p_left - p_right) - total_children_w) / (len(visible_indices) - 1)

            for i in visible_indices:
                child = self.children[i]
                bx, by, bw, bh = child_boxes[i]

                # Align cross axis (Y)
                if self.align_items == "center":
                    child_y = p_top + ((total_h - p_top - p_bottom) - bh) * 0.5
                elif self.align_items == "end":
                    child_y = total_h - p_bottom - bh
                else:  # start
                    child_y = p_top

                child.position.set(Vector2D(curr_x - bx, child_y - by))
                curr_x += bw + step_gap

        else:  # "column"
            total_children_h = sum(child_boxes[i][3] for i in visible_indices)
            total_gaps = gap_val * max(0, len(visible_indices) - 1)
            content_h = total_children_h + total_gaps
            max_w = max((child_boxes[i][2] for i in visible_indices), default=0.0)

            total_w = self.width.get(time) if self._fixed_width else (max_w + p_left + p_right)
            total_h = self.height.get(time) if self._fixed_height else (content_h + p_top + p_bottom)

            curr_y = p_top
            step_gap = gap_val
            if self.justify_content == "center" and self._fixed_height:
                curr_y = p_top + (total_h - p_top - p_bottom - content_h) * 0.5
            elif self.justify_content == "end" and self._fixed_height:
                curr_y = total_h - p_bottom - content_h
            elif self.justify_content == "space_between" and self._fixed_height and len(visible_indices) > 1:
                curr_y = p_top
                step_gap = ((total_h - p_top - p_bottom) - total_children_h) / (len(visible_indices) - 1)

            for i in visible_indices:
                child = self.children[i]
                bx, by, bw, bh = child_boxes[i]

                # Align cross axis (X)
                if self.align_items == "center":
                    child_x = p_left + ((total_w - p_left - p_right) - bw) * 0.5
                elif self.align_items == "end":
                    child_x = total_w - p_right - bw
                else:  # start
                    child_x = p_left

                child.position.set(Vector2D(child_x - bx, curr_y - by))
                curr_y += bh + step_gap

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
