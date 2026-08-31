"""
Audio Voiceover Ducker for Vibmo / Motio.

Computes dynamic sidechain volume compression envelopes to automatically
duck background music / ambient tracks whenever narration/voiceover is active.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence


@dataclass
class VoiceoverSegment:
    start_time: float
    end_time: float
    speaker: str = "narrator"


class VoiceoverDucker:
    """Calculates smooth volume envelopes for background music ducking."""

    def __init__(
        self,
        normal_volume: float = 1.0,
        ducked_volume: float = 0.22,
        fade_in_time: float = 0.35,
        fade_out_time: float = 0.25,
    ) -> None:
        self.normal_volume = normal_volume
        self.ducked_volume = ducked_volume
        self.fade_in_time = fade_in_time
        self.fade_out_time = fade_out_time

    def compute_volume_at(
        self,
        t: float,
        segments: Sequence[VoiceoverSegment | tuple[float, float]],
    ) -> float:
        # Check if inside or near any voiceover segment
        current_duck = 0.0  # 0.0 = full volume, 1.0 = fully ducked

        for seg in segments:
            if isinstance(seg, tuple):
                start, end = seg
            else:
                start, end = seg.start_time, seg.end_time

            # Pre-duck fade in
            duck_start = max(0.0, start - self.fade_in_time)
            # Post-duck release
            duck_end = end + self.fade_out_time

            if t < duck_start or t > duck_end:
                continue

            if duck_start <= t < start:
                # Fading down
                p = (t - duck_start) / max(0.01, self.fade_in_time)
                duck_amount = 0.5 - 0.5 * math.cos(p * math.pi)
                current_duck = max(current_duck, duck_amount)
            elif start <= t <= end:
                # Fully ducked
                current_duck = 1.0
            elif end < t <= duck_end:
                # Fading back up
                p = (t - end) / max(0.01, self.fade_out_time)
                duck_amount = 0.5 + 0.5 * math.cos(p * math.pi)
                current_duck = max(current_duck, duck_amount)

        # Interpolate between normal and ducked volume
        return self.normal_volume * (1.0 - current_duck) + self.ducked_volume * current_duck
