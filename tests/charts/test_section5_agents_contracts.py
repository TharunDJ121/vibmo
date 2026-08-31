"""
Comprehensive Verification Tests for Section 5: Financial, 3D Spatial & Motion Charts
Validates all 14 chart suites, child node classes, AGENTS.md recipes, and animation verbs.
"""

import math
import pytest
from unittest.mock import MagicMock

from vibmo.timeline.scheduler import Choreographer
from vibmo.scene.scene import Scene
from vibmo.core.color import colors, Color
from vibmo.charts import (
    CandlestickChartPro,
    VolumeBarSubplot,
    RadialSunburstHierarchy,
    SunburstRing,
    SpeedometerHudDial,
    KpiMetricGauge,
    SurfaceMesh3DPlot,
    WireframeTopology,
    BubbleScatter4DPlot,
    RegressionCurve,
    WaterfallFinancialChart,
    FlowBarNode,
    ChoroplethGeoMap,
    RegionPolygonNode,
    ViolinDensityPlot,
    KdeEnvelopeCurve,
    MarketCapTreemap,
    TreemapCellNode,
    SankeyFlowDiagram,
    BezierFlowRibbon,
    OrganicWaveStreamgraph,
    StackedWaveRibbon,
    PolarRoseCoxcombChart,
    RoseWedgeNode,
    BoxAndWhiskerPlot,
    OutlierDotNode,
    ParetoAnalysisChart,
    CumulativeCurve,
)


@pytest.fixture
def mock_ctx():
    ctx = MagicMock()
    ctx.text_extents.return_value = MagicMock(width=40.0, height=14.0)
    return ctx


# 1. Candlestick & Volume
def test_candlestick_pro_contract(mock_ctx):
    ohlc = [
        {"open": 100, "high": 115, "low": 95, "close": 110, "volume": 12000},
        {"open": 110, "high": 125, "low": 105, "close": 108, "volume": 15000},
        {"open": 108, "high": 120, "low": 102, "close": 118, "volume": 18000},
    ]
    chart = CandlestickChartPro(ohlc_data=ohlc, width=600, height=300)
    vol = VolumeBarSubplot(data=ohlc, width=600, height=100)

    # Test animation verb
    action = chart.draw_bars(duration=1.5)
    assert action is not None

    choreographer = Choreographer()
    duration = choreographer.run(lambda: (yield chart.draw_bars(duration=1.5)))
    assert duration == 1.5
    assert chart.progress.get(1.5) == 1.0

    # Test draw
    chart.draw(mock_ctx, 1.5)
    vol.draw(mock_ctx, 1.5)
    assert mock_ctx.save.called


# 2. Radial Sunburst Hierarchy
def test_radial_sunburst_hierarchy_contract(mock_ctx):
    tree = {
        "name": "Global",
        "children": [
            {
                "name": "Americas",
                "children": [
                    {"name": "US", "value": 50},
                    {"name": "Canada", "value": 20}
                ]
            },
            {
                "name": "EMEA",
                "children": [
                    {"name": "UK", "value": 30},
                    {"name": "Germany", "value": 25}
                ]
            }
        ]
    }
    sun = RadialSunburstHierarchy(tree_data=tree)
    assert len(sun._arcs) >= 4

    ring = SunburstRing(inner_radius=50, outer_radius=100, start_angle=0, end_angle=math.pi)
    assert ring is not None

    choreographer = Choreographer()
    duration = choreographer.run(lambda: (yield sun.expand_rings(duration=1.2)))
    assert duration >= 1.2
    assert all(arc.expand_progress.get(duration) == 1.0 for arc in sun._arcs)

    sun.draw(mock_ctx, 1.5)
    ring.draw(mock_ctx, 1.5)
    assert mock_ctx.save.called


# 3. Speedometer HUD Dial
def test_speedometer_hud_dial_contract(mock_ctx):
    gauge = SpeedometerHudDial(min_val=0, max_val=220, radius=120)
    kpi = KpiMetricGauge(min_val=0, max_val=100)

    choreographer = Choreographer()
    duration = choreographer.run(lambda: (yield gauge.needle_to(140, duration=1.0)))
    assert duration == 1.0
    assert gauge.value.get() == 140.0

    gauge.draw(mock_ctx, 1.0)
    kpi.draw(mock_ctx, 1.0)
    assert mock_ctx.stroke.called


