import numpy as np

class GlitchStutterSuite:
    SAMPLE_RATE = 48000

    @staticmethod
    def tape_motor_stop(audio_in: np.ndarray, slowdown_curve: float = 2.0) -> np.ndarray:
        """
        Analog vinyl/tape machine power-down deceleration and exponential pitch drop.
        """
        audio_in = np.asarray(audio_in, dtype=np.float32)
        n_samples = len(audio_in)
        if n_samples == 0:
            return audio_in

        t_out = np.arange(n_samples)
        # Read velocity decreases from 1 to 0 over the output duration
        # v(t) = (1 - t / N)^c
        # Integral p(t) = N / (c + 1) * (1 - (1 - t / N)^(c + 1))
        # Since p(t) is the read index in the input array.
        normalized_t = t_out / n_samples
        read_positions = (n_samples / (slowdown_curve + 1.0)) * (1.0 - (1.0 - normalized_t)**(slowdown_curve + 1.0))

        # Ensure we don't go out of bounds
        read_positions = np.clip(read_positions, 0, n_samples - 1)

        # Linear interpolation
        out = np.interp(read_positions, np.arange(n_samples), audio_in)
        return out.astype(np.float32)

    @staticmethod
    def bitcrush_buffer_freeze(duration: float = 0.4, bit_depth: int = 4, sample_rate_reduction: int = 8) -> np.ndarray:
        """
        Lo-fi digital bitcrusher with quantization distortion.
        Generates a frozen buffer (looped noise) and applies bitcrushing.
        """
        n_samples = int(duration * GlitchStutterSuite.SAMPLE_RATE)
        if n_samples == 0:
            return np.array([], dtype=np.float32)

        # Generate a "frozen" buffer: a short loop of random noise
        loop_length = max(1, int(GlitchStutterSuite.SAMPLE_RATE * 0.05)) # 50ms loop
        base_noise = np.random.uniform(-1.0, 1.0, loop_length).astype(np.float32)
        repeats = int(np.ceil(n_samples / loop_length))
        audio = np.tile(base_noise, repeats)[:n_samples]

        # Sample rate reduction (Sample and Hold)
        if sample_rate_reduction > 1:
            indices = np.arange(n_samples)
            # Hold the value from the start of each block
            held_indices = (indices // sample_rate_reduction) * sample_rate_reduction
            audio = audio[held_indices]

        # Bit depth quantization
        if bit_depth > 0:
            levels = 2 ** bit_depth
            # Map [-1, 1] to [0, levels - 1]
            normalized = (audio + 1.0) / 2.0
            quantized = np.round(normalized * (levels - 1))
            # Map back to [-1, 1]
            audio = (quantized / (levels - 1)) * 2.0 - 1.0

        return audio.astype(np.float32)

    @staticmethod
    def digital_glitch_stutter(duration: float = 0.5, slice_count: int = 12, randomize: bool = True) -> np.ndarray:
        """
        Granular buffer stutter and micro-repeats.
        """
        n_samples = int(duration * GlitchStutterSuite.SAMPLE_RATE)
        if n_samples == 0:
            return np.array([], dtype=np.float32)

        # Base tone to stutter
        t = np.linspace(0, duration, n_samples, endpoint=False)
        # Complex tone: sine wave + FM modulation + noise
        base_audio = np.sin(2 * np.pi * 110 * t + np.sin(2 * np.pi * 55 * t)) * 0.5
        base_audio += np.random.uniform(-0.1, 0.1, n_samples)
        base_audio = np.clip(base_audio, -1.0, 1.0)

        if slice_count <= 0:
            return base_audio.astype(np.float32)

        slice_length = max(1, n_samples // slice_count)
        slices = []
        for i in range(slice_count):
            start = i * slice_length
            end = min(n_samples, start + slice_length)
            slices.append(base_audio[start:end])

        output = []
        current_len = 0

        # If randomizing, we randomly repeat some slices
        # If not, we just repeat every second slice once
        for i in range(slice_count):
            sl = slices[i]
            repeats = 1
            if randomize:
                if np.random.rand() > 0.5:
                    repeats = np.random.randint(2, 5) # Micro-repeats
            else:
                if i % 2 == 1:
                    repeats = 2

            for _ in range(repeats):
                output.append(sl)
                current_len += len(sl)
                if current_len >= n_samples:
                    break
            if current_len >= n_samples:
                break

        if len(output) > 0:
            out_audio = np.concatenate(output)[:n_samples]
        else:
            out_audio = np.zeros(n_samples, dtype=np.float32)

        # Pad with zeros if shorter (though logic above should mostly fill it)
        if len(out_audio) < n_samples:
            out_audio = np.pad(out_audio, (0, n_samples - len(out_audio)))

        return out_audio.astype(np.float32)

    @staticmethod
    def data_corruption_burst(duration: float = 0.3) -> np.ndarray:
        """
        Synthetic high-entropy digital data packet burst.
        """
        n_samples = int(duration * GlitchStutterSuite.SAMPLE_RATE)
        if n_samples == 0:
            return np.array([], dtype=np.float32)

        # Start with high-entropy noise
        audio = np.random.uniform(-1.0, 1.0, n_samples).astype(np.float32)

        # Modulate with various square waves to simulate digital packets
        t = np.arange(n_samples) / GlitchStutterSuite.SAMPLE_RATE

        packet_freq1 = 150.0
        packet_freq2 = 1200.0

        mod1 = np.sign(np.sin(2 * np.pi * packet_freq1 * t))
        mod2 = np.sign(np.sin(2 * np.pi * packet_freq2 * t + 0.5))

        # Add random dropouts
        dropouts = np.where(np.random.rand(n_samples) > 0.95, 0.0, 1.0)

        audio = audio * mod1 * mod2 * dropouts

        # Hard clipping
        audio = np.clip(audio * 2.0, -1.0, 1.0)

        return audio.astype(np.float32)
