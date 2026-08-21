import random
import pytest
import cairo
import math
from vibmo.core.color import Color, colors
from vibmo.fx.backgrounds.bg_bokeh_light_bubbles import (
    DriftingBokehOrbs,
    AnamorphicLensGleamBackdrop,
    GoldenDustAmbience
)


class MockContext:
    """Mock Cairo context for isolated unit tests testing rendering logic."""
    def __init__(self):
        self.operations = []
        self.saved_states = 0
        self.operator = None
        self.matrix = [(0, 0)] # stack of translations
        self.sources = []
        self.current_path = []

    def save(self):
        self.saved_states += 1
        self.matrix.append(self.matrix[-1])
        self.operations.append("save")

    def restore(self):
        if self.saved_states > 0:
            self.saved_states -= 1
            self.matrix.pop()
        self.operations.append("restore")

    def set_operator(self, operator):
        self.operator = operator
        self.operations.append(f"set_operator({operator})")

    def translate(self, tx, ty):
        curr_tx, curr_ty = self.matrix[-1]
        self.matrix[-1] = (curr_tx + tx, curr_ty + ty)
        self.operations.append(f"translate({tx:.2f}, {ty:.2f})")

    def arc(self, xc, yc, radius, angle1, angle2):
        self.operations.append(f"arc({xc}, {yc}, {radius:.2f})")

    def rectangle(self, x, y, width, height):
        self.operations.append(f"rectangle({x:.2f}, {y:.2f}, {width:.2f}, {height:.2f})")

    def new_path(self):
        self.current_path = []
        self.operations.append("new_path")

    def move_to(self, x, y):
        self.current_path.append((x, y))
        self.operations.append(f"move_to({x:.2f}, {y:.2f})")

    def line_to(self, x, y):
        self.current_path.append((x, y))
        self.operations.append(f"line_to({x:.2f}, {y:.2f})")

    def close_path(self):
        self.operations.append("close_path")

    def set_source(self, source):
        self.sources.append(source)
        self.operations.append(f"set_source({type(source).__name__})")

    def fill(self):
        self.operations.append("fill")

    # For introspection in tests
    def get_translations(self):
        return [op for op in self.operations if op.startswith("translate")]


def test_drifting_bokeh_orbs_lifecycle():
    random.seed(42)
    bg = DriftingBokehOrbs(width=800, height=600, count=10, shape="circle")
    
    # Test bounds
    assert bg.local_bounds() == (0.0, 0.0, 800.0, 600.0)
    
    # Test particle initialization
    assert len(bg.particles) == 10
    
    ctx = MockContext()
    bg.draw(ctx, time=0.0)
    
    # Check operator (ADD mode if cairo supports it)
    try:
        assert ctx.operator == cairo.Operator.ADD
    except AttributeError:
        pass # Handle if test environment cairo doesn't have ADD
        
    assert "save" in ctx.operations
    assert "restore" in ctx.operations
    assert ctx.operations.count("fill") == 10 # One for each particle
    
    # Test time progression
    ctx2 = MockContext()
    bg.draw(ctx2, time=2.0)
    
    # Compare translations to ensure particles moved
    trans1 = ctx.get_translations()
    trans2 = ctx2.get_translations()
    assert trans1 != trans2

def test_drifting_bokeh_orbs_hexagon():
    random.seed(42)
    bg = DriftingBokehOrbs(count=2, shape="hexagon")
    ctx = MockContext()
    bg.draw(ctx, time=0.0)
    
    assert "new_path" in ctx.operations
    assert "close_path" in ctx.operations
    move_tos = sum(1 for op in ctx.operations if op.startswith("move_to"))
    line_tos = sum(1 for op in ctx.operations if op.startswith("line_to"))
    
    assert move_tos == 2 # One per particle
    assert line_tos == 10 # 5 per particle (6 sides total)

def test_anamorphic_lens_gleam_backdrop():
    random.seed(123)
    bg = AnamorphicLensGleamBackdrop(width=1000, height=500, count=5)
    
    assert len(bg.streaks) == 5
    
    ctx = MockContext()
    bg.draw(ctx, time=1.0)
    
    try:
        assert ctx.operator == cairo.Operator.ADD
    except AttributeError:
        pass
        
    assert ctx.operations.count("fill") >= 5 # At least one fill per streak (main rectangle)
    
    # Verify we drew rectangles (the streaks)
    rects = [op for op in ctx.operations if op.startswith("rectangle")]
    assert len(rects) == 5
    
    # LinearGradients should be used for streaks
    gradients = [s for s in ctx.sources if isinstance(s, cairo.LinearGradient)]
    assert len(gradients) == 5
    
def test_golden_dust_ambience():
    random.seed(777)
    bg = GoldenDustAmbience(width=400, height=400, count=20)
    
    assert len(bg.motes) == 20
    
    ctx = MockContext()
    bg.draw(ctx, time=5.0) # Advanced time to allow some flickering
    
    # Fills may be less than 20 due to opacity threshold filtering
    fills = ctx.operations.count("fill")
    assert fills <= 20
    
    # Verify particles use radial gradients
    radial_gradients = [s for s in ctx.sources if isinstance(s, cairo.RadialGradient)]
    assert len(radial_gradients) == fills
    
    # Test time progression and motion
    ctx2 = MockContext()
    bg.draw(ctx2, time=6.0)
    
    trans1 = ctx.get_translations()
    trans2 = ctx2.get_translations()
    # Particles move over time
    assert trans1 != trans2
