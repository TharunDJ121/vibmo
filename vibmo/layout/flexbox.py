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
        wrap: bool = False,
        align_content: str = "start",
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

        boxes = []
        for child in children:
            bx, by, bw, bh = child.local_bounds(time)
            scale = child.scale.get(time)
            sx = scale.x if hasattr(scale, "x") else scale[0]
            sy = scale.y if hasattr(scale, "y") else scale[1]
            boxes.append((max(0.0, bw * sx), max(0.0, bh * sy)))

        if is_reverse:
            boxes.reverse()

        time_width = fixed_width if fixed_width is not None else 0.0
        time_height = fixed_height if fixed_height is not None else 0.0
        max_main_avail = time_width - padding * 2.0 if is_row else time_height - padding * 2.0

        lines = []
        current_line = []
        current_main_size = 0.0
        current_cross_size = 0.0

        for i, (bw, bh) in enumerate(boxes):
            c_main = bw if is_row else bh
            c_cross = bh if is_row else bw

            if wrap and max_main_avail > 0 and (fixed_width if is_row else fixed_height):
                if current_line and current_main_size + gap + c_main > max_main_avail:
                    lines.append((current_line, current_main_size, current_cross_size))
                    current_line = []
                    current_main_size = 0.0
                    current_cross_size = 0.0

            if current_line:
                current_main_size += gap
            current_main_size += c_main
            current_cross_size = max(current_cross_size, c_cross)
            current_line.append((i, bw, bh))

        if current_line:
            lines.append((current_line, current_main_size, current_cross_size))

        total_cross = sum(line_cross for _, _, line_cross in lines) + max(0, len(lines) - 1) * gap
        max_main = max((line_main for _, line_main, _ in lines), default=0.0)

        content_w = max_main if is_row else total_cross
        content_h = total_cross if is_row else max_main

        total_w = time_width if fixed_width else (content_w + padding * 2.0)
        total_h = time_height if fixed_height else (content_h + padding * 2.0)

        inner_w = max(0.0, total_w - padding * 2.0)
        inner_h = max(0.0, total_h - padding * 2.0)
        cross_avail = inner_h if is_row else inner_w

        free_cross = max(0.0, cross_avail - total_cross)
        cross_start = 0.0
        cross_gap = gap

        if align_content == "center":
            cross_start = free_cross * 0.5
        elif align_content == "end":
            cross_start = free_cross
        elif align_content == "space_between" and len(lines) > 1:
            cross_gap = free_cross / (len(lines) - 1) + gap
        elif align_content == "space_around" and len(lines) > 0:
            unit = free_cross / (len(lines) * 2)
            cross_start = unit
            cross_gap = gap + unit * 2

        curr_cross = padding + cross_start

        positions: List[Tuple[float, float]] = [(0.0, 0.0)] * len(boxes)

        for line_items, line_main, line_cross in lines:
            main_avail = inner_w if is_row else inner_h
            free_main = max(0.0, main_avail - line_main)
            main_start = 0.0
            main_gap = gap

            if justify == "center":
                main_start = free_main * 0.5
            elif justify == "end":
                main_start = free_main
            elif justify == "space_between" and len(line_items) > 1:
                main_gap = free_main / (len(line_items) - 1) + gap
            elif justify == "space_around" and len(line_items) > 0:
                unit = free_main / (len(line_items) * 2)
                main_start = unit
                main_gap = gap + unit * 2

            curr_main = padding + main_start

            for i, bw, bh in line_items:
                c_main = bw if is_row else bh
                c_cross = bh if is_row else bw

                item_cross_offset = 0.0
                if align_items == "center":
                    item_cross_offset = (line_cross - c_cross) * 0.5
                elif align_items == "end":
                    item_cross_offset = line_cross - c_cross

                child_x = curr_main if is_row else (curr_cross + item_cross_offset)
                child_y = (curr_cross + item_cross_offset) if is_row else curr_main

                positions[i] = (child_x, child_y)
                curr_main += c_main + main_gap

            curr_cross += line_cross + cross_gap

        if is_reverse:
            positions.reverse()

        return (total_w, total_h, positions)
