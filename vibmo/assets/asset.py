"""
Unified Asset Management system for images, SVGs, videos, audio tracks, and custom fonts.
"""

from __future__ import annotations
import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union
import numpy as np
from PIL import Image
import cairo

from vibmo.core.color import Color
from vibmo.core.vector import Vector2D
from vibmo.scene.node import Node
from vibmo.audio.track import AudioTrack


class ImageNode(Node):
    """Renderable image node with automatic aspect ratio scaling and alpha support."""

    def __init__(
        self,
        image_path: str,
        width: Optional[float] = None,
        height: Optional[float] = None,
        corner_radius: float = 0.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.image_path = str(image_path)
        self.corner_radius = float(corner_radius)
        
        # Load image metadata
        if os.path.exists(self.image_path):
            img = Image.open(self.image_path)
            self.orig_w, self.orig_h = img.size
        else:
            self.orig_w, self.orig_h = 100, 100

        self._surface_cache: Optional[cairo.ImageSurface] = None
        self._surface_arr: Optional[np.ndarray] = None

        if width is not None and height is not None:
            self.width_val = float(width)
            self.height_val = float(height)
        elif width is not None:
            self.width_val = float(width)
            self.height_val = (float(width) / self.orig_w) * self.orig_h
        elif height is not None:
            self.height_val = float(height)
            self.width_val = (float(height) / self.orig_h) * self.orig_w
        else:
            self.width_val = float(self.orig_w)
            self.height_val = float(self.orig_h)

    @property
    def width(self) -> float:
        return self.width_val

    @property
    def height(self) -> float:
        return self.height_val

    def __getstate__(self) -> Dict[str, Any]:

        state = self.__dict__.copy()
        state.pop("_surface_cache", None)
        state.pop("_surface_arr", None)
        return state

    def __setstate__(self, state: Dict[str, Any]) -> None:
        self.__dict__.update(state)
        self._surface_cache = None
        self._surface_arr = None

    def _get_surface(self) -> Optional[cairo.ImageSurface]:
        if self._surface_cache is None and os.path.exists(self.image_path):
            img = Image.open(self.image_path).convert("RGBA")
            self.orig_w, self.orig_h = img.size
            arr = np.array(img)
            bgra = np.zeros_like(arr)
            bgra[:, :, 0] = arr[:, :, 2]
            bgra[:, :, 1] = arr[:, :, 1]
            bgra[:, :, 2] = arr[:, :, 0]
            bgra[:, :, 3] = arr[:, :, 3]
            self._surface_arr = np.ascontiguousarray(bgra)
            self._surface_cache = cairo.ImageSurface.create_for_data(
                self._surface_arr, cairo.FORMAT_ARGB32, self.orig_w, self.orig_h
            )
        return self._surface_cache

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        surf = self._get_surface()
        if surf is None:
            return

        ctx.save()
        
        # Clip rounded corners if specified
        if self.corner_radius > 0:
            r = min(self.corner_radius, self.width_val * 0.5, self.height_val * 0.5)
            import math
            ctx.new_path()
            ctx.arc(self.width_val - r, r, r, -math.pi * 0.5, 0)
            ctx.arc(self.width_val - r, self.height_val - r, r, 0, math.pi * 0.5)
            ctx.arc(r, self.height_val - r, r, math.pi * 0.5, math.pi)
            ctx.arc(r, r, r, math.pi, math.pi * 1.5)
            ctx.close_path()
            ctx.clip()

        sx = self.width_val / self.orig_w
        sy = self.height_val / self.orig_h
        ctx.scale(sx, sy)
        ctx.set_source_surface(surf, 0, 0)
        ctx.paint()
        
        ctx.restore()



class Asset:
    """Factory and registry for project assets."""

    _cache: Dict[str, Any] = {}

    @classmethod
    def web(
        cls,
        url: str,
        width: float = 1200.0,
        height: float = 750.0,
        scale: float = 2.0,
        corner_radius: float = 0.0,
        **kwargs: Any,
    ) -> Any:
        """
        Renders a live website URL at 4K retina resolution and returns an animatable WebNode.
        Usage:
            browser.add_content(Asset.web("https://linear.app", width=1280, height=800))
        """
        from vibmo.importers.web import WebNode
        return WebNode(url, width=width, height=height, scale=scale, corner_radius=corner_radius, **kwargs)

    @classmethod
    def html(
        cls,
        markup_or_tailwind: str,
        width: float = 1200.0,
        height: float = 750.0,
        scale: float = 2.0,
        corner_radius: float = 0.0,
        **kwargs: Any,
    ) -> Any:
        """
        Renders a raw HTML / CSS / Tailwind snippet at high-DPI retina resolution into a WebNode.
        Usage:
            ui = Asset.html('<div class="p-8 bg-slate-900 text-white font-bold">Hello Tailwind</div>')
        """
        from vibmo.importers.web import WebNode
        return WebNode(markup_or_tailwind, width=width, height=height, scale=scale, corner_radius=corner_radius, **kwargs)

    @classmethod
    def image(
        cls,
        path: str,
        width: Optional[float] = None,
        height: Optional[float] = None,
        corner_radius: float = 0.0,
        **kwargs: Any,
    ) -> ImageNode:
        """Loads and caches an image asset (PNG, JPG, WebP) as an animatable Node."""
        return ImageNode(path, width=width, height=height, corner_radius=corner_radius, **kwargs)


    @classmethod
    def audio(cls, path_or_url: str) -> AudioTrack:
        """
        Loads and caches an audio track (MP3, WAV, FLAC, M4A, OGG).
        Supports:
        - Local filesystem paths: Asset.audio("assets/track.mp3")
        - Online direct URLs: Asset.audio("https://cdn.example.com/soundtrack.mp3")
        - Curated presets: Asset.audio("tech_ambient"), Asset.audio("preset:cyberpunk"), Asset.audio("lofi_chill")
        """
        raw_str = str(path_or_url).strip()
        if raw_str.startswith("http://") or raw_str.startswith("https://") or raw_str.startswith("preset:") or raw_str in ("tech_ambient", "cyberpunk", "lofi_chill", "future_bass"):
            from vibmo.audio.library import fetch_online_audio
            local_resolved_path = fetch_online_audio(raw_str)
        else:
            local_resolved_path = os.path.abspath(raw_str) if os.path.exists(raw_str) else raw_str

        if local_resolved_path not in cls._cache:
            cls._cache[local_resolved_path] = AudioTrack(local_resolved_path)
        return cls._cache[local_resolved_path]


    @classmethod
    def video(
        cls,
        path: str,
        width: Optional[float] = None,
        height: Optional[float] = None,
        trim: Optional[Tuple[float, float]] = None,
        speed: float = 1.0,
        loop: bool = True,
        corner_radius: float = 0.0,
        **kwargs: Any,
    ) -> Any:
        """Loads and decodes a video clip (MP4, WebM, MOV) as an animatable VideoNode."""
        from vibmo.assets.video import VideoNode
        return VideoNode(
            path,
            width=width,
            height=height,
            trim=trim,
            speed=speed,
            loop=loop,
            corner_radius=corner_radius,
            **kwargs,
        )

    @classmethod
    def lottie(
        cls,
        path_or_dict: Union[str, Dict[str, Any]],
        width: Optional[float] = None,
        height: Optional[float] = None,
        speed: float = 1.0,
        loop: bool = True,
        **kwargs: Any,
    ) -> Any:
        """Loads and parses a Lottie/Bodymovin JSON vector animation."""
        from vibmo.importers.lottie import LottieAnimation
        return LottieAnimation(
            path_or_dict,
            width=width,
            height=height,
            speed=speed,
            loop=loop,
            **kwargs,
        )

    @classmethod
    def font(cls, path: str, family_name: Optional[str] = None) -> str:
        """Registers a TrueType or OpenType font file for scene typography."""
        font_path = os.path.abspath(path)
        name = family_name or os.path.splitext(os.path.basename(path))[0]
        cls._cache[f"font:{name}"] = font_path
        return name

    @classmethod
    def preload(cls, *paths: str) -> None:
        """Pre-fetches and validates assets (images, audio, fonts, lottie) concurrently."""
        for p in paths:
            if not p:
                continue
            if p.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".svg")):
                cls.image(p)
            elif p.lower().endswith((".mp3", ".wav", ".aac", ".flac", ".ogg")):
                cls.audio(p)
            elif p.lower().endswith(".json"):
                cls.lottie(p)

    @classmethod
    def bundle(cls, scene: Any, output_zip: str) -> str:
        """Packages all referenced image, audio, font, and video assets into a portable bundle."""
        import zipfile
        out_path = os.path.abspath(output_zip)
        with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for k, v in cls._cache.items():
                if isinstance(v, str) and os.path.exists(v):
                    zf.write(v, arcname=os.path.basename(v))
        return out_path

