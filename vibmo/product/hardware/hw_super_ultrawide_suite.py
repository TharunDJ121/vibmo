from __future__ import annotations
import math
from typing import Any, Optional, Sequence, Tuple, Union

import cairo

from vibmo.scene.node import Node
from vibmo.core.color import Color
from vibmo.layout.container import FlexContainer
from vibmo.spatial.shadows import DropShadow


class MonitorArmPivotingBase(Node):
    """
    Heavy-duty gas-spring desk clamp monitor arm.
    """
    def __init__(self, color: Union[Color, str] = Color.hex("#2c2c2c"), **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.arm_color = Color.from_any(color) if isinstance(color, (str, Color)) else Color.hex("#2c2c2c")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        # Draw base clamp
        ctx.set_source_rgba(self.arm_color.r, self.arm_color.g, self.arm_color.b, 1.0)
        ctx.rectangle(-40, 0, 80, 20)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.1, 0.1, 0.1, 1.0)
        ctx.set_line_width(2.0)
        ctx.stroke()

        # Draw arm pole
        ctx.set_source_rgba(self.arm_color.r * 1.1, self.arm_color.g * 1.1, self.arm_color.b * 1.1, 1.0)
        ctx.rectangle(-15, -150, 30, 150)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.1, 0.1, 0.1, 1.0)
        ctx.stroke()

        # Draw pivot joint
        ctx.arc(0, -150, 25, 0, 2 * math.pi)
        ctx.set_source_rgba(self.arm_color.r * 0.8, self.arm_color.g * 0.8, self.arm_color.b * 0.8, 1.0)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.1, 0.1, 0.1, 1.0)
        ctx.stroke()
        ctx.restore()


class GamerBackGlowRgbLed(Node):
    """
    Rear ambient RGB bias lighting aura projecting against the back wall.
    """
    def __init__(
        self,
        width: float = 1200.0,
        height: float = 300.0,
        colors_rgb: Sequence[Union[Color, str]] = (Color.hex("#ff0055"), Color.hex("#0055ff")),
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.width_val = float(width)
        self.height_val = float(height)
        self.colors = [Color.from_any(c) if isinstance(c, (str, Color)) else Color.hex("#ff0055") for c in colors_rgb]

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        w = self.width_val
        h = self.height_val

        intensity = 0.6 + 0.4 * math.sin(time * 2.0)

        if hasattr(cairo, "RadialGradient") and hasattr(ctx, "set_source"):
            try:
                glow = cairo.RadialGradient(w / 2, h / 2, 0, w / 2, h / 2, max(w, h) / 1.5)
                if len(self.colors) >= 2:
                    c1, c2 = self.colors[0], self.colors[-1]
                    glow.add_color_stop_rgba(0.0, c1.r, c1.g, c1.b, 0.8 * intensity)
                    glow.add_color_stop_rgba(0.5, c2.r, c2.g, c2.b, 0.4 * intensity)
                    glow.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.0)
                else:
                    c = self.colors[0] if self.colors else Color.WHITE
                    glow.add_color_stop_rgba(0.0, c.r, c.g, c.b, 0.8 * intensity)
                    glow.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.0)

                ctx.set_source(glow)
            except Exception:
                ctx.set_source_rgba(0.2, 0.4, 1.0, 0.3)
        else:
            ctx.set_source_rgba(0.2, 0.4, 1.0, 0.3)

        ctx.rectangle(-w * 0.5, -h * 0.5, w * 2, h * 2)
        ctx.fill()
        ctx.restore()


