import numpy as np
import cairo
from PIL import Image, ImageFilter
from typing import Tuple

try:
    from vibmo.fx.filters import Filter
except ImportError:
    class Filter:
        def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
            raise NotImplementedError

class AsciiMatrixArtShader(Filter):
    """
    Converts full video frame luminance into real-time dynamic ASCII character grid.
    """
    def __init__(self, char_set: str = "@%#*+=-:. ", grid_size: int = 10):
        self.char_set = char_set
        self.grid_size = grid_size
        self.num_chars = len(char_set)

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        h, w, _ = rgba.shape
        img = Image.fromarray(rgba[:, :, :3])

        # Calculate grid dimensions
        cols = max(1, w // self.grid_size)
        rows = max(1, h // self.grid_size)

        # Resize image to grid size to get average luminance per block
        small_img = img.resize((cols, rows), Image.Resampling.NEAREST).convert('L')
        luma_arr = np.array(small_img, dtype=np.float32)

        # Normalize to 0 - num_chars - 1
        idx_arr = np.clip((luma_arr / 255.0) * self.num_chars, 0, self.num_chars - 1).astype(int)

        # Create output surface
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        ctx = cairo.Context(surface)

        ctx.set_source_rgba(0, 0, 0, 1) # Black background
        ctx.paint()

        ctx.select_font_face("monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(self.grid_size)
        ctx.set_source_rgba(0, 1, 0, 1) # Matrix Green default

        for r in range(rows):
            for c in range(cols):
                char_idx = idx_arr[r, c]
                char = self.char_set[char_idx]
                ctx.move_to(c * self.grid_size, (r + 1) * self.grid_size)
                ctx.show_text(char)

        # Get raw data and convert to numpy array
        buf = surface.get_data()
        out = np.ndarray(shape=(h, w, 4), dtype=np.uint8, buffer=buf)
        # Cairo is BGRA, convert to RGBA
        out = out[:, :, [2, 1, 0, 3]].copy()

        return out


class TerminalColorPaletteFilter(Filter):
    """
    Monochromatic color remapping (Matrix Green, Amber CRT, Cyberpunk Cyan/Magenta).
    """
    def __init__(self, palette: str = "matrix"):
        self.palette = palette.lower()
        if self.palette == "matrix":
            self.color = np.array([0, 255, 0], dtype=np.float32)
        elif self.palette == "amber":
            self.color = np.array([255, 176, 0], dtype=np.float32)
        elif self.palette == "cyan":
            self.color = np.array([0, 255, 255], dtype=np.float32)
        elif self.palette == "magenta":
            self.color = np.array([255, 0, 255], dtype=np.float32)
        else:
            self.color = np.array([0, 255, 0], dtype=np.float32)

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        h, w, _ = rgba.shape
        rgb = rgba[:, :, :3].astype(np.float32)
        luma = (0.2126 * rgb[:, :, 0] + 0.7152 * rgb[:, :, 1] + 0.0722 * rgb[:, :, 2]) / 255.0

        out_rgb = np.clip(luma[:, :, None] * self.color, 0, 255).astype(np.uint8)

        out = rgba.copy()
        out[:, :, :3] = out_rgb
        return out


class DynamicCharResolutionGrid(Filter):
    """
    Adjustable grid cell granularity.
    """
    def __init__(self, cols: int = 80, rows: int = 45):
        self.cols = cols
        self.rows = rows

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        h, w, _ = rgba.shape
        img = Image.fromarray(rgba)

        small_img = img.resize((self.cols, self.rows), Image.Resampling.NEAREST)
        pixelated = small_img.resize((w, h), Image.Resampling.NEAREST)

        return np.array(pixelated)


class EdgeContourAsciiOverlay(Filter):
    """
    Blends ASCII edge outlines with underlying video graphics.
    """
    def __init__(self, threshold: float = 0.2, char: str = "#", grid_size: int = 10, intensity: float = 1.0):
        self.threshold = threshold
        self.char = char
        self.grid_size = grid_size
        self.intensity = intensity

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        h, w, _ = rgba.shape
        img = Image.fromarray(rgba[:, :, :3])

        edges = img.filter(ImageFilter.FIND_EDGES).convert('L')
        edges_arr = np.array(edges, dtype=np.float32) / 255.0

        edge_mask = np.clip((edges_arr - self.threshold) / (1.0 - self.threshold), 0.0, 1.0)

        cols = max(1, w // self.grid_size)
        rows = max(1, h // self.grid_size)

        # We don't downsample the edge mask with PIL resizing as it loses the thin edges easily.
        # Instead, we evaluate the edge mask by checking the maximum value in each grid cell.

        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        ctx = cairo.Context(surface)

        ctx.select_font_face("monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(self.grid_size)
        ctx.set_source_rgba(0, 1, 0, 1) # Matrix Green default

        for r in range(rows):
            for c in range(cols):
                y0, y1 = r * self.grid_size, min((r + 1) * self.grid_size, h)
                x0, x1 = c * self.grid_size, min((c + 1) * self.grid_size, w)

                # Check if there is a significant edge in this cell
                if np.max(edge_mask[y0:y1, x0:x1]) > 0.5:
                    ctx.move_to(c * self.grid_size, (r + 1) * self.grid_size)
                    ctx.show_text(self.char)

        buf = surface.get_data()
        ascii_out = np.ndarray(shape=(h, w, 4), dtype=np.uint8, buffer=buf)
        ascii_out = ascii_out[:, :, [2, 1, 0, 3]]

        ascii_rgb = ascii_out[:, :, :3].astype(np.float32)
        ascii_alpha = (ascii_out[:, :, 3] / 255.0)[:, :, None] * self.intensity

        out = rgba.copy()
        out_rgb = out[:, :, :3].astype(np.float32)

        blended = np.clip(out_rgb * (1.0 - ascii_alpha) + ascii_rgb * ascii_alpha, 0, 255).astype(np.uint8)
        out[:, :, :3] = blended
        return out
