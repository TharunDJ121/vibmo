"""
Fast FFT Spectrum decomposition, RMS power, and Beat Onset Detection.
"""

from __future__ import annotations
import math
import numpy as np
from typing import List, Tuple
from vibmo.audio.track import AudioTrack


class AudioAnalyzer:
    """Extracts frequency bands (Bass, Mid, Treble) and beat transients from an AudioTrack."""

    def __init__(self, track: AudioTrack, window_size: int = 2048) -> None:
        self.track = track
        self.window_size = window_size
        self._beat_times: List[float] = []
        self._spectrum_cache: dict[int, np.ndarray] = {}
        self._detect_beats()

    def get_spectrum(self, time: float) -> np.ndarray:
        """Returns normalized frequency spectrum magnitudes at time t with sub-frame caching."""
        if len(self.track.samples) == 0:
            return np.zeros(self.window_size // 2, dtype=np.float32)

        # Cache key quantized to 5ms resolution
        cache_key = int(time * 200)
        if cache_key in self._spectrum_cache:
            return self._spectrum_cache[cache_key]

        idx = int(time * self.track.sample_rate)
        half_win = self.window_size // 2
        start = max(0, idx - half_win)
        end = min(len(self.track.samples), start + self.window_size)
        chunk = self.track.samples[start:end]

        if len(chunk) < self.window_size:
            chunk = np.pad(chunk, (0, self.window_size - len(chunk)))

        windowed = chunk * np.hanning(self.window_size)
        fft_vals = np.abs(np.fft.rfft(windowed))
        norm = np.max(fft_vals) if np.max(fft_vals) > 1e-4 else 1.0
        res = (fft_vals / norm).astype(np.float32)
        self._spectrum_cache[cache_key] = res
        return res

    def bass(self, time: float) -> float:
        """Normalized energy in bass band (20Hz - 250Hz)."""
        spec = self.get_spectrum(time)
        freq_bin_hz = (self.track.sample_rate * 0.5) / len(spec)
        bin_start = int(20 / freq_bin_hz)
        bin_end = max(bin_start + 1, int(250 / freq_bin_hz))
        return float(np.mean(spec[bin_start:bin_end]))

    def mid(self, time: float) -> float:
        """Normalized energy in mid band (250Hz - 4000Hz)."""
        spec = self.get_spectrum(time)
        freq_bin_hz = (self.track.sample_rate * 0.5) / len(spec)
        bin_start = int(250 / freq_bin_hz)
        bin_end = max(bin_start + 1, int(4000 / freq_bin_hz))
        return float(np.mean(spec[bin_start:bin_end]))

    def treble(self, time: float) -> float:
        """Normalized energy in treble band (4000Hz - 20000Hz)."""
        spec = self.get_spectrum(time)
        freq_bin_hz = (self.track.sample_rate * 0.5) / len(spec)
        bin_start = int(4000 / freq_bin_hz)
        bin_end = max(bin_start + 1, int(18000 / freq_bin_hz))
        return float(np.mean(spec[bin_start:bin_end]))

    def rms(self, time: float, window_sec: float = 0.05) -> float:
        """Overall RMS amplitude at time t."""
        idx = int(time * self.track.sample_rate)
        win = int(window_sec * self.track.sample_rate)
        start = max(0, idx - win // 2)
        end = min(len(self.track.samples), start + win)
        chunk = self.track.samples[start:end]
        if len(chunk) == 0:
            return 0.0
        return float(np.sqrt(np.mean(chunk * chunk)))

    def _detect_beats(self) -> None:
        """Simple onset energy peak detector."""
        if len(self.track.samples) == 0:
            return
        step_sec = 0.05
        times = np.arange(0, self.track.duration, step_sec)
        energies = [self.rms(t) for t in times]
        if not energies:
            return

        mean_energy = float(np.mean(energies))
        std_energy = float(np.std(energies))
        thresh = mean_energy + std_energy * 1.2

        for i, (t, e) in enumerate(zip(times, energies)):
            if e > thresh:
                if not self._beat_times or (t - self._beat_times[-1]) > 0.25:
                    self._beat_times.append(float(t))

    def beats(self) -> List[float]:
        return self._beat_times

    def next_beat(self, current_time: float) -> float:
        for b in self._beat_times:
            if b > current_time:
                return b
        return current_time + 0.5
