"""
Tier 2 E2E Tests: Boundary Value Analysis & Corner Cases.
Validates system robustness across empty datasets, extreme ranges, zero/negative bounds,
extreme durations, max canvas resolutions, and numerical singularity guards.
"""

import math
import pytest
import numpy as np
import cairo
from .conftest import assert_valid_audio_array, assert_cairo_draw_safe

from vibmo.scene.scene import Scene
from vibmo.primitives.rect import Rect
from vibmo.typography.text import Text
from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal

# Import components from across suites
from vibmo.charts.chart_candlestick_pro_suite import CandlestickChartPro
from vibmo.charts.chart_sunburst_radial_suite import SunburstRadialHierarchy
from vibmo.charts.chart_speedometer_hud_suite import SpeedometerNeedleGauge
from vibmo.charts.chart_surface_mesh_3d_suite import Animated3DSurfaceMesh
from vibmo.charts.chart_bubble_scatter_suite import MultiVariableBubbleScatter
from vibmo.charts.chart_waterfall_flow_suite import WaterfallCostChart
from vibmo.charts.chart_sankey_flow_suite import SankeyFlowDiagram
from vibmo.charts.chart_streamgraph_wave_suite import FlowingStreamgraphArea
from vibmo.charts.chart_treemap_market_suite import TreemapMarketCapGrid
from vibmo.charts.chart_violin_density_suite import ViolinDistributionPlot
from vibmo.charts.chart_box_whisker_suite import StatisticalBoxPlot
from vibmo.charts.chart_pareto_curve_suite import ParetoAnalysisChart

from vibmo.product.ai.ui_token_streamer_suite import StreamingTokenOutput
from vibmo.product.ai.ui_tree_of_thought_suite import TreeOfThoughtTree
from vibmo.product.ai.ui_diffusion_canvas_suite import DiffusionCanvas
from vibmo.product.ai.ui_embeddings_space_suite import VectorEmbeddingsVisualizer
from vibmo.product.ai.ui_pricing_matrix_suite import PricingTierMatrix
from vibmo.product.ai.ui_api_key_vault_suite import ApiKeyVault
from vibmo.product.ai.ui_git_pr_timeline_suite import GitPrTimeline
from vibmo.product.ai.ui_quota_meter_suite import TokenQuotaMeter
from vibmo.product.ai.ui_code_sandbox_suite import CodeSandboxPlayground
from vibmo.product.ai.ui_prompt_diff_suite import PromptDiffViewer

from vibmo.typography.kinetic.typo_glitch_decryptor_suite import GlitchDecryptorText
from vibmo.typography.kinetic.typo_liquid_wave_suite import LiquidWaveText
from vibmo.typography.kinetic.typo_split_flap_suite import SplitFlapAirportBoard
from vibmo.typography.kinetic.typo_odometer_tumbler_suite import OdometerTumblerCounter
from vibmo.typography.kinetic.typo_terminal_typewriter_suite import PhosphorTerminalTypewriter

from vibmo.product.hardware.hw_foldable_device_suite import FoldableDeviceFrame
from vibmo.product.hardware.hw_super_ultrawide_suite import SuperUltrawideMonitorFrame
from vibmo.product.hardware.hw_cctv_surveillance_suite import CctvQuadViewOverlay

from vibmo.audio.generators.sfx_whoosh_designer_suite import WhooshDesignerSuite
from vibmo.audio.generators.sfx_ambient_drone_suite import AmbientDroneSuite
from vibmo.audio.generators.sfx_riser_tension_suite import RiserTensionSuite


# ============================================================================
# 1. Empty Datasets & Zero Collections
# ============================================================================

def test_candlestick_empty_data():
    chart = CandlestickChartPro(data=[])
    assert_cairo_draw_safe(chart)


def test_sunburst_empty_tree():
    sun = SunburstRadialHierarchy(data={})
    assert_cairo_draw_safe(sun)


def test_bubble_scatter_empty_points():
    scatter = MultiVariableBubbleScatter(points=[])
    assert_cairo_draw_safe(scatter)


def test_waterfall_empty_steps():
    waterfall = WaterfallCostChart(steps=[])
    assert_cairo_draw_safe(waterfall)


def test_sankey_empty_links():
    sankey = SankeyFlowDiagram(links=[])
    assert_cairo_draw_safe(sankey)


def test_streamgraph_empty_series():
    stream = FlowingStreamgraphArea(series=[])
    assert_cairo_draw_safe(stream)


def test_treemap_empty_stocks():
    treemap = TreemapMarketCapGrid(stocks=[])
    assert_cairo_draw_safe(treemap)


def test_violin_empty_distributions():
    violin = ViolinDistributionPlot(distributions=[])
    assert_cairo_draw_safe(violin)


def test_box_plot_empty_datasets():
    box = StatisticalBoxPlot(datasets=[])
    assert_cairo_draw_safe(box)


def test_pareto_empty_categories():
    pareto = ParetoAnalysisChart(categories=[])
    assert_cairo_draw_safe(pareto)


# ============================================================================
# 2. Single-Item Datasets & Minimal Structures
# ============================================================================

def test_candlestick_single_candle():
    chart = CandlestickChartPro(data=[{"open": 100, "high": 105, "low": 98, "close": 102}])
    assert_cairo_draw_safe(chart)


