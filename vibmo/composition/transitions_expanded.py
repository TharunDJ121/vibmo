"""
Expanded transition library with 10+ core transitions.
Inspired by Remotion's transition system with GPU-ready architecture.
"""

from __future__ import annotations
import math
import numpy as np
from PIL import Image, ImageFilter, ImageTransform
from typing import Any, Optional, Tuple, Union
from enum import Enum

from vibmo.core.color import Color, colors
from vibmo.core.easing import Ease, EasingFunc
from vibmo.composition.sequence import Transition
from vibmo.composition.webgl_transitions import WebGL2TransitionEngine, ShaderTransition


class SlideDirection(Enum):
    """Direction for slide transitions."""
    FROM_LEFT = "from-left"
    FROM_RIGHT = "from-right"
    FROM_TOP = "from-top"
    FROM_BOTTOM = "from-bottom"


class Slide(Transition):
    """
    Multi-directional slide transition.
    Entering scene pushes exiting scene in specified direction.
    """

    def __init__(
        self,
        direction: Union[str, SlideDirection] = SlideDirection.FROM_LEFT,
        blur: bool = True,
        duration: float = 0.5,
        ease: Optional[Any] = None,
    ) -> None:
        super().__init__(duration=duration)
        if isinstance(direction, str):
            dir_map = {
                "left": SlideDirection.FROM_LEFT,
                "right": SlideDirection.FROM_RIGHT,
                "top": SlideDirection.FROM_TOP,
                "up": SlideDirection.FROM_TOP,
                "bottom": SlideDirection.FROM_BOTTOM,
                "down": SlideDirection.FROM_BOTTOM,
                "from-left": SlideDirection.FROM_LEFT,
                "from-right": SlideDirection.FROM_RIGHT,
                "from-top": SlideDirection.FROM_TOP,
                "from-bottom": SlideDirection.FROM_BOTTOM,
            }
            self.direction = dir_map.get(direction.lower(), SlideDirection.FROM_LEFT)
        else:
            self.direction = direction
        self.blur = blur
        self.ease = ease or Ease.in_out_cubic

    def blend(self, img_a: np.ndarray, img_b: np.ndarray, progress: float) -> np.ndarray:
        p = self.ease(max(0.0, min(1.0, float(progress)))) if callable(self.ease) else progress
        h, w, _ = img_a.shape
        out = np.zeros_like(img_a)

        shift = int(w * p)
        
        if self.direction == SlideDirection.FROM_LEFT:
            # Slide from left - A moves right, B enters from left
            if shift < w:
                out[:, shift:] = img_a[:, :w - shift]
            if shift > 0:
                out[:, :shift] = img_b[:, w - shift:]
        elif self.direction == SlideDirection.FROM_RIGHT:
            # Slide from right - A moves left, B enters from right
            if shift < w:
                out[:, :w - shift] = img_a[:, shift:]
            if shift > 0:
                out[:, w - shift:] = img_b[:, :shift]
        elif self.direction == SlideDirection.FROM_TOP:
            # Slide from top - A moves down, B enters from top
            if shift < h:
                out[shift:, :] = img_a[:h - shift, :]
            if shift > 0:
                out[:shift, :] = img_b[h - shift:, :]
        else:  # FROM_BOTTOM
            # Slide from bottom - A moves up, B enters from bottom
            if shift < h:
                out[:h - shift, :] = img_a[shift:, :]
            if shift > 0:
                out[h - shift:, :] = img_b[:shift, :]

        # Apply motion blur during peak velocity
        if self.blur and 0.15 < p < 0.85:
            blur_radius = int(math.sin(p * math.pi) * 8.0)
            if blur_radius > 1:
                pil_img = Image.fromarray(out, "RGBA").filter(ImageFilter.BoxBlur(blur_radius))
                out = np.array(pil_img)

        return out


