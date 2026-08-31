"""
Airport/Train Station Split-Flap Display suite.
"""

import math
import string
import cairo
from typing import Any, Callable, List, Optional, Tuple, Union

from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal, AnimationAction
from vibmo.scene.node import Node
from vibmo.typography.text import Text
from vibmo.core.vector import Vector2D
from vibmo.core.easing import Ease

# Standard character set for the split flap
FLAP_CHARSET = " " + string.ascii_uppercase + string.digits + ".,!?-"

class SplitFlapSoundSync:
    """Event hooks designed to trigger click events per flap."""
    def __init__(self):
        self.callbacks: List[Callable[[], None]] = []
        
    def add_listener(self, callback: Callable[[], None]):
        self.callbacks.append(callback)
        
    def trigger_flap(self):
        for cb in self.callbacks:
            cb()

class RapidLetterScramble:
    """Staggered flipping rhythm where letters flip rapidly before clattering into place."""
    
    def __init__(self, start_char: str, target_char: str, total_flaps: int):
        self.start_char = start_char.upper()
        self.target_char = target_char.upper()
        
        if self.start_char not in FLAP_CHARSET:
            self.start_char = " "
        if self.target_char not in FLAP_CHARSET:
            self.target_char = " "
            
        self.start_idx = FLAP_CHARSET.index(self.start_char)
        self.target_idx = FLAP_CHARSET.index(self.target_char)
        
        # Calculate how many flips to reach target, ensuring minimum flaps
        diff = (self.target_idx - self.start_idx) % len(FLAP_CHARSET)
        if diff == 0 and self.start_char != self.target_char:
            # Should not happen with modulo unless they are the same char, but if same char we might want to flip a full cycle
            pass
            
        # Add full cycles if total_flaps is large
        self.total_flaps = diff
        while self.total_flaps < total_flaps:
            self.total_flaps += len(FLAP_CHARSET)
            
    def get_state(self, progress: float) -> Tuple[str, str, str, float, bool]:
        """
        Given progress [0, 1], returns:
        (top_half_char, bottom_half_char, flap_char, flap_progress [0,1], just_flipped)
        """
        if progress >= 1.0:
            return (self.target_char, self.target_char, self.target_char, 0.0, False)
            
        # Eased progress for clattering into place (starts fast, ends slow)
        # Using ease out cubic or similar
        eased_p = Ease.out_cubic(progress)
        
        current_flap_float = eased_p * self.total_flaps
        current_flap_idx = int(current_flap_float)
        
        flap_progress = current_flap_float - current_flap_idx
        
        # Determine chars
        idx_current = (self.start_idx + current_flap_idx) % len(FLAP_CHARSET)
        idx_next = (self.start_idx + current_flap_idx + 1) % len(FLAP_CHARSET)
        
        char_current = FLAP_CHARSET[idx_current]
        char_next = FLAP_CHARSET[idx_next]
        
        if flap_progress < 0.5:
            top_char = char_next
            bottom_char = char_current
            flap_char = char_current
            # flap goes from 1.0 height to 0.0
            visual_progress = flap_progress * 2
        else:
            top_char = char_next
            bottom_char = char_current
            flap_char = char_next
            # flap goes from 0.0 height to 1.0
            visual_progress = (flap_progress - 0.5) * 2
            
        # We can use flap_progress exactly as is, and let the renderer handle the <0.5 and >0.5 logic
        return (char_current, char_next, char_current if flap_progress < 0.5 else char_next, flap_progress, False)


