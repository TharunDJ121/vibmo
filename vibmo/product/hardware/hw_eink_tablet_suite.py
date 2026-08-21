import math
from typing import Any
import random
import numpy as np

from vibmo.scene.node import Node
from vibmo.core.vector import Vector2D
from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal

class PaperEInkReaderFrame(Node):
    """
    ReMarkable / Kindle Scribe style paper-like e-ink digital notepad.
    Features a wide left leather grip bezel and a textured white screen.
    """
    def __init__(self, width: float = 600.0, height: float = 800.0, **kwargs):
        super().__init__(**kwargs)
        self.width = width
        self.height = height

        # Dimensions
        self.corner_radius = 16.0
        self.grip_width = 80.0
        self.bezel_width = 12.0

        # Inner screen dimensions
        self.screen_x = self.grip_width
        self.screen_y = self.bezel_width
        self.screen_width = self.width - self.grip_width - self.bezel_width
        self.screen_height = self.height - (2 * self.bezel_width)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        """Render the e-ink tablet frame."""
        ctx.save()

        w, h = self.width, self.height
        r = self.corner_radius

        # 1. Outer Chassis / Bezel Background (Dark Leather-like gray/black)
        chassis_color = Color.hex("#2C2C2E")
        ctx.set_source_rgba(chassis_color.r, chassis_color.g, chassis_color.b, self.world_opacity(time))

        # Rounded rectangle for the main body
        ctx.new_path()
        ctx.arc(r, r, r, math.pi, 1.5 * math.pi)
        ctx.arc(w - r, r, r, 1.5 * math.pi, 2 * math.pi)
        ctx.arc(w - r, h - r, r, 0, 0.5 * math.pi)
        ctx.arc(r, h - r, r, 0.5 * math.pi, math.pi)
        ctx.close_path()
        ctx.fill()

        # 2. Leather Grip detail (left side)
        # Adding some subtle lines/texture indicator for the grip
        ctx.set_source_rgba(0.0, 0.0, 0.0, 0.2 * self.world_opacity(time))
        for i in range(5):
            y_pos = (h / 6) * (i + 1)
            ctx.move_to(self.grip_width * 0.2, y_pos)
            ctx.line_to(self.grip_width * 0.8, y_pos)
            ctx.set_line_width(1.5)
            ctx.stroke()

        # 3. Inner Screen Area (Paper-like white)
        screen_bg = Color.hex("#F2F2F2")  # slightly off-white for e-ink paper feel
        ctx.set_source_rgba(screen_bg.r, screen_bg.g, screen_bg.b, self.world_opacity(time))

        sx, sy, sw, sh = self.screen_x, self.screen_y, self.screen_width, self.screen_height
        sr = 4.0 # smaller corner radius for screen
        ctx.new_path()
        ctx.arc(sx + sr, sy + sr, sr, math.pi, 1.5 * math.pi)
        ctx.arc(sx + sw - sr, sy + sr, sr, 1.5 * math.pi, 2 * math.pi)
        ctx.arc(sx + sw - sr, sy + sh - sr, sr, 0, 0.5 * math.pi)
        ctx.arc(sx + sr, sy + sh - sr, sr, 0.5 * math.pi, math.pi)
        ctx.close_path()
        ctx.fill()

        # Screen inner shadow / depth
        ctx.set_source_rgba(0.0, 0.0, 0.0, 0.1 * self.world_opacity(time))
        ctx.set_line_width(2.0)
        ctx.stroke()

        ctx.restore()

    def local_bounds(self, time: float = 0.0) -> tuple[float, float, float, float]:
        return (0.0, 0.0, self.width, self.height)


