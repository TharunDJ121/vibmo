import numpy as np

class Retro8BitSuite:
    """
    Authentic 8-Bit Chiptune sound generator suite producing 48kHz float32 NumPy arrays.
    Simulates NES-style pulse (12.5%, 25%, 50% duty), triangle, and 1-bit LFSR noise channels.
    """
    SR = 48000
    SAMPLE_RATE = 48000

    @staticmethod
    def _pulse_wave(freqs: np.ndarray, duty: float = 0.5) -> np.ndarray:
        phase = np.cumsum(freqs) / Retro8BitSuite.SR
        return np.where(np.mod(phase, 1.0) < duty, 1.0, -1.0).astype(np.float32)

    @staticmethod
    def _triangle_wave(freqs: np.ndarray) -> np.ndarray:
        phase = np.cumsum(freqs) / Retro8BitSuite.SR
        tri = 4.0 * np.abs(np.mod(phase, 1.0) - 0.5) - 1.0
        # Simulating 4-bit triangle wave resolution common in 8-bit systems
        tri = np.floor((tri + 1.0) * 7.5) / 7.5 - 1.0
        return tri.astype(np.float32)

    @staticmethod
    def _noise(duration: float, mode: int = 0, shift_interval: int = 4) -> np.ndarray:
        num_samples = int(Retro8BitSuite.SR * duration)
        # NES noise LFSR: 32767 for mode 0, 93 for mode 1 (metallic)
        lfsr_len = 32767 if mode == 0 else 93
        seq = np.zeros(lfsr_len, dtype=np.float32)
        reg = 1
        for i in range(lfsr_len):
            bit = (reg & 1) ^ ((reg >> (6 if mode == 1 else 1)) & 1)
            reg = (reg >> 1) | (bit << 14)
            seq[i] = 1.0 if (reg & 1) else -1.0
        indices = (np.arange(num_samples) // shift_interval) % lfsr_len
        return seq[indices]

    @staticmethod
    def jump_boing(duration: float = 0.20, f_start: float = 150.0, f_end: float = 600.0) -> np.ndarray:
        """8-bit Mario-style jump sweep."""
        num_samples = int(Retro8BitSuite.SR * duration)
        freqs = np.linspace(f_start, f_end, num_samples)
        wave = Retro8BitSuite._pulse_wave(freqs, duty=0.5)
        # Quick fade out to avoid pop
        env = np.linspace(1.0, 0.0, num_samples)
        return (wave * env).astype(np.float32)

    @staticmethod
    def coin_pickup(duration: float = 0.30) -> np.ndarray:
        """Two-tone rapid arpeggio (B5 -> E6) pulse wave coin collect."""
        num_samples = int(Retro8BitSuite.SR * duration)
        # B5 = ~987.77 Hz, E6 = ~1318.51 Hz
        t_switch = int(0.3 * num_samples) # Switch to higher note at 30% mark
        freqs = np.empty(num_samples, dtype=np.float32)
        freqs[:t_switch] = 987.77
        freqs[t_switch:] = 1318.51
        wave = Retro8BitSuite._pulse_wave(freqs, duty=0.5)

        env = np.ones(num_samples, dtype=np.float32)
        fade_len = int(0.05 * Retro8BitSuite.SR)
        env[-fade_len:] = np.linspace(1.0, 0.0, fade_len)
        return (wave * env).astype(np.float32)

    @staticmethod
    def power_down_slide(duration: float = 0.45) -> np.ndarray:
        """Descending chromatic death/failure slide."""
        num_samples = int(Retro8BitSuite.SR * duration)
        # E5 (~659.25Hz) sliding down 12 semitones chromatically
        steps = np.linspace(0, -12, num_samples)
        freqs = 659.25 * (2 ** (np.floor(steps) / 12.0))

        # Mix 25% duty pulse, triangle, and some noise
        wave1 = Retro8BitSuite._pulse_wave(freqs, duty=0.25)
        wave2 = Retro8BitSuite._triangle_wave(freqs)
        noise = Retro8BitSuite._noise(duration, mode=0, shift_interval=8)

        wave = (0.4 * wave1 + 0.4 * wave2 + 0.2 * noise).astype(np.float32)
        env = np.linspace(1.0, 0.0, num_samples)
        return (wave * env).astype(np.float32)

    @staticmethod
    def level_up_fanfare(duration: float = 0.8) -> np.ndarray:
        """4-note victory flourish with square wave harmonics."""
        num_samples = int(Retro8BitSuite.SR * duration)
        # G4, C5, E5, G5
        notes = [392.00, 523.25, 659.25, 783.99]
        n1 = int(0.15 * Retro8BitSuite.SR)
        n2 = int(0.30 * Retro8BitSuite.SR)
        n3 = int(0.45 * Retro8BitSuite.SR)

        freqs = np.zeros(num_samples, dtype=np.float32)
        freqs[:n1] = notes[0]
        freqs[n1:n2] = notes[1]
        freqs[n2:n3] = notes[2]
        freqs[n3:] = notes[3]

        # Lead square wave and lower octave 12.5% pulse
        sq1 = Retro8BitSuite._pulse_wave(freqs, duty=0.5)
        sq2 = Retro8BitSuite._pulse_wave(freqs / 2.0, duty=0.125)

        # Metallic noise bursts on note changes
        noise = Retro8BitSuite._noise(duration, mode=1, shift_interval=16)
        noise_env = np.zeros(num_samples, dtype=np.float32)
        for start in [0, n1, n2, n3]:
            end = min(start + int(0.05 * Retro8BitSuite.SR), num_samples)
            noise_env[start:end] = np.linspace(0.5, 0.0, end - start)

        wave = np.clip(0.5 * sq1 + 0.3 * sq2 + noise * noise_env, -1.0, 1.0).astype(np.float32)

        env = np.ones(num_samples, dtype=np.float32)
        fade_len = int(0.1 * Retro8BitSuite.SR)
        env[-fade_len:] = np.linspace(1.0, 0.0, fade_len)
        return (wave * env).astype(np.float32)

    @staticmethod
    def arcade_coin_jump(duration: float = 0.30) -> np.ndarray:
        """Classic arcade coin pickup sound with ascending pulse arpeggio."""
        return Retro8BitSuite.coin_pickup(duration=duration)

# Canonical AGENTS.md alias
Retro8bitSuite = Retro8BitSuite

