import math
from typing import Any, List, Optional
import cairo

from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease
from vibmo.scene.node import Node


class LiquidWaveText(Node):
    """
    Kinetic text where glyph baselines undulate smoothly along a sinusoidal wave across time.
    """
    def __init__(self, text: str, font_size: float = 32.0, font_family: str = "Inter", color: Color = colors.WHITE,
                 amplitude: float = 10.0, frequency: float = 0.5, speed: float = 2.0, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.font_size = Signal(float(font_size), f"{self.name}.font_size")
        self.font_family = font_family
        self.color = Signal(color, f"{self.name}.color")
        self.amplitude = amplitude
        self.frequency = frequency
        self.speed = speed
        self.reveal_progress = Signal(1.0, f"{self.name}.reveal_progress")

    def ripple_reveal(
        self,
        duration: float = 1.8,
        delay: float = 0.0,
        ease: Optional[Any] = None,
    ) -> AnimationAction:
        """Animates a staggered fluid wave reveal where characters emerge with liquid ripple dynamics."""
        self.reveal_progress.set(0.0)
        e = ease or Ease.out_cubic
        return self.reveal_progress.to(1.0, duration=duration, ease=e, delay=delay)

    def _setup_cairo_font(self, ctx: cairo.Context, font_size: float) -> None:
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(font_size)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        fs = self.font_size.get(time)
        c = self.color.get(time)
        prog = float(self.reveal_progress.get(time))

        ctx.save()
        self._setup_cairo_font(ctx, fs)

        current_x = 0.0
        n_chars = max(1, len(self.text))
        for i, char in enumerate(self.text):
            # Calculate wave offset
            wave_offset = math.sin((i * self.frequency) + (time * self.speed)) * self.amplitude

            if prog < 1.0:
                char_start = i / n_chars
                char_end = (i + 1) / n_chars
                if prog <= char_start:
                    local_p = 0.0
                elif prog >= char_end:
                    local_p = 1.0
                else:
                    local_p = (prog - char_start) / (char_end - char_start)
                
                eased_p = Ease.out_cubic(local_p)
                char_alpha = eased_p * c.a
                y_emerge = (1.0 - eased_p) * fs * 0.8
                ripple_mod = math.sin(local_p * math.pi) * (self.amplitude * 1.5) if local_p < 1.0 else 0.0
            else:
                char_alpha = c.a
                y_emerge = 0.0
                ripple_mod = 0.0

            extents = ctx.text_extents(char)
            if char_alpha > 0.01:
                ctx.set_source_rgba(c.r, c.g, c.b, char_alpha)
                ctx.move_to(current_x, fs * 0.88 + wave_offset + y_emerge - ripple_mod)
                ctx.show_text(char)
            current_x += extents.x_advance

        ctx.restore()
        super().draw(ctx, time)


class ChromaticBaselineDrift(Node):
    """
    RGB color splitting on crests and troughs of the text wave.
    """
    def __init__(self, text: str, font_size: float = 32.0, font_family: str = "Inter", color: Color = colors.WHITE,
                 amplitude: float = 10.0, frequency: float = 0.5, speed: float = 2.0, rgb_split_max: float = 5.0, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.font_size = Signal(float(font_size), f"{self.name}.font_size")
        self.font_family = font_family
        self.color = Signal(color, f"{self.name}.color")
        self.amplitude = amplitude
        self.frequency = frequency
        self.speed = speed
        self.rgb_split_max = rgb_split_max

    def _setup_cairo_font(self, ctx: cairo.Context, font_size: float) -> None:
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(font_size)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        fs = self.font_size.get(time)
        base_c = self.color.get(time)
        alpha = base_c.a

        ctx.save()
        self._setup_cairo_font(ctx, fs)

        current_x = 0.0
        for i, char in enumerate(self.text):
            phase = (i * self.frequency) + (time * self.speed)
            wave_offset = math.sin(phase) * self.amplitude

            # The derivative of sin(x) is cos(x). Max drift on crests/troughs means sin(x) is +/- 1,
            # so we can use sin(phase) for drift amount to have max drift at crests and troughs.
            # Or derivative: cos(phase) for zero crossings. The request says "on crests and troughs".
            drift = math.sin(phase) * self.rgb_split_max

            extents = ctx.text_extents(char)
            base_y = fs * 0.88 + wave_offset

            ctx.set_operator(cairo.OPERATOR_ADD)

            # Red channel
            ctx.set_source_rgba(base_c.r, 0.0, 0.0, alpha)
            ctx.move_to(current_x - drift, base_y)
            ctx.show_text(char)

            # Green channel
            ctx.set_source_rgba(0.0, base_c.g, 0.0, alpha)
            ctx.move_to(current_x, base_y)
            ctx.show_text(char)

            # Blue channel
            ctx.set_source_rgba(0.0, 0.0, base_c.b, alpha)
            ctx.move_to(current_x + drift, base_y)
            ctx.show_text(char)

            current_x += extents.x_advance
            ctx.set_operator(cairo.OPERATOR_OVER) # Restore default operator

        ctx.restore()
        super().draw(ctx, time)


class SubmergedTextRefraction(Node):
    """
    Text viewed through simulated water refraction with shimmering caustic reflections.
    """
    def __init__(self, text: str, font_size: float = 32.0, font_family: str = "Inter", color: Color = colors.WHITE, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.font_size = Signal(float(font_size), f"{self.name}.font_size")
        self.font_family = font_family
        self.color = Signal(color, f"{self.name}.color")
        self.caustic_color = colors.CYAN.with_alpha(0.6)

    def _setup_cairo_font(self, ctx: cairo.Context, font_size: float) -> None:
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(font_size)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        fs = self.font_size.get(time)
        c = self.color.get(time)

        ctx.save()
        self._setup_cairo_font(ctx, fs)

        current_x = 0.0
        for i, char in enumerate(self.text):
            # Complex X/Y sine distortion
            refract_x = math.sin(time * 3.0 + i * 0.8) * 3.0 + math.cos(time * 1.5 - i * 0.5) * 1.5
            refract_y = math.sin(time * 2.5 - i * 1.1) * 2.5 + math.cos(time * 4.0 + i * 0.3) * 1.0

            extents = ctx.text_extents(char)

            # Base text
            ctx.set_source_rgba(*c.to_cairo())
            ctx.move_to(current_x + refract_x, fs * 0.88 + refract_y)
            ctx.show_text(char)

            # Caustic shimmer layer
            shimmer_alpha = (math.sin(time * 5.0 + i * 1.5) * 0.5 + 0.5) * self.caustic_color.a
            if shimmer_alpha > 0.01:
                ctx.set_source_rgba(self.caustic_color.r, self.caustic_color.g, self.caustic_color.b, shimmer_alpha)
                # Caustic offset slightly differently
                c_offset_x = math.sin(time * -2.0 + i * 1.2) * 2.0
                c_offset_y = math.cos(time * 3.2 + i * 0.7) * 2.0
                ctx.move_to(current_x + refract_x + c_offset_x, fs * 0.88 + refract_y + c_offset_y)
                ctx.show_text(char)

            current_x += extents.x_advance

        ctx.restore()
        super().draw(ctx, time)


class RippleWordReveal(Node):
    """
    Staggered wave splash reveal where words emerge from water surface.
    """
    def __init__(self, text: str, font_size: float = 32.0, font_family: str = "Inter", color: Color = colors.WHITE, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.words = text.split(" ")
        self.font_size = Signal(float(font_size), f"{self.name}.font_size")
        self.font_family = font_family
        self.color = Signal(color, f"{self.name}.color")
        self.progress = Signal(0.0, f"{self.name}.progress")

    def reveal(self, duration: float = 2.0) -> AnimationAction:
        return self.progress.to(1.0, duration=duration, ease=Ease.linear)

    def _setup_cairo_font(self, ctx: cairo.Context, font_size: float) -> None:
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(font_size)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        prog = self.progress.get(time)
        fs = self.font_size.get(time)
        c = self.color.get(time)

        ctx.save()
        self._setup_cairo_font(ctx, fs)

        current_x = 0.0
        num_words = len(self.words)

        space_extents = ctx.text_extents(" ")
        space_width = space_extents.x_advance

        for i, word in enumerate(self.words):
            word_start_prog = i / max(1, num_words)
            word_end_prog = (i + 1) / max(1, num_words)

            # Local progress for this word
            if prog <= word_start_prog:
                local_prog = 0.0
            elif prog >= word_end_prog:
                local_prog = 1.0
            else:
                local_prog = (prog - word_start_prog) / (word_end_prog - word_start_prog)

            # Easing for smooth reveal
            eased_prog = Ease.out_cubic(local_prog)

            # Submerged offset (comes from below)
            y_offset = (1.0 - eased_prog) * fs * 1.5
            alpha = eased_prog * c.a

            word_extents = ctx.text_extents(word)

            if alpha > 0.01:
                ctx.set_source_rgba(c.r, c.g, c.b, alpha)

                # Add a little wave during the reveal
                splash_wave = math.sin(local_prog * math.pi) * (fs * 0.2) if local_prog < 1.0 else 0.0

                ctx.move_to(current_x, fs * 0.88 + y_offset - splash_wave)
                ctx.show_text(word)

            current_x += word_extents.x_advance + space_width

        ctx.restore()
        super().draw(ctx, time)
