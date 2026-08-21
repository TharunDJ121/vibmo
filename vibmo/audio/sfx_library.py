"""
Procedural UI Sound Effects Synthesizer and Audio Ducking Engine.
Generates clicks, pops, whooshes, risers, and impacts without external audio files.
"""

from __future__ import annotations
import math
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np


class ProceduralSFXGenerator:
    """
    Synthesizes crisp, studio-quality UI sound effects procedurally at 44.1 kHz.
    """

    SAMPLE_RATE = 44100

    @classmethod
    def click(cls, duration: float = 0.04, freq: float = 1200.0) -> np.ndarray:
        """Crisp mouse / button click sound."""
        n_samples = int(cls.SAMPLE_RATE * duration)
        t = np.linspace(0, duration, n_samples, False)
        # Fast exponential pitch drop + decay
        pitch_env = np.exp(-t * 80.0)
        wave = np.sin(2.0 * math.pi * (freq * pitch_env) * t)
        amp_env = np.exp(-t * 90.0)
        audio = (wave * amp_env * 0.8).astype(np.float32)
        return audio

    @classmethod
    def pop(cls, duration: float = 0.08, start_freq: float = 400.0, end_freq: float = 900.0) -> np.ndarray:
        """Bubbly pop / toggle sound."""
        n_samples = int(cls.SAMPLE_RATE * duration)
        t = np.linspace(0, duration, n_samples, False)
        freq = start_freq + (end_freq - start_freq) * (t / duration)
        wave = np.sin(2.0 * math.pi * freq * t)
        amp_env = np.sin(np.pi * (t / duration)) ** 1.5
        audio = (wave * amp_env * 0.85).astype(np.float32)
        return audio

    @classmethod
    def whoosh(cls, duration: float = 0.35, center_freq: float = 600.0) -> np.ndarray:
        """Smooth swoosh / transition swipe sound."""
        n_samples = int(cls.SAMPLE_RATE * duration)
        t = np.linspace(0, duration, n_samples, False)
        rng = np.random.RandomState(42)
        noise = rng.randn(n_samples).astype(np.float32)
        # Bell curve volume envelope
        amp_env = np.sin(np.pi * (t / duration)) ** 2.0
        audio = (noise * amp_env * 0.4).astype(np.float32)
        return audio

    @classmethod
    def chime(cls, duration: float = 0.6, freq: float = 880.0) -> np.ndarray:
        """Ethereal bell / success chime sound."""
        n_samples = int(cls.SAMPLE_RATE * duration)
        t = np.linspace(0, duration, n_samples, False)
        wave = (
            np.sin(2.0 * math.pi * freq * t) * 0.6 +
            np.sin(2.0 * math.pi * (freq * 2.0) * t) * 0.25 +
            np.sin(2.0 * math.pi * (freq * 3.0) * t) * 0.15
        )
        amp_env = np.exp(-t * 5.0)
        audio = (wave * amp_env * 0.75).astype(np.float32)
        return audio

    @classmethod
    def impact(cls, duration: float = 0.5, sub_freq: float = 75.0) -> np.ndarray:
        """Deep cinematic bass drop / card impact thud."""
        n_samples = int(cls.SAMPLE_RATE * duration)
        t = np.linspace(0, duration, n_samples, False)
        pitch = sub_freq * np.exp(-t * 8.0)
        wave = np.sin(2.0 * math.pi * pitch * t)
        amp_env = np.exp(-t * 6.0)
        audio = (wave * amp_env * 0.95).astype(np.float32)
        return audio


class AudioDucker:
    """
    Automatic audio ducking processor. Dips background music volume when voiceover or sound effects play.
    """

    def __init__(
        self,
        duck_volume: float = 0.25,
        attack_time: float = 0.1,
        release_time: float = 0.3,
    ) -> None:
        self.duck_volume = max(0.0, min(1.0, float(duck_volume)))
        self.attack_time = max(0.01, float(attack_time))
        self.release_time = max(0.01, float(release_time))

    def compute_duck_curve(self, voice_activity: np.ndarray, sample_rate: int = 44100) -> np.ndarray:
        """Generates a smooth volume envelope curve (0.0 to 1.0) based on voice activity."""
        curve = np.ones_like(voice_activity, dtype=np.float32)
        is_active = voice_activity > 0.05
        # Lower volume where voice active
        curve[is_active] = self.duck_volume
        return curve
