import numpy as np
from scipy import signal

class RiserTensionSuite:
    """
    An illusionary Shepard Tone & Tension Pitch Riser generator suite.
    Generates 48kHz float32 NumPy audio arrays.
    """

    @staticmethod
    def shepard_tone_riser(duration: float = 2.5, base_freq: float = 65.4, octaves: int = 5) -> np.ndarray:
        """
        Infinitely ascending Shepard-Risset glissando illusion.
        """
        sample_rate = 48000
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        audio = np.zeros_like(t)

        for i in range(octaves):
            # Frequency glides up one octave over the duration
            f_start = base_freq * (2 ** i)
            f_end = base_freq * (2 ** (i + 1))

            # Exponential frequency sweep
            # The phase integral of f(t) = f0 * 2^(t/T) is f0 * T / ln(2) * (2^(t/T) - 1)
            # Actually, standard Shepard-Risset glissando is an exponential sweep
            # phase = 2 * pi * \int f(t) dt
            # Let f(t) = f_start * (f_end/f_start)**(t/duration) = f_start * 2**(t/duration)
            # phase = 2 * np.pi * f_start * duration / np.log(2) * (2**(t/duration) - 1)

            phase = 2 * np.pi * f_start * duration / np.log(2) * (2**(t/duration) - 1)

            # Amplitude envelope: bell shape over the whole Shepard tone range.
            # To create the illusion, the lower octaves fade in and higher fade out.
            # Risset bell: 1 - cos(2*pi * (t/duration + i) / octaves) or similar.
            # Wait, the true Shepard-Risset glissando loops smoothly.
            # Normalized position of this partial goes from i/octaves to (i+1)/octaves
            pos = (i + t/duration) / octaves

            # Amplitude envelope, peaks at center of the octaves range
            amp = np.sin(np.pi * pos)**2

            audio += amp * np.sin(phase)

        # Normalize
        if np.max(np.abs(audio)) > 0:
            audio /= np.max(np.abs(audio))

        return audio.astype(np.float32)

    @staticmethod
    def cyber_pitch_riser(duration: float = 1.8, start_f: float = 100.0, end_f: float = 3500.0, lfo_rate: float = 8.0) -> np.ndarray:
        """
        Modulated cyber synth pitch sweep with accelerating LFO vibrato.
        """
        sample_rate = 48000
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

        # Base exponential frequency sweep
        # f_base(t) = start_f * (end_f / start_f)**(t / duration)

        # Accelerating LFO rate
        # lfo_rate(t) = lfo_rate * (1 + 2 * t / duration) # starts at lfo_rate, ends at 3*lfo_rate
        # phase_lfo = \int lfo_rate(t) dt = lfo_rate * (t + t**2 / duration)
        phase_lfo = 2 * np.pi * lfo_rate * (t + (t**2) / duration)

        # LFO modulates frequency. Let's make it modulate pitch.
        # depth = 0.05 octaves initially, maybe increasing.
        lfo = 0.05 * np.sin(phase_lfo)

        # f(t) = start_f * (end_f / start_f)**(t / duration) * 2**lfo
        # Actually easier: just integrate f(t) directly.
        # But for an LFO, it's easier to just compute instantaneous frequency and then cumsum (integrate).

        inst_f = start_f * (end_f / start_f)**(t / duration) * (2 ** lfo)
        phase = 2 * np.pi * np.cumsum(inst_f) / sample_rate

        # Sawtooth wave for a "cyber" synth sound
        # using np.mod or scipy.signal.sawtooth
        audio = signal.sawtooth(phase)

        # Add a lowpass filter that opens up
        # We can implement a simple time-varying lowpass filter, or just shape the sound.
        # Since we just need the audio array, let's keep it simple: apply a fade in/out.
        env = np.ones_like(t)
        fade_samples = int(0.05 * sample_rate)
        if fade_samples > 0:
            env[:fade_samples] = np.linspace(0, 1, fade_samples)
            env[-fade_samples:] = np.linspace(1, 0, fade_samples)

        audio = audio * env

        # Normalize
        if np.max(np.abs(audio)) > 0:
            audio /= np.max(np.abs(audio))

        return audio.astype(np.float32)

    @staticmethod
    def white_noise_sweep(duration: float = 1.5, resonance: float = 4.0) -> np.ndarray:
        """
        Resonant band-pass filtered white noise sweep from 200Hz to 12kHz.
        """
        sample_rate = 48000
        n_samples = int(sample_rate * duration)
        t = np.linspace(0, duration, n_samples, endpoint=False)
        noise = np.random.uniform(-1.0, 1.0, n_samples)

        # Sweep from 200 to 12000 exponentially
        start_f = 200.0
        end_f = 12000.0
        center_freqs = start_f * (end_f / start_f)**(t / duration)

        # Implement a simple time-varying resonant filter.
        # A state variable filter is good for this.
        audio = np.zeros(n_samples)

        # SVF parameters
        # r = 1 / resonance. resonance is Q.
        # q = 1.0 / resonance

        # For an SVF, max freq is fs/6, but we can use a simpler approach or oversample.
        # Better yet, since it's Python and we want to avoid super slow loops if possible,
        # but 1.5s is 72k samples. A numba/cython approach is best, but here we only have numpy.
        # We can run a simple loop or use an IIR filter.
        # Since time-varying IIR in Python is slow, let's try a blocked approach or just write the loop.

        # Precompute coefficients
        # 2-pole resonant bandpass using state variable filter
        # f = 2 * sin(pi * Fc / Fs)
        # q = 1 / Q
        q = 1.0 / resonance
        f = 2.0 * np.sin(np.pi * center_freqs / sample_rate)

        hp = 0.0
        bp = 0.0
        lp = 0.0

        # Use a simple python loop, 72k iterations should take ~10-20ms, it's fine.
        for i in range(n_samples):
            # To avoid instability at high freqs, we can use 2x oversampling or clip f
            f_i = min(f[i], 1.0)
            hp = noise[i] - lp - q * bp
            bp += f_i * hp
            lp += f_i * bp
            audio[i] = bp

        # Add envelope
        env = np.ones_like(t)
        fade_samples = int(0.05 * sample_rate)
        if fade_samples > 0:
            env[:fade_samples] = np.linspace(0, 1, fade_samples)
            env[-fade_samples:] = np.linspace(1, 0, fade_samples)

        audio = audio * env

        # Normalize
        if np.max(np.abs(audio)) > 0:
            audio /= np.max(np.abs(audio))

        return audio.astype(np.float32)

    @staticmethod
    def tension_alarm_build(duration: float = 2.0, pulses: int = 8) -> np.ndarray:
        """
        Accelerating pulsing alarm siren riser leading up to a beat drop.
        """
        sample_rate = 48000
        n_samples = int(sample_rate * duration)
        t = np.linspace(0, duration, n_samples, endpoint=False)

        # Base pitch rises
        start_f = 400.0
        end_f = 1200.0
        base_f = start_f * (end_f / start_f)**(t / duration)

        # The siren wails up and down.
        # Siren LFO accelerates.
        # Let's say we want 'pulses' wails.
        # To make it accelerate, the frequency of the wail LFO increases.
        # phase_wail = \int wail_rate(t) dt
        # Let wail_rate(t) = a * t + b
        # We want the total phase to be pulses * 2 * pi over 'duration'
        # Let's make it linearly accelerating: wail_rate(0) = r0, wail_rate(duration) = r1
        # r1 = 3 * r0 for example.
        # total_wails = (r0 + r1)/2 * duration = pulses
        # 2 * r0 * duration = pulses => r0 = pulses / (2 * duration)
        # r1 = 3 * pulses / (2 * duration)

        r0 = pulses / (2 * duration)
        wail_rate = r0 + (3 * r0 - r0) * (t / duration)
        phase_wail = 2 * np.pi * np.cumsum(wail_rate) / sample_rate

        # Siren modulates pitch by e.g. a minor third (1.2 ratio)
        wail_mod = 1.0 + 0.2 * np.sin(phase_wail)

        inst_f = base_f * wail_mod
        phase = 2 * np.pi * np.cumsum(inst_f) / sample_rate

        # Use a square wave or distorted sine for alarm
        audio = np.sign(np.sin(phase)) * 0.5 + 0.5 * np.sin(phase)

        # Add pulsing amplitude envelope
        # Sharp cuts for alarm effect, accelerating
        # We can use the wail phase for this, when wail is high, volume is high
        amp_mod = 0.5 + 0.5 * np.sin(phase_wail - np.pi/2) # Peak when wail is highest
        audio = audio * amp_mod

        # Add a high-pass filter to make it sound "thin/alarm-like"
        # Since we don't have an easy HPF without scipy.signal, let's just use scipy.signal.butter
        b, a = signal.butter(2, 200.0 / (sample_rate / 2), btype='high')
        audio = signal.lfilter(b, a, audio)

        # Fade out slightly at the very end
        fade_samples = int(0.05 * sample_rate)
        env = np.ones_like(t)
        if fade_samples > 0:
            env[:fade_samples] = np.linspace(0, 1, fade_samples)
            env[-fade_samples:] = np.linspace(1, 0, fade_samples)
        audio = audio * env

        # Normalize
        if np.max(np.abs(audio)) > 0:
            audio /= np.max(np.abs(audio))

        return audio.astype(np.float32)
