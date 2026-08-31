import math
import random
from typing import Any, Tuple, Optional, List
import cairo

from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease
from vibmo.scene.node import Node
from vibmo.typography.text import Text



class HexMatrixCycle(Node):
    """
    Fast cycle animation where unsettled characters cycle with high frequency.
    Renders a single character that changes over time, pulling from a pool of glyphs.
    """
    def __init__(self, target_char: str, pool: str = "0123456789ABCDEF!@#$%^&*", font_size: float = 32.0, font_family: str = "Inter", color: Color = colors.CYAN, cycle_speed: float = 30.0, **kwargs):
        super().__init__(**kwargs)
        self.target_char = target_char
        self.pool = pool
        self.font_size = Signal(float(font_size), f"{self.name}.font_size")
        self.font_family = font_family
        self.color = Signal(color, f"{self.name}.color")
        self.cycle_speed = cycle_speed

        self.progress = Signal(0.0, f"{self.name}.progress")
        self._rng = random.Random(hash(target_char) + id(self))

    def _setup_cairo_font(self, ctx: cairo.Context, font_size: float) -> None:
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(font_size)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        prog = self.progress.get(time)
        if prog >= 1.0:
            char_to_draw = self.target_char
        else:
            # Change character based on time and cycle speed
            idx = int(time * self.cycle_speed) % len(self.pool)

            # Make it pseudo-random based on time index and self identity to avoid all characters cycling identically
            self._rng.seed(int(time * self.cycle_speed) + id(self))
            char_to_draw = self._rng.choice(self.pool)

        fs = self.font_size.get(time)
        c = self.color.get(time)

        ctx.save()
        self._setup_cairo_font(ctx, fs)
        ctx.set_source_rgba(c.r, c.g, c.b, c.a)

        extents = ctx.text_extents(char_to_draw)
        ctx.move_to(0, fs * 0.88)
        ctx.show_text(char_to_draw)
        ctx.restore()

        super().draw(ctx, time)

