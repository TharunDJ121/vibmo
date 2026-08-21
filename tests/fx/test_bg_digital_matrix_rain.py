import pytest
import cairo
from unittest.mock import MagicMock

from vibmo.fx.backgrounds.bg_digital_matrix_rain import (
    DigitalMatrixRainBackdrop,
    BinaryStreamBackdrop,
    HexCodeColumnBackdrop,
    _CodeColumn
)

def test_code_column_initialization():
    col = _CodeColumn(x=10.0, num_chars=5, speed=100.0, font_size=20.0, charset="01", y_offset=50.0)
    assert col.x == 10.0
    assert len(col.chars) == 5
    assert all(c in "01" for c in col.chars)
    assert col.head_y == 50.0
    assert col.get_char_y(0) == 50.0
    assert col.get_char_y(1) == 30.0

def test_code_column_mutation():
    col = _CodeColumn(x=0.0, num_chars=10, speed=100.0, font_size=20.0, charset="A", y_offset=0.0)
    # Change charset to force noticeable mutation
    col.charset = "B"
    col.mutate_glitch(chance=1.0) # 100% chance
    assert all(c == "B" for c in col.chars)

@pytest.fixture
def mock_ctx():
    return MagicMock()

def test_digital_matrix_rain_initialization(mock_ctx):
    bg = DigitalMatrixRainBackdrop(width=800, height=600, font_size=20)
    assert not bg._initialized
    bg.draw(mock_ctx, time=0.0)
    assert bg._initialized
    # Expected columns: 800 / 20 = 40
    assert len(bg.columns) == 40
    assert mock_ctx.save.called
    assert mock_ctx.restore.called

def test_binary_stream_falling_logic(mock_ctx):
    bg = BinaryStreamBackdrop(width=100, height=100, font_size=10)
    bg.draw(mock_ctx, time=0.0) # Init

    col = bg.columns[0]
    initial_y = col.head_y
    speed = col.speed * bg.speed_multiplier

    # Advance time
    bg.draw(mock_ctx, time=1.0)
    expected_y = initial_y + speed

    # The logic correctly recycles if it goes offscreen, so we bypass checking the EXACT expected_y if it recycled
    if expected_y - (col.num_chars * col.font_size) > bg.h:
        # It recycled
        assert col.head_y <= 0.0
    else:
        assert abs(col.head_y - expected_y) < 1e-5

def test_hex_code_drawing(mock_ctx):
    bg = HexCodeColumnBackdrop(width=200, height=200, font_size=20)
    bg.draw(mock_ctx, time=0.0)

    # Hex columns are wider, so fewer of them: 200 / (20 * 2) = 5
    assert len(bg.columns) == 5
    assert mock_ctx.show_text.called

def test_column_recycling(mock_ctx):
    bg = DigitalMatrixRainBackdrop(width=100, height=100, font_size=10)
    bg.draw(mock_ctx, time=0.0)

    col = bg.columns[0]
    # Move column way past the bottom
    col.head_y = 1000.0
    col.last_update = 0.0

    bg.draw(mock_ctx, time=1.0)
    # It should have been recycled to a negative or zero Y value
    assert col.head_y <= 100.0
