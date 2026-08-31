"""
Tier 1 E2E Tests: Financial, 3D Spatial & Motion Charts (Section 5).
Covers all 14 chart engines with >=5 tests per feature.
"""

import pytest
import cairo
from .conftest import assert_cairo_draw_safe

from vibmo.scene.scene import Scene
from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D

from vibmo.charts.chart_candlestick_pro_suite import CandlestickChartPro, ProCandlestickChart
from vibmo.charts.chart_sunburst_radial_suite import SunburstRadialHierarchy, ExpandingRingArc
from vibmo.charts.chart_speedometer_hud_suite import SpeedometerNeedleGauge, DigitalSpeedNumberTicker
from vibmo.charts.chart_surface_mesh_3d_suite import Animated3DSurfaceMesh, ElevationColorGradient
from vibmo.charts.chart_bubble_scatter_suite import MultiVariableBubbleScatter, BubbleScaleLegend
from vibmo.charts.chart_waterfall_flow_suite import WaterfallCostChart, CumulativeBridgeConnector
from vibmo.charts.chart_choropleth_map_suite import ChoroplethWorldMiniMap, RegionalHeatPolygon
from vibmo.charts.chart_violin_density_suite import ViolinDistributionPlot, ProbabilityDensityKernel
from vibmo.charts.chart_treemap_market_suite import TreemapMarketCapGrid, ZoomableTreemapTile
from vibmo.charts.chart_sankey_flow_suite import SankeyFlowDiagram, FlowRibbonNode
from vibmo.charts.chart_streamgraph_wave_suite import FlowingStreamgraphArea, OrganicWaveBand
from vibmo.charts.chart_polar_rose_suite import PolarRoseAreaChart, ConcentricRadiusRings
from vibmo.charts.chart_box_whisker_suite import StatisticalBoxPlot, InterquartileBox
from vibmo.charts.chart_pareto_curve_suite import ParetoAnalysisChart, Cumulative8020Curve


# ============================================================================
# 1. Pro Candlestick Chart (>=5 tests)
# ============================================================================

def test_candlestick_chart_defaults():
    chart = CandlestickChartPro()
    assert_cairo_draw_safe(chart)


def test_candlestick_chart_sample_ohlc():
    data = [
        {"open": 100.0, "high": 110.0, "low": 95.0, "close": 108.0},
        {"open": 108.0, "high": 115.0, "low": 105.0, "close": 102.0},
        {"open": 102.0, "high": 120.0, "low": 100.0, "close": 118.0},
    ]
    chart = CandlestickChartPro(data=data)
    assert_cairo_draw_safe(chart)


def test_candlestick_chart_draw_bars_action():
    data = [{"open": 50.0, "high": 55.0, "low": 48.0, "close": 52.0}]
    chart = CandlestickChartPro(data=data)
    action = chart.draw_bars(duration=1.2)
    assert action is not None
    assert_cairo_draw_safe(chart, timestamps=(0.0, 0.6, 1.2))


def test_candlestick_chart_alias():
    chart = ProCandlestickChart()
    assert_cairo_draw_safe(chart)


def test_candlestick_chart_flat_range():
    flat_data = [{"open": 100.0, "high": 100.0, "low": 100.0, "close": 100.0}]
    chart = CandlestickChartPro(data=flat_data)
    assert_cairo_draw_safe(chart)


# ============================================================================
# 2. Radial Sunburst Hierarchy (>=5 tests)
# ============================================================================

def test_sunburst_hierarchy_defaults():
    sun = SunburstRadialHierarchy()
    assert_cairo_draw_safe(sun)


def test_sunburst_hierarchy_expand_rings():
    sun = SunburstRadialHierarchy()
    action = sun.expand_rings(duration=1.5)
    assert action is not None
    assert_cairo_draw_safe(sun)


def test_sunburst_hierarchy_custom_tree():
    tree = {
        "name": "Global",
        "children": [
            {"name": "Engineering", "value": 40},
            {"name": "Product", "value": 30},
            {"name": "Marketing", "value": 30},
        ]
    }
    sun = SunburstRadialHierarchy(data=tree)
    assert_cairo_draw_safe(sun)


def test_sunburst_expanding_ring_arc():
    ring = ExpandingRingArc()
    assert_cairo_draw_safe(ring)


def test_sunburst_hierarchy_progression():
    sun = SunburstRadialHierarchy()
    assert_cairo_draw_safe(sun, timestamps=(0.0, 0.5, 1.0, 2.0))


# ============================================================================
# 3. Speedometer KPI Gauge (>=5 tests)
# ============================================================================

def test_speedometer_gauge_defaults():
    gauge = SpeedometerNeedleGauge()
    assert_cairo_draw_safe(gauge)