class MechanicalFlapTile(Node):
    """Split top and bottom half-tiles with 3D folding perspective flap and center split gap."""
    def __init__(self, width: float = 60.0, height: float = 90.0, font_size: float = 64.0, **kwargs):
        super().__init__(**kwargs)
        self.width = Signal(width, f"{self.name}.width")
        self.height = Signal(height, f"{self.name}.height")
        self.font_size = Signal(font_size, f"{self.name}.font_size")
        
        self.char_current = " "
        self.char_next = " "
        self.flap_progress = 0.0 # 0.0 to 1.0
        
        self.bg_color = colors.SLATE_900
        self.text_color = colors.WHITE
        self.gap_height = 2.0
        
        # Internal text nodes for rendering (we won't add them as children to avoid auto-rendering, 
        # we will render them manually in our draw method to apply clipping)
        self._text_node = Text(text=" ", font_size=font_size, font_family="Inter", bold=True, color=self.text_color, align="center")

    def _draw_half_tile(self, ctx: cairo.Context, char: str, is_top: bool, scale_y: float = 1.0):
        w = self.width.get()
        h = self.height.get()
        half_h = h / 2.0 - self.gap_height / 2.0
        
        ctx.save()
        
        # Translate to the center hinge
        ctx.translate(w / 2.0, h / 2.0)
        
        # Apply scaling (for the flipping flap perspective)
        ctx.scale(1.0, scale_y)
        
        if is_top:
            # Drawing top half (which scales from 1.0 to 0.0, so y goes from -half_h to 0)
            rect_y = -self.gap_height/2.0 - half_h
        else:
            # Drawing bottom half (scales from 0.0 to 1.0, so y goes from 0 to half_h)
            rect_y = self.gap_height/2.0
            
        # Draw background
        ctx.rectangle(-w/2.0, rect_y, w, half_h)
        ctx.set_source_rgba(*self.bg_color.to_cairo())
        ctx.fill()
        
        # Clip to half tile for text
        ctx.rectangle(-w/2.0, rect_y, w, half_h)
        ctx.clip()
        
        # Render text (centered at origin, which is center of tile before we translated)
        # Wait, if we translated to hinge, text should be drawn such that its center is at (0, 0)
        self._text_node.text.set(char)
        self._text_node.font_size.set(self.font_size.get())
        
        # We need to compute text bounds to center it properly
        # Or just draw it at (0, 0) since align="center" might handle X, but Y is tricky
        ctx.save()
        ctx.translate(0, 0) # Text center is at hinge
        
        # Small hack: to vertically center text, we usually need its bounds
        bounds = self._text_node.local_bounds(0.0)
        text_w = bounds[2]
        text_h = bounds[3]
        
        # Move text so its visual center is at (0, 0)
        # Because we are in the coordinate space where (0,0) is the center of the tile
        ctx.translate(-text_w/2.0, text_h/4.0) 
        
        self._text_node.draw(ctx, 0.0)
        ctx.restore()
        
        ctx.restore()

    def set_state(self, current: str, next_char: str, progress: float):
        self.char_current = current
        self.char_next = next_char
        self.flap_progress = max(0.0, min(1.0, progress))
        
    def draw(self, ctx: cairo.Context, time: float):
        w = self.width.get()
        h = self.height.get()
        
        # Base translation for the tile (assuming origin is top-left of tile)
        # We will draw within (0, 0) to (w, h)
        
        # 1. Draw static top half (shows NEXT character)
        self._draw_half_tile(ctx, self.char_next, is_top=True)
        
        # 2. Draw static bottom half (shows CURRENT character)
        self._draw_half_tile(ctx, self.char_current, is_top=False)
        
        # 3. Draw the flipping flap
        if self.flap_progress < 0.5:
            # Top flap folding down
            # Progress 0 -> 0.49 means scale_y 1.0 -> ~0.0
            scale = 1.0 - (self.flap_progress * 2.0)
            self._draw_half_tile(ctx, self.char_current, is_top=True, scale_y=scale)
        else:
            # Bottom flap folding down
            # Progress 0.5 -> 1.0 means scale_y ~0.0 -> 1.0
            scale = (self.flap_progress - 0.5) * 2.0
            self._draw_half_tile(ctx, self.char_next, is_top=False, scale_y=scale)
            
        super().draw(ctx, time)