class PushCut(Transition):
    """
    Directional push cut with motion blur.
    More aggressive than slide with faster motion.
    """

    def __init__(self, direction: Union[str, SlideDirection] = SlideDirection.FROM_LEFT,
                 blur: bool = True, duration: float = 0.35) -> None:
        super().__init__(duration=duration)
        self.direction = SlideDirection(direction) if isinstance(direction, str) else direction
        self.blur = blur

    def blend(self, img_a: np.ndarray, img_b: np.ndarray, progress: float) -> np.ndarray:
        p = Ease.in_out_quad(max(0.0, min(1.0, float(progress))))
        h, w, _ = img_a.shape
        out = np.zeros_like(img_a)

        shift = int(w * p)
        
        if self.direction == SlideDirection.FROM_LEFT:
            if shift < w:
                out[:, shift:] = img_a[:, :w - shift]
            if shift > 0:
                out[:, :shift] = img_b[:, w - shift:]
        elif self.direction == SlideDirection.FROM_RIGHT:
            if shift < w:
                out[:, :w - shift] = img_a[:, shift:]
            if shift > 0:
                out[:, w - shift:] = img_b[:, :shift]
        elif self.direction == SlideDirection.FROM_TOP:
            if shift < h:
                out[shift:, :] = img_a[:h - shift, :]
            if shift > 0:
                out[:shift, :] = img_b[h - shift:, :]
        else:  # FROM_BOTTOM
            if shift < h:
                out[:h - shift, :] = img_a[shift:, :]
            if shift > 0:
                out[h - shift:, :] = img_b[:shift, :]

        # Stronger motion blur for push cut
        if self.blur and 0.1 < p < 0.9:
            blur_radius = int(math.sin(p * math.pi) * 12.0)
            if blur_radius > 1:
                pil_img = Image.fromarray(out, "RGBA").filter(ImageFilter.BoxBlur(blur_radius))
                out = np.array(pil_img)

        return out


class Fade(Transition):
    """Simple fade transition with opacity blend."""

    def blend(self, img_a: np.ndarray, img_b: np.ndarray, progress: float) -> np.ndarray:
        p = max(0.0, min(1.0, float(progress)))
        return (img_a.astype(np.float32) * (1.0 - p) + img_b.astype(np.float32) * p).astype(np.uint8)


class Dissolve(Transition):
    """
    Enhanced dissolve with noise/dither pattern.
    Creates a film-like dissolve effect.
    """

    def __init__(self, noise_amount: float = 0.15, duration: float = 0.6) -> None:
        super().__init__(duration=duration)
        self.noise_amount = noise_amount

    def blend(self, img_a: np.ndarray, img_b: np.ndarray, progress: float) -> np.ndarray:
        p = max(0.0, min(1.0, float(progress)))
        
        # Base crossfade
        base = (img_a.astype(np.float32) * (1.0 - p) + img_b.astype(np.float32) * p)
        
        # Add noise for film grain effect
        if self.noise_amount > 0:
            noise = np.random.normal(0, self.noise_amount * 255, base.shape)
            base = np.clip(base + noise, 0, 255)
        
        return base.astype(np.uint8)


class IrisShape(Enum):
    """Shape for iris transitions."""
    CIRCLE = "circle"
    DIAMOND = "diamond"
    SQUARE = "square"
    STAR = "star"


