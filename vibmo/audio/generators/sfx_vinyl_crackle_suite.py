import numpy as np

class VinylCrackleSuite:
    SAMPLE_RATE = 48000

    @staticmethod
    def vinyl_surface_hiss(duration=4.0, noise_floor=0.08):
        """Warm analog turntable vinyl surface noise and groove friction."""
        samples = int(duration * VinylCrackleSuite.SAMPLE_RATE)
        # Generate white noise
        white = np.random.normal(0, 1, samples)

        # Apply a pink noise filter using FFT
        fft_white = np.fft.rfft(white)
        freqs = np.fft.rfftfreq(samples, d=1.0/VinylCrackleSuite.SAMPLE_RATE)

        with np.errstate(divide='ignore'):
            pink_filter = 1 / (freqs ** 0.5)
        pink_filter[0] = 0

        pink_noise = np.fft.irfft(fft_white * pink_filter, n=samples)

        if np.max(np.abs(pink_noise)) > 0:
            pink_noise = pink_noise / np.max(np.abs(pink_noise))

        t = np.linspace(0, duration, samples, endpoint=False)
        # Groove friction (rumble)
        rumble = np.sin(2 * np.pi * (33.33 / 60) * t) * 0.5
        rumble += np.sin(2 * np.pi * 50 * t) * 0.2

        hiss = (pink_noise * 0.7 + rumble * 0.3) * noise_floor
        return hiss.astype(np.float32)

    @staticmethod
    def dust_pops(duration=4.0, pop_density=12.0):
        """Random non-periodic micro vinyl pops and clicks."""
        samples = int(duration * VinylCrackleSuite.SAMPLE_RATE)
        audio = np.zeros(samples, dtype=np.float32)

        num_pops_expected = duration * pop_density
        num_pops = np.random.poisson(num_pops_expected)

        if num_pops > 0:
            pop_indices = np.random.randint(0, samples, num_pops)
            for idx in pop_indices:
                pop_len = int(VinylCrackleSuite.SAMPLE_RATE * np.random.uniform(0.001, 0.005))
                pop = np.random.uniform(-1, 1, pop_len)
                decay = np.exp(-np.linspace(0, 5, pop_len))
                pop = pop * decay * np.random.uniform(0.1, 0.8)

                end_idx = min(idx + pop_len, samples)
                act_len = end_idx - idx
                audio[idx:end_idx] += pop[:act_len]

        return audio.astype(np.float32)

    @staticmethod
    def needle_drop_thump(duration=0.6):
        """Acoustic turntable stylus landing on record groove with low-end rumble."""
        samples = int(duration * VinylCrackleSuite.SAMPLE_RATE)
        t = np.linspace(0, duration, samples, endpoint=False)

        # Thump (frequency drop)
        f0 = 80.0
        f1 = 20.0
        freqs = f0 * (f1/f0)**(t / (duration * 0.2 + 0.01))
        phase = np.cumsum(freqs) / VinylCrackleSuite.SAMPLE_RATE * 2 * np.pi
        thump = np.sin(phase)

        env = np.exp(-t * 15)
        thump *= env

        # Scratch from landing
        scratch_len = int(0.05 * VinylCrackleSuite.SAMPLE_RATE)
        scratch = np.random.uniform(-1, 1, scratch_len)
        scratch_env = np.exp(-np.linspace(0, 10, scratch_len))
        scratch *= scratch_env * 0.3

        audio = thump.copy()
        if scratch_len > 0:
            end_idx = min(scratch_len, samples)
            audio[:end_idx] += scratch[:end_idx]

        # Low-end rumble
        rumble = np.sin(2 * np.pi * (33.33 / 60) * t) * 0.2
        rumble_env = 1.0 - np.exp(-t * 5)
        audio += rumble * rumble_env

        return audio.astype(np.float32)

    @staticmethod
    def analog_tape_hiss(duration=4.0, warm_color=True):
        """1/4-inch magnetic tape saturation and subtle wow/flutter."""
        samples = int(duration * VinylCrackleSuite.SAMPLE_RATE)
        white_noise = np.random.normal(0, 1, samples)

        if warm_color:
            fft_white = np.fft.rfft(white_noise)
            freqs = np.fft.rfftfreq(samples, d=1.0/VinylCrackleSuite.SAMPLE_RATE)
            # Lowpass filter like tape (roll-off around 5000 Hz)
            filter_curve = 1.0 / (1.0 + (freqs / 5000.0)**2)
            noise = np.fft.irfft(fft_white * filter_curve, n=samples)
            if np.max(np.abs(noise)) > 0:
                noise /= np.max(np.abs(noise))
        else:
            noise = white_noise
            if np.max(np.abs(noise)) > 0:
                noise /= np.max(np.abs(noise))

        noise = noise * 0.05

        t = np.linspace(0, duration, samples, endpoint=False)
        wow = np.sin(2 * np.pi * 0.5 * t) * 0.1
        flutter = np.sin(2 * np.pi * 10 * t) * 0.05

        wobble = 1.0 + wow + flutter
        tape_hiss = noise * wobble

        # Tape saturation (soft clipping)
        tape_hiss = np.tanh(tape_hiss * 1.5)

        return tape_hiss.astype(np.float32)
