"""
Audio Track loading, waveform decoding, and sample array caching.
"""

from __future__ import annotations
import os
import numpy as np
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class TimelineAudioClip:
    """An audio clip placed on a composition's global timeline.

    The clip stays declarative until export.  FFmpeg applies trimming, gain,
    fades, and timeline offset in one final mix, avoiding lossy intermediate
    audio renders.
    """

    file_path: str
    start: float = 0.0
    duration: Optional[float] = None
    volume: float = 1.0
    fade_in: float = 0.0
    fade_out: float = 0.0
    name: str = ""

    def __post_init__(self) -> None:
        if self.start < 0:
            raise ValueError("Audio clip start cannot be negative.")
        if self.duration is not None and self.duration <= 0:
            raise ValueError("Audio clip duration must be greater than zero.")
        if self.volume < 0:
            raise ValueError("Audio clip volume cannot be negative.")
        if self.fade_in < 0 or self.fade_out < 0:
            raise ValueError("Audio fade durations cannot be negative.")
        if self.duration is not None and self.fade_in + self.fade_out > self.duration:
            raise ValueError("Audio fades cannot be longer than the clip duration.")

    def ffmpeg_filter(self, input_index: int, output_label: str) -> str:
        """Builds the deterministic FFmpeg filter chain for this clip."""
        filters = [f"[{input_index}:a]asetpts=PTS-STARTPTS"]
        if self.duration is not None:
            filters.append(f"atrim=duration={self.duration:.6f}")
        if self.volume != 1.0:
            filters.append(f"volume={self.volume:.6f}")
        if self.fade_in > 0:
            filters.append(f"afade=t=in:st=0:d={self.fade_in:.6f}")
        if self.fade_out > 0 and self.duration is not None:
            fade_start = max(0.0, self.duration - self.fade_out)
            filters.append(f"afade=t=out:st={fade_start:.6f}:d={self.fade_out:.6f}")
        delay_ms = round(self.start * 1000)
        filters.append(f"adelay={delay_ms}:all=1")
        return ",".join(filters) + f"[{output_label}]"


class AudioTrack:
    """Represents an audio file for playback, FFT analysis, and video muxing."""

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.sample_rate = 44100
        self.samples: np.ndarray = np.zeros(0, dtype=np.float32)
        self.duration = 0.0
        self._load_audio()

    def _load_audio(self) -> None:
        if not os.path.exists(self.file_path):
            # Create synthetic fallback sine tone
            self.sample_rate = 44100
            t = np.linspace(0, 5, 44100 * 5)
            self.samples = (np.sin(2 * np.pi * 120 * t) * 0.5).astype(np.float32)
            self.duration = 5.0
            return

        try:
            from pydub import AudioSegment
            seg = AudioSegment.from_file(self.file_path)
            self.sample_rate = seg.frame_rate
            raw_data = seg.raw_data
            dtype = np.int16 if seg.sample_width == 2 else np.int32
            arr = np.frombuffer(raw_data, dtype=dtype)
            if seg.channels == 2:
                arr = arr.reshape((-1, 2)).mean(axis=1)
            # Normalize to [-1.0, 1.0]
            max_val = float(np.iinfo(dtype).max)
            self.samples = (arr / max_val).astype(np.float32)
            self.duration = len(self.samples) / self.sample_rate
        except Exception:
            # Fallback
            self.samples = np.zeros(44100 * 5, dtype=np.float32)
            self.duration = 5.0
