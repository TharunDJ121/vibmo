"""
Scene Pacing & Audio Cue Alignment Verifier for Vibmo / Motio.

Provides frame-accurate mathematical verification that visual events
(terminal commands, button clicks, chart reveals, slide transitions)
align with narration/voiceover audio cues within a tight tolerance window.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Sequence


@dataclass
class TimelineLandmark:
    video_time: float
    kind: str
    label: str


@dataclass
class PacingReport:
    is_aligned: bool
    scene_start: float
    scene_end: float
    total_duration: float
    landmarks: list[TimelineLandmark]
    mismatches: list[str]


class ScenePacingVerifier:
    """Mathematical verification of visual action vs. audio narration pacing."""

    @classmethod
    def trace_landmarks(
        cls,
        steps: Sequence[dict[str, Any]],
        scene_start: float = 0.0,
        fps: int = 60,
    ) -> list[TimelineLandmark]:
        cursor = 0.0
        landmarks: list[TimelineLandmark] = []

        for s in steps:
            kind = s.get("kind", "action")
            current_vt = round(cursor + scene_start, 2)
            label = s.get("text") or s.get("label") or s.get("name", "")

            landmarks.append(TimelineLandmark(video_time=current_vt, kind=kind.upper(), label=str(label)))
            dur = cls.calculate_step_duration(s, fps=fps)
            cursor += dur

        return landmarks

    @classmethod
    def calculate_step_duration(cls, step: dict[str, Any], fps: int = 60) -> float:
        kind = step.get("kind", "action")
        if kind == "cmd":
            speed = step.get("typeSpeed", 0.035)
            text_len = len(step.get("text", ""))
            type_frames = math.ceil(text_len * speed * fps)
            hold = step.get("holdSeconds", 0.3)
            return type_frames / fps + hold
        elif kind == "out":
            reveal_frames = max(2, math.ceil(0.08 * fps))
            hold = step.get("holdSeconds", 0.15)
            return reveal_frames / fps + hold
        elif kind == "pause" or kind == "wait":
            return float(step.get("seconds", step.get("duration", 0.5)))
        elif kind == "action" or kind == "pop":
            return float(step.get("duration", 0.8))
        elif kind == "pill" or kind == "overlay":
            # Non-blocking overlay
            return 0.0
        return float(step.get("duration", 0.5))

    @classmethod
    def verify_alignment(
        cls,
        steps: Sequence[dict[str, Any]],
        scene_start: float,
        scene_end: float,
        narration_cues: Sequence[tuple[float, str]],
        tolerance: float = 1.0,
        fps: int = 60,
    ) -> PacingReport:
        landmarks = cls.trace_landmarks(steps, scene_start=scene_start, fps=fps)
        total_dur = sum(cls.calculate_step_duration(s, fps=fps) for s in steps)
        computed_end = round(scene_start + total_dur, 2)

        mismatches: list[str] = []
        if computed_end > scene_end + 0.1:
            mismatches.append(
                f"Visual steps duration ({total_dur:.2f}s) overflows scene window (start={scene_start}s, end={scene_end}s)"
            )

        for cue_time, cue_desc in narration_cues:
            # Find closest landmark
            matched = False
            for lm in landmarks:
                if abs(lm.video_time - cue_time) <= tolerance:
                    matched = True
                    break
            if not matched:
                closest = min(landmarks, key=lambda l: abs(l.video_time - cue_time)) if landmarks else None
                closest_str = f"closest is {closest.video_time}s ({closest.label})" if closest else "no landmarks found"
                mismatches.append(
                    f"Narration cue at {cue_time:.2f}s ('{cue_desc}') has no matching visual event within ±{tolerance}s ({closest_str})"
                )

        return PacingReport(
            is_aligned=len(mismatches) == 0,
            scene_start=scene_start,
            scene_end=scene_end,
            total_duration=total_dur,
            landmarks=landmarks,
            mismatches=mismatches,
        )
