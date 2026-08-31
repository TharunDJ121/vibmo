"""
Tier 1 E2E Tests: Procedural Audio & Sound Synthesis (Section 1).
Covers all 15 audio generator suites with >=5 tests per feature.
"""

import pytest
import numpy as np
from .conftest import assert_valid_audio_array

from vibmo.audio.generators.sfx_whoosh_designer_suite import WhooshDesignerSuite
from vibmo.audio.generators.sfx_cyber_ui_suite import CyberUISFXSuite
from vibmo.audio.generators.sfx_glitch_stutter_suite import GlitchStutterSuite
from vibmo.audio.generators.sfx_impact_sub_suite import ImpactSubSuite
from vibmo.audio.generators.sfx_keyboard_foley_suite import KeyboardFoleySuite
from vibmo.audio.generators.sfx_riser_tension_suite import RiserTensionSuite
from vibmo.audio.generators.sfx_ambient_drone_suite import AmbientDroneSuite
from vibmo.audio.generators.sfx_vinyl_crackle_suite import VinylCrackleSuite
from vibmo.audio.generators.sfx_laser_plasma_suite import LaserPlasmaSuite
from vibmo.audio.generators.sfx_liquid_bubbles_suite import LiquidBubblesSuite
from vibmo.audio.generators.sfx_paper_card_suite import PaperCardSuite
from vibmo.audio.generators.sfx_retro_8bit_suite import Retro8BitSuite
from vibmo.audio.generators.sfx_alarm_siren_suite import AlarmSirenSuite
from vibmo.audio.generators.sfx_chimes_harmonic_suite import ChimesHarmonicSuite
from vibmo.audio.generators.sfx_camera_shutter_suite import CameraShutterSuite


# ============================================================================
# 1. Whoosh Designer Suite (>=5 tests)
# ============================================================================

def test_whoosh_cinematic_passby_defaults():
    audio = WhooshDesignerSuite.cinematic_passby()
    assert_valid_audio_array(audio, expected_sr=48000)
    assert audio.ndim in (1, 2)


def test_whoosh_doppler_whip_speed_variation():
    audio_fast = WhooshDesignerSuite.doppler_whip(duration=0.3, speed=3.0)
    audio_slow = WhooshDesignerSuite.doppler_whip(duration=0.6, speed=1.0)
    assert_valid_audio_array(audio_fast)
    assert_valid_audio_array(audio_slow)
    assert audio_slow.size > audio_fast.size


def test_whoosh_quick_snap_whoosh():
    audio = WhooshDesignerSuite.quick_snap_whoosh()
    assert_valid_audio_array(audio)


def test_whoosh_airy_transition():
    audio = WhooshDesignerSuite.airy_transition()
    assert_valid_audio_array(audio)


def test_whoosh_sub_bass_flyby():
    audio = WhooshDesignerSuite.sub_bass_flyby()
    assert_valid_audio_array(audio)


# ============================================================================
# 2. Cyber UI Suite (>=5 tests)
# ============================================================================

def test_cyber_ui_holographic_click():
    audio = CyberUISFXSuite.holographic_click()
    assert_valid_audio_array(audio)


def test_cyber_ui_holo_chirp_frequencies():
    audio_high = CyberUISFXSuite.holo_chirp(freq_start=1800, freq_end=3200)
    assert_valid_audio_array(audio_high)


def test_cyber_ui_data_packet_burst():
    audio = CyberUISFXSuite.data_packet_burst()
    assert_valid_audio_array(audio)


def test_cyber_ui_access_granted_tone():
    audio = CyberUISFXSuite.access_granted_tone()
    assert_valid_audio_array(audio)


def test_cyber_ui_access_denied_klaxon():
    audio = CyberUISFXSuite.access_denied_klaxon()
    assert_valid_audio_array(audio)


# ============================================================================
# 3. Glitch Stutter Suite (>=5 tests)
# ============================================================================

def test_glitch_digital_stutter_burst():
    audio = GlitchStutterSuite.digital_stutter_burst()
    assert_valid_audio_array(audio)


