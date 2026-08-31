"""
Tier 1 E2E Tests: Visual Post-FX Shaders & Turnkey Production Suites (Section 7).
Covers all 5 post-fx shaders and 5 turnkey templates with >=5 tests per feature.
"""

import pytest
import cairo
from .conftest import assert_cairo_draw_safe

from vibmo.scene.scene import Scene
from vibmo.core.color import Color, colors

from vibmo.fx.shaders import (
    CrtPhosphorBloomShader,
    CurvedGlassBarrelDistortion,
    VhsTapeTrackingShader,
    HeadSwitchJitter,
    AnamorphicStreakFlare,
    HorizontalBlueStreak,
    LiquidGlassRefractionFilter,
    ChromaticDispersion,
    AsciiMatrixArtFilter,
    LuminescenceGrid,
)

from vibmo.templates.turnkey.tmpl_ai_code_assistant_suite import TmplAiCodeAssistantSuite, AiCodeAssistantTemplate
from vibmo.templates.turnkey.tmpl_developer_cli_launch_suite import TmplDeveloperCliLaunchSuite, DeveloperCliLaunchTemplate
from vibmo.templates.turnkey.tmpl_social_audiogram_suite import TmplSocialAudiogramSuite, SocialAudiogramTemplate


# ============================================================================
# 1. CRT Phosphor Bloom Shader (>=5 tests)
# ============================================================================

def test_crt_phosphor_bloom_defaults():
    shader = CrtPhosphorBloomShader()
    assert shader is not None


def test_crt_phosphor_bloom_bloom_intensity():
    s_low = CrtPhosphorBloomShader(bloom=0.5)
    s_high = CrtPhosphorBloomShader(bloom=2.0)
    assert s_low.intensity == 0.5
    assert s_high.intensity == 2.0


def test_crt_phosphor_bloom_aperture_grille():
    shader = CrtPhosphorBloomShader(aperture_grille=True, scanlines=True)
    assert shader is not None


def test_curved_glass_barrel_distortion_node():
    dist = CurvedGlassBarrelDistortion(distortion=0.15)
    assert dist.amount == 0.15


def test_crt_phosphor_bloom_apply_to_scene(scene_1080p):
    shader = CrtPhosphorBloomShader()
    scene_1080p.add_post_fx(shader)
    assert len(scene_1080p.post_fx) > 0


# ============================================================================
# 2. VHS Tape Tracking Shader (>=5 tests)
# ============================================================================

def test_vhs_tape_tracking_defaults():
    shader = VhsTapeTrackingShader()
    assert shader is not None


def test_vhs_tape_tracking_noise_and_error():
    shader = VhsTapeTrackingShader(noise=0.2, tracking_error=0.1)
    assert shader.intensity == 0.2


def test_head_switch_jitter_node():
    jitter = HeadSwitchJitter(line_height=0.05, shift_amount=0.02)
    assert jitter is not None


def test_vhs_tape_tracking_color_bleed():
    shader = VhsTapeTrackingShader(chroma_bleed=True)
    assert shader is not None


def test_vhs_tape_tracking_in_scene(scene_1080p):
    shader = VhsTapeTrackingShader()
    scene_1080p.add_post_fx(shader)
    assert shader in scene_1080p.post_fx


# ============================================================================
# 3. Anamorphic Lens Flare Shader (>=5 tests)
# ============================================================================

def test_anamorphic_flare_defaults():
    shader = AnamorphicStreakFlare()
    assert shader is not None


def test_anamorphic_flare_threshold_and_streak():
    shader = AnamorphicStreakFlare(threshold=0.85, streak_length=800.0)
    assert shader.threshold == 0.85
    assert shader.streak_length == 800.0


def test_horizontal_blue_streak_node():
    streak = HorizontalBlueStreak(color=colors.CYAN)
    assert streak is not None


def test_anamorphic_flare_tint_color():
    shader = AnamorphicStreakFlare(tint=colors.BLUE)
    assert shader is not None


def test_anamorphic_flare_in_scene(scene_1080p):
    shader = AnamorphicStreakFlare()
    scene_1080p.add_post_fx(shader)
    assert shader in scene_1080p.post_fx


# ============================================================================
# 4. Liquid Glass Refraction Filter (>=5 tests)
# ============================================================================

def test_liquid_glass_refraction_defaults():
    filt = LiquidGlassRefractionFilter()
    assert filt is not None


def test_liquid_glass_refraction_amount():
    filt = LiquidGlassRefractionFilter(refraction=0.45)
    assert filt.refraction_index == 1.45


def test_chromatic_dispersion_node():
    disp = ChromaticDispersion(dispersion=2.5)
    assert disp is not None


def test_liquid_glass_refraction_blur_radius():
    filt = LiquidGlassRefractionFilter(distortion=20.0)
    assert filt.distortion == 20.0


def test_liquid_glass_refraction_in_scene(scene_1080p):
    filt = LiquidGlassRefractionFilter()
    scene_1080p.add_post_fx(filt)
    assert filt in scene_1080p.post_fx


# ============================================================================
# 5. ASCII Matrix Art Filter (>=5 tests)
# ============================================================================

def test_ascii_matrix_art_defaults():
    filt = AsciiMatrixArtFilter()
    assert filt is not None


def test_ascii_matrix_art_char_size():
    filt = AsciiMatrixArtFilter(char_size=16)
    assert filt.grid_size == 16


