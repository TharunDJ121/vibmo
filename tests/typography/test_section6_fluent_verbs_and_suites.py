import pytest
import cairo
import numpy as np

from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D
from vibmo.typography.kinetic import (
    GlitchDecryptorText, HexMatrixCycle,
    LiquidWaveText, SubmergedTextRefraction,
    IsometricExtruded3DText, BevelGleamLight,
    RealisticNeonStrobeSign, BallastFlickerFailure,
    ParticleFlameText, DisintegratingEmbers,
    SplitFlapAirportBoard, MechanicalFlapTile,
    MatrixRainTypography, PhosphorTrailDecay,
    SlitScanVideoSynthText, ChromaWarpWave,
    OdometerTumblerCounter, VerticalRollingGlyphs,
    RubberStampTitleSlam, DustPuffShockwave,
    MagneticGravityLetters, MagnetPullReassembly,
    HologramChromaText, InterferenceFringeLines,
    PhosphorTerminalTypewriter, BlinkingBlockCaret,
    BrushCalligraphyPathReveal, InkSplatterBleed,
    ElasticSquashBounceTitle, JellyMorphTypography,
)


@pytest.fixture
def cairo_ctx():
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1920, 1080)
    return cairo.Context(surf)


def test_suite_01_glitch_decryptor(cairo_ctx):
    text = GlitchDecryptorText("QUANTUM SECURE", font_size=48.0, color=colors.CYAN)
    action = text.decrypt(duration=1.8)
    assert action is not None
    action.apply_at(0.0)

    text.draw(cairo_ctx, 0.0)
    text.draw(cairo_ctx, 0.9)
    text.draw(cairo_ctx, 1.8)

    cycle = HexMatrixCycle(target_char="A", font_size=32.0)
    cycle.draw(cairo_ctx, 0.5)


def test_suite_02_liquid_wave_refraction(cairo_ctx):
    wave_text = LiquidWaveText("FLUID DYNAMICS", font_size=36.0, amplitude=12.0)
    action = wave_text.ripple_reveal(duration=1.8)
    assert action is not None
    action.apply_at(0.0)

    wave_text.draw(cairo_ctx, 0.0)
    wave_text.draw(cairo_ctx, 0.9)
    wave_text.draw(cairo_ctx, 1.8)

    submerged = SubmergedTextRefraction("SUBMERGED", font_size=32.0)
    submerged.draw(cairo_ctx, 1.0)


def test_suite_03_isometric_3d_extruded(cairo_ctx):
    iso = IsometricExtruded3DText("FUTURE TECH", depth=35, font_size=52.0)
    action = iso.gleam(duration=1.2)
    assert action is not None
    action.apply_at(0.0)

    iso.draw(cairo_ctx, 0.0)
    iso.draw(cairo_ctx, 0.6)
    iso.draw(cairo_ctx, 1.2)

    bevel = BevelGleamLight("BEVEL", font_size=32.0)
    bevel_act = bevel.gleam(duration=1.0)
    assert bevel_act is not None
    bevel.draw(cairo_ctx, 0.5)


def test_suite_04_realistic_neon_strobe(cairo_ctx):
    neon = RealisticNeonStrobeSign("OPEN 24/7", color=colors.CYAN, font_size=64.0)
    actions = neon.ignite(duration=1.0, delay=0.1)
    assert actions is not None

    neon.draw(cairo_ctx, 0.0)
    neon.draw(cairo_ctx, 0.5)
    neon.draw(cairo_ctx, 1.1)

    ballast = BallastFlickerFailure()
    intensity = ballast.get_flicker_intensity(0.5)
    assert 0.0 <= intensity <= 1.0


def test_suite_05_particle_flame_embers(cairo_ctx):
    fire = ParticleFlameText("BURNING PASSION", font_size=48.0)
    action = fire.disintegrate(duration=3.0)
    assert action is not None
    action.apply_at(0.0)

    fire.draw(cairo_ctx, 0.0)
    fire.draw(cairo_ctx, 1.5)
    fire.draw(cairo_ctx, 3.0)

    embers = DisintegratingEmbers("EMBERS", font_size=32.0)
    emb_act = embers.disintegrate(duration=2.0)
    assert emb_act is not None
    embers.draw(cairo_ctx, 1.0)


def test_suite_06_split_flap_board(cairo_ctx):
    board = SplitFlapAirportBoard(rows=2, cols=14)
    action = board.flip_to(["SAN FRANCISCO", "GATE B24"], duration=1.5)
    assert action is not None
    action.apply_at(0.0)

    board.draw(cairo_ctx, 0.0)
    board.draw(cairo_ctx, 0.75)
    board.draw(cairo_ctx, 1.5)

    tile = MechanicalFlapTile(width=60.0, height=90.0)
    tile.set_state("A", "B", 0.4)
    tile.draw(cairo_ctx, 0.0)