def test_speedometer_gauge_needle_to():
    gauge = SpeedometerNeedleGauge(min_val=0, max_val=220)
    action = gauge.needle_to(140.0, duration=1.0)
    assert action is not None
    assert_cairo_draw_safe(gauge)


def test_speedometer_gauge_min_max_bounds():
    gauge_min = SpeedometerNeedleGauge(value=0.0)
    gauge_max = SpeedometerNeedleGauge(value=220.0)
    assert_cairo_draw_safe(gauge_min)
    assert_cairo_draw_safe(gauge_max)


def test_digital_speed_ticker_alias():
    ticker = DigitalSpeedNumberTicker()
    assert_cairo_draw_safe(ticker)


def test_speedometer_gauge_theme_and_colors():
    gauge = SpeedometerNeedleGauge(accent_color=colors.EMERALD, warning_color=colors.AMBER)
    assert_cairo_draw_safe(gauge)


# ============================================================================
# 4. 3D Surface Topology Mesh (>=5 tests)
# ============================================================================

def test_surface_mesh_3d_defaults():
    mesh = Animated3DSurfaceMesh()
    assert_cairo_draw_safe(mesh)


def test_surface_mesh_3d_rotate():
    mesh = Animated3DSurfaceMesh()
    action = mesh.rotate_3d(duration=2.0)
    assert action is not None
    assert_cairo_draw_safe(mesh)


def test_surface_mesh_3d_resolution():
    mesh_low = Animated3DSurfaceMesh(grid_resolution=8)
    mesh_high = Animated3DSurfaceMesh(grid_resolution=24)
    assert_cairo_draw_safe(mesh_low)
    assert_cairo_draw_safe(mesh_high)


def test_elevation_color_gradient_node():
    grad = ElevationColorGradient()
    assert grad.get_color(0.5) is not None


def test_surface_mesh_3d_multi_timestamp():
    mesh = Animated3DSurfaceMesh()
    assert_cairo_draw_safe(mesh, timestamps=(0.0, 1.0, 2.0, 3.0))


# ============================================================================
# 5. 4D Bubble Scatter Plot (>=5 tests)
# ============================================================================

def test_bubble_scatter_defaults():
    scatter = MultiVariableBubbleScatter()
    assert_cairo_draw_safe(scatter)


def test_bubble_scatter_grow_bubbles():
    scatter = MultiVariableBubbleScatter()
    action = scatter.grow_bubbles(duration=1.5)
    assert action is not None
    assert_cairo_draw_safe(scatter)


def test_bubble_scatter_points_data():
    points = [
        {"x": 10.0, "y": 20.0, "size": 15.0, "color": colors.CYAN},
        {"x": 40.0, "y": 80.0, "size": 30.0, "color": colors.ROSE},
    ]
    scatter = MultiVariableBubbleScatter(points=points)
    assert_cairo_draw_safe(scatter)


def test_bubble_scale_legend():
    legend = BubbleScaleLegend(values=[10.0, 50.0, 100.0])
    assert_cairo_draw_safe(legend)


def test_bubble_scatter_dimensions():
    scatter = MultiVariableBubbleScatter(width=1000, height=500)
    assert_cairo_draw_safe(scatter)


# ============================================================================
# 6. Waterfall Variance Chart (>=5 tests)
# ============================================================================

def test_waterfall_chart_defaults():
    waterfall = WaterfallCostChart(steps=[100, -30, 50, -20, 100])
    assert_cairo_draw_safe(waterfall)


def test_waterfall_chart_reveal_steps():
    waterfall = WaterfallCostChart(steps=[100, -30, 50, -20, 100])
    action = waterfall.reveal_steps(duration=1.5)
    assert action is not None
    assert_cairo_draw_safe(waterfall)


def test_waterfall_chart_custom_steps():
    steps = [
        {"label": "Gross Rev", "amount": 100000, "is_total": False},
        {"label": "COGS", "amount": -30000, "is_total": False},
        {"label": "Net Profit", "amount": 70000, "is_total": True},
    ]
    waterfall = WaterfallCostChart(steps=steps)
    assert_cairo_draw_safe(waterfall)


def test_cumulative_bridge_connector():
    bridge = CumulativeBridgeConnector(start_point=Vector2D(0, 0), end_point=Vector2D(100, 50))
    assert_cairo_draw_safe(bridge)


def test_waterfall_chart_timestamps():
    waterfall = WaterfallCostChart(steps=[100, -30, 50, -20, 100])
    assert_cairo_draw_safe(waterfall, timestamps=(0.0, 0.5, 1.0, 2.0))


# ============================================================================
# 7. Choropleth Geographic Map (>=5 tests)
# ============================================================================

