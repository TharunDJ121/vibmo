import pytest
import cairo
from vibmo.product.ai.ui_diffusion_canvas_suite import (
    DiffusionGenerationCanvas,
    PromptAspectSelector,
    SeedVariationPills,
    MagicPromptEnhanceBar,
    DiffusionCanvas,
    DenoisingProgress,
)

def test_diffusion_generation_canvas():
    canvas = DiffusionGenerationCanvas(width=400, height=400)
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 400, 400)
    ctx = cairo.Context(surface)
    canvas.draw(ctx, time=0.0)
    assert canvas.local_bounds(0.0) == (0.0, 0.0, 400.0, 400.0)

def test_prompt_aspect_selector():
    selector = PromptAspectSelector(aspects=["1:1", "16:9", "9:16"])
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 400, 60)
    ctx = cairo.Context(surface)
    selector.draw(ctx, time=0.0)
    assert len(selector.aspects) == 3

def test_seed_variation_pills():
    pills = SeedVariationPills(seeds=[42, 1337, 9000])
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 400, 60)
    ctx = cairo.Context(surface)
    pills.draw(ctx, time=0.0)
    assert len(pills.seeds) == 3

def test_magic_prompt_enhance_bar():
    bar = MagicPromptEnhanceBar(prompt="Photorealistic cyberpunk city")
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 600, 60)
    ctx = cairo.Context(surface)
    bar.draw(ctx, time=0.0)
    assert bar.prompt == "Photorealistic cyberpunk city"
