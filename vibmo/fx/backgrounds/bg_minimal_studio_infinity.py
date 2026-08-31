import math
from typing import Any, Optional, Tuple, Union
import cairo

from vibmo.scene.node import Node
from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal


class HorizonYSignal(Signal[float]):
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Signal):
            return self.get(0.0) == other.get(0.0)
        return self.get(0.0) == other


class AppleStudioInfinityCyc(Node):
    """
    Infinite curved photography cyclorama studio with soft overhead softbox
    lighting falloff and floor contact reflection.
    """
    def __init__(
        self,
        base_color: Union[Color, str] = colors.WHITE,
        bg_color: Union[Color, str] = "#e0e0e0",
        floor_color: Union[Color, str] = "#d0d0d0",
        width: float = 1920.0,
        height: float = 1080.0,
        horizon_y: Optional[float] = None,
        rim_light: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.base_color = Signal(Color.from_any(base_color), f"{self.name}.base_color")
        self.bg_color = Signal(Color.from_any(bg_color), f"{self.name}.bg_color")
        self.floor_color = Signal(Color.from_any(floor_color), f"{self.name}.floor_color")
        self.width = Signal(float(width), f"{self.name}.width")
        self.height = Signal(float(height), f"{self.name}.height")
        self.horizon_y = HorizonYSignal(float(horizon_y) if horizon_y is not None else float(height) * 0.7, f"{self.name}.horizon_y")
        self.rim_light = rim_light

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width.get(time)
        h = self.height.get(time)
        base = self.base_color.get(time)
        bg = self.bg_color.get(time)
        floor = self.floor_color.get(time)
        hy = self.horizon_y.get(time)

        # Softbox radial gradient overhead
        radial = cairo.RadialGradient(w/2, 0, 0, w/2, 0, w * 0.8)
        radial.add_color_stop_rgba(0, base.r, base.g, base.b, base.a)
        radial.add_color_stop_rgba(1, bg.r, bg.g, bg.b, bg.a)

        ctx.save()
        ctx.rectangle(0, 0, w, h)
        ctx.set_source(radial)
        ctx.fill()

        # Floor contact shadow/reflection gradient
        linear = cairo.LinearGradient(0, hy, 0, h)
        linear.add_color_stop_rgba(0, bg.r, bg.g, bg.b, 0.0)
        linear.add_color_stop_rgba(1, floor.r, floor.g, floor.b, floor.a)

        ctx.rectangle(0, hy, w, max(0.0, h - hy))
        ctx.set_source(linear)
        ctx.fill()

        # Rim light highlight on horizon if enabled
        if self.rim_light:
            rim = cairo.LinearGradient(0, hy - 4, 0, hy + 4)
            rim.add_color_stop_rgba(0, 1.0, 1.0, 1.0, 0.0)
            rim.add_color_stop_rgba(0.5, 1.0, 1.0, 1.0, 0.4)
            rim.add_color_stop_rgba(1, 1.0, 1.0, 1.0, 0.0)
            ctx.rectangle(0, hy - 4, w, 8)
            ctx.set_source(rim)
            ctx.fill()

        ctx.restore()


class SoftStageSpotlightBackdrop(Node):
    """
    Gentle elliptical stage spotlight that breathes and glides with camera focus.
    """
    def __init__(
        self,
        spot_color: Union[Color, str] = "#ffffff",
        bg_color: Union[Color, str] = "#111111",
        width: float = 1920.0,
        height: float = 1080.0,
        breath_speed: float = 1.0,
        breath_amplitude: float = 0.1,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.spot_color = Signal(Color.from_any(spot_color), f"{self.name}.spot_color")
        self.bg_color = Signal(Color.from_any(bg_color), f"{self.name}.bg_color")
        self.width = Signal(float(width), f"{self.name}.width")
        self.height = Signal(float(height), f"{self.name}.height")
        self.breath_speed = Signal(float(breath_speed), f"{self.name}.breath_speed")
        self.breath_amplitude = Signal(float(breath_amplitude), f"{self.name}.breath_amplitude")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width.get(time)
        h = self.height.get(time)
        spot = self.spot_color.get(time)
        bg = self.bg_color.get(time)
        b_speed = self.breath_speed.get(time)
        b_amp = self.breath_amplitude.get(time)

        ctx.save()

        # Fill base background
        ctx.set_source_rgba(bg.r, bg.g, bg.b, bg.a)
        ctx.rectangle(0, 0, w, h)
        ctx.fill()

        # Calculate breath radius
        base_radius = min(w, h) * 0.4
        breath = math.sin(time * math.pi * b_speed) * b_amp
        radius = base_radius * (1.0 + breath)

        # Apply matrix scaling for elliptical spotlight
        ctx.translate(w/2, h/2)
        ctx.scale(1.5, 1.0)

        radial = cairo.RadialGradient(0, 0, 0, 0, 0, radius)
        radial.add_color_stop_rgba(0, spot.r, spot.g, spot.b, spot.a)
        radial.add_color_stop_rgba(1, spot.r, spot.g, spot.b, 0.0)

        ctx.arc(0, 0, radius, 0, math.pi * 2)
        ctx.set_source(radial)
        ctx.fill()

        ctx.restore()


class FrostedGlassHorizon(Node):
    """
    Minimalist split horizon with frosted glass blur separation line.
    """
    def __init__(
        self,
        top_color: Union[Color, str] = "#f0f0f0",
        bottom_color: Union[Color, str] = "#d0d0d0",
        width: float = 1920.0,
        height: float = 1080.0,
        horizon_y: float = 540.0,
        blur_height: float = 100.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.top_color = Signal(Color.from_any(top_color), f"{self.name}.top_color")
        self.bottom_color = Signal(Color.from_any(bottom_color), f"{self.name}.bottom_color")
        self.width = Signal(float(width), f"{self.name}.width")
        self.height = Signal(float(height), f"{self.name}.height")
        self.horizon_y = Signal(float(horizon_y), f"{self.name}.horizon_y")
        self.blur_height = Signal(float(blur_height), f"{self.name}.blur_height")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width.get(time)
        h = self.height.get(time)
        top = self.top_color.get(time)
        bottom = self.bottom_color.get(time)
        hy = self.horizon_y.get(time)
        bh = self.blur_height.get(time)

        ctx.save()

        # Top rectangle
        ctx.set_source_rgba(top.r, top.g, top.b, top.a)
        ctx.rectangle(0, 0, w, hy)
        ctx.fill()

        # Bottom rectangle
        ctx.set_source_rgba(bottom.r, bottom.g, bottom.b, bottom.a)
        ctx.rectangle(0, hy, w, h - hy)
        ctx.fill()

        # Frosted glass blur overlay
        # Since the background is already split sharply, we can draw a gradient
        # that interpolates between top and bottom colors directly over the blur area
        # to simulate the diffusion of a frosted glass separating the two.
        linear = cairo.LinearGradient(0, hy - bh/2, 0, hy + bh/2)
        linear.add_color_stop_rgba(0, top.r, top.g, top.b, top.a)
        linear.add_color_stop_rgba(1, bottom.r, bottom.g, bottom.b, bottom.a)

        ctx.rectangle(0, hy - bh/2, w, bh)
        ctx.set_source(linear)
        ctx.fill()

        ctx.restore()


# Semantic Alias
MinimalStudioInfinity = AppleStudioInfinityCyc

__all__ = [
    "AppleStudioInfinityCyc",
    "MinimalStudioInfinity",
    "SoftStageSpotlightBackdrop",
    "FrostedGlassHorizon",
]