# 4. 3D Surface Mesh Plot
def test_surface_mesh_3d_contract(mock_ctx):
    surf = SurfaceMesh3DPlot(fn=lambda x, y: math.sin(x) * math.cos(y), size=8.0, resolution=10)
    wire = WireframeTopology(rig=surf.rig, size=8.0)

    choreographer = Choreographer()
    duration = choreographer.run(lambda: (yield surf.rotate_3d(duration=2.0)))
    assert duration == 2.0

    surf.draw(mock_ctx, 2.0)
    wire.draw(mock_ctx, 2.0)
    assert mock_ctx.save.called


# 5. 4D Bubble Scatter Plot
def test_bubble_scatter_4d_contract(mock_ctx):
    pts = [
        {"x": 10, "y": 20, "z": 5, "color": colors.CYAN},
        {"x": 30, "y": 40, "z": 15, "color": colors.EMERALD},
        {"x": 50, "y": 80, "z": 25, "color": colors.ROSE},
    ]
    scatter = BubbleScatter4DPlot(points=pts, width=800, height=500)
    reg = RegressionCurve(points=pts, width=800, height=500)

    choreographer = Choreographer()
    duration = choreographer.run(lambda: (yield scatter.grow_bubbles(duration=1.0)))
    assert duration == 1.0
    assert scatter.bubble_scale.get(1.0) == 1.0

    scatter.draw(mock_ctx, 1.0)
    reg.draw(mock_ctx, 1.0)
    assert mock_ctx.save.called


# 6. Waterfall Financial Chart
def test_waterfall_financial_chart_contract(mock_ctx):
    steps = [
        {"label": "Revenue", "value": 500},
        {"label": "COGS", "value": -150},
        {"label": "OpEx", "value": -120},
        {"label": "Tax", "value": -40},
    ]
    waterfall = WaterfallFinancialChart(steps=steps, column_width=60, spacing=15)
    bar = FlowBarNode(width=60, height=100, is_gain=True)

    assert len(waterfall.columns) == 5  # 4 steps + 1 total

    choreographer = Choreographer()
    duration = choreographer.run(lambda: (yield waterfall.reveal_steps(duration=1.5)))
    assert duration >= 1.5

    waterfall.draw(mock_ctx, duration)
    bar.draw(mock_ctx, 1.0)
    assert mock_ctx.save.called


# 7. Choropleth Geo Map
def test_choropleth_geo_map_contract(mock_ctx):
    regions = {
        "NA": {"coordinates": [(0, 0), (100, 0), (100, 80), (0, 80)], "value": 0.85},
        "EU": {"coordinates": [(120, 0), (220, 0), (220, 80), (120, 80)], "value": 0.65},
        "APAC": {"coordinates": [(240, 0), (340, 0), (340, 80), (240, 80)], "value": 0.95},
    }
    geo = ChoroplethGeoMap(regions=regions)
    poly = RegionPolygonNode(coordinates=[(0, 0), (50, 0), (50, 50), (0, 50)], value=0.5)

    assert len(geo.polygons) == 3

    choreographer = Choreographer()
    duration = choreographer.run(lambda: (yield geo.animate_heat_gradient(duration=1.5)))
    assert duration == 1.5

    geo.draw(mock_ctx, 1.5)
    poly.draw(mock_ctx, 1.5)
    assert mock_ctx.save.called


# 8. Violin Probability Density Plot
def test_violin_density_plot_contract(mock_ctx):
    distributions = [
        [1.0, 2.0, 2.5, 3.0, 3.2, 3.5, 4.0, 4.5, 5.0, 6.0],
        [3.0, 3.5, 4.0, 4.2, 4.5, 5.0, 5.5, 6.0, 7.0, 8.0],
    ]
    violin = ViolinDensityPlot(distributions=distributions)
    kde = KdeEnvelopeCurve(data=[1.0, 2.0, 3.0, 4.0])

    assert len(violin.kde_nodes) == 2

    choreographer = Choreographer()
    duration = choreographer.run(lambda: (yield violin.expand_kde(duration=1.2)))
    assert duration >= 1.2

    violin.draw(mock_ctx, 1.5)
    kde.draw(mock_ctx, 1.5)
    assert mock_ctx.save.called


# 9. Market Cap Treemap
def test_market_cap_treemap_contract(mock_ctx):
    stocks = {
        "Tech": [
            {"ticker": "AAPL", "market_cap": 3.0e12, "performance": 0.05},
            {"ticker": "MSFT", "market_cap": 2.8e12, "performance": 0.03},
        ],
        "Energy": [
            {"ticker": "XOM", "market_cap": 5.0e11, "performance": -0.02},
        ]
    }
    treemap = MarketCapTreemap(stocks=stocks, width=1000, height=600)
    cell = TreemapCellNode(ticker="NVDA", market_cap=2.5e12, performance=0.08, width=200, height=150)

    assert len(treemap.tiles) == 3

    choreographer = Choreographer()
    duration = choreographer.run(lambda: (yield treemap.zoom_sector("Tech", duration=1.2)))
    assert duration == 1.2

    treemap.draw(mock_ctx, 1.2)
    cell.draw(mock_ctx, 1.2)
    assert mock_ctx.save.called


