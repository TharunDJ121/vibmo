from __future__ import annotations
import math
from typing import Any, Optional, Tuple, Union

import cairo

from vibmo.core.color import Color
from vibmo.scene.node import Node
from vibmo.spatial.shadows import DropShadow


def rounded_rect(ctx: Any, x: float, y: float, width: float, height: float, r: float) -> None:
    r = min(r, width * 0.5, height * 0.5)
    if r <= 0:
        ctx.rectangle(x, y, width, height)
        return
    ctx.new_path()
    ctx.move_to(x + r, y)
    ctx.line_to(x + width - r, y)
    ctx.arc(x + width - r, y + r, r, -math.pi / 2, 0)
    ctx.line_to(x + width, y + height - r)
    ctx.arc(x + width - r, y + height - r, r, 0, math.pi / 2)
    ctx.line_to(x + r, y + height)
    ctx.arc(x + r, y + height - r, r, math.pi / 2, math.pi)
    ctx.line_to(x, y + r)
    ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    ctx.close_path()


class BaseWatch(Node):
    """Base watch node providing screen container and unified .add_screen() API."""
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.screen = Node(name=f"{self.name}_screen")
        self.add(self.screen)

    def add_screen(self, *nodes: Node) -> BaseWatch:
        """Add child nodes to the watch screen viewport."""
        self.screen.add(*nodes)
        return self

    def add_screen_content(self, *nodes: Node) -> BaseWatch:
        """Alias for add_screen."""
        return self.add_screen(*nodes)


class RuggedSmartwatchFrame(BaseWatch):
    """
    Titanium rugged smartwatch with ocean band, raised protective bezel,
    orange action button, digital crown with ridges, and clipped screen viewport.
    """
    def __init__(
        self,
        width: float = 300.0,
        height: float = 380.0,
        corner_radius: float = 40.0,
        bezel_padding: float = 20.0,
        shadow: Optional[Union[DropShadow, bool]] = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.width = float(width)
        self.height = float(height)
        self.cr = float(corner_radius)
        self.bezel_padding = float(bezel_padding)
        self.screen_width = self.width - 2 * self.bezel_padding
        self.screen_height = self.height - 2 * self.bezel_padding
        self.screen_cr = max(0.0, self.cr - self.bezel_padding)

        if shadow is True:
            self.shadow = DropShadow.elevated(blur=28.0, offset=(0, 14), color=Color.BLACK.with_alpha(0.45))
        elif isinstance(shadow, DropShadow):
            self.shadow = shadow
        else:
            self.shadow = None

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width, self.height)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        # Band (Ribbed Ocean Band)
        ctx.save()
        band_width = self.width * 0.8
        band_x = (self.width - band_width) / 2
        ctx.set_source_rgba(0.2, 0.2, 0.22, 1.0)
        # Top band
        rounded_rect(ctx, band_x, -100, band_width, 150, 10)
        ctx.fill()
        # Bottom band
        rounded_rect(ctx, band_x, self.height - 50, band_width, 150, 10)
        ctx.fill()

        # Ribs
        ctx.set_source_rgba(0.15, 0.15, 0.17, 1.0)
        ctx.set_line_width(4)
        for i in range(5):
            ctx.move_to(band_x, -90 + i * 15)
            ctx.line_to(band_x + band_width, -90 + i * 15)
            ctx.stroke()
        for i in range(5):
            ctx.move_to(band_x, self.height + 40 + i * 15)
            ctx.line_to(band_x + band_width, self.height + 40 + i * 15)
            ctx.stroke()
        ctx.restore()

        # Shadow (only when real surface is available)
        if self.shadow is not None and hasattr(ctx, "set_source_surface"):
            self.shadow.render_shadow(ctx, (0, 0, self.width, self.height), self.cr)

        # Action Button (Orange)
        ctx.save()
        button_w, button_h = 10.0, 60.0
        rounded_rect(ctx, -button_w, self.height / 2 - button_h / 2, button_w + 5, button_h, 4)
        ctx.set_source_rgba(1.0, 0.4, 0.0, 1.0)
        ctx.fill()
        ctx.restore()

        # Digital Crown
        ctx.save()
        crown_w, crown_h = 18.0, 50.0
        rounded_rect(ctx, self.width - 5, self.height / 3 - crown_h / 2, crown_w, crown_h, 6)
        ctx.set_source_rgba(0.8, 0.8, 0.8, 1.0)
        ctx.fill()
        # Crown ridges
        ctx.set_source_rgba(0.6, 0.6, 0.6, 1.0)
        ctx.set_line_width(2)
        for i in range(8):
            y = self.height / 3 - crown_h / 2 + 5 + i * 5
            ctx.move_to(self.width - 5, y)
            ctx.line_to(self.width - 5 + crown_w, y)
            ctx.stroke()
        ctx.restore()

        # Titanium Case
        ctx.save()
        rounded_rect(ctx, 0, 0, self.width, self.height, self.cr)
        ctx.set_source_rgba(0.85, 0.85, 0.88, 1.0)
        ctx.fill_preserve()
        # Raised bezel
        ctx.set_source_rgba(0.75, 0.75, 0.78, 1.0)
        ctx.set_line_width(4)
        ctx.stroke()
        ctx.restore()

        # Screen black border
        ctx.save()
        rounded_rect(
            ctx,
            self.bezel_padding / 2,
            self.bezel_padding / 2,
            self.width - self.bezel_padding,
            self.height - self.bezel_padding,
            max(0.0, self.cr - self.bezel_padding / 2),
        )
        ctx.set_source_rgba(0.0, 0.0, 0.0, 1.0)
        ctx.fill()
        ctx.restore()

        # Draw screen content with clip
        ctx.save()
        ctx.translate(self.bezel_padding, self.bezel_padding)
        rounded_rect(ctx, 0, 0, self.screen_width, self.screen_height, self.screen_cr)
        ctx.clip()

        for child in self.screen.children:
            child.draw(ctx, time)
        ctx.restore()


