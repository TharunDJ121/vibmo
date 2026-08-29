import math
import random
from typing import Any, List, Optional, Tuple

import cairo

from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease
from vibmo.scene.node import Node
from vibmo.typography.text import Text

class BallastFlickerFailure(Node):
    """
    Intermittent realistic ballast ignition flicker sequence
    (quick double-blink, pause, buzz on).
    Used as an overlay/effect node or signal generator.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.progress = Signal(0.0, f"{self.name}.progress")

    def get_flicker_intensity(self, time: float) -> float:
        """
        Returns intensity between 0 and 1 representing the flicker state
        based on the progress signal (0.0 to 1.0).
        """
        prog = self.progress.get(time)
        if prog <= 0.0:
            return 0.0
        if prog >= 1.0:
            return 1.0

        # Pattern: quick double blink, pause, longer flicker, buzz on.
        # We can map progress to a sequence of intervals.
        if prog < 0.1:
            return 1.0
        elif prog < 0.15:
            return 0.0
        elif prog < 0.25:
            return 1.0
        elif prog < 0.4:
            return 0.0
        elif prog < 0.45:
            return 1.0
        elif prog < 0.5:
            return 0.0
        elif prog < 0.7:
            # high frequency random flicker
            # seed based on prog to be somewhat deterministic for testing if needed
            rnd = random.Random(int(prog * 100))
            return rnd.choice([0.0, 1.0, 0.5])
        else:
            return 1.0

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        # This node doesn't render anything itself, it provides the flicker signal
        # Alternatively, it could render a dark overlay if it were covering the sign,
        # but typical usage is to feed its intensity into the neon sign.
        super().draw(ctx, time)

class GasIgnitionSurge(Node):
    """
    High-voltage ignition flash surge on startup.
    A sudden bright flash of white/color that dissipates quickly.
    """
    def __init__(self, color: Color = colors.WHITE, max_radius: float = 100.0, **kwargs):
        super().__init__(**kwargs)
        self.surge_color = color
        self.max_radius = Signal(max_radius, f"{self.name}.max_radius")
        self.progress = Signal(0.0, f"{self.name}.progress")
        self.position = Signal(Vector2D(0.0, 0.0), f"{self.name}.position")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        prog = self.progress.get(time)
        if prog <= 0.0 or prog >= 1.0:
            super().draw(ctx, time)
            return

        # Peak intensity early, then fade
        alpha = 1.0 - (prog ** 0.5)
        radius = self.max_radius.get(time) * (0.2 + 0.8 * prog)

        pos = self.position.get(time)

        ctx.save()
        ctx.translate(pos.x, pos.y)

        # Draw a radial gradient flash
        pat = cairo.RadialGradient(0, 0, 0, 0, 0, radius)
        c = self.surge_color
        pat.add_color_stop_rgba(0.0, c.r, c.g, c.b, alpha)
        pat.add_color_stop_rgba(1.0, c.r, c.g, c.b, 0.0)

        ctx.set_source(pat)
        ctx.arc(0, 0, radius, 0, 2 * math.pi)
        ctx.fill()

        ctx.restore()
        super().draw(ctx, time)

class NeonTubeConnectors(Node):
    """
    Black wiring and rubber connector caps between separate letter tubes.
    """
    def __init__(self, points: List[Vector2D], **kwargs):
        super().__init__(**kwargs)
        self.points = points

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        if len(self.points) < 2:
            super().draw(ctx, time)
            return

        ctx.save()
        # Draw wire
        ctx.set_source_rgba(0.1, 0.1, 0.1, 1.0) # Dark grey/black
        ctx.set_line_width(3.0)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)

        ctx.move_to(self.points[0].x, self.points[0].y)
        for p in self.points[1:]:
            ctx.line_to(p.x, p.y)
        ctx.stroke()

        # Draw rubber caps at the ends
        ctx.set_source_rgba(0.05, 0.05, 0.05, 1.0)
        for p in self.points:
            ctx.arc(p.x, p.y, 4.0, 0, 2 * math.pi)
            ctx.fill()

        ctx.restore()
        super().draw(ctx, time)

class RealisticNeonStrobeSign(Node):
    """
    Glowing glass tube neon signage with multi-layer colored bloom halos.
    Includes an .ignite(delay=0.1) animation to tie flicker and surge.
    """
    def __init__(
        self,
        text: str,
        font_size: float = 64.0,
        font_family: str = "Inter",
        neon_color: Color = colors.CYAN,
        off_color: Color = Color.hex("#222222"),
        **kwargs
    ):
        super().__init__(**kwargs)
        self.text = text
        self.font_size = Signal(float(font_size), f"{self.name}.font_size")
        self.font_family = font_family
        self.neon_color = Signal(neon_color, f"{self.name}.neon_color")
        self.off_color = Signal(off_color, f"{self.name}.off_color")

        # 0.0 is completely off, 1.0 is fully on
        self.intensity = Signal(0.0, f"{self.name}.intensity")

        self.flicker = BallastFlickerFailure(name=f"{self.name}_flicker")
        self.add(self.flicker)

        self.surge = GasIgnitionSurge(color=colors.WHITE, max_radius=font_size*2, name=f"{self.name}_surge")
        self.add(self.surge)

        # Simplified connectors: just drawing a line under the text
        # To make it more realistic, we would need to know the glyph bounds.
        self.connectors = NeonTubeConnectors(points=[Vector2D(0, font_size * 0.9), Vector2D(len(text) * font_size * 0.5, font_size * 0.9)])
        self.add(self.connectors)


    def ignite(self, duration: float = 1.0, delay: float = 0.1) -> List[AnimationAction]:
        """
        Runs the ballast flicker and a gas surge.
        """
        actions = []
        actions.append(self.flicker.progress.to(1.0, duration=duration, delay=delay, ease=Ease.linear))

        # Surge occurs when it fully catches, say towards the end of the flicker
        actions.append(self.surge.progress.to(1.0, duration=0.3, delay=delay + duration * 0.7, ease=Ease.out_quad))

        return actions

    def _setup_cairo_font(self, ctx: cairo.Context, font_size: float) -> None:
        # Use bold for tubes
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(font_size)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        fs = self.font_size.get(time)
        on_c = self.neon_color.get(time)
        off_c = self.off_color.get(time)

        # Calculate current intensity using flicker progress
        flicker_int = self.flicker.get_flicker_intensity(time)

        # Override with explicit intensity if it's set higher, for manual control
        explicit_int = self.intensity.get(time)
        current_intensity = max(flicker_int, explicit_int)

        ctx.save()
        self._setup_cairo_font(ctx, fs)

        # Draw the base "off" tube
        ctx.move_to(0, fs * 0.88)
        ctx.set_source_rgba(off_c.r, off_c.g, off_c.b, off_c.a)
        ctx.set_line_width(fs * 0.05)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.text_path(self.text)
        ctx.stroke()

        if current_intensity > 0:
            # Draw multi-layer colored bloom halos
            layers = [
                (0.4, 0.1 * current_intensity),   # Widest, lowest opacity
                (0.2, 0.2 * current_intensity),
                (0.1, 0.4 * current_intensity),
                (0.05, 0.8 * current_intensity),  # Inner glow
            ]

            for width_mult, alpha in layers:
                ctx.move_to(0, fs * 0.88)
                ctx.set_source_rgba(on_c.r, on_c.g, on_c.b, alpha)
                ctx.set_line_width(fs * width_mult)
                ctx.text_path(self.text)
                ctx.stroke()

            # Draw the bright core
            ctx.move_to(0, fs * 0.88)
            core_c = on_c.lerp(colors.WHITE, 0.8) # Almost white core
            ctx.set_source_rgba(core_c.r, core_c.g, core_c.b, current_intensity)
            ctx.set_line_width(fs * 0.02)
            ctx.text_path(self.text)
            ctx.stroke()

        ctx.restore()

        super().draw(ctx, time)
