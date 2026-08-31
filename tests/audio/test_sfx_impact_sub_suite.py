import unittest
import numpy as np
from vibmo.audio.generators.sfx_impact_sub_suite import ImpactSubSuite

class TestImpactSubSuite(unittest.TestCase):
    def setUp(self):
        self.SR = ImpactSubSuite.SR

    def _verify_audio_props(self, audio, expected_duration):
        # Sample rate adherence & correct array lengths
        expected_len = int(expected_duration * self.SR)
        self.assertEqual(len(audio), expected_len, f"Expected length {expected_len}, got {len(audio)}")

        # Array types
        self.assertEqual(audio.dtype, np.float32, f"Expected dtype float32, got {audio.dtype}")

        # Non-clipping
        max_amp = np.max(np.abs(audio))
        self.assertTrue(max_amp <= 1.0 + 1e-6, f"Audio clipped, max amplitude is {max_amp}")

        # Decay (verify end of file is quieter than the beginning for impacts)
        # We can check max amplitude in first 20% vs last 20%
        first_part = audio[:int(len(audio)*0.2)]
        last_part = audio[-int(len(audio)*0.2):]

        max_first = np.max(np.abs(first_part)) if len(first_part) > 0 else 0
        max_last = np.max(np.abs(last_part)) if len(last_part) > 0 else 0

        # Not all sounds decay to absolute 0 immediately, but should be quieter than beginning
        # (Though some could have a slow attack, impacts typically have fast attack and decay)
        self.assertTrue(max_last < max_first * 0.5 + 0.05,
                        f"Expected decay, but last part max ({max_last}) is not significantly smaller than first part max ({max_first})")

    def test_cinematic_808_drop(self):
        duration = 1.2
        audio = ImpactSubSuite.cinematic_808_drop(duration=duration, start_freq=160.0, end_freq=32.0, saturation=1.4)
        self._verify_audio_props(audio, duration)

    def test_punch_thud_impact(self):
        duration = 0.45
        audio = ImpactSubSuite.punch_thud_impact(duration=duration, attack_click=True)
        self._verify_audio_props(audio, duration)

        # Also test without click
        audio_no_click = ImpactSubSuite.punch_thud_impact(duration=duration, attack_click=False)
        self._verify_audio_props(audio_no_click, duration)

    def test_metallic_anvil_hit(self):
        duration = 0.9
        audio = ImpactSubSuite.metallic_anvil_hit(duration=duration, ring_freq=880.0)
        self._verify_audio_props(audio, duration)

    def test_card_slam_impact(self):
        duration = 0.35
        audio = ImpactSubSuite.card_slam_impact(duration=duration)
        self._verify_audio_props(audio, duration)

    def test_cinematic_trailer_sub_drop(self):
        decay = 2.0
        audio = ImpactSubSuite.cinematic_trailer_sub_drop(decay=decay)
        self._verify_audio_props(audio, decay)

if __name__ == '__main__':
    unittest.main()