def test_choropleth_map_defaults():
    geo = ChoroplethWorldMiniMap()
    assert_cairo_draw_safe(geo)


def test_choropleth_map_animate_heat():
    geo = ChoroplethWorldMiniMap()
    action = geo.animate_heat_gradient(duration=1.2)
    assert action is not None
    assert_cairo_draw_safe(geo)


def test_choropleth_map_regional_heat_node():
    region = RegionalHeatPolygon(coordinates=[(0, 0), (100, 0), (100, 100), (0, 100)], value=0.75)
    assert_cairo_draw_safe(region)


def test_choropleth_map_custom_data():
    geo = ChoroplethWorldMiniMap(region_values={"NA": 0.8, "EU": 0.6, "APAC": 0.9})
    assert_cairo_draw_safe(geo)


def test_choropleth_map_multi_time():
    geo = ChoroplethWorldMiniMap()
    assert_cairo_draw_safe(geo, timestamps=(0.0, 0.6, 1.2))


# ============================================================================
# 8. Violin Probability Density (>=5 tests)
# ============================================================================

def test_violin_density_defaults():
    violin = ViolinDistributionPlot()
    assert_cairo_draw_safe(violin)


def test_violin_density_expand_kde():
    violin = ViolinDistributionPlot()
    action = violin.expand_kde(duration=1.0)
    assert action is not None
    assert_cairo_draw_safe(violin)


def test_probability_density_kernel():
    kernel = ProbabilityDensityKernel(data=[1.0, 2.0, 2.5, 3.0, 3.2, 4.0, 5.0])
    assert_cairo_draw_safe(kernel)


def test_violin_density_distributions():
    dists = [
        [1.0, 2.0, 2.5, 3.0, 3.2, 4.0, 5.0],
        [2.0, 3.0, 3.5, 3.8, 4.2, 6.0, 7.0],
    ]
    violin = ViolinDistributionPlot(distributions=dists)
    assert_cairo_draw_safe(violin)


def test_violin_density_timestamps():
    violin = ViolinDistributionPlot()
    assert_cairo_draw_safe(violin, timestamps=(0.0, 0.5, 1.0))


# ============================================================================
# 9. Market Cap Treemap (>=5 tests)
# ============================================================================

def test_market_cap_treemap_defaults():
    treemap = TreemapMarketCapGrid()
    assert_cairo_draw_safe(treemap)


def test_market_cap_treemap_zoom_sector():
    treemap = TreemapMarketCapGrid()
    action = treemap.zoom_sector("Tech", duration=1.0)
    assert action is not None
    assert_cairo_draw_safe(treemap)


def test_zoomable_treemap_tile():
    tile = ZoomableTreemapTile(ticker="AAPL", market_cap=3000.0, performance=0.05, width=200.0, height=150.0)
    assert_cairo_draw_safe(tile)


def test_market_cap_treemap_custom_stocks():
    stocks = [
        {"ticker": "NVDA", "cap": 3000, "change": 0.04, "sector": "Semiconductors"},
        {"ticker": "AAPL", "cap": 3200, "change": -0.01, "sector": "Hardware"},
    ]
    treemap = TreemapMarketCapGrid(stocks=stocks)
    assert_cairo_draw_safe(treemap)


def test_market_cap_treemap_dimensions():
    treemap = TreemapMarketCapGrid(width=1200, height=700)
    assert_cairo_draw_safe(treemap)


# ============================================================================
# 10. Sankey Flow Diagram (>=5 tests)
# ============================================================================

def test_sankey_flow_defaults():
    sankey = SankeyFlowDiagram()
    assert_cairo_draw_safe(sankey)


def test_sankey_flow_animate_current():
    sankey = SankeyFlowDiagram()
    action = sankey.animate_flow_current(duration=1.5)
    assert action is not None
    assert_cairo_draw_safe(sankey)


def test_sankey_flow_ribbon_node():
    ribbon = FlowRibbonNode(label="Revenue", value=500.0, height=100.0)
    assert_cairo_draw_safe(ribbon)


def test_sankey_flow_custom_links():
    links = [
        {"source": "Inbound Traffic", "target": "Landing Page", "value": 100},
        {"source": "Landing Page", "target": "Sign Up", "value": 35},
        {"source": "Landing Page", "target": "Bounce", "value": 65},
    ]
    sankey = SankeyFlowDiagram(links=links)
    assert_cairo_draw_safe(sankey)


def test_sankey_flow_time_evolution():
    sankey = SankeyFlowDiagram()
    assert_cairo_draw_safe(sankey, timestamps=(0.0, 0.75, 1.5))


# ============================================================================
# 11. Organic Wave Streamgraph (>=5 tests)
# ============================================================================

