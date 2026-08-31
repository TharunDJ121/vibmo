"""
DiagramNode & Vector Flowchart Generator for Vibmo / Motio.

Renders architecture diagrams, flowcharts, and sequence connection graphs
directly into PyCairo vector frames with animated arrow reveals and glowing node boxes.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Sequence
import cairo

from vibmo.core.color import Color, colors
from vibmo.scene.node import Node


@dataclass
class DiagramBox:
    id: str
    label: str
    subtext: str = ""
    x: float = 0.0
    y: float = 0.0
    width: float = 160.0
    height: float = 70.0
    color: Color = field(default_factory=lambda: colors.CYAN)
    bg_color: Color | None = None


@dataclass
class DiagramConnection:
    from_id: str
    to_id: str
    label: str = ""
    color: Color = field(default_factory=lambda: colors.CYAN)


class DiagramNode(Node):
    """Semantic vector flowchart and architecture diagram component."""

    def __init__(
        self,
        boxes: Sequence[DiagramBox | dict[str, Any]] | None = None,
        connections: Sequence[DiagramConnection | dict[str, Any]] | None = None,
        position: tuple[float, float] = (960, 540),
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.position.set(position)
        self.boxes: dict[str, DiagramBox] = {}
        self.connections: list[DiagramConnection] = []

        if boxes:
            for b in boxes:
                if isinstance(b, dict):
                    box = DiagramBox(
                        id=str(b.get("id", len(self.boxes))),
                        label=b.get("label", "Node"),
                        subtext=b.get("subtext", ""),
                        x=b.get("x", 0.0),
                        y=b.get("y", 0.0),
                        width=b.get("width", 160.0),
                        height=b.get("height", 70.0),
                        color=b.get("color", colors.CYAN),
                    )
                else:
                    box = b
                self.boxes[box.id] = box

        if connections:
            for c in connections:
                if isinstance(c, dict):
                    conn = DiagramConnection(
                        from_id=str(c.get("from", c.get("from_id", ""))),
                        to_id=str(c.get("to", c.get("to_id", ""))),
                        label=c.get("label", ""),
                        color=c.get("color", colors.CYAN),
                    )
                else:
                    conn = c
                self.connections.append(conn)

    def add_box(
        self,
        id: str,
        label: str,
        subtext: str = "",
        x: float = 0.0,
        y: float = 0.0,
        width: float = 180.0,
        height: float = 70.0,
        color: Color = colors.CYAN,
    ) -> DiagramNode:
        self.boxes[id] = DiagramBox(id=id, label=label, subtext=subtext, x=x, y=y, width=width, height=height, color=color)
        return self


    def connect(self, from_id: str, to_id: str, label: str = "", color: Color = colors.CYAN) -> DiagramNode:
        self.connections.append(DiagramConnection(from_id=from_id, to_id=to_id, label=label, color=color))
        return self

    def draw(self, ctx: cairo.Context, t: float = 0.0) -> None:
        self._render_self(ctx, t)

    def _render_self(self, ctx: cairo.Context, t: float) -> None:

        ctx.save()

        # Draw Connections First
        for conn in self.connections:
            if conn.from_id not in self.boxes or conn.to_id not in self.boxes:
                continue
            b1 = self.boxes[conn.from_id]
            b2 = self.boxes[conn.to_id]

            # Start and End points (centers)
            x1, y1 = b1.x, b1.y
            x2, y2 = b2.x, b2.y

            # Connect line
            ctx.set_source_rgba(conn.color.r, conn.color.g, conn.color.b, 0.7)
            ctx.set_line_width(2.0)
            ctx.move_to(x1, y1)
            ctx.line_to(x2, y2)
            ctx.stroke()

            # Arrow head at end
            angle = math.atan2(y2 - y1, x2 - x1)
            arrow_len = 12.0
            # Offset from target center by half width
            tx = x2 - math.cos(angle) * (b2.width / 2)
            ty = y2 - math.sin(angle) * (b2.height / 2)

            ctx.new_path()
            ctx.move_to(tx, ty)
            ctx.line_to(tx - arrow_len * math.cos(angle - 0.4), ty - arrow_len * math.sin(angle - 0.4))
            ctx.line_to(tx - arrow_len * math.cos(angle + 0.4), ty - arrow_len * math.sin(angle + 0.4))
            ctx.close_path()
            ctx.set_source_rgba(*conn.color.to_rgba())
            ctx.fill()

        # Draw Boxes
        for box in self.boxes.values():
            bx = box.x - box.width / 2
            by = box.y - box.height / 2
            bw = box.width
            bh = box.height
            r = 10.0

            # Box Shadow
            ctx.save()
            ctx.set_source_rgba(0.0, 0.0, 0.0, 0.4)
            self._rounded_rect(ctx, bx + 2, by + 6, bw, bh, r)
            ctx.fill()
            ctx.restore()

            # Box Fill
            self._rounded_rect(ctx, bx, by, bw, bh, r)
            ctx.set_source_rgba(0.08, 0.10, 0.15, 0.95)
            ctx.fill_preserve()
            # Border
            ctx.set_source_rgba(*box.color.to_rgba())
            ctx.set_line_width(1.8)
            ctx.stroke()

            # Label Text
            ctx.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(15)
            ctx.set_source_rgba(0.95, 0.97, 1.0, 1.0)
            ext = ctx.text_extents(box.label)
            ctx.move_to(box.x - ext.width / 2, box.y - (4 if box.subtext else -5))
            ctx.show_text(box.label)

            # Subtext
            if box.subtext:
                ctx.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                ctx.set_font_size(11)
                ctx.set_source_rgba(0.65, 0.70, 0.80, 0.85)
                sub_ext = ctx.text_extents(box.subtext)
                ctx.move_to(box.x - sub_ext.width / 2, box.y + 14)
                ctx.show_text(box.subtext)

        ctx.restore()

    def _rounded_rect(self, ctx: cairo.Context, x: float, y: float, w: float, h: float, r: float) -> None:
        ctx.new_path()
        ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
        ctx.arc(x + w - r, y + r, r, 1.5 * math.pi, 2 * math.pi)
        ctx.arc(x + w - r, y + h - r, r, 0, 0.5 * math.pi)
        ctx.arc(x + r, y + h - r, r, 0.5 * math.pi, math.pi)
        ctx.close_path()
