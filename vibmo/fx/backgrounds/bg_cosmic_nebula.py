import math
import random
from typing import Any, List, Optional, Tuple, Union

from vibmo.core.color import Color, RadialGradient, colors
from vibmo.scene.node import Node

class CosmicNebulaBackdrop(Node):
    """
    Multi-layered volumetric cosmic interstellar gas clouds drifting and rotating
    with deep purple, magenta, and cyan hues.
    """
    def __init__(
        self,
        width: float = 1920.0,
        height: float = 1080.0,
        seed: int = 42,
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.width = width
        self.height = height

        # Pre-generate clouds
        random.seed(seed)
        self.clouds = []
        for _ in range(12):
            x = random.uniform(0, width)
            y = random.uniform(0, height)
            r = random.uniform(300, 800)

            # Deep purple, magenta, and cyan hues
            hue = random.choice([
                (0.66, 0.33, 0.98), # Purple
                (0.93, 0.28, 0.60), # Magenta
                (0.02, 0.71, 0.83), # Cyan
                (0.04, 0.05, 0.3)   # Deep Blue
            ])
            color = Color(hue[0], hue[1], hue[2], random.uniform(0.1, 0.4))

            phase_x = random.uniform(0, math.pi * 2)
            phase_y = random.uniform(0, math.pi * 2)
            speed_x = random.uniform(0.05, 0.15)
            speed_y = random.uniform(0.05, 0.15)
            rot_speed = random.uniform(-0.1, 0.1)

            self.clouds.append({
                "x": x,
                "y": y,
                "r": r,
                "color": color,
                "phase_x": phase_x,
                "phase_y": phase_y,
                "speed_x": speed_x,
                "speed_y": speed_y,
                "rot_speed": rot_speed
            })

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        if self.world_opacity(time) <= 0.01:
            return

        ctx.save()
        # Draw background color
        ctx.set_source_rgba(*colors.DARK_NAVY.to_cairo())
        ctx.rectangle(0, 0, self.width, self.height)
        ctx.fill()

        # Set additive blending for glowing effect
        has_cairo = False
        try:
            import cairo
            ctx.set_operator(cairo.Operator.ADD)
            has_cairo = True
        except ImportError:
            pass

        for cloud in self.clouds:
            cx = cloud["x"] + math.sin(time * cloud["speed_x"] + cloud["phase_x"]) * 100
            cy = cloud["y"] + math.cos(time * cloud["speed_y"] + cloud["phase_y"]) * 100

            radius = cloud["r"]
            color = cloud["color"]

            if has_cairo:
                pat = cairo.RadialGradient(cx, cy, 0, cx, cy, radius)
                pat.add_color_stop_rgba(0, color.r, color.g, color.b, color.a)
                pat.add_color_stop_rgba(1, color.r, color.g, color.b, 0.0)
                ctx.set_source(pat)
            else:
                ctx.set_source_rgba(color.r, color.g, color.b, color.a * 0.5)

            ctx.arc(cx, cy, radius, 0, 2 * math.pi)
            ctx.fill()

        ctx.restore()


class StarfieldWarpDrift(Node):
    """
    3D perspective stars accelerating and streaking outward from center with parallax depth layers.
    """
    def __init__(
        self,
        width: float = 1920.0,
        height: float = 1080.0,
        num_stars: int = 200,
        seed: int = 42,
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.width = width
        self.height = height

        random.seed(seed)
        self.stars = []
        for _ in range(num_stars):
            # 3D coordinates: x, y in [-1, 1], z in [0, 1]
            x = random.uniform(-1, 1)
            y = random.uniform(-1, 1)
            z = random.uniform(0.1, 1.0)
            self.stars.append([x, y, z])

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        if self.world_opacity(time) <= 0.01:
            return

        ctx.save()

        cx = self.width / 2.0
        cy = self.height / 2.0

        # Time-based acceleration / warp factor
        # t increases warp speed over time
        speed = 0.5
        z_offset = time * speed

        ctx.set_line_cap(1) # Round cap

        for i, star in enumerate(self.stars):
            x, y, z_orig = star

            # Move star towards camera
            z = z_orig - z_offset
            z = z % 1.0 # Wrap around
            if z <= 0.01:
                z = 0.99

            # Previous z for streaking
            z_prev = z + 0.05

            # Projection
            px = x / z * cx + cx
            py = y / z * cy + cy

            px_prev = x / z_prev * cx + cx
            py_prev = y / z_prev * cy + cy

            # Check bounds
            if 0 <= px <= self.width and 0 <= py <= self.height:
                # Opacity based on depth (closer = brighter)
                opacity = 1.0 - z
                ctx.set_source_rgba(1.0, 1.0, 1.0, opacity)
                ctx.set_line_width(2.0 * (1.0 - z))

                ctx.move_to(px_prev, py_prev)
                ctx.line_to(px, py)
                ctx.stroke()

        ctx.restore()


class ConstellationGrid(Node):
    """
    Drifting geometric stars connected by dynamic proximity-based glowing line segments.
    """
    def __init__(
        self,
        width: float = 1920.0,
        height: float = 1080.0,
        num_points: int = 50,
        max_distance: float = 150.0,
        seed: int = 42,
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.width = width
        self.height = height
        self.max_distance = max_distance

        random.seed(seed)
        self.points = []
        for _ in range(num_points):
            x = random.uniform(0, width)
            y = random.uniform(0, height)
            vx = random.uniform(-20, 20)
            vy = random.uniform(-20, 20)
            radius = random.uniform(1.0, 3.0)
            self.points.append({"x": x, "y": y, "vx": vx, "vy": vy, "r": radius})

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        if self.world_opacity(time) <= 0.01:
            return

        ctx.save()

        current_points = []
        for p in self.points:
            # Linear drift with wrap around
            x = (p["x"] + p["vx"] * time) % self.width
            y = (p["y"] + p["vy"] * time) % self.height
            current_points.append((x, y, p["r"]))

        # Draw connections
        ctx.set_line_width(1.0)
        for i in range(len(current_points)):
            x1, y1, r1 = current_points[i]
            for j in range(i + 1, len(current_points)):
                x2, y2, r2 = current_points[j]

                dist = math.hypot(x2 - x1, y2 - y1)
                if dist < self.max_distance:
                    alpha = 1.0 - (dist / self.max_distance)
                    ctx.set_source_rgba(0.5, 0.8, 1.0, alpha * 0.6)
                    ctx.move_to(x1, y1)
                    ctx.line_to(x2, y2)
                    ctx.stroke()

        # Draw points
        for x, y, r in current_points:
            ctx.set_source_rgba(1.0, 1.0, 1.0, 0.9)
            ctx.arc(x, y, r, 0, 2 * math.pi)
            ctx.fill()

        ctx.restore()
