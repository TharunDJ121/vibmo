"""
Tier 4 E2E Tests: Real-World Application Scenarios.
Simulates production-grade end-to-end motion graphics pipelines:
1. SaaS Launch Showcase
2. Fintech Crypto Card Demo
3. Developer CLI Launch Pipeline
4. AI Venture Pitch Deck
5. Social Media Dynamic Audiogram
"""

import os
import pytest
from .conftest import assert_valid_audio_array, assert_cairo_draw_safe, assert_scene_storyboard_valid

from vibmo.scene.scene import Scene
from vibmo.components.glass import GlassCard
from vibmo.components.counter import MetricCounter
from vibmo.product.mockups import BrowserWindow
from vibmo.product.charts_advanced import LineChart
from vibmo.typography.kinetic.kinetic_core import KineticText
from vibmo.core.color import Color, colors
from vibmo.core.easing import Ease
from vibmo.fx.filters import Vignette, FilmGrain

# Expansion suites
from vibmo.fx.backgrounds.bg_mesh_gradient_flow import MeshGradientFlow
from vibmo.fx.backgrounds.bg_cyber_grid_horizon import CyberGridHorizon
from vibmo.fx.backgrounds.bg_minimal_studio_infinity import MinimalStudioInfinity
from vibmo.product.hardware.hw_super_ultrawide_suite import SuperUltrawideMonitorFrame
from vibmo.product.hardware.hw_vintage_crt_suite import RetroArcadeCrtCabinet
from vibmo.product.hardware.hw_smartwatch_rugged_suite import RuggedSmartwatchFrame
from vibmo.product.ai.ui_token_streamer_suite import StreamingTokenOutput
from vibmo.product.ai.ui_tree_of_thought_suite import TreeOfThoughtTree
from vibmo.product.ai.ui_embeddings_space_suite import VectorEmbeddingsVisualizer
from vibmo.product.ai.ui_pricing_matrix_suite import PricingTierMatrix
from vibmo.product.ai.ui_code_sandbox_suite import CodeSandboxPlayground
from vibmo.charts.chart_candlestick_pro_suite import CandlestickChartPro
from vibmo.charts.chart_streamgraph_wave_suite import FlowingStreamgraphArea
from vibmo.typography.kinetic.typo_neon_strobe_suite import RealisticNeonStrobeSign
from vibmo.typography.kinetic.typo_terminal_typewriter_suite import PhosphorTerminalTypewriter
from vibmo.typography.kinetic.typo_odometer_tumbler_suite import OdometerTumblerCounter
from vibmo.audio.generators.sfx_whoosh_designer_suite import WhooshDesignerSuite
from vibmo.audio.generators.sfx_impact_sub_suite import ImpactSubSuite
from vibmo.audio.generators.sfx_keyboard_foley_suite import KeyboardFoleySuite
from vibmo.audio.generators.sfx_ambient_drone_suite import AmbientDroneSuite
from vibmo.audio.generators.sfx_vinyl_crackle_suite import VinylCrackleSuite
from vibmo.fx.shaders import AnamorphicStreakFlare, CrtPhosphorBloomShader


# ============================================================================
# Scenario 1: SaaS Launch Showcase
# ============================================================================

def test_scenario_saas_launch_pipeline(temp_output_dir):
    # 1. Initialize Scene (1080p @ 60 FPS, Dark Navy)
    scene = Scene(
        width=1920,
        height=1080,
        fps=60,
        duration=5.0,
        background=colors.DARK_NAVY,
    )
    
    # 2. Procedural Backdrop & Post-FX
    bg = MeshGradientFlow(colors=[colors.INDIGO, colors.CYAN], speed=0.6, complexity=4)
    scene.add(bg)
    scene.add_post_fx(Vignette(intensity=0.25), FilmGrain(amount=0.015))
    
    # 3. Hero Glass UI Container
    card = GlassCard(direction="column", gap=16, padding=32, corner_radius=24, position=(240, 200))
    title = KineticText("Automated Motion in Python", font_size=32, bold=True)
    counter = MetricCounter(start_val=0, end_val=250000, prefix="$", suffix=" MRR", font_size=52, bold=True, color=colors.EMERALD)
    streamer = StreamingTokenOutput(text="Real-time rendering at 60 FPS")
    
    card.add(title, counter, streamer)
    scene.add(card)
    
    # 4. Choreography
    @scene.animate
    def main():
        yield card.pop_in(delay=0.1, duration=0.8)
        yield scene.all(
            counter.count_to(duration=1.8, ease=Ease.out_expo),
            streamer.stream_tokens(duration=1.8),
        )
        card.float_idle(amplitude=6, speed=1.2)
        yield scene.wait(1.0)
    
    # 5. Audio SFX synthesis
    audio_sfx = WhooshDesignerSuite.cinematic_passby(duration=1.2)
    assert_valid_audio_array(audio_sfx)
    
    # 6. Validation & Storyboard
    report = scene.validate()
    assert report is not None
    
    storyboard_path = os.path.join(temp_output_dir, "storyboard_saas_launch.png")
    assert_scene_storyboard_valid(scene, storyboard_path)


# ============================================================================
# Scenario 2: Fintech Crypto Card Demo
# ============================================================================

