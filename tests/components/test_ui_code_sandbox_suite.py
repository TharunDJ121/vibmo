import pytest
import math
import cairo
from unittest.mock import MagicMock
from vibmo.core.color import Color
from vibmo.product.ai.ui_code_sandbox_suite import (
    SplitCodePlayground,
    InteractiveTerminalLogs,
    RunCodeSuccessIndicator,
    DependencyInstallPill,
)

class MockCairoContext:
    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        def _mock_method(*args, **kwargs):
            if name == "text_extents":
                return (0, 0, 100, 12, 0, 0)
            self.calls.append((name, args, kwargs))
            return self
        return _mock_method

def test_split_code_playground_draw():
    ctx = MockCairoContext()
    comp = SplitCodePlayground(width=1000.0, height=600.0, split_ratio=0.6)
    
    comp.draw(ctx, time=0.0)
    
    # Check that it draws the left pane (600 width) and right pane (400 width)
    rect_calls = [c for c in ctx.calls if c[0] == "rectangle"]
    
    # rect calls: (x, y, w, h)
    # First is left pane: (0, 0, 600.0, 600.0)
    # Second is right pane: (600.0, 0, 400.0, 600.0)
    assert len(rect_calls) >= 2
    
    assert rect_calls[0][1] == (0, 0, 600.0, 600.0)
    assert rect_calls[1][1] == (600.0, 0, 400.0, 600.0)

def test_interactive_terminal_logs_draw():
    ctx = MockCairoContext()
    comp = InteractiveTerminalLogs(logs=["Log 1", "Log 2"], execution_time="1.0s")
    
    comp.draw(ctx, time=0.0)
    
    show_text_calls = [c for c in ctx.calls if c[0] == "show_text"]
    assert len(show_text_calls) == 3 # 1 header + 2 logs
    assert "Execution time: 1.0s" in show_text_calls[0][1][0]
    assert show_text_calls[1][1][0] == "Log 1"
    assert show_text_calls[2][1][0] == "Log 2"

def test_run_code_success_indicator_draw():
    ctx = MockCairoContext()
    comp = RunCodeSuccessIndicator(radius=20.0, success=False)
    
    # Test time=0, success=0 (should draw play button, i.e., 3 points for triangle)
    comp.draw(ctx, time=0.0)
    line_to_calls = [c for c in ctx.calls if c[0] == "line_to"]
    # 2 line_tos for triangle
    assert len(line_to_calls) >= 2 
    
    # Test pulsing effect
    # At success=0, time=pi/10, sin(time*5) = sin(pi/2) = 1, pulse = 1.1
    # arc is called with radius = 20 * 1.1 = 22.0
    ctx.calls.clear()
    comp.draw(ctx, time=math.pi / 10.0)
    arc_calls = [c for c in ctx.calls if c[0] == "arc"]
    # (x, y, r, a1, a2)
    assert math.isclose(arc_calls[0][1][2], 22.0, rel_tol=1e-5)
    
    # Test success=1 (should draw checkmark, no pulse)
    ctx.calls.clear()
    comp.success.set(1.0)
    comp.draw(ctx, time=0.0)
    
    arc_calls = [c for c in ctx.calls if c[0] == "arc"]
    assert math.isclose(arc_calls[0][1][2], 20.0, rel_tol=1e-5) # radius should be exactly 20.0 (no pulse)
    
    stroke_calls = [c for c in ctx.calls if c[0] == "stroke"]
    assert len(stroke_calls) > 0 # checkmark is stroked, play is filled

def test_dependency_install_pill_draw():
    ctx = MockCairoContext()
    comp = DependencyInstallPill(text="Done!")
    
    comp.draw(ctx, time=0.0)
    
    show_text_calls = [c for c in ctx.calls if c[0] == "show_text"]
    assert len(show_text_calls) == 1
    assert show_text_calls[0][1][0] == "Done!"
    
    # Check dimensions
    # Our text_extents mock returns 100 width, 12 height
    # padding is 12, so w = 100 + 24 = 124
    arc_calls = [c for c in ctx.calls if c[0] == "arc"]
    # 4 calls to arc for rounded rect
    assert len(arc_calls) >= 4
