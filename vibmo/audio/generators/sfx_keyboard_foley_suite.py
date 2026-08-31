import numpy as np

class KeyboardFoleySuite:
    SAMPLE_RATE = 48000

    @staticmethod
    def clicky_blue_switch(duration=0.06):
        sr = 48000
        n_samples = int(sr * duration)
        if n_samples == 0:
            return np.array([], dtype=np.float32)
        t = np.linspace(0, duration, n_samples, endpoint=False)

        # Click 1: Click jacket snapping down
        env1 = np.exp(-t * 2000)
        noise1 = np.random.normal(0, 1, n_samples)
        click1 = noise1 * env1

        # Click 2: Bottom out
        t2_offset = int(0.015 * sr)
        t2_len = n_samples - t2_offset
        if t2_len > 0:
            t2 = np.linspace(0, t2_len/sr, t2_len, endpoint=False)
            env2 = np.exp(-t2 * 800)
            noise2 = np.random.normal(0, 0.8, t2_len)
            thud2 = np.sin(2 * np.pi * 500 * t2) * np.exp(-t2 * 1000)
            click2 = np.zeros(n_samples)
            click2[t2_offset:] = (noise2 + thud2 * 0.5) * env2
        else:
            click2 = np.zeros(n_samples)

        audio = click1 * 0.6 + click2 * 0.4

        fade_len = int(0.005 * sr)
        if fade_len > 0 and n_samples > fade_len:
            audio[-fade_len:] *= np.linspace(1, 0, fade_len)

        return np.clip(audio, -1.0, 1.0).astype(np.float32)

    @staticmethod
    def tactile_brown_switch(duration=0.05):
        sr = 48000
        n_samples = int(sr * duration)
        if n_samples == 0:
            return np.array([], dtype=np.float32)
        t = np.linspace(0, duration, n_samples, endpoint=False)

        # Tactile bump
        env1 = np.exp(-t * 1200)
        noise1 = np.random.normal(0, 1, n_samples)
        window1 = np.ones(5)/5
        noise1_lp = np.convolve(noise1, window1, mode='same')
        bump = noise1_lp * env1 * 0.5

        # Bottom out
        t2_offset = int(0.01 * sr)
        t2_len = n_samples - t2_offset
        if t2_len > 0:
            t2 = np.linspace(0, t2_len/sr, t2_len, endpoint=False)
            env2 = np.exp(-t2 * 600)
            noise2 = np.random.normal(0, 1, t2_len)
            window2 = np.ones(10)/10
            noise2_lp = np.convolve(noise2, window2, mode='same')
            thud = np.sin(2 * np.pi * 300 * t2) * np.exp(-t2 * 800)
            bottom_out = np.zeros(n_samples)
            bottom_out[t2_offset:] = (noise2_lp * 0.8 + thud * 0.6) * env2
        else:
            bottom_out = np.zeros(n_samples)

        audio = bump + bottom_out

        fade_len = int(0.005 * sr)
        if fade_len > 0 and n_samples > fade_len:
            audio[-fade_len:] *= np.linspace(1, 0, fade_len)

        return np.clip(audio, -1.0, 1.0).astype(np.float32)

    @staticmethod
    def linear_red_switch(duration=0.04):
        sr = 48000
        n_samples = int(sr * duration)
        if n_samples == 0:
            return np.array([], dtype=np.float32)
        t = np.linspace(0, duration, n_samples, endpoint=False)

        # Smooth travel noise
        travel_env = np.exp(-t * 200)
        travel = np.random.normal(0, 0.1, n_samples) * travel_env

        # Bottom out thud
        thud_t_offset = int(0.005 * sr)
        t2_len = n_samples - thud_t_offset
        if t2_len > 0:
            t2 = np.linspace(0, t2_len/sr, t2_len, endpoint=False)
            env2 = np.exp(-t2 * 800)
            noise = np.random.normal(0, 1, t2_len)
            window = np.ones(15)/15
            thud_noise = np.convolve(noise, window, mode='same')
            thud_tone = np.sin(2 * np.pi * 200 * t2) * np.exp(-t2 * 1000)
            bottom = np.zeros(n_samples)
            bottom[thud_t_offset:] = (thud_noise * 0.7 + thud_tone * 0.4) * env2
        else:
            bottom = np.zeros(n_samples)

        audio = travel + bottom

        fade_len = int(0.005 * sr)
        if fade_len > 0 and n_samples > fade_len:
            audio[-fade_len:] *= np.linspace(1, 0, fade_len)

        return np.clip(audio, -1.0, 1.0).astype(np.float32)

    @staticmethod
    def spacebar_thud(duration=0.09):
        sr = 48000
        n_samples = int(sr * duration)
        if n_samples == 0:
            return np.array([], dtype=np.float32)
        t = np.linspace(0, duration, n_samples, endpoint=False)

        # Strong bottom out
        env_bottom = np.exp(-t * 300)
        thud_tone1 = np.sin(2 * np.pi * 100 * t) * np.exp(-t * 400)
        thud_tone2 = np.sin(2 * np.pi * 150 * t) * np.exp(-t * 500)
        noise = np.random.normal(0, 1, n_samples)
        window = np.ones(8)/8
        noise_bottom = np.convolve(noise, window, mode='same')
        bottom = (thud_tone1 * 0.6 + thud_tone2 * 0.3 + noise_bottom * 0.5) * env_bottom

        # Stabilizer bar rattle
        stab_tone1 = np.sin(2 * np.pi * 2500 * t) * np.exp(-t * 600)
        stab_tone2 = np.sin(2 * np.pi * 3200 * t) * np.exp(-t * 800)
        stab_env = np.exp(-t * 100) * (1 - np.exp(-t * 2000))
        rattle = (stab_tone1 * 0.3 + stab_tone2 * 0.2 + np.random.normal(0, 0.2, n_samples)) * stab_env

        # Rebound
        rebound_offset = int(0.04 * sr)
        rebound_len = n_samples - rebound_offset
        if rebound_len > 0:
            t_rebound = np.linspace(0, rebound_len/sr, rebound_len, endpoint=False)
            reb_env = np.exp(-t_rebound * 1000)
            reb_tone = np.sin(2 * np.pi * 600 * t_rebound) * np.exp(-t_rebound * 1500)
            reb_noise = np.random.normal(0, 1, rebound_len)
            rebound = np.zeros(n_samples)
            rebound[rebound_offset:] = (reb_tone * 0.4 + reb_noise * 0.3) * reb_env
        else:
            rebound = np.zeros(n_samples)

        audio = bottom + rattle * 0.3 + rebound

        max_val = np.max(np.abs(audio))
        if max_val > 1.0:
            audio /= max_val

        fade_len = int(0.005 * sr)
        if fade_len > 0 and n_samples > fade_len:
            audio[-fade_len:] *= np.linspace(1, 0, fade_len)

        return np.clip(audio, -1.0, 1.0).astype(np.float32)

    @staticmethod
    def typewriter_bell(duration=0.6):
        sr = 48000
        n_samples = int(sr * duration)
        if n_samples == 0:
            return np.array([], dtype=np.float32)
        t = np.linspace(0, duration, n_samples, endpoint=False)

        # Striker click
        click_env = np.exp(-t * 3000)
        click_noise = np.random.normal(0, 1, n_samples)
        striker = click_noise * click_env

        # Bell resonance
        f0 = 1500
        partials = [
            (f0, 1.0, 5),
            (f0 * 2.1, 0.6, 7),
            (f0 * 3.4, 0.4, 10),
            (f0 * 4.9, 0.2, 15),
            (f0 * 6.2, 0.1, 20)
        ]

        bell = np.zeros(n_samples)
        for freq, amp, decay in partials:
            bell += amp * np.sin(2 * np.pi * freq * t) * np.exp(-t * decay)

        # Modulation
        beat = np.sin(2 * np.pi * 10 * t) * 0.1 + 0.9
        bell *= beat

        audio = striker * 0.3 + bell * 0.7

        max_val = np.max(np.abs(audio))
        if max_val > 0.9:
            audio = (audio / max_val) * 0.9

        fade_len = int(0.01 * sr)
        if fade_len > 0 and n_samples > fade_len:
            audio[-fade_len:] *= np.linspace(1, 0, fade_len)

        return np.clip(audio, -1.0, 1.0).astype(np.float32)

    @staticmethod
    def mechanical_keystroke(switch: str = "blue", duration: float = None) -> np.ndarray:
        """Mechanical keyboard keystroke Foley synthesizing authentic switch profiles."""
        switch_lower = str(switch).lower()
        if "blue" in switch_lower or "clicky" in switch_lower:
            dur = duration if duration is not None else 0.06
            return KeyboardFoleySuite.clicky_blue_switch(duration=dur)
        elif "brown" in switch_lower or "tactile" in switch_lower:
            dur = duration if duration is not None else 0.05
            return KeyboardFoleySuite.tactile_brown_switch(duration=dur)
        elif "red" in switch_lower or "linear" in switch_lower:
            dur = duration if duration is not None else 0.04
            return KeyboardFoleySuite.linear_red_switch(duration=dur)
        elif "space" in switch_lower:
            dur = duration if duration is not None else 0.09
            return KeyboardFoleySuite.spacebar_thud(duration=dur)
        elif "typewriter" in switch_lower or "bell" in switch_lower:
            dur = duration if duration is not None else 0.6
            return KeyboardFoleySuite.typewriter_bell(duration=dur)
        else:
            dur = duration if duration is not None else 0.06
            return KeyboardFoleySuite.clicky_blue_switch(duration=dur)