def test_suite_07_matrix_code_rain(cairo_ctx):
    matrix_title = MatrixRainTypography("THE CONSTRUCT", font_size=36.0)
    action = matrix_title.consolidate(duration=2.0)
    assert action is not None
    action.apply_at(0.0)

    matrix_title.draw(cairo_ctx, 0.0)
    matrix_title.draw(cairo_ctx, 1.0)
    matrix_title.draw(cairo_ctx, 2.0)

    trail = PhosphorTrailDecay("MATRIX", font_size=28.0)
    trail.draw(cairo_ctx, 1.0)


def test_suite_08_slit_scan_video_synth(cairo_ctx):
    synth = SlitScanVideoSynthText("SYNTHESIZER", font_size=48.0)
    action = synth.warp_scan(duration=2.0)
    assert action is not None
    action.apply_at(0.0)

    synth.draw(cairo_ctx, 0.0)
    synth.draw(cairo_ctx, 1.0)
    synth.draw(cairo_ctx, 2.0)

    wave = ChromaWarpWave("WARP", font_size=32.0)
    wave.draw(cairo_ctx, 0.5)


def test_suite_09_mechanical_odometer_tumbler(cairo_ctx):
    odo = OdometerTumblerCounter(start_val=0, end_val=9999, font_size=36.0)
    action = odo.roll_to(8420, duration=2.0)
    assert action is not None
    action.apply_at(0.0)

    odo.draw(cairo_ctx, 0.0)
    odo.draw(cairo_ctx, 1.0)
    odo.draw(cairo_ctx, 2.0)

    wheel = VerticalRollingGlyphs(font_size=32.0)
    w_act = wheel.roll_to(7.0, duration=1.0)
    assert w_act is not None
    wheel.draw(cairo_ctx, 0.5)


def test_suite_10_rubber_stamp_slam(cairo_ctx):
    stamp = RubberStampTitleSlam("APPROVED", color=colors.ROSE, font_size=64.0)
    action = stamp.slam(duration=0.6)
    assert action is not None
    action.apply_at(0.0)

    stamp.draw(cairo_ctx, 0.0)
    stamp.draw(cairo_ctx, 0.3)
    stamp.draw(cairo_ctx, 0.6)

    dust = DustPuffShockwave(color=colors.GRAY)
    dust.burst(duration=0.5)
    dust.draw(cairo_ctx, 0.25)


def test_suite_11_magnetic_gravity_snap(cairo_ctx):
    magnet = MagneticGravityLetters("MAGNETIC FORCE", font_size=48.0)
    action = magnet.snap_reassemble(duration=1.5)
    assert action is not None
    action.apply_at(0.0)

    magnet.draw(cairo_ctx, 0.0)
    magnet.draw(cairo_ctx, 0.75)
    magnet.draw(cairo_ctx, 1.5)

    pull = MagnetPullReassembly("ATTRACT", font_size=32.0)
    p_act = pull.snap_reassemble(duration=1.0)
    assert p_act is not None
    pull.draw(cairo_ctx, 0.5)


def test_suite_12_prismatic_hologram_chroma(cairo_ctx):
    holo = HologramChromaText("HOLOGRAPHIC", font_size=48.0)
    action = holo.project_emitter(duration=1.5)
    assert action is not None
    action.apply_at(0.0)

    holo.draw(cairo_ctx, 0.0)
    holo.draw(cairo_ctx, 0.75)
    holo.draw(cairo_ctx, 1.5)

    fringes = InterferenceFringeLines("OPTICAL", font_size=32.0)
    fringes.draw(cairo_ctx, 1.0)


def test_suite_13_phosphor_terminal_typewriter(cairo_ctx):
    term = PhosphorTerminalTypewriter(prompt="user@vibmo:~$ ", font_size=24.0)
    action = term.typewriter("deploy --prod", speed=30.0)
    assert action is not None
    action.apply_at(0.0)

    term.draw(cairo_ctx, 0.0)
    term.draw(cairo_ctx, 0.2)
    term.draw(cairo_ctx, 1.0)

    caret = BlinkingBlockCaret(blink_rate=2.0)
    caret.draw(cairo_ctx, 0.1)


def test_suite_14_brush_calligraphy_reveal(cairo_ctx):
    brush = BrushCalligraphyPathReveal("Zenith", font_size=56.0, color=colors.BLACK)
    action = brush.draw_strokes(duration=2.0)
    assert action is not None
    action.apply_at(0.0)

    brush.draw(cairo_ctx, 0.0)
    brush.draw(cairo_ctx, 1.0)
    brush.draw(cairo_ctx, 2.0)

    splatter = InkSplatterBleed(center=(100, 100), num_splatters=8)
    splatter.draw(cairo_ctx, 0.5)


def test_suite_15_elastic_squash_bounce(cairo_ctx):
    comic = ElasticSquashBounceTitle("POW!", font_size=72.0)
    action = comic.bounce_in(duration=0.8)
    assert action is not None
    action.apply_at(0.0)

    comic.draw(cairo_ctx, 0.0)
    comic.draw(cairo_ctx, 0.4)
    comic.draw(cairo_ctx, 0.8)

    jelly = JellyMorphTypography("JELLY", font_size=48.0)
    j_act = jelly.bounce_in(duration=0.8)
    assert j_act is not None
    jelly.draw(cairo_ctx, 0.4)
