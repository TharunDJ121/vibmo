"""
Automated Scene Detection & Shot Boundary Analyzer for Vibmo.

Detects shot transitions and cuts in raw video files using FFmpeg select / PySceneDetect.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass
class SceneBoundary:
    scene_number: int
    start_time: float
    end_time: float
    duration: float


class SceneDetector:
    """Detects shot cut boundaries in video."""

    @classmethod
    def detect_scenes(
        cls,
        video_path: str | Path,
        threshold: float = 0.35,
        min_scene_duration: float = 1.0,
    ) -> list[SceneBoundary]:
        path = Path(video_path)
        if not path.is_file() or not shutil.which("ffmpeg"):
            return []

        # Use FFmpeg scene detection filter: "select='gt(scene,0.35)',showinfo"
        cmd = [
            "ffmpeg",
            "-nostats",
            "-i",
            str(path),
            "-filter_complex",
            f"select='gt(scene,{threshold})',showinfo",
            "-f",
            "null",
            "-",
        ]
        try:
            res = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True, timeout=60)
            output = res.stderr
        except Exception:
            return []

        pts_times: list[float] = [0.0]
        for line in output.splitlines():
            if "pts_time:" in line:
                m = re.search(r"pts_time:\s*([\d\.]+)", line)
                if m:
                    t = float(m.group(1))
                    if t - pts_times[-1] >= min_scene_duration:
                        pts_times.append(t)

        scenes: list[SceneBoundary] = []
        for i in range(len(pts_times) - 1):
            s = pts_times[i]
            e = pts_times[i + 1]
            scenes.append(SceneBoundary(scene_number=i + 1, start_time=s, end_time=e, duration=e - s))

        return scenes