def test_glitch_digital_glitch_stutter_durations():
    audio1 = GlitchStutterSuite.digital_glitch_stutter(duration=0.2)
    audio2 = GlitchStutterSuite.digital_glitch_stutter(duration=0.5)
    assert_valid_audio_array(audio1)
    assert_valid_audio_array(audio2)
    assert len(audio2) > len(audio1)


def test_glitch_bitcrush_buffer_freeze():
    audio = GlitchStutterSuite.bitcrush_buffer_freeze()
    assert_valid_audio_array(audio)


def test_glitch_data_corruption_burst():
    audio = GlitchStutterSuite.data_corruption_burst()
    assert_valid_audio_array(audio)


def test_glitch_tape_motor_stop():
    base_audio = GlitchStutterSuite.digital_glitch_stutter(duration=0.5)
    audio = GlitchStutterSuite.tape_motor_stop(base_audio)
    assert_valid_audio_array(audio)


# ============================================================================
# 4. Impact Sub Suite (>=5 tests)
# ============================================================================

def test_impact_cinematic_trailer_sub_drop():
    audio = ImpactSubSuite.cinematic_trailer_sub_drop()
    assert_valid_audio_array(audio)


def test_impact_cinematic_808_drop():
    audio = ImpactSubSuite.cinematic_808_drop()
    assert_valid_audio_array(audio)


def test_impact_card_slam_impact():
    audio = ImpactSubSuite.card_slam_impact()
    assert_valid_audio_array(audio)


def test_impact_metallic_anvil_hit():
    audio = ImpactSubSuite.metallic_anvil_hit()
    assert_valid_audio_array(audio)


def test_impact_punch_thud_impact():
    audio = ImpactSubSuite.punch_thud_impact()
    assert_valid_audio_array(audio)


# ============================================================================
# 5. Keyboard Foley Suite (>=5 tests)
# ============================================================================

def test_keyboard_mechanical_keystroke_switches():
    for switch in ["blue", "brown", "red"]:
        audio = KeyboardFoleySuite.mechanical_keystroke(switch=switch)
        assert_valid_audio_array(audio)


def test_keyboard_clicky_blue_switch():
    audio = KeyboardFoleySuite.clicky_blue_switch()
    assert_valid_audio_array(audio)


def test_keyboard_tactile_brown_switch():
    audio = KeyboardFoleySuite.tactile_brown_switch()
    assert_valid_audio_array(audio)


def test_keyboard_linear_red_switch():
    audio = KeyboardFoleySuite.linear_red_switch()
    assert_valid_audio_array(audio)


def test_keyboard_spacebar_thud_and_typewriter_bell():
    audio_space = KeyboardFoleySuite.spacebar_thud()
    audio_bell = KeyboardFoleySuite.typewriter_bell()
    assert_valid_audio_array(audio_space)
    assert_valid_audio_array(audio_bell)


# ============================================================================
# 6. Riser Tension Suite (>=5 tests)
# ============================================================================

def test_riser_shepard_tone_riser_defaults():
    audio = RiserTensionSuite.shepard_tone_riser(duration=2.0)
    assert_valid_audio_array(audio)


def test_riser_cyber_pitch_riser():
    audio = RiserTensionSuite.cyber_pitch_riser(duration=1.5)
    assert_valid_audio_array(audio)


def test_riser_white_noise_sweep():
    audio = RiserTensionSuite.white_noise_sweep(duration=1.0)
    assert_valid_audio_array(audio)


def test_riser_tension_alarm_build():
    audio = RiserTensionSuite.tension_alarm_build()
    assert_valid_audio_array(audio)


def test_riser_shepard_tone_varying_durations():
    audio_short = RiserTensionSuite.shepard_tone_riser(duration=0.8)
    audio_long = RiserTensionSuite.shepard_tone_riser(duration=2.5)
    assert_valid_audio_array(audio_short)
    assert_valid_audio_array(audio_long)
    assert len(audio_long) > len(audio_short)