def test_wave_streamgraph_defaults():
    stream = FlowingStreamgraphArea()
    assert_cairo_draw_safe(stream)


def test_wave_streamgraph_undulate():
    stream = FlowingStreamgraphArea()
    action = stream.undulate_stream(duration=2.0)
    assert action is not None
    assert_cairo_draw_safe(stream)


def test_organic_wave_band_node():
    band = OrganicWaveBand()
    assert_cairo_draw_safe(band)


def test_wave_streamgraph_custom_series():
    series = [
        [10, 25, 40, 30, 60, 80],
        [20, 15, 30, 45, 50, 70],
    ]
    stream = FlowingStreamgraphArea(series=series)
    assert_cairo_draw_safe(stream)


def test_wave_streamgraph_timestamps():
    stream = FlowingStreamgraphArea()
    assert_cairo_draw_safe(stream, timestamps=(0.0, 1.0, 2.0, 3.0))


# ============================================================================
# 12. Polar Rose Coxcomb Chart (>=5 tests)
# ============================================================================

def test_polar_rose_defaults():
    rose = PolarRoseAreaChart()
    assert_cairo_draw_safe(rose)


def test_polar_rose_bloom_wedges():
    rose = PolarRoseAreaChart()
    action = rose.bloom_wedges(duration=1.2)
    assert action is not None
    assert_cairo_draw_safe(rose)


def test_concentric_radius_rings():
    rings = ConcentricRadiusRings(max_value=100.0, max_radius=200.0)
    assert_cairo_draw_safe(rings)


def test_polar_rose_custom_sectors():
    sectors = [
        {"label": "Jan", "value": 45},
        {"label": "Feb", "value": 80},
        {"label": "Mar", "value": 60},
        {"label": "Apr", "value": 95},
    ]
    rose = PolarRoseAreaChart(sectors=sectors)
    assert_cairo_draw_safe(rose)


def test_polar_rose_colors():
    rose = PolarRoseAreaChart(palette=[colors.CYAN, colors.ROSE, colors.AMBER])
    assert_cairo_draw_safe(rose)


# ============================================================================
# 13. Box-and-Whisker Plot (>=5 tests)
# ============================================================================

def test_box_and_whisker_defaults():
    box = StatisticalBoxPlot(datasets=[[10, 20, 35, 50, 70], [15, 30, 48, 65, 85]])
    assert_cairo_draw_safe(box)


def test_box_and_whisker_extend_whiskers():
    box = StatisticalBoxPlot(datasets=[[10, 20, 35, 50, 70], [15, 30, 48, 65, 85]])
    action = box.extend_whiskers(duration=1.0)
    assert action is not None
    assert_cairo_draw_safe(box)


def test_interquartile_box_node():
    iq_box = InterquartileBox(q1=20.0, median=35.0, q3=50.0)
    assert_cairo_draw_safe(iq_box)


def test_box_and_whisker_custom_datasets():
    datasets = [
        [10, 20, 35, 50, 70],
        [15, 30, 48, 65, 85],
    ]
    box = StatisticalBoxPlot(datasets=datasets)
    assert_cairo_draw_safe(box)


def test_box_and_whisker_timestamps():
    box = StatisticalBoxPlot(datasets=[[10, 20, 35, 50, 70], [15, 30, 48, 65, 85]])
    assert_cairo_draw_safe(box, timestamps=(0.0, 0.5, 1.0))


# ============================================================================
# 14. Pareto 80/20 Analysis Chart (>=5 tests)
# ============================================================================

def test_pareto_analysis_defaults():
    pareto = ParetoAnalysisChart()
    assert_cairo_draw_safe(pareto)


def test_pareto_analysis_draw_cutoff():
    pareto = ParetoAnalysisChart()
    action = pareto.draw_80_20_cutoff(duration=1.5)
    assert action is not None
    assert_cairo_draw_safe(pareto)


def test_cumulative_8020_curve_node():
    curve = Cumulative8020Curve(cumulative_data=[0.2, 0.5, 0.7, 0.85, 0.95, 1.0])
    assert_cairo_draw_safe(curve)


def test_pareto_analysis_custom_categories():
    categories = [
        {"category": "Feature Requests", "count": 120},
        {"category": "Bug Reports", "count": 80},
        {"category": "Billing", "count": 25},
        {"category": "Other", "count": 10},
    ]
    pareto = ParetoAnalysisChart(categories=categories)
    assert_cairo_draw_safe(pareto)


def test_pareto_analysis_time_progression():
    pareto = ParetoAnalysisChart()
    assert_cairo_draw_safe(pareto, timestamps=(0.0, 0.75, 1.5))
