"""
Procedural Foley and UI Sound Effects Generator (Pops, Clicks, Whooshes, Risers, Bass Drops).
Generates high-fidelity 48kHz audio directly in Python without requiring external asset files.
"""

from __future__ import annotations
import math
import os
import tempfile
from typing import Dict, List, Optional, Tuple
import numpy as np
from scipy.io import wavfile


class ProceduralSFX:
    """Procedural synthesizer for UI and cinematic motion sound effects."""

    SAMPLE_RATE = 48000

    @classmethod
    def generate(cls, name: str, duration: Optional[float] = None) -> np.ndarray:
        """Generates float32 mono audio array in [-1.0, 1.0]."""
        name = name.lower()
        if name in ("pop", "bubble"):
            return cls.pop(duration=duration or 0.12)
        elif name in ("click", "tap"):
            return cls.click(duration=duration or 0.04)
        elif name in ("whoosh", "swoosh", "swipe"):
            return cls.whoosh(duration=duration or 0.45)
        elif name in ("riser", "sweep"):
            return cls.riser(duration=duration or 1.2)
        elif name in ("bass_drop", "thud", "impact"):
            return cls.bass_drop(duration=duration or 0.6)
        elif name in ("sparkle", "chime", "magic"):
            return cls.sparkle(duration=duration or 0.5)
        else:
            raise KeyError(f"Unknown procedural sound '{name}'. Supported: pop, click, whoosh, riser, bass_drop, sparkle")


    @classmethod
    def pop(cls, duration: float = 0.12, freq_start: float = 240.0, freq_end: float = 880.0) -> np.ndarray:
        """Playful bubbly pop with exponential decay."""
        sr = cls.SAMPLE_RATE
        n_samples = int(duration * sr)
        t = np.linspace(0, duration, n_samples, endpoint=False)
        
        # Exponential frequency pitch rise
        freqs = freq_start * ((freq_end / freq_start) ** (t / duration))
        phase = 2.0 * np.pi * np.cumsum(freqs) / sr
        
        # Fast attack, exponential decay envelope
        env = np.exp(-t * 32.0)
        audio = np.sin(phase) * env * 0.75
        return audio.astype(np.float32)

    @classmethod
    def click(cls, duration: float = 0.04, freq: float = 1850.0) -> np.ndarray:
        """Crisp mechanical mouse / UI switch click."""
        sr = cls.SAMPLE_RATE
        n_samples = int(duration * sr)
        t = np.linspace(0, duration, n_samples, endpoint=False)
        
        env = np.exp(-t * 90.0)
        audio = (np.sin(2.0 * np.pi * freq * t) * 0.7 + np.sin(2.0 * np.pi * freq * 2.2 * t) * 0.3) * env * 0.65
        return audio.astype(np.float32)

    @classmethod
    def whoosh(cls, duration: float = 0.45) -> np.ndarray:
        """Airy whoosh for fast camera and card fly-in transitions."""
        sr = cls.SAMPLE_RATE
        n_samples = int(duration * sr)
        t = np.linspace(0, duration, n_samples, endpoint=False)
        
        # Bandpass filtered white noise with bell curve amplitude
        rng = np.random.RandomState(42)
        noise = rng.randn(n_samples)
        
        # Bell curve amplitude envelope
        mid = duration * 0.45
        env = np.exp(-((t - mid) ** 2) / (2 * (duration * 0.18) ** 2))
        
        # Pitch sweep sine carrier blended with shaped noise
        f_sweep = 120.0 + 380.0 * np.sin(np.pi * t / duration)
        carrier = np.sin(2.0 * np.pi * np.cumsum(f_sweep) / sr)
        
        audio = (noise * 0.5 + carrier * 0.5) * env * 0.7
        return audio.astype(np.float32)

    @classmethod
    def riser(cls, duration: float = 1.2, f_start: float = 120.0, f_end: float = 2400.0) -> np.ndarray:
        """Tension-building riser sweep towards a beat drop."""
        sr = cls.SAMPLE_RATE
        n_samples = int(duration * sr)
        t = np.linspace(0, duration, n_samples, endpoint=False)
        
        freqs = f_start * ((f_end / f_start) ** (t / duration))
        phase = 2.0 * np.pi * np.cumsum(freqs) / sr
        
        # Swelling amplitude envelope
        env = (t / duration) ** 2.2
        audio = np.sin(phase) * env * 0.65
        return audio.astype(np.float32)

    @classmethod
    def bass_drop(cls, duration: float = 0.6, f_start: float = 140.0, f_end: float = 38.0) -> np.ndarray:
        """Deep 808 sub-bass impact thud."""
        sr = cls.SAMPLE_RATE
        n_samples = int(duration * sr)
        t = np.linspace(0, duration, n_samples, endpoint=False)
        
        freqs = f_start * ((f_end / f_start) ** (t / duration))
        phase = 2.0 * np.pi * np.cumsum(freqs) / sr
        
        env = np.exp(-t * 6.5)
        # Add slight saturation warmth
        raw = np.sin(phase) * env
        saturated = np.tanh(raw * 1.5) * 0.8
        return saturated.astype(np.float32)

    @classmethod
    def sparkle(cls, duration: float = 0.5) -> np.ndarray:
        """Magical bell chime triad."""
        sr = cls.SAMPLE_RATE
        n_samples = int(duration * sr)
        t = np.linspace(0, duration, n_samples, endpoint=False)
        
        env = np.exp(-t * 8.0)
        c1 = np.sin(2.0 * np.pi * 1046.5 * t)  # C6
        c2 = np.sin(2.0 * np.pi * 1318.5 * t)  # E6
        c3 = np.sin(2.0 * np.pi * 1567.9 * t)  # G6
        
        audio = (c1 * 0.4 + c2 * 0.35 + c3 * 0.35) * env * 0.6
        return audio.astype(np.float32)


class SFXTrack:
    """Manages scheduled foley sound effects and mixes them into a master audio track."""

    def __init__(self, sample_rate: int = 48000) -> None:
        self.sample_rate = sample_rate
        self.cues: List[Tuple[float, str, float]] = []  # (time, sound_name, volume)

    def add(self, sound: str, time: float, volume: float = 1.0) -> None:
        """Schedules a sound effect at timestamp (in seconds)."""
        self.cues.append((float(time), str(sound), float(volume)))

    def render_to_wav(self, duration: float, output_path: str) -> str:
        """Renders all cues to a master 16-bit PCM WAV file."""
        n_samples = max(100, int(duration * self.sample_rate))
        master = np.zeros(n_samples, dtype=np.float32)

        for cue_time, sound_name, volume in self.cues:
            if cue_time >= duration:
                continue
            sfx_buf = ProceduralSFX.generate(sound_name) * volume
            start_sample = max(0, int(cue_time * self.sample_rate))
            end_sample = min(n_samples, start_sample + len(sfx_buf))
            sfx_len = end_sample - start_sample
            if sfx_len > 0:
                master[start_sample:end_sample] += sfx_buf[:sfx_len]

        # Normalize without clipping
        max_amp = np.max(np.abs(master))
        if max_amp > 0.95:
            master = master * (0.95 / max_amp)

        pcm16 = (master * 32767.0).astype(np.int16)
        wavfile.write(output_path, self.sample_rate, pcm16)
        return output_path
