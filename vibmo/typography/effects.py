"""
Advanced typography effects (NeonText, GradientText, Text3D, TextStroke, TextShadow, TextGlow, WarpText).
"""

from __future__ import annotations
import math
from typing import Any, List, Optional, Sequence, Tuple, Union
import cairo

from vibmo.core.color import Color, LinearGradient, colors
from vibmo.core.vector import Vector2D
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.scene.node import Node


class NeonText(Node):
    """
    Vibrant flickering neon tube sign text effect with glass tube core and multi-octave glow aura.
    """

    def __init__(
        self,
        text: str = "CYBERPUNK",
        font_size: float = 64.0,
        font_family: str = "Segoe UI",
        color: Union[Color, str] = colors.CYAN,
        flicker: bool = True,
        flicker_speed: float = 8.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.text_content = text
        self.font_size = float(font_size)
        self.font_family = font_family
        self.color = Color.from_any(color)
        self.flicker = flicker
        self.flicker_speed = float(flicker_speed)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        pad = self.font_size * 0.5
        return (-pad, -pad, len(self.text_content) * self.font_size * 0.7 + pad * 2, self.font_size * 1.5 + pad * 2)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(self.font_size)

        # Flicker intensity modulation
        glow_mult = 1.0
        if self.flicker:
            # Pseudo-random neon tube buzz
            f = math.sin(time * self.flicker_speed * 13.7) * math.cos(time * self.flicker_speed * 7.3)
            glow_mult = 0.85 + 0.15 * f if f > -0.7 else 0.35

        c = self.color
        # 1. Outer Diffuse Aura Glow
        ctx.set_source_rgba(c.r, c.g, c.b, 0.15 * glow_mult)
        ctx.set_line_width(self.font_size * 0.35)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.text_path(self.text_content)
        ctx.stroke()

        # 2. Medium Radiant Halo
        ctx.set_source_rgba(c.r, c.g, c.b, 0.45 * glow_mult)
        ctx.set_line_width(self.font_size * 0.12)
        ctx.text_path(self.text_content)
        ctx.stroke()

        # 3. Inner White-Hot Glass Core Tube
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.95 * glow_mult)
        ctx.set_line_width(max(1.5, self.font_size * 0.04))
        ctx.text_path(self.text_content)
        ctx.stroke()

        ctx.restore()


class GradientText(Node):
    """
    Text filled with dynamic multi-stop linear or radial gradients.
    """

    def __init__(
        self,
        text: str = "VIBMO STUDIO",
        font_size: float = 56.0,
        font_family: str = "Segoe UI",
        gradient_colors: Sequence[Union[Color, str]] = (colors.INDIGO, colors.PINK, colors.AMBER),
        angle: float = 0.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.text_content = text
        self.font_size = float(font_size)
        self.font_family = font_family
        self.gradient_colors = [Color.from_any(c) for c in gradient_colors]
        self.angle = float(angle)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, len(self.text_content) * self.font_size * 0.7, self.font_size * 1.4)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(self.font_size)
        ext = ctx.text_extents(self.text_content)

        # Create gradient along text bounds
        rad = math.radians(self.angle)
        sx = 0.0
        sy = self.font_size * 0.5 - math.sin(rad) * self.font_size * 0.5
        ex = ext.width
        ey = self.font_size * 0.5 + math.sin(rad) * self.font_size * 0.5

        pat = cairo.LinearGradient(sx, sy, ex, ey)
        n = len(self.gradient_colors)
        for i, c in enumerate(self.gradient_colors):
            offset = float(i) / max(1, n - 1)
            pat.add_color_stop_rgba(offset, c.r, c.g, c.b, c.a)

        ctx.set_source(pat)
        ctx.move_to(0.0, self.font_size)
        ctx.show_text(self.text_content)
        ctx.restore()


