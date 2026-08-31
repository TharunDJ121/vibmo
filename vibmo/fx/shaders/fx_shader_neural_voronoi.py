"""
✦ Vibmo Shaders: Neural Noise & Voronoi Cellular Grid Backdrops
Inspired by Remocn shader-neuro-noise & shader-voronoi with procedural high-speed vectorized synthesis.
"""

from __future__ import annotations

import numpy as np
import math
from typing import Any, List, Optional, Tuple, Union

try:
    from vibmo.scene.node import Node
except ImportError:
    class Node:
        pass


class ShaderNeuroNoise(Node):
    """
    Animated neural synapse network backdrop with pulsing synaptic filaments and glow nodes.
    """
    def __init__(
        self,
        speed: float = 0.8,
        complexity: int = 4,
        color_core: Tuple[int, int, int] = (14, 165, 233),   # Cyan/Sky
        color_edge: Tuple[int, int, int] = (99, 102, 241),  # Indigo
        density: float = 1.0,
        **kwargs: Any,
    ):
        super().__init__(**kwargs) if hasattr(super(), '__init__') else None
        self.speed = speed
        self.complexity = complexity
        self.color_core = np.array(color_core, dtype=np.float32)
        self.color_edge = np.array(color_edge, dtype=np.float32)
        self.density = density

    def render_frame(self, width: int, height: int, time: float = 0.0) -> np.ndarray:
        t = time * self.speed

        # Downsample for fast procedural synthesis then scale up
        scale_factor = 4
        sw, sh = max(1, width // scale_factor), max(1, height // scale_factor)

        x = np.linspace(-2.0, 2.0, sw, dtype=np.float32)
        y = np.linspace(-2.0, 2.0, sh, dtype=np.float32)
        xx, yy = np.meshgrid(x, y)

        r = np.sqrt(xx * xx + yy * yy)
        theta = np.arctan2(yy, xx)

        # Multi-octave neural pulse
        wave = np.sin(theta * 6.0 + np.sin(r * 4.0 - t * 2.0) * 2.0 + t)
        wave += 0.5 * np.cos(xx * 5.0 + np.sin(yy * 4.0 + t * 1.5))
        wave += 0.25 * np.sin((xx + yy) * 8.0 - t * 3.0)

        intensity = np.clip((wave + 1.75) / 3.5, 0.0, 1.0)
        intensity = np.power(intensity, 2.2) * self.density

        # Color ramp
        rgb = np.zeros((sh, sw, 3), dtype=np.float32)
        for c in range(3):
            rgb[:, :, c] = (
                self.color_edge[c] * (1.0 - intensity) +
                self.color_core[c] * intensity
            )

        # Darken deep background
        bg_factor = np.clip(intensity * 1.4, 0.05, 1.0)[:, :, None]
        rgb = rgb * bg_factor

        from PIL import Image
        pil_img = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))
        full_img = pil_img.resize((width, height), Image.Resampling.BILINEAR)

        out_rgba = np.zeros((height, width, 4), dtype=np.uint8)
        out_rgba[:, :, :3] = np.array(full_img)
        out_rgba[:, :, 3] = 255
        return out_rgba


class ShaderVoronoiGrid(Node):
    """
    Animated Voronoi cellular tessellation background with shifting nuclei and distance fields.
    """
    def __init__(
        self,
        num_cells: int = 16,
        speed: float = 0.6,
        cell_color: Tuple[int, int, int] = (16, 185, 129),  # Emerald
        edge_color: Tuple[int, int, int] = (15, 23, 42),   # Slate 900
        **kwargs: Any,
    ):
        super().__init__(**kwargs) if hasattr(super(), '__init__') else None
        self.num_cells = num_cells
        self.speed = speed
        self.cell_color = np.array(cell_color, dtype=np.float32)
        self.edge_color = np.array(edge_color, dtype=np.float32)

        # Pre-seed pseudo-random points and velocities
        np.random.seed(42)
        self.base_points = np.random.rand(self.num_cells, 2).astype(np.float32)
        self.frequencies = (np.random.rand(self.num_cells, 2) * 2.0 + 0.5).astype(np.float32)

    def render_frame(self, width: int, height: int, time: float = 0.0) -> np.ndarray:
        t = time * self.speed
        scale_factor = 4
        sw, sh = max(1, width // scale_factor), max(1, height // scale_factor)

        # Animate cell centers
        points = self.base_points.copy()
        for i in range(self.num_cells):
            points[i, 0] = (self.base_points[i, 0] + 0.15 * math.sin(t * self.frequencies[i, 0])) % 1.0
            points[i, 1] = (self.base_points[i, 1] + 0.15 * math.cos(t * self.frequencies[i, 1])) % 1.0

        grid_x, grid_y = np.meshgrid(np.linspace(0, 1, sw, dtype=np.float32),
                                     np.linspace(0, 1, sh, dtype=np.float32))

        # Compute minimum distance to any point (Euclidean)
        min_dist = np.full((sh, sw), 1e5, dtype=np.float32)
        sec_dist = np.full((sh, sw), 1e5, dtype=np.float32)

        for p in points:
            d = np.sqrt((grid_x - p[0]) ** 2 + (grid_y - p[1]) ** 2)
            mask = d < min_dist
            sec_dist = np.where(mask, min_dist, np.minimum(sec_dist, d))
            min_dist = np.minimum(min_dist, d)

        # Edge thickness
        edge_diff = sec_dist - min_dist
        edge_mask = np.clip(edge_diff * 12.0, 0.0, 1.0)[:, :, None]

        rgb = (self.edge_color * (1.0 - edge_mask) +
               self.cell_color * edge_mask * (1.0 - min_dist[:, :, None] * 2.0))

        from PIL import Image
        pil_img = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))
        full_img = pil_img.resize((width, height), Image.Resampling.BILINEAR)

        out_rgba = np.zeros((height, width, 4), dtype=np.uint8)
        out_rgba[:, :, :3] = np.array(full_img)
        out_rgba[:, :, 3] = 255
        return out_rgba
