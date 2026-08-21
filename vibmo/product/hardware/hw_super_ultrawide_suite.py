import math
from typing import Any, Optional, Sequence, Tuple, Union
import cairo

from vibmo.scene.node import Node
from vibmo.core.color import Color, colors
from vibmo.layout.container import FlexContainer
from vibmo.primitives.rect import Rect


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
        self.width_val = width
        self.height_val = height
        self.colors = [Color.from_any(c) if isinstance(c, (str, Color)) else Color.hex("#ff0055") for c in colors_rgb]

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        w = self.width_val
        h = self.height_val

        # Animated breathing glow effect
        intensity = 0.6 + 0.4 * math.sin(time * 2.0)

        # Simple radial gradient approximation for aura
        glow = cairo.RadialGradient(w/2, h/2, 0, w/2, h/2, max(w, h)/1.5)
        if len(self.colors) >= 2:
            c1, c2 = self.colors[0], self.colors[-1]
            # Mix colors in the center
            glow.add_color_stop_rgba(0.0, c1.r, c1.g, c1.b, 0.8 * intensity)
            glow.add_color_stop_rgba(0.5, c2.r, c2.g, c2.b, 0.4 * intensity)
            glow.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.0)
        else:
            c = self.colors[0] if self.colors else Color.WHITE
            glow.add_color_stop_rgba(0.0, c.r, c.g, c.b, 0.8 * intensity)
            glow.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.0)

        ctx.set_source(glow)
        # Expand drawing area to cover glow
        ctx.rectangle(-w * 0.5, -h * 0.5, w * 2, h * 2)
        ctx.fill()
        ctx.restore()


class Curved49InchUltrawide(Node):
    """
    32:9 aspect curved gaming/productivity monitor with subtle 1000R panoramic curvature and slim bezels.
    """
    def __init__(
        self,
        height: float = 360.0,
        bezel_color: Union[Color, str] = Color.hex("#111111"),
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        # 32:9 Aspect Ratio
        self.height_val = height
        self.width_val = height * (32.0 / 9.0)
        self.bezel_color = Color.from_any(bezel_color) if isinstance(bezel_color, (str, Color)) else Color.hex("#111111")

        # Curvature simulation offset
        self.curve_depth = self.height_val * 0.05
        self.corner_radius = 12.0

        # Screen content container
        self.screen = FlexContainer(
            width=self.width_val - 4.0, # Slight bezel inset
            height=self.height_val - 4.0 - self.curve_depth,
            direction="row",
            justify_content="center",
            align_items="center"
        )
        # Positioned relative to monitor center
        self.screen.position.set((2.0, 2.0 + self.curve_depth / 2))

        # 3-column split layout slots
        col_width = (self.screen.width() - 32) / 3 # Gap approximation
        self.col_1 = FlexContainer(width=col_width, height=self.screen.height(), direction="column", fill=None)
        self.col_2 = FlexContainer(width=col_width, height=self.screen.height(), direction="column", fill=None)
        self.col_3 = FlexContainer(width=col_width, height=self.screen.height(), direction="column", fill=None)

        # We don't add them automatically to allow arbitrary content,
        # but they are available if needed for the 3-column split layout slots requirement.

        self.add(self.screen)

    def add_screen_content(self, *nodes: Node) -> 'Curved49InchUltrawide':
        self.screen.add(*nodes)
        return self

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width_val
        h = self.height_val
        cd = self.curve_depth
        cr = self.corner_radius

        ctx.save()

        # Draw curved monitor body
        ctx.set_source_rgba(self.bezel_color.r, self.bezel_color.g, self.bezel_color.b, 1.0)

        ctx.new_path()
        # Top-left corner
        ctx.arc(cr, cr + cd, cr, math.pi, math.pi * 1.5)
        # Top curved edge
        ctx.curve_to(w * 0.33, cd * 0.5, w * 0.66, cd * 0.5, w - cr, cr + cd)
        # Top-right corner
        ctx.arc(w - cr, cr + cd, cr, -math.pi * 0.5, 0)
        # Right edge
        ctx.line_to(w, h - cr)
        # Bottom-right corner
        ctx.arc(w - cr, h - cr, cr, 0, math.pi * 0.5)
        # Bottom curved edge
        ctx.curve_to(w * 0.66, h - cd * 0.5, w * 0.33, h - cd * 0.5, cr, h - cr)
        # Bottom-left corner
        ctx.arc(cr, h - cr, cr, math.pi * 0.5, math.pi)
        ctx.close_path()

        ctx.fill_preserve()

        # Subtle specular highlight on top bezel
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.15)
        ctx.set_line_width(2.0)
        ctx.stroke()

        # Screen Masking to fit curvature (simplified as rect for child nodes but we mask slightly)
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
        ctx.paint()

        ctx.restore()

        # Note: the children (screen container) are drawn by the Node base class after this method