class SplitFlapAirportBoard(Node):
    """Matrix of mechanical split-flap character modules flipping through letters to form titles."""
    def __init__(
        self,
        initial_text: Union[str, List[str]] = "",
        rows: int = 1,
        cols: int = 16,
        tile_width: float = 60.0,
        tile_height: float = 90.0,
        gap: float = 10.0,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.rows = rows
        self.cols = cols
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.gap = gap
        
        if isinstance(initial_text, list):
            init_str = " ".join(initial_text)
        else:
            init_str = str(initial_text)
        if not init_str and (rows > 1 or cols > 1):
            init_str = " " * (rows * cols)

        self.text_signal = Signal(init_str, f"{self.name}.text")
        
        self.tiles: List[MechanicalFlapTile] = []
        self.scrambles: List[RapidLetterScramble] = []
        self.sound_sync = SplitFlapSoundSync()
        
        self.anim_progress = Signal(0.0, f"{self.name}.anim_progress")
        self.anim_duration = 0.0
        
        self._setup_tiles(init_str)
        
    def _setup_tiles(self, text: str):
        self.children.clear()
        self.tiles.clear()
        
        for i, char in enumerate(text):
            tile = MechanicalFlapTile(width=self.tile_width, height=self.tile_height)
            row_idx = i // self.cols if self.cols > 0 else 0
            col_idx = i % self.cols if self.cols > 0 else i
            tile.position.set(((self.tile_width + self.gap) * col_idx, (self.tile_height + self.gap) * row_idx))
            tile.set_state(char, char, 0.0)
            self.tiles.append(tile)
            self.add(tile)
            
    def flip_to(
        self,
        target_text: Union[str, List[str]],
        duration: float = 1.5,
        delay: float = 0.0,
        ease: Optional[Any] = None,
    ) -> AnimationAction:
        if isinstance(target_text, list):
            target_str = " ".join(target_text)
        else:
            target_str = str(target_text)

        current_text = self.text_signal.get()
        
        # Pad strings to equal length
        max_len = max(len(current_text), len(target_str))
        current_text = current_text.ljust(max_len, " ")
        target_str = target_str.ljust(max_len, " ")
        
        if len(self.tiles) != max_len:
            self._setup_tiles(current_text)
            
        self.scrambles.clear()
        
        for i in range(max_len):
            start_char = current_text[i]
            target_char = target_str[i]
            # Staggered total flaps: later characters flip longer
            flaps = 5 + i * 3
            self.scrambles.append(RapidLetterScramble(start_char, target_char, flaps))
            
        self.anim_progress.set(0.0)
        e = ease or Ease.linear
        self.anim_duration = duration
        self.text_signal.set(target_str)
        return self.anim_progress.to(1.0, duration=duration, ease=e, delay=delay)
        
    def draw(self, ctx: cairo.Context, time: float):
        prog = self.anim_progress.get(time)
        
        last_flaps = getattr(self, '_last_flaps', [-1] * len(self.tiles))
        current_flaps = []
        
        for i, (tile, scramble) in enumerate(zip(self.tiles, self.scrambles)):
            if prog > 0:
                # Add some stagger based on index
                stagger_delay = i * 0.1
                local_prog = max(0.0, min(1.0, (prog - stagger_delay) / (1.0 - stagger_delay))) if stagger_delay < 1.0 else prog
                
                state = scramble.get_state(local_prog)
                char_current, char_next, _, flap_prog, _ = state
                tile.set_state(char_current, char_next, flap_prog)
                
                # Check for flap flip (passing 0.5) to trigger sound
                # Actually, RapidLetterScramble flaps multiple times. We can detect when current_flap_idx changes.
                # Re-calculate current_flap_idx to detect change
                if local_prog < 1.0:
                    eased_p = Ease.out_cubic(local_prog)
                    flap_idx = int(eased_p * scramble.total_flaps)
                else:
                    flap_idx = scramble.total_flaps
                    
                current_flaps.append(flap_idx)
                
                if flap_idx != last_flaps[i] and last_flaps[i] != -1:
                    if self.sound_sync:
                        self.sound_sync.trigger_flap()
            else:
                current_flaps.append(-1)
                
        self._last_flaps = current_flaps
        
        # We need to call compute_layout if it was a FlexContainer, but it's just a Node, and we manually set positions.
        super().draw(ctx, time)

