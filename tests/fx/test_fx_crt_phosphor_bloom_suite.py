import pytest
import numpy as np
from vibmo.fx.shaders.fx_crt_phosphor_bloom_suite import (
    CrtPhosphorBloomShader,
    CurvedGlassBarrelDistortion,
    PhosphorPersistenceTrail,
    HorizontalRGBBeamBleed
)

def test_crt_phosphor_bloom_shader_cpu():
    rgba = np.ones((100, 100, 4), dtype=np.uint8) * 128
    filter = CrtPhosphorBloomShader(intensity=0.5, radius=5.0, use_gpu=False)
    out = filter.apply(rgba)
    assert out.shape == (100, 100, 4)
    assert out.dtype == np.uint8

def test_crt_phosphor_bloom_shader_gpu():
    rgba = np.ones((100, 100, 4), dtype=np.uint8) * 128
    filter = CrtPhosphorBloomShader(intensity=0.5, radius=5.0, use_gpu=True)
    if filter.use_gpu:
        out = filter.apply(rgba)
        assert out.shape == (100, 100, 4)
        assert out.dtype == np.uint8
    else:
        pytest.skip("GPU not available")

def test_curved_glass_barrel_distortion_cpu():
    rgba = np.ones((100, 100, 4), dtype=np.uint8) * 128
    filter = CurvedGlassBarrelDistortion(amount=0.1, corner_darkness=0.3, use_gpu=False)
    out = filter.apply(rgba)
    assert out.shape == (100, 100, 4)
    assert out.dtype == np.uint8

def test_curved_glass_barrel_distortion_gpu():
    rgba = np.ones((100, 100, 4), dtype=np.uint8) * 128
    filter = CurvedGlassBarrelDistortion(amount=0.1, corner_darkness=0.3, use_gpu=True)
    if filter.use_gpu:
        out = filter.apply(rgba)
        assert out.shape == (100, 100, 4)
        assert out.dtype == np.uint8
    else:
        pytest.skip("GPU not available")

def test_phosphor_persistence_trail_cpu():
    rgba1 = np.ones((100, 100, 4), dtype=np.uint8) * 128
    filter = PhosphorPersistenceTrail(decay=0.9, use_gpu=False)
    out1 = filter.apply(rgba1)
    assert out1.shape == (100, 100, 4)
    assert out1.dtype == np.uint8
    assert np.array_equal(out1, rgba1)
    
    rgba2 = np.ones((100, 100, 4), dtype=np.uint8) * 0
    out2 = filter.apply(rgba2)
    assert out2.shape == (100, 100, 4)
    assert out2.dtype == np.uint8
    # Test decay effect
    assert np.any(out2[:, :, :3] > 0)

def test_phosphor_persistence_trail_gpu():
    rgba1 = np.ones((100, 100, 4), dtype=np.uint8) * 128
    filter = PhosphorPersistenceTrail(decay=0.9, use_gpu=True)
    if filter.use_gpu:
        out1 = filter.apply(rgba1)
        assert out1.shape == (100, 100, 4)
        assert out1.dtype == np.uint8
        
        rgba2 = np.ones((100, 100, 4), dtype=np.uint8) * 0
        out2 = filter.apply(rgba2)
        assert out2.shape == (100, 100, 4)
        assert out2.dtype == np.uint8
        # Test decay effect
        assert np.any(out2[:, :, :3] > 0)
    else:
        pytest.skip("GPU not available")

def test_horizontal_rgb_beam_bleed_cpu():
    rgba = np.ones((100, 100, 4), dtype=np.uint8) * 128
    filter = HorizontalRGBBeamBleed(offset_r=-2.0, offset_g=0.0, offset_b=2.0, use_gpu=False)
    out = filter.apply(rgba)
    assert out.shape == (100, 100, 4)
    assert out.dtype == np.uint8

def test_horizontal_rgb_beam_bleed_gpu():
    rgba = np.ones((100, 100, 4), dtype=np.uint8) * 128
    filter = HorizontalRGBBeamBleed(offset_r=-2.0, offset_g=0.0, offset_b=2.0, use_gpu=True)
    if filter.use_gpu:
        out = filter.apply(rgba)
        assert out.shape == (100, 100, 4)
        assert out.dtype == np.uint8
    else:
        pytest.skip("GPU not available")