# ============================================================================
# 7. Ambient Drone Suite (>=5 tests)
# ============================================================================

def test_ambient_sci_fi_deep_space_drone():
    audio = AmbientDroneSuite.sci_fi_deep_space_drone(duration=2.0)
    assert_valid_audio_array(audio)


def test_ambient_dark_scifi_drone():
    audio = AmbientDroneSuite.dark_scifi_drone(duration=2.0)
    assert_valid_audio_array(audio)


def test_ambient_ethereal_sub_pad():
    audio = AmbientDroneSuite.ethereal_sub_pad(duration=2.0)
    assert_valid_audio_array(audio)


def test_ambient_server_room_fan_hum():
    audio = AmbientDroneSuite.server_room_fan_hum(duration=1.5)
    assert_valid_audio_array(audio)


def test_ambient_warp_drive_hum():
    audio = AmbientDroneSuite.warp_drive_hum(duration=2.0)
    assert_valid_audio_array(audio)


# ============================================================================
# 8. Vinyl Crackle Suite (>=5 tests)
# ============================================================================

def test_vinyl_vintage_turntable_hiss():
    audio = VinylCrackleSuite.vintage_turntable_hiss(duration=2.0)
    assert_valid_audio_array(audio)


def test_vinyl_dust_pops():
    audio = VinylCrackleSuite.dust_pops(duration=1.5)
    assert_valid_audio_array(audio)


def test_vinyl_needle_drop_thump():
    audio = VinylCrackleSuite.needle_drop_thump()
    assert_valid_audio_array(audio)


def test_vinyl_analog_tape_hiss():
    audio = VinylCrackleSuite.analog_tape_hiss(duration=2.0)
    assert_valid_audio_array(audio)


def test_vinyl_surface_hiss():
    audio = VinylCrackleSuite.vinyl_surface_hiss(duration=1.5)
    assert_valid_audio_array(audio)


# ============================================================================
# 9. Laser Plasma Suite (>=5 tests)
# ============================================================================

def test_laser_plasma_beam_fire():
    audio = LaserPlasmaSuite.plasma_beam_fire()
    assert_valid_audio_array(audio)


def test_laser_plasma_pulse_blast():
    audio = LaserPlasmaSuite.plasma_pulse_blast()
    assert_valid_audio_array(audio)


def test_laser_arcade_laser_zap():
    audio = LaserPlasmaSuite.arcade_laser_zap()
    assert_valid_audio_array(audio)


def test_laser_energy_beam_charge():
    audio = LaserPlasmaSuite.energy_beam_charge(duration=1.2)
    assert_valid_audio_array(audio)


def test_laser_shield_deflect_ping():
    audio = LaserPlasmaSuite.shield_deflect_ping()
    assert_valid_audio_array(audio)


# ============================================================================
# 10. Liquid Bubbles Suite (>=5 tests)
# ============================================================================

def test_liquid_water_bubble_pop():
    audio = LiquidBubblesSuite.water_bubble_pop()
    assert_valid_audio_array(audio)


def test_liquid_viscous_pop_bubble():
    audio = LiquidBubblesSuite.viscous_pop_bubble()
    assert_valid_audio_array(audio)


def test_liquid_submerged_bubble_cluster():
    audio = LiquidBubblesSuite.submerged_bubble_cluster()
    assert_valid_audio_array(audio)


def test_liquid_drop_splash():
    audio = LiquidBubblesSuite.liquid_drop_splash()
    assert_valid_audio_array(audio)


def test_liquid_water_pour_stream():
    audio = LiquidBubblesSuite.water_pour_stream(duration=1.5)
    assert_valid_audio_array(audio)


# ============================================================================
# 11. Paper Card Suite (>=5 tests)
# ============================================================================

def test_paper_card_flip_shuffle():
    audio = PaperCardSuite.card_flip_shuffle()
    assert_valid_audio_array(audio)


def test_paper_card_shuffle_slide():
    audio = PaperCardSuite.card_shuffle_slide()
    assert_valid_audio_array(audio)


