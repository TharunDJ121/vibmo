from __future__ import annotations
import math
import numpy as np
import cv2
from typing import Any, Optional

from vibmo.scene.node import Node
from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal
from vibmo.core.vector import Vector2D

class CyberGridHorizon(Node):
    """
    Perspective 3D ground plane with moving neon glowing grid lines scrolling toward the camera.
    """

    def __init__(
        self,
        name: str = "",
        width: int = 1920,
        height: int = 1080,
        grid_color: Color = colors.CYAN,
        grid_spacing: int = 80,
        line_thickness: float = 2.0,
        horizon_pitch: float = 0.6,
        scroll_speed: float = 1.0,
        glow_intensity: float = 0.5,
        fade_distance: float = 0.8,
        **kwargs: Any
    ) -> None:
        super().__init__(name=name, **kwargs)
        self.width = width
        self.height = height
        
        self.grid_color = Signal(Color.from_any(grid_color), f"{self.name}.grid_color")
        self.grid_spacing = Signal(float(grid_spacing), f"{self.name}.grid_spacing")
        self.line_thickness = Signal(float(line_thickness), f"{self.name}.line_thickness")
        self.horizon_pitch = Signal(float(horizon_pitch), f"{self.name}.horizon_pitch")
        self.scroll_speed = Signal(float(scroll_speed), f"{self.name}.scroll_speed")
        self.glow_intensity = Signal(float(glow_intensity), f"{self.name}.glow_intensity")
        self.fade_distance = Signal(float(fade_distance), f"{self.name}.fade_distance")

    def get_bounds(self) -> tuple[float, float, float, float]:
        return 0.0, 0.0, float(self.width), float(self.height)

    def render(self, time: float, render_ctx: Any) -> None:
        if not self.visible:
            return

        horizon_pitch = self.horizon_pitch(time)
        horizon_y = int(self.height * (1.0 - horizon_pitch))
        
        # Only render the ground plane portion
        ground_height = self.height - horizon_y
        if ground_height <= 0:
            return

        grid_color = self.grid_color(time)
        grid_spacing = max(10, int(self.grid_spacing(time)))
        line_thickness = max(0.5, self.line_thickness(time))
        scroll_speed = self.scroll_speed(time)
        glow_intensity = self.glow_intensity(time)
        fade_distance = max(0.0, min(1.0, self.fade_distance(time)))

        surface = render_ctx.get_surface(self.width, self.height)
        ctx = surface.context
        
        # We'll render a high-res flat grid then apply a perspective warp using cv2
        # To avoid aliasing, we draw it a bit larger
        flat_w = self.width * 2
        flat_h = ground_height * 4
        
        # Pre-allocate numpy array for the flat grid
        flat_grid = np.zeros((flat_h, flat_w, 4), dtype=np.uint8)
        
        # Draw vertical lines
        num_v_lines = flat_w // grid_spacing
        v_offset = (flat_w % grid_spacing) // 2
        for i in range(num_v_lines + 1):
            x = v_offset + i * grid_spacing
            cv2.line(flat_grid, (x, 0), (x, flat_h), (255, 255, 255, 255), int(line_thickness))
            
        # Draw horizontal lines with scrolling
        scroll_offset = (time * scroll_speed * 100.0) % grid_spacing
        num_h_lines = flat_h // grid_spacing + 2
        for i in range(num_h_lines):
            y = int(flat_h - (i * grid_spacing) + scroll_offset)
            if 0 <= y < flat_h:
                cv2.line(flat_grid, (0, y), (flat_w, y), (255, 255, 255, 255), int(line_thickness))
                
        # Define perspective transform
        src_pts = np.float32([
            [0, 0],
            [flat_w, 0],
            [flat_w, flat_h],
            [0, flat_h]
        ])
        
        # Taper the top edges to create perspective
        top_width = self.width * 0.1
        top_x1 = self.width / 2 - top_width / 2
        top_x2 = self.width / 2 + top_width / 2
        
        dst_pts = np.float32([
            [top_x1, 0],
            [top_x2, 0],
            [self.width * 1.5, ground_height],
            [-self.width * 0.5, ground_height]
        ])
        
        matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
        warped_grid = cv2.warpPerspective(flat_grid, matrix, (self.width, ground_height))
        
        # Create gradient mask for distance fading
        fade_mask = np.zeros((ground_height, self.width), dtype=np.float32)
        for y in range(ground_height):
            # 0.0 at top (horizon), 1.0 at bottom
            dist = y / ground_height
            # Apply fade based on fade_distance
            # If fade_distance is 0.8, the top 20% will fade out
            alpha = min(1.0, max(0.0, (dist - (1.0 - fade_distance)) / max(0.001, fade_distance)))
            fade_mask[y, :] = alpha
            
        # Apply mask and color
        r, g, b = int(grid_color.r * 255), int(grid_color.g * 255), int(grid_color.b * 255)
        warped_grid_colored = np.zeros_like(warped_grid)
        
        alpha_channel = (warped_grid[:, :, 3].astype(np.float32) / 255.0) * fade_mask
        
        warped_grid_colored[:, :, 0] = b  # OpenCV is BGR(A) but we'll convert to Cairo ARGB32
        warped_grid_colored[:, :, 1] = g
        warped_grid_colored[:, :, 2] = r
        warped_grid_colored[:, :, 3] = (alpha_channel * 255).astype(np.uint8)
        
        # Apply glow if needed
        if glow_intensity > 0:
            glow_size = int(line_thickness * 2 * glow_intensity)
            if glow_size % 2 == 0: glow_size += 1
            if glow_size >= 3:
                glow = cv2.GaussianBlur(warped_grid_colored, (glow_size, glow_size), 0)
                # Add glow to original
                alpha_glow = glow[:, :, 3].astype(np.float32) / 255.0
                alpha_orig = warped_grid_colored[:, :, 3].astype(np.float32) / 255.0
                
                alpha_out = alpha_orig + alpha_glow * (1 - alpha_orig) * 0.5
                
                # Simple additive blend for RGB where alpha exists
                for c in range(3):
                    c_orig = warped_grid_colored[:, :, c].astype(np.float32) * alpha_orig
                    c_glow = glow[:, :, c].astype(np.float32) * alpha_glow * glow_intensity
                    warped_grid_colored[:, :, c] = np.clip(c_orig + c_glow, 0, 255).astype(np.uint8)
                    
                warped_grid_colored[:, :, 3] = np.clip(alpha_out * 255, 0, 255).astype(np.uint8)

        # Draw the result onto the Cairo context
        import cairo
        
        # OpenCV uses BGRA, Cairo uses ARGB32 (which is BGRA in little-endian memory)
        # So we can just use the buffer
        stride = cairo.ImageSurface.format_stride_for_width(cairo.FORMAT_ARGB32, self.width)
        img_surface = cairo.ImageSurface.create_for_data(
            warped_grid_colored.data, cairo.FORMAT_ARGB32, self.width, ground_height, stride
        )
        
        ctx.save()
        ctx.translate(0, horizon_y)
        ctx.set_source_surface(img_surface, 0, 0)
        ctx.paint()
        ctx.restore()


