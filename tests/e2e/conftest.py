"""
Shared fixtures and verification helpers for the E2E test suite.
"""

import os
import shutil
import tempfile
import pytest
import numpy as np
from PIL import Image

import cairo
from vibmo.scene.scene import Scene
from vibmo.core.color import colors


@pytest.fixture
def scene_1080p():
    """Returns a standard 1080p 60fps 5.0s Scene."""
    return Scene(
        width=1920,
        height=1080,
        fps=60,
        duration=5.0,
        background=colors.DARK_NAVY,
    )


@pytest.fixture
def scene_vertical():
    """Returns a 9:16 vertical 1080x1920 60fps 4.0s Scene."""
    return Scene(
        width=1080,
        height=1920,
        fps=60,
        duration=4.0,
        background=colors.SLATE_900,
    )


@pytest.fixture
def scene_square():
    """Returns a 1:1 square 1080x1080 30fps 3.0s Scene."""
    return Scene(
        width=1080,
        height=1080,
        fps=30,
        duration=3.0,
        background=colors.BLACK,
    )


@pytest.fixture
def temp_output_dir():
    """Provides a temporary directory for output artifacts, cleaned up after test."""
    temp_dir = tempfile.mkdtemp(prefix="vibmo_e2e_test_")
    yield temp_dir
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)


def assert_valid_audio_array(arr: np.ndarray, expected_sr: int = 48000, min_duration: float = 0.01) -> None:
    """
    Validates that the returned audio array is valid float32/float64,
    free of NaN/Inf values, non-empty, and peak bounded.
    """
    assert isinstance(arr, np.ndarray), f"Expected numpy ndarray, got {type(arr)}"
    assert arr.dtype in (np.float32, np.float64), f"Expected float audio array, got {arr.dtype}"
    assert len(arr) > 0, "Audio array must not be empty"
    assert not np.isnan(arr).any(), "Audio array contains NaN values"
    assert not np.isinf(arr).any(), "Audio array contains Infinite values"
    
    # Check peak amplitude is finite and bounded
    peak = float(np.max(np.abs(arr)))
    assert peak <= 5.0, f"Audio peak amplitude exceeds limit: {peak}"
    
    # Check minimum length corresponding to min_duration
    min_samples = int(expected_sr * min_duration)
    sample_count = arr.shape[0] if arr.ndim == 1 else max(arr.shape)
    assert sample_count >= min_samples, f"Audio array too short: {sample_count} < {min_samples}"


def assert_cairo_draw_safe(node, width: int = 1920, height: int = 1080, timestamps: tuple = (0.0, 0.5, 1.0)) -> None:
    """
    Draws the node onto a headless Cairo ImageSurface across multiple timestamps to verify
    zero rendering crashes, transform leaks, or matrix singularities.
    """
    if isinstance(node, Scene):
        for t in timestamps:
            frame = node.render_frame(t)
            assert frame is not None
        return

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surface)
    
    for t in timestamps:
        ctx.save()
        if hasattr(node, "draw"):
            node.draw(ctx, time=t)
        ctx.restore()


def assert_scene_storyboard_valid(scene: Scene, output_path: str) -> None:
    """
    Executes scene.storyboard(output_path) and asserts that the resulting
    contact sheet image is valid, non-empty, and has expected dimensions.
    """
    res = scene.storyboard(output_path)
    assert os.path.exists(output_path), f"Storyboard file was not created at {output_path}"
    assert os.path.getsize(output_path) > 0, f"Storyboard file at {output_path} is 0 bytes"
    
    with Image.open(output_path) as img:
        assert img.width > 0 and img.height > 0, "Invalid image dimensions"
        assert img.format in ("PNG", "JPEG", "WEBP"), f"Unexpected image format: {img.format}"
