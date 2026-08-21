"""
Frame-Accurate Video Asset & VideoNode primitive for embedded screen recordings, app demos, and B-roll.
"""

from __future__ import annotations
import os
import shutil
import subprocess
import json
import math
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
from PIL import Image
import cairo

from vibmo.core.color import Color
from vibmo.core.vector import Vector2D
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.scene.node import Node


class VideoMetadata:
    """Stores probed video stream dimensions, duration, and framerate."""

    def __init__(self, width: int, height: int, duration: float, fps: float):
        self.width = width
        self.height = height
        self.duration = duration
        self.fps = fps


def probe_video(file_path: str) -> VideoMetadata:
    """Probes video metadata using ffprobe or ffmpeg."""
    ffprobe_bin = shutil.which("ffprobe")
    if ffprobe_bin:
        cmd = [
            ffprobe_bin,
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height,duration,r_frame_rate",
            "-of", "json",
            file_path,
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            info = json.loads(res.stdout)["streams"][0]
            w = int(info.get("width", 1920))
            h = int(info.get("height", 1080))
            
            # FPS
            r_fps = info.get("r_frame_rate", "30/1")
            num, den = map(float, r_fps.split("/")) if "/" in r_fps else (float(r_fps), 1.0)
            fps = num / max(1.0, den)
            
            dur = float(info.get("duration", 10.0))
            return VideoMetadata(w, h, dur, fps)
        except Exception:
            pass

    return VideoMetadata(1920, 1080, 10.0, 30.0)


class VideoClip:
    """Frame-accurate video decoder with LRU surface memory cache."""

    def __init__(self, file_path: str):
        self.file_path = os.path.abspath(file_path)
        self.meta = probe_video(self.file_path)
        self._frame_cache: Dict[int, cairo.ImageSurface] = {}
        self._cache_order: List[int] = []
        self._max_cached_frames = 120  # ~2 seconds in RAM

    def get_surface(self, time_sec: float) -> Optional[cairo.ImageSurface]:
        """Extracts and returns the Cairo surface for a given timestamp."""
        frame_idx = max(0, int(round(time_sec * self.meta.fps)))

        if frame_idx in self._frame_cache:
            return self._frame_cache[frame_idx]

        # Extract single frame via FFmpeg seeking
        ffmpeg_bin = shutil.which("ffmpeg") or "ffmpeg"
        cmd = [
            ffmpeg_bin,
            "-ss", f"{time_sec:.4f}",
            "-i", self.file_path,
            "-vframes", "1",
            "-f", "rawvideo",
            "-pix_fmt", "rgba",
            "-loglevel", "error",
            "-",
        ]

        try:
            res = subprocess.run(cmd, capture_output=True, check=True)
            raw_bytes = res.stdout
            expected_size = self.meta.width * self.meta.height * 4

            if len(raw_bytes) >= expected_size:
                arr = np.frombuffer(raw_bytes[:expected_size], dtype=np.uint8).reshape((self.meta.height, self.meta.width, 4))
                # Cairo expects ARGB32 or raw buffer with stride
                surf = cairo.ImageSurface.create_for_data(
                    arr.copy(), cairo.FORMAT_ARGB32, self.meta.width, self.meta.height
                )

                # Store in LRU cache
                if len(self._cache_order) >= self._max_cached_frames:
                    oldest = self._cache_order.pop(0)
                    self._frame_cache.pop(oldest, None)

                self._frame_cache[frame_idx] = surf
                self._cache_order.append(frame_idx)
                return surf
        except Exception:
            pass

        return None


class VideoNode(Node):
    """
    Animatable Video playback node for screen recordings and UI walkthroughs.
    Supports trimming, speed scaling, looping, corner clipping, and region zooming.
    """

    def __init__(
        self,
        video_path: str,
        width: Optional[float] = None,
        height: Optional[float] = None,
        trim: Optional[Tuple[float, float]] = None,
        speed: float = 1.0,
        loop: bool = True,
        corner_radius: float = 0.0,
        position: Union[Vector2D, Tuple[float, float]] = (0.0, 0.0),
        **kwargs: Any,
    ) -> None:
        super().__init__(position=position, **kwargs)
        self.video_path = str(video_path)
        self.clip = VideoClip(self.video_path)
        self.speed = float(speed)
        self.loop = loop
        self.corner_radius = float(corner_radius)

        # Trimming
        if trim:
            self.trim_start, self.trim_end = trim
        else:
            self.trim_start = 0.0
            self.trim_end = self.clip.meta.duration

        # Display dimensions
        if width is not None and height is not None:
            self.width_val = float(width)
            self.height_val = float(height)
        elif width is not None:
            self.width_val = float(width)
            self.height_val = (float(width) / max(1, self.clip.meta.width)) * self.clip.meta.height
        elif height is not None:
            self.height_val = float(height)
            self.width_val = (float(height) / max(1, self.clip.meta.height)) * self.clip.meta.width
        else:
            self.width_val = float(self.clip.meta.width)
            self.height_val = float(self.clip.meta.height)

        # Region Zoom & Pan Signals (normalized rect: x0, y0, x1, y1)
        self.crop_region = Signal((0.0, 0.0, 1.0, 1.0), f"{self.name}.crop_region")

    def zoom_to_region(
        self,
        region: Tuple[float, float, float, float],
        duration: float = 1.0,
        ease: EasingFunc = Ease.out_expo,
        delay: float = 0.0,
    ) -> AnimationAction:
        """
        Smoothly crops and zooms into a normalized sub-region (x, y, w, h) of the video screen.
        Usage: video.zoom_to_region((0.2, 0.3, 0.5, 0.5), duration=1.0)
        """
        rx, ry, rw, rh = region
        target_crop = (rx, ry, rx + rw, ry + rh)
        return self.crop_region.to(target_crop, duration=duration, ease=ease, delay=delay)

    def reset_zoom(
        self,
        duration: float = 0.8,
        ease: EasingFunc = Ease.out_expo,
        delay: float = 0.0,
    ) -> AnimationAction:
        """Pulls zoom back to full video frame."""
        return self.crop_region.to((0.0, 0.0, 1.0, 1.0), duration=duration, ease=ease, delay=delay)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        # Calculate local playback timestamp
        dur = max(0.1, self.trim_end - self.trim_start)
        playback_t = time * self.speed

        if self.loop:
            local_t = self.trim_start + (playback_t % dur)
        else:
            local_t = min(self.trim_end, self.trim_start + playback_t)

        surface = self.clip.get_surface(local_t)
        if surface is None:
            return

        ctx.save()

        # Rounded corner clipping
        if self.corner_radius > 0:
            r = min(self.corner_radius, self.width_val * 0.5, self.height_val * 0.5)
            ctx.new_path()
            ctx.arc(self.width_val - r, r, r, -math.pi * 0.5, 0)
            ctx.arc(self.width_val - r, self.height_val - r, r, 0, math.pi * 0.5)
            ctx.arc(r, self.height_val - r, r, math.pi * 0.5, math.pi)
            ctx.arc(r, r, r, math.pi, math.pi * 1.5)
            ctx.close_path()
            ctx.clip()

        # Region crop and scaling
        crop = self.crop_region.get(time)
        cx0, cy0, cx1, cy1 = crop
        cw = max(0.01, cx1 - cx0)
        ch = max(0.01, cy1 - cy0)

        # Scale and position to map the cropped region to the node bounds
        sx = (self.width_val / (self.clip.meta.width * cw))
        sy = (self.height_val / (self.clip.meta.height * ch))

        ctx.scale(sx, sy)
        ctx.translate(-cx0 * self.clip.meta.width, -cy0 * self.clip.meta.height)
        ctx.set_source_surface(surface, 0, 0)
        ctx.paint()

        ctx.restore()
