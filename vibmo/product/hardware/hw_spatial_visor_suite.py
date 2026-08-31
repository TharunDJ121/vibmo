from __future__ import annotations
import math
from typing import Any, Optional, Tuple, Union

import cairo

from vibmo.scene.node import Node
from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal
from vibmo.layout.container import FlexContainer
from vibmo.spatial.shadows import DropShadow


class SpatialVisorFrame(Node):
    """
    Next-generation spatial computing glass visor with EyeSight lenticular shimmer,
    aluminum perimeter frame, orange knit headband straps, and nested screen viewport.
    """
    def __init__(
        self,
        width: float = 600.0,
        height: float = 300.0,
        eye_tracking_glow: bool = True,
        shadow: Optional[Union[DropShadow, bool]] = True,
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.width = Signal(float(width), f"{self.name}.width")
        self.height = Signal(float(height), f"{self.name}.height")
        self.eye_tracking_glow = eye_tracking_glow

        if shadow is True:
            self.shadow = DropShadow.elevated(blur=36.0, offset=(0, 18), color=Color.BLACK.with_alpha(0.50))
        elif isinstance(shadow, DropShadow):
            self.shadow = shadow
        else:
            self.shadow = None

        w = float(width)
        h = float(height)
        self.screen = FlexContainer(
            direction="column",
            gap=8.0,
            padding=16.0,
            width=w * 0.75,
            height=h * 0.65,
            position=(-w * 0.375, -h * 0.325),
            fill=Color.hex("#090d16").with_alpha(0.85),
            stroke=Color.TRANSPARENT,
            corner_radius=20.0,
        )
        self.add(self.screen)

    def add_screen(self, *nodes: Node) -> SpatialVisorFrame:
        """Add child nodes to the spatial screen viewport."""
        self.screen.add(*nodes)
        return self

    def add_screen_content(self, *nodes: Node) -> SpatialVisorFrame:
        """Alias for add_screen."""
        return self.add_screen(*nodes)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        w = self.width(time)
        h = self.height(time)
        return (-w / 2, -h / 2, w, h)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width(time)
        h = self.height(time)

        ctx.save()

        # Shadow (only when real surface is available)
        if self.shadow is not None and hasattr(ctx, "set_source_surface"):
            self.shadow.render_shadow(ctx, (-w / 2, -h / 2, w, h), 40.0)

        # 1. Aluminum Frame
        ctx.set_source_rgba(*colors.SLATE_200.to_tuple_rgba())
        ctx.set_line_width(8.0)

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

        # 4. EyeSight lenticular shimmer / eye tracking glow
        if self.eye_tracking_glow:
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


# Semantic alias
VisionProSpatialGlassVisor = SpatialVisorFrame


class QuestGoggleFrame(Node):
    """
    Lightweight VR headset goggle chassis with front-facing spatial tracking camera sensors.
    """
    def __init__(
        self,
        width: float = 400.0,
        height: float = 250.0,
        shadow: Optional[Union[DropShadow, bool]] = True,
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.width = Signal(float(width), f"{self.name}.width")
        self.height = Signal(float(height), f"{self.name}.height")

        if shadow is True:
            self.shadow = DropShadow.elevated(blur=28.0, offset=(0, 14), color=Color.BLACK.with_alpha(0.40))
        elif isinstance(shadow, DropShadow):
            self.shadow = shadow
        else:
            self.shadow = None

        w = float(width)
        h = float(height)
        self.screen = FlexContainer(
            direction="row",
            gap=8.0,
            padding=12.0,
            width=w * 0.70,
            height=h * 0.60,
            position=(-w * 0.35, -h * 0.30),
            fill=Color.hex("#0d0d14"),
            stroke=Color.TRANSPARENT,
            corner_radius=12.0,
        )
        self.add(self.screen)

    def add_screen(self, *nodes: Node) -> QuestGoggleFrame:
        self.screen.add(*nodes)
        return self

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        w = self.width(time)
        h = self.height(time)
        return (-w / 2, -h / 2, w, h)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width(time)
        h = self.height(time)

        ctx.save()

        if self.shadow is not None and hasattr(ctx, "set_source_surface"):
            self.shadow.render_shadow(ctx, (-w / 2, -h / 2, w, h), 30.0)

        # Main body
        ctx.set_source_rgba(0.9, 0.9, 0.9, 1.0)
        ctx.move_to(-w / 2 + 30, -h / 2)
        ctx.line_to(w / 2 - 30, -h / 2)
        ctx.arc(w / 2 - 30, -h / 2 + 30, 30, -math.pi / 2, 0)
        ctx.line_to(w / 2, h / 2 - 30)
        ctx.arc(w / 2 - 30, h / 2 - 30, 30, 0, math.pi / 2)
        ctx.line_to(-w / 2 + 30, h / 2)
        ctx.arc(-w / 2 + 30, h / 2 - 30, 30, math.pi / 2, math.pi)
        ctx.line_to(-w / 2, -h / 2 + 30)
        ctx.arc(-w / 2 + 30, -h / 2 + 30, 30, math.pi, 3 * math.pi / 2)
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
    """
    Curved cylindrical holographic HUD projection surface for spatial UI panes.
    """
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
        self.screen = self.content_container
        self.children.append(self.content_container)
        self.content_container.parent = self

    def add_screen_content(self, *nodes: Node) -> SpatialHudCurvedProjection:
        for node in nodes:
            self.content_container.children.append(node)
            node.parent = self.content_container
        return self

    def add_screen(self, *nodes: Node) -> SpatialHudCurvedProjection:
        return self.add_screen_content(*nodes)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        w = self.width(time)
        h = self.height(time)
        return (-w / 2, -h / 2, w, h)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width(time)
        h = self.height(time)
        depth = self.curve_depth(time)

        ctx.save()

        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.1)

        ctx.move_to(-w / 2, -h / 2)
        ctx.curve_to(-w / 4, -h / 2 - depth, w / 4, -h / 2 - depth, w / 2, -h / 2)
        ctx.line_to(w / 2, h / 2)
        ctx.curve_to(w / 4, h / 2 - depth, -w / 4, h / 2 - depth, -w / 2, h / 2)
        ctx.close_path()
        ctx.fill_preserve()

        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.3)
        ctx.set_line_width(2.0)
        ctx.stroke()

        ctx.restore()


class SpatialVisorSuite:
    """
    Suite factory for spatial computing visors, VR goggles, and curved HUD projections.
    """
    @staticmethod
    def visor(eye_tracking_glow: bool = True, **kwargs: Any) -> SpatialVisorFrame:
        return SpatialVisorFrame(eye_tracking_glow=eye_tracking_glow, **kwargs)

    @staticmethod
    def vision_visor(eye_tracking_glow: bool = True, **kwargs: Any) -> VisionProSpatialGlassVisor:
        return VisionProSpatialGlassVisor(eye_tracking_glow=eye_tracking_glow, **kwargs)

    @staticmethod
    def quest_goggles(**kwargs: Any) -> QuestGoggleFrame:
        return QuestGoggleFrame(**kwargs)

    @staticmethod
    def curved_projection(**kwargs: Any) -> SpatialHudCurvedProjection:
        return SpatialHudCurvedProjection(**kwargs)