class Iris(Transition):
    """
    Iris wipe transition with customizable shape.
    Scene B reveals through geometric shape opening.
    """

    def __init__(self, shape: Union[str, IrisShape] = IrisShape.CIRCLE,
                 feather: float = 0.1, duration: float = 0.5) -> None:
        super().__init__(duration=duration)
        self.shape = IrisShape(shape) if isinstance(shape, str) else shape
        self.feather = feather

    def blend(self, img_a: np.ndarray, img_b: np.ndarray, progress: float) -> np.ndarray:
        p = Ease.in_out_cubic(max(0.0, min(1.0, float(progress))))
        h, w, _ = img_a.shape

        y, x = np.ogrid[:h, :w]
        cx, cy = w * 0.5, h * 0.5
        
        # Normalize coordinates
        nx = (x - cx) / (w * 0.5)
        ny = (y - cy) / (h * 0.5)
        
        if self.shape == IrisShape.CIRCLE:
            # Circular iris
            radius = np.sqrt(nx**2 + ny**2)
            mask = radius <= p
        elif self.shape == IrisShape.DIAMOND:
            # Diamond iris
            diamond = np.abs(nx) + np.abs(ny)
            mask = diamond <= p
        elif self.shape == IrisShape.SQUARE:
            # Square iris
            square = np.maximum(np.abs(nx), np.abs(ny))
            mask = square <= p
        else:  # STAR
            # Star iris (5-point)
            angle = np.arctan2(ny, nx)
            star_factor = 1.0 - 0.3 * np.cos(5 * angle)
            radius = np.sqrt(nx**2 + ny**2) * star_factor
            mask = radius <= p

        # Apply feathering
        if self.feather > 0:
            feather_range = self.feather
            # Create smooth edges with distance field
            if self.shape == IrisShape.CIRCLE:
                dist = np.abs(radius - p)
            elif self.shape == IrisShape.DIAMOND:
                dist = np.abs(diamond - p)
            elif self.shape == IrisShape.SQUARE:
                dist = np.abs(square - p)
            else:
                dist = np.abs(radius - p)
            
            feather_mask = np.clip(1.0 - (dist / feather_range), 0.0, 1.0)
            mask = mask.astype(float) * feather_mask
        
        # Blend based on mask
        out = img_a.copy()
        if isinstance(mask, np.ndarray):
            mask_3d = np.stack([mask] * 4, axis=-1) if img_a.shape[2] == 4 else np.stack([mask] * 3, axis=-1)
            out = img_a.astype(float) * (1 - mask_3d) + img_b.astype(float) * mask_3d
        else:
            out[mask] = img_b[mask]
        
        return out.astype(np.uint8)


class WipeDirection(Enum):
    """Direction for wipe transitions."""
    LEFT_TO_RIGHT = "left-to-right"
    RIGHT_TO_LEFT = "right-to-left"
    TOP_TO_BOTTOM = "top-to-bottom"
    BOTTOM_TO_TOP = "bottom-to-top"
    DIAGONAL_TL_BR = "diagonal-tl-br"
    DIAGONAL_BL_TR = "diagonal-bl-tr"


class Wipe(Transition):
    """
    Linear wipe transition with multiple direction options.
    """

    def __init__(self, direction: Union[str, WipeDirection] = WipeDirection.LEFT_TO_RIGHT,
                 feather: float = 0.05, duration: float = 0.4) -> None:
        super().__init__(duration=duration)
        self.direction = WipeDirection(direction) if isinstance(direction, str) else direction
        self.feather = feather

    def blend(self, img_a: np.ndarray, img_b: np.ndarray, progress: float) -> np.ndarray:
        p = Ease.in_out_cubic(max(0.0, min(1.0, float(progress))))
        h, w, _ = img_a.shape

        y, x = np.ogrid[:h, :w]
        
        # Normalize coordinates
        nx = x / w
        ny = y / h
        
        if self.direction == WipeDirection.LEFT_TO_RIGHT:
            mask = nx <= p
        elif self.direction == WipeDirection.RIGHT_TO_LEFT:
            mask = nx >= (1.0 - p)
        elif self.direction == WipeDirection.TOP_TO_BOTTOM:
            mask = ny <= p
        elif self.direction == WipeDirection.BOTTOM_TO_TOP:
            mask = ny >= (1.0 - p)
        elif self.direction == WipeDirection.DIAGONAL_TL_BR:
            mask = (nx + ny) / 2 <= p
        else:  # DIAGONAL_BL_TR
            mask = ((1.0 - nx) + ny) / 2 <= p

        # Apply feathering
        if self.feather > 0:
            if self.direction == WipeDirection.LEFT_TO_RIGHT:
                dist = np.abs(nx - p)
            elif self.direction == WipeDirection.RIGHT_TO_LEFT:
                dist = np.abs(nx - (1.0 - p))
            elif self.direction == WipeDirection.TOP_TO_BOTTOM:
                dist = np.abs(ny - p)
            elif self.direction == WipeDirection.BOTTOM_TO_TOP:
                dist = np.abs(ny - (1.0 - p))
            elif self.direction == WipeDirection.DIAGONAL_TL_BR:
                dist = np.abs((nx + ny) / 2 - p)
            else:
                dist = np.abs(((1.0 - nx) + ny) / 2 - p)
            
            feather_mask = np.clip(1.0 - (dist / self.feather), 0.0, 1.0)
            mask = mask.astype(float) * feather_mask

        out = img_a.copy()
        if isinstance(mask, np.ndarray):
            mask_3d = np.stack([mask] * 4, axis=-1) if img_a.shape[2] == 4 else np.stack([mask] * 3, axis=-1)
            out = img_a.astype(float) * (1 - mask_3d) + img_b.astype(float) * mask_3d
        else:
            out[mask] = img_b[mask]
        
        return out.astype(np.uint8)


