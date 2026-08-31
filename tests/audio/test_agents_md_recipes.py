import numpy as np
import pytest

from vibmo.audio.generators import (
    WhooshDesignerSuite,
    CyberUiSuite,
    CyberUISFXSuite,
    GlitchStutterSuite,
    ImpactSubSuite,
    KeyboardFoleySuite,
    RiserTensionSuite,
    AmbientDroneSuite,
    VinylCrackleSuite,
    LaserPlasmaSuite,
    LiquidBubblesSuite,
    PaperCardSuite,
    Retro8bitSuite,
    Retro8BitSuite,
    AlarmSirenSuite,
    ChimesHarmonicSuite,
    CameraShutterSuite,
)


def _check_audio_common(audio: np.ndarray, expected_duration: float = None, sample_rate: int = 48000):
    assert isinstance(audio, np.ndarray), f"Expected np.ndarray, got {type(audio)}"
    assert audio.dtype == np.float32, f"Expected float32 dtype, got {audio.dtype}"
    assert np.any(np.abs(audio) > 1e-4), "Audio output is completely silent"
    assert np.max(np.abs(audio)) <= 1.05, f"Audio exceeds standard amplitude range: {np.max(np.abs(audio))}"

    if expected_duration is not None:
        expected_samples = int(expected_duration * sample_rate)
        if audio.ndim == 1:
            assert len(audio) == expected_samples, f"Expected {expected_samples} samples, got {len(audio)}"
        elif audio.ndim == 2:
            if audio.shape[0] == 2:  # Stereo (2, N)
                assert audio.shape[1] == expected_samples, f"Expected {expected_samples} samples per channel, got {audio.shape[1]}"
            else:  # Stereo (N, 2)
                assert audio.shape[0] == expected_samples, f"Expected {expected_samples} samples, got {audio.shape[0]}"


def test_recipe_1_whoosh_designer():
    audio = WhooshDesignerSuite.cinematic_passby(duration=1.2)
    _check_audio_common(audio, expected_duration=1.2)
    assert audio.shape == (2, int(48000 * 1.2))


def test_recipe_2_cyber_ui():
    click_sfx = CyberUiSuite.holographic_click(pitch=800)
    _check_audio_common(click_sfx, expected_duration=0.05)

    # Alias check
    assert CyberUiSuite is CyberUISFXSuite
    click_alias = CyberUISFXSuite.holographic_click(pitch=800)
    np.testing.assert_array_equal(click_sfx, click_alias)


def test_recipe_3_glitch_stutter():
    glitch_audio = GlitchStutterSuite.digital_stutter_burst(duration=0.8)
    _check_audio_common(glitch_audio, expected_duration=0.8)


def test_recipe_4_impact_sub():
    boom = ImpactSubSuite.cinematic_trailer_sub_drop(decay=2.0)
    _check_audio_common(boom, expected_duration=2.0)


def test_recipe_5_keyboard_foley():
    typing_sfx = KeyboardFoleySuite.mechanical_keystroke(switch="blue")
    _check_audio_common(typing_sfx)


def test_recipe_6_riser_tension():
    riser = RiserTensionSuite.shepard_tone_riser(duration=3.0)
    _check_audio_common(riser, expected_duration=3.0)


def test_recipe_7_ambient_drone():
    drone = AmbientDroneSuite.sci_fi_deep_space_drone(duration=10.0)
    _check_audio_common(drone, expected_duration=10.0)
    assert drone.shape == (int(48000 * 10.0), 2)


def test_recipe_8_vinyl_crackle():
    lofi = VinylCrackleSuite.vintage_turntable_hiss(duration=5.0)
    _check_audio_common(lofi, expected_duration=5.0)


def test_recipe_9_laser_plasma():
    pew = LaserPlasmaSuite.plasma_beam_fire()
    _check_audio_common(pew, expected_duration=0.32)


def test_recipe_10_liquid_bubbles():
    pop = LiquidBubblesSuite.water_bubble_pop()
    _check_audio_common(pop, expected_duration=0.09)


def test_recipe_11_paper_card():
    card_sfx = PaperCardSuite.card_flip_shuffle()
    _check_audio_common(card_sfx, expected_duration=0.22)


def test_recipe_12_retro_8bit():
    coin = Retro8bitSuite.arcade_coin_jump()
    _check_audio_common(coin, expected_duration=0.30)

    # Alias check
    assert Retro8bitSuite is Retro8BitSuite
    coin_alias = Retro8BitSuite.arcade_coin_jump()
    np.testing.assert_array_equal(coin, coin_alias)


def test_recipe_13_alarm_siren():
    alarm = AlarmSirenSuite.emergency_klaxon_sweep()
    _check_audio_common(alarm, expected_duration=1.5)


def test_recipe_14_chimes_harmonic():
    sparkle_sfx = ChimesHarmonicSuite.celestial_wind_chime()
    _check_audio_common(sparkle_sfx, expected_duration=1.2)


def test_recipe_15_camera_shutter():
    photo = CameraShutterSuite.dslr_rapid_burst()
    _check_audio_common(photo, expected_duration=0.60)


def test_all_15_suites_exist_and_exported():
    expected_suites = [
        "AlarmSirenSuite",
        "AmbientDroneSuite",
        "CameraShutterSuite",
        "ChimesHarmonicSuite",
        "CyberUiSuite",
        "CyberUISFXSuite",
        "GlitchStutterSuite",
        "ImpactSubSuite",
        "KeyboardFoleySuite",
        "LaserPlasmaSuite",
        "LiquidBubblesSuite",
        "PaperCardSuite",
        "Retro8bitSuite",
        "Retro8BitSuite",
        "RiserTensionSuite",
        "VinylCrackleSuite",
        "WhooshDesignerSuite",
    ]
    import vibmo.audio.generators as g
    for suite_name in expected_suites:
        assert hasattr(g, suite_name), f"Missing {suite_name} in vibmo.audio.generators"
        assert suite_name in g.__all__, f"{suite_name} not in vibmo.audio.generators.__all__"
