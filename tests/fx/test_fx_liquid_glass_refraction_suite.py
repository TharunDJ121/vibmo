import pytest
import numpy as np
from vibmo.fx.shaders.fx_liquid_glass_refraction_suite import (
    LiquidGlassRefractionShader,
    ChromaticDispersionFilter,
    SpecularRimSheen,
    FrostedBackdropBlur
)

def test_liquid_glass_refraction_no_normal_map_cpu():
    rgba = np.ones((50, 50, 4), dtype=np.uint8) * 128
    filter = LiquidGlassRefractionShader(distortion=10.0, use_gpu=False)
    out = filter.apply(rgba)
    assert out.shape == (50, 50, 4)
    assert out.dtype == np.uint8

def test_liquid_glass_refraction_no_normal_map_gpu():
    rgba = np.ones((50, 50, 4), dtype=np.uint8) * 128
    filter = LiquidGlassRefractionShader(distortion=10.0, use_gpu=True)
    if filter.use_gpu:
        out = filter.apply(rgba)
        assert out.shape == (50, 50, 4)
        assert out.dtype == np.uint8
    else:
        pytest.skip("GPU not available")

def test_liquid_glass_refraction_with_normal_map_cpu():
    rgba = np.ones((50, 50, 4), dtype=np.uint8) * 128
    # Create a dummy normal map (RGB image)
    normal_map = np.ones((50, 50, 3), dtype=np.uint8) * 128
    filter = LiquidGlassRefractionShader(distortion=10.0, normal_map=normal_map, use_gpu=False)
    out = filter.apply(rgba)
    assert out.shape == (50, 50, 4)
    assert out.dtype == np.uint8

def test_liquid_glass_refraction_with_normal_map_gpu():
    rgba = np.ones((50, 50, 4), dtype=np.uint8) * 128
    normal_map = np.ones((50, 50, 3), dtype=np.uint8) * 128
    filter = LiquidGlassRefractionShader(distortion=10.0, normal_map=normal_map, use_gpu=True)
    if filter.use_gpu:
        out = filter.apply(rgba)
        assert out.shape == (50, 50, 4)
        assert out.dtype == np.uint8
    else:
        pytest.skip("GPU not available")

def test_chromatic_dispersion_cpu():
    rgba = np.ones((50, 50, 4), dtype=np.uint8) * 128
    filter = ChromaticDispersionFilter(dispersion=5.0, use_gpu=False)
    out = filter.apply(rgba)
    assert out.shape == (50, 50, 4)
    assert out.dtype == np.uint8

def test_chromatic_dispersion_gpu():
    rgba = np.ones((50, 50, 4), dtype=np.uint8) * 128
    filter = ChromaticDispersionFilter(dispersion=5.0, use_gpu=True)
    if filter.use_gpu:
        out = filter.apply(rgba)
        assert out.shape == (50, 50, 4)
        assert out.dtype == np.uint8
    else:
        pytest.skip("GPU not available")

def test_specular_rim_sheen_cpu():
    rgba = np.zeros((50, 50, 4), dtype=np.uint8)
    # Draw a circle to create edges in alpha
    import cv2
    cv2.circle(rgba, (25, 25), 15, (255, 255, 255, 255), -1)

    filter = SpecularRimSheen(threshold=0.1, intensity=1.0, color=(1.0, 1.0, 1.0), use_gpu=False)
    out = filter.apply(rgba)
    assert out.shape == (50, 50, 4)
    assert out.dtype == np.uint8
    # Test that sheen was applied
    assert np.any(out[:, :, :3] > 0)

def test_specular_rim_sheen_gpu():
    rgba = np.zeros((50, 50, 4), dtype=np.uint8)
    import cv2
    cv2.circle(rgba, (25, 25), 15, (255, 255, 255, 255), -1)

    filter = SpecularRimSheen(threshold=0.1, intensity=1.0, color=(1.0, 1.0, 1.0), use_gpu=True)
    if filter.use_gpu:
        out = filter.apply(rgba)
        assert out.shape == (50, 50, 4)
        assert out.dtype == np.uint8
    else:
        pytest.skip("GPU not available")

def test_frosted_backdrop_blur_cpu():
    rgba = np.random.randint(0, 255, (50, 50, 4), dtype=np.uint8)
    filter = FrostedBackdropBlur(blur_radius=5.0, passes=2, noise_amount=0.1, use_gpu=False)
    out = filter.apply(rgba)
    assert out.shape == (50, 50, 4)
    assert out.dtype == np.uint8

def test_frosted_backdrop_blur_gpu():
    rgba = np.random.randint(0, 255, (50, 50, 4), dtype=np.uint8)
    filter = FrostedBackdropBlur(blur_radius=5.0, passes=2, noise_amount=0.1, use_gpu=True)
    if filter.use_gpu:
        out = filter.apply(rgba)
        assert out.shape == (50, 50, 4)
        assert out.dtype == np.uint8
    else:
        pytest.skip("GPU not available")

def test_filter_blend():
    rgba = np.random.randint(0, 255, (50, 50, 4), dtype=np.uint8)

    filters = [
        LiquidGlassRefractionShader(distortion=5.0, use_gpu=False),
        ChromaticDispersionFilter(dispersion=2.0, use_gpu=False),
        FrostedBackdropBlur(blur_radius=2.0, passes=1, noise_amount=0.05, use_gpu=False)
    ]

    out = rgba.copy()
    for f in filters:
        out = f.apply(out)

    assert out.shape == (50, 50, 4)
    assert out.dtype == np.uint8
