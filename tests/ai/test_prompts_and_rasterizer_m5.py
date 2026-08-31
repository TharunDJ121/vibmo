"""
Unit tests for AI prompt construction and Rasterizer proxy scale robustness.
Covers M5 milestone requirements:
- vibmo/ai/prompts.py JSON template escaping and context injection
- vibmo/render/rasterizer.py 3D quad projective transform with proxy scaling
"""

import pytest
import numpy as np
import cairo

from vibmo.ai.prompts import (
    build_system_prompt,
    build_surgical_edit_prompt,
    build_auto_repair_prompt,
)
from vibmo.agent_api import (
    Scene,
    GlassCard,
    KineticText,
    MetricCounter,
    Vignette,
    FilmGrain,
    colors,
)
from vibmo.render.rasterizer import Rasterizer


def test_build_system_prompt_default():
    prompt = build_system_prompt()
    assert isinstance(prompt, str)
    assert len(prompt) > 100
    assert "from motio.agent_api import *" in prompt
    assert "colors.DARK_NAVY" in prompt
    assert "GlassCard" in prompt
    assert "@scene.animate" in prompt


def test_build_system_prompt_with_custom_context():
    context = "User requires high-contrast cybersecurity theme with green terminal aesthetics."
    prompt = build_system_prompt(custom_context=context)
    assert context in prompt
    assert "Additional User Context & Instructions:" in prompt


def test_build_surgical_edit_prompt_json_brace_escaping():
    code = """
from motio.agent_api import *
scene = Scene(width=1920, height=1080, duration=4.0)
title = KineticText("Hello", font_size=32)
scene.add(title)
"""
    instruction = "Change duration of main_shot to 5.5s and increase text font_size to 48"
    
    # Must format cleanly without ValueError (e.g. Invalid format specifier)
    prompt = build_surgical_edit_prompt(current_code=code, instruction=instruction)
    
    assert instruction in prompt
    assert code in prompt
    # Verify the JSON template structure has unescaped valid JSON brackets in the final prompt
    assert '"op_type": "change_shot_duration"' in prompt
    assert '"shot_id": "main_shot"' in prompt
    assert '"duration": 5.5' in prompt
    assert '```json' in prompt
    assert '```' in prompt


def test_build_auto_repair_prompt():
    code = "scene = Scene(width=1920, height=1080)\nscene.add(card)"
    errors = [
        "NameError: name 'card' is not defined",
        "SyntaxError: unexpected EOF while parsing",
    ]
    prompt = build_auto_repair_prompt(code=code, errors=errors)
    assert "NameError: name 'card' is not defined" in prompt
    assert "SyntaxError: unexpected EOF while parsing" in prompt
    assert code in prompt


@pytest.mark.parametrize("scale", [0.25, 0.333, 0.5, 0.75, 1.0, 1.5, 2.0])
def test_rasterizer_proxy_scale_dimensions_and_buffers(scale):
    """
    Verifies that Rasterizer correctly scales dimensions and creates matched-size
    Cairo ImageSurfaces across all proxy scale factors without buffer length errors.
    """
    rasterizer = Rasterizer(width=1920, height=1080)
    card = GlassCard(position=(960, 540))
    title = KineticText("Proxy Test", font_size=36)
    card.add(title)

    rgba = rasterizer.render_frame(
        root_nodes=[card],
        time=0.5,
        background=colors.DARK_NAVY,
        scale=scale,
    )

    expected_w = max(16, int(1920 * max(0.1, min(2.0, scale))))
    expected_h = max(16, int(1080 * max(0.1, min(2.0, scale))))

    assert rgba.shape == (expected_h, expected_w, 4)
    assert rgba.dtype == np.uint8


@pytest.mark.parametrize("scale", [0.25, 0.5, 1.0])
def test_rasterizer_3d_quad_with_proxy_scales(scale):
    """
    Verifies that 3D projective transformations with rotate_x and rotate_y
    correctly warp onto the Cairo canvas without 'buffer is not long enough' errors.
    """
    scene = Scene(width=1920, height=1080, fps=30.0, duration=2.0)
    card = GlassCard(position=(960, 540))
    card.rotate_x.set(30.0)
    card.rotate_y.set(-20.0)
    counter = MetricCounter(start_val=0, end_val=5000)
    card.add(counter)
    scene.add(card)

    rgba = scene.render_frame(time=1.0, scale=scale)

    expected_w = max(16, int(1920 * scale))
    expected_h = max(16, int(1080 * scale))

    assert rgba.shape == (expected_h, expected_w, 4)
    assert rgba.dtype == np.uint8


def test_rasterizer_motion_blur_and_post_fx():
    rasterizer = Rasterizer(width=640, height=360)
    card = GlassCard(position=(320, 180))
    
    blurred = rasterizer.render_frame_with_motion_blur(
        root_nodes=[card],
        time=0.5,
        fps=30.0,
        shutter_angle=180.0,
        samples=4,
        background=colors.DARK_NAVY,
        post_fx=[Vignette(0.25), FilmGrain(0.01)],
    )

    assert blurred.shape == (360, 640, 4)
    assert blurred.dtype == np.uint8
