import numpy as np

class CameraShutterSuite:
    """Procedural Camera Shutter & Mechanical Foley generator suite."""

    SR = 48000
    SAMPLE_RATE = 48000

    @staticmethod
    def _generate_noise(length):
        return np.random.uniform(-1, 1, length).astype(np.float32)

    @staticmethod
    def _apply_envelope(audio, attack, decay, sustain, release):
        length = len(audio)
        a_len = int(attack * length)
        d_len = int(decay * length)
        r_len = int(release * length)
        s_len = length - a_len - d_len - r_len

        env = np.concatenate([
            np.linspace(0, 1, a_len),
            np.linspace(1, sustain, d_len),
            np.full(max(0, s_len), sustain),
            np.linspace(sustain, 0, r_len)
        ])

        # Ensure envelope length matches audio length (can be slightly off due to float casting/rounding)
        if len(env) < length:
             env = np.concatenate([env, np.zeros(length - len(env))])
        elif len(env) > length:
             env = env[:length]

        return (audio * env).astype(np.float32)

    @staticmethod
    def dslr_mirror_slap(duration=0.16):
        """Professional DSLR reflex mirror flip-up and mechanical curtain snap."""
        length = int(CameraShutterSuite.SR * duration)
        t = np.linspace(0, duration, length, False)

        # Mirror slap (low transient)
        f_mirror = 150
        mirror_slap = np.sin(2 * np.pi * f_mirror * t) * np.exp(-30 * t)

        # Curtain snap (high transient snap)
        noise = CameraShutterSuite._generate_noise(length)
        curtain_snap = noise * np.exp(-80 * t)

        audio = (mirror_slap * 0.6 + curtain_snap * 0.4)

        # Envelope to prevent clicks
        audio = CameraShutterSuite._apply_envelope(audio, 0.01, 0.1, 0.0, 0.01)

        return np.clip(audio, -1.0, 1.0).astype(np.float32)

    @staticmethod
    def vintage_motor_advance(duration=0.65):
        """1980s 35mm camera motorized film winding motor buzz."""
        length = int(CameraShutterSuite.SR * duration)
        t = np.linspace(0, duration, length, False)

        # Motor buzz (sawtooth-like buzz, sweeping slightly)
        f_motor = np.linspace(300, 350, length)
        phase = np.cumsum(f_motor) / CameraShutterSuite.SR
        motor_buzz = 0.5 * (2 * (phase - np.floor(0.5 + phase)))  # Sawtooth wave

        # Gear friction (noise)
        noise = CameraShutterSuite._generate_noise(length)
        gear_friction = noise * 0.2

        audio = motor_buzz + gear_friction

        # Envelope
        audio = CameraShutterSuite._apply_envelope(audio, 0.05, 0.2, 0.6, 0.1)

        return np.clip(audio, -1.0, 1.0).astype(np.float32)

    @staticmethod
    def smartphone_snap_flash(duration=0.12):
        """Crisp synthetic digital camera shutter snapshot."""
        length = int(CameraShutterSuite.SR * duration)
        t = np.linspace(0, duration, length, False)

        # Synthetic chirp
        f_start, f_end = 2000, 500
        f_t = np.linspace(f_start, f_end, length)
        phase = np.cumsum(f_t) / CameraShutterSuite.SR
        chirp = np.sin(2 * np.pi * phase) * np.exp(-40 * t)

        # Digital click
        noise = CameraShutterSuite._generate_noise(length)
        click = noise * np.exp(-100 * t)

        audio = chirp * 0.5 + click * 0.5

        # Envelope
        audio = CameraShutterSuite._apply_envelope(audio, 0.02, 0.1, 0.0, 0.02)

        return np.clip(audio, -1.0, 1.0).astype(np.float32)

    @staticmethod
    def polaroid_eject(duration=0.85):
        """Instant camera motorized print ejection whir and gear friction."""
        length = int(CameraShutterSuite.SR * duration)
        t = np.linspace(0, duration, length, False)

        # Motor whir
        f_whir = 400 + 50 * np.sin(2 * np.pi * 5 * t) # Modulated frequency
        phase = np.cumsum(f_whir) / CameraShutterSuite.SR
        whir = np.sin(2 * np.pi * phase)

        # Gear grinding / friction
        noise = CameraShutterSuite._generate_noise(length)
        grind = noise * (0.3 + 0.1 * np.sin(2 * np.pi * 10 * t))

        audio = whir * 0.4 + grind * 0.6

        # Envelope
        audio = CameraShutterSuite._apply_envelope(audio, 0.1, 0.2, 0.7, 0.2)

        return np.clip(audio, -1.0, 1.0).astype(np.float32)

    @staticmethod
    def dslr_rapid_burst(duration: float = 0.6, shots: int = 3) -> np.ndarray:
        """Rapid DSLR continuous burst mode multi-shot shutter snap sequence."""
        sr = CameraShutterSuite.SR
        length = int(sr * duration)
        master = np.zeros(length, dtype=np.float32)

        shot_interval = duration / max(1, shots)
        for i in range(shots):
            start_time = i * shot_interval
            start_idx = int(start_time * sr)
            shot_audio = CameraShutterSuite.dslr_mirror_slap(duration=min(0.16, shot_interval))
            end_idx = min(start_idx + len(shot_audio), length)
            act_len = end_idx - start_idx
            if act_len > 0:
                master[start_idx:end_idx] += shot_audio[:act_len]

        max_val = np.max(np.abs(master))
        if max_val > 0:
            master = master / max_val

        return master.astype(np.float32)

