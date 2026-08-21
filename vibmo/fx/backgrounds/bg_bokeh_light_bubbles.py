"""
Cinematic Bokeh & Ambient Particle Backdrops.
"""

from __future__ import annotations
import math
import random
from typing import Any, Tuple, Union, List
import cairo

from vibmo.core.color import Color, colors
from vibmo.scene.node import Node


class DriftingBokehOrbs(Node):
    """
    Soft, out-of-focus hexagonal and circular aperture bokeh discs drifting vertically.
    """

    def __init__(
        self,
        width: float = 1920.0,
        height: float = 1080.0,
        count: int = 50,
        speed_multiplier: float = 1.0,
        base_color: Union[Color, str] = colors.WHITE,
        shape: str = "circle", # "circle" or "hexagon"
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.w = float(width)
        self.h = float(height)
        self.count = int(count)
        self.speed_multiplier = float(speed_multiplier)
        self.base_color = Color.from_any(base_color)
        self.shape = shape
        
        # Initialize particles
        self.particles = []
         # Deterministic for testing/consistency
        for _ in range(self.count):
            self.particles.append({
                "x": random.uniform(0, self.w),
                "y": random.uniform(0, self.h),
                "radius": random.uniform(20.0, 150.0),
                "speed_y": random.uniform(10.0, 40.0),
                "drift_x": random.uniform(-10.0, 10.0),
                "phase": random.uniform(0, math.pi * 2),
                "opacity": random.uniform(0.1, 0.6),
                "depth": random.uniform(0.5, 2.0)
            })

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.w, self.h)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        
        # Set blending mode to ADD for that glowing light effect
        try:
            ctx.set_operator(cairo.Operator.ADD)
        except AttributeError:
            pass # fallback if cairo version doesn't support it

        for p in self.particles:
            # Update particle position
            py = p["y"] - (p["speed_y"] * time * self.speed_multiplier / p["depth"])
            # Wrap around vertically
            py = py % (self.h + p["radius"] * 2) - p["radius"]
            
            px = p["x"] + math.sin(time * 0.5 + p["phase"]) * p["drift_x"] * self.speed_multiplier
            
            ctx.save()
            ctx.translate(px, py)
            
            # Subtle pulsation based on time and phase
            current_opacity = p["opacity"] * (0.8 + 0.2 * math.sin(time * 2.0 + p["phase"]))
            
            c = self.base_color
            
            if self.shape == "hexagon":
                self._draw_hexagon(ctx, 0, 0, p["radius"])
            else:
                ctx.arc(0, 0, p["radius"], 0, math.pi * 2)
                
            # Radial gradient for soft edges
            pat = cairo.RadialGradient(0, 0, p["radius"] * 0.1, 0, 0, p["radius"])
            pat.add_color_stop_rgba(0.0, c.r, c.g, c.b, current_opacity)
            pat.add_color_stop_rgba(0.7, c.r, c.g, c.b, current_opacity * 0.8)
            pat.add_color_stop_rgba(1.0, c.r, c.g, c.b, 0.0)
            
            ctx.set_source(pat)
            ctx.fill()
            
            ctx.restore()

        ctx.restore()
        
    def _draw_hexagon(self, ctx: Any, x: float, y: float, r: float) -> None:
        ctx.new_path()
        for i in range(6):
            angle = i * math.pi / 3
            px = x + r * math.cos(angle)
            py = y + r * math.sin(angle)
            if i == 0:
                ctx.move_to(px, py)
            else:
                ctx.line_to(px, py)
        ctx.close_path()


