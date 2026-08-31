"""
Tier 1 E2E Tests: Kinetic Typography & Title Sequences (Section 6).
Covers all 15 dynamic typography components with >=5 tests per feature.
"""

import pytest
import cairo
from .conftest import assert_cairo_draw_safe

from vibmo.scene.scene import Scene
from vibmo.core.color import Color, colors

from vibmo.typography.kinetic.typo_glitch_decryptor_suite import GlitchDecryptorText, HexMatrixCycle
from vibmo.typography.kinetic.typo_liquid_wave_suite import LiquidWaveText, SubmergedTextRefraction
from vibmo.typography.kinetic.typo_isometric_3d_suite import IsometricExtruded3DText, BevelGleamLight
from vibmo.typography.kinetic.typo_neon_strobe_suite import RealisticNeonStrobeSign, BallastFlickerFailure
from vibmo.typography.kinetic.typo_particle_flame_suite import ParticleFlameText, DisintegratingEmbers
from vibmo.typography.kinetic.typo_split_flap_suite import SplitFlapAirportBoard, MechanicalFlapTile
from vibmo.typography.kinetic.typo_matrix_code_rain_suite import MatrixRainTypography, PhosphorTrailDecay
from vibmo.typography.kinetic.typo_slit_scan_synth_suite import SlitScanVideoSynthText, ChromaWarpWave
from vibmo.typography.kinetic.typo_odometer_tumbler_suite import OdometerTumblerCounter, VerticalRollingGlyphs
from vibmo.typography.kinetic.typo_badge_stamp_slam_suite import RubberStampTitleSlam, DustPuffShockwave
from vibmo.typography.kinetic.typo_magnetic_gravity_suite import MagneticGravityLetters, MagnetPullReassembly
from vibmo.typography.kinetic.typo_hologram_chroma_suite import HologramChromaText, InterferenceFringeLines
from vibmo.typography.kinetic.typo_terminal_typewriter_suite import PhosphorTerminalTypewriter, BlinkingBlockCaret
from vibmo.typography.kinetic.typo_brush_calligraphy_suite import BrushCalligraphyPathReveal, InkSplatterBleed
from vibmo.typography.kinetic.typo_elastic_squash_bounce_suite import ElasticSquashBounceTitle, JellyMorphTypography


# ============================================================================
# 1. Glitch Decryptor Text (>=5 tests)
# ============================================================================

def test_glitch_decryptor_defaults():
    text = GlitchDecryptorText("QUANTUM SECURE")
    assert_cairo_draw_safe(text)


def test_glitch_decryptor_decrypt_action():
    text = GlitchDecryptorText("DECRYPTING DATA")
    action = text.decrypt(duration=1.5)
    assert action is not None
    assert_cairo_draw_safe(text, timestamps=(0.0, 0.75, 1.5))


def test_glitch_decryptor_hex_matrix_cycle():
    cycle = HexMatrixCycle("A")
    assert_cairo_draw_safe(cycle)


def test_glitch_decryptor_empty_and_special_chars():
    t_empty = GlitchDecryptorText("")
    t_spec = GlitchDecryptorText("V!BM0_#99%")
    assert_cairo_draw_safe(t_empty)
    assert_cairo_draw_safe(t_spec)


def test_glitch_decryptor_custom_colors():
    text = GlitchDecryptorText("CYBERPUNK 2026", color=colors.CYAN, scramble_color=colors.EMERALD)
    assert_cairo_draw_safe(text)


# ============================================================================
# 2. Liquid Wave Refraction Text (>=5 tests)
# ============================================================================

def test_liquid_wave_text_defaults():
    text = LiquidWaveText("FLUID DYNAMICS")
    assert_cairo_draw_safe(text)


def test_liquid_wave_ripple_reveal():
    text = LiquidWaveText("RIPPLE STREAM")
    action = text.ripple_reveal(duration=1.2)
    assert action is not None
    assert_cairo_draw_safe(text)


def test_submerged_text_refraction():
    node = SubmergedTextRefraction("FLUID")
    assert_cairo_draw_safe(node)


def test_liquid_wave_amplitude_and_speed():
    text = LiquidWaveText("HIGH WAVE", wave_amplitude=15.0, wave_speed=2.0)
    assert_cairo_draw_safe(text)


def test_liquid_wave_timestamps():
    text = LiquidWaveText("OCEAN FLOW")
    assert_cairo_draw_safe(text, timestamps=(0.0, 0.5, 1.0, 2.0))


# ============================================================================
# 3. 3D Isometric Extruded Text (>=5 tests)
# ============================================================================

