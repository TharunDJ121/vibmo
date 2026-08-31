import math
from typing import Any, Optional, Tuple, Union
from vibmo.scene.node import Node
from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal

class HyperspaceWarpTunnel(Node):
    """
    Concentric rotating wireframe rings rushing towards camera creating an infinite fly-through wormhole effect.
    """
    def __init__(
        self,
        speed: float = 1.0,
        warp_speed: Optional[float] = None,
        rings: int = 20,
        tunnel_radius: float = 500.0,
        tunnel_depth: float = 2000.0,
        ring_color: Union[Color, str] = colors.CYAN,
        streak_color: Optional[Union[Color, str]] = None,
        thickness: float = 2.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        actual_speed = float(warp_speed if warp_speed is not None else speed)
        actual_color = streak_color if streak_color is not None else ring_color
        self.speed = Signal(actual_speed, f"{self.name}.speed")
        self.rings = rings
        self.tunnel_radius = Signal(float(tunnel_radius), f"{self.name}.tunnel_radius")
        self.tunnel_depth = Signal(float(tunnel_depth), f"{self.name}.tunnel_depth")
        self.ring_color = Signal(Color.from_any(actual_color), f"{self.name}.ring_color")
        self.thickness = Signal(float(thickness), f"{self.name}.thickness")

    @property
    def warp_speed(self) -> float:
        return float(self.speed.get(0.0))

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        speed = self.speed.get(time)
        radius = self.tunnel_radius.get(time)
        depth = self.tunnel_depth.get(time)
        color = self.ring_color.get(time)
        thickness = self.thickness.get(time)
        
        ctx.save()
        
        # We need a perspective projection for Z to scale
        # Simple projection: scale = focal_length / (focal_length + Z)
        # We assume focal_length = depth / 2 roughly, or just scale = 1 / (z/focal_length + 1)
        focal_length = 500.0
        
        z_offset = (time * speed * 500.0) % (depth / self.rings)
        
        for i in range(self.rings):
            # Calculate Z for this ring
            z = depth - (i * (depth / self.rings)) - z_offset
            
            if z <= -focal_length:
                # Keep it looping effectively
                z += depth
                
            if z <= -focal_length * 0.9:
                continue

            # Scale based on distance Z
            scale = focal_length / (focal_length + z)
            
            if scale <= 0:
                continue
                
            # Rotation can also vary by distance/time
            rotation = time * speed * 0.5 + i * 0.1
            
            ctx.save()
            ctx.scale(scale, scale)
            ctx.rotate(rotation)
            
            ctx.set_source_rgba(color.r, color.g, color.b, color.a * min(1.0, scale))
            ctx.set_line_width(thickness / scale) # Maintain line thickness
            
            ctx.new_path()
            ctx.arc(0, 0, radius, 0, 2.0 * math.pi)
            ctx.stroke()
            
            ctx.restore()

        ctx.restore()

class HexagonalSpeedTunnel(Node):
    """
    Sci-fi hexagonal corridor panels speeding past with neon edge trim.
    """
    def __init__(
        self,
        speed: float = 1.0,
        panels: int = 15,
        tunnel_radius: float = 600.0,
        tunnel_depth: float = 3000.0,
        edge_color: Union[Color, str] = colors.GREEN_500,
        thickness: float = 3.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.speed = Signal(float(speed), f"{self.name}.speed")
        self.panels = panels
        self.tunnel_radius = Signal(float(tunnel_radius), f"{self.name}.tunnel_radius")
        self.tunnel_depth = Signal(float(tunnel_depth), f"{self.name}.tunnel_depth")
        self.edge_color = Signal(Color.from_any(edge_color) if isinstance(edge_color, (str, Color)) else colors.GREEN_500, f"{self.name}.edge_color")
        self.thickness = Signal(float(thickness), f"{self.name}.thickness")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        speed = self.speed.get(time)
        radius = self.tunnel_radius.get(time)
        depth = self.tunnel_depth.get(time)
        color = self.edge_color.get(time)
        thickness = self.thickness.get(time)
        
        ctx.save()
        
        focal_length = 500.0
        panel_spacing = depth / self.panels
        z_offset = (time * speed * 800.0) % panel_spacing
        
        for i in range(self.panels):
            z = depth - (i * panel_spacing) - z_offset
            
            if z <= -focal_length * 0.9:
                continue

            scale = focal_length / (focal_length + z)
            if scale <= 0:
                continue
                
            rotation = time * speed * 0.2
            
            ctx.save()
            ctx.scale(scale, scale)
            ctx.rotate(rotation)
            
            # Opacity fades into distance
            opacity = color.a * min(1.0, max(0.0, 1.0 - (z / depth)))
            ctx.set_source_rgba(color.r, color.g, color.b, opacity)
            ctx.set_line_width(thickness / scale)
            
            ctx.new_path()
            for j in range(6):
                angle = j * (math.pi / 3)
                px = math.cos(angle) * radius
                py = math.sin(angle) * radius
                if j == 0:
                    ctx.move_to(px, py)
                else:
                    ctx.line_to(px, py)
            ctx.close_path()
            ctx.stroke()
            
            ctx.restore()

        # Draw connecting lines
        for j in range(6):
            angle = j * (math.pi / 3)
            ctx.new_path()
            for i in range(self.panels):
                z = depth - (i * panel_spacing) - z_offset
                if z <= -focal_length * 0.9:
                    continue
                scale = focal_length / (focal_length + z)
                if scale <= 0:
                    continue
                rotation = time * speed * 0.2
                
                # We need absolute projection coords here
                px = math.cos(angle + rotation) * radius * scale
                py = math.sin(angle + rotation) * radius * scale
                
                if i == 0:
                    ctx.move_to(px, py)
                else:
                    ctx.line_to(px, py)
            
            ctx.set_source_rgba(color.r, color.g, color.b, color.a * 0.5)
            ctx.set_line_width(thickness * 0.5)
            ctx.stroke()

        ctx.restore()


class InfiniteZoomVortex(Node):
    """
    Spiral logarithmic vortex rotating and drawing the eye inward toward a center event horizon.
    """
    def __init__(
        self,
        speed: float = 1.0,
        arms: int = 5,
        twists: float = 4.0,
        vortex_color: Union[Color, str] = colors.PURPLE,
        thickness: float = 2.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.speed = Signal(float(speed), f"{self.name}.speed")
        self.arms = arms
        self.twists = Signal(float(twists), f"{self.name}.twists")
        self.vortex_color = Signal(Color.from_any(vortex_color) if isinstance(vortex_color, (str, Color)) else colors.PURPLE, f"{self.name}.vortex_color")
        self.thickness = Signal(float(thickness), f"{self.name}.thickness")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        speed = self.speed.get(time)
        twists = self.twists.get(time)
        color = self.vortex_color.get(time)
        thickness = self.thickness.get(time)
        
        ctx.save()
        
        rotation_offset = time * speed * 2.0
        zoom_offset = (time * speed) % 1.0 # This handles the zoom aspect continuously
        
        ctx.set_source_rgba(color.r, color.g, color.b, color.a)
        
        for i in range(self.arms):
            arm_angle_offset = i * (2.0 * math.pi / self.arms)
            
            ctx.new_path()
            
            steps = 200
            for j in range(steps):
                # t goes from 0.01 (center) to 1.0 (edge)
                t = (j + 1) / steps
                
                # Apply zoom effect continuously by shifting t logarithmically
                # We want continuous zoom, so scale t by zoom_offset logarithmically
                # r = a * e^(b * theta)
                # Let's map t to a distance exponentially.
                
                # Let distance go from a small value to large
                dist = math.exp((t + zoom_offset) * 6.0) * 0.1
                
                # Angle twists as we go out
                angle = arm_angle_offset + rotation_offset + t * twists * 2.0 * math.pi
                
                px = math.cos(angle) * dist
                py = math.sin(angle) * dist
                
                if j == 0:
                    ctx.move_to(px, py)
                else:
                    ctx.line_to(px, py)
                    
            ctx.set_line_width(thickness)
            ctx.stroke()
            
        ctx.restore()


# Semantic Alias
HyperspaceTunnel = HyperspaceWarpTunnel

__all__ = [
    "HyperspaceWarpTunnel",
    "HyperspaceTunnel",
    "HexagonalSpeedTunnel",
    "InfiniteZoomVortex",
]