class ZoomBlur(Transition):
    """
    Radial zoom blur transition.
    Creates dramatic zoom effect with motion blur.
    """

    def __init__(self, max_scale: float = 1.8, blur_intensity: float = 0.3, duration: float = 0.5) -> None:
        super().__init__(duration=duration)
        self.max_scale = max_scale
        self.blur_intensity = blur_intensity

    def blend(self, img_a: np.ndarray, img_b: np.ndarray, progress: float) -> np.ndarray:
        p = Ease.in_out_cubic(max(0.0, min(1.0, float(progress))))
        h, w, _ = img_a.shape

        if p < 0.5:
            # Zoom blur A
            local_p = p * 2.0
            scale = 1.0 + (self.max_scale - 1.0) * Ease.in_expo(local_p)
            pil_a = Image.fromarray(img_a, "RGBA")
            nw, nh = int(w * scale), int(h * scale)
            zoomed = pil_a.resize((nw, nh), Image.Resampling.BILINEAR)
            
            # Apply radial blur
            if self.blur_intensity > 0:
                blur_radius = int(local_p * 20 * self.blur_intensity)
                if blur_radius > 1:
                    zoomed = zoomed.filter(ImageFilter.GaussianBlur(blur_radius))
            
            x0 = (nw - w) // 2
            y0 = (nh - h) // 2
            return np.array(zoomed.crop((x0, y0, x0 + w, y0 + h)))
        else:
            # Zoom blur B (reverse)
            local_p = (p - 0.5) * 2.0
            scale = self.max_scale - (self.max_scale - 1.0) * Ease.out_expo(local_p)
            pil_b = Image.fromarray(img_b, "RGBA")
            nw, nh = int(w * scale), int(h * scale)
            zoomed = pil_b.resize((nw, nh), Image.Resampling.BILINEAR)
            
            # Apply radial blur
            if self.blur_intensity > 0:
                blur_radius = int((1.0 - local_p) * 20 * self.blur_intensity)
                if blur_radius > 1:
                    zoomed = zoomed.filter(ImageFilter.GaussianBlur(blur_radius))
            
            x0 = (nw - w) // 2
            y0 = (nh - h) // 2
            return np.array(zoomed.crop((x0, y0, x0 + w, y0 + h)))


