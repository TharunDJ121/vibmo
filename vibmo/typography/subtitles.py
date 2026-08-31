"""
Subtitle Generation, Parsing & Formatting Suite for Vibmo.

Supports:
  1. Parsing .srt, .vtt, and JSON transcripts into word-level timestamps.
  2. Generating formatted .srt, .vtt, and karaoke-highlighted caption files.
  3. Seamless bridge to KineticCaptions & AdvancedKaraokeCaptions.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Sequence


@dataclass
class SubtitleCue:
    start_time: float
    end_time: float
    text: str
    words: list[dict[str, Any]] | None = None

    def to_srt_time(self, seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int(round((seconds - int(seconds)) * 1000))
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def to_vtt_time(self, seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int(round((seconds - int(seconds)) * 1000))
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


class SubtitleGenerator:
    """Generates and parses SRT, VTT, and JSON subtitles."""

    @classmethod
    def generate_srt(cls, cues: Sequence[SubtitleCue]) -> str:
        lines: list[str] = []
        for idx, cue in enumerate(cues, 1):
            start_str = cue.to_srt_time(cue.start_time)
            end_str = cue.to_srt_time(cue.end_time)
            lines.append(str(idx))
            lines.append(f"{start_str} --> {end_str}")
            lines.append(cue.text.strip())
            lines.append("")
        return "\n".join(lines)

    @classmethod
    def generate_vtt(cls, cues: Sequence[SubtitleCue]) -> str:
        lines: list[str] = ["WEBVTT", ""]
        for idx, cue in enumerate(cues, 1):
            start_str = cue.to_vtt_time(cue.start_time)
            end_str = cue.to_vtt_time(cue.end_time)
            lines.append(str(idx))
            lines.append(f"{start_str} --> {end_str}")
            lines.append(cue.text.strip())
            lines.append("")
        return "\n".join(lines)

    @classmethod
    def parse_srt(cls, srt_content: str) -> list[SubtitleCue]:
        cues: list[SubtitleCue] = []
        pattern = re.compile(
            r"(\d+)\s*\n"
            r"(\d{2}:\d{2}:\d{2}[,\.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,\.]\d{3})\s*\n"
            r"([\s\S]*?)(?=\n\s*\d+\s*\n|\Z)",
            re.MULTILINE,
        )

        def parse_ts(ts: str) -> float:
            ts = ts.replace(",", ".")
            h, m, s = ts.split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)

        for match in pattern.finditer(srt_content.strip() + "\n"):
            start = parse_ts(match.group(2))
            end = parse_ts(match.group(3))
            text = match.group(4).strip()
            cues.append(SubtitleCue(start_time=start, end_time=end, text=text))

        return cues