def test_scenario_fintech_crypto_card(temp_output_dir):
    scene = Scene(
        width=1920,
        height=1080,
        fps=60,
        duration=4.5,
        background=colors.BLACK,
    )
    
    bg = CyberGridHorizon(grid_color=colors.CYAN, perspective=0.85)
    monitor = SuperUltrawideMonitorFrame(width=1600, height=700, curve_depth=45.0)
    
    chart_data = [
        {"open": 64000, "high": 68500, "low": 63200, "close": 67900},
        {"open": 67900, "high": 71200, "low": 66800, "close": 70500},
        {"open": 70500, "high": 74800, "low": 69800, "close": 74200},
    ]
    chart = CandlestickChartPro(ohlc_data=chart_data, width=1400, height=500)
    neon_title = RealisticNeonStrobeSign("BITCOIN ALL-TIME HIGH", color=colors.CYAN)
    
    monitor.add_screen(chart)
    scene.add(bg)
    scene.add(monitor)
    scene.add(neon_title)
    scene.add_post_fx(AnamorphicStreakFlare(threshold=0.8, streak_length=600.0))
    
    @scene.animate
    def main():
        yield neon_title.ignite(duration=1.0)
        yield chart.draw_bars(duration=2.0)
        yield scene.wait(1.0)
    
    boom = ImpactSubSuite.cinematic_trailer_sub_drop(decay=2.0)
    assert_valid_audio_array(boom)
    
    report = scene.validate()
    assert report is not None
    
    storyboard_path = os.path.join(temp_output_dir, "storyboard_crypto_demo.png")
    assert_scene_storyboard_valid(scene, storyboard_path)


# ============================================================================
# Scenario 3: Developer CLI Launch Pipeline
# ============================================================================

def test_scenario_developer_cli_launch(temp_output_dir):
    scene = Scene(
        width=1920,
        height=1080,
        fps=60,
        duration=4.0,
        background=colors.SLATE_900,
    )
    
    arcade = RetroArcadeCrtCabinet()
    term = PhosphorTerminalTypewriter(prompt="user@vibmo:~$ ")
    code_box = CodeSandboxPlayground(code="import vibmo\nscene = Scene(1920, 1080)\nscene.render('output.mp4')")
    
    arcade.add_screen(term)
    scene.add(arcade)
    scene.add(code_box)
    scene.add_post_fx(CrtPhosphorBloomShader(bloom=1.4, scanlines=True))
    
    @scene.animate
    def main():
        yield term.typewriter("npm install -g vibmo-cli", speed=35.0)
        yield code_box.run_execution(duration=1.2)
        yield scene.wait(1.0)
    
    typing_sfx = KeyboardFoleySuite.mechanical_keystroke(switch="blue")
    assert_valid_audio_array(typing_sfx)
    
    report = scene.validate()
    assert report is not None
    
    storyboard_path = os.path.join(temp_output_dir, "storyboard_cli_launch.png")
    assert_scene_storyboard_valid(scene, storyboard_path)


# ============================================================================
# Scenario 4: AI Venture Pitch Deck
# ============================================================================

def test_scenario_ai_pitch_deck(temp_output_dir):
    scene = Scene(
        width=1920,
        height=1080,
        fps=60,
        duration=5.0,
        background=colors.DARK_NAVY,
    )
    
    bg = MinimalStudioInfinity(rim_light=True)
    tot = TreeOfThoughtTree()
    vec = VectorEmbeddingsVisualizer(num_points=60)
    pricing = PricingTierMatrix()
    odo = OdometerTumblerCounter(start_val=0, end_val=10000000, prefix="$", suffix=" ARR")
    
    scene.add(bg)
    scene.add(tot)
    scene.add(vec)
    scene.add(pricing)
    scene.add(odo)
    
    @scene.animate
    def main():
        yield tot.expand_branch(0, duration=1.2)
        yield scene.all(
            vec.rotate_cluster(duration=1.5),
            odo.roll_to(10000000, duration=1.8),
            pricing.highlight_tier("Pro", duration=1.0),
        )
        yield scene.wait(1.0)
    
    drone_sfx = AmbientDroneSuite.sci_fi_deep_space_drone(duration=5.0)
    assert_valid_audio_array(drone_sfx)
    
    report = scene.validate()
    assert report is not None
    
    storyboard_path = os.path.join(temp_output_dir, "storyboard_ai_pitch.png")
    assert_scene_storyboard_valid(scene, storyboard_path)


# ============================================================================
# Scenario 5: Social Media Dynamic Audiogram
# ============================================================================

def test_scenario_social_audiogram(temp_output_dir):
    scene = Scene(
        width=1080,
        height=1920,
        fps=60,
        duration=4.0,
        background=colors.BLACK,
    )
    
    watch = RuggedSmartwatchFrame()
    stream = FlowingStreamgraphArea()
    title = KineticText("EPISODE 42: THE MOTION ERA", font_size=36, color=colors.CYAN)
    
    watch.add_screen(stream)
    scene.add(watch)
    scene.add(title)
    
    @scene.animate
    def main():
        yield title.reveal_characters(stagger=0.03)
        yield stream.undulate_stream(duration=2.0)
        yield scene.wait(1.0)
    
    crackle_sfx = VinylCrackleSuite.vintage_turntable_hiss(duration=4.0)
    assert_valid_audio_array(crackle_sfx)
    
    report = scene.validate()
    assert report is not None
    
    storyboard_path = os.path.join(temp_output_dir, "storyboard_social_audiogram.png")
    assert_scene_storyboard_valid(scene, storyboard_path)
