import numpy as np
from scipy import signal

class WhooshDesignerSuite:
    SAMPLE_RATE = 48000

    @staticmethod
    def _normalize_and_format(stereo_array):
        """Ensures the array is float32 and peak normalized to 1.0 (if not silent)."""
        out = stereo_array.astype(np.float32)
        peak = np.max(np.abs(out))
        if peak > 0:
            out = out / peak
        return out

    @staticmethod
    def _pink_noise(n_samples):
        """Generates pink noise using a 1/f filter on white noise."""
        white = np.random.normal(0, 1, n_samples)
        # Simple pinking filter
        b, a = signal.butter(1, 0.05, btype='high')
        pink = signal.lfilter(b, a, white)
        return pink

    @staticmethod
    def doppler_whip(duration=0.35, speed=2.5):
        """High-velocity whip whoosh with dynamic pitch sweep and stereo-panned frequency shift."""
        sr = WhooshDesignerSuite.SAMPLE_RATE
        n_samples = int(sr * duration)
        t = np.linspace(0, duration, n_samples, endpoint=False)

        # Pitch sweep: high to low quickly
        f0, f1 = 1500 * speed, 100 * speed
        # Exponential sweep
        freqs = f0 * (f1 / f0) ** (t / duration)
        phase = np.cumsum(freqs) / sr * 2 * np.pi

        tone = np.sin(phase)
        noise = np.random.normal(0, 1, n_samples)

        # Mix tone and noise
        mixed = tone * 0.3 + noise * 0.7

        # Envelope: fast attack, logarithmic decay
        env = t / (0.1 * duration) * np.exp(1 - t / (0.1 * duration))
        env = np.clip(env, 0, 1)

        audio = mixed * env

        # Stereo panning: fast sweep left to right
        pan = np.linspace(0, 1, n_samples)
        left = audio * (1 - pan)
        right = audio * pan

        return WhooshDesignerSuite._normalize_and_format(np.vstack((left, right)))

    @staticmethod
    def sub_bass_flyby(duration=0.75, sub_freq=55.0):
        """Heavy low-end sub-bass fly-by with resonant low-pass filter sweep."""
        sr = WhooshDesignerSuite.SAMPLE_RATE
        n_samples = int(sr * duration)
        t = np.linspace(0, duration, n_samples, endpoint=False)

        # Sub-bass fundamentals + harmonics
        tone1 = np.sin(2 * np.pi * sub_freq * t)
        tone2 = np.sin(2 * np.pi * (sub_freq * 2.01) * t) * 0.5
        noise = np.random.normal(0, 1, n_samples) * 0.3

        raw_audio = tone1 + tone2 + noise

        # Low-pass filter sweep (simulate using time-varying or simple fixed with swell)
        # We can simulate the filter sweep by creating a dynamic mix of filtered signals
        b, a = signal.butter(4, 300 / (sr / 2), btype='low')
        filtered_audio = signal.lfilter(b, a, raw_audio)

        # Envelope: slow swell up and fade out (bell shape)
        env = np.sin(np.pi * t / duration) ** 2

        audio = filtered_audio * env

        # Panning: center-heavy, slight movement
        pan = 0.5 + 0.3 * np.sin(2 * np.pi * t / duration)
        left = audio * (1 - pan)
        right = audio * pan

        return WhooshDesignerSuite._normalize_and_format(np.vstack((left, right)))

    @staticmethod
    def airy_transition(duration=0.50, breath_noise=0.8):
        """Soft, airy transition whoosh using filtered white/pink noise envelope."""
        sr = WhooshDesignerSuite.SAMPLE_RATE
        n_samples = int(sr * duration)
        t = np.linspace(0, duration, n_samples, endpoint=False)

        # Pink noise base
        noise = WhooshDesignerSuite._pink_noise(n_samples)

        # Bandpass filter for airy sound
        b, a = signal.butter(2, [1000 / (sr / 2), 8000 / (sr / 2)], btype='bandpass')
        filtered_noise = signal.lfilter(b, a, noise)

        # Envelope: smooth bell curve
        env = np.exp(-((t - duration/2)**2) / (2 * (duration/5)**2))

        audio = filtered_noise * env * breath_noise

        # Stereo spread: mostly centered but wide
        left = audio * 0.9 + np.random.normal(0, 0.05, n_samples) * env
        right = audio * 0.9 + np.random.normal(0, 0.05, n_samples) * env

        return WhooshDesignerSuite._normalize_and_format(np.vstack((left, right)))

    @staticmethod
    def quick_snap_whoosh(duration=0.18):
        """Fast swipe whoosh for rapid slide cuts and card fly-ins."""
        sr = WhooshDesignerSuite.SAMPLE_RATE
        n_samples = int(sr * duration)
        t = np.linspace(0, duration, n_samples, endpoint=False)

        noise = np.random.normal(0, 1, n_samples)

        # High-pass filter to remove low end
        b, a = signal.butter(2, 2000 / (sr / 2), btype='high')
        filtered_noise = signal.lfilter(b, a, noise)

        # Very sharp envelope: fast attack, exponential decay
        env = np.exp(-15 * t / duration) * (1 - np.exp(-100 * t / duration))

        audio = filtered_noise * env

        # Center pan
        left = audio * 0.707
        right = audio * 0.707

        return WhooshDesignerSuite._normalize_and_format(np.vstack((left, right)))

    @staticmethod
    def cinematic_passby(duration=1.2, speed=1.8, sub_impact=True):
        """Cinematic whoosh pass-by sound with dynamic stereo pan and low-mid resonant sweep."""
        sr = WhooshDesignerSuite.SAMPLE_RATE
        n_samples = int(sr * duration)
        if n_samples == 0:
            return np.zeros((2, 0), dtype=np.float32)
        t = np.linspace(0, duration, n_samples, endpoint=False)

        # Broadband filtered noise pass-by sweep
        noise = WhooshDesignerSuite._pink_noise(n_samples)

        # Resonant bandpass filter
        b, a = signal.butter(2, [150 / (sr / 2), 4000 / (sr / 2)], btype='bandpass')
        filtered_noise = signal.lfilter(b, a, noise)

        # Sub rumble underlay
        sub_tone = np.sin(2 * np.pi * 50.0 * t) * np.exp(-((t - duration * 0.5) ** 2) / (2 * (duration * 0.2) ** 2))

        # Overall envelope: smooth swell and decay
        env = np.sin(np.pi * (t / duration)) ** 2

        audio_mono = (filtered_noise * 0.8 + (sub_tone * 0.4 if sub_impact else 0.0)) * env

        # Stereo panning sweep: Left -> Center -> Right
        pan = np.clip((t - duration * 0.2) / max(1e-6, (duration * 0.6)), 0.0, 1.0)
        left = audio_mono * np.cos(pan * np.pi / 2)
        right = audio_mono * np.sin(pan * np.pi / 2)

        return WhooshDesignerSuite._normalize_and_format(np.vstack((left, right)))