def test_isometric_3d_text_defaults():
    text = IsometricExtruded3DText("FUTURE TECH")
    assert_cairo_draw_safe(text)


def test_isometric_3d_text_gleam():
    text = IsometricExtruded3DText("GLEAM TITLE", depth=30.0)
    action = text.gleam(duration=1.0)
    assert action is not None
    assert_cairo_draw_safe(text)


def test_bevel_gleam_light_node():
    light = BevelGleamLight("3D")
    assert_cairo_draw_safe(light)


def test_isometric_3d_text_depth_variations():
    text_shallow = IsometricExtruded3DText("SHALLOW", depth=5.0)
    text_deep = IsometricExtruded3DText("DEEP", depth=60.0)
    assert_cairo_draw_safe(text_shallow)
    assert_cairo_draw_safe(text_deep)


def test_isometric_3d_text_colors():
    text = IsometricExtruded3DText("GOLD TITLE", face_color=colors.AMBER, shadow_color=colors.DARK_NAVY)
    assert_cairo_draw_safe(text)


# ============================================================================
# 4. Realistic Neon Strobe Sign (>=5 tests)
# ============================================================================

def test_neon_strobe_sign_defaults():
    neon = RealisticNeonStrobeSign("OPEN 24/7")
    assert_cairo_draw_safe(neon)


def test_neon_strobe_sign_ignite():
    neon = RealisticNeonStrobeSign("NEON SIGN")
    action = neon.ignite(duration=1.5)
    assert action is not None
    assert_cairo_draw_safe(neon)


def test_ballast_flicker_failure_node():
    ballast = BallastFlickerFailure()
    assert_cairo_draw_safe(ballast)


def test_neon_strobe_sign_colors():
    neon_cyan = RealisticNeonStrobeSign("CYAN GLOW", color=colors.CYAN)
    neon_rose = RealisticNeonStrobeSign("ROSE GLOW", color=colors.ROSE)
    assert_cairo_draw_safe(neon_cyan)
    assert_cairo_draw_safe(neon_rose)


def test_neon_strobe_sign_flicker_warmup():
    neon = RealisticNeonStrobeSign("FLICKER", flicker_warmup=True)
    assert_cairo_draw_safe(neon, timestamps=(0.0, 0.2, 0.8, 2.0))


# ============================================================================
# 5. Particle Flame Text (>=5 tests)
# ============================================================================

def test_particle_flame_text_defaults():
    fire = ParticleFlameText("BURNING PASSION")
    assert_cairo_draw_safe(fire)


def test_particle_flame_disintegrate():
    fire = ParticleFlameText("DISINTEGRATE")
    action = fire.disintegrate(duration=2.0)
    assert action is not None
    assert_cairo_draw_safe(fire)


def test_disintegrating_embers_node():
    embers = DisintegratingEmbers("BURNING")
    assert_cairo_draw_safe(embers)


def test_particle_flame_density():
    fire_dense = ParticleFlameText("BLAZE", ember_count=80)
    fire_sparse = ParticleFlameText("SPARK", ember_count=15)
    assert_cairo_draw_safe(fire_dense)
    assert_cairo_draw_safe(fire_sparse)


def test_particle_flame_timestamps():
    fire = ParticleFlameText("PHOENIX")
    assert_cairo_draw_safe(fire, timestamps=(0.0, 0.5, 1.5, 3.0))


# ============================================================================
# 6. Split-Flap Airport Board (>=5 tests)
# ============================================================================

def test_split_flap_board_defaults():
    board = SplitFlapAirportBoard(rows=2, cols=12)
    assert_cairo_draw_safe(board)


def test_split_flap_flip_to():
    board = SplitFlapAirportBoard(rows=2, cols=16)
    action = board.flip_to(["SAN FRANCISCO", "GATE B24"], duration=1.8)
    assert action is not None
    assert_cairo_draw_safe(board)


def test_mechanical_flap_tile_node():
    tile = MechanicalFlapTile(char="A")
    assert_cairo_draw_safe(tile)


def test_split_flap_board_dimensions():
    board = SplitFlapAirportBoard(rows=4, cols=20, tile_width=32, tile_height=48)
    assert_cairo_draw_safe(board)


def test_split_flap_timestamps():
    board = SplitFlapAirportBoard(rows=1, cols=8)
    assert_cairo_draw_safe(board, timestamps=(0.0, 0.5, 1.0, 2.0))


# ============================================================================
# 7. Matrix Code Rain Typography (>=5 tests)
# ============================================================================

def test_matrix_rain_typography_defaults():
    matrix = MatrixRainTypography("THE MATRIX")
    assert_cairo_draw_safe(matrix)


