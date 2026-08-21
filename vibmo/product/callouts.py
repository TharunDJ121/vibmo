"""
Spotlight, Callout, and Tooltip focus elements for highlighting features in product demo videos.
"""

from __future__ import annotations
import math
from typing import Any, Optional, Sequence, Tuple, Union
import cairo

from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D
from vibmo.core.signal import Signal
from vibmo.scene.node import Node
from vibmo.layout.container import FlexContainer
from vibmo.typography.kinetic import KineticText


class Spotlight(Node):
    """
    Dimming backdrop layer with an illuminated focal cutout over a target element.
    """

    def __init__(
        self,
        target: Optional[Node] = None,
        focal_point: Union[Vector2D, Sequence[float]] = (960.0, 540.0),
        radius: float = 220.0,
        dim_color: Optional[Union[Color, str]] = None,
        scene_width: float = 1920.0,
        scene_height: float = 1080.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.target = target
        self.focal_point = Signal(Vector2D.from_any(focal_point), f"{self.name}.focal_point")
        self.radius = Signal(float(radius), f"{self.name}.radius")
        self.dim_color = Color.from_any(dim_color) if dim_color else Color(0.02, 0.04, 0.08, 0.78)
        self.scene_width = scene_width
        self.scene_height = scene_height

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.scene_width, self.scene_height)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        op = max(0.0, min(1.0, float(self.opacity.get(time))))
        if op <= 0.001:
            return

        w = self.scene_width
        h = self.scene_height
        
        # Resolve center of spotlight
        if self.target is not None and hasattr(self.target, "world_bounds"):
            bx, by, bw, bh = self.target.world_bounds(time)
            fx = bx + bw * 0.5
            fy = by + bh * 0.5
        else:
            p = self.focal_point.get(time)
            fx, fy = p.x, p.y

        r = max(10.0, self.radius.get(time))

        ctx.save()

        # 1. Fullscreen dark mask with circular cutout (using Even-Odd winding rule)
        ctx.set_source_rgba(self.dim_color.r, self.dim_color.g, self.dim_color.b, self.dim_color.a * op)
        
        ctx.new_path()
        # Outer rectangle (clockwise)
        ctx.rectangle(0, 0, w, h)
        # Inner circle cutout (counter-clockwise)
        ctx.new_sub_path()
        ctx.arc_negative(fx, fy, r, 0, -math.pi * 2)
        ctx.close_path()
        
        ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
        ctx.fill()

        # 2. Glowing rim ring around spotlight hole
        ctx.set_source_rgba(0.39, 0.40, 0.95, 0.6 * op)  # Indigo glow ring
        ctx.set_line_width(2.5)
        ctx.arc(fx, fy, r, 0, math.pi * 2)
        ctx.stroke()

        ctx.restore()


class Callout(FlexContainer):
    """
    Floating feature callout badge with pointer beacon and animated text.
    """

    def __init__(
        self,
        title: str = "Feature Highlight",
        description: str = "Automated real-time anomaly detection",
        badge: str = "NEW",
        badge_color: Optional[Union[Color, str]] = None,
        position: Union[Vector2D, Sequence[float]] = (400.0, 300.0),
        **kwargs: Any,
    ) -> None:
        super().__init__(
            direction="column",
            gap=8.0,
            padding=20.0,
            corner_radius=16.0,
            fill=Color.hex("#0f172a").with_alpha(0.92),
            stroke=Color.hex("#6366f1").with_alpha(0.4),
            stroke_width=1.5,
            position=position,
            **kwargs,
        )
        self.title_text = title
        self.desc_text = description
        self.badge_text = badge
        self.resolved_badge_color = Color.from_any(badge_color) if badge_color else Color.hex("#6366f1")

        # Header Row
        header = FlexContainer(
            direction="row",
            gap=10.0,
            fill=Color.TRANSPARENT,
            stroke=Color.TRANSPARENT,
            padding=0.0,
        )
        
        # Mini Badge Tag
        tag = FlexContainer(
            direction="row",
            padding=4.0,
            corner_radius=6.0,
            fill=self.resolved_badge_color.with_alpha(0.2),
            stroke=self.resolved_badge_color,
            stroke_width=1.0,
        )
        tag.add(KineticText(self.badge_text, font_size=11.0, bold=True, color=self.resolved_badge_color))
        
        header.add(tag, KineticText(self.title_text, font_size=16.0, bold=True, color=colors.WHITE))
        
        # Description
        self.add(header, KineticText(self.desc_text, font_size=13.0, color=colors.SLATE_400))


    @property
    def title(self) -> str:
        return self.title_text

    @property
    def description(self) -> str:
        return self.desc_text


class Tooltip(FlexContainer):
    """Compact floating tooltip pill with icon and helper text."""

    def __init__(
        self,
        text: str = "Click to inspect",
        position: Union[Vector2D, Sequence[float]] = (0.0, 0.0),
        **kwargs: Any,
    ) -> None:
        super().__init__(
            direction="row",
            gap=8.0,
            padding=10.0,
            corner_radius=8.0,
            fill=Color.hex("#1e293b"),
            stroke=Color.hex("#334155"),
            stroke_width=1.0,
            position=position,
            **kwargs,
        )
        self.text = str(text)
        self.add(KineticText(text, font_size=12.0, color=colors.WHITE))
