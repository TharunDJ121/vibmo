import pytest
from vibmo.product.ai.ui_diffusion_canvas_suite import (
    DiffusionGenerationCanvas,
    PromptAspectSelector,
    SeedVariationPills,
    MagicPromptEnhanceBar
)
from vibmo.timeline.scheduler import ParallelGroup, SequentialGroup
from vibmo.core.vector import Vector2D
import cairo

class MockContext:
    def save(self): pass
    def restore(self): pass
    def translate(self, x, y): pass
    def scale(self, x, y): pass
    def rotate(self, angle): pass
    def set_source_rgba(self, r, g, b, a): pass
    def set_source(self, source): pass
    def new_path(self): pass
    def new_sub_path(self): pass
    def arc(self, x, y, r, a1, a2): pass
    def close_path(self): pass
    def set_line_width(self, w): pass
    def stroke(self): pass
    def fill(self): pass
    def clip(self): pass
    def get_current_point(self): return (0, 0)
    def move_to(self, x, y): pass
    def line_to(self, x, y): pass
    def text_extents(self, text):
        class Extents:
            x_bearing = 0
            y_bearing = 0
            width = 100
            height = 20
            x_advance = 100
            y_advance = 0
        return Extents()
    def select_font_face(self, family, slant, weight): pass
    def set_font_size(self, size): pass
    def show_text(self, text): pass
    def text_path(self, text): pass
    def rectangle(self, x, y, w, h): pass
    def fill_preserve(self): pass
    def stroke_preserve(self): pass

def test_diffusion_generation_canvas():
    canvas = DiffusionGenerationCanvas(width=400, height=400, total_steps=20)
    assert canvas.width.get() == 400
    assert canvas.height.get() == 400

    # Check initial step text and opacity
    assert "Step 0/20" in canvas.step_text.text.get()
    assert canvas.noise_overlay.opacity.get() == 1.0

    # Animate
    canvas.denoise_to(10, duration=1.0).apply_at(0.0)

    # Fast forward
    assert canvas.current_step.get(1.0) == 10.0
    assert "Step 10/20" in canvas.step_text.text.get(1.0)
    assert canvas.noise_overlay.opacity.get(1.0) == 0.5

    # Test rendering hooks
    ctx = MockContext()
    canvas.draw(ctx, 1.0)

def test_prompt_aspect_selector():
    selector = PromptAspectSelector()
    assert len(selector.aspect_ratios) == 4

    # Run layout to populate positions
    selector.compute_layout(0.0)

    # Active indicator should be at first pill
    assert selector.indicator.position.get().x == selector.pills[0].position.get().x

    # Select second option
    selector.select(1, duration=1.0).apply_at(0.0)

    # Test interpolation at 0.5s (halfway between 0 and 1)
    selector.compute_layout(0.5)
    # The active_index is cubic ease by default, let's just check final position
    selector.compute_layout(1.0)
    assert selector.indicator.position.get(1.0).x == selector.pills[1].position.get(1.0).x

    ctx = MockContext()
    selector.draw(ctx, 1.0)

def test_seed_variation_pills():
    pills = SeedVariationPills()
    assert len(pills.cards) == 4

    # Run layout
    pills.compute_layout(0.0)

    # Highlight second card
    action = pills.highlight(1, duration=1.0)
    action.apply_at(0.0)

    # At 1.0s, the second card should have a stroke width of 4.0 and INDIGO color
    assert pills.cards[1].stroke_width.get(1.0) == 4.0

    ctx = MockContext()
    pills.draw(ctx, 1.0)

def test_magic_prompt_enhance_bar():
    bar = MagicPromptEnhanceBar()

    # Run layout
    bar.compute_layout(0.0)

    # Shimmer animation
    action = bar.shimmer(duration=1.0)
    action.apply_at(0.0)

    # At 0.5s, scale should be 1.05
    assert bar.button.scale.get(0.5).x == 1.05
    assert bar.button.scale.get(0.5).y == 1.05

    ctx = MockContext()
    bar.draw(ctx, 1.0)
