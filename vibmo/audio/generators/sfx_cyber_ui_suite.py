import numpy as np
from typing import List, Optional

SAMPLE_RATE = 48000

class CyberUISFXSuite:
    """
    Procedural Cyberpunk Holographic UI sound generator suite.
    Produces 48kHz float32 NumPy audio arrays normalized to [-1.0, 1.0].
    """

    @staticmethod
    def holo_chirp(duration: float = 0.08, freq_start: float = 1800.0, freq_end: float = 3200.0) -> np.ndarray:
        """Dual-frequency resonant FM chirp for button hover/touch."""
        if duration <= 0:
            return np.array([], dtype=np.float32)

        t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)

        # Base chirp
        phase = 2 * np.pi * (freq_start * t + (freq_end - freq_start) / (2 * duration) * t**2)
        wave1 = np.sin(phase)

        # Harmonic chirp
        freq_start_h = freq_start * 1.5
        freq_end_h = freq_end * 1.5
        phase_h = 2 * np.pi * (freq_start_h * t + (freq_end_h - freq_start_h) / (2 * duration) * t**2)
        wave2 = np.sin(phase_h)

        mixed = wave1 + 0.5 * wave2

        # Exponential decay envelope with quick attack
        env = np.exp(-t * 20)
        attack_len = int(0.01 * SAMPLE_RATE)
        if attack_len > 0 and len(env) > attack_len:
            env[:attack_len] = np.linspace(0, 1, attack_len)
        elif len(env) > 0:
            env[:] = np.linspace(0, 1, len(env))

        output = mixed * env

        # Normalize
        max_val = np.max(np.abs(output))
        if max_val > 0:
            output = output / max_val

        return output.astype(np.float32)

    @staticmethod
    def data_packet_burst(duration: float = 0.15, count: int = 6, freq: float = 2400.0) -> np.ndarray:
        """Rapid granular data stream burst."""
        if duration <= 0:
            return np.array([], dtype=np.float32)

        t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)

        # Carrier wave
        wave = np.sin(2 * np.pi * freq * t)

        # Burst modulation
        burst_rate = count / duration
        modulation = np.sin(2 * np.pi * burst_rate * t)
        modulation = np.where(modulation > 0, 1.0, 0.0)

        # Add white noise
        noise = np.random.normal(0, 0.2, len(t))

        output = (wave + noise) * modulation

        # Soft envelope to smooth the burst edges
        env = np.ones_like(t)
        attack_len = int(0.005 * SAMPLE_RATE)
        decay_len = int(0.01 * SAMPLE_RATE)
        if attack_len > 0 and len(env) > attack_len:
            env[:attack_len] = np.linspace(0, 1, attack_len)
        if decay_len > 0 and len(env) > decay_len:
            env[-decay_len:] = np.linspace(1, 0, decay_len)

        output = output * env

        # Normalize
        max_val = np.max(np.abs(output))
        if max_val > 0:
            output = output / max_val

        return output.astype(np.float32)

    @staticmethod
    def access_granted_tone(duration: float = 0.45, chord: Optional[List[float]] = None) -> np.ndarray:
        """Euphoric ascending harmonic major 7th chime."""
        if duration <= 0:
            return np.array([], dtype=np.float32)

        if chord is None:
            chord = [523.25, 659.25, 783.99, 1046.50]  # C5, E5, G5, C6

        t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
        output = np.zeros_like(t)

        delay = duration / (len(chord) + 2)

        for i, freq in enumerate(chord):
            start_time = i * delay
            start_idx = int(start_time * SAMPLE_RATE)
            if start_idx >= len(t):
                continue

            note_duration = duration - start_time
            note_t = np.linspace(0, note_duration, len(t) - start_idx, endpoint=False)

            # Simple FM synth for chime
            mod = np.sin(2 * np.pi * (freq * 2) * note_t)
            note = np.sin(2 * np.pi * freq * note_t + 1.0 * mod * np.exp(-note_t * 5))

            # Envelope
            env = np.exp(-note_t * 3)
            attack_len = min(int(0.02 * SAMPLE_RATE), len(env))
            if attack_len > 0:
                env_attack = np.linspace(0, 1, attack_len)
                env[:attack_len] = env_attack

            output[start_idx:] += note * env

        # Overall envelope
        overall_env = np.ones_like(t)
        decay_len = int(0.05 * SAMPLE_RATE)
        if decay_len > 0 and len(overall_env) > decay_len:
            overall_env[-decay_len:] = np.linspace(1, 0, decay_len)

        output = output * overall_env

        # Normalize
        max_val = np.max(np.abs(output))
        if max_val > 0:
            output = output / max_val

        return output.astype(np.float32)

    @staticmethod
    def access_denied_klaxon(duration: float = 0.35, freq: float = 180.0) -> np.ndarray:
        """Harsh saw-wave dual-tone warning buzzer with rapid envelope decay."""
        if duration <= 0:
            return np.array([], dtype=np.float32)

        t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)

        # Dual saw waves
        saw1 = 2 * (t * freq - np.floor(t * freq + 0.5))
        saw2 = 2 * (t * (freq * 1.05) - np.floor(t * (freq * 1.05) + 0.5))

        wave = saw1 + saw2

        # Klaxon modulation (rapid on/off)
        lfo = np.sin(2 * np.pi * 15 * t)
        env_lfo = np.where(lfo > 0, 1.0, 0.1)

        # Rapid overall decay
        env = np.exp(-t * 6)

        output = wave * env * env_lfo

        # Normalize
        max_val = np.max(np.abs(output))
        if max_val > 0:
            output = output / max_val

        return output.astype(np.float32)

    @staticmethod
    def cyber_pip(duration: float = 0.04, freq: float = 2200.0) -> np.ndarray:
        """Crisp micro-tap feedback."""
        if duration <= 0:
            return np.array([], dtype=np.float32)

        t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)

        wave = np.sin(2 * np.pi * freq * t)

        # Sharp transient envelope
        attack_time = min(0.002, duration * 0.1)
        attack_idx = int(attack_time * SAMPLE_RATE)

        env = np.zeros_like(t)
        if attack_idx > 0:
            env[:attack_idx] = np.linspace(0, 1, attack_idx)
        if len(t) > attack_idx:
            decay_time = duration - attack_time
            env[attack_idx:] = np.exp(-np.linspace(0, decay_time, len(t) - attack_idx) * 40)

        output = wave * env

        # Normalize
        max_val = np.max(np.abs(output))
        if max_val > 0:
            output = output / max_val

        return output.astype(np.float32)

# Standalone convenience functions
def holo_chirp(duration: float = 0.08, freq_start: float = 1800.0, freq_end: float = 3200.0) -> np.ndarray:
    return CyberUISFXSuite.holo_chirp(duration, freq_start, freq_end)

def data_packet_burst(duration: float = 0.15, count: int = 6, freq: float = 2400.0) -> np.ndarray:
    return CyberUISFXSuite.data_packet_burst(duration, count, freq)

def access_granted_tone(duration: float = 0.45, chord: Optional[List[float]] = None) -> np.ndarray:
    return CyberUISFXSuite.access_granted_tone(duration, chord)

def access_denied_klaxon(duration: float = 0.35, freq: float = 180.0) -> np.ndarray:
    return CyberUISFXSuite.access_denied_klaxon(duration, freq)

def cyber_pip(duration: float = 0.04, freq: float = 2200.0) -> np.ndarray:
    return CyberUISFXSuite.cyber_pip(duration, freq)