def test_matrix_rain_consolidate():
    matrix = MatrixRainTypography("CONSOLIDATE")
    action = matrix.consolidate(duration=2.0)
    assert action is not None
    assert_cairo_draw_safe(matrix)


def test_phosphor_trail_decay_node():
    trail = PhosphorTrailDecay("MATRIX")
    assert_cairo_draw_safe(trail)


def test_matrix_rain_glyph_density():
    matrix = MatrixRainTypography("CYBERDECK", stream_count=25)
    assert_cairo_draw_safe(matrix)


def test_matrix_rain_timestamps():
    matrix = MatrixRainTypography("CONSTRUCT")
    assert_cairo_draw_safe(matrix, timestamps=(0.0, 1.0, 2.5))


# ============================================================================
# 8. Slit-Scan Video Synth Text (>=5 tests)
# ============================================================================

def test_slit_scan_text_defaults():
    synth = SlitScanVideoSynthText("SYNTHESIZER")
    assert_cairo_draw_safe(synth)


def test_slit_scan_warp_scan():
    synth = SlitScanVideoSynthText("WARP SCAN")
    action = synth.warp_scan(duration=1.5)
    assert action is not None
    assert_cairo_draw_safe(synth)


def test_chroma_warp_wave_node():
    wave = ChromaWarpWave("SYNTH")
    assert_cairo_draw_safe(wave)


def test_slit_scan_frequencies():
    synth = SlitScanVideoSynthText("OSCILLATOR", wave_freq=4.0)
    assert_cairo_draw_safe(synth)


def test_slit_scan_timestamps():
    synth = SlitScanVideoSynthText("FEEDBACK")
    assert_cairo_draw_safe(synth, timestamps=(0.0, 0.5, 1.0, 2.0))


# ============================================================================
# 9. Mechanical Odometer Tumbler Counter (>=5 tests)
# ============================================================================

def test_odometer_counter_defaults():
    odo = OdometerTumblerCounter(start_val=0, end_val=1000)
    assert_cairo_draw_safe(odo)


def test_odometer_roll_to():
    odo = OdometerTumblerCounter(start_val=0, end_val=9999)
    action = odo.roll_to(8420, duration=1.8)
    assert action is not None
    assert_cairo_draw_safe(odo)


def test_vertical_rolling_glyphs_node():
    rolling = VerticalRollingGlyphs(digit=5)
    assert_cairo_draw_safe(rolling)


def test_odometer_counter_prefix_and_suffix():
    odo = OdometerTumblerCounter(start_val=0, end_val=500000, prefix="$", suffix=" MRR")
    assert_cairo_draw_safe(odo)


def test_odometer_tumbler_timestamps():
    odo = OdometerTumblerCounter(start_val=100, end_val=500)
    assert_cairo_draw_safe(odo, timestamps=(0.0, 0.5, 1.0, 2.0))


# ============================================================================
# 10. Rubber Stamp Title Slam (>=5 tests)
# ============================================================================

def test_rubber_stamp_defaults():
    stamp = RubberStampTitleSlam("APPROVED")
    assert_cairo_draw_safe(stamp)


def test_rubber_stamp_slam_action():
    stamp = RubberStampTitleSlam("TOP SECRET")
    action = stamp.slam(duration=0.6)
    assert action is not None
    assert_cairo_draw_safe(stamp)


def test_dust_puff_shockwave_node():
    dust = DustPuffShockwave()
    assert_cairo_draw_safe(dust)


def test_rubber_stamp_colors_and_angles():
    stamp = RubberStampTitleSlam("VERIFIED", color=colors.ROSE, rotation_deg=-12.0)
    assert_cairo_draw_safe(stamp)


def test_rubber_stamp_timestamps():
    stamp = RubberStampTitleSlam("FINALIZED")
    assert_cairo_draw_safe(stamp, timestamps=(0.0, 0.2, 0.6, 1.5))


# ============================================================================
# 11. Magnetic Gravity Letters (>=5 tests)
# ============================================================================

def test_magnetic_gravity_defaults():
    magnet = MagneticGravityLetters("MAGNETIC FORCE")
    assert_cairo_draw_safe(magnet)


def test_magnetic_gravity_snap_reassemble():
    magnet = MagneticGravityLetters("ATTRACTION")
    action = magnet.snap_reassemble(duration=1.2)
    assert action is not None
    assert_cairo_draw_safe(magnet)


def test_magnet_pull_reassembly_node():
    pull = MagnetPullReassembly("MAGNET")
    assert_cairo_draw_safe(pull)


