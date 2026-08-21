"""
Unit tests for visual effects, post-processing filters, and drop shadows.
"""

import numpy as np
import pytest
from vibmo.fx.filters import (
    FilmGrain,
    Vignette,
    Bloom,
    Glow,
    ChromaticAberration,
    DepthOfField,
    TiltShift,
    Dither,
)
from vibmo.spatial.shadows import DropShadow
from vibmo.core.color import Color, colors


@pytest.fixture
def sample_frame():
    # 200x200 RGBA frame with gradient
    frame = np.zeros((200, 200, 4), dtype=np.uint8)
    frame[:, :, 0] = 128  # R
    frame[:, :, 1] = 64   # G
    frame[:, :, 2] = 200  # B
    frame[:, :, 3] = 255  # A
    return frame


def test_film_grain(sample_frame):
    fx = FilmGrain(amount=0.05)
    out = fx.apply(sample_frame.copy(), time=0.0)
    assert out.shape == sample_frame.shape
    assert out.dtype == np.uint8
    assert not np.array_equal(out, sample_frame)


def test_vignette(sample_frame):
    fx = Vignette(intensity=0.5, radius=0.8)
    out = fx.apply(sample_frame.copy(), time=0.0)
    # Corners should be darker than center
    center_val = int(out[100, 100, 0])
    corner_val = int(out[10, 10, 0])
    assert corner_val <= center_val


def test_bloom_and_glow(sample_frame):
    # Add bright specular spot
    sample_frame[80:120, 80:120, :3] = 255
    bloom = Bloom(threshold=0.6, intensity=0.5)
    out_bloom = bloom.apply(sample_frame.copy(), time=0.0)
    assert out_bloom.shape == sample_frame.shape

    glow = Glow(intensity=0.8)
    out_glow = glow.apply(sample_frame.copy(), time=0.0)
    assert out_glow.shape == sample_frame.shape


def test_chromatic_aberration(sample_frame):
    fx = ChromaticAberration(offset=4.0)
    out = fx.apply(sample_frame.copy(), time=0.0)
    assert out.shape == sample_frame.shape


def test_depth_of_field_and_tilt_shift(sample_frame):
    dof = DepthOfField(focus_y=0.5, focus_width=0.2, blur_radius=12.0)
    out_dof = dof.apply(sample_frame.copy(), time=0.0)
    assert out_dof.shape == sample_frame.shape

    ts = TiltShift(focus_y=0.5, blur_radius=16.0)
    out_ts = ts.apply(sample_frame.copy(), time=0.0)
    assert out_ts.shape == sample_frame.shape


def test_dither(sample_frame):
    dither = Dither(amount=1.5)
    out = dither.apply(sample_frame.copy(), time=0.0)
    assert out.shape == sample_frame.shape


def test_drop_shadow_presets():
    elevated = DropShadow.elevated(blur=30.0)
    assert elevated.blur == 30.0
    assert elevated.offset.y == 12.0

    glow_shadow = DropShadow.glow(colors.CYAN, blur=40.0)
    assert glow_shadow.blur == 40.0


def test_color_correction_primary_grading(sample_frame):
    from vibmo.fx.filters import ColorCorrection
    cc = ColorCorrection(
        exposure=0.5,
        contrast=1.2,
        saturation=1.4,
        temperature=0.2,
        lift=(0.02, 0.0, 0.05),
        gamma=(1.1, 1.0, 0.9),
        gain=(1.2, 1.1, 1.0),
    )
    out = cc.apply(sample_frame.copy(), time=0.0)
    assert out.shape == sample_frame.shape
    assert out.dtype == np.uint8
    assert not np.array_equal(out, sample_frame)


def test_lens_flare_anamorphic_streak(sample_frame):
    from vibmo.fx.filters import LensFlare
    flare = LensFlare(position=(0.5, 0.5), intensity=1.0, streak_length=0.9, num_ghosts=5)
    out = flare.apply(sample_frame.copy(), time=0.0)
    assert out.shape == sample_frame.shape
    # Center should be brighter due to flare core
    assert np.mean(out[90:110, 90:110, :3]) >= np.mean(sample_frame[90:110, 90:110, :3])


def test_god_rays_volumetric_shafts(sample_frame):
    from vibmo.fx.filters import GodRays
    # Add bright emitter
    sample_frame[20:60, 80:120, :3] = 255
    gr = GodRays(light_position=(0.5, 0.2), decay=0.95, density=0.8, exposure=0.7)
    out = gr.apply(sample_frame.copy(), time=0.0)
    assert out.shape == sample_frame.shape
    assert out.dtype == np.uint8


def test_glitch_digital_corruption(sample_frame):
    from vibmo.fx.filters import Glitch
    glitch = Glitch(intensity=0.8, slice_count=8, rgb_split=8.0, scanlines=True)
    out = glitch.apply(sample_frame.copy(), time=1.5)
    assert out.shape == sample_frame.shape
    assert not np.array_equal(out, sample_frame)


def test_pixelate_mosaic_filter(sample_frame):
    from vibmo.fx.filters import Pixelate
    pix = Pixelate(cell_size=16.0)
    out = pix.apply(sample_frame.copy(), time=0.0)
    assert out.shape == sample_frame.shape
    # Blocks of 16x16 will have identical pixel values
    assert np.array_equal(out[0:16, 0:16, :], out[0, 0, :].reshape(1, 1, 4).repeat(16, 0).repeat(16, 1))


def test_radial_and_zoom_blur(sample_frame):
    from vibmo.fx.filters import RadialBlur, ZoomBlur
    r_blur = RadialBlur(center=(0.5, 0.5), amount=0.05, samples=6)
    out_r = r_blur.apply(sample_frame.copy(), time=0.0)
    assert out_r.shape == sample_frame.shape

    z_blur = ZoomBlur(center=(0.5, 0.5), amount=0.08, samples=6)
    out_z = z_blur.apply(sample_frame.copy(), time=0.0)
    assert out_z.shape == sample_frame.shape


def test_edge_glow_neon_cyber(sample_frame):
    from vibmo.fx.filters import EdgeGlow
    # Add high contrast box
    sample_frame[50:150, 50:150, :3] = 255
    eg = EdgeGlow(threshold=0.1, intensity=1.5, color=colors.CYAN)
    out = eg.apply(sample_frame.copy(), time=0.0)
    assert out.shape == sample_frame.shape


def test_halftone_and_duotone(sample_frame):
    from vibmo.fx.filters import Halftone, Duotone
    ht = Halftone(dot_size=8.0, contrast=1.5)
    out_ht = ht.apply(sample_frame.copy(), time=0.0)
    assert out_ht.shape == sample_frame.shape

    dt = Duotone(color_dark="#0f172a", color_light="#06b6d4")
    out_dt = dt.apply(sample_frame.copy(), time=0.0)
    assert out_dt.shape == sample_frame.shape


