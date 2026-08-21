"""
Matrix Digital Code Rain backdrops.
Provides classic matrix green rain, binary streams, and hexadecimal memory dumps.
"""

from __future__ import annotations
import math
import random
from typing import Any, List, Optional, Tuple, Union
import cairo

from vibmo.core.color import Color, colors
from vibmo.scene.node import Node


class _CodeColumn:
    """Helper class to manage state for a single column of code."""
    def __init__(self, x: float, num_chars: int, speed: float, font_size: float, charset: str, y_offset: float = 0.0):
        self.x = x
        self.num_chars = num_chars
        self.speed = speed
        self.font_size = font_size
        self.charset = charset
        self.chars = [random.choice(self.charset) for _ in range(self.num_chars)]
        
        # State
        self.head_y = y_offset  # logical Y position in pixels
        self.last_update = 0.0

    def get_char_y(self, index: int) -> float:
        """Get pixel Y coordinate for character at index (0 is head, 1 is trail...)"""
        return self.head_y - (index * self.font_size)
    
    def mutate_glitch(self, chance: float = 0.05):
        for i in range(self.num_chars):
            if random.random() < chance:
                self.chars[i] = random.choice(self.charset)


class _BaseRainBackdrop(Node):
    def __init__(
        self,
        width: float = 1920.0,
        height: float = 1080.0,
        font_size: float = 20.0,
        speed_multiplier: float = 1.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.w = float(width)
        self.h = float(height)
        self.font_size = float(font_size)
        self.speed_multiplier = float(speed_multiplier)
        
        self.columns: List[_CodeColumn] = []
        self._initialized = False

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.w, self.h)

    def _init_columns(self):
        pass # Implemented by subclasses
        
    def _draw_column(self, ctx: Any, col: _CodeColumn, time: float):
        pass

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        if not self._initialized:
            self._init_columns()
            # Initialize last_update to the current time to prevent massive jumps on first frame
            for col in self.columns:
                col.last_update = time
            self._initialized = True
            
        ctx.save()
        
        # Clip to bounds
        ctx.rectangle(0, 0, self.w, self.h)
        ctx.clip()
        
        ctx.select_font_face("monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(self.font_size)

        for col in self.columns:
            # Update position
            dt = time - col.last_update
            if dt > 0:
                col.head_y += col.speed * self.speed_multiplier * dt
                # Reset if completely off screen
                if col.head_y - (col.num_chars * col.font_size) > self.h:
                    col.head_y = -random.uniform(0, self.h)
                    col.chars = [random.choice(col.charset) for _ in range(col.num_chars)]
            
            self._draw_column(ctx, col, time)
            col.last_update = time
            
        ctx.restore()


class DigitalMatrixRainBackdrop(_BaseRainBackdrop):
    """Cascading vertical columns of glowing green katakana/alphanumeric glyphs with bright white leading drops."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Katakana 0x30A0 to 0x30FF + Alphanumeric
        self.charset = "".join(chr(i) for i in range(0x30A0, 0x30FF)) + "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        
    def _init_columns(self):
        num_cols = int(self.w / self.font_size)
        self.columns = []
        for i in range(num_cols):
            x = i * self.font_size
            speed = random.uniform(100.0, 400.0)
            num_chars = random.randint(10, 40)
            y_offset = random.uniform(-self.h, self.h)
            self.columns.append(_CodeColumn(x, num_chars, speed, self.font_size, self.charset, y_offset))

    def _draw_column(self, ctx: Any, col: _CodeColumn, time: float):
        col.mutate_glitch(0.01) # occasional mutation
        
        for i, char in enumerate(col.chars):
            y = col.get_char_y(i)
            if y < 0 or y > self.h + self.font_size:
                continue
                
            if i == 0:
                # Leading drop is white/bright green
                ctx.set_source_rgba(0.8, 1.0, 0.8, 1.0)
            else:
                # Fading phosphor trail
                alpha = max(0.0, 1.0 - (i / col.num_chars))
                # Neon green
                ctx.set_source_rgba(0.0, 0.8, 0.2, alpha)
                
            ctx.move_to(col.x, y)
            ctx.show_text(char)


class BinaryStreamBackdrop(_BaseRainBackdrop):
    """Futuristic high-speed cyan stream of 0s and 1s with variable column speeds."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.charset = "01"
        self.speed_multiplier *= 2.0  # High speed
        
    def _init_columns(self):
        num_cols = int(self.w / self.font_size)
        self.columns = []
        for i in range(num_cols):
            x = i * self.font_size
            speed = random.uniform(200.0, 600.0)
            num_chars = random.randint(15, 60)
            y_offset = random.uniform(-self.h, self.h)
            self.columns.append(_CodeColumn(x, num_chars, speed, self.font_size, self.charset, y_offset))

    def _draw_column(self, ctx: Any, col: _CodeColumn, time: float):
        col.mutate_glitch(0.05) # more mutation
        
        for i, char in enumerate(col.chars):
            y = col.get_char_y(i)
            if y < 0 or y > self.h + self.font_size:
                continue
                
            # Cyan trail
            alpha = max(0.0, 1.0 - (i / col.num_chars))
            if i == 0:
                ctx.set_source_rgba(0.5, 1.0, 1.0, 1.0)
            else:
                ctx.set_source_rgba(0.0, 0.8, 1.0, alpha * 0.8)
                
            ctx.move_to(col.x, y)
            ctx.show_text(char)


class HexCodeColumnBackdrop(_BaseRainBackdrop):
    """Cryptographic hexadecimal memory dump columns with random character mutating glitches."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.charset = "0123456789ABCDEF"
        
    def _init_columns(self):
        # Wider columns for hex pairs
        num_cols = int(self.w / (self.font_size * 2))
        self.columns = []
        for i in range(num_cols):
            x = i * self.font_size * 2
            speed = random.uniform(50.0, 150.0)  # Slower dump
            num_chars = random.randint(20, 50)
            y_offset = random.uniform(-self.h, self.h)
            self.columns.append(_CodeColumn(x, num_chars, speed, self.font_size, self.charset, y_offset))

    def _draw_column(self, ctx: Any, col: _CodeColumn, time: float):
        col.mutate_glitch(0.1)  # High glitch rate
        
        for i in range(0, col.num_chars - 1, 2):
            y = col.get_char_y(i)
            if y < 0 or y > self.h + self.font_size:
                continue
                
            char_pair = col.chars[i] + col.chars[i+1]
            
            # Amber/Orange cryptography theme
            alpha = max(0.1, 1.0 - (i / col.num_chars))
            ctx.set_source_rgba(1.0, 0.6, 0.0, alpha)
                
            ctx.move_to(col.x, y)
            ctx.show_text(char_pair)

