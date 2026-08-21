import pytest
import numpy as np
import cairo
from vibmo.fx.backgrounds.bg_retro_crt_scanlines import (
    CrtPhosphorScanlineBackdrop,
    TVSignalNoiseStatic,
    VcrBlueScreenGlitch,
)
from vibmo.core.color import Color

def test_crt_phosphor_scanline_backdrop():
    # Test initialization
    backdrop = CrtPhosphorScanlineBackdrop(width=800, height=600, scanline_spacing=5.0)
    assert backdrop.width == 800
    assert backdrop.height == 600
    assert backdrop.scanline_spacing == 5.0
    assert isinstance(backdrop.base_color, Color)
    assert isinstance(backdrop.scanline_color, Color)

    # Test drawing at different times (temporal output should not be static)
    surface1 = cairo.ImageSurface(cairo.FORMAT_ARGB32, 800, 600)
    ctx1 = cairo.Context(surface1)
    backdrop.draw(ctx1, time=0.0)

    surface2 = cairo.ImageSurface(cairo.FORMAT_ARGB32, 800, 600)
    ctx2 = cairo.Context(surface2)
    backdrop.draw(ctx2, time=1.0)

    # We could theoretically extract surface data and compare but
    # it's easiest to verify there's output and it didn't crash.
    # To check temporal output changes, we can look at the buffer data.
    buf1 = surface1.get_data()
    buf2 = surface2.get_data()
    assert buf1 != buf2, "Temporal output is static at t=0 and t=1"


def test_tv_signal_noise_static():
    node = TVSignalNoiseStatic(width=320, height=240, coarseness=2, hum_frequency=30.0)
    assert node.width == 320
    assert node.height == 240
    assert node.coarseness == 2

    surface1 = cairo.ImageSurface(cairo.FORMAT_ARGB32, 320, 240)
    ctx1 = cairo.Context(surface1)
    node.draw(ctx1, time=0.0)

    surface2 = cairo.ImageSurface(cairo.FORMAT_ARGB32, 320, 240)
    ctx2 = cairo.Context(surface2)
    node.draw(ctx2, time=0.1)

    buf1 = surface1.get_data()
    buf2 = surface2.get_data()
    assert buf1 != buf2, "Noise output should be different across time"

def test_vcr_blue_screen_glitch():
    node = VcrBlueScreenGlitch(width=640, height=480, blue_color="#0000FF", show_play_text=True)
    assert node.width == 640
    assert node.height == 480
    assert node.blue_color.r == 0.0
    assert node.blue_color.g == 0.0
    assert node.blue_color.b == 1.0

    surface1 = cairo.ImageSurface(cairo.FORMAT_ARGB32, 640, 480)
    ctx1 = cairo.Context(surface1)
    node.draw(ctx1, time=0.0)

    surface2 = cairo.ImageSurface(cairo.FORMAT_ARGB32, 640, 480)
    ctx2 = cairo.Context(surface2)
    node.draw(ctx2, time=1.0)

    buf1 = surface1.get_data()
    buf2 = surface2.get_data()

    # VCR tracking noise should be different
    assert buf1 != buf2, "Glitch tracking noise output should be temporal"