class Text3D(Node):
    """
    Extruded isometric 3D text with directional bevel shadow layers.
    """

    def __init__(
        self,
        text: str = "EXTRUDED",
        font_size: float = 64.0,
        font_family: str = "Segoe UI",
        depth: int = 14,
        front_color: Union[Color, str] = colors.EMERALD,
        side_color: Union[Color, str] = colors.DARK_NAVY,
        angle: float = 45.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.text_content = text
        self.font_size = float(font_size)
        self.font_family = font_family
        self.depth = max(1, int(depth))
        self.front_color = Color.from_any(front_color)
        self.side_color = Color.from_any(side_color)
        self.angle = float(angle)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        d = self.depth + 10.0
        return (-d, -d, len(self.text_content) * self.font_size * 0.7 + d * 2, self.font_size * 1.5 + d * 2)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(self.font_size)

        rad = math.radians(self.angle)
        dx = math.cos(rad)
        dy = math.sin(rad)

        # 1. Extrusion Shadow Layers (Back to Front)
        sc = self.side_color
        for layer in range(self.depth, 0, -1):
            offset_x = layer * dx
            offset_y = layer * dy
            ctx.set_source_rgba(sc.r, sc.g, sc.b, 0.6 + 0.4 * (1.0 - layer / self.depth))
            ctx.move_to(offset_x, self.font_size + offset_y)
            ctx.show_text(self.text_content)

        # 2. Front Face
        fc = self.front_color
        ctx.set_source_rgba(fc.r, fc.g, fc.b, fc.a)
        ctx.move_to(0, self.font_size)
        ctx.show_text(self.text_content)

        ctx.restore()


class TextStroke(Node):
    """
    Text with customizable stroke outline and optional fill.
    """

    def __init__(
        self,
        text: str = "OUTLINE",
        font_size: float = 52.0,
        font_family: str = "Segoe UI",
        stroke_color: Union[Color, str] = colors.WHITE,
        stroke_width: float = 2.5,
        fill_color: Optional[Union[Color, str]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.text_content = text
        self.font_size = float(font_size)
        self.font_family = font_family
        self.stroke_color = Color.from_any(stroke_color)
        self.stroke_width = float(stroke_width)
        self.fill_color = Color.from_any(fill_color) if fill_color else None

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, len(self.text_content) * self.font_size * 0.7, self.font_size * 1.5)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(self.font_size)
        ctx.move_to(0, self.font_size)
        ctx.text_path(self.text_content)

        if self.fill_color:
            fc = self.fill_color
            ctx.set_source_rgba(fc.r, fc.g, fc.b, fc.a)
            ctx.fill_preserve()

        sc = self.stroke_color
        ctx.set_source_rgba(sc.r, sc.g, sc.b, sc.a)
        ctx.set_line_width(self.stroke_width)
        ctx.stroke()

        ctx.restore()


class WarpText(Node):
    """
    Warped text along geometric arcs, waves, or bulges.
    """

    def __init__(
        self,
        text: str = "WARPED MOTION",
        font_size: float = 48.0,
        warp_type: str = "arc",  # "arc", "wave", "bulge"
        intensity: float = 0.4,
        color: Union[Color, str] = colors.WHITE,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.text_content = text
        self.font_size = float(font_size)
        self.warp_type = warp_type
        self.intensity = float(intensity)
        self.color = Color.from_any(color)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, -40.0, len(self.text_content) * self.font_size * 0.75, self.font_size * 2.5)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        ctx.select_font_face("Segoe UI", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(self.font_size)
        c = self.color
        ctx.set_source_rgba(c.r, c.g, c.b, c.a)

        cur_x = 0.0
        n = len(self.text_content)
        for i, char in enumerate(self.text_content):
            t_norm = (float(i) / max(1, n - 1)) * 2.0 - 1.0  # -1.0 to 1.0
            
            if self.warp_type == "wave":
                y_off = math.sin(t_norm * math.pi * 2.0 + time * 3.0) * self.font_size * self.intensity
                rot = math.cos(t_norm * math.pi * 2.0 + time * 3.0) * self.intensity * 0.4
            else:  # Arc / Dome
                y_off = -(1.0 - t_norm ** 2) * self.font_size * self.intensity * 1.5
                rot = t_norm * self.intensity * 0.6

            ctx.save()
            ctx.translate(cur_x, self.font_size + y_off)
            ctx.rotate(rot)
            ctx.move_to(0, 0)
            ctx.show_text(char)
            ext = ctx.text_extents(char)
            ctx.restore()

            cur_x += ext.x_advance + 2.0

        ctx.restore()
