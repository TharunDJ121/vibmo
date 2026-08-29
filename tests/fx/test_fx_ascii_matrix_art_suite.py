import numpy as np
import pytest
from vibmo.fx.shaders.fx_ascii_matrix_art_suite import (
    AsciiMatrixArtShader,
    TerminalColorPaletteFilter,
    DynamicCharResolutionGrid,
    EdgeContourAsciiOverlay,
)

@pytest.fixture
def sample_frame():
    # 200x200 RGBA frame with gradient
    frame = np.zeros((200, 200, 4), dtype=np.uint8)
    frame[:, :, 0] = 128  # R
    frame[:, :, 1] = 64   # G
    frame[:, :, 2] = 200  # B
    frame[:, :, 3] = 255  # A
    return frame

def test_ascii_matrix_art_shader(sample_frame):
    # Add varying luminance
    sample_frame[0:100, :, :3] = 0
    sample_frame[100:200, :, :3] = 255

    fx = AsciiMatrixArtShader(char_set="@%#*+=-:. ", grid_size=20)
    out = fx.apply(sample_frame.copy(), time=0.0)

    assert out.shape == sample_frame.shape
    assert out.dtype == np.uint8
    # Should be predominantly matrix green on black
    # But since text coverage varies, we just check it modified the frame
    assert not np.array_equal(out, sample_frame)

def test_terminal_color_palette_filter(sample_frame):
    # Matrix green
    fx_matrix = TerminalColorPaletteFilter(palette="matrix")
    out_matrix = fx_matrix.apply(sample_frame.copy(), time=0.0)

    assert out_matrix.shape == sample_frame.shape

    # Check that red and blue are zero, and green is non-zero
    assert np.max(out_matrix[:, :, 0]) == 0
    assert np.max(out_matrix[:, :, 2]) == 0
    assert np.max(out_matrix[:, :, 1]) > 0

    # Cyberpunk magenta
    fx_magenta = TerminalColorPaletteFilter(palette="magenta")
    out_magenta = fx_magenta.apply(sample_frame.copy(), time=0.0)

    assert np.max(out_magenta[:, :, 1]) == 0  # Green should be zero
    assert np.max(out_magenta[:, :, 0]) > 0
    assert np.max(out_magenta[:, :, 2]) > 0

def test_dynamic_char_resolution_grid(sample_frame):
    fx = DynamicCharResolutionGrid(cols=10, rows=10)
    out = fx.apply(sample_frame.copy(), time=0.0)

    assert out.shape == sample_frame.shape

    # Each 20x20 block should be uniform since 200/10 = 20
    assert np.array_equal(out[0:20, 0:20, :], out[0, 0, :].reshape(1, 1, 4).repeat(20, 0).repeat(20, 1))

def test_edge_contour_ascii_overlay(sample_frame):
    # Create a high contrast edge
    sample_frame[50:150, 50:150, :3] = 255

    fx = EdgeContourAsciiOverlay(threshold=0.1, char="#", grid_size=10, intensity=1.0)
    out = fx.apply(sample_frame.copy(), time=0.0)

    assert out.shape == sample_frame.shape
    assert not np.array_equal(out, sample_frame)
