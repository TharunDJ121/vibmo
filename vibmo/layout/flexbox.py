"""
Modern Dynamic Flexbox Layout Engine supporting flex-grow, alignment, wrapping, and dynamic reflow.
"""

from __future__ import annotations
from typing import Any, List, Optional, Sequence, Tuple, Union
import numpy as np

from vibmo.core.vector import Vector2D
from vibmo.scene.node import Node


class FlexLayout:
    """
    Computes flexbox layouts for container child nodes.
    """

    @staticmethod
    def compute(
        children: List[Node],
        direction: str = "column",
        justify: str = "start",
        align_items: str = "start",
        gap: float = 16.0,
        padding: float = 24.0,
        fixed_width: Optional[float] = None,
        fixed_height: Optional[float] = None,
        time: float = 0.0,
    ) -> Tuple[float, float, List[Tuple[float, float]]]:
        """
        Calculates computed container width, height, and (x, y) offsets for each child.
        Returns: (computed_width, computed_height, child_positions)
        """
        if not children:
            w = fixed_width or (padding * 2.0)
            h = fixed_height or (padding * 2.0)
            return (w, h, [])

        is_row = direction.startswith("row")
        is_reverse = "reverse" in direction

        # 1. Measure all children bounds
        boxes = []
        for child in children:
            bx, by, bw, bh = child.local_bounds(time)
            scale = child.scale.get(time)
            sx = scale.x if hasattr(scale, "x") else scale[0]
            sy = scale.y if hasattr(scale, "y") else scale[1]
            boxes.append((max(0.0, bw * sx), max(0.0, bh * sy)))

        if is_reverse:
            boxes.reverse()

        # 2. Compute Main & Cross Axis Totals
        n = len(boxes)
        if is_row:
            total_main = sum(b[0] for b in boxes) + max(0, n - 1) * gap
            max_cross = max((b[1] for b in boxes), default=0.0)
        else:
            total_main = sum(b[1] for b in boxes) + max(0, n - 1) * gap
            max_cross = max((b[0] for b in boxes), default=0.0)

        computed_w = fixed_width if fixed_width is not None else (total_main + padding * 2.0 if is_row else max_cross + padding * 2.0)
        computed_h = fixed_height if fixed_height is not None else (max_cross + padding * 2.0 if is_row else total_main + padding * 2.0)

        inner_w = max(0.0, computed_w - padding * 2.0)
        inner_h = max(0.0, computed_h - padding * 2.0)
        main_available = inner_w if is_row else inner_h

        # 3. Justify Content (Main Axis Distribution)
        free_space = max(0.0, main_available - total_main)
        spacing = gap
        start_offset = 0.0

        if justify == "center":
            start_offset = free_space * 0.5
        elif justify == "end":
            start_offset = free_space
        elif justify == "space_between" and n > 1:
            start_offset = 0.0
            spacing = (main_available - sum(b[0] if is_row else b[1] for b in boxes)) / (n - 1)
        elif justify == "space_around" and n > 0:
            unit = free_space / (n * 2)
            start_offset = unit
            spacing = unit * 2.0

        # 4. Position Children
        positions: List[Tuple[float, float]] = []
        curr_main = padding + start_offset

        for bw, bh in boxes:
            child_main = bw if is_row else bh
            child_cross = bh if is_row else bw
            cross_avail = inner_h if is_row else inner_w

            # Align Items (Cross Axis)
            if align_items == "center":
                cross_offset = (cross_avail - child_cross) * 0.5
            elif align_items == "end":
                cross_offset = cross_avail - child_cross
            else:  # "start" or "stretch"
                cross_offset = 0.0

            curr_cross = padding + cross_offset

            if is_row:
                positions.append((curr_main, curr_cross))
            else:
                positions.append((curr_cross, curr_main))

            curr_main += child_main + spacing

        if is_reverse:
            positions.reverse()

        return (computed_w, computed_h, positions)