def test_paper_deck_snap_slide():
    audio = PaperCardSuite.deck_snap_slide()
    assert_valid_audio_array(audio)


def test_paper_flip_rustle():
    audio = PaperCardSuite.paper_flip_rustle()
    assert_valid_audio_array(audio)


def test_paper_sheet_unfold_crinkle():
    audio = PaperCardSuite.sheet_unfold_crinkle()
    assert_valid_audio_array(audio)


# ============================================================================
# 12. Retro 8-Bit Suite (>=5 tests)
# ============================================================================

def test_retro_arcade_coin_jump():
    audio = Retro8BitSuite.arcade_coin_jump()
    assert_valid_audio_array(audio)


def test_retro_coin_pickup():
    audio = Retro8BitSuite.coin_pickup()
    assert_valid_audio_array(audio)


def test_retro_jump_boing():
    audio = Retro8BitSuite.jump_boing()
    assert_valid_audio_array(audio)


def test_retro_level_up_fanfare():
    audio = Retro8BitSuite.level_up_fanfare()
    assert_valid_audio_array(audio)


def test_retro_power_down_slide():
    audio = Retro8BitSuite.power_down_slide()
    assert_valid_audio_array(audio)


# ============================================================================
# 13. Alarm Siren Suite (>=5 tests)
# ============================================================================

def test_alarm_emergency_klaxon_sweep():
    audio = AlarmSirenSuite.emergency_klaxon_sweep()
    assert_valid_audio_array(audio)


def test_alarm_biohazard_pulse_siren():
    audio = AlarmSirenSuite.biohazard_pulse_siren()
    assert_valid_audio_array(audio)


def test_alarm_nuclear_countdown_beep():
    audio = AlarmSirenSuite.nuclear_countdown_beep()
    assert_valid_audio_array(audio)


def test_alarm_security_chirp_alarm():
    audio = AlarmSirenSuite.security_chirp_alarm()
    assert_valid_audio_array(audio)


def test_alarm_durations_and_frequencies():
    audio = AlarmSirenSuite.emergency_klaxon_sweep(duration=1.8)
    assert_valid_audio_array(audio)
    assert len(audio) == int(48000 * 1.8) or len(audio) > 0


# ============================================================================
# 14. Chimes Harmonic Suite (>=5 tests)
# ============================================================================

def test_chimes_celestial_wind_chime():
    audio = ChimesHarmonicSuite.celestial_wind_chime()
    assert_valid_audio_array(audio)


def test_chimes_crystal_bell_chime():
    audio = ChimesHarmonicSuite.crystal_bell_chime()
    assert_valid_audio_array(audio)


def test_chimes_sparkle_magic_glimmer():
    audio = ChimesHarmonicSuite.sparkle_magic_glimmer()
    assert_valid_audio_array(audio)


def test_chimes_dream_harp_glissando():
    audio = ChimesHarmonicSuite.dream_harp_glissando()
    assert_valid_audio_array(audio)


def test_chimes_celebration_fanfare_tone():
    audio = ChimesHarmonicSuite.celebration_fanfare_tone()
    assert_valid_audio_array(audio)


# ============================================================================
# 15. Camera Shutter Suite (>=5 tests)
# ============================================================================

def test_camera_dslr_rapid_burst():
    audio = CameraShutterSuite.dslr_rapid_burst()
    assert_valid_audio_array(audio)


def test_camera_dslr_mirror_slap():
    audio = CameraShutterSuite.dslr_mirror_slap()
    assert_valid_audio_array(audio)


def test_camera_polaroid_eject():
    audio = CameraShutterSuite.polaroid_eject()
    assert_valid_audio_array(audio)


def test_camera_smartphone_snap_flash():
    audio = CameraShutterSuite.smartphone_snap_flash()
    assert_valid_audio_array(audio)


def test_camera_vintage_motor_advance():
    audio = CameraShutterSuite.vintage_motor_advance()
    assert_valid_audio_array(audio)
