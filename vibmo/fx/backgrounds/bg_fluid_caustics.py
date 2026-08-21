from __future__ import annotations
import math
import numpy as np
from typing import Any, Union
import cairo
from PIL import Image
from scipy.ndimage import zoom

from vibmo.core.color import Color, colors
from vibmo.scene.node import Node

class FluidWaterCaustics(Node):
    def __init__(self, width: float = 1920.0, height: float = 1080.0, speed: float = 1.0, scale: float = 1.0, color: Union[Color, str] = colors.CYAN, **kwargs: Any):
        super().__init__(**kwargs)
        self.w = float(width)
        self.h = float(height)
        self.speed = float(speed)
        self.scale = float(scale)
        self.base_color = Color.from_any(color) if isinstance(color, (str, Color)) else colors.CYAN

    def local_bounds(self, time: float = 0.0) -> tuple[float, float, float, float]:
        return (0.0, 0.0, self.w, self.h)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        grid_w, grid_h = max(32, int(self.w / 10 / self.scale)), max(32, int(self.h / 10 / self.scale))
        
        # Smooth animated Voronoi approximation via multiple shifting cellular sine waves
        y, x = np.ogrid[0:grid_h, 0:grid_w]
        x = x.astype(float) / grid_w * 4.0 * math.pi
        y = y.astype(float) / grid_h * 4.0 * math.pi
        
        t = time * self.speed
        
        # 3 interfering directional cellular patterns
        v1 = np.sin(x + t) * np.cos(y - t * 0.5)
        v2 = np.sin(x * 1.5 - t * 1.2 + y) * np.cos(y * 1.5 + t)
        v3 = np.sin(x * 0.5 + y * 2.0 + t * 0.8)
        
        voronoi = np.abs(v1 + v2 + v3) / 3.0
        
        voronoi = zoom(voronoi, (self.h / grid_h, self.w / grid_w), order=1)[:int(self.h), :int(self.w)]
        voronoi = (voronoi - voronoi.min()) / (voronoi.max() - voronoi.min() + 1e-5)
        
        # Sharp caustics lines
        caustics_alpha_f = np.power(1.0 - voronoi, 5.0)
        caustics_alpha = (caustics_alpha_f * 255.0).astype(np.uint8)
        
        arr = np.zeros((int(self.h), int(self.w), 4), dtype=np.uint8)
        
        # Pre-multiply RGB with alpha for Cairo
        r = int(self.base_color.r * 255)
        g = int(self.base_color.g * 255)
        b = int(self.base_color.b * 255)
        
        arr[..., 0] = (r * caustics_alpha_f).astype(np.uint8)
        arr[..., 1] = (g * caustics_alpha_f).astype(np.uint8)
        arr[..., 2] = (b * caustics_alpha_f).astype(np.uint8)
        arr[..., 3] = caustics_alpha
        
        img = Image.fromarray(arr, "RGBA")
        
        ctx.save()
        surface = cairo.ImageSurface.create_for_data(bytearray(img.tobytes("raw", "BGRA")), cairo.FORMAT_ARGB32, int(self.w), int(self.h))
        ctx.set_source_surface(surface, 0, 0)
        ctx.paint()
        ctx.restore()

class UnderwaterLightRays(Node):
    def __init__(self, width: float = 1920.0, height: float = 1080.0, speed: float = 1.0, intensity: float = 0.5, **kwargs: Any):
        super().__init__(**kwargs)
        self.w = float(width)
        self.h = float(height)
        self.speed = float(speed)
        self.intensity = float(intensity)

    def local_bounds(self, time: float = 0.0) -> tuple[float, float, float, float]:
        return (0.0, 0.0, self.w, self.h)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        ctx.set_operator(cairo.OPERATOR_ADD)
        
        num_rays = 15
        rng = np.random.RandomState(42)  # Deterministic seed for ray placement
        
        for i in range(num_rays):
            base_x = rng.uniform(0, self.w)
            top_width = rng.uniform(20, 150)
            bottom_width = top_width * rng.uniform(1.5, 3.0)
            
            # Animate sway
            sway_speed = rng.uniform(0.5, 1.5) * self.speed
            sway_amount = rng.uniform(30, 150)
            current_sway = math.sin(time * sway_speed + i) * sway_amount
            
            top_left = base_x - top_width / 2 + current_sway * 0.2
            top_right = base_x + top_width / 2 + current_sway * 0.2
            bottom_left = base_x - bottom_width / 2 + current_sway
            bottom_right = base_x + bottom_width / 2 + current_sway
            
            pat = cairo.LinearGradient(0, 0, 0, self.h)
            opacity = rng.uniform(0.1, 0.4) * self.intensity
            pat.add_color_stop_rgba(0, 1.0, 1.0, 1.0, opacity)
            pat.add_color_stop_rgba(1, 1.0, 1.0, 1.0, 0.0)
            
            ctx.move_to(top_left, 0)
            ctx.line_to(top_right, 0)
            ctx.line_to(bottom_right, self.h)
            ctx.line_to(bottom_left, self.h)
            ctx.close_path()
            
            ctx.set_source(pat)
            ctx.fill()
            
        ctx.restore()

class PrismaticIridescentWaves(Node):
    def __init__(self, width: float = 1920.0, height: float = 1080.0, speed: float = 1.0, scale: float = 1.0, **kwargs: Any):
        super().__init__(**kwargs)
        self.w = float(width)
        self.h = float(height)
        self.speed = float(speed)
        self.scale = float(scale)

    def local_bounds(self, time: float = 0.0) -> tuple[float, float, float, float]:
        return (0.0, 0.0, self.w, self.h)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        grid_w, grid_h = max(16, int(self.w / 20 / self.scale)), max(16, int(self.h / 20 / self.scale))
        y, x = np.ogrid[0:grid_h, 0:grid_w]
        
        x = x.astype(float) / grid_w
        y = y.astype(float) / grid_h
        
        t = time * self.speed
        
        # Overlapping sine waves
        v = np.sin(x * 10 + t) + np.sin(y * 8 - t * 0.8) + np.sin((x + y) * 12 + t * 1.2)
        v = (v + 3.0) / 6.0 # Normalize 0-1
        
        arr = np.zeros((grid_h, grid_w, 4), dtype=np.uint8)
        
        # Cosine palette for iridescence
        # Pre-multiply since Alpha is always 255 anyway here
        arr[..., 0] = (np.clip(0.5 + 0.5 * np.cos(6.28318 * (1.0 * v + 0.0)), 0, 1) * 255).astype(np.uint8)
        arr[..., 1] = (np.clip(0.5 + 0.5 * np.cos(6.28318 * (1.0 * v + 0.33)), 0, 1) * 255).astype(np.uint8)
        arr[..., 2] = (np.clip(0.5 + 0.5 * np.cos(6.28318 * (1.0 * v + 0.67)), 0, 1) * 255).astype(np.uint8)
        arr[..., 3] = 255
        
        # Upscale
        arr_up = np.zeros((int(self.h), int(self.w), 4), dtype=np.uint8)
        for i in range(4):
            arr_up[..., i] = zoom(arr[..., i], (self.h / grid_h, self.w / grid_w), order=1)[:int(self.h), :int(self.w)]
        
        img = Image.fromarray(arr_up, "RGBA")
        
        ctx.save()
        surface = cairo.ImageSurface.create_for_data(bytearray(img.tobytes("raw", "BGRA")), cairo.FORMAT_ARGB32, int(self.w), int(self.h))
        ctx.set_source_surface(surface, 0, 0)
        ctx.paint()
        ctx.restore()