class SuperUltrawideMonitorFrame(Node):
    """
    32:9 aspect curved gaming/productivity monitor with subtle 1000R panoramic curvature,
    slim bezels, and auto-clipped screen viewport.
    """
    def __init__(
        self,
        width: Optional[float] = None,
        height: Optional[float] = None,
        curve_depth: Optional[float] = None,
        bezel_color: Optional[Union[Color, str]] = None,
        shadow: Optional[Union[DropShadow, bool]] = True,
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)

        if width is not None and height is not None:
            self.width_val = float(width)
            self.height_val = float(height)
        elif width is not None:
            self.width_val = float(width)
            self.height_val = self.width_val * (9.0 / 32.0)
        elif height is not None:
            self.height_val = float(height)
            self.width_val = self.height_val * (32.0 / 9.0)
        else:
            self.width_val = 1280.0
            self.height_val = 360.0

        self.bezel_color = Color.from_any(bezel_color) if bezel_color else Color.hex("#111111")
        self.curve_depth = float(curve_depth) if curve_depth is not None else self.height_val * 0.12
        self.corner_radius = 12.0

        if shadow is True:
            self.shadow = DropShadow.elevated(blur=40.0, offset=(0, 20), color=Color.BLACK.with_alpha(0.50))
        elif isinstance(shadow, DropShadow):
            self.shadow = shadow
        else:
            self.shadow = None

        self.screen = FlexContainer(
            width=self.width_val - 8.0,
            height=self.height_val - 8.0 - self.curve_depth,
            direction="row",
            justify_content="center",
            align_items="center",
            fill=Color.hex("#080808"),
            stroke=Color.TRANSPARENT,
            corner_radius=8.0,
        )
        self.screen.position.set((4.0, 4.0 + self.curve_depth / 2))

        col_width = (self.screen.width() - 32) / 3
        self.col_1 = FlexContainer(width=col_width, height=self.screen.height(), direction="column", fill=None)
        self.col_2 = FlexContainer(width=col_width, height=self.screen.height(), direction="column", fill=None)
        self.col_3 = FlexContainer(width=col_width, height=self.screen.height(), direction="column", fill=None)

        self.add(self.screen)

    def add_screen(self, *nodes: Node) -> SuperUltrawideMonitorFrame:
        """Add child nodes to the 32:9 screen container."""
        self.screen.add(*nodes)
        return self

    def add_screen_content(self, *nodes: Node) -> SuperUltrawideMonitorFrame:
        """Alias for add_screen."""
        return self.add_screen(*nodes)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width_val
        h = self.height_val
        cd = self.curve_depth
        cr = self.corner_radius

        ctx.save()

        # Shadow (only when real surface is available)
        if self.shadow is not None and hasattr(ctx, "set_source_surface"):
            self.shadow.render_shadow(ctx, (0, 0, w, h), cr)

        # Draw curved monitor body
        ctx.set_source_rgba(self.bezel_color.r, self.bezel_color.g, self.bezel_color.b, self.bezel_color.a)

        ctx.new_path()
        ctx.arc(cr, cr + cd, cr, math.pi, math.pi * 1.5)
        ctx.curve_to(w * 0.33, cd * 0.5, w * 0.66, cd * 0.5, w - cr, cr + cd)
        ctx.arc(w - cr, cr + cd, cr, -math.pi * 0.5, 0)
        ctx.line_to(w, h - cr)
        ctx.arc(w - cr, h - cr, cr, 0, math.pi * 0.5)
        ctx.curve_to(w * 0.66, h - cd * 0.5, w * 0.33, h - cd * 0.5, cr, h - cr)
        ctx.arc(cr, h - cr, cr, math.pi * 0.5, math.pi)
        ctx.close_path()

        ctx.fill_preserve()

        # Subtle specular highlight on top bezel
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.15)
        ctx.set_line_width(2.0)
        ctx.stroke()

        # Screen Masking to fit curvature
        ctx.new_path()
        inset = 2.0
        ctx.arc(cr + inset, cr + cd + inset, cr, math.pi, math.pi * 1.5)
        ctx.curve_to(w * 0.33, cd * 0.5 + inset, w * 0.66, cd * 0.5 + inset, w - cr - inset, cr + cd + inset)
        ctx.arc(w - cr - inset, cr + cd + inset, cr, -math.pi * 0.5, 0)
        ctx.line_to(w - inset, h - cr - inset)
        ctx.arc(w - cr - inset, h - cr - inset, cr, 0, math.pi * 0.5)
        ctx.curve_to(w * 0.66, h - cd * 0.5 - inset, w * 0.33, h - cd * 0.5 - inset, cr + inset, h - cr - inset)
        ctx.arc(cr + inset, h - cr - inset, cr, math.pi * 0.5, math.pi)
        ctx.close_path()
        ctx.clip()

        # Draw dark screen background
        ctx.set_source_rgba(0.05, 0.05, 0.05, 1.0)
        if hasattr(ctx, "paint"):
            ctx.paint()
        else:
            ctx.rectangle(0, 0, w, h)
            ctx.fill()

        ctx.restore()


# Semantic alias
Curved49InchUltrawide = SuperUltrawideMonitorFrame


class SuperUltrawideSuite:
    """
    Suite factory for ultrawide 32:9 monitors, monitor arms, and ambient back glow.
    """
    @staticmethod
    def monitor(width: float = 1600.0, curve_depth: float = 45.0, **kwargs: Any) -> SuperUltrawideMonitorFrame:
        return SuperUltrawideMonitorFrame(width=width, curve_depth=curve_depth, **kwargs)

    @staticmethod
    def monitor_arm(**kwargs: Any) -> MonitorArmPivotingBase:
        return MonitorArmPivotingBase(**kwargs)

    @staticmethod
    def rgb_glow(width: float = 1200.0, height: float = 300.0, **kwargs: Any) -> GamerBackGlowRgbLed:
        return GamerBackGlowRgbLed(width=width, height=height, **kwargs)
