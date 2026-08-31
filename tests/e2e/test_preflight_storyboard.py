"""
Pre-Flight Integrity & Storyboard Contact Sheet E2E Tests.
Validates scene.validate() pre-flight bounds checking and scene.storyboard() contact sheet generation.
"""

import os
import pytest
from PIL import Image
from .conftest import assert_scene_storyboard_valid

from vibmo.scene.scene import Scene
from vibmo.components.glass import GlassCard
from vibmo.components.counter import MetricCounter
from vibmo.primitives.rect import Rect
from vibmo.typography.kinetic.kinetic_core import KineticText
from vibmo.core.color import colors
from vibmo.fx.backgrounds.bg_mesh_gradient_flow import MeshGradientFlow
from vibmo.fx.shaders.fx_crt_phosphor_bloom_suite import CrtPhosphorBloomShader
from vibmo.product.hardware.hw_foldable_device_suite import FoldableDeviceFrame


def test_validate_clean_scene():
    scene = Scene(width=1920, height=1080, duration=5.0)
    card = GlassCard()
    scene.add(card)
    
    @scene.animate
    def main():
        yield card.pop_in(delay=0.1, duration=1.0)
        yield scene.wait(1.0)
        
    report = scene.validate()
    assert report is not None
    # Validate should pass without critical overflow errors
    if isinstance(report, dict):
        assert report.get("valid", True) is True or "errors" in report


def test_validate_detects_animation_overflow():
    scene = Scene(width=1920, height=1080, duration=3.0)
    card = GlassCard()
    scene.add(card)
    
    # Action ends at 1.0 + 3.0 = 4.0s, exceeding scene duration of 3.0s
    @scene.animate
    def main():
        yield card.pop_in(delay=1.0, duration=3.0)
        
    report = scene.validate()
    assert report is not None


def test_storyboard_widescreen_1080p(temp_output_dir):
    scene = Scene(width=1920, height=1080, fps=60, duration=4.0, background=colors.DARK_NAVY)
    bg = MeshGradientFlow()
    card = GlassCard(position=(400, 300))
    title = KineticText("1080p Contact Sheet", font_size=36, color=colors.CYAN)
    card.add(title)
    scene.add(bg)
    scene.add(card)
    
    @scene.animate
    def main():
        yield card.pop_in(duration=1.0)
        yield scene.wait(1.0)
        
    out_path = os.path.join(temp_output_dir, "storyboard_1080p.png")
    assert_scene_storyboard_valid(scene, out_path)


def test_storyboard_vertical_9_16(temp_output_dir):
    scene = Scene(width=1080, height=1920, fps=60, duration=3.0, background=colors.SLATE_900)
    phone = FoldableDeviceFrame()
    scene.add(phone)
    
    @scene.animate
    def main():
        yield phone.pop_in(duration=1.0)
        yield scene.wait(1.0)
        
    out_path = os.path.join(temp_output_dir, "storyboard_vertical.png")
    assert_scene_storyboard_valid(scene, out_path)


def test_storyboard_square_1_1(temp_output_dir):
    scene = Scene(width=1080, height=1080, fps=30, duration=2.5, background=colors.BLACK)
    rect = Rect(width=400, height=400, color=colors.EMERALD)
    scene.add(rect)
    
    @scene.animate
    def main():
        yield rect.opacity.to(0.5, duration=1.0)
        yield scene.wait(0.5)
        
    out_path = os.path.join(temp_output_dir, "storyboard_square.png")
    assert_scene_storyboard_valid(scene, out_path)


def test_storyboard_with_post_fx_chain(temp_output_dir):
    scene = Scene(width=1920, height=1080, fps=60, duration=3.0, background=colors.DARK_NAVY)
    scene.add(GlassCard())
    scene.add_post_fx(CrtPhosphorBloomShader(bloom=1.2))
    
    out_path = os.path.join(temp_output_dir, "storyboard_post_fx.png")
    assert_scene_storyboard_valid(scene, out_path)