def test_bubble_scatter_single_point():
    scatter = MultiVariableBubbleScatter(points=[{"x": 10, "y": 20, "size": 15, "color": colors.CYAN}])
    assert_cairo_draw_safe(scatter)


def test_waterfall_single_step():
    waterfall = WaterfallCostChart(steps=[{"label": "Revenue", "amount": 50000, "is_total": True}])
    assert_cairo_draw_safe(waterfall)


def test_split_flap_single_character():
    board = SplitFlapAirportBoard(rows=1, cols=1)
    action = board.flip_to(["A"])
    assert action is not None
    assert_cairo_draw_safe(board)


def test_token_streamer_single_character():
    streamer = StreamingTokenOutput(text="X")
    assert_cairo_draw_safe(streamer)


# ============================================================================
# 3. Zero / Flat / Negative Ranges & Numerical Singularity Guards
# ============================================================================

def test_candlestick_flat_price_singularity():
    # All prices are identical: max_p == min_p -> zero range guard
    chart = CandlestickChartPro(data=[
        {"open": 50.0, "high": 50.0, "low": 50.0, "close": 50.0},
        {"open": 50.0, "high": 50.0, "low": 50.0, "close": 50.0},
    ])
    assert_cairo_draw_safe(chart)


def test_speedometer_zero_range():
    gauge = SpeedometerNeedleGauge(min_val=0, max_val=0, value=0)
    assert_cairo_draw_safe(gauge)


def test_speedometer_needle_beyond_bounds():
    gauge = SpeedometerNeedleGauge(min_val=0, max_val=100)
    action1 = gauge.needle_to(150.0)
    action2 = gauge.needle_to(-50.0)
    assert action1 is not None and action2 is not None
    assert_cairo_draw_safe(gauge)


def test_token_quota_zero_total_and_overflow():
    meter_zero = TokenQuotaMeter(used=0, total=0)
    meter_over = TokenQuotaMeter(used=150000, total=100000)
    assert_cairo_draw_safe(meter_zero)
    assert_cairo_draw_safe(meter_over)


def test_odometer_negative_and_zero_values():
    odo_neg = OdometerTumblerCounter(start_val=-100, end_val=500)
    odo_zero = OdometerTumblerCounter(start_val=0, end_val=0)
    assert_cairo_draw_safe(odo_neg)
    assert_cairo_draw_safe(odo_zero)


# ============================================================================
# 4. Extreme Durations & Timing Limits
# ============================================================================

def test_audio_ultra_short_duration():
    audio = WhooshDesignerSuite.cinematic_passby(duration=0.05)
    assert_valid_audio_array(audio, min_duration=0.04)


def test_audio_long_drone_duration():
    audio = AmbientDroneSuite.sci_fi_deep_space_drone(duration=10.0)
    assert_valid_audio_array(audio, min_duration=9.0)


def test_scene_zero_duration_action(scene_1080p):
    text = Text("Instant Action")
    scene_1080p.add(text)
    action = text.opacity.to(1.0, duration=0.0)
    assert action is not None


def test_scene_action_at_boundary_of_duration():
    scene = Scene(width=1920, height=1080, duration=4.0)
    text = Text("Boundary")
    scene.add(text)
    # Action ends precisely at duration (delay 2.0 + duration 2.0 = 4.0)
    action = text.opacity.to(0.0, delay=2.0, duration=2.0)
    assert action is not None
    report = scene.validate()
    assert report is not None


# ============================================================================
# 5. Extreme Canvas Dimensions & Scales
# ============================================================================

def test_canvas_8k_resolution():
    scene_8k = Scene(width=7680, height=4320, duration=1.0)
    rect = Rect(width=4000, height=2000, color=colors.CYAN)
    scene_8k.add(rect)
    assert_cairo_draw_safe(rect, width=7680, height=4320)


def test_canvas_sub_pixel_dimensions():
    rect = Rect(width=0.5, height=0.5, color=colors.WHITE)
    assert_cairo_draw_safe(rect, width=10, height=10)


def test_hardware_frame_zero_fold_angle():
    frame = FoldableDeviceFrame(fold_angle=0.0)
    assert_cairo_draw_safe(frame)


def test_super_ultrawide_zero_curve():
    monitor = SuperUltrawideMonitorFrame(curve_depth=0.0)
    assert_cairo_draw_safe(monitor)


# ============================================================================
# 6. String Escaping & Special Character Resilience
# ============================================================================

def test_kinetic_text_special_characters():
    spec_strings = [
        "Special: <script>alert(1)</script>",
        "Math: \u2211 \u222b \u2248 \u03c0 \u221e",
        "Control Chars: \t \n \r",
        "Quotes: \" ' ` $ # @ ! % & * ()",
        "Emoji: \U0001F680 \U0001F525 \u2728 \U0001F4C8",
    ]
    for s in spec_strings:
        text = GlitchDecryptorText(s)
        assert_cairo_draw_safe(text)


def test_prompt_diff_empty_and_special_strings():
    diff = PromptDiffViewer(v1="", v2="<tag> \n $100% {key: 'val'}")
    assert_cairo_draw_safe(diff)


def test_terminal_typewriter_shell_metacharacters():
    term = PhosphorTerminalTypewriter()
    action = term.typewriter("curl -s https://api.vibmo.io | grep 'status: 200' && echo $SUCCESS")
    assert action is not None
    assert_cairo_draw_safe(term)
