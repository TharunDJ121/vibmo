import numpy as np

class ImpactSubSuite:
    """
    Procedural Sub-Bass Impact & Hit sound generator suite.
    Produces 48kHz float32 NumPy audio arrays.
    """

    SR = 48000
    SAMPLE_RATE = 48000

    @staticmethod
    def _generate_time_array(duration):
        return np.linspace(0, duration, int(duration * ImpactSubSuite.SR), endpoint=False)

    @staticmethod
    def _apply_envelope(audio, attack_time, release_time):
        t = np.linspace(0, len(audio) / ImpactSubSuite.SR, len(audio), endpoint=False)
        envelope = np.ones_like(t)

        attack_samples = int(attack_time * ImpactSubSuite.SR)
        release_samples = int(release_time * ImpactSubSuite.SR)

        if attack_samples > 0:
            attack_samples = min(attack_samples, len(audio))
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)

        if release_samples > 0:
            release_samples = min(release_samples, len(audio) - attack_samples)
            if release_samples > 0:
                # Exponential decay for release
                decay_env = np.exp(-np.linspace(0, 5, release_samples))
                envelope[-release_samples:] = decay_env

                # Zero out any remaining samples if attack+release < len (usually doesn't happen with our logic, but just in case)
                if attack_samples + release_samples < len(audio):
                     mid_samples = len(audio) - attack_samples - release_samples
                     envelope[attack_samples:attack_samples+mid_samples] = 1.0

        return audio * envelope

    @staticmethod
    def cinematic_808_drop(duration=1.2, start_freq=160.0, end_freq=32.0, saturation=1.4):
        """Heavy saturated 808 sub-bass drop with exponential pitch decay."""
        t = ImpactSubSuite._generate_time_array(duration)

        # Exponential pitch decay
        # f(t) = start_freq * (end_freq / start_freq) ^ (t / duration)
        freq_env = start_freq * np.power((end_freq / start_freq), (t / duration))

        # To get the phase, we integrate the frequency
        # integral of a^t dt = a^t / ln(a)
        # So phase = 2 * pi * integral of freq_env
        a = (end_freq / start_freq) ** (1 / duration)
        if a != 1:
            phase = 2 * np.pi * start_freq * (np.power(a, t) - 1) / np.log(a)
        else:
            phase = 2 * np.pi * start_freq * t

        audio = np.sin(phase)

        # Apply saturation (soft clipping)
        audio = np.tanh(audio * saturation)
        # Normalize post-saturation slightly to keep within [-1, 1] safely
        audio /= np.max(np.abs(audio)) + 1e-6

        # Amplitude envelope (fast attack, long exponential release)
        attack_samples = int(0.01 * ImpactSubSuite.SR)
        release_samples = len(audio) - attack_samples
        envelope = np.ones_like(t)
        if attack_samples > 0:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        if release_samples > 0:
            envelope[attack_samples:] = np.exp(-np.linspace(0, 4, release_samples))

        audio *= envelope
        return audio.astype(np.float32)

    @staticmethod
    def punch_thud_impact(duration=0.45, attack_click=True):
        """Tight punchy acoustic impact with transient click and low-mid resonance."""
        t = ImpactSubSuite._generate_time_array(duration)
        audio = np.zeros_like(t)

        # Low-mid resonance (pitch drop from ~150Hz to ~50Hz)
        start_freq = 150.0
        end_freq = 50.0
        # fast pitch drop in first 0.1s
        freq_env = np.where(t < 0.1,
                            start_freq - (start_freq - end_freq) * (t / 0.1),
                            end_freq)

        # Integrate frequency to get phase (numerical integration)
        phase = 2 * np.pi * np.cumsum(freq_env) / ImpactSubSuite.SR

        resonance = np.sin(phase)

        # Quick decay for resonance
        res_env = np.exp(-t * 15) # fast decay
        resonance *= res_env
        audio += resonance * 0.8

        if attack_click:
            # Short transient noise/click
            click_len = int(0.015 * ImpactSubSuite.SR) # 15ms click
            if click_len > len(t):
                click_len = len(t)
            click = np.random.normal(0, 1, click_len)

            # Apply lowpass-ish filter by smoothing, or just leave as broadband click
            # Decay the click very fast
            click_env = np.exp(-np.linspace(0, 10, click_len))
            click *= click_env

            audio[:click_len] += click * 0.5

        # Overall envelope to prevent clicking at ends
        audio = ImpactSubSuite._apply_envelope(audio, attack_time=0.001, release_time=duration-0.001)

        # Normalize and clip to be safe
        audio = np.clip(audio, -1.0, 1.0)

        return audio.astype(np.float32)

    @staticmethod
    def metallic_anvil_hit(duration=0.9, ring_freq=880.0):
        """Metallic cinematic hit with harmonic bell-like ring resonance."""
        t = ImpactSubSuite._generate_time_array(duration)
        audio = np.zeros_like(t)

        # Impact transient (noise burst)
        transient_len = int(0.05 * ImpactSubSuite.SR)
        if transient_len > len(t): transient_len = len(t)
        noise = np.random.normal(0, 1, transient_len)
        noise_env = np.exp(-np.linspace(0, 5, transient_len))
        audio[:transient_len] += noise * noise_env * 0.4

        # Bell-like inharmonic partials
        # Common bell partial ratios: 1, 1.18, 1.56, 2, 2.51, 3.56
        ratios = [1.0, 1.18, 1.56, 2.0, 2.51, 3.56]
        amplitudes = [1.0, 0.8, 0.6, 0.5, 0.4, 0.2]
        decays = [3.0, 4.0, 5.0, 6.0, 7.0, 8.0] # Higher partials decay faster

        for ratio, amp, decay in zip(ratios, amplitudes, decays):
            freq = ring_freq * ratio
            if freq < ImpactSubSuite.SR / 2: # Anti-aliasing
                partial = np.sin(2 * np.pi * freq * t)
                env = np.exp(-t * decay)
                audio += partial * amp * env * 0.3

        # Normalize
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            audio /= max_val

        # Overall envelope
        audio = ImpactSubSuite._apply_envelope(audio, attack_time=0.001, release_time=duration*0.5)

        return audio.astype(np.float32)

    @staticmethod
    def card_slam_impact(duration=0.35):
        """Solid organic UI card impact on virtual canvas."""
        t = ImpactSubSuite._generate_time_array(duration)
        audio = np.zeros_like(t)

        # Thud component (low frequency fast drop)
        thud_freq = np.linspace(120, 40, len(t))
        thud_phase = 2 * np.pi * np.cumsum(thud_freq) / ImpactSubSuite.SR
        thud = np.sin(thud_phase)
        thud_env = np.exp(-t * 20)
        audio += thud * thud_env * 0.7

        # Slap component (filtered noise)
        noise_len = int(0.04 * ImpactSubSuite.SR)
        if noise_len > len(t): noise_len = len(t)
        noise = np.random.normal(0, 1, noise_len)
        noise_env = np.exp(-np.linspace(0, 10, noise_len))
        audio[:noise_len] += noise * noise_env * 0.3

        # Overall envelope
        audio = ImpactSubSuite._apply_envelope(audio, attack_time=0.002, release_time=duration*0.8)

        # Normalize safely
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            audio /= (max_val + 1e-6)

        # Keep slightly under 0 dBFS to sound like a UI sound
        audio *= 0.8

        return audio.astype(np.float32)

    @staticmethod
    def cinematic_trailer_sub_drop(decay: float = 2.0, duration: float = None) -> np.ndarray:
        """Massive cinematic trailer sub-bass drop with exponential pitch decay and saturation."""
        dur = duration if duration is not None else decay
        return ImpactSubSuite.cinematic_808_drop(duration=dur, start_freq=180.0, end_freq=28.0, saturation=1.6)

