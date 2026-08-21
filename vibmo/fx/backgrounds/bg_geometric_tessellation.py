from __future__ import annotations
import math
import cmath
from typing import Any, List, Optional, Sequence, Tuple, Union
import numpy as np

from vibmo.core.vector import Vector2D
from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal
from vibmo.scene.node import Node
from scipy.spatial import Voronoi

class VoronoiCellEvolution(Node):
    """
    Real-time evolving 2D Voronoi cellular diagram with undulating cell seed points and glowing borders.
    """
    def __init__(
        self,
        width: float = 1920.0,
        height: float = 1080.0,
        num_cells: int = 20,
        speed: float = 1.0,
        border_color: Union[Color, str] = colors.CYAN,
        fill_color: Union[Color, str] = colors.CYAN.with_alpha(0.1),
        border_width: float = 2.0,
        seed: int = 42,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.width = width
        self.height = height
        self.num_cells = num_cells
        self.speed = speed
        self.border_color = Color.from_any(border_color) if isinstance(border_color, (str, Color)) else border_color
        self.fill_color = Color.from_any(fill_color) if isinstance(fill_color, (str, Color)) else fill_color
        self.border_width = border_width
        self.seed = seed
        
        # Initialize random base points
        rng = np.random.default_rng(self.seed)
        self.base_points = rng.random((self.num_cells, 2)) * [self.width, self.height]
        # Random phase and frequency for undulating
        self.phases = rng.random((self.num_cells, 2)) * 2 * math.pi
        self.freqs = rng.random((self.num_cells, 2)) * 0.5 + 0.5
        # Add boundary points to ensure closed voronoi cells in the middle
        self.boundary_points = np.array([
            [-self.width, -self.height],
            [-self.width, 2*self.height],
            [2*self.width, -self.height],
            [2*self.width, 2*self.height],
            [self.width/2, -self.height],
            [self.width/2, 2*self.height],
            [-self.width, self.height/2],
            [2*self.width, self.height/2]
        ])

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        # Calculate current points based on time
        t = time * self.speed
        offsets = np.sin(t * self.freqs + self.phases) * 50.0  # Undulation amplitude
        current_points = self.base_points + offsets
        
        # Combine with boundary points
        all_points = np.vstack([current_points, self.boundary_points])
        
        try:
            vor = Voronoi(all_points)
        except Exception:
            return

        ctx.save()
        # Draw cells
        for region_index in vor.point_region[:self.num_cells]:
            region = vor.regions[region_index]
            if not region or -1 in region:
                continue
            
            polygon = [vor.vertices[i] for i in region]
            if len(polygon) < 3:
                continue
                
            ctx.new_path()
            ctx.move_to(polygon[0][0], polygon[0][1])
            for p in polygon[1:]:
                ctx.line_to(p[0], p[1])
            ctx.close_path()
            
            # Fill
            ctx.set_source_rgba(self.fill_color.r, self.fill_color.g, self.fill_color.b, self.fill_color.a)
            ctx.fill_preserve()
            
            # Border (glow is simulated by setting color and width)
            ctx.set_source_rgba(self.border_color.r, self.border_color.g, self.border_color.b, self.border_color.a)
            ctx.set_line_width(self.border_width)
            ctx.stroke()
        ctx.restore()


class PenroseTilingFlow(Node):
    """
    Aperiodic Penrose tile patterns morphing with non-repeating rotational symmetry.
    Uses Robinson triangles decomposition.
    """
    def __init__(
        self,
        width: float = 1920.0,
        height: float = 1080.0,
        generations: int = 5,
        speed: float = 1.0,
        color1: Union[Color, str] = colors.PURPLE.with_alpha(0.5),
        color2: Union[Color, str] = colors.ORANGE.with_alpha(0.5),
        border_color: Union[Color, str] = colors.WHITE.with_alpha(0.2),
        border_width: float = 1.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.width = width
        self.height = height
        self.generations = generations
        self.speed = speed
        self.color1 = Color.from_any(color1) if isinstance(color1, (str, Color)) else color1
        self.color2 = Color.from_any(color2) if isinstance(color2, (str, Color)) else color2
        self.border_color = Color.from_any(border_color) if isinstance(border_color, (str, Color)) else border_color
        self.border_width = border_width
        self.golden_ratio = (1 + math.sqrt(5)) / 2

    def subdivide(self, triangles: List[Tuple[int, complex, complex, complex]]) -> List[Tuple[int, complex, complex, complex]]:
        result = []
        for color, A, B, C in triangles:
            if color == 0:
                # Half-kite
                P = A + (B - A) / self.golden_ratio
                result.append((0, C, P, B))
                result.append((1, P, C, A))
            else:
                # Half-dart
                Q = B + (A - B) / self.golden_ratio
                R = B + (C - B) / self.golden_ratio
                result.append((1, R, C, A))
                result.append((1, Q, R, B))
                result.append((0, R, Q, A))
        return result

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        t = time * self.speed
        
        # Initial sun configuration
        triangles = []
        for i in range(10):
            B = complex(self.width/2, self.height/2)
            # Rotating base slightly based on time
            r = min(self.width, self.height) / 2
            angle1 = (2 * i - 1) * math.pi / 10 + t
            angle2 = (2 * i + 1) * math.pi / 10 + t
            A = B + cmath.rect(r, angle1)
            C = B + cmath.rect(r, angle2)
            if i % 2 == 0:
                B, C = C, B  # Mirror every other triangle
            triangles.append((0, A, B, C))

        # Subdivide
        for _ in range(self.generations):
            triangles = self.subdivide(triangles)

        ctx.save()
        for color, A, B, C in triangles:
            ctx.new_path()
            ctx.move_to(A.real, A.imag)
            ctx.line_to(B.real, B.imag)
            ctx.line_to(C.real, C.imag)
            ctx.close_path()

            fill_c = self.color1 if color == 0 else self.color2
            # Morphing aspect by oscillating alpha based on distance from center
            dist = abs((A.real - self.width/2) + 1j*(A.imag - self.height/2))
            alpha_mod = 0.5 + 0.5 * math.sin(dist / 100.0 - t * 2.0)
            
            ctx.set_source_rgba(fill_c.r, fill_c.g, fill_c.b, fill_c.a * alpha_mod)
            ctx.fill_preserve()
            
            ctx.set_source_rgba(self.border_color.r, self.border_color.g, self.border_color.b, self.border_color.a)
            ctx.set_line_width(self.border_width)
            ctx.stroke()
        ctx.restore()


class HexagonalHoneyGridPulse(Node):
    """
    Hexagonal honeycomb lattice with breathing radial color waves rippling outward.
    """
    def __init__(
        self,
        width: float = 1920.0,
        height: float = 1080.0,
        hex_radius: float = 30.0,
        speed: float = 1.0,
        base_color: Union[Color, str] = colors.DARK_NAVY,
        pulse_color: Union[Color, str] = colors.EMERALD,
        border_color: Union[Color, str] = colors.WHITE.with_alpha(0.1),
        border_width: float = 1.5,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.width = width
        self.height = height
        self.hex_radius = hex_radius
        self.speed = speed
        self.base_color = Color.from_any(base_color) if isinstance(base_color, (str, Color)) else base_color
        self.pulse_color = Color.from_any(pulse_color) if isinstance(pulse_color, (str, Color)) else pulse_color
        self.border_color = Color.from_any(border_color) if isinstance(border_color, (str, Color)) else border_color
        self.border_width = border_width
        
        self.hex_width = math.sqrt(3) * self.hex_radius
        self.hex_height = 2 * self.hex_radius

    def draw_hexagon(self, ctx: Any, cx: float, cy: float, radius: float) -> None:
        ctx.new_path()
        for i in range(6):
            angle = math.pi / 3 * i - math.pi / 6 # Pointy topped
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            if i == 0:
                ctx.move_to(x, y)
            else:
                ctx.line_to(x, y)
        ctx.close_path()

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        t = time * self.speed
        
        cx_center = self.width / 2
        cy_center = self.height / 2
        
        cols = int(self.width / self.hex_width) + 2
        rows = int(self.height / (self.hex_height * 0.75)) + 2
        
        ctx.save()
        for row in range(-1, rows):
            for col in range(-1, cols):
                cx = col * self.hex_width
                if row % 2 == 1:
                    cx += self.hex_width / 2
                cy = row * self.hex_height * 0.75
                
                dist = math.hypot(cx - cx_center, cy - cy_center)
                
                # Breathing radial wave formula
                wave_val = 0.5 + 0.5 * math.sin(dist / 100.0 - t * 3.0)
                
                # Interpolate color
                r = self.base_color.r + (self.pulse_color.r - self.base_color.r) * wave_val
                g = self.base_color.g + (self.pulse_color.g - self.base_color.g) * wave_val
                b = self.base_color.b + (self.pulse_color.b - self.base_color.b) * wave_val
                a = self.base_color.a + (self.pulse_color.a - self.base_color.a) * wave_val
                
                self.draw_hexagon(ctx, cx, cy, self.hex_radius * 0.95) # Slight gap
                ctx.set_source_rgba(r, g, b, a)
                ctx.fill_preserve()
                
                ctx.set_source_rgba(self.border_color.r, self.border_color.g, self.border_color.b, self.border_color.a)
                ctx.set_line_width(self.border_width)
                ctx.stroke()
        ctx.restore()
