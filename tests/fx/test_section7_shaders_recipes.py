import pytest
import numpy as np
from motio.agent_api import (
    Scene,
    colors,
    CrtPhosphorBloomShader,
    CurvedGlassBarrelDistortion,
    VhsTapeTrackingShader,
    HeadSwitchJitter,
    HeadSwitchingJitterLine,
    AnamorphicStreakFlare,
    HorizontalBlueStreak,
    AnamorphicStreakFlareShader,
    LiquidGlassRefractionFilter,
    LiquidGlassRefractionShader,
    ChromaticDispersion,
    ChromaticDispersionFilter,
    AsciiMatrixArtFilter,
    AsciiMatrixArtShader,
    LuminescenceGrid,
    DynamicCharResolutionGrid,
)


@pytest.fixture
def sample_frame():
    # 200x300 RGBA frame with varied colors and high luminance regions
    h, w = 200, 300
    frame = np.zeros((h, w, 4), dtype=np.uint8)
    frame[:, :, 3] = 255
    # Color gradients & highlights
    frame[:100, :150, 0] = 240 # Red region
    frame[100:, 150:, 1] = 255 # Green region
    frame[50:150, 75:225, 2] = 230 # Blue region
    frame[80:120, 130:170, :3] = 255 # Bright white highlight
    return frame


def test_crt_phosphor_bloom_shader_recipe(sample_frame):
    """Test AGENTS.md recipe: CrtPhosphorBloomShader(bloom=1.4, aperture_grille=True)."""
    shader = CrtPhosphorBloomShader(bloom=1.4, aperture_grille=True, use_gpu=False)
    out = shader.apply(sample_frame.copy(), time=0.5)
    assert out.shape == sample_frame.shape
    assert out.dtype == np.uint8

    alias_filter = CurvedGlassBarrelDistortion(distortion=0.15, use_gpu=False)
    out_alias = alias_filter.apply(sample_frame.copy(), time=0.5)
    assert out_alias.shape == sample_frame.shape
    assert out_alias.dtype == np.uint8


def test_vhs_tape_tracking_shader_recipe(sample_frame):
    """Test AGENTS.md recipe: VhsTapeTrackingShader(noise=0.15, tracking_error=0.08)."""
    shader = VhsTapeTrackingShader(noise=0.15, tracking_error=0.08, use_gpu=False)
    out = shader.apply(sample_frame.copy(), time=0.5)
    assert out.shape == sample_frame.shape
    assert out.dtype == np.uint8

    alias_filter = HeadSwitchJitter(line_height=0.05, shift_amount=0.02, use_gpu=False)
    out_alias = alias_filter.apply(sample_frame.copy(), time=0.5)
    assert out_alias.shape == sample_frame.shape
    assert out_alias.dtype == np.uint8


def test_anamorphic_streak_flare_recipe(sample_frame):
    """Test AGENTS.md recipe: AnamorphicStreakFlare(threshold=0.8, streak_length=600)."""
    shader = AnamorphicStreakFlare(threshold=0.8, streak_length=600)
    out = shader.apply(sample_frame.copy(), time=0.5)
    assert out.shape == sample_frame.shape
    assert out.dtype == np.uint8

    alias_filter = HorizontalBlueStreak(threshold=0.75, streak_length=400)
    out_alias = alias_filter.apply(sample_frame.copy(), time=0.5)
    assert out_alias.shape == sample_frame.shape
    assert out_alias.dtype == np.uint8


def test_liquid_glass_refraction_recipe(sample_frame):
    """Test AGENTS.md recipe: LiquidGlassRefractionFilter(refraction=0.3)."""
    shader = LiquidGlassRefractionFilter(refraction=0.3, use_gpu=False)
    out = shader.apply(sample_frame.copy(), time=0.5)
    assert out.shape == sample_frame.shape
    assert out.dtype == np.uint8

    alias_filter = ChromaticDispersion(dispersion=4.0, use_gpu=False)
    out_alias = alias_filter.apply(sample_frame.copy(), time=0.5)
    assert out_alias.shape == sample_frame.shape
    assert out_alias.dtype == np.uint8


def test_ascii_matrix_art_filter_recipe(sample_frame):
    """Test AGENTS.md recipe: AsciiMatrixArtFilter(char_size=12, green_phosphor=True)."""
    shader = AsciiMatrixArtFilter(char_size=12, green_phosphor=True)
    out = shader.apply(sample_frame.copy(), time=0.5)
    assert out.shape == sample_frame.shape
    assert out.dtype == np.uint8

    grid_filter = LuminescenceGrid(cell_size=16)
    out_grid = grid_filter.apply(sample_frame.copy(), time=0.5)
    assert out_grid.shape == sample_frame.shape
    assert out_grid.dtype == np.uint8


def test_scene_add_post_fx_integration():
    """Verifies that all 5 shaders can be added to a Scene via scene.add_post_fx."""
    scene = Scene(width=640, height=360, fps=30, duration=2.0, background=colors.DARK_NAVY)

    scene.add_post_fx(
        CrtPhosphorBloomShader(bloom=1.4, aperture_grille=True, use_gpu=False),
        VhsTapeTrackingShader(noise=0.15, tracking_error=0.08, use_gpu=False),
        AnamorphicStreakFlare(threshold=0.8, streak_length=600),
        LiquidGlassRefractionFilter(refraction=0.3, use_gpu=False),
        AsciiMatrixArtFilter(char_size=12, green_phosphor=True),
    )

    assert len(scene.post_fx) == 5
    frame = scene.render_frame(0.5)
    assert isinstance(frame, np.ndarray)
    assert frame.shape == (360, 640, 4)