# Semantic alias
TitaniumRuggedWatch = RuggedSmartwatchFrame


class MinimalistSquareWatch(BaseWatch):
    """
    Sleek aluminum square smartwatch with 2.5D curved front glass and silicone strap.
    """
    def __init__(
        self,
        width: float = 280.0,
        height: float = 340.0,
        corner_radius: float = 45.0,
        shadow: Optional[Union[DropShadow, bool]] = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.width = float(width)
        self.height = float(height)
        self.cr = float(corner_radius)

        self.bezel_padding = 15.0
        self.screen_width = self.width - 2 * self.bezel_padding
        self.screen_height = self.height - 2 * self.bezel_padding
        self.screen_cr = max(0.0, self.cr - self.bezel_padding)

        if shadow is True:
            self.shadow = DropShadow.elevated(blur=24.0, offset=(0, 12), color=Color.BLACK.with_alpha(0.40))
        elif isinstance(shadow, DropShadow):
            self.shadow = shadow
        else:
            self.shadow = None

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width, self.height)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        # Band (Simple silicone)
        ctx.save()
        band_width = self.width * 0.75
        band_x = (self.width - band_width) / 2
        ctx.set_source_rgba(0.1, 0.1, 0.15, 1.0)
        rounded_rect(ctx, band_x, -100, band_width, self.height + 200, 5)
        ctx.fill()
        ctx.restore()

        # Shadow (only when real surface is available)
        if self.shadow is not None and hasattr(ctx, "set_source_surface"):
            self.shadow.render_shadow(ctx, (0, 0, self.width, self.height), self.cr)

        # Aluminum Case
        ctx.save()
        rounded_rect(ctx, 0, 0, self.width, self.height, self.cr)
        ctx.set_source_rgba(0.2, 0.2, 0.2, 1.0)
        ctx.fill_preserve()
        # 2.5D glass edge curve (inner shadow/highlight)
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.1)
        ctx.set_line_width(2)
        ctx.stroke()
        ctx.restore()

        # Screen black border
        ctx.save()
        rounded_rect(
            ctx,
            self.bezel_padding / 2,
            self.bezel_padding / 2,
            self.width - self.bezel_padding,
            self.height - self.bezel_padding,
            max(0.0, self.cr - self.bezel_padding / 2),
        )
        ctx.set_source_rgba(0.0, 0.0, 0.0, 1.0)
        ctx.fill()
        ctx.restore()

        # Draw screen content with clip
        ctx.save()
        ctx.translate(self.bezel_padding, self.bezel_padding)
        rounded_rect(ctx, 0, 0, self.screen_width, self.screen_height, self.screen_cr)
        ctx.clip()

        for child in self.screen.children:
            child.draw(ctx, time)
        ctx.restore()