class AnamorphicLensGleamBackdrop(Node):
    """
    Subtle horizontal chromatic streaks and lens glints drifting across dark background.
    """

    def __init__(
        self,
        width: float = 1920.0,
        height: float = 1080.0,
        count: int = 15,
        speed_multiplier: float = 1.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.w = float(width)
        self.h = float(height)
        self.count = int(count)
        self.speed_multiplier = float(speed_multiplier)
        
        self.streaks = []
        
        for _ in range(self.count):
            self.streaks.append({
                "y": random.uniform(0, self.h),
                "speed_x": random.uniform(20.0, 100.0),
                "width": random.uniform(200.0, 800.0),
                "height": random.uniform(2.0, 10.0),
                "opacity": random.uniform(0.3, 0.8),
                "phase": random.uniform(0, math.pi * 2),
                "color_shift": random.choice([-1, 0, 1]) # -1: cyan, 0: white, 1: orange/red
            })

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.w, self.h)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        
        try:
            ctx.set_operator(cairo.Operator.ADD) # Screen/Add blend mode
        except AttributeError:
            pass
            
        for s in self.streaks:
            px = (time * s["speed_x"] * self.speed_multiplier + s["phase"] * 100) % (self.w + s["width"] * 2) - s["width"]
            py = s["y"] + math.sin(time * 0.2 + s["phase"]) * 20.0 # gentle vertical drift
            
            ctx.save()
            ctx.translate(px, py)
            
            # Anamorphic streak is very wide, very thin
            sw = s["width"]
            sh = s["height"]
            
            current_opacity = s["opacity"] * (0.5 + 0.5 * math.sin(time + s["phase"]))
            
            # Determine color based on shift
            if s["color_shift"] == -1:
                r, g, b = 0.2, 0.6, 1.0 # Cyan/Blue
            elif s["color_shift"] == 1:
                r, g, b = 1.0, 0.4, 0.1 # Orange/Red
            else:
                r, g, b = 0.9, 0.9, 1.0 # Cool white
                
            # Horizontal gradient
            pat = cairo.LinearGradient(-sw/2, 0, sw/2, 0)
            pat.add_color_stop_rgba(0.0, r, g, b, 0.0)
            pat.add_color_stop_rgba(0.4, r, g, b, current_opacity * 0.8)
            pat.add_color_stop_rgba(0.5, 1.0, 1.0, 1.0, current_opacity) # Hot core
            pat.add_color_stop_rgba(0.6, r, g, b, current_opacity * 0.8)
            pat.add_color_stop_rgba(1.0, r, g, b, 0.0)
            
            ctx.rectangle(-sw/2, -sh/2, sw, sh)
            ctx.set_source(pat)
            ctx.fill()
            
            # Add a small bright glint in the center
            if current_opacity > 0.4:
                ctx.arc(0, 0, sh * 1.5, 0, math.pi * 2)
                glint_pat = cairo.RadialGradient(0, 0, 0, 0, 0, sh * 1.5)
                glint_pat.add_color_stop_rgba(0.0, 1.0, 1.0, 1.0, current_opacity)
                glint_pat.add_color_stop_rgba(1.0, r, g, b, 0.0)
                ctx.set_source(glint_pat)
                ctx.fill()
                
            ctx.restore()
            
        ctx.restore()


class GoldenDustAmbience(Node):
    """
    Shimmering micro-dust motes catching directional light rays with organic turbulence.
    """

    def __init__(
        self,
        width: float = 1920.0,
        height: float = 1080.0,
        count: int = 200,
        speed_multiplier: float = 1.0,
        color: Union[Color, str] = colors.AMBER,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.w = float(width)
        self.h = float(height)
        self.count = int(count)
        self.speed_multiplier = float(speed_multiplier)
        self.color = Color.from_any(color)
        
        self.motes = []
        
        for _ in range(self.count):
            self.motes.append({
                "x": random.uniform(0, self.w),
                "y": random.uniform(0, self.h),
                "radius": random.uniform(1.0, 4.0),
                "vx": random.uniform(-10.0, 10.0),
                "vy": random.uniform(-20.0, 5.0), # generally drifts up
                "phase": random.uniform(0, math.pi * 2),
                "opacity": random.uniform(0.2, 0.9),
                "flicker_speed": random.uniform(2.0, 8.0)
            })

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.w, self.h)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        
        try:
            ctx.set_operator(cairo.Operator.ADD)
        except AttributeError:
            pass

        # Simulate directional light rays hitting dust
        # We'll just make opacity depend on position slightly to fake light shafts
            
        for m in self.motes:
            # Add some turbulence using sin waves
            turb_x = math.sin(time * 0.5 + m["y"] * 0.01) * 20.0
            turb_y = math.cos(time * 0.3 + m["x"] * 0.01) * 10.0
            
            px = (m["x"] + m["vx"] * time * self.speed_multiplier + turb_x) % self.w
            py = (m["y"] + m["vy"] * time * self.speed_multiplier + turb_y) % self.h
            
            # Flickering opacity
            flicker = 0.5 + 0.5 * math.sin(time * m["flicker_speed"] + m["phase"])
            current_opacity = m["opacity"] * flicker
            
            # Fake light shafts: dust is brighter in certain diagonal bands
            shaft = (px + py * 0.5) % 300
            if 100 < shaft < 150:
                current_opacity *= 1.5 # Boost brightness in "light shaft"
            else:
                current_opacity *= 0.5 # Dim outside
                
            current_opacity = min(1.0, max(0.0, current_opacity))
            
            if current_opacity > 0.05:
                ctx.save()
                ctx.translate(px, py)
                
                c = self.color
                ctx.arc(0, 0, m["radius"], 0, math.pi * 2)
                
                pat = cairo.RadialGradient(0, 0, 0, 0, 0, m["radius"])
                pat.add_color_stop_rgba(0.0, 1.0, 1.0, 1.0, current_opacity) # White hot center
                pat.add_color_stop_rgba(0.4, c.r, c.g, c.b, current_opacity * 0.8)
                pat.add_color_stop_rgba(1.0, c.r, c.g, c.b, 0.0)
                
                ctx.set_source(pat)
                ctx.fill()
                
                ctx.restore()
                
        ctx.restore()