class NeonSunBackdrop(Node):
    """
    Segmented Venetian-blind style sunset orb with animated horizontal stripe bars and radial corona glow.
    """

    def __init__(
        self,
        name: str = "",
        radius: float = 300.0,
        core_color: Color = colors.AMBER,
        edge_color: Color = colors.PINK,
        num_stripes: int = 6,
        stripe_speed: float = 0.5,
        glow_radius: float = 100.0,
        **kwargs: Any
    ) -> None:
        super().__init__(name=name, **kwargs)
        self.radius_val = Signal(float(radius), f"{self.name}.radius")
        self.core_color = Signal(Color.from_any(core_color), f"{self.name}.core_color")
        self.edge_color = Signal(Color.from_any(edge_color), f"{self.name}.edge_color")
        self.num_stripes = Signal(float(num_stripes), f"{self.name}.num_stripes")
        self.stripe_speed = Signal(float(stripe_speed), f"{self.name}.stripe_speed")
        self.glow_radius = Signal(float(glow_radius), f"{self.name}.glow_radius")

    def get_bounds(self) -> tuple[float, float, float, float]:
        r = float(self.radius_val(0.0)) + float(self.glow_radius(0.0))
        return -r, -r, r, r

    def render(self, time: float, render_ctx: Any) -> None:
        if not self.visible:
            return

        radius = self.radius_val(time)
        core_color = self.core_color(time)
        edge_color = self.edge_color(time)
        num_stripes = max(1, int(self.num_stripes(time)))
        stripe_speed = self.stripe_speed(time)
        glow_radius = self.glow_radius(time)

        surface = render_ctx.get_surface(int((radius + glow_radius) * 2), int((radius + glow_radius) * 2))
        ctx = surface.context
        
        # Center coordinates
        cx, cy = radius + glow_radius, radius + glow_radius
        
        # 1. Draw Corona Glow (radial gradient)
        if glow_radius > 0:
            import cairo
            pat_glow = cairo.RadialGradient(cx, cy, radius * 0.8, cx, cy, radius + glow_radius)
            # Edge color fading to transparent
            r, g, b, a = edge_color.to_cairo()
            pat_glow.add_color_stop_rgba(0, r, g, b, a * 0.6)
            pat_glow.add_color_stop_rgba(1, r, g, b, 0.0)
            
            ctx.arc(cx, cy, radius + glow_radius, 0, 2 * math.pi)
            ctx.set_source(pat_glow)
            ctx.fill()
            
        # 2. Draw Sun Base (linear gradient from top to bottom)
        import cairo
        pat_sun = cairo.LinearGradient(cx, cy - radius, cx, cy + radius)
        # Top is core color, bottom is edge color
        r1, g1, b1, a1 = core_color.to_cairo()
        r2, g2, b2, a2 = edge_color.to_cairo()
        
        pat_sun.add_color_stop_rgba(0, r1, g1, b1, a1)
        pat_sun.add_color_stop_rgba(1, r2, g2, b2, a2)
        
        # Draw the solid circle first
        ctx.arc(cx, cy, radius, 0, 2 * math.pi)
        ctx.set_source(pat_sun)
        ctx.fill()
        
        # 3. Cut out the stripes using DEST_OUT
        ctx.save()
        ctx.set_operator(cairo.OPERATOR_DEST_OUT)
        
        # Stripe logic:
        # Bottom half of the sun gets cut into horizontal stripes
        # They grow wider towards the bottom and move upwards
        
        time_offset = (time * stripe_speed) % 1.0
        
        # We define a few fixed stripe positions (y coordinates relative to bottom)
        # And their widths. The positions animate upwards.
        
        # We'll use a normalized y from 0 (equator) to 1 (bottom pole)
        for i in range(num_stripes + 2):  # +2 to handle wrap-around
            # Calculate base position
            base_pos = (i - time_offset) / num_stripes
            
            # Only consider bottom half (base_pos > 0)
            if 0 < base_pos < 1.0:
                # Calculate actual Y position on the circle
                # Non-linear spacing to make them wider at the bottom
                y_norm = base_pos ** 1.5
                y_pos = cy + y_norm * radius
                
                # Calculate stripe thickness based on position (thicker at bottom)
                # Max thickness at bottom is maybe 15% of radius
                thickness = radius * 0.15 * (y_norm ** 2 + 0.1)
                
                # Draw stripe rectangle across the entire width of the sun
                ctx.rectangle(cx - radius, y_pos - thickness / 2, radius * 2, thickness)
                ctx.fill()
                
        ctx.restore()
        