class ClassicRoundSmartwatchFace(BaseWatch):
    """
    Classic circular smartwatch with rotating bezel notches, stainless steel chassis, and leather strap.
    """
    def __init__(
        self,
        radius: float = 160.0,
        shadow: Optional[Union[DropShadow, bool]] = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.radius = float(radius)
        self.width = self.radius * 2
        self.height = self.radius * 2

        self.bezel_padding = 25.0
        self.screen_radius = self.radius - self.bezel_padding

        if shadow is True:
            self.shadow = DropShadow.elevated(blur=28.0, offset=(0, 14), color=Color.BLACK.with_alpha(0.45))
        elif isinstance(shadow, DropShadow):
            self.shadow = shadow
        else:
            self.shadow = None

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width, self.height)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        cx, cy = self.radius, self.radius

        # Lugs and band
        ctx.save()
        band_width = self.radius * 1.1
        band_x = cx - band_width / 2
        # Leather-style band
        ctx.set_source_rgba(0.4, 0.25, 0.15, 1.0)
        rounded_rect(ctx, band_x, -80, band_width, self.height + 160, 4)
        ctx.fill()

        # Metal Lugs
        ctx.set_source_rgba(0.7, 0.7, 0.7, 1.0)
        # Top left
        rounded_rect(ctx, band_x - 10, -20, 15, 40, 2)
        # Top right
        rounded_rect(ctx, band_x + band_width - 5, -20, 15, 40, 2)
        # Bottom left
        rounded_rect(ctx, band_x - 10, self.height - 20, 15, 40, 2)
        # Bottom right
        rounded_rect(ctx, band_x + band_width - 5, self.height - 20, 15, 40, 2)
        ctx.fill()
        ctx.restore()

        # Shadow (only when real surface is available)
        if self.shadow is not None and hasattr(ctx, "set_source_surface"):
            self.shadow.render_shadow(ctx, (0, 0, self.width, self.height), self.radius)

        # Stainless Steel Case / Outer Bezel
        ctx.save()
        ctx.arc(cx, cy, self.radius, 0, 2 * math.pi)
        ctx.set_source_rgba(0.15, 0.15, 0.15, 1.0)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.7, 0.7, 0.7, 1.0)
        ctx.set_line_width(4)
        ctx.stroke()

        # Rotating bezel notches
        num_notches = 60
        ctx.set_source_rgba(0.6, 0.6, 0.6, 1.0)
        ctx.set_line_width(2)
        for i in range(num_notches):
            angle = i * (2 * math.pi / num_notches)
            r1 = self.radius
            r2 = self.radius - 8
            if i % 5 == 0:
                r2 = self.radius - 12
                ctx.set_line_width(3)
            else:
                ctx.set_line_width(1)
            ctx.move_to(cx + r1 * math.cos(angle), cy + r1 * math.sin(angle))
            ctx.line_to(cx + r2 * math.cos(angle), cy + r2 * math.sin(angle))
            ctx.stroke()
        ctx.restore()

        # Inner black border (Display deadzone)
        ctx.save()
        ctx.arc(cx, cy, self.screen_radius + 4, 0, 2 * math.pi)
        ctx.set_source_rgba(0.0, 0.0, 0.0, 1.0)
        ctx.fill()
        ctx.restore()

        # Screen content with circular clip
        ctx.save()
        ctx.translate(self.bezel_padding, self.bezel_padding)
        ctx.arc(self.screen_radius, self.screen_radius, self.screen_radius, 0, 2 * math.pi)
        ctx.clip()

        for child in self.screen.children:
            child.draw(ctx, time)
        ctx.restore()


class SmartwatchRuggedSuite:
    """
    Suite factory for smartwatches and wearable chassis mockups.
    """
    @staticmethod
    def watch(**kwargs: Any) -> RuggedSmartwatchFrame:
        return RuggedSmartwatchFrame(**kwargs)

    @staticmethod
    def rugged_watch(**kwargs: Any) -> RuggedSmartwatchFrame:
        return RuggedSmartwatchFrame(**kwargs)

    @staticmethod
    def square_watch(**kwargs: Any) -> MinimalistSquareWatch:
        return MinimalistSquareWatch(**kwargs)

    @staticmethod
    def round_watch(**kwargs: Any) -> ClassicRoundSmartwatchFace:
        return ClassicRoundSmartwatchFace(**kwargs)
