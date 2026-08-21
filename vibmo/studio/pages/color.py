"""
Color & Grading Page: Lift, Gamma, Gain color wheels, Tone Curves & Post-FX shader controllers.
"""

from __future__ import annotations
from typing import Any, Dict, List


class ColorGradeState:
    """Manages color grading parameters (Lift, Gamma, Gain, Exposure, Saturation)."""

    def __init__(self) -> None:
        self.exposure: float = 0.0
        self.contrast: float = 1.0
        self.saturation: float = 1.0
        self.temperature: float = 0.0
        self.tint: float = 0.0
        self.lift: Dict[str, float] = {"r": 0.0, "g": 0.0, "b": 0.0}
        self.gamma: Dict[str, float] = {"r": 0.0, "g": 0.0, "b": 0.0}
        self.gain: Dict[str, float] = {"r": 1.0, "g": 1.0, "b": 1.0}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "exposure": self.exposure,
            "contrast": self.contrast,
            "saturation": self.saturation,
            "temperature": self.temperature,
            "tint": self.tint,
            "lift": self.lift,
            "gamma": self.gamma,
            "gain": self.gain,
        }
