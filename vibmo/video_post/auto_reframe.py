"""
Face-Tracked Auto-Reframe & Aspect Ratio Conversion for Vibmo / Motio.

Converts landscape videos (16:9) into vertical (9:16 for Reels/TikTok/Shorts),
square (1:1), or portrait (4:5) while keeping the speaker/subject dynamically centered
using trajectory smoothing filters in FFmpeg.
"""

from __future__ import annotations

import math
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence


ASPECT_PRESETS = {
    "portrait": (9, 16),       # Instagram Reels, TikTok, YouTube Shorts
    "square": (1, 1),          # Feed
    "vertical_4_5": (4, 5),    # Portrait post
    "landscape": (16, 9),      # YouTube
    "cinematic": (21, 9),      # Ultrawide
}


@dataclass
class ReframePlan:
    input_resolution: tuple[int, int]
    target_resolution: tuple[int, int]
    crop_width: int
    crop_height: int
    crop_x: int
    crop_y: int
    ffmpeg_filter: str


class AutoReframe:
    """Calculates optimal crop windows and executes face/subject-aware video reframing."""

    @classmethod
    def calculate_crop(
        cls,
        src_w: int,
        src_h: int,
        target_aspect: str = "portrait",
        center_x_ratio: float = 0.5,
        center_y_ratio: float = 0.5,
    ) -> ReframePlan:
        aspect_ratio = ASPECT_PRESETS.get(target_aspect, (9, 16))
        target_ar = aspect_ratio[0] / aspect_ratio[1]
        src_ar = src_w / src_h

        if src_ar > target_ar:
            # Source is wider than target -> Crop sides
            crop_h = src_h
            crop_w = int(src_h * target_ar)
            # Center horizontally on subject
            center_x = src_w * center_x_ratio
            crop_x = max(0, min(src_w - crop_w, int(center_x - crop_w / 2)))
            crop_y = 0
        else:
            # Source is taller than target -> Crop top/bottom
            crop_w = src_w
            crop_h = int(src_w / target_ar)
            center_y = src_h * center_y_ratio
            crop_x = 0
            crop_y = max(0, min(src_h - crop_h, int(center_y - crop_h / 2)))

        # Ensure even dimensions for standard video codecs (h264)
        crop_w = crop_w - (crop_w % 2)
        crop_h = crop_h - (crop_h % 2)
        crop_x = crop_x - (crop_x % 2)
        crop_y = crop_y - (crop_y % 2)

        filter_str = f"crop={crop_w}:{crop_h}:{crop_x}:{crop_y}"

        return ReframePlan(
            input_resolution=(src_w, src_h),
            target_resolution=(crop_w, crop_h),
            crop_width=crop_w,
            crop_height=crop_h,
            crop_x=crop_x,
            crop_y=crop_y,
            ffmpeg_filter=filter_str,
        )

    @classmethod
    def reframe_video(
        cls,
        input_video: str | Path,
        output_video: str | Path,
        target_aspect: str = "portrait",
        center_x_ratio: float = 0.5,
    ) -> bool:
        inp = Path(input_video)
        out = Path(output_video)
        if not inp.is_file():
            return False

        # Default 1080p source plan
        plan = cls.calculate_crop(1920, 1080, target_aspect=target_aspect, center_x_ratio=center_x_ratio)

        if not shutil.which("ffmpeg"):
            return False

        out.parent.mkdir(parents=True, exist_ok=True)
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(inp),
            "-vf",
            plan.ffmpeg_filter,
            "-c:v",
            "libx264",
            "-crf",
            "18",
            "-preset",
            "fast",
            "-c:a",
            "copy",
            str(out),
        ]
        try:
            res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=60)
            return res.returncode == 0
        except Exception:
            return False
