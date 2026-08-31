from __future__ import annotations
import math
from typing import Any, Optional, Tuple, Union
import cairo

from vibmo.core.color import Color, colors
from vibmo.scene.node import Node

class CalifornianSunsetBackdrop(Node):
    def __init__(
        self,
        width: float = 1920.0,
        height: float = 1080.0,
        sun_radius: Optional[float] = None,
        atmospheric_haze: Optional[float] = None,
        speed: float = 1.0,
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.width = float(width)
        self.height = float(height)
        self.sun_radius = float(sun_radius) if sun_radius is not None else 400.0
        self.atmospheric_haze = float(atmospheric_haze) if atmospheric_haze is not None else 0.2
        self.speed = float(speed)
        
        self.amber = Color.hex("#FFBF00")
        self.coral = Color.hex("#FF7F50")
        self.violet = Color.hex("#EE82EE")

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width, self.height)
        
    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        
        # Base horizon gradient
        pat = cairo.LinearGradient(0, 0, 0, self.height)
        pat.add_color_stop_rgba(0.0, self.violet.r, self.violet.g, self.violet.b, self.violet.a)
        pat.add_color_stop_rgba(0.5, self.coral.r, self.coral.g, self.coral.b, self.coral.a)
        pat.add_color_stop_rgba(1.0, self.amber.r, self.amber.g, self.amber.b, self.amber.a)
        
        ctx.rectangle(0, 0, self.width, self.height)
        ctx.set_source(pat)
        ctx.fill()
        
        # Warm breathing sun glow
        glow_radius = self.sun_radius + math.sin(time * self.speed * 0.5) * (self.sun_radius * 0.125)
        sun_x = self.width / 2
        sun_y = self.height * 0.75
        
        sun_pat = cairo.RadialGradient(sun_x, sun_y, 0, sun_x, sun_y, glow_radius)
        sun_pat.add_color_stop_rgba(0.0, 1.0, 0.9, 0.5, 0.6)
        sun_pat.add_color_stop_rgba(0.4, 1.0, 0.6, 0.2, 0.3)
        sun_pat.add_color_stop_rgba(1.0, 1.0, 0.6, 0.2, 0.0)
        
        ctx.set_source(sun_pat)
        ctx.set_operator(cairo.OPERATOR_ADD)
        ctx.rectangle(0, 0, self.width, self.height)
        ctx.fill()
        
        # Atmospheric haze overlay
        if self.atmospheric_haze > 0:
            haze_pat = cairo.LinearGradient(0, self.height * 0.5, 0, self.height)
            haze_pat.add_color_stop_rgba(0.0, 1.0, 0.9, 0.7, 0.0)
            haze_pat.add_color_stop_rgba(1.0, 1.0, 0.85, 0.6, self.atmospheric_haze)
            ctx.set_source(haze_pat)
            ctx.rectangle(0, 0, self.width, self.height)
            ctx.fill()
        
        # Subtle heat shimmer (y offset variation across x)
        horizon_y = self.height * 0.75
        ctx.set_line_width(2.0)
        for i in range(5):
            y_base = horizon_y + (i - 2) * 30.0
            ctx.new_path()
            for x in range(0, int(self.width) + 40, 40):
                # shimmer waves depend on x and time
                y_offset = math.sin((x / 60.0) + time * self.speed * (3.0 + i * 0.5)) * 4.0
                if x == 0:
                    ctx.move_to(x, y_base + y_offset)
                else:
                    ctx.line_to(x, y_base + y_offset)
            ctx.set_source_rgba(1.0, 0.9, 0.7, 0.15 - abs(i - 2) * 0.03)
            ctx.stroke()
            
        ctx.restore()

class GoldenHourSkyGradient(Node):
    def __init__(self, width: float = 1920.0, height: float = 1080.0, **kwargs):
        super().__init__(**kwargs)
        self.width = float(width)
        self.height = float(height)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width, self.height)
        
    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        
        # Shifting twilight sky
        # Diurnal cycle: shifts colors based on time
        cycle = (math.sin(time * 0.1) + 1.0) / 2.0  # 0.0 to 1.0
        
        # Top color (blue to dark purple)
        top_r = 0.2 + cycle * 0.1
        top_g = 0.4 - cycle * 0.2
        top_b = 0.8 - cycle * 0.3
        
        # Bottom color (orange to deep red)
        bot_r = 1.0 - cycle * 0.3
        bot_g = 0.7 - cycle * 0.5
        bot_b = 0.2 - cycle * 0.1
        
        pat = cairo.LinearGradient(0, 0, 0, self.height)
        pat.add_color_stop_rgba(0.0, top_r, top_g, top_b, 1.0)
        pat.add_color_stop_rgba(1.0, bot_r, bot_g, bot_b, 1.0)
        
        ctx.rectangle(0, 0, self.width, self.height)
        ctx.set_source(pat)
        ctx.fill()
        
        ctx.restore()


class AtmosphericHazeHorizon(Node):
    def __init__(self, width: float = 1920.0, height: float = 1080.0, **kwargs):
        super().__init__(**kwargs)
        self.width = float(width)
        self.height = float(height)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width, self.height)
        
    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        
        # Base sky
        sky_pat = cairo.LinearGradient(0, 0, 0, self.height)
        sky_pat.add_color_stop_rgba(0.0, 0.6, 0.7, 0.8, 1.0)
        sky_pat.add_color_stop_rgba(1.0, 0.9, 0.8, 0.7, 1.0)
        ctx.rectangle(0, 0, self.width, self.height)
        ctx.set_source(sky_pat)
        ctx.fill()
        
        # Layered silhouetted mountain waves
        for i in range(3):
            layer_time = time * (0.2 + i * 0.1)
            y_base = self.height * (0.6 + i * 0.15)
            alpha = 0.3 + i * 0.2
            
            ctx.new_path()
            ctx.move_to(0, self.height)
            
            for x in range(0, int(self.width) + 50, 50):
                # Misty waves
                wave = math.sin((x / 200.0) + layer_time) * 30.0 * (1.0 - i * 0.2)
                ctx.line_to(x, y_base + wave)
                
            ctx.line_to(self.width, self.height)
            ctx.close_path()
            
            ctx.set_source_rgba(0.2, 0.2, 0.3, alpha)
            ctx.fill()
            
        ctx.restore()


# Semantic Alias
SunsetHorizonGlow = CalifornianSunsetBackdrop

__all__ = [
    "CalifornianSunsetBackdrop",
    "SunsetHorizonGlow",
    "GoldenHourSkyGradient",
    "AtmosphericHazeHorizon",
]