def test_magnetic_gravity_scatter_radius():
    magnet = MagneticGravityLetters("SCATTER", scatter_radius=300.0)
    assert_cairo_draw_safe(magnet)


def test_magnetic_gravity_timestamps():
    magnet = MagneticGravityLetters("POLARITY")
    assert_cairo_draw_safe(magnet, timestamps=(0.0, 0.4, 0.8, 1.6))


# ============================================================================
# 12. Prismatic Hologram Text (>=5 tests)
# ============================================================================

def test_hologram_chroma_defaults():
    holo = HologramChromaText("HOLOGRAPHIC")
    assert_cairo_draw_safe(holo)


def test_hologram_chroma_project_emitter():
    holo = HologramChromaText("PROJECTION")
    action = holo.project_emitter(duration=1.5)
    assert action is not None
    assert_cairo_draw_safe(holo)


def test_interference_fringe_lines_node():
    fringe = InterferenceFringeLines("HOLO")
    assert_cairo_draw_safe(fringe)


def test_hologram_chroma_dispersion():
    holo = HologramChromaText("DISPERSION", chromatic_dispersion=4.0)
    assert_cairo_draw_safe(holo)


def test_hologram_chroma_timestamps():
    holo = HologramChromaText("VIRTUAL")
    assert_cairo_draw_safe(holo, timestamps=(0.0, 0.5, 1.0, 2.5))


# ============================================================================
# 13. Phosphor Terminal Typewriter (>=5 tests)
# ============================================================================

def test_terminal_typewriter_defaults():
    term = PhosphorTerminalTypewriter(prompt="user@vibmo:~$ ")
    assert_cairo_draw_safe(term)


def test_terminal_typewriter_action():
    term = PhosphorTerminalTypewriter(prompt=">> ")
    action = term.typewriter("deploy --prod --instant", speed=35.0)
    assert action is not None
    assert_cairo_draw_safe(term)


def test_blinking_block_caret_node():
    caret = BlinkingBlockCaret()
    assert_cairo_draw_safe(caret)


def test_terminal_typewriter_colors():
    term_green = PhosphorTerminalTypewriter(color=colors.EMERALD)
    term_amber = PhosphorTerminalTypewriter(color=colors.AMBER)
    assert_cairo_draw_safe(term_green)
    assert_cairo_draw_safe(term_amber)


def test_terminal_typewriter_timestamps():
    term = PhosphorTerminalTypewriter()
    assert_cairo_draw_safe(term, timestamps=(0.0, 0.5, 1.0, 2.0))


# ============================================================================
# 14. Brush Calligraphy Path Reveal (>=5 tests)
# ============================================================================

def test_brush_calligraphy_defaults():
    brush = BrushCalligraphyPathReveal("Zenith")
    assert_cairo_draw_safe(brush)


def test_brush_calligraphy_draw_strokes():
    brush = BrushCalligraphyPathReveal("Elegance")
    action = brush.draw_strokes(duration=2.0)
    assert action is not None
    assert_cairo_draw_safe(brush)


def test_ink_splatter_bleed_node():
    splatter = InkSplatterBleed((100.0, 100.0))
    assert_cairo_draw_safe(splatter)


def test_brush_calligraphy_ink_flow():
    brush = BrushCalligraphyPathReveal("Ink Flow", ink_bleed=True)
    assert_cairo_draw_safe(brush)


def test_brush_calligraphy_timestamps():
    brush = BrushCalligraphyPathReveal("Harmony")
    assert_cairo_draw_safe(brush, timestamps=(0.0, 0.6, 1.2, 2.0))


# ============================================================================
# 15. Elastic Squash & Stretch Bounce Title (>=5 tests)
# ============================================================================

def test_elastic_squash_bounce_defaults():
    title = ElasticSquashBounceTitle("POW!")
    assert_cairo_draw_safe(title)


def test_elastic_squash_bounce_action():
    title = ElasticSquashBounceTitle("BOOM!")
    action = title.bounce_in(duration=1.0)
    assert action is not None
    assert_cairo_draw_safe(title)


def test_jelly_morph_typography_node():
    jelly = JellyMorphTypography("POW")
    assert_cairo_draw_safe(jelly)


def test_elastic_squash_elasticity_and_bounces():
    title = ElasticSquashBounceTitle("SNAP", elasticity=1.8, bounces=4)
    assert_cairo_draw_safe(title)


def test_elastic_squash_timestamps():
    title = ElasticSquashBounceTitle("DYNAMIC")
    assert_cairo_draw_safe(title, timestamps=(0.0, 0.25, 0.5, 1.0))
