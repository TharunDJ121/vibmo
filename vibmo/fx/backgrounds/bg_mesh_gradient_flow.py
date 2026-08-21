from __future__ import annotations
import math
import cairo
import numpy as np
from PIL import Image
from typing import Any, List, Optional, Tuple, Sequence, Union

from vibmo.scene.node import Node
from vibmo.core.color import Color, ColorStop
from vibmo.core.signal import Signal

class MeshGradientFlow(Node):
    """
    4-point to 9-point multi-color control mesh where gradient color control nodes
    orbit organically using harmonic sine/cosine paths as time advances.
    """
    def __init__(
        self,
        width: float = 1920.0,
        height: float = 1080.0,
        colors: Sequence[Union[Color, str]] = None,
        speed_multiplier: float = 1.0,
        resolution_scale: float = 0.25,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.width = Signal(width)
        self.height = Signal(height)

        if colors is None:
            colors = ["#ff0055", "#0055ff", "#00ff55", "#ffaa00", "#5500ff"]

        self.mesh_colors = [Color.from_any(c) for c in colors]
        self.speed_multiplier = Signal(speed_multiplier)
        self.resolution_scale = Signal(resolution_scale)

        # We assign some orbital parameters for each color point
        self._orbits = []
        for i in range(len(self.mesh_colors)):
            # Pseudorandom but deterministic orbital parameters
            cx = 0.5 + 0.3 * math.sin(i * 1.7)
            cy = 0.5 + 0.3 * math.cos(i * 2.3)
            r = 0.2 + 0.15 * (i % 3)
            freq_x = 0.5 + 0.2 * (i % 4)
            freq_y = 0.6 + 0.3 * (i % 2)
            phase = i * 1.1
            self._orbits.append((cx, cy, r, freq_x, freq_y, phase))

    def _generate_surface(self, w: int, h: int, time: float) -> cairo.ImageSurface:
        speed = self.speed_multiplier.get(time)
        t = time * speed

        # Compute current positions of color nodes
        nodes = []
        for (cx, cy, r, fx, fy, phase), c in zip(self._orbits, self.mesh_colors):
            nx = cx + r * math.sin(t * fx + phase)
            ny = cy + r * math.cos(t * fy + phase)
            nodes.append((nx * w, ny * h, c.r, c.g, c.b))

        # Create coordinate grid
        x = np.arange(w)
        y = np.arange(h)
        xx, yy = np.meshgrid(x, y)

        # Accumulate colors via inverse-square distance weighting
        r_out = np.zeros((h, w), dtype=np.float32)
        g_out = np.zeros((h, w), dtype=np.float32)
        b_out = np.zeros((h, w), dtype=np.float32)
        weight_sum = np.zeros((h, w), dtype=np.float32)

        for nx, ny, cr, cg, cb in nodes:
            dist_sq = (xx - nx)**2 + (yy - ny)**2
            # Add small epsilon to prevent division by zero
            w_i = 1.0 / (dist_sq + 100.0)

            r_out += cr * w_i
            g_out += cg * w_i
            b_out += cb * w_i
            weight_sum += w_i

        r_out /= weight_sum
        g_out /= weight_sum
        b_out /= weight_sum

        # Convert to 8-bit BGRA for Cairo
        bgra = np.zeros((h, w, 4), dtype=np.uint8)
        bgra[..., 0] = np.clip(b_out * 255, 0, 255).astype(np.uint8) # B
        bgra[..., 1] = np.clip(g_out * 255, 0, 255).astype(np.uint8) # G
        bgra[..., 2] = np.clip(r_out * 255, 0, 255).astype(np.uint8) # R
        bgra[..., 3] = 255 # A

        # Make a cairo surface
        surface = cairo.ImageSurface.create_for_data(bgra, cairo.FORMAT_ARGB32, w, h)
        return surface

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = max(1.0, self.width.get(time))
        h = max(1.0, self.height.get(time))
        res = max(0.01, min(1.0, self.resolution_scale.get(time)))

        rw = int(max(1, w * res))
        rh = int(max(1, h * res))

        surface = self._generate_surface(rw, rh, time)

        ctx.save()
        # Translate to local position? No, local transform is handled by Scene.
        # But we must scale up the low-res surface to fill bounds.
        ctx.scale(1.0 / res, 1.0 / res)
        ctx.set_source_surface(surface, 0, 0)

        # Use bilinear filtering
        ctx.get_source().set_filter(cairo.FILTER_BILINEAR)
        ctx.paint()
        ctx.restore()

class AuroraGradientWave(Node):
    """
    Ethereal green/cyan/purple ribbon wave curtains that undulate across dark backdrops.
    """
    def __init__(
        self,
        width: float = 1920.0,
        height: float = 1080.0,
        color_stops: Sequence[ColorStop] = None,
        speed_multiplier: float = 1.0,
        resolution_scale: float = 0.5,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.width = Signal(width)
        self.height = Signal(height)

        if color_stops is None:
            self.colors = [
                Color.from_any("#050510"),
                Color.from_any("#0a2a20"),
                Color.from_any("#15a060"),
                Color.from_any("#00d0a0"),
                Color.from_any("#401080"),
            ]
        else:
            self.colors = [cs.color for cs in color_stops]

        self.speed_multiplier = Signal(speed_multiplier)
        self.resolution_scale = Signal(resolution_scale)

    def _generate_surface(self, w: int, h: int, time: float) -> cairo.ImageSurface:
        speed = self.speed_multiplier.get(time)
        t = time * speed

        x = np.linspace(0, 1, w)
        y = np.linspace(0, 1, h)
        xx, yy = np.meshgrid(x, y)

        # Sum of sines for wave curtains
        wave1 = np.sin(xx * 5.0 + t * 1.2) * 0.1
        wave2 = np.sin(xx * 13.0 - t * 0.8) * 0.05
        wave3 = np.cos(xx * 3.0 + yy * 2.0 + t * 0.5) * 0.15

        # Distortion field
        dist = yy + wave1 + wave2 + wave3

        # Map dist to color index
        # Let's do a simple gradient blend
        val = np.clip(dist * 2.0 - 0.5, 0.0, 1.0)

        r_out = np.zeros_like(val)
        g_out = np.zeros_like(val)
        b_out = np.zeros_like(val)

        n_colors = len(self.colors)
        if n_colors == 1:
            c = self.colors[0]
            r_out.fill(c.r)
            g_out.fill(c.g)
            b_out.fill(c.b)
        else:
            scaled_val = val * (n_colors - 1)
            idx0 = np.clip(np.floor(scaled_val).astype(int), 0, n_colors - 1)
            idx1 = np.clip(idx0 + 1, 0, n_colors - 1)
            frac = scaled_val - idx0

            for i in range(n_colors):
                mask0 = (idx0 == i)
                mask1 = (idx1 == i)
                c = self.colors[i]

                # Where idx0 is i, we add c * (1 - frac)
                r_out[mask0] += c.r * (1.0 - frac[mask0])
                g_out[mask0] += c.g * (1.0 - frac[mask0])
                b_out[mask0] += c.b * (1.0 - frac[mask0])

                # Where idx1 is i, we add c * frac
                r_out[mask1] += c.r * frac[mask1]
                g_out[mask1] += c.g * frac[mask1]
                b_out[mask1] += c.b * frac[mask1]

        bgra = np.zeros((h, w, 4), dtype=np.uint8)
        bgra[..., 0] = np.clip(b_out * 255, 0, 255).astype(np.uint8)
        bgra[..., 1] = np.clip(g_out * 255, 0, 255).astype(np.uint8)
        bgra[..., 2] = np.clip(r_out * 255, 0, 255).astype(np.uint8)
        bgra[..., 3] = 255

        return cairo.ImageSurface.create_for_data(bgra, cairo.FORMAT_ARGB32, w, h)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = max(1.0, self.width.get(time))
        h = max(1.0, self.height.get(time))
        res = max(0.01, min(1.0, self.resolution_scale.get(time)))

        rw = int(max(1, w * res))
        rh = int(max(1, h * res))

        surface = self._generate_surface(rw, rh, time)

        ctx.save()
        ctx.scale(1.0 / res, 1.0 / res)
        ctx.set_source_surface(surface, 0, 0)
        ctx.get_source().set_filter(cairo.FILTER_BILINEAR)
        ctx.paint()
        ctx.restore()

class LiquidPlasmaBackdrop(Node):
    """
    Animated Perlin/Simplex-style organic color plasma field.
    """
    def __init__(
        self,
        width: float = 1920.0,
        height: float = 1080.0,
        color_stops: Sequence[ColorStop] = None,
        speed_multiplier: float = 1.0,
        resolution_scale: float = 0.25,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.width = Signal(width)
        self.height = Signal(height)

        if color_stops is None:
            self.colors = [
                Color.from_any("#ff003c"),
                Color.from_any("#ff7a00"),
                Color.from_any("#ffe600"),
                Color.from_any("#00ff66"),
            ]
        else:
            self.colors = [cs.color for cs in color_stops]

        self.speed_multiplier = Signal(speed_multiplier)
        self.resolution_scale = Signal(resolution_scale)

    def _generate_surface(self, w: int, h: int, time: float) -> cairo.ImageSurface:
        speed = self.speed_multiplier.get(time)
        t = time * speed

        # Simple simulated plasma using interfering sines
        x = np.linspace(0, 10, w)
        y = np.linspace(0, 10, h)
        xx, yy = np.meshgrid(x, y)

        v1 = np.sin(xx + t)
        v2 = np.sin(yy - t)
        v3 = np.sin(xx + yy + t)
        v4 = np.sin(np.sqrt(xx**2 + yy**2) - t * 1.5)

        val = v1 + v2 + v3 + v4 # Range ~ -4 to 4
        # Normalize to 0-1
        val = (val + 4.0) / 8.0
        val = np.clip(val, 0.0, 1.0)

        r_out = np.zeros_like(val)
        g_out = np.zeros_like(val)
        b_out = np.zeros_like(val)

        n_colors = len(self.colors)
        if n_colors == 1:
            c = self.colors[0]
            r_out.fill(c.r)
            g_out.fill(c.g)
            b_out.fill(c.b)
        else:
            scaled_val = val * (n_colors - 1)
            idx0 = np.clip(np.floor(scaled_val).astype(int), 0, n_colors - 1)
            idx1 = np.clip(idx0 + 1, 0, n_colors - 1)
            frac = scaled_val - idx0

            for i in range(n_colors):
                mask0 = (idx0 == i)
                mask1 = (idx1 == i)
                c = self.colors[i]

                r_out[mask0] += c.r * (1.0 - frac[mask0])
                g_out[mask0] += c.g * (1.0 - frac[mask0])
                b_out[mask0] += c.b * (1.0 - frac[mask0])

                r_out[mask1] += c.r * frac[mask1]
                g_out[mask1] += c.g * frac[mask1]
                b_out[mask1] += c.b * frac[mask1]

        bgra = np.zeros((h, w, 4), dtype=np.uint8)
        bgra[..., 0] = np.clip(b_out * 255, 0, 255).astype(np.uint8)
        bgra[..., 1] = np.clip(g_out * 255, 0, 255).astype(np.uint8)
        bgra[..., 2] = np.clip(r_out * 255, 0, 255).astype(np.uint8)
        bgra[..., 3] = 255

        return cairo.ImageSurface.create_for_data(bgra, cairo.FORMAT_ARGB32, w, h)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = max(1.0, self.width.get(time))
        h = max(1.0, self.height.get(time))
        res = max(0.01, min(1.0, self.resolution_scale.get(time)))

        rw = int(max(1, w * res))
        rh = int(max(1, h * res))

        surface = self._generate_surface(rw, rh, time)

        ctx.save()
        ctx.scale(1.0 / res, 1.0 / res)
        ctx.set_source_surface(surface, 0, 0)
        ctx.get_source().set_filter(cairo.FILTER_BILINEAR)
        ctx.paint()
        ctx.restore()
