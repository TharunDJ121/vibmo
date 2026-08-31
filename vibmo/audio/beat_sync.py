"""
Audio Beat-Sync & Timeline SFX Engine for Vibmo.
Inspired by video-shotcraft music-beat-sync and sound-design.
Implements beat grid calculation, transient alignment, and timeline SFX tables.
"""

from __future__ import annotations
import math
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass, field


@dataclass
class SFXCue:
    """An individual sound effect event anchored to timeline beats."""
    name: str
    target_beat: float
    peak_offset_sec: float = 0.0
    volume: float = 0.8
    category: str = "transition"
    comment: str = ""

    def calculate_start_time(self, grid: BeatSyncGrid) -> float:
        """Calculates exact start time in seconds compensating for peak transient."""
        beat_t = grid.beat_time(self.target_beat)
        return max(0.0, beat_t - self.peak_offset_sec)

    def calculate_start_frame(self, grid: BeatSyncGrid, fps: float = 60.0) -> int:
        """Calculates exact start frame number."""
        return round(self.calculate_start_time(grid) * fps)


class BeatSyncGrid:
    """
    Rhythmic beat grid engine for musical synchronization.
    Calculates exact frame and time positions for any musical beat:
    beatF(n) = round((beat0 + n * beat_period) * fps)
    """

    def __init__(
        self,
        bpm: float = 126.0,
        beat0_sec: float = 0.0538,
        fps: float = 60.0,
    ) -> None:
        self.bpm = bpm
        self.beat0_sec = beat0_sec
        self.fps = fps
        self.beat_period = 60.0 / bpm if bpm > 0 else 0.5

    def beat_time(self, beat_number: float) -> float:
        """Returns time in seconds for a given beat number."""
        return self.beat0_sec + beat_number * self.beat_period

    def beat_frame(self, beat_number: float) -> int:
        """Returns exact frame index for a given beat number."""
        return round(self.beat_time(beat_number) * self.fps)

    def nearest_beat(self, time_sec: float) -> float:
        """Finds closest beat number for a given timestamp."""
        return (time_sec - self.beat0_sec) / self.beat_period

    def is_on_beat(self, time_sec: float, tolerance_sec: float = 0.03) -> bool:
        """Checks if a timestamp falls within a musical beat tolerance window."""
        nb = self.nearest_beat(time_sec)
        exact_t = self.beat_time(round(nb))
        return abs(time_sec - exact_t) <= tolerance_sec


class TimelineSFXTable:
    """
    Declarative SFX Table manager for central audio design and beat alignment.
    """

    def __init__(self, grid: Optional[BeatSyncGrid] = None) -> None:
        self.grid = grid or BeatSyncGrid()
        self.cues: List[SFXCue] = []

    def add_cue(
        self,
        name: str,
        target_beat: float,
        peak_offset_sec: float = 0.0,
        volume: float = 0.8,
        category: str = "transition",
        comment: str = "",
    ) -> SFXCue:
        """Registers an SFX cue anchored to a musical beat."""
        cue = SFXCue(
            name=name,
            target_beat=target_beat,
            peak_offset_sec=peak_offset_sec,
            volume=volume,
            category=category,
            comment=comment,
        )
        self.cues.append(cue)
        return cue

    def export_cues_schedule(self, fps: float = 60.0) -> List[Dict[str, Any]]:
        """Exports computed cue schedule with start frames and timings."""
        schedule = []
        for cue in self.cues:
            start_t = cue.calculate_start_time(self.grid)
            start_f = cue.calculate_start_frame(self.grid, fps)
            schedule.append({
                "name": cue.name,
                "target_beat": cue.target_beat,
                "start_time": start_t,
                "start_frame": start_f,
                "volume": cue.volume,
                "category": cue.category,
                "comment": cue.comment,
            })
        return schedule
