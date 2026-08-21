import numpy as np

class LaserPlasmaSuite:
    SAMPLE_RATE = 48000

    @staticmethod
    def arcade_laser_zap(duration=0.18, f_start=3000.0, f_end=150.0):
        t = np.linspace(0, duration, int(LaserPlasmaSuite.SAMPLE_RATE * duration), endpoint=False)

        # Exponential frequency decay
        # f(t) = f_start * (f_end / f_start) ** (t / duration)
        # Phase phi(t) = integral of 2 * pi * f(t) dt
        # phi(t) = 2 * pi * f_start * duration / ln(f_end / f_start) * ((f_end / f_start) ** (t / duration) - 1)

        c = np.log(f_end / f_start)
        if abs(c) < 1e-6:
            phi = 2 * np.pi * f_start * t
        else:
            phi = 2 * np.pi * f_start * duration / c * (np.exp(c * t / duration) - 1)

        # Generate sawtooth wave for retro feel, or square/pulse
        wave = np.sin(phi)
        # add some clipping for square/saw feel
        wave = np.clip(wave * 2.0, -1.0, 1.0)

        # Envelope: fast attack, exponential decay
        env = np.exp(-5.0 * t / duration)

        # Fade out to avoid clicks
        fade_samples = int(0.01 * LaserPlasmaSuite.SAMPLE_RATE)
        if fade_samples > 0 and fade_samples < len(env):
            env[-fade_samples:] *= np.linspace(1, 0, fade_samples)

        return (wave * env).astype(np.float32)

    @staticmethod
    def plasma_pulse_blast(duration=0.32):
        t = np.linspace(0, duration, int(LaserPlasmaSuite.SAMPLE_RATE * duration), endpoint=False)

        # Base blast: low frequency swept pulse
        f_start = 800.0
        f_end = 100.0
        c = np.log(f_end / f_start)
        phi_blast = 2 * np.pi * f_start * duration / c * (np.exp(c * t / duration) - 1)
        blast = np.sin(phi_blast)
        blast = np.sign(blast) * (1 - np.exp(-abs(blast)*4)) # saturate

        # Sizzle: white noise bandpass filtered or modulated
        noise = np.random.uniform(-1, 1, len(t))
        sizzle_env = np.exp(-8.0 * t / duration)
        sizzle = noise * sizzle_env

        # Resonant sci-fi ring
        ring_freq = 1200.0 * np.exp(-2.0 * t / duration)
        ring_phi = 2 * np.pi * np.cumsum(ring_freq) / LaserPlasmaSuite.SAMPLE_RATE
        ring = np.sin(ring_phi)
        ring_env = np.exp(-6.0 * t / duration) * np.sin(np.pi * t / duration)

        mix = (blast * 0.5 + sizzle * 0.3 + ring * ring_env * 0.4)

        # Master envelope
        env = np.exp(-3.0 * t / duration)
        # Fade out
        fade_samples = int(0.02 * LaserPlasmaSuite.SAMPLE_RATE)
        if fade_samples > 0 and fade_samples < len(env):
            env[-fade_samples:] *= np.linspace(1, 0, fade_samples)

        return (mix * env).astype(np.float32)

    @staticmethod
    def energy_beam_charge(duration=1.2):
        t = np.linspace(0, duration, int(LaserPlasmaSuite.SAMPLE_RATE * duration), endpoint=False)

        # Accelerating ascending oscillator
        # Frequency increases exponentially
        f_start = 50.0
        f_end = 2500.0
        c = np.log(f_end / f_start)
        phi_main = 2 * np.pi * f_start * duration / c * (np.exp(c * t / duration) - 1)

        # Complex waveform: fundamental + harmonics
        wave1 = np.sin(phi_main)
        wave2 = 0.5 * np.sin(2 * phi_main)
        wave3 = 0.25 * np.sin(4 * phi_main + np.pi/4)

        # LFO that accelerates
        lfo_rate_start = 2.0
        lfo_rate_end = 20.0
        lfo_c = np.log(lfo_rate_end / lfo_rate_start)
        phi_lfo = 2 * np.pi * lfo_rate_start * duration / lfo_c * (np.exp(lfo_c * t / duration) - 1)
        lfo = 0.5 * (1 + np.sin(phi_lfo))

        # Mix
        mix = (wave1 + wave2 + wave3) * (0.5 + 0.5 * lfo)

        # Envelope: swell up
        # We want it to swell and hit max at the end, maybe fade out very quickly
        env = (t / duration) ** 2  # quadratic rise

        fade_samples = int(0.05 * LaserPlasmaSuite.SAMPLE_RATE)
        if fade_samples > 0 and fade_samples < len(env):
            env[-fade_samples:] *= np.linspace(1, 0, fade_samples)

        return (mix * env * 0.8).astype(np.float32)

    @staticmethod
    def shield_deflect_ping(duration=0.25):
        t = np.linspace(0, duration, int(LaserPlasmaSuite.SAMPLE_RATE * duration), endpoint=False)

        # High energy impact ping
        f_ping = 3500.0
        # Rapid decay on frequency for the ping
        f_instant = f_ping * np.exp(-20.0 * t)
        phi_ping = 2 * np.pi * np.cumsum(f_instant) / LaserPlasmaSuite.SAMPLE_RATE
        ping = np.sin(phi_ping) * np.exp(-30.0 * t)

        # Harmonic ring
        f_ring = 1800.0
        # slight vibrato
        vibrato = 1 + 0.02 * np.sin(2 * np.pi * 30.0 * t)
        phi_ring = 2 * np.pi * np.cumsum(f_ring * vibrato) / LaserPlasmaSuite.SAMPLE_RATE
        ring1 = np.sin(phi_ring)

        f_ring2 = 2750.0
        phi_ring2 = 2 * np.pi * np.cumsum(f_ring2 * vibrato) / LaserPlasmaSuite.SAMPLE_RATE
        ring2 = np.sin(phi_ring2)

        ring_env = np.exp(-4.0 * t)

        mix = ping * 0.8 + (ring1 * 0.4 + ring2 * 0.3) * ring_env

        # Smooth master envelope
        env = np.exp(-1.5 * t / duration)
        # fast attack fade in
        attack_samples = int(0.002 * LaserPlasmaSuite.SAMPLE_RATE)
        if attack_samples > 0 and attack_samples < len(env):
            env[:attack_samples] *= np.linspace(0, 1, attack_samples)

        fade_samples = int(0.01 * LaserPlasmaSuite.SAMPLE_RATE)
        if fade_samples > 0 and fade_samples < len(env):
            env[-fade_samples:] *= np.linspace(1, 0, fade_samples)

        return (mix * env).astype(np.float32)
