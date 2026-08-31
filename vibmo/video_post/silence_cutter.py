"""
Automated Silence Cutter & Jump-Cut Generator for Vibmo / Motio.

Detects silent pauses in talking-head / voiceover footage and:
  1. Cuts silent dead air to create tight, snappy jump-cuts.
  2. Or speeds up silence segments ($6x$) for seamless instructional pacing.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass
class SilenceInterval:
    start_time: float
    end_time: float
    duration: float


class SilenceCutter:
    """Detects and cuts or speeds up audio silences."""

    @classmethod
    def detect_silence(
        cls,
        audio_video_path: str | Path,
        silence_threshold_db: float = -35.0,
        min_silence_duration: float = 0.5,
    ) -> list[SilenceInterval]:
        path = Path(audio_video_path)
        if not path.is_file() or not shutil.which("ffmpeg"):
            return []

        cmd = [
            "ffmpeg",
            "-nostats",
            "-i",
            str(path),
            "-af",
            f"silencedetect=noise={silence_threshold_db}dB:d={min_silence_duration}",
            "-f",
            "null",
            "-",
        ]
        try:
            res = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True, timeout=30)
            output = res.stderr
        except Exception:
            return []

        # Parse: "silence_start: 1.23" and "silence_end: 2.45 | silence_duration: 1.22"
        intervals: list[SilenceInterval] = []
        start_time: float | None = None

        for line in output.splitlines():
            if "silence_start:" in line:
                m = re.search(r"silence_start:\s*([\d\.]+)", line)
                if m:
                    start_time = float(m.group(1))
            elif "silence_end:" in line and start_time is not None:
                m_end = re.search(r"silence_end:\s*([\d\.]+)", line)
                m_dur = re.search(r"silence_duration:\s*([\d\.]+)", line)
                if m_end:
                    end_val = float(m_end.group(1))
                    dur_val = float(m_dur.group(1)) if m_dur else (end_val - start_time)
                    intervals.append(SilenceInterval(start_time=start_time, end_time=end_val, duration=dur_val))
                    start_time = None

        return intervals

    @classmethod
    def calculate_active_speech_intervals(
        cls,
        total_duration: float,
        silence_intervals: Sequence[SilenceInterval],
        padding: float = 0.08,
    ) -> list[tuple[float, float]]:
        if not silence_intervals:
            return [(0.0, total_duration)]

        speech: list[tuple[float, float]] = []
        cursor = 0.0

        for sil in silence_intervals:
            speech_end = max(cursor, sil.start_time + padding)
            if speech_end > cursor + 0.1:
                speech.append((cursor, speech_end))
            cursor = max(cursor, sil.end_time - padding)

        if cursor < total_duration:
            speech.append((cursor, total_duration))

        return speech