class StylusPenMockup(Node):
    """
    Precision digital stylus pen magnetically docked to side bezel.
    """
    def __init__(self, length: float = 140.0, radius: float = 4.0, **kwargs):
        super().__init__(**kwargs)
        self.length = length
        self.radius = radius
        # Default styling
        self.body_color = Color.hex("#E5E5EA")
        self.tip_color = Color.hex("#3A3A3C")
        self.accent_color = Color.hex("#C7C7CC")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        """Render the stylus pen."""
        ctx.save()

        l, r = self.length, self.radius
        op = self.world_opacity(time)

        # Draw vertically by default, tip at the bottom (y=l)

        # 1. Main cylindrical body
        ctx.set_source_rgba(self.body_color.r, self.body_color.g, self.body_color.b, op)
        ctx.new_path()
        # Top rounded end
        ctx.arc(r, r, r, math.pi, 0)
        # Right edge
        ctx.line_to(2*r, l - 15.0)
        # Left edge
        ctx.line_to(0, l - 15.0)
        ctx.close_path()
        ctx.fill()

        # Add subtle highlight for cylinder 3D effect
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.5 * op)
        ctx.move_to(r * 0.5, r)
        ctx.line_to(r * 0.5, l - 15.0)
        ctx.set_line_width(r * 0.8)
        ctx.stroke()

        # 2. Pen tip cone
        ctx.set_source_rgba(self.tip_color.r, self.tip_color.g, self.tip_color.b, op)
        ctx.move_to(0, l - 15.0)
        ctx.line_to(2*r, l - 15.0)
        ctx.line_to(r + 0.5, l - 2.0)
        ctx.line_to(r - 0.5, l - 2.0)
        ctx.close_path()
        ctx.fill()

        # 3. Fine nib
        ctx.set_source_rgba(0.1, 0.1, 0.1, op)
        ctx.move_to(r - 0.5, l - 2.0)
        ctx.line_to(r + 0.5, l - 2.0)
        ctx.line_to(r + 0.2, l)
        ctx.line_to(r - 0.2, l)
        ctx.close_path()
        ctx.fill()

        # 4. Magnetic flat side / accent band
        ctx.set_source_rgba(self.accent_color.r, self.accent_color.g, self.accent_color.b, op)
        ctx.move_to(0, r * 3)
        ctx.line_to(2*r, r * 3)
        ctx.set_line_width(2.0)
        ctx.stroke()

        ctx.restore()

    def local_bounds(self, time: float = 0.0) -> tuple[float, float, float, float]:
        return (0.0, 0.0, self.radius * 2, self.length)


class TextureMatteScreenBezel(Node):
    """
    Subtle paper tooth grain texture and low-contrast e-ink refresh artifact simulator.
    """
    def __init__(self, width: float, height: float, **kwargs):
        super().__init__(**kwargs)
        self.width = width
        self.height = height
        self.refresh_progress = Signal(0.0) # 0.0 to 1.0
        self.base_color = Color.hex("#F2F2F2")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        """Render the matte texture and refresh artifacts."""
        ctx.save()
        op = self.world_opacity(time)

        # Create a paper tooth grain texture using noise
        # For Cairo, we can approximate this with many small translucent dots or a pattern,
        # but to keep it lightweight, we'll draw semi-transparent random lines/dots
        # using a fixed seed to prevent flickering across frames unless refreshing.

        rng = random.Random(42) # fixed seed for static texture

        # Base paper color
        ctx.set_source_rgba(self.base_color.r, self.base_color.g, self.base_color.b, op)
        ctx.rectangle(0, 0, self.width, self.height)
        ctx.fill()

        # Subtle noise grain
        ctx.set_source_rgba(0.0, 0.0, 0.0, 0.02 * op)
        ctx.set_line_width(1.0)

        # Drawing a simplified mesh/grain to avoid excessive overhead
        # In a real app this would be a cached image surface pattern
        step = 4.0
        for y in np.arange(0, self.height, step):
            for x in np.arange(0, self.width, step):
                if rng.random() > 0.5:
                    ctx.rectangle(x, y, 1, 1)
        ctx.fill()

        # E-ink refresh artifact simulator
        refresh = self.refresh_progress.get(time)
        if refresh > 0.0 and refresh < 1.0:
            # When refreshing, e-ink flashes black/negative then settles
            if refresh < 0.3:
                # Black flash phase
                intensity = refresh / 0.3
                ctx.set_source_rgba(0.1, 0.1, 0.1, intensity * 0.8 * op)
                ctx.rectangle(0, 0, self.width, self.height)
                ctx.fill()
            elif refresh < 0.6:
                # White flash phase
                intensity = (refresh - 0.3) / 0.3
                ctx.set_source_rgba(0.95, 0.95, 0.95, intensity * 0.9 * op)
                ctx.rectangle(0, 0, self.width, self.height)
                ctx.fill()
            else:
                # Settling with some ghosting artifacts
                intensity = 1.0 - ((refresh - 0.6) / 0.4)
                ctx.set_source_rgba(0.0, 0.0, 0.0, intensity * 0.1 * op)

                # Draw random horizontal bands as ghosting artifacts
                rng = random.Random(int(time * 10)) # Seed changes with time during this phase
                for _ in range(5):
                    gy = rng.uniform(0, self.height)
                    gh = rng.uniform(10, 50)
                    ctx.rectangle(0, gy, self.width, gh)
                ctx.fill()

        # Restore random seed state
        ctx.restore()

    def local_bounds(self, time: float = 0.0) -> tuple[float, float, float, float]:
        return (0.0, 0.0, self.width, self.height)
