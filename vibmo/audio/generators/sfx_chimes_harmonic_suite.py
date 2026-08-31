import numpy as np

class ChimesHarmonicSuite:
    SAMPLE_RATE = 48000

    @staticmethod
    def crystal_bell_chime(duration=1.2, fundamental=1046.50):
        t = np.linspace(0, duration, int(ChimesHarmonicSuite.SAMPLE_RATE * duration), endpoint=False)
        overtones = [1.0, 2.76, 5.4, 8.9]

        audio = np.zeros_like(t)

        for i, ratio in enumerate(overtones):
            freq = fundamental * ratio
            amp = 1.0 / (i + 1)
            decay = 2.0 + i * 1.5
            envelope = np.exp(-t * decay)
            audio += amp * envelope * np.sin(2 * np.pi * freq * t)

        max_val = np.max(np.abs(audio))
        if max_val > 0:
            audio /= max_val

        return audio.astype(np.float32)

    @staticmethod
    def sparkle_magic_glimmer(duration=0.8, density=16):
        t_total = np.linspace(0, duration, int(ChimesHarmonicSuite.SAMPLE_RATE * duration), endpoint=False)
        audio = np.zeros_like(t_total)

        num_bells = int(duration * density)
        rng = np.random.default_rng(42)

        for _ in range(num_bells):
            start_time = rng.uniform(0, duration * 0.8)
            freq = rng.uniform(2000, 8000)
            bell_duration = rng.uniform(0.1, 0.3)

            start_idx = int(start_time * ChimesHarmonicSuite.SAMPLE_RATE)
            end_idx = min(start_idx + int(bell_duration * ChimesHarmonicSuite.SAMPLE_RATE), len(audio))

            if end_idx <= start_idx:
                continue

            t_bell = np.linspace(0, (end_idx - start_idx) / ChimesHarmonicSuite.SAMPLE_RATE, end_idx - start_idx, endpoint=False)

            envelope = np.exp(-t_bell * 15.0)
            bell_audio = envelope * np.sin(2 * np.pi * freq * t_bell)

            audio[start_idx:end_idx] += bell_audio

        max_val = np.max(np.abs(audio))
        if max_val > 0:
            audio /= max_val

        return audio.astype(np.float32)

    @staticmethod
    def dream_harp_glissando(duration=1.4, scale="pentatonic_major"):
        t = np.linspace(0, duration, int(ChimesHarmonicSuite.SAMPLE_RATE * duration), endpoint=False)
        audio = np.zeros_like(t)

        base_freq = 261.63
        if scale == "pentatonic_major":
            intervals = [0, 2, 4, 7, 9]
        else:
            intervals = [0, 2, 4, 5, 7, 9, 11]

        notes = []
        for octave in range(3):
            for interval in intervals:
                notes.append(base_freq * (2 ** octave) * (2 ** (interval / 12)))

        num_notes = len(notes)
        note_interval_time = (duration * 0.6) / num_notes

        for i, freq in enumerate(notes):
            start_time = i * note_interval_time
            start_idx = int(start_time * ChimesHarmonicSuite.SAMPLE_RATE)

            t_note = t[start_idx:]
            t_local = t_note - start_time

            envelope = np.exp(-t_local * 3.0)

            note_audio = np.sin(2 * np.pi * freq * t_local)
            note_audio += 0.5 * np.sin(2 * np.pi * freq * 2 * t_local)
            note_audio += 0.25 * np.sin(2 * np.pi * freq * 3 * t_local)

            audio[start_idx:] += envelope * note_audio * (1.0 / num_notes)

        max_val = np.max(np.abs(audio))
        if max_val > 0:
            audio /= max_val

        return audio.astype(np.float32)

    @staticmethod
    def celebration_fanfare_tone(duration=1.0):
        t = np.linspace(0, duration, int(ChimesHarmonicSuite.SAMPLE_RATE * duration), endpoint=False)
        audio = np.zeros_like(t)

        frequencies = [261.63, 329.63, 392.00, 523.25]

        attack_time = 0.1
        decay_time = 0.2
        sustain_level = 0.7
        release_time = 0.3

        attack_samples = int(attack_time * ChimesHarmonicSuite.SAMPLE_RATE)
        decay_samples = int(decay_time * ChimesHarmonicSuite.SAMPLE_RATE)
        release_samples = int(release_time * ChimesHarmonicSuite.SAMPLE_RATE)
        sustain_samples = len(t) - attack_samples - decay_samples - release_samples

        if sustain_samples < 0:
            envelope = np.ones_like(t)
        else:
            attack = np.linspace(0, 1, attack_samples, endpoint=False)
            decay = np.linspace(1, sustain_level, decay_samples, endpoint=False)
            sustain = np.ones(sustain_samples) * sustain_level
            release = np.linspace(sustain_level, 0, release_samples, endpoint=False)
            envelope = np.concatenate([attack, decay, sustain, release])
            if len(envelope) < len(t):
                envelope = np.pad(envelope, (0, len(t) - len(envelope)), 'constant')
            else:
                envelope = envelope[:len(t)]

        for freq in frequencies:
            for h in range(1, 8):
                h_amp = 1.0 / (h ** 1.5)
                audio += h_amp * np.sin(2 * np.pi * freq * h * t)

        audio *= envelope

        max_val = np.max(np.abs(audio))
        if max_val > 0:
            audio /= max_val

        return audio.astype(np.float32)

    @staticmethod
    def celestial_wind_chime(duration: float = 1.2) -> np.ndarray:
        """Gentle polyphonic celestial wind chime cluster with harmonic shimmer."""
        t = np.linspace(0, duration, int(ChimesHarmonicSuite.SAMPLE_RATE * duration), endpoint=False)
        audio = np.zeros_like(t)

        chimes = [
            {"freq": 1046.50, "time": 0.00, "amp": 0.8},
            {"freq": 1318.51, "time": 0.08, "amp": 0.7},
            {"freq": 1567.98, "time": 0.16, "amp": 0.6},
            {"freq": 2093.00, "time": 0.28, "amp": 0.75},
            {"freq": 2637.02, "time": 0.40, "amp": 0.5},
        ]

        for ch in chimes:
            start_idx = int(ch["time"] * ChimesHarmonicSuite.SAMPLE_RATE)
            if start_idx >= len(t):
                continue
            t_sub = t[start_idx:] - ch["time"]
            env = np.exp(-t_sub * 4.5)
            chime_wave = np.sin(2 * np.pi * ch["freq"] * t_sub)
            chime_wave += 0.3 * np.sin(2 * np.pi * ch["freq"] * 2.76 * t_sub)
            audio[start_idx:] += chime_wave * env * ch["amp"]

        max_val = np.max(np.abs(audio))
        if max_val > 0:
            audio /= max_val

        return audio.astype(np.float32)