class WireframeMountainHorizon(Node):
    """
    Distant wireframe neon mountain terrain silhouettes undulating with low-frequency noise.
    """

    def __init__(
        self,
        name: str = "",
        width: int = 1920,
        height: int = 300,
        line_color: Color = colors.PINK,
        num_layers: int = 3,
        amplitude: float = 80.0,
        frequency: float = 0.005,
        scroll_speed: float = 50.0,
        line_thickness: float = 2.0,
        **kwargs: Any
    ) -> None:
        super().__init__(name=name, **kwargs)
        self.width = width
        self.height = height
        
        self.line_color = Signal(Color.from_any(line_color), f"{self.name}.line_color")
        self.num_layers = Signal(float(num_layers), f"{self.name}.num_layers")
        self.amplitude = Signal(float(amplitude), f"{self.name}.amplitude")
        self.frequency = Signal(float(frequency), f"{self.name}.frequency")
        self.scroll_speed = Signal(float(scroll_speed), f"{self.name}.scroll_speed")
        self.line_thickness = Signal(float(line_thickness), f"{self.name}.line_thickness")

    def get_bounds(self) -> tuple[float, float, float, float]:
        return 0.0, 0.0, float(self.width), float(self.height)

    def render(self, time: float, render_ctx: Any) -> None:
        if not self.visible:
            return

        line_color = self.line_color(time)
        num_layers = max(1, int(self.num_layers(time)))
        amplitude = self.amplitude(time)
        frequency = self.frequency(time)
        scroll_speed = self.scroll_speed(time)
        line_thickness = max(0.5, self.line_thickness(time))

        surface = render_ctx.get_surface(self.width, self.height)
        ctx = surface.context
        
        # Simple 1D Perlin noise equivalent using multiple sine waves
        def noise1d(x: float, seed: float) -> float:
            val = math.sin(x * 1.0 + seed) * 1.0
            val += math.sin(x * 2.1 + seed * 1.3) * 0.5
            val += math.sin(x * 4.3 + seed * 1.7) * 0.25
            return val / 1.75  # Normalize somewhat

        import cairo
        ctx.set_line_width(line_thickness)
        
        # Draw layers from back to front
        for layer in range(num_layers - 1, -1, -1):
            # Calculate parallax and scaling for this layer
            # Back layers move slower, are smaller, and darker
            depth_factor = (layer + 1) / num_layers  # 1.0 is front, smaller is back
            
            layer_amp = amplitude * depth_factor
            layer_freq = frequency * (2.0 - depth_factor)  # Back layers have higher frequency
            layer_scroll = time * scroll_speed * depth_factor
            layer_seed = layer * 100.0  # Offset seed for each layer
            
            # Base height for this layer (back layers are higher up to be visible)
            base_y = self.height - (self.height * 0.5 * depth_factor)
            
            # Set color (darken and fade back layers)
            r, g, b, a = line_color.to_cairo()
            layer_alpha = a * depth_factor
            
            ctx.set_source_rgba(r, g, b, layer_alpha)
            
            # Draw the mountain line
            ctx.move_to(0, self.height)
            
            step_size = max(5, self.width // 100)
            for x in range(0, self.width + step_size, step_size):
                # Calculate x position in world space
                world_x = x + layer_scroll
                
                # Generate noise value
                n = noise1d(world_x * layer_freq, layer_seed)
                
                # Mountain peaks should be sharp, valleys smooth
                # Use abs() to create sharp peaks
                n = 1.0 - abs(n)
                
                y = base_y - n * layer_amp
                ctx.line_to(x, y)
                
            ctx.line_to(self.width, self.height)
            ctx.close_path()
            
            # Fill with black to hide lines behind it
            ctx.save()
            ctx.set_source_rgba(0, 0, 0, 1.0)
            ctx.fill_preserve()
            ctx.restore()
            
            # Stroke the glowing line
            ctx.stroke()
            
            # Optional vertical wireframe lines down to base
            ctx.save()
            ctx.set_source_rgba(r, g, b, layer_alpha * 0.5)
            ctx.set_line_width(line_thickness * 0.5)
            
            for x in range(0, self.width + step_size, step_size * 4):
                world_x = x + layer_scroll
                n = 1.0 - abs(noise1d(world_x * layer_freq, layer_seed))
                y = base_y - n * layer_amp
                
                ctx.move_to(x, y)
                ctx.line_to(x, self.height)
                ctx.stroke()
                
            ctx.restore()
