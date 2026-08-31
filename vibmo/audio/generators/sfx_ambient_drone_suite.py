import numpy as np

class AmbientDroneSuite:
    """
    Procedural Sci-Fi Drone & Atmospheric Sound generator suite.
    Produces 48kHz float32 NumPy audio arrays.
    """

    SAMPLE_RATE = 48000

    @staticmethod
    def dark_scifi_drone(duration=5.0, root_freq=55.0):
        """
        Multi-oscillator detuned sub drone with slow harmonic phase movement.
        """
        sr = AmbientDroneSuite.SAMPLE_RATE
        N = int(sr * duration)
        t = np.linspace(0, duration, N, endpoint=False)
        base_hz = 1.0 / duration

        freqs = [
            round(root_freq * 0.98 / base_hz) * base_hz,
            round(root_freq / base_hz) * base_hz,
            round(root_freq * 1.02 / base_hz) * base_hz,
            round(root_freq * 2.00 / base_hz) * base_hz,
            round(root_freq * 0.50 / base_hz) * base_hz,
        ]
        amps = [0.4, 0.6, 0.4, 0.2, 0.5]

        left = np.zeros_like(t)
        right = np.zeros_like(t)

        # LFOs for amplitude modulation to create slow harmonic phase movement
        lfo_freqs = [
            round(0.1 / base_hz) * base_hz or base_hz,
            round(0.2 / base_hz) * base_hz or base_hz,
            round(0.15 / base_hz) * base_hz or base_hz,
            round(0.3 / base_hz) * base_hz or base_hz,
            round(0.05 / base_hz) * base_hz or base_hz,
        ]

        for i, (f, a) in enumerate(zip(freqs, amps)):
            lfo = 0.5 + 0.5 * np.sin(2 * np.pi * lfo_freqs[i] * t + i)
            left += a * np.sin(2 * np.pi * f * t) * lfo
            right += a * np.sin(2 * np.pi * f * t + 0.5) * lfo

        max_val = np.max(np.abs(left)) + 1e-6
        left = (left / max_val * 0.8).astype(np.float32)
        right = (right / (np.max(np.abs(right)) + 1e-6) * 0.8).astype(np.float32)

        return np.column_stack((left, right))

    @staticmethod
    def warp_drive_hum(duration=4.0, rpm=120.0):
        """
        Throbbing spacecraft hyperdrive hum with stereo rotary phase.
        """
        sr = AmbientDroneSuite.SAMPLE_RATE
        N = int(sr * duration)
        t = np.linspace(0, duration, N, endpoint=False)
        base_hz = 1.0 / duration

        rps = rpm / 60.0
        rps = round(rps / base_hz) * base_hz
        if rps == 0:
            rps = base_hz

        fundamental = round(60.0 / base_hz) * base_hz
        harmonics = [fundamental, fundamental*2, fundamental*3, fundamental*4]

        signal = np.zeros_like(t)
        for h in harmonics:
            signal += np.sin(2 * np.pi * h * t) / (h / fundamental)

        # Rotary effect (stereo phase)
        pan = 0.5 + 0.5 * np.sin(2 * np.pi * rps * t)

        left = signal * pan
        right = signal * (1.0 - pan)

        left = (left / (np.max(np.abs(left)) + 1e-6) * 0.7).astype(np.float32)
        right = (right / (np.max(np.abs(right)) + 1e-6) * 0.7).astype(np.float32)

        return np.column_stack((left, right))

    @staticmethod
    def server_room_fan_hum(duration=4.0):
        """
        Realistic server farm cooling air ventilation noise with low frequency resonant hums.
        """
        sr = AmbientDroneSuite.SAMPLE_RATE
        N = int(sr * duration)

        # Generate frequency domain noise for perfect looping
        freqs = np.fft.rfftfreq(N, 1/sr)

        # Pink-ish noise profile
        mag = np.ones_like(freqs)
        # Avoid division by zero at freq=0
        with np.errstate(divide='ignore'):
            mag = np.where(freqs > 0, 1.0 / np.sqrt(freqs), 0.0)

        # Resonances for server hum
        for res_f in [120, 240, 360, 480]:
            idx = int(res_f * duration)
            if idx < len(mag):
                width = 5
                for w in range(-width, width+1):
                    curr_idx = idx + w
                    if 0 <= curr_idx < len(mag):
                        mag[curr_idx] += 2.0 / (1 + abs(w))

        phase_L = np.random.uniform(0, 2*np.pi, len(freqs))
        phase_R = np.random.uniform(0, 2*np.pi, len(freqs))

        spec_L = mag * np.exp(1j * phase_L)
        spec_R = mag * np.exp(1j * phase_R)

        left = np.fft.irfft(spec_L, n=N)
        right = np.fft.irfft(spec_R, n=N)

        left = (left / (np.max(np.abs(left)) + 1e-6) * 0.5).astype(np.float32)
        right = (right / (np.max(np.abs(right)) + 1e-6) * 0.5).astype(np.float32)

        return np.column_stack((left, right))

    @staticmethod
    def ethereal_sub_pad(duration=6.0, chord="minor9"):
        """
        Warm lush evolving analog synth pad.
        """
        sr = AmbientDroneSuite.SAMPLE_RATE
        N = int(sr * duration)
        t = np.linspace(0, duration, N, endpoint=False)
        base_hz = 1.0 / duration

        chord_map = {
            "minor9": [65.41, 77.78, 98.00, 116.54, 146.83],
            "major9": [65.41, 82.41, 98.00, 123.47, 146.83],
            "sus4": [65.41, 87.31, 98.00, 130.81],
        }
        notes = chord_map.get(chord, chord_map["minor9"])

        left = np.zeros(N)
        right = np.zeros(N)

        for idx, freq in enumerate(notes):
            f_rounded = round(freq / base_hz) * base_hz
            f_sub = round((freq / 2.0) / base_hz) * base_hz

            lfo_rate = round((0.1 + idx * 0.05) / base_hz) * base_hz
            if lfo_rate == 0:
                lfo_rate = base_hz

            lfo = 0.6 + 0.4 * np.sin(2 * np.pi * lfo_rate * t)

            wave_L = np.sin(2 * np.pi * f_rounded * t) + 0.3 * np.sin(2 * np.pi * f_rounded * 2 * t)
            wave_R = np.sin(2 * np.pi * f_rounded * t + 0.1) + 0.3 * np.sin(2 * np.pi * f_rounded * 2 * t + 0.2)

            wave_L += 0.5 * np.sin(2 * np.pi * f_sub * t)
            wave_R += 0.5 * np.sin(2 * np.pi * f_sub * t + 0.1)

            left += wave_L * lfo
            right += wave_R * lfo

        left = (left / (np.max(np.abs(left)) + 1e-6) * 0.6).astype(np.float32)
        right = (right / (np.max(np.abs(right)) + 1e-6) * 0.6).astype(np.float32)

        return np.column_stack((left, right))

    @staticmethod
    def sci_fi_deep_space_drone(duration: float = 10.0, root_freq: float = 55.0) -> np.ndarray:
        """
        Atmospheric multi-oscillator evolving deep space drone with slow stereo phase movement.
        """
        return AmbientDroneSuite.dark_scifi_drone(duration=duration, root_freq=root_freq)

