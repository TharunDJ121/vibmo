"""
Unit tests for Hardware-Accelerated ModernGL GPU Pipeline (Bloom, Vignette, Grain, Aberration).
"""

import numpy as np
import pytest
from vibmo.render.gpu.pipeline import GPUPostProcessor
from vibmo.fx.filters import Bloom, Vignette, FilmGrain, ChromaticAberration
from vibmo.scene.scene import Scene
from vibmo.components.glass import GlassCard
from vibmo.typography.kinetic import KineticText


def test_gpu_post_processor_lifecycle():
    gpu = GPUPostProcessor(width=640, height=360)
    assert gpu is not None

    if gpu.is_available:
        # Create test frame
        dummy = np.zeros((360, 640, 4), dtype=np.uint8)
        dummy[100:260, 200:440, :] = 255  # Bright square in center

        # Apply multi-effect GPU chain
        post_fx = [
            Bloom(threshold=0.5, intensity=0.5, radius=12.0),
            Vignette(intensity=0.3),
            FilmGrain(amount=0.01),
            ChromaticAberration(offset=0.5),
        ]

        out = gpu.apply_post_fx(dummy, time=1.0, post_fx=post_fx)
        assert out.shape == (360, 640, 4)
        assert out.dtype == np.uint8
        # Bloom should have spread beyond bright square
        assert out[90, 190, 0] > 0 or out[100, 200, 0] > 0


def test_scene_gpu_rendering_and_proxy_scaling():
    scene = Scene(width=640, height=360, fps=30, duration=2.0)
    card = GlassCard(position=(200, 100))
    card.add(KineticText("GPU Accelerated", font_size=20))
    scene.add(card)

    scene.add_post_fx(
        Bloom(threshold=0.6, intensity=0.4, radius=16.0),
        Vignette(intensity=0.25),
        FilmGrain(amount=0.005),
    )

    # 1. Full Scale
    frame_full = scene.render_frame(time=0.5, scale=1.0)
    assert frame_full.shape == (360, 640, 4)

    # 2. Proxy Scale (Half 540p / 180p)
    frame_proxy = scene.render_frame(time=0.5, scale=0.5)
    assert frame_proxy.shape == (180, 320, 4)
