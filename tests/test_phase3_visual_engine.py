"""
Unit tests for Phase 3A: Output Polish, Real Compositing & Visual Rendering Engine.
Tests ColorGrade, 4-octave Bloom, AnamorphicStreak, GlassCard backdrop blur, Particle presets, and KineticText reveals.
"""

import math
import numpy as np
import pytest
from PIL import Image

from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D
from vibmo.scene.scene import Scene
from vibmo.components.glass import GlassCard
from vibmo.components.counter import MetricCounter
from vibmo.typography.kinetic import KineticText
from vibmo.physics.particles import ParticleEmitter
from vibmo.color.grading import ColorGrade
from vibmo.fx.filters import Bloom, Glow, AnamorphicStreak, FilmGrain, Vignette


class TestColorGradingEngine:
    def test_color_grade_lift_gain(self):
        # Create a test gradient image
        h, w = 100, 100
        grad = np.linspace(0, 255, w, dtype=np.uint8)
        rgba = np.zeros((h, w, 4), dtype=np.uint8)
        rgba[:, :, 0] = grad
        rgba[:, :, 1] = grad
        rgba[:, :, 2] = grad
        rgba[:, :, 3] = 255

        # Lift boosts shadows (lift=(0.2, 0.0, 0.0))
        grade = ColorGrade(lift=(0.2, 0.0, 0.0), gain=(1.0, 1.0, 1.0))
        out = grade.apply(rgba)
        assert out.shape == (h, w, 4)
        # Deep blacks should have red boosted
        assert out[0, 0, 0] > rgba[0, 0, 0]

    def test_color_grade_temperature_tint(self):
        rgba = np.full((50, 50, 4), 128, dtype=np.uint8)
        rgba[:, :, 3] = 255

        # Warm temperature (+0.8) should increase Red, decrease Blue
        warm_grade = ColorGrade(temperature=0.8)
        out = warm_grade.apply(rgba)
        assert out[0, 0, 0] > rgba[0, 0, 0]  # Red increased
        assert out[0, 0, 2] < rgba[0, 0, 2]  # Blue decreased

    def test_color_grade_contrast_s_curve(self):
        rgba = np.full((50, 50, 4), 180, dtype=np.uint8)
        rgba[:, :, 3] = 255

        grade = ColorGrade(contrast=1.5, pivot=0.435, use_s_curve=True)
        out = grade.apply(rgba)
        # Highlights above pivot get pushed brighter
        assert out[0, 0, 0] >= rgba[0, 0, 0]

    def test_color_grade_saturation_boost(self):
        rgba = np.zeros((50, 50, 4), dtype=np.uint8)
        rgba[:, :, 0] = 160
        rgba[:, :, 1] = 120
        rgba[:, :, 2] = 100
        rgba[:, :, 3] = 255

        # Saturation 0 -> B&W (R == G == B)
        bw_grade = ColorGrade(saturation=0.0)
        bw_out = bw_grade.apply(rgba)
        assert abs(int(bw_out[0, 0, 0]) - int(bw_out[0, 0, 1])) <= 1


class TestBloomAndGlowPyramid:
    def test_bloom_4_octave_pyramid(self):
        rgba = np.zeros((120, 120, 4), dtype=np.uint8)
        rgba[:, :, 3] = 255
        # Single bright white square in the center
        rgba[50:70, 50:70, :3] = 255

        bloom = Bloom(threshold=0.6, intensity=0.8, radius=20.0)
        out = bloom.apply(rgba)
        assert out.shape == (120, 120, 4)
        # Pixels adjacent to the bright center should have non-zero diffuse glow
        assert out[40, 60, 0] > 0
        assert out[80, 60, 0] > 0

    def test_glow_emissive(self):
        rgba = np.zeros((100, 100, 4), dtype=np.uint8)
        rgba[:, :, 3] = 255
        rgba[45:55, 45:55, :3] = 220

        glow = Glow(intensity=1.0, radius=24.0, threshold=0.4)
        out = glow.apply(rgba)
        assert out[40, 50, 0] > 0

    def test_anamorphic_streak(self):
        rgba = np.zeros((100, 100, 4), dtype=np.uint8)
        rgba[:, :, 3] = 255
        # High specular center point
        rgba[48:52, 48:52, :3] = 255

        streak = AnamorphicStreak(intensity=0.8, threshold=0.7, streak_length=80.0)
        out = streak.apply(rgba)
        # Far horizontal edges along the same y-line should have cyan/blue diffuse streak
        assert out[50, 20, 2] > 0 or out[50, 80, 2] > 0


class TestGlassCardBackdropBlur:
    def test_glass_card_with_backdrop_blur(self):
        scene = Scene(width=400, height=400, fps=30, duration=2.0)
        
        # Add background element
        bg_card = GlassCard(position=(50, 50), fill=colors.CYAN)
        scene.add(bg_card)

        # Add frosted glass card over it with backdrop blur
        frost = GlassCard(position=(100, 100), backdrop_blur=16.0, specular_rim=True)
        frost.gleam(duration=1.0)
        scene.add(frost)

        frame = scene.render_frame(0.5)
        assert frame.shape == (400, 400, 4)
        assert frame.dtype == np.uint8


class TestParticleEmitterPresets:
    def test_fire_embers_and_laser_sparks(self):
        scene = Scene(width=400, height=400, fps=30, duration=2.0)
        
        embers = ParticleEmitter(preset="fire_embers", position=(200, 350))
        embers.burst(count=30, time=0.0)
        scene.add(embers)

        lasers = ParticleEmitter(preset="laser_sparks", position=(200, 200), blend_mode="add")
        lasers.burst(count=20, time=0.2)
        scene.add(lasers)

        frame = scene.render_frame(0.5)
        assert frame.shape == (400, 400, 4)
        assert frame.dtype == np.uint8


class TestKineticTypographyReveals:
    def test_scramble_decrypt_and_bounce(self):
        scene = Scene(width=600, height=400, fps=30, duration=3.0)
        
        title = KineticText("QUANTUM SECURE", font_size=32, bold=True)
        scene.add(title)

        @scene.animate
        def anim():
            yield scene.all(
                title.scramble_decrypt(duration=1.0),
            )

        # Check frame at t=0.5s (during decryption scramble)
        frame_mid = scene.render_frame(0.5)
        assert frame_mid.shape == (400, 600, 4)

        # Check frame at t=2.0s (fully resolved and legible)
        frame_end = scene.render_frame(2.0)
        assert frame_end.shape == (400, 600, 4)