class Ripple(Transition):
    """
    Water ripple displacement transition.
    Creates organic ripple distortion during transition.
    """

    def __init__(self, amplitude: float = 50.0, frequency: float = 3.0, duration: float = 0.6) -> None:
        super().__init__(duration=duration)
        self.amplitude = amplitude
        self.frequency = frequency

    def blend(self, img_a: np.ndarray, img_b: np.ndarray, progress: float) -> np.ndarray:
        p = Ease.in_out_cubic(max(0.0, min(1.0, float(progress))))
        h, w, _ = img_a.shape

        # Create ripple displacement map
        y, x = np.ogrid[:h, :w]
        cx, cy = w * 0.5, h * 0.5
        
        # Distance from center
        dist = np.sqrt((x - cx)**2 + (y - cy)**2)
        
        # Ripple effect based on distance and time
        ripple = np.sin(dist * self.frequency * 0.01 - p * math.pi * 2) * self.amplitude * p
        
        # Apply displacement to create distortion
        # Base crossfade
        base = (img_a.astype(np.float32) * (1.0 - p) + img_b.astype(np.float32) * p)
        
        # Add ripple distortion using numpy roll for simulation
        # In full implementation would use proper displacement mapping
        ripple_shift = int(ripple.max() * p) if ripple.max() > 0 else 0
        if ripple_shift > 0:
            # Simple shift to simulate ripple (for full effect need proper displacement)
            distorted = np.roll(base, ripple_shift, axis=1)
            base = base.astype(float) * 0.7 + distorted.astype(float) * 0.3
        
        return base.astype(np.uint8)


class FlipDirection(Enum):
    """Direction for flip transitions."""
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


class Flip(Transition):
    """
    3D card flip transition.
    Simulates 3D rotation along specified axis.
    """

    def __init__(self, direction: Union[str, FlipDirection] = FlipDirection.HORIZONTAL,
                 duration: float = 0.6) -> None:
        super().__init__(duration=duration)
        self.direction = FlipDirection(direction) if isinstance(direction, str) else direction

    def blend(self, img_a: np.ndarray, img_b: np.ndarray, progress: float) -> np.ndarray:
        p = Ease.in_out_cubic(max(0.0, min(1.0, float(progress))))
        h, w, _ = img_a.shape

        if p < 0.5:
            # First half of flip - shrink A
            local_p = p * 2.0
            scale = math.cos(local_p * math.pi * 0.5)
            
            if self.direction == FlipDirection.HORIZONTAL:
                nw = int(w * scale)
                nh = h
            else:
                nw = w
                nh = int(h * scale)
            
            if nw > 0 and nh > 0:
                pil_a = Image.fromarray(img_a, "RGBA")
                resized = pil_a.resize((nw, nh), Image.Resampling.BILINEAR)
                
                # Center the scaled image
                result = Image.new("RGBA", (w, h), (0, 0, 0, 0))
                x0 = (w - nw) // 2
                y0 = (h - nh) // 2
                result.paste(resized, (x0, y0))
                return np.array(result)
            return img_a
        else:
            # Second half of flip - expand B
            local_p = (p - 0.5) * 2.0
            scale = math.sin(local_p * math.pi * 0.5)
            
            if self.direction == FlipDirection.HORIZONTAL:
                nw = int(w * scale)
                nh = h
            else:
                nw = w
                nh = int(h * scale)
            
            if nw > 0 and nh > 0:
                pil_b = Image.fromarray(img_b, "RGBA")
                resized = pil_b.resize((nw, nh), Image.Resampling.BILINEAR)
                
                # Center the scaled image
                result = Image.new("RGBA", (w, h), (0, 0, 0, 0))
                x0 = (w - nw) // 2
                y0 = (h - nh) // 2
                result.paste(resized, (x0, y0))
                return np.array(result)
            return img_b


class BookFlipDirection(Enum):
    """Direction for book flip transitions."""
    FROM_LEFT = "from-left"
    FROM_RIGHT = "from-right"
    FROM_TOP = "from-top"
    FROM_BOTTOM = "from-bottom"


