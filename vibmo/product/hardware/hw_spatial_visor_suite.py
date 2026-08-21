"""
Spatial Computing & VR Visor mockup suite.
"""

from __future__ import annotations
import math
from typing import Any, List, Optional
import cairo

from vibmo.scene.node import Node
from vibmo.core.vector import Vector2D
from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal

class VisionProSpatialGlassVisor(Node):
    def __init__(
        self,
        width: float = 600.0,
        height: float = 300.0,
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.width = Signal(float(width), f"{self.name}.width")
        self.height = Signal(float(height), f"{self.name}.height")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width(time)
        h = self.height(time)

        ctx.save()

        # 1. Aluminum Frame
        ctx.set_source_rgba(*colors.SLATE_200.to_tuple_rgba())
        ctx.set_line_width(8.0)

        # Draw curved outline (simplified path)
        ctx.move_to(-w / 2, -h / 2 + 20)
        ctx.curve_to(0, -h / 2 - 20, 0, -h / 2 - 20, w / 2, -h / 2 + 20)
        ctx.line_to(w / 2, h / 2 - 20)
        ctx.curve_to(0, h / 2 + 20, 0, h / 2 + 20, -w / 2, h / 2 - 20)
        ctx.close_path()
        ctx.stroke_preserve()

        # 2. 3D Laminated Glass Visor (dark base)
        ctx.set_source_rgba(0.05, 0.05, 0.07, 0.95)
        ctx.fill()

        # 3. Headband Straps
        ctx.set_source_rgba(*colors.ORANGE.to_tuple_rgba())
        ctx.rectangle(-w / 2 - 40, -30, 40, 60)
        ctx.rectangle(w / 2, -30, 40, 60)
        ctx.fill()

        # 4. EyeSight lenticular shimmer
        shimmer_x = math.sin(time * 2.0) * (w / 4)
        ctx.set_source_rgba(0.4, 0.8, 1.0, 0.15)

        for i in range(-5, 6):
            ctx.arc(shimmer_x + i * 15, 0, 40, 0, 2 * math.pi)
            ctx.fill()

        # 5. Specular highlight
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.2)
        ctx.move_to(-w / 4, -h / 2 + 20)
        ctx.curve_to(0, -h / 4, 0, -h / 4, w / 4, -h / 2 + 20)
        ctx.fill()

        ctx.restore()


class QuestGoggleFrame(Node):
    def __init__(
        self,
        width: float = 400.0,
        height: float = 250.0,
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.width = Signal(float(width), f"{self.name}.width")
        self.height = Signal(float(height), f"{self.name}.height")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width(time)
        h = self.height(time)

        ctx.save()

        # Main body
        ctx.set_source_rgba(0.9, 0.9, 0.9, 1.0) # White/light gray plastic
        ctx.move_to(-w / 2 + 30, -h / 2)
        ctx.line_to(w / 2 - 30, -h / 2)
        ctx.arc(w / 2 - 30, -h / 2 + 30, 30, -math.pi/2, 0)
        ctx.line_to(w / 2, h / 2 - 30)
        ctx.arc(w / 2 - 30, h / 2 - 30, 30, 0, math.pi/2)
        ctx.line_to(-w / 2 + 30, h / 2)
        ctx.arc(-w / 2 + 30, h / 2 - 30, 30, math.pi/2, math.pi)
        ctx.line_to(-w / 2, -h / 2 + 30)
        ctx.arc(-w / 2 + 30, -h / 2 + 30, 30, math.pi, 3*math.pi/2)
        ctx.fill()

        # Front tracking camera sensors
        sensor_positions = [
            (-w / 2 + 40, -h / 2 + 40),
            (w / 2 - 40, -h / 2 + 40),
            (-w / 2 + 40, h / 2 - 40),
            (w / 2 - 40, h / 2 - 40),
        ]
        ctx.set_source_rgba(0.1, 0.1, 0.1, 1.0)
        for sx, sy in sensor_positions:
            ctx.arc(sx, sy, 10, 0, 2 * math.pi)
            ctx.fill()

        ctx.restore()


class SpatialHudCurvedProjection(Node):
    def __init__(
        self,
        width: float = 800.0,
        height: float = 500.0,
        curve_depth: float = 100.0,
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.width = Signal(float(width), f"{self.name}.width")
        self.height = Signal(float(height), f"{self.name}.height")
        self.curve_depth = Signal(float(curve_depth), f"{self.name}.curve_depth")
        self.content_container = Node(name=f"{self.name}_content")
        self.children.append(self.content_container)
        self.content_container.parent = self

    def add_screen_content(self, *nodes: Node) -> SpatialHudCurvedProjection:
        for node in nodes:
            self.content_container.children.append(node)
            node.parent = self.content_container
        return self

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width(time)
        h = self.height(time)
        depth = self.curve_depth(time)

        ctx.save()

        # Spatial depth blur simulation
        ctx.set_source_rgba(*colors.WHITE.to_tuple_rgba())

        # Draw cylindrical HUD projection plane (curved window)
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.1) # Translucent glass

        ctx.move_to(-w / 2, -h / 2)
        ctx.curve_to(-w / 4, -h / 2 - depth, w / 4, -h / 2 - depth, w / 2, -h / 2)
        ctx.line_to(w / 2, h / 2)
        ctx.curve_to(w / 4, h / 2 - depth, -w / 4, h / 2 - depth, -w / 2, h / 2)
        ctx.close_path()
        ctx.fill_preserve()

        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.3)
        ctx.set_line_width(2.0)
        ctx.stroke()

        # We don't draw children here manually, because Node class
        # rendering pipeline usually visits children automatically.
        # But for spatial mapping, we would theoretically deform children.
        # Here we just supply the base projection graphics.

        ctx.restore()