# 10. Sankey Flow Diagram
def test_sankey_flow_diagram_contract(mock_ctx):
    links = [
        {"source": "Impressions", "target": "Clicks", "value": 500, "dropoff": 50},
        {"source": "Clicks", "target": "Conversions", "value": 200, "dropoff": 30},
    ]
    sankey = SankeyFlowDiagram(links=links, value_scale=0.2)
    ribbon = BezierFlowRibbon(start_pos=(0, 0), end_pos=(200, 100), width=30)

    choreographer = Choreographer()
    duration = choreographer.run(lambda: (yield sankey.animate_flow_current(duration=2.0)))
    assert duration >= 2.0

    sankey.draw(mock_ctx, 2.0)
    ribbon.draw(mock_ctx, 2.0)
    assert mock_ctx.save.called


# 11. Wave Streamgraph
def test_organic_wave_streamgraph_contract(mock_ctx):
    series = [
        [10, 20, 15, 30, 25, 40],
        [15, 25, 20, 35, 30, 45],
        [5, 10, 8, 15, 12, 20],
    ]
    stream = OrganicWaveStreamgraph(series=series, width=800, height=400)
    ribbon = StackedWaveRibbon(bottom_points=[(0, 50), (100, 60)], top_points=[(0, 10), (100, 20)])

    choreographer = Choreographer()
    duration = choreographer.run(lambda: (yield stream.undulate_stream(duration=2.0)))
    assert duration == 2.0

    stream.draw(mock_ctx, 2.0)
    ribbon.draw(mock_ctx, 2.0)
    assert mock_ctx.save.called


# 12. Polar Rose Coxcomb Chart
def test_polar_rose_coxcomb_contract(mock_ctx):
    sectors = [
        {"category": "Jan", "value": 45},
        {"category": "Feb", "value": 60},
        {"category": "Mar", "value": 85},
        {"category": "Apr", "value": 40},
    ]
    rose = PolarRoseCoxcombChart(sectors=sectors, max_radius=180)
    wedge = RoseWedgeNode(value=50, max_value=100, max_radius=150, start_angle=0, end_angle=math.pi / 2)

    assert len(rose.wedges) == 4

    choreographer = Choreographer()
    duration = choreographer.run(lambda: (yield rose.bloom_wedges(duration=1.5)))
    assert duration >= 1.5

    rose.draw(mock_ctx, 1.5)
    wedge.draw(mock_ctx, 1.5)
    assert mock_ctx.save.called


# 13. Box-and-Whisker Plot
def test_box_and_whisker_contract(mock_ctx):
    datasets = [
        [12, 15, 18, 19, 21, 22, 25, 28, 45],
        [30, 32, 35, 38, 40, 42, 45, 48, 50],
    ]
    box = BoxAndWhiskerPlot(datasets=datasets, width=500, height=350)
    dot = OutlierDotNode(outliers=[45.0], x_pos=100.0)

    assert len(box.whiskers) == 2
    assert len(box.boxes) == 2

    choreographer = Choreographer()
    duration = choreographer.run(lambda: (yield box.extend_whiskers(duration=1.2)))
    assert duration >= 1.2

    box.draw(mock_ctx, 1.2)
    dot.draw(mock_ctx, 1.2)
    assert mock_ctx.save.called


# 14. Pareto Analysis Chart
def test_pareto_analysis_contract(mock_ctx):
    categories = [
        ("Defect A", 120),
        ("Defect B", 85),
        ("Defect C", 40),
        ("Defect D", 15),
        ("Defect E", 5),
    ]
    pareto = ParetoAnalysisChart(categories=categories, width=800, height=400)
    curve = CumulativeCurve(cumulative_data=[0.45, 0.77, 0.92, 0.98, 1.0], width=800, height=400)

    choreographer = Choreographer()
    duration = choreographer.run(lambda: (yield pareto.draw_80_20_cutoff(duration=1.5)))
    assert duration >= 1.5

    pareto.draw(mock_ctx, 1.5)
    curve.draw(mock_ctx, 1.5)
    assert mock_ctx.save.called