class BookFlip(Transition):
    """
    Page flip effect with realistic shading.
    Simulates turning a page in a book.
    """

    def __init__(self, direction: Union[str, BookFlipDirection] = BookFlipDirection.FROM_RIGHT,
                 shading: bool = True, duration: float = 0.7) -> None:
        super().__init__(duration=duration)
        self.direction = BookFlipDirection(direction) if isinstance(direction, str) else direction
        self.shading = shading

    def blend(self, img_a: np.ndarray, img_b: np.ndarray, progress: float) -> np.ndarray:
        p = Ease.in_out_cubic(max(0.0, min(1.0, float(progress))))
        h, w, _ = img_a.shape

        # Simulate page flip with perspective distortion
        # This is a simplified version - full implementation would use 3D transforms
        
        if self.direction == BookFlipDirection.FROM_RIGHT:
            # Flip from right side
            if p < 0.5:
                # Page A curling
                local_p = p * 2.0
                curl_width = int(w * local_p * 0.3)
                
                # Create curling effect by shrinking right side
                result = img_a.copy()
                if curl_width > 0:
                    # Apply shading to curled area
                    if self.shading:
                        shade_factor = 1.0 - (local_p * 0.5)
                        result[:, -curl_width:] = (result[:, -curl_width:].astype(float) * shade_factor).astype(np.uint8)
                
                return result
            else:
                # Page B revealing
                local_p = (p - 0.5) * 2.0
                reveal_width = int(w * local_p)
                
                result = img_b.copy()
                if reveal_width > 0 and reveal_width < w:
                    # Blend between images
                    result[:, :reveal_width] = img_b[:, :reveal_width]
                    result[:, reveal_width:] = img_a[:, reveal_width:]
                    
                    # Apply shading to transition area
                    if self.shading:
                        shade_factor = 0.7 + (local_p * 0.3)
                        transition_width = min(50, w - reveal_width)
                        if transition_width > 0:
                            result[:, reveal_width:reveal_width + transition_width] = (
                                result[:, reveal_width:reveal_width + transition_width].astype(float) * shade_factor
                            ).astype(np.uint8)
                
                return result
        else:
            # Other directions - simplified implementation
            return (img_a.astype(np.float32) * (1.0 - p) + img_b.astype(np.float32) * p).astype(np.uint8)


# Convenience functions for creating transitions with default parameters

def slide(direction: Union[str, SlideDirection] = SlideDirection.FROM_LEFT, 
          duration: float = 0.5) -> Slide:
    """Create a slide transition with defaults."""
    return Slide(direction=direction, duration=duration)


def push_cut(direction: Union[str, SlideDirection] = SlideDirection.FROM_LEFT,
             duration: float = 0.35) -> PushCut:
    """Create a push cut transition with defaults."""
    return PushCut(direction=direction, duration=duration)


def fade(duration: float = 0.4) -> Fade:
    """Create a fade transition with defaults."""
    return Fade(duration=duration)


def dissolve(noise_amount: float = 0.15, duration: float = 0.6) -> Dissolve:
    """Create a dissolve transition with defaults."""
    return Dissolve(noise_amount=noise_amount, duration=duration)


def iris(shape: Union[str, IrisShape] = IrisShape.CIRCLE,
         duration: float = 0.5) -> Iris:
    """Create an iris transition with defaults."""
    return Iris(shape=shape, duration=duration)


def wipe(direction: Union[str, WipeDirection] = WipeDirection.LEFT_TO_RIGHT,
         duration: float = 0.4) -> Wipe:
    """Create a wipe transition with defaults."""
    return Wipe(direction=direction, duration=duration)


def zoom_blur(max_scale: float = 1.8, duration: float = 0.5) -> ZoomBlur:
    """Create a zoom blur transition with defaults."""
    return ZoomBlur(max_scale=max_scale, duration=duration)


def ripple(amplitude: float = 50.0, duration: float = 0.6) -> Ripple:
    """Create a ripple transition with defaults."""
    return Ripple(amplitude=amplitude, duration=duration)


def flip(direction: Union[str, FlipDirection] = FlipDirection.HORIZONTAL,
          duration: float = 0.6) -> Flip:
    """Create a flip transition with defaults."""
    return Flip(direction=direction, duration=duration)


def book_flip(direction: Union[str, BookFlipDirection] = BookFlipDirection.FROM_RIGHT,
              duration: float = 0.7) -> BookFlip:
    """Create a book flip transition with defaults."""
    return BookFlip(direction=direction, duration=duration)