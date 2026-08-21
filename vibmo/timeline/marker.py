"""
Editorial Markers and Timeline Cues for NLE Compositions and Scenes.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
from vibmo.core.color import Color, colors


@dataclass
class Marker:
    """
    An editorial marker positioned on a timeline or composition.
    Used for beat drops, scene transitions, cut points, and agent cue annotations.
    """

    time: float
    name: str
    color: Union[Color, str] = "#00ffff"
    comment: str = ""
    duration: float = 0.0  # Duration for range markers (e.g. intro section)

    @property
    def end_time(self) -> float:
        return self.time + max(0.0, self.duration)

    def to_dict(self) -> Dict[str, Any]:
        c = self.color if isinstance(self.color, str) else self.color.to_hex()
        return {
            "time": self.time,
            "name": self.name,
            "color": c,
            "comment": self.comment,
            "duration": self.duration,
            "end_time": self.end_time,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Marker:
        return cls(
            time=float(data.get("time", 0.0)),
            name=str(data.get("name", "")),
            color=data.get("color", "#00ffff"),
            comment=str(data.get("comment", "")),
            duration=float(data.get("duration", 0.0)),
        )
