"""
Edge and line effects inspired by Remotion's edge detection library.
Includes Outline, ContourLines, RoughenEdges, and DropShadow enhancements.
"""

from __future__ import annotations
import math
import numpy as np
from typing import Any, Optional, Tuple, Union
from enum import Enum
from dataclasses import dataclass
from PIL import Image, ImageFilter, ImageOps


class EdgeDetectionMethod(Enum):
    """Methods for edge detection."""
    SOBEL = "sobel"
    LAPLACIAN = "laplacian"
    CANNY = "canny"
    PREWITT = "prewitt"


@dataclass
class EdgeParams:
    """Parameters for edge effects."""
    threshold: float = 0.1
    thickness: int = 2
    smooth: bool = True
    invert: bool = False


class Outline:
    """
    Edge detection outline effect.
    Creates outlines around objects in the image.
    """

    def __init__(self,
                 color: Union[str, tuple] = (1.0, 1.0, 1.0, 1.0),
                 thickness: int = 2,
                 threshold: float = 0.1,
                 method: Union[str, EdgeDetectionMethod] = EdgeDetectionMethod.SOBEL) -> None:
        self.color = self._parse_color(color)
        self.thickness = max(1, thickness)
        self.threshold = max(0.0, min(1.0, threshold))
        self.method = EdgeDetectionMethod(method) if isinstance(method, str) else method

    def _parse_color(self, color_input: Union[str, tuple]) -> tuple:
        """Parse color input to RGBA tuple."""
        if isinstance(color_input, tuple):
            return color_input
        elif isinstance(color_input, str):
            color_map = {
                'white': (1.0, 1.0, 1.0, 1.0),
                'black': (0.0, 0.0, 0.0, 1.0),
                'red': (1.0, 0.0, 0.0, 1.0),
                'green': (0.0, 1.0, 0.0, 1.0),
                'blue': (0.0, 0.0, 1.0, 1.0),
                'cyan': (0.0, 1.0, 1.0, 1.0),
                'magenta': (1.0, 0.0, 1.0, 1.0),
                'yellow': (1.0, 1.0, 0.0, 1.0),
            }
            return color_map.get(color_input.lower(), (1.0, 1.0, 1.0, 1.0))
        return (1.0, 1.0, 1.0, 1.0)

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        """Apply outline effect to image."""
        h, w, c = rgba.shape
        result = rgba.copy()
        
        # Convert to PIL Image for edge detection
        pil_img = Image.fromarray(rgba, "RGBA")
        
        # Convert to grayscale for edge detection
        gray_img = pil_img.convert("L")
        
        # Apply edge detection based on method
        if self.method == EdgeDetectionMethod.SOBEL:
            edges = self._sobel_edge_detection(gray_img)
        elif self.method == EdgeDetectionMethod.LAPLACIAN:
            edges = self._laplacian_edge_detection(gray_img)
        elif self.method == EdgeDetectionMethod.PREWITT:
            edges = self._prewitt_edge_detection(gray_img)
        else:  # CANNY
            edges = self._canny_edge_detection(gray_img)
        
        # Convert edges to numpy array
        edges_array = np.array(edges)
        
        # Apply threshold
        edge_mask = edges_array > (255 * self.threshold)
        
        # Create outline with specified color
        color_arr = np.array([self.color[0] * 255, self.color[1] * 255, 
                            self.color[2] * 255, self.color[3] * 255], dtype=np.uint8)
        
        # Apply outline to result
        for i in range(3):
            outline_channel = np.where(edge_mask, color_arr[i], result[:, :, i])
            result[:, :, i] = outline_channel
        
        return result

    def _sobel_edge_detection(self, gray_img: Image.Image) -> Image.Image:
        """Sobel edge detection."""
        # Convert to numpy array
        gray_array = np.array(gray_img)
        
        # Sobel kernels
        sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
        sobel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
        
        # Apply convolution
        edges_x = self._convolve(gray_array, sobel_x)
        edges_y = self._convolve(gray_array, sobel_y)
        
        # Combine edges
        edges = np.sqrt(edges_x**2 + edges_y**2)
        edges = np.clip(edges, 0, 255).astype(np.uint8)
        
        return Image.fromarray(edges)

    def _laplacian_edge_detection(self, gray_img: Image.Image) -> Image.Image:
        """Laplacian edge detection."""
        gray_array = np.array(gray_img)
        
        # Laplacian kernel
        laplacian = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]])
        
        edges = self._convolve(gray_array, laplacian)
        edges = np.abs(edges)
        edges = np.clip(edges, 0, 255).astype(np.uint8)
        
        return Image.fromarray(edges)

    def _prewitt_edge_detection(self, gray_img: Image.Image) -> Image.Image:
        """Prewitt edge detection."""
        gray_array = np.array(gray_img)
        
        # Prewitt kernels
        prewitt_x = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]])
        prewitt_y = np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]])
        
        edges_x = self._convolve(gray_array, prewitt_x)
        edges_y = self._convolve(gray_array, prewitt_y)
        
        edges = np.sqrt(edges_x**2 + edges_y**2)
        edges = np.clip(edges, 0, 255).astype(np.uint8)
        
        return Image.fromarray(edges)

    def _canny_edge_detection(self, gray_img: Image.Image) -> Image.Image:
        """Simplified Canny edge detection."""
        # Use PIL's built-in edge detection as fallback
        edges = gray_img.filter(ImageFilter.FIND_EDGES)
        return edges

    def _convolve(self, image: np.ndarray, kernel: np.ndarray) -> np.ndarray:
        """Simple 2D convolution."""
        h, w = image.shape
        kh, kw = kernel.shape
        pad_h, pad_w = kh // 2, kw // 2
        
        # Pad image
        padded = np.pad(image, ((pad_h, pad_h), (pad_w, pad_w)), mode='reflect')
        
        # Convolve
        result = np.zeros_like(image, dtype=np.float32)
        for i in range(h):
            for j in range(w):
                result[i, j] = np.sum(padded[i:i+kh, j:j+kw] * kernel)
        
        return result