class LockInGlitchFlash(Node):
    """
    Cyan/white chromatic flash upon each character successfully locking into final letter.
    """
    def __init__(self, char: str, font_size: float = 32.0, font_family: str = "Inter", **kwargs):
        super().__init__(**kwargs)
        self.char = char
        self.font_size = Signal(float(font_size), f"{self.name}.font_size")
        self.font_family = font_family

        self.flash_progress = Signal(0.0, f"{self.name}.flash_progress")

    def flash(self, duration: float = 0.3) -> AnimationAction:
        return self.flash_progress.to(1.0, duration=duration, ease=Ease.out_expo)

    def _setup_cairo_font(self, ctx: cairo.Context, font_size: float) -> None:
        ctx.select_font_face(self.font_family, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(font_size)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        prog = self.flash_progress.get(time)
        if prog <= 0.0 or prog >= 1.0:
            return

        fs = self.font_size.get(time)

        ctx.save()
        self._setup_cairo_font(ctx, fs)

        # Flash color logic: starts white, fades to cyan, then disappears
        alpha = 1.0 - prog
        if prog < 0.2:
            r, g, b = 1.0, 1.0, 1.0 # White peak
        else:
            r, g, b = colors.CYAN.r, colors.CYAN.g, colors.CYAN.b # Settle to cyan

        ctx.set_source_rgba(r, g, b, alpha)

        # Optional: add slight chromatic offset
        offset = (1.0 - prog) * 2.0

        # Red channel offset
        ctx.save()
        ctx.set_source_rgba(1.0, 0.0, 0.0, alpha * 0.5)
        ctx.move_to(-offset, fs * 0.88)
        ctx.show_text(self.char)
        ctx.restore()

        # Blue channel offset
        ctx.save()
        ctx.set_source_rgba(0.0, 1.0, 1.0, alpha * 0.5)
        ctx.move_to(offset, fs * 0.88)
        ctx.show_text(self.char)
        ctx.restore()

        # Main flash
        ctx.set_source_rgba(r, g, b, alpha)
        ctx.move_to(0, fs * 0.88)
        ctx.show_text(self.char)

        ctx.restore()
        super().draw(ctx, time)

class PasswordUnmaskEffect(Node):
    """
    Password mask unmasking animation with binary digital noise.
    Starts as '*' or '•', then scrambles, then reveals the target string.
    """
    def __init__(self, target_text: str, mask_char: str = "•", font_size: float = 32.0, font_family: str = "Inter", color: Color = colors.WHITE, **kwargs):
        super().__init__(**kwargs)
        self.target_text = target_text
        self.mask_char = mask_char
        self.font_size = Signal(float(font_size), f"{self.name}.font_size")
        self.font_family = font_family
        self.color = Signal(color, f"{self.name}.color")

        self.progress = Signal(0.0, f"{self.name}.progress")
        self._rng = random.Random(hash(target_text))

    def unmask(self, duration: float = 1.5) -> AnimationAction:
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
        ctx.set_source_rgba(c.r, c.g, c.b, c.a)

        current_x = 0.0

        for i, char in enumerate(self.target_text):
            char_prog_start = i / len(self.target_text)
            char_prog_end = (i + 1) / len(self.target_text)

            # Map global progress to character progress
            if prog <= char_prog_start:
                display_char = self.mask_char
            elif prog >= char_prog_end:
                display_char = char
            else:
                # Scrambling phase
                self._rng.seed(int(time * 20) + i)
                display_char = self._rng.choice("01") # Binary noise

            ctx.move_to(current_x, fs * 0.88)
            ctx.show_text(display_char)
            extents = ctx.text_extents(display_char)
            current_x += max(extents.width, fs * 0.6) + fs * 0.1 # fixed spacing

        ctx.restore()
        super().draw(ctx, time)

class GlitchDecryptorText(Node):
    """
    Title text that scrambles through random hexadecimal/katakana glyphs before resolving
    character-by-character from left to right.
    """
    def __init__(self, text: str, font_size: float = 48.0, font_family: str = "Inter",
                 color: Color = colors.CYAN, scramble_pool: str = "0123456789ABCDEF", **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.font_size = Signal(float(font_size), f"{self.name}.font_size")
        self.font_family = font_family
        self.color = Signal(color, f"{self.name}.color")
        self.scramble_pool = scramble_pool

        self.decrypt_progress = Signal(0.0, f"{self.name}.decrypt_progress")

        # We will manage our own glyph nodes to utilize the other effects
        self.cycles = []
        self.flashes = []
        self.final_glyphs = []

        current_x = 0.0
        # For precise layout, we need to estimate or calculate widths, but since this is dynamic
        # we'll use a fixed monospace-like advancement for glitch effects, or query Cairo.
        # For simplicity, we use an estimated advancement based on font_size.
        advancement = font_size * 0.7

        for i, char in enumerate(text):
            # Create a container node for each character position
            char_node = Node(position=Vector2D(current_x, 0))

            cycle = HexMatrixCycle(target_char=char, pool=scramble_pool, font_size=font_size, font_family=font_family, color=color)
            flash = LockInGlitchFlash(char=char, font_size=font_size, font_family=font_family)

            # Add to local lists
            self.cycles.append(cycle)
            self.flashes.append(flash)

            char_node.add(cycle)
            char_node.add(flash)
            self.add(char_node)

            current_x += advancement

        self._last_locked_index = -1

    def decrypt(
        self,
        duration: float = 2.0,
        delay: float = 0.0,
        ease: Optional[Any] = None,
    ) -> AnimationAction:
        """Starts the decryption animation from left to right."""
        # We also reset state if called multiple times
        self._last_locked_index = -1
        for cycle in self.cycles:
            cycle.progress.set(0.0)
        for flash in self.flashes:
            flash.flash_progress.set(0.0)
        self.decrypt_progress.set(0.0)
        e = ease or Ease.linear
        return self.decrypt_progress.to(1.0, duration=duration, ease=e, delay=delay)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        prog = self.decrypt_progress.get(time)

        # Update children progress based on global decrypt progress
        total_chars = len(self.text)

        for i in range(total_chars):
            char_prog_start = i / total_chars

            char_prog_end = (i + 1) / total_chars

            if prog >= char_prog_end:
                # This character is locked in
                self.cycles[i].progress.set(1.0)

                # Trigger flash if newly locked
                if i > self._last_locked_index:
                    # We need to simulate the flash starting at this exact time.
                    # Since we are inside draw(), we can't easily yield AnimationActions.
                    # But we can start an autonomous action or just manually set a time-based signal offset.
                    # For simplicity, we'll just track that it locked.
                    pass
            else:
                self.cycles[i].progress.set(0.0)

        # Manually manage flashes inside draw if needed, or rely on timeline
        # A cleaner way is if we triggered flashes from the timeline.
        # But for this component, we'll just map flash progress directly from time.

        for i in range(total_chars):
            char_prog_start = i / total_chars
            # If we just passed the threshold, we flash for 0.3s relative to total duration
            # This requires knowing the duration, which is tricky in draw().
            # So we use a time-based hack or just let the user schedule flashes,
            # OR we calculate flash progress dynamically.

            # Let's say decrypt() takes duration D. Then 1 char takes D/N.
            # We can map global progress to local flash progress.
            char_prog = (prog * total_chars) - i
            if 0 <= char_prog <= 1.0: # Arbitrary duration mapped to progress
                # If char_prog is between 0 and 1, we are in the flashing window
                # Let's say flash takes the same time as 1 char decrypt
                self.flashes[i].flash_progress.set(char_prog)
            elif char_prog > 1.0:
                self.flashes[i].flash_progress.set(1.0)
            else:
                self.flashes[i].flash_progress.set(0.0)

        super().draw(ctx, time)
