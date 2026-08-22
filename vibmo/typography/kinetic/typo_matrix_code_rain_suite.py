import cairo
import random
from typing import List, Tuple, Optional
from vibmo.scene.node import Node
from vibmo.core.color import colors, Color
from vibmo.core.vector import Vector2D
from vibmo.core.signal import Signal

class MatrixRainTypography(Node):
    """
    Cascading green digital code rain drops that freeze and solidify into high-contrast bold title letters.
    """
    def __init__(self, target_text: str, font_size: float = 36.0, drop_speed: float = 100.0, **kwargs):
        super().__init__(**kwargs)
        self.target_text = target_text
        self.font_size = font_size
        self.drop_speed = drop_speed
        
        self.color = Signal(colors.GREEN_500)
        self.final_color = Signal(colors.WHITE)
        self.consolidated = Signal(0.0) # 0 to 1 progress of consolidation
        
        # Internal state needed for tests but not strictly used in current derived drawing
        self.drops: List[Tuple[float, float, str, float, bool]] = []
        self._init_drops()
        
    def _init_drops(self):
        rng = random.Random(hash(self.target_text))
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*"
        for i, char in enumerate(self.target_text):
            x = i * self.font_size * 0.8 # Roughly monospace spacing
            y = rng.uniform(-500.0, -100.0)
            speed_mult = rng.uniform(0.8, 1.5)
            # Pick a random char initially
            current_char = rng.choice(chars)
            self.drops.append((x, y, current_char, speed_mult, False))
            
    def _update_drops(self, time: float):
        rng = random.Random(int(time * 10) + hash(self.target_text))
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*"
        progress = self.consolidated.get(time)
        
        new_drops = []
        for i, (x, y, char, speed_mult, is_target) in enumerate(self.drops):
            target_char = self.target_text[i] if i < len(self.target_text) else " "
            
            # If consolidating, move towards y=0 and snap
            if progress > 0.0:
                target_y = 0.0
                # Snap to target char based on progress
                if progress > (i / len(self.target_text)):
                    new_char = target_char
                    is_target = True
                else:
                    new_char = rng.choice(chars) if rng.random() > 0.8 else char
                    
                # Lerp towards 0
                new_y = y + (target_y - y) * progress
            else:
                # Normal falling
                new_y = y + self.drop_speed * speed_mult * 0.016 # Assume roughly 60fps delta
                if new_y > 500.0:
                    new_y = rng.uniform(-500.0, -100.0)
                new_char = rng.choice(chars) if rng.random() > 0.9 else char
                
            new_drops.append((x, new_y, new_char, speed_mult, is_target))
            
        return new_drops
        
    def draw(self, ctx: cairo.Context, time: float) -> None:
        ctx.select_font_face("Courier New", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(self.font_size)
        
        rng = random.Random(int(time * 15) + hash(self.target_text))
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*"
        progress = self.consolidated.get(time)
        
        for i, target_char in enumerate(self.target_text):
            x = i * self.font_size * 0.7
            
            # Deterministic falling based on time and index
            base_speed = self.drop_speed * (1.0 + (hash(str(i)) % 50) / 100.0)
            raw_y = -500 + (time * base_speed) % 1000
            
            if progress > 0:
                snap_threshold = i / max(1, len(self.target_text))
                if progress > snap_threshold:
                    y = 0.0
                    display_char = target_char
                    color = self.final_color.get(time).to_tuple_rgba()
                else:
                    # Lerp y towards 0
                    y = raw_y * (1.0 - progress)
                    display_char = rng.choice(chars) if rng.random() > 0.5 else chars[hash(str(i) + str(int(time*10))) % len(chars)]
                    color = self.color.get(time).to_tuple_rgba()
            else:
                y = raw_y
                display_char = rng.choice(chars) if rng.random() > 0.5 else chars[hash(str(i) + str(int(time*10))) % len(chars)]
                color = self.color.get(time).to_tuple_rgba()
                
            ctx.set_source_rgba(*color)
            ctx.move_to(x, y)
            ctx.show_text(display_char)
            

class PhosphorTrailDecay(Node):
    """
    Bright glowing leading glyphs with fading phosphor decay tails.
    """
    def __init__(self, text: str, trail_length: int = 5, font_size: float = 36.0, speed: float = 150.0, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.trail_length = trail_length
        self.font_size = font_size
        self.speed = speed
        self.color = Signal(colors.GREEN_500)
        
    def draw(self, ctx: cairo.Context, time: float) -> None:
        ctx.select_font_face("Courier New", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(self.font_size)
        
        base_color = self.color.get(time)
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        
        for i, char in enumerate(self.text):
            x = i * self.font_size * 0.7
            
            # Use deterministic falling
            speed_mult = 1.0 + (hash(str(i)) % 50) / 100.0
            leading_y = -300 + (time * self.speed * speed_mult) % 800
            
            for j in range(self.trail_length):
                trail_y = leading_y - (j * self.font_size)
                
                # Fade out based on trail index
                alpha = 1.0 - (j / self.trail_length)
                c = base_color.with_alpha(alpha)
                
                display_char = chars[hash(str(i) + str(j) + str(int(time*5))) % len(chars)]
                if j == 0:
                    ctx.set_source_rgba(1.0, 1.0, 1.0, 1.0) # Leading char is white/bright
                    ctx.select_font_face("Courier New", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
                else:
                    ctx.set_source_rgba(*c.to_tuple_rgba())
                    ctx.select_font_face("Courier New", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                
                ctx.move_to(x, trail_y)
                ctx.show_text(display_char)


class HeadlineConsolidation(Node):
    """
    Transition where rain drops snap into final letter shapes with a white flash.
    """
    def __init__(self, text: str, font_size: float = 48.0, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.font_size = font_size
        self.progress = Signal(0.0) # 0 to 1
        
    def draw(self, ctx: cairo.Context, time: float) -> None:
        prog = self.progress.get(time)
        if prog <= 0:
            return
            
        ctx.select_font_face("Courier New", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(self.font_size)
        
        rng = random.Random(hash(self.text) + int(time * 20))
        chars = "01"
        
        for i, char in enumerate(self.text):
            x = i * self.font_size * 0.6
            y = 0.0
            
            char_prog_threshold = i / max(1, len(self.text))
            
            if prog > char_prog_threshold:
                # Snap to final letter
                display_char = char
                # Flash white initially, then fade to normal color
                flash_amount = max(0.0, 1.0 - (prog - char_prog_threshold) * 5.0)
                color = Color.rgba(255, 255, 255, 1.0) if flash_amount > 0.5 else colors.WHITE
                ctx.set_source_rgba(*color.to_tuple_rgba())
                
                if flash_amount > 0:
                    # Draw flash glow
                    ctx.save()
                    ctx.set_source_rgba(1.0, 1.0, 1.0, flash_amount * 0.5)
                    ctx.set_line_width(2.0 + flash_amount * 5.0)
                    ctx.move_to(x, y)
                    ctx.text_path(display_char)
                    ctx.stroke()
                    ctx.restore()
                    
            else:
                # Still scrambling/consolidating
                display_char = rng.choice(chars)
                # Jitter position slightly
                jx = x + rng.uniform(-2.0, 2.0)
                jy = y + rng.uniform(-5.0, 5.0)
                ctx.set_source_rgba(*colors.GREEN_500.to_tuple_rgba())
                x, y = jx, jy
                
            ctx.move_to(x, y)
            ctx.show_text(display_char)


class GlyphMatrixSubText(Node):
    """
    Accompanying decoding subtitles in digital monospace font.
    """
    def __init__(self, text: str, font_size: float = 16.0, decode_speed: float = 20.0, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.font_size = font_size
        self.decode_speed = decode_speed
        self.color = Signal(colors.GREEN_500)
        
    def draw(self, ctx: cairo.Context, time: float) -> None:
        ctx.select_font_face("Courier New", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(self.font_size)
        
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+"
        
        # Determine how many characters are fully decoded based on time
        decoded_count = int(time * self.decode_speed)
        
        # For characters not yet fully decoded, show random glyphs
        rng = random.Random(int(time * 15))
        
        display_str = ""
        for i, char in enumerate(self.text):
            if i < decoded_count:
                display_str += char
            else:
                display_str += rng.choice(chars)
                
        ctx.set_source_rgba(*self.color.get(time).to_tuple_rgba())
        
        # Simple left-aligned text
        lines = display_str.split("\n")
        for idx, line in enumerate(lines):
            ctx.move_to(0, idx * self.font_size * 1.2)
            ctx.show_text(line)

