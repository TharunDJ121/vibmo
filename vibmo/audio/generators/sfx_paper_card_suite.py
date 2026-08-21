import numpy as np
from scipy import signal

class PaperCardSuite:
    SAMPLE_RATE = 48000

    @staticmethod
    def _generate_noise(length):
        return np.random.normal(0, 1, length).astype(np.float32)

    @staticmethod
    def _apply_envelope(audio, env):
        return (audio * env).astype(np.float32)

    @staticmethod
    def card_shuffle_slide(duration=0.22):
        """Crisp poker card sliding off a deck across a smooth surface."""
        t = np.linspace(0, duration, int(PaperCardSuite.SAMPLE_RATE * duration), endpoint=False)
        noise = PaperCardSuite._generate_noise(len(t))

        # Highpass filter for crispness
        sos = signal.butter(4, 2000, 'hp', fs=PaperCardSuite.SAMPLE_RATE, output='sos')
        filtered = signal.sosfilt(sos, noise)

        # Envelope: sharp attack, sustained body, quick release
        attack = max(1, int(len(t) * 0.1))
        decay = len(t) - attack
        env = np.concatenate([
            np.linspace(0, 1, attack),
            np.linspace(1, 0, decay)**2
        ])

        audio = PaperCardSuite._apply_envelope(filtered, env)
        audio = audio / (np.max(np.abs(audio)) + 1e-9)
        return audio.astype(np.float32)

    @staticmethod
    def paper_flip_rustle(duration=0.18):
        """Organic notebook paper turn rustle with high-frequency friction noise."""
        t = np.linspace(0, duration, int(PaperCardSuite.SAMPLE_RATE * duration), endpoint=False)
        noise = PaperCardSuite._generate_noise(len(t))

        # Bandpass filter for paper rustle
        sos = signal.butter(4, [1500, 6000], 'bp', fs=PaperCardSuite.SAMPLE_RATE, output='sos')
        filtered = signal.sosfilt(sos, noise)

        # Envelope: multiple peaks for crinkling rustle
        env = np.sin(np.pi * t / duration) * (0.5 + 0.5 * np.sin(20 * np.pi * t / duration))
        env = env * np.linspace(1, 0, len(t))

        audio = PaperCardSuite._apply_envelope(filtered, env)
        audio = audio / (np.max(np.abs(audio)) + 1e-9)
        return audio.astype(np.float32)

    @staticmethod
    def sheet_unfold_crinkle(duration=0.35):
        """Origami/map paper unfolding crinkle texture."""
        t = np.linspace(0, duration, int(PaperCardSuite.SAMPLE_RATE * duration), endpoint=False)
        noise = PaperCardSuite._generate_noise(len(t))

        # Crinkle has a bit more mid frequencies
        sos = signal.butter(4, [800, 8000], 'bp', fs=PaperCardSuite.SAMPLE_RATE, output='sos')
        filtered = signal.sosfilt(sos, noise)

        # Envelope: randomish peaks
        env_noise = np.abs(PaperCardSuite._generate_noise(len(t)))
        sos_env = signal.butter(2, 20, 'lp', fs=PaperCardSuite.SAMPLE_RATE, output='sos')
        env = signal.sosfilt(sos_env, env_noise)

        # Fade in and out
        fade_len = max(1, int(len(t) * 0.1))
        fade = np.ones(len(t))
        fade[:fade_len] = np.linspace(0, 1, fade_len)
        fade[-fade_len:] = np.linspace(1, 0, fade_len)

        env = env * fade
        env = env / (np.max(np.abs(env)) + 1e-9)

        audio = PaperCardSuite._apply_envelope(filtered, env)
        audio = audio / (np.max(np.abs(audio)) + 1e-9)
        return audio.astype(np.float32)

    @staticmethod
    def deck_snap_slide(duration=0.12):
        """Snappy tactile card snap on a UI dashboard."""
        t = np.linspace(0, duration, int(PaperCardSuite.SAMPLE_RATE * duration), endpoint=False)
        noise = PaperCardSuite._generate_noise(len(t))

        # Highpass for snap
        sos = signal.butter(4, 3000, 'hp', fs=PaperCardSuite.SAMPLE_RATE, output='sos')
        filtered = signal.sosfilt(sos, noise)

        # Short attack, exponential decay
        attack = max(1, int(len(t) * 0.05))
        decay = len(t) - attack
        env = np.concatenate([
            np.linspace(0, 1, attack),
            np.exp(-np.linspace(0, 10, decay))
        ])

        audio = PaperCardSuite._apply_envelope(filtered, env)
        audio = audio / (np.max(np.abs(audio)) + 1e-9)
        return audio.astype(np.float32)
