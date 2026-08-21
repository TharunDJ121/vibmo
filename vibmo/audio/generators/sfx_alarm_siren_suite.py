import numpy as np
import math

class AlarmSirenSuite:
    """Procedural Emergency Alarm & Siren sound generator suite."""

    SAMPLE_RATE = 48000

    @staticmethod
    def emergency_klaxon_sweep(duration: float = 1.5, f_low: float = 350.0, f_high: float = 950.0) -> np.ndarray:
        """Industrial warning klaxon horn with triangle frequency modulation."""
        t = np.linspace(0, duration, int(AlarmSirenSuite.SAMPLE_RATE * duration), endpoint=False)
        # Triangle modulation wave (sweep up and down)
        # Let's say 2 sweeps per second
        mod_freq = 2.0
        triangle_mod = np.abs((t * mod_freq * 2) % 2 - 1)
        freq = f_low + (f_high - f_low) * triangle_mod
        phase = np.cumsum(freq) * 2 * np.pi / AlarmSirenSuite.SAMPLE_RATE

        # Klaxon usually has rich harmonics (sawtooth/square mix)
        audio = 0.6 * np.sign(np.sin(phase)) + 0.4 * (2 * (phase / (2 * np.pi) - np.floor(phase / (2 * np.pi) + 0.5)))

        # Envelope to avoid clicks
        env = np.ones_like(t)
        fade = int(0.05 * AlarmSirenSuite.SAMPLE_RATE)
        env[:fade] = np.linspace(0, 1, fade)
        env[-fade:] = np.linspace(1, 0, fade)

        return (audio * env).astype(np.float32)

    @staticmethod
    def nuclear_countdown_beep(duration: float = 0.25, freq: float = 1400.0) -> np.ndarray:
        """Urgent electronic security countdown beep with square sub-harmonic."""
        t = np.linspace(0, duration, int(AlarmSirenSuite.SAMPLE_RATE * duration), endpoint=False)
        phase_main = 2 * np.pi * freq * t
        phase_sub = 2 * np.pi * (freq / 2) * t

        audio = 0.7 * np.sin(phase_main) + 0.3 * np.sign(np.sin(phase_sub))

        env = np.ones_like(t)
        fade_in = int(0.01 * AlarmSirenSuite.SAMPLE_RATE)
        fade_out = int(0.05 * AlarmSirenSuite.SAMPLE_RATE)
        env[:fade_in] = np.linspace(0, 1, fade_in)
        env[-fade_out:] = np.linspace(1, 0, fade_out)

        return (audio * env).astype(np.float32)

    @staticmethod
    def security_chirp_alarm(duration: float = 0.8, pulses: int = 4) -> np.ndarray:
        """Fast multi-burst car security chirp sequence."""
        t = np.linspace(0, duration, int(AlarmSirenSuite.SAMPLE_RATE * duration), endpoint=False)

        pulse_duration = duration / pulses
        pulse_t = t % pulse_duration

        # Quick sweep from high to low for each chirp
        freq = 3000.0 - (2000.0 * (pulse_t / pulse_duration))
        phase = np.cumsum(freq) * 2 * np.pi / AlarmSirenSuite.SAMPLE_RATE

        audio = np.sin(phase)

        # Envelope for each pulse
        env = np.zeros_like(t)
        pulse_fade_in = int(0.01 * AlarmSirenSuite.SAMPLE_RATE)
        pulse_fade_out = int(0.02 * AlarmSirenSuite.SAMPLE_RATE)

        for i in range(pulses):
            start_idx = int(i * pulse_duration * AlarmSirenSuite.SAMPLE_RATE)
            end_idx = int((i + 1) * pulse_duration * AlarmSirenSuite.SAMPLE_RATE)

            p_len = end_idx - start_idx
            p_env = np.ones(p_len)
            p_env[:pulse_fade_in] = np.linspace(0, 1, pulse_fade_in)

            # Make sure fade out isn't larger than pulse length
            act_fade_out = min(pulse_fade_out, p_len)
            p_env[-act_fade_out:] = np.linspace(1, 0, act_fade_out)

            env[start_idx:end_idx] = p_env

        return (audio * env).astype(np.float32)

    @staticmethod
    def biohazard_pulse_siren(duration: float = 2.0) -> np.ndarray:
        """Dystopian deep sci-fi biohazard strobe siren."""
        t = np.linspace(0, duration, int(AlarmSirenSuite.SAMPLE_RATE * duration), endpoint=False)

        # Slow underlying frequency modulation
        f_center = 400.0
        f_dev = 200.0
        lfo = np.sin(2 * np.pi * 0.5 * t)
        freq = f_center + f_dev * lfo
        phase = np.cumsum(freq) * 2 * np.pi / AlarmSirenSuite.SAMPLE_RATE

        # Deep square/saw mix
        audio = 0.5 * np.sign(np.sin(phase)) + 0.5 * (2 * (phase / (2 * np.pi) - np.floor(phase / (2 * np.pi) + 0.5)))

        # Strobe amplitude modulation (pulse)
        strobe = 0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 8 * t)) # 8Hz strobe
        audio *= strobe

        env = np.ones_like(t)
        fade = int(0.1 * AlarmSirenSuite.SAMPLE_RATE)
        env[:fade] = np.linspace(0, 1, fade)
        env[-fade:] = np.linspace(1, 0, fade)

        return (audio * env).astype(np.float32)