class ContourLines:
    """
    Topographic contour line effect.
    Creates elevation map-style contour lines based on luminance.
    """

    def __init__(self,
                 line_count: int = 10,
                 line_thickness: int = 1,
                 line_color: Union[str, tuple] = (0.0, 0.0, 0.0, 1.0),
                 background_color: Union[str, tuple] = (1.0, 1.0, 1.0, 1.0)) -> None:
        self.line_count = max(1, line_count)
        self.line_thickness = max(1, line_thickness)
        self.line_color = self._parse_color(line_color)
        self.background_color = self._parse_color(background_color)

    def _parse_color(self, color_input: Union[str, tuple]) -> tuple:
        """Parse color input to RGBA tuple."""
        if isinstance(color_input, tuple):
            return color_input
        elif isinstance(color_input, str):
            color_map = {
                'white': (1.0, 1.0, 1.0, 1.0),
                'black': (0.0, 0.0, 0.0, 1.0),
                'red': (1.0, 0.0, 0.0, 1.0),
                'green': (0.0, 1.0, 0.0, 1.0),
                'blue': (0.0, 0.0, 1.0, 1.0),
            }
            return color_map.get(color_input.lower(), (0.0, 0.0, 0.0, 1.0))
        return (0.0, 0.0, 0.0, 1.0)

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        """Apply contour line effect to image."""
        h, w, c = rgba.shape
        
        # Calculate luminance
        rgb = rgba[:, :, :3].astype(np.float32)
        luminance = (0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]) / 255.0
        
        # Create background
        bg_arr = np.array([self.background_color[0] * 255, self.background_color[1] * 255,
                          self.background_color[2] * 255, self.background_color[3] * 255], dtype=np.uint8)
        result = np.full((h, w, 4), bg_arr)
        
        # Create contour lines
        line_arr = np.array([self.line_color[0] * 255, self.line_color[1] * 255,
                            self.line_color[2] * 255, self.line_color[3] * 255], dtype=np.uint8)
        
        # Generate contour levels
        for i in range(self.line_count):
            level = (i + 1) / (self.line_count + 1)
            
            # Find pixels near this contour level
            contour_mask = np.abs(luminance - level) < 0.05
            
            # Apply line color to contour pixels
            for j in range(4):
                result[:, :, j] = np.where(contour_mask, line_arr[j], result[:, :, j])
        
        return result