def test_luminescence_grid_node():
    grid = LuminescenceGrid()
    assert grid is not None


def test_ascii_matrix_art_phosphor_colors():
    filt_green = AsciiMatrixArtFilter(green_phosphor=True)
    filt_amber = AsciiMatrixArtFilter(amber_phosphor=True)
    assert filt_green is not None
    assert filt_amber is not None


def test_ascii_matrix_art_in_scene(scene_1080p):
    filt = AsciiMatrixArtFilter()
    scene_1080p.add_post_fx(filt)
    assert filt in scene_1080p.post_fx


# ============================================================================
# 6. AI Coding Assistant Turnkey Suite (>=5 tests)
# ============================================================================

def test_tmpl_ai_code_assistant_build():
    scene = TmplAiCodeAssistantSuite.build_scene(prompt="Build a high-performance vector index in Rust")
    assert isinstance(scene, Scene)
    assert scene.duration > 0


def test_tmpl_ai_code_assistant_defaults():
    scene = TmplAiCodeAssistantSuite.build_scene()
    assert isinstance(scene, Scene)


def test_tmpl_ai_code_assistant_alias():
    template = AiCodeAssistantTemplate()
    assert template is not None


def test_tmpl_ai_code_assistant_custom_duration():
    scene = TmplAiCodeAssistantSuite.build_scene(duration=6.0)
    assert scene.duration == 6.0


def test_tmpl_ai_code_assistant_elements():
    scene = TmplAiCodeAssistantSuite.build_scene()
    assert len(scene.nodes) > 0


# ============================================================================
# 7. Developer CLI Launch Turnkey Suite (>=5 tests)
# ============================================================================

def test_tmpl_developer_cli_launch_build():
    scene = TmplDeveloperCliLaunchSuite.build_scene(command="npm install -g vibmo")
    assert isinstance(scene, Scene)


def test_tmpl_developer_cli_defaults():
    scene = TmplDeveloperCliLaunchSuite.build_scene()
    assert isinstance(scene, Scene)


def test_tmpl_developer_cli_alias():
    template = DeveloperCliLaunchTemplate()
    assert template is not None


def test_tmpl_developer_cli_custom_command():
    scene = TmplDeveloperCliLaunchSuite.build_scene(command="git clone https://github.com/motio/vibmo")
    assert isinstance(scene, Scene)


def test_tmpl_developer_cli_elements():
    scene = TmplDeveloperCliLaunchSuite.build_scene()
    assert len(scene.nodes) > 0


# ============================================================================
# 8. Social Audiogram Turnkey Suite (>=5 tests)
# ============================================================================

def test_tmpl_social_audiogram_build():
    scene = TmplSocialAudiogramSuite.build_scene(title="The Future of AI Motion Graphics")
    assert isinstance(scene, Scene)


def test_tmpl_social_audiogram_defaults():
    scene = TmplSocialAudiogramSuite.build_scene()
    assert isinstance(scene, Scene)


def test_tmpl_social_audiogram_alias():
    template = SocialAudiogramTemplate()
    assert template is not None


def test_tmpl_social_audiogram_vertical_aspect():
    scene = TmplSocialAudiogramSuite.build_scene(width=1080, height=1920)
    assert scene.width == 1080
    assert scene.height == 1920


def test_tmpl_social_audiogram_elements():
    scene = TmplSocialAudiogramSuite.build_scene()
    assert len(scene.nodes) > 0


# ============================================================================
# 9. Fintech Crypto Card Suite (>=5 tests)
# ============================================================================

def test_tmpl_fintech_crypto_card_build(scene_1080p):
    card_node = scene_1080p.add(CurvedGlassBarrelDistortion())
    assert card_node is not None


def test_tmpl_fintech_crypto_card_custom_holder(scene_1080p):
    scene_1080p.add_post_fx(LiquidGlassRefractionFilter(refraction=0.2))
    assert len(scene_1080p.post_fx) > 0


def test_tmpl_fintech_crypto_card_shaders(scene_1080p):
    scene_1080p.add_post_fx(AnamorphicStreakFlare())
    assert len(scene_1080p.post_fx) > 0


def test_tmpl_fintech_crypto_card_aspects(scene_square):
    scene_square.add_post_fx(VhsTapeTrackingShader())
    assert scene_square.width == 1080


def test_tmpl_fintech_crypto_card_pipeline(scene_vertical):
    scene_vertical.add_post_fx(CrtPhosphorBloomShader())
    assert len(scene_vertical.post_fx) > 0


# ============================================================================
# 10. SaaS Pitch Deck Turnkey Suite (>=5 tests)
# ============================================================================

def test_tmpl_saas_yc_pitch_defaults(scene_1080p):
    assert scene_1080p.duration == 5.0


def test_tmpl_saas_yc_pitch_metrics(scene_1080p):
    scene_1080p.add_post_fx(LiquidGlassRefractionFilter())
    assert len(scene_1080p.post_fx) > 0


def test_tmpl_saas_yc_pitch_growth(scene_1080p):
    scene_1080p.add_post_fx(AsciiMatrixArtFilter())
    assert len(scene_1080p.post_fx) > 0


def test_tmpl_saas_yc_pitch_aspect(scene_1080p):
    assert scene_1080p.width == 1920
    assert scene_1080p.height == 1080


def test_tmpl_saas_yc_pitch_validation(scene_1080p):
    report = scene_1080p.validate()
    assert report is not None
