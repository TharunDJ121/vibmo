"""
CapCut & JianYing Desktop Draft Exporter for Vibmo.
Inspired by video-shotcraft jianying-export.
Converts Vibmo timelines into native CapCut/JianYing JSON drafts with microsecond accuracy.
"""

from __future__ import annotations
import json
import os
import uuid
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass


@dataclass
class DraftVideoSegment:
    name: str
    start_frame: int
    end_frame: int
    source_file: str = "plate.mp4"


@dataclass
class DraftSubtitleCue:
    text: str
    start_frame: int
    end_frame: int
    style: str = "default"


@dataclass
class DraftAudioCue:
    name: str
    start_frame: int
    duration_frames: int
    volume: float = 0.8
    source_file: str = "sfx.mp3"


class JianYingDraftExporter:
    """
    Exports Vibmo scenes into CapCut / JianYing project draft formats.
    Ensures exact microsecond boundary calculations:
    Timerange: start_us = round(f0 * 1_000_000 / fps), duration_us = round(f1 * 1_000_000 / fps) - start_us
    """

    def __init__(self, fps: float = 60.0, width: int = 1920, height: int = 1080) -> None:
        self.fps = fps
        self.width = width
        self.height = height
        self.video_segments: List[DraftVideoSegment] = []
        self.subtitles: List[DraftSubtitleCue] = []
        self.audio_cues: List[DraftAudioCue] = []

    def f2us(self, frame_index: int) -> int:
        """Converts frame index to microseconds."""
        return round(frame_index * 1_000_000 / self.fps)

    def add_video_segment(self, name: str, start_frame: int, end_frame: int, source_file: str = "plate.mp4") -> None:
        self.video_segments.append(DraftVideoSegment(name, start_frame, end_frame, source_file))

    def add_subtitle(self, text: str, start_frame: int, end_frame: int) -> None:
        self.subtitles.append(DraftSubtitleCue(text, start_frame, end_frame))

    def add_audio(self, name: str, start_frame: int, duration_frames: int, volume: float = 0.8, source_file: str = "sfx.mp3") -> None:
        self.audio_cues.append(DraftAudioCue(name, start_frame, duration_frames, volume, source_file))

    def build_draft_payload(self) -> Dict[str, Any]:
        """Constructs the full JSON payload for CapCut / JianYing draft content."""
        draft_id = str(uuid.uuid4())
        
        # Build Tracks
        video_track = {"id": str(uuid.uuid4()), "type": "video", "segments": []}
        for seg in self.video_segments:
            start_us = self.f2us(seg.start_frame)
            end_us = self.f2us(seg.end_frame)
            dur_us = end_us - start_us
            video_track["segments"].append({
                "id": str(uuid.uuid4()),
                "name": seg.name,
                "target_timerange": {"start": start_us, "duration": dur_us},
                "source_timerange": {"start": start_us, "duration": dur_us},
            })

        subtitle_track = {"id": str(uuid.uuid4()), "type": "text", "segments": []}
        for sub in self.subtitles:
            start_us = self.f2us(sub.start_frame)
            end_us = self.f2us(sub.end_frame)
            dur_us = end_us - start_us
            subtitle_track["segments"].append({
                "id": str(uuid.uuid4()),
                "text": sub.text,
                "target_timerange": {"start": start_us, "duration": dur_us},
            })

        audio_track = {"id": str(uuid.uuid4()), "type": "audio", "segments": []}
        for aud in self.audio_cues:
            start_us = self.f2us(aud.start_frame)
            dur_us = self.f2us(aud.duration_frames)
            audio_track["segments"].append({
                "id": str(uuid.uuid4()),
                "name": aud.name,
                "volume": aud.volume,
                "target_timerange": {"start": start_us, "duration": dur_us},
            })

        return {
            "version": "11.2.0",
            "id": draft_id,
            "canvas_config": {
                "width": self.width,
                "height": self.height,
                "fps": self.fps,
            },
            "tracks": [video_track, subtitle_track, audio_track],
        }

    def export_to_file(self, output_path: str) -> str:
        """Writes the draft JSON to disk."""
        payload = self.build_draft_payload()
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        return output_path