class RoughenEdges:
    """
    Rough edge effect for organic, distressed look.
    Adds noise and irregularity to edges for grunge aesthetic.
    """

    def __init__(self,
                 roughness: float = 0.5,
                 edge_amount: float = 0.3,
                 seed: Optional[int] = None) -> None:
        self.roughness = max(0.0, min(1.0, roughness))
        self.edge_amount = max(0.0, min(1.0, edge_amount))
        self.seed = seed

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        """Apply rough edge effect to image."""
        h, w, c = rgba.shape
        result = rgba.copy()
        
        # Create random noise
        rng = np.random.RandomState(self.seed or int(time * 1000) % 100000)
        noise = rng.randn(h, w, 3) * self.roughness * 50
        
        # Apply noise to RGB channels
        result[:, :, :3] = np.clip(result[:, :, :3].astype(np.float32) + noise, 0, 255).astype(np.uint8)
        
        # Add edge roughening using displacement
        if self.edge_amount > 0:
            # Create displacement map
            displacement = rng.randn(h, w) * self.edge_amount * 3
            
            # Apply displacement (simplified version)
            for i in range(3):
                channel = result[:, :, i].astype(np.float32)
                # Simple horizontal displacement
                displaced = np.roll(channel, int(displacement[0, 0]), axis=1)
                result[:, :, i] = np.clip(displaced, 0, 255).astype(np.uint8)
        
        return result


class DropShadow:
    """
    Enhanced drop shadow effect with multiple shadow layers.
    Creates realistic shadows with blur and offset.
    """

    def __init__(self,
                 offset_x: int = 10,
                 offset_y: int = 10,
                 blur_radius: int = 8,
                 color: Union[str, tuple] = (0.0, 0.0, 0.0, 0.5),
                 spread: int = 0) -> None:
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.blur_radius = max(0, blur_radius)
        self.color = self._parse_color(color)
        self.spread = max(0, spread)

    def _parse_color(self, color_input: Union[str, tuple]) -> tuple:
        """Parse color input to RGBA tuple."""
        if isinstance(color_input, tuple):
            return color_input
        elif isinstance(color_input, str):
            color_map = {
                'black': (0.0, 0.0, 0.0, 0.5),
                'white': (1.0, 1.0, 1.0, 0.5),
                'red': (1.0, 0.0, 0.0, 0.5),
                'blue': (0.0, 0.0, 1.0, 0.5),
            }
            return color_map.get(color_input.lower(), (0.0, 0.0, 0.0, 0.5))
        return (0.0, 0.0, 0.0, 0.5)

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        """Apply drop shadow to image."""
        h, w, c = rgba.shape
        
        # Create shadow layer
        shadow = np.zeros((h, w, 4), dtype=np.uint8)
        
        # Set shadow color
        color_arr = np.array([self.color[0] * 255, self.color[1] * 255,
                            self.color[2] * 255, self.color[3] * 255], dtype=np.uint8)
        
        # Create alpha mask from original image
        alpha_mask = rgba[:, :, 3] > 0
        
        # Apply offset to shadow
        shadow_y = np.clip(np.arange(h)[:, None] + self.offset_y, 0, h - 1).astype(int)
        shadow_x = np.clip(np.arange(w)[None, :] + self.offset_x, 0, w - 1).astype(int)
        
        # Apply shadow with spread
        if self.spread > 0:
            # Simple morphological dilation without scipy
            for _ in range(self.spread):
                alpha_mask_expanded = np.zeros_like(alpha_mask)
                for y in range(h):
                    for x in range(w):
                        if alpha_mask[y, x]:
                            # Expand to neighbors
                            for dy in [-1, 0, 1]:
                                for dx in [-1, 0, 1]:
                                    ny, nx = y + dy, x + dx
                                    if 0 <= ny < h and 0 <= nx < w:
                                        alpha_mask_expanded[ny, nx] = 1
                alpha_mask = alpha_mask_expanded
        
        # Apply shadow color where alpha mask exists
        for i in range(4):
            for y in range(h):
                for x in range(w):
                    if alpha_mask[y, x]:
                        sy, sx = shadow_y[y, x], shadow_x[y, x]
                        shadow[sy, sx, i] = color_arr[i]
        
        # Apply blur to shadow
        if self.blur_radius > 0:
            pil_shadow = Image.fromarray(shadow, "RGBA")
            blurred_shadow = pil_shadow.filter(ImageFilter.GaussianBlur(self.blur_radius))
            shadow = np.array(blurred_shadow)
        
        # Composite shadow with original image
        result = rgba.copy()
        
        # Blend shadow behind original
        for i in range(4):
            result[:, :, i] = np.where(
                shadow[:, :, 3] > 0,
                (shadow[:, :, i].astype(np.float32) * (shadow[:, :, 3] / 255.0) + 
                 result[:, :, i].astype(np.float32) * (1 - shadow[:, :, 3] / 255.0)).astype(np.uint8),
                result[:, :, i]
            )
        
        return result


