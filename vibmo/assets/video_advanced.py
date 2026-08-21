"""
Advanced Video Node with frame-accurate trimming, speed scaling, region zooming, and chroma keying.
"""

from __future__ import annotations
import math
from typing import Any, Optional, Tuple, Union, Sequence
import numpy as np
from PIL import Image

from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.scene.node import Node
from vibmo.assets.video import VideoNode, VideoClip


class AdvancedVideoNode(VideoNode):
    """
    Frame-accurate video node with speed scaling, loop controls, zoom-to-region choreography, and chroma key removal.
    """

    def __init__(
        self,
        source: Union[str, VideoClip],
        width: Optional[float] = None,
        height: Optional[float] = None,
        trim: Optional[Tuple[float, float]] = None,
        speed: float = 1.0,
        loop: bool = True,
        corner_radius: float = 0.0,
        chroma_key_color: Optional[Union[Color, str]] = None,
        chroma_similarity: float = 0.35,
        chroma_smoothness: float = 0.1,
        **kwargs: Any,
    ) -> None:
        super().__init__(source=source, width=width, height=height, **kwargs)
        self.trim = trim  # (start_time, end_time)
        self.speed = float(speed)
        self.loop = loop
        self.corner_radius = float(corner_radius)
        self.chroma_color = Color.from_any(chroma_key_color) if chroma_key_color else None
        self.chroma_similarity = float(chroma_similarity)
        self.chroma_smoothness = float(chroma_smoothness)

        # Zoom Region Signals: (x, y, w, h) in normalized 0-1 coordinates
        self.zoom_rect = Signal((0.0, 0.0, 1.0, 1.0), f"{self.name}.zoom_rect")

    def zoom_to_region(
        self,
        region: Tuple[float, float, float, float],  # (x, y, w, h)
        duration: float = 1.0,
        ease: Optional[EasingFunc] = None,
    ) -> AnimationAction:
        """Animates a viewport zoom into a specific sub-region of the video."""
        return self.zoom_rect.to(region, duration=duration, ease=ease or Ease.out_expo)

    def reset_zoom(self, duration: float = 0.8, ease: Optional[EasingFunc] = None) -> AnimationAction:
        """Pulls back video zoom to full view."""
        return self.zoom_rect.to((0.0, 0.0, 1.0, 1.0), duration=duration, ease=ease or Ease.out_expo)

    def _apply_chroma_key(self, frame_rgba: np.ndarray) -> np.ndarray:
        """Perform green screen / chroma key color removal with soft edges."""
        if not self.chroma_color:
            return frame_rgba

        rgb = frame_rgba[:, :, :3].astype(np.float32) / 255.0
        target = np.array([self.chroma_color.r, self.chroma_color.g, self.chroma_color.b], dtype=np.float32)

        # Euclidean distance in RGB color space
        dist = np.linalg.norm(rgb - target, axis=2)
        
        sim = self.chroma_similarity
        smooth = max(1e-4, self.chroma_smoothness)

        # Alpha mask: 0 where color matches chroma, 1 elsewhere
        alpha_mask = np.clip((dist - sim) / smooth, 0.0, 1.0)
        
        out = frame_rgba.copy()
        out[:, :, 3] = (out[:, :, 3].astype(np.float32) * alpha_mask).astype(np.uint8)
        return out
