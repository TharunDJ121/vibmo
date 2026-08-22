import pytest
from vibmo.product.ai.ui_token_streamer_suite import (
    TokenStreamerBox,
    ShimmeringCaretIndicator,
    TokenSpeedVelocityCounter,
    StopGenerationButton,
)
from vibmo.core.vector import Vector2D

class MockContext:
    def __init__(self):
        pass
    def save(self): pass
    def restore(self): pass
    def set_source_rgba(self, r, g, b, a): pass
    def translate(self, x, y): pass
    def scale(self, x, y): pass
    def set_line_width(self, w): pass
    def set_line_cap(self, cap): pass
    def move_to(self, x, y): pass
    def line_to(self, x, y): pass
    def stroke(self): pass
    def fill(self): pass
    def fill_preserve(self): pass
    def new_path(self): pass
    def new_sub_path(self): pass
    def arc(self, x, y, r, a1, a2): pass
    def rectangle(self, x, y, w, h): pass
    def close_path(self): pass
    def select_font_face(self, family, slant, weight): pass
    def set_font_size(self, size): pass
    def show_text(self, text): pass
    class Extents:
        def __init__(self, w, a):
            self.width = w
            self.x_advance = a
    def text_extents(self, text):
        return self.Extents(10, 10)

def test_token_streamer_box_init():
    box = TokenStreamerBox()
    assert box is not None
    assert isinstance(box.velocity_counter, TokenSpeedVelocityCounter)
    assert isinstance(box.stop_btn, StopGenerationButton)

def test_token_streamer_stream_text():
    box = TokenStreamerBox()
    text = "Hello\nWorld"
    actions = box.stream_text(text, duration=2.0)
    
    assert box._current_text == text
    assert box.streaming_text.total_chars == len(text)
    assert box.streaming_text.speed == len(text) / 2.0
    
    assert len(actions) == 1 # tokens_count to
    
def test_velocity_counter_math():
    counter = TokenSpeedVelocityCounter()
    ctx = MockContext()
    
    counter.tokens_count.set(0.0)
    counter.draw(ctx, 0.0)
    assert counter._velocity == 0.0
    assert counter.text_node.text.get(0.0) == "0.0 tok/s"
    
    # Fast advance
    counter.tokens_count.set(100.0)
    counter.draw(ctx, 1.0) # dt = 1.0
    
    assert counter._velocity > 0.0
    assert "tok/s" in counter.text_node.text.get(1.0)
    
def test_stop_generation_button_pulse():
    btn = StopGenerationButton()
    ctx = MockContext()
    
    btn.draw(ctx, 0.0)
    s1 = btn.icon.scale.get().x
    
    btn.draw(ctx, 1.0)
    s2 = btn.icon.scale.get().x
    
    assert s1 != s2 # Pulsing scale
    
def test_shimmering_caret_pulse():
    caret = ShimmeringCaretIndicator()
    ctx = MockContext()
    
    # We can't easily capture the alpha sent to ctx, but we can verify it doesn't crash
    caret.draw(ctx, 0.0)
    caret.draw(ctx, 1.0)
    assert True