class Glow:
    """
    Enhanced glow effect with multiple glow layers.
    Creates beautiful glowing effects around bright areas.
    """

    def __init__(self,
                 radius: int = 20,
                 intensity: float = 0.8,
                 color: Union[str, tuple] = (1.0, 1.0, 1.0, 1.0),
                 threshold: float = 0.5) -> None:
        self.radius = max(1, radius)
        self.intensity = max(0.0, min(1.0, intensity))
        self.color = self._parse_color(color)
        self.threshold = max(0.0, min(1.0, threshold))

    def _parse_color(self, color_input: Union[str, tuple]) -> tuple:
        """Parse color input to RGBA tuple."""
        if isinstance(color_input, tuple):
            return color_input
        elif isinstance(color_input, str):
            color_map = {
                'white': (1.0, 1.0, 1.0, 1.0),
                'cyan': (0.0, 1.0, 1.0, 1.0),
                'orange': (1.0, 0.5, 0.0, 1.0),
                'pink': (1.0, 0.75, 0.8, 1.0),
            }
            return color_map.get(color_input.lower(), (1.0, 1.0, 1.0, 1.0))
        return (1.0, 1.0, 1.0, 1.0)

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        """Apply glow effect to image."""
        h, w, c = rgba.shape
        result = rgba.copy()
        
        # Calculate luminance
        rgb = rgba[:, :, :3].astype(np.float32)
        luminance = (0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]) / 255.0
        
        # Create glow mask based on threshold
        glow_mask = (luminance > self.threshold).astype(np.float32)
        
        # Create glow layer
        glow = np.zeros((h, w, 4), dtype=np.uint8)
        color_arr = np.array([self.color[0] * 255, self.color[1] * 255,
                            self.color[2] * 255, self.color[3] * 255], dtype=np.uint8)
        
        # Apply color to glow areas
        for i in range(4):
            glow[:, :, i] = np.where(glow_mask > 0, color_arr[i], 0)
        
        # Apply blur to glow
        if self.radius > 0:
            pil_glow = Image.fromarray(glow, "RGBA")
            blurred_glow = pil_glow.filter(ImageFilter.GaussianBlur(self.radius))
            glow = np.array(blurred_glow)
        
        # Composite glow with original image
        for i in range(3):
            result[:, :, i] = np.clip(
                result[:, :, i].astype(np.float32) + 
                glow[:, :, i].astype(np.float32) * self.intensity * (glow[:, :, 3] / 255.0),
                0, 255
            ).astype(np.uint8)
        
        return result


# Convenience functions for creating edge effects

def outline(color: Union[str, tuple] = 'white', thickness: int = 2) -> Outline:
    """Create outline effect with common defaults."""
    return Outline(color=color, thickness=thickness)


def contour_lines(line_count: int = 10, line_color: Union[str, tuple] = 'black') -> ContourLines:
    """Create contour line effect with common defaults."""
    return ContourLines(line_count=line_count, line_color=line_color)


def roughen_edges(roughness: float = 0.5, edge_amount: float = 0.3) -> RoughenEdges:
    """Create rough edge effect with common defaults."""
    return RoughenEdges(roughness=roughness, edge_amount=edge_amount)


def drop_shadow(offset_x: int = 10, offset_y: int = 10, blur_radius: int = 8) -> DropShadow:
    """Create drop shadow effect with common defaults."""
    return DropShadow(offset_x=offset_x, offset_y=offset_y, blur_radius=blur_radius)


def glow(radius: int = 20, intensity: float = 0.8, color: Union[str, tuple] = 'white') -> Glow:
    """Create glow effect with common defaults."""
    return Glow(radius=radius, intensity=intensity, color=color)


# Aliases
EdgeGlow = Glow
edge_glow = glow