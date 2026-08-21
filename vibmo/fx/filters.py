"""
Film grain, Noise, Vignette, Blur, and Post-Processing Filters.
"""

from __future__ import annotations
import numpy as np
from PIL import Image, ImageFilter
from typing import Any, Tuple


class FilmGrain:
    """Adds subtle, organic film grain noise to rendered frames without noisy dark speckles."""

    def __init__(self, amount: float = 0.008, luminance_weighted: bool = True) -> None:
        self.amount = float(amount)
        self.luminance_weighted = luminance_weighted

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        if self.amount <= 1e-4:
            return rgba
        h, w, c = rgba.shape
        rng = np.random.RandomState(int((time * 1000) % 100000))
        noise = (rng.randn(h, w, 1) * self.amount * 255.0).astype(np.float32)
        
        rgb = rgba[:, :, :3].astype(np.float32)
        
        if self.luminance_weighted:
            # Calculate luminance (0.0 to 1.0) and suppress noise in deep blacks and highlights
            luma = (0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]) / 255.0
            # Keep deep blacks velvety and clean
            weight = np.clip(np.sin(luma * np.pi) * 1.2, 0.0, 1.0)[:, :, np.newaxis]
            noise = noise * weight

        rgb = np.clip(rgb + noise, 0, 255).astype(np.uint8)
        
        out = rgba.copy()
        out[:, :, :3] = rgb
        return out


class Vignette:
    """Adds a smooth dark optical falloff towards the edges of the frame."""

    def __init__(self, intensity: float = 0.35, radius: float = 0.75) -> None:
        self.intensity = float(intensity)
        self.radius = float(radius)

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        if self.intensity <= 0:
            return rgba
        h, w, _ = rgba.shape
        y, x = np.ogrid[:h, :w]
        cx, cy = w * 0.5, h * 0.5
        max_dist = np.hypot(cx, cy)
        
        dist = np.hypot(x - cx, y - cy) / max_dist
        falloff = np.clip((dist - self.radius) / (1.0 - self.radius), 0.0, 1.0)
        mask = (1.0 - (falloff * self.intensity)).astype(np.float32)
        mask = mask[:, :, np.newaxis]

        rgb = (rgba[:, :, :3].astype(np.float32) * mask).astype(np.uint8)
        out = rgba.copy()
        out[:, :, :3] = rgb
        return out


class BackdropBlur:
    """Gaussian background blur descriptor for glassmorphic cards."""
    def __init__(self, radius: float = 24.0) -> None:
        self.radius = float(radius)


class MotionBlur:
    """Sub-frame temporal motion blur post-processing descriptor."""
    def __init__(self, shutter_angle: float = 180.0, samples: int = 6) -> None:
        self.shutter_angle = float(shutter_angle)
        self.samples = int(samples)


