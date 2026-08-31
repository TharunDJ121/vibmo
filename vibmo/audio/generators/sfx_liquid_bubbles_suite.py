import numpy as np

class LiquidBubblesSuite:
    """Procedural Liquid & Bubble Foley sound generator suite."""
    SAMPLE_RATE = 48000

    @classmethod
    def liquid_drop_splash(cls, duration=0.15, resonant_pitch=1200.0) -> np.ndarray:
        """Single water droplet impact with rising pitch bubble ring."""
        sr = cls.SAMPLE_RATE
        n_samples = int(duration * sr)
        if n_samples == 0:
            return np.array([], dtype=np.float32)

        t = np.linspace(0, duration, n_samples, endpoint=False)

        # Rising pitch for bubble ring
        freq_start = resonant_pitch * 0.3
        freq_end = resonant_pitch

        # Exponential frequency rise
        freqs = freq_start * ((freq_end / freq_start) ** (t / duration))
        phase = 2.0 * np.pi * np.cumsum(freqs) / sr

        # Envelope: fast attack, exponential decay
        env = np.exp(-t * 20.0)

        # Add a brief burst of noise at the very beginning for the "impact" splash
        noise_env = np.exp(-t * 150.0)
        noise = np.random.RandomState(42).randn(n_samples) * noise_env * 0.3

        audio = (np.sin(phase) * env + noise) * 0.8
        return audio.astype(np.float32)

    @classmethod
    def viscous_pop_bubble(cls, duration=0.09) -> np.ndarray:
        """Playful bubbly UI toggle pop with rounded low-mid resonance."""
        sr = cls.SAMPLE_RATE
        n_samples = int(duration * sr)
        if n_samples == 0:
            return np.array([], dtype=np.float32)

        t = np.linspace(0, duration, n_samples, endpoint=False)

        # Very fast pitch drop followed by steady resonance (rounded pop)
        freq_start = 800.0
        freq_end = 300.0

        # Use an exponential decay curve for pitch drop
        freqs = freq_end + (freq_start - freq_end) * np.exp(-t * 80.0)
        phase = 2.0 * np.pi * np.cumsum(freqs) / sr

        # Envelope: fast attack, slower exponential decay
        attack_time = 0.01
        attack = np.minimum(t / attack_time, 1.0)
        decay = np.exp(-(t - np.minimum(t, attack_time)) * 30.0)
        env = attack * decay

        audio = np.sin(phase) * env * 0.85
        return audio.astype(np.float32)

    @classmethod
    def submerged_bubble_cluster(cls, duration=0.6, bubble_count=10) -> np.ndarray:
        """Effervescent sparkling soda bubble stream."""
        sr = cls.SAMPLE_RATE
        n_samples = int(duration * sr)
        if n_samples == 0:
            return np.array([], dtype=np.float32)

        t = np.linspace(0, duration, n_samples, endpoint=False)
        master = np.zeros(n_samples, dtype=np.float32)
        rng = np.random.RandomState(42)

        for _ in range(bubble_count):
            # Randomize bubble parameters
            start_time = rng.uniform(0, duration * 0.8)
            bubble_dur = rng.uniform(0.02, 0.08)

            start_sample = int(start_time * sr)
            b_samples = int(bubble_dur * sr)

            if start_sample + b_samples > n_samples:
                b_samples = n_samples - start_sample

            if b_samples <= 0:
                continue

            bt = np.linspace(0, bubble_dur, b_samples, endpoint=False)

            # Fast pitch drop like a pop but higher pitch
            freq_start = rng.uniform(1500, 2500)
            freq_end = freq_start * rng.uniform(0.3, 0.6)

            freqs = freq_end + (freq_start - freq_end) * np.exp(-bt * 120.0)
            phase = 2.0 * np.pi * np.cumsum(freqs) / sr

            env = np.exp(-bt * (1.0 / bubble_dur) * 4.0)

            bubble_audio = np.sin(phase) * env * rng.uniform(0.3, 0.7)
            master[start_sample:start_sample + b_samples] += bubble_audio

        # Normalize to prevent clipping, but leave headroom
        max_amp = np.max(np.abs(master))
        if max_amp > 0:
            master = master * (0.8 / max_amp)

        return master.astype(np.float32)

    @classmethod
    def water_pour_stream(cls, duration=2.0) -> np.ndarray:
        """Continuous organic pouring liquid stream with fluctuating frequency modes."""
        sr = cls.SAMPLE_RATE
        n_samples = int(duration * sr)
        if n_samples == 0:
            return np.array([], dtype=np.float32)

        t = np.linspace(0, duration, n_samples, endpoint=False)
        rng = np.random.RandomState(42)

        # Base white noise
        noise = rng.randn(n_samples)

        # We simulate the pouring sound using frequency-modulated bandpass filters
        # To do this efficiently without scipy filters, we use phase modulation of multiple sine carriers

        audio = np.zeros(n_samples, dtype=np.float64)

        # Add a few resonant modes that wobble in frequency
        modes = [
            {"base_f": 400.0, "wobble_f": 2.0, "wobble_amt": 50.0, "amp": 0.4},
            {"base_f": 800.0, "wobble_f": 3.5, "wobble_amt": 100.0, "amp": 0.3},
            {"base_f": 1500.0, "wobble_f": 1.5, "wobble_amt": 300.0, "amp": 0.2},
            {"base_f": 2500.0, "wobble_f": 4.1, "wobble_amt": 500.0, "amp": 0.15},
        ]

        for mode in modes:
            # Wobbly frequency
            freq_variation = np.sin(2.0 * np.pi * mode["wobble_f"] * t) * mode["wobble_amt"]

            # The mode resonates based on the noise input
            # We approximate this by ring-modulating a sine wave with smoothed noise
            smoothed_noise = np.convolve(noise, np.ones(50)/50.0, mode='same')

            phase = 2.0 * np.pi * np.cumsum(mode["base_f"] + freq_variation) / sr
            carrier = np.sin(phase)

            audio += carrier * smoothed_noise * mode["amp"]

        # Add high frequency "splatter" noise
        high_noise = noise * np.sin(2.0 * np.pi * np.cumsum(np.linspace(4000, 6000, n_samples)) / sr)
        audio += high_noise * 0.15

        # Smooth attack and release
        attack_time = 0.2
        release_time = 0.3

        attack_samples = int(attack_time * sr)
        release_samples = int(release_time * sr)

        env = np.ones(n_samples)
        if attack_samples > 0:
            env[:attack_samples] = np.linspace(0, 1, attack_samples)
        if release_samples > 0 and n_samples > release_samples:
            env[-release_samples:] = np.linspace(1, 0, release_samples)

        audio = audio * env

        # Normalize
        max_amp = np.max(np.abs(audio))
        if max_amp > 0:
            audio = audio * (0.8 / max_amp)

        return audio.astype(np.float32)

    @classmethod
    def water_bubble_pop(cls, duration: float = 0.09) -> np.ndarray:
        """Crisp organic water bubble pop with resonant frequency decay."""
        return cls.viscous_pop_bubble(duration=duration)