class Bloom:
    """
    Cinematic emissive bloom and multi-octave glow filter.
    Extracts luminous highlights and diffuses them softly across the scene.
    """

    def __init__(
        self,
        threshold: float = 0.65,
        intensity: float = 0.45,
        radius: float = 24.0,
    ) -> None:
        self.threshold = float(threshold)
        self.intensity = float(intensity)
        self.radius = float(radius)

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        if self.intensity <= 0.001:
            return rgba

        h, w, _ = rgba.shape
        rgb = rgba[:, :, :3].astype(np.float32)

        # 1. High-pass threshold filter
        luma = (0.2126 * rgb[:, :, 0] + 0.7152 * rgb[:, :, 1] + 0.0722 * rgb[:, :, 2]) / 255.0
        thresh_val = self.threshold
        bright_mask = np.clip((luma - thresh_val) / max(0.01, (1.0 - thresh_val)), 0.0, 1.0)
        bright_pixels = (rgb * bright_mask[:, :, np.newaxis]).astype(np.uint8)

        # 2. Fast multi-scale Gaussian blur on downscaled image
        img_bright = Image.fromarray(bright_pixels, "RGB")
        scale_fac = 0.25
        sw, sh = max(1, int(w * scale_fac)), max(1, int(h * scale_fac))
        img_small = img_bright.resize((sw, sw * h // w), Image.Resampling.BILINEAR)

        # Octave 1: tight bloom
        blur1 = img_small.filter(ImageFilter.GaussianBlur(self.radius * scale_fac * 0.5))
        # Octave 2: wide ambient bloom
        blur2 = img_small.filter(ImageFilter.GaussianBlur(self.radius * scale_fac * 1.5))

        arr1 = np.array(blur1.resize((w, h), Image.Resampling.BILINEAR), dtype=np.float32)
        arr2 = np.array(blur2.resize((w, h), Image.Resampling.BILINEAR), dtype=np.float32)

        bloom_combined = (arr1 * 0.6 + arr2 * 0.4) * self.intensity

        # 3. Additive composite with saturation preservation
        out_rgb = np.clip(rgb + bloom_combined, 0, 255).astype(np.uint8)
        out = rgba.copy()
        out[:, :, :3] = out_rgb
        return out


class Glow(Bloom):
    """Alias for Bloom with higher default intensity for neon graphics."""
    def __init__(self, intensity: float = 0.7, radius: float = 32.0, threshold: float = 0.5) -> None:
        super().__init__(threshold=threshold, intensity=intensity, radius=radius)


class ChromaticAberration:
    """
    Simulates optical lens chromatic dispersion by radially separating RGB color channels.
    """

    def __init__(self, offset: float = 3.0) -> None:
        self.offset = float(offset)

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        if self.offset <= 0.1:
            return rgba

        h, w, _ = rgba.shape
        img = Image.fromarray(rgba, "RGBA")
        r, g, b, a = img.split()

        # Scale Red slightly up (expansion) and Blue slightly down (shrink)
        shift = self.offset
        rw = int(w + shift * 2)
        rh = int(h + shift * 2)
        r_scaled = r.resize((rw, rh), Image.Resampling.BILINEAR).crop((int(shift), int(shift), int(shift + w), int(shift + h)))

        bw = max(1, int(w - shift * 2))
        bh = max(1, int(h - shift * 2))
        b_scaled = Image.new("L", (w, h), 0)
        b_shrunk = b.resize((bw, bh), Image.Resampling.BILINEAR)
        b_scaled.paste(b_shrunk, (int(shift), int(shift)))

        merged = Image.merge("RGBA", (r_scaled, g, b_scaled, a))
        return np.array(merged)


class DepthOfField:
    """
    Cinematic optical Depth-of-Field (DoF) and Bokeh Blur filter.
    Blurs out-of-focus foreground and background elements with luminous circular bokeh discs.
    """

    def __init__(
        self,
        focus_y: float = 0.5,
        focus_width: float = 0.25,
        blur_radius: float = 18.0,
        bokeh_intensity: float = 1.6,
        falloff_power: float = 2.0,
    ) -> None:
        self.focus_y = float(focus_y)
        self.focus_width = max(0.01, float(focus_width))
        self.blur_radius = max(0.0, float(blur_radius))
        self.bokeh_intensity = float(bokeh_intensity)
        self.falloff_power = float(falloff_power)

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        if self.blur_radius <= 0.5:
            return rgba

        h, w, _ = rgba.shape
        img = Image.fromarray(rgba, "RGBA")
        rgb = rgba[:, :, :3].astype(np.float32)

        # 1. Compute Circle of Confusion (CoC) depth map across frame height
        y_coords = np.linspace(0.0, 1.0, h)[:, np.newaxis]
        dist_from_focus = np.abs(y_coords - self.focus_y)
        # Inside focus_width/2 -> blur is 0. Outside -> ramps smoothly to 1.0
        coc = np.clip((dist_from_focus - self.focus_width * 0.5) / (0.5 - self.focus_width * 0.5 + 1e-4), 0.0, 1.0)
        coc = (coc ** self.falloff_power)[:, :, np.newaxis]

        # 2. Multi-tier progressive optical blur
        # Base blur
        blur_img = img.filter(ImageFilter.GaussianBlur(self.blur_radius * 0.5))
        heavy_blur_img = img.filter(ImageFilter.GaussianBlur(self.blur_radius))

        arr_mid = np.array(blur_img)[:, :, :3].astype(np.float32)
        arr_heavy = np.array(heavy_blur_img)[:, :, :3].astype(np.float32)

        blurred_rgb = arr_mid * 0.4 + arr_heavy * 0.6

        # 3. Luminous Bokeh highlights extraction
        luma = (0.2126 * rgb[:, :, 0] + 0.7152 * rgb[:, :, 1] + 0.0722 * rgb[:, :, 2]) / 255.0
        bokeh_mask = np.clip((luma - 0.7) / 0.3, 0.0, 1.0)[:, :, np.newaxis]
        bokeh_disc = np.array(Image.fromarray((rgb * bokeh_mask).astype(np.uint8)).filter(ImageFilter.GaussianBlur(self.blur_radius * 0.8)), dtype=np.float32)

        enhanced_blur = blurred_rgb + bokeh_disc * (self.bokeh_intensity - 1.0) * coc

        # 4. Alpha blend based on CoC
        final_rgb = np.clip(rgb * (1.0 - coc) + enhanced_blur * coc, 0, 255).astype(np.uint8)

        out = rgba.copy()
        out[:, :, :3] = final_rgb
        return out


class TiltShift(DepthOfField):
    """Miniature / Macro tilt-shift focus filter with shallow depth of field."""
    def __init__(
        self,
        focus_y: float = 0.5,
        focus_width: float = 0.20,
        blur_radius: float = 24.0,
        bokeh_intensity: float = 1.8,
    ) -> None:
        super().__init__(
            focus_y=focus_y,
            focus_width=focus_width,
            blur_radius=blur_radius,
            bokeh_intensity=bokeh_intensity,
            falloff_power=2.2,
        )


class Dither:
    """
    Spatial triangular blue-noise dithering to eliminate 8-bit gradient banding in dark scenes.
    """

    def __init__(self, amount: float = 1.0, levels: Optional[int] = None) -> None:
        self.amount = float(amount)
        self.levels = levels

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        if self.amount <= 0.01:
            return rgba

        h, w, _ = rgba.shape
        rng = np.random.RandomState(42)
        dither_noise = (rng.rand(h, w, 1) + rng.rand(h, w, 1) - 1.0) * self.amount

        rgb = rgba[:, :, :3].astype(np.float32)
        rgb_dithered = np.clip(rgb + dither_noise, 0, 255).astype(np.uint8)

        out = rgba.copy()
        out[:, :, :3] = rgb_dithered
        return out


# =========================================================================
# NEW PHASE 3 PRODUCTION POST-PROCESSING FILTERS
# =========================================================================

class ColorCorrection:
    """
    Primary Color Grading: Lift, Gamma, Gain, Exposure, Contrast, Saturation, Temperature, and Tint.
    Directly binds with DaVinci Resolve color wheels in Vibmo Studio Pro.
    """

    def __init__(
        self,
        exposure: float = 0.0,
        contrast: float = 1.0,
        saturation: float = 1.0,
        temperature: float = 0.0,
        tint: float = 0.0,
        lift: Tuple[float, float, float] = (0.0, 0.0, 0.0),
        gamma: Tuple[float, float, float] = (1.0, 1.0, 1.0),
        gain: Tuple[float, float, float] = (1.0, 1.0, 1.0),
    ) -> None:
        self.exposure = float(exposure)
        self.contrast = float(contrast)
        self.saturation = float(saturation)
        self.temperature = float(temperature)
        self.tint = float(tint)
        self.lift = np.array(lift, dtype=np.float32)
        self.gamma = np.array(gamma, dtype=np.float32)
        self.gain = np.array(gain, dtype=np.float32)

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        rgb = rgba[:, :, :3].astype(np.float32) / 255.0

        # 1. Lift, Gamma, Gain
        # Lift affects shadows, Gain affects highlights, Gamma affects midtones
        lifted = rgb * self.gain + self.lift * (1.0 - rgb)
        lifted = np.clip(lifted, 0.0, 10.0)
        gamma_safe = np.maximum(1e-3, self.gamma)
        graded = np.power(lifted, 1.0 / gamma_safe)

        # 2. Exposure & Contrast
        if abs(self.exposure) > 1e-4:
            graded = graded * (2.0 ** self.exposure)
        if abs(self.contrast - 1.0) > 1e-4:
            graded = 0.5 + (graded - 0.5) * self.contrast

        # 3. Saturation
        if abs(self.saturation - 1.0) > 1e-4:
            luma = 0.2126 * graded[:, :, 0] + 0.7152 * graded[:, :, 1] + 0.0722 * graded[:, :, 2]
            luma = luma[:, :, np.newaxis]
            graded = luma + (graded - luma) * self.saturation

        # 4. Temperature & Tint
        if abs(self.temperature) > 1e-4 or abs(self.tint) > 1e-4:
            graded[:, :, 0] += self.temperature * 0.1
            graded[:, :, 2] -= self.temperature * 0.1
            graded[:, :, 1] += self.tint * 0.1

        out = rgba.copy()
        out[:, :, :3] = np.clip(graded * 255.0, 0, 255).astype(np.uint8)
        return out


class LensFlare:
    """
    Anamorphic horizontal streak + anti-reflective glare ghosts.
    """

    def __init__(
        self,
        position: Tuple[float, float] = (0.5, 0.3),
        intensity: float = 1.0,
        streak_length: float = 0.8,
        color: Optional[Any] = None,
        num_ghosts: int = 5,
    ) -> None:
        self.position = position
        self.intensity = float(intensity)
        self.streak_length = float(streak_length)
        self.color = color
        self.num_ghosts = int(num_ghosts)

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        if self.intensity <= 0.01:
            return rgba
        h, w, _ = rgba.shape
        lx = int(self.position[0] * w)
        ly = int(self.position[1] * h)

        flare_layer = np.zeros((h, w, 3), dtype=np.float32)

        # 1. Main flare burst
        y_grid, x_grid = np.ogrid[:h, :w]
        dist_sq = (x_grid - lx) ** 2 + (y_grid - ly) ** 2
        core_radius = max(8.0, w * 0.05)
        core_glow = np.exp(-dist_sq / (2.0 * core_radius ** 2)) * 255.0 * self.intensity

        # 2. Anamorphic horizontal streak
        streak_y = np.exp(-((y_grid - ly) ** 2) / 8.0)
        streak_x = np.exp(-((x_grid - lx) ** 2) / (2.0 * (w * self.streak_length * 0.5) ** 2))
        streak = (streak_y * streak_x) * 220.0 * self.intensity

        # 3. Flare color tint (Cyan/Blue tint by default)
        flare_layer[:, :, 0] += core_glow * 0.6 + streak * 0.5
        flare_layer[:, :, 1] += core_glow * 0.85 + streak * 0.8
        flare_layer[:, :, 2] += core_glow * 1.0 + streak * 1.0

        # 4. Anti-reflective ghosts along the optical axis
        cx, cy = w * 0.5, h * 0.5
        dx, dy = cx - lx, cy - ly
        for i in range(1, self.num_ghosts + 1):
            factor = (i / (self.num_ghosts + 1)) * 1.6
            gx = int(cx + dx * factor)
            gy = int(cy + dy * factor)
            if 0 <= gx < w and 0 <= gy < h:
                g_dist_sq = (x_grid - gx) ** 2 + (y_grid - gy) ** 2
                g_radius = max(6.0, 15.0 * (1.0 + factor * 0.5))
                ghost_glow = np.exp(-g_dist_sq / (2.0 * g_radius ** 2)) * (60.0 / i) * self.intensity
                flare_layer[:, :, (i % 3)] += ghost_glow

        rgb = np.clip(rgba[:, :, :3].astype(np.float32) + flare_layer, 0, 255).astype(np.uint8)
        out = rgba.copy()
        out[:, :, :3] = rgb
        return out


class GodRays:
    """
    Volumetric light shafts radiating outward from luminous highlights.
    """

    def __init__(
        self,
        light_position: Tuple[float, float] = (0.5, 0.2),
        decay: float = 0.94,
        density: float = 0.8,
        weight: float = 0.4,
        exposure: float = 0.5,
        samples: int = 16,
    ) -> None:
        self.light_position = light_position
        self.decay = float(decay)
        self.density = float(density)
        self.weight = float(weight)
        self.exposure = float(exposure)
        self.samples = max(4, int(samples))

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        h, w, _ = rgba.shape
        rgb = rgba[:, :, :3].astype(np.float32)

        # Extract highlight threshold
        luma = (0.2126 * rgb[:, :, 0] + 0.7152 * rgb[:, :, 1] + 0.0722 * rgb[:, :, 2]) / 255.0
        highlight_mask = np.clip((luma - 0.6) / 0.4, 0.0, 1.0)[:, :, np.newaxis]
        highlights = rgb * highlight_mask

        # Radial step accumulation
        rays = np.zeros_like(rgb)
        illumination_decay = 1.0

        lx, ly = self.light_position[0] * w, self.light_position[1] * h
        y, x = np.mgrid[:h, :w]
        dx = (x - lx) * (self.density / self.samples)
        dy = (y - ly) * (self.density / self.samples)

        # Vectorized approximation via multi-scale PIL blurs
        pil_hl = Image.fromarray(highlights.astype(np.uint8))
        for step in range(1, 5):
            blurred_step = np.array(pil_hl.filter(ImageFilter.GaussianBlur(step * 10.0)), dtype=np.float32)
            rays += blurred_step * illumination_decay * self.weight
            illumination_decay *= self.decay

        final_rgb = np.clip(rgb + rays * self.exposure, 0, 255).astype(np.uint8)
        out = rgba.copy()
        out[:, :, :3] = final_rgb
        return out


class Glitch:
    """
    Digital scanline glitch, horizontal block corruption, and RGB chromatic separation.
    """

    def __init__(
        self,
        intensity: float = 0.3,
        slice_count: int = 6,
        rgb_split: float = 6.0,
        scanlines: bool = True,
    ) -> None:
        self.intensity = float(intensity)
        self.slice_count = int(slice_count)
        self.rgb_split = float(rgb_split)
        self.scanlines = scanlines

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        if self.intensity <= 0.01:
            return rgba
        h, w, _ = rgba.shape
        out = rgba.copy()
        rng = np.random.RandomState(int((time * 300) % 50000))

        # 1. RGB Channel Split
        split = int(self.rgb_split * self.intensity)
        if split > 0:
            out[:, split:, 0] = rgba[:, :-split, 0]  # Red shift
            out[:, :-split, 2] = rgba[:, split:, 2]  # Blue shift

        # 2. Horizontal block slices displacement
        for _ in range(self.slice_count):
            if rng.rand() < self.intensity * 0.8:
                sy = rng.randint(0, h)
                sh = rng.randint(4, max(8, int(h * 0.15)))
                disp = rng.randint(-int(w * 0.08), int(w * 0.08))
                if disp != 0 and sy + sh <= h:
                    out[sy : sy + sh, :] = np.roll(out[sy : sy + sh, :], disp, axis=1)

        # 3. Scanline overlay
        if self.scanlines:
            scan = np.ones((h, 1, 1), dtype=np.float32)
            scan[::2, :, :] = 0.85
            out[:, :, :3] = (out[:, :, :3].astype(np.float32) * scan).astype(np.uint8)

        return out


class Pixelate:
    """
    Mosaic grid pixelation filter with smooth animatable cell size.
    """

    def __init__(self, cell_size: float = 12.0, size: Optional[float] = None) -> None:
        effective = size if size is not None else cell_size
        self.cell_size = max(1.0, float(effective))

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        if self.cell_size <= 1.05:
            return rgba
        h, w, _ = rgba.shape
        img = Image.fromarray(rgba)
        
        # Downscale then upscale using nearest neighbor
        small_w = max(1, int(w / self.cell_size))
        small_h = max(1, int(h / self.cell_size))
        small_img = img.resize((small_w, small_h), Image.Resampling.NEAREST)
        pixelated = small_img.resize((w, h), Image.Resampling.NEAREST)
        return np.array(pixelated)


class RadialBlur:
    """
    Directional rotational spin motion blur.
    """

    def __init__(
        self,
        center: Tuple[float, float] = (0.5, 0.5),
        amount: float = 0.04,
        samples: int = 8,
    ) -> None:
        self.center = center
        self.amount = float(amount)
        self.samples = max(2, int(samples))

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        if self.amount <= 0.001:
            return rgba
        h, w, _ = rgba.shape
        img = Image.fromarray(rgba)
        acc = rgba.astype(np.float32)

        angles = np.linspace(-self.amount * 45.0, self.amount * 45.0, self.samples)
        for ang in angles:
            if abs(ang) > 0.01:
                rot = img.rotate(ang, resample=Image.Resampling.BILINEAR)
                acc += np.array(rot, dtype=np.float32)

        acc = np.clip(acc / (self.samples + 1), 0, 255).astype(np.uint8)
        return acc


class ZoomBlur:
    """
    Directional optical zoom motion speed blur.
    """

    def __init__(
        self,
        center: Tuple[float, float] = (0.5, 0.5),
        amount: float = 0.06,
        samples: int = 6,
    ) -> None:
        self.center = center
        self.amount = float(amount)
        self.samples = max(2, int(samples))

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        if self.amount <= 0.001:
            return rgba
        h, w, _ = rgba.shape
        img = Image.fromarray(rgba)
        acc = rgba.astype(np.float32)

        scales = np.linspace(1.0, 1.0 + self.amount, self.samples)
        for s in scales:
            if s > 1.001:
                nw, nh = int(w * s), int(h * s)
                scaled = img.resize((nw, nh), Image.Resampling.BILINEAR)
                # Crop back to original dimensions centered
                cx, cy = nw // 2, nh // 2
                cropped = scaled.crop((cx - w // 2, cy - h // 2, cx - w // 2 + w, cy - h // 2 + h))
                acc += np.array(cropped, dtype=np.float32)

        return np.clip(acc / (self.samples + 1), 0, 255).astype(np.uint8)


class EdgeGlow:
    """
    Cyberpunk / Sci-Fi Sobel edge detection outline with customizable glow tint.
    """

    def __init__(
        self,
        threshold: float = 0.2,
        intensity: float = 1.0,
        color: Optional[Any] = None,
    ) -> None:
        self.threshold = float(threshold)
        self.intensity = float(intensity)
        self.color = color

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        h, w, _ = rgba.shape
        img = Image.fromarray(rgba[:, :, :3])
        # Find edges via PIL filter
        edges = img.filter(ImageFilter.FIND_EDGES)
        edges_arr = np.array(edges, dtype=np.float32) / 255.0

        # Threshold and boost
        edge_mask = np.clip((edges_arr - self.threshold) / (1.0 - self.threshold), 0.0, 1.0)
        edge_glow = edge_mask * 255.0 * self.intensity

        # Tint edges
        if self.color is not None:
            c = self.color
            cr, cg, cb = (c.r, c.g, c.b) if hasattr(c, "r") else (0.0, 0.9, 1.0)
            edge_glow[:, :, 0] *= cr
            edge_glow[:, :, 1] *= cg
            edge_glow[:, :, 2] *= cb

        rgb = np.clip(rgba[:, :, :3].astype(np.float32) + edge_glow, 0, 255).astype(np.uint8)
        out = rgba.copy()
        out[:, :, :3] = rgb
        return out


class Halftone:
    """
    Print newspaper / comic book CMYK dot raster halftone screen.
    """

    def __init__(self, dot_size: float = 6.0, contrast: float = 1.2) -> None:
        self.dot_size = max(2.0, float(dot_size))
        self.contrast = float(contrast)

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        h, w, _ = rgba.shape
        rgb = rgba[:, :, :3].astype(np.float32) / 255.0
        luma = 0.2126 * rgb[:, :, 0] + 0.7152 * rgb[:, :, 1] + 0.0722 * rgb[:, :, 2]

        y, x = np.ogrid[:h, :w]
        grid_x = (x % self.dot_size) - (self.dot_size * 0.5)
        grid_y = (y % self.dot_size) - (self.dot_size * 0.5)
        dist = np.hypot(grid_x, grid_y) / (self.dot_size * 0.5)

        # Dot threshold based on luminance
        dots = np.clip((luma - dist) * 4.0 * self.contrast, 0.0, 1.0)[:, :, np.newaxis]
        out_rgb = (rgb * dots * 255.0).astype(np.uint8)

        out = rgba.copy()
        out[:, :, :3] = out_rgb
        return out


class Duotone:
    """
    High-contrast stylized 2-color duotone mapping.
    """

    def __init__(self, color_dark: Any = None, color_light: Any = None) -> None:
        from vibmo.core.color import Color
        self.c_dark = Color.from_any(color_dark) if color_dark else Color.hex("#0f172a")
        self.c_light = Color.from_any(color_light) if color_light else Color.hex("#06b6d4")

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        rgb = rgba[:, :, :3].astype(np.float32) / 255.0
        luma = (0.2126 * rgb[:, :, 0] + 0.7152 * rgb[:, :, 1] + 0.0722 * rgb[:, :, 2])[:, :, np.newaxis]

        # Interpolate between dark and light colors
        r = self.c_dark.r + (self.c_light.r - self.c_dark.r) * luma
        g = self.c_dark.g + (self.c_light.g - self.c_dark.g) * luma
        b = self.c_dark.b + (self.c_light.b - self.c_dark.b) * luma

        out_rgb = np.clip(np.concatenate([r, g, b], axis=-1) * 255.0, 0, 255).astype(np.uint8)
        out = rgba.copy()
        out[:, :, :3] = out_rgb
        return out




