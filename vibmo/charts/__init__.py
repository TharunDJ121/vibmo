"""Financial, 3D spatial and motion chart suites."""
from __future__ import annotations

from vibmo.charts.chart_box_whisker_suite import (
    AnimatedOutlierPings,
    BoxAndWhiskerPlot,
    InterquartileBox,
    OutlierDotNode,
    StatisticalBoxPlot,
    WhiskersErrorBars,
)
from vibmo.charts.chart_bubble_scatter_suite import (
    BubbleScaleLegend,
    BubbleScatter4DPlot,
    MotionTrailBubble,
    MultiVariableBubbleScatter,
    QuadrantPartitionLines,
    RegressionCurve,
)
from vibmo.charts.chart_candlestick_pro_suite import (
    CandlestickChartPro,
    CrosshairPriceTracker,
    MovingAverageCurves,
    ProCandlestickChart,
    VolumeBarSubplot,
    VolumeProfileOverlay,
)
from vibmo.charts.chart_choropleth_map_suite import (
    ChoroplethGeoMap,
    ChoroplethWorldMiniMap,
    CountryRankLeaderboard,
    GeoDataTooltip,
    RegionalHeatPolygon,
    RegionPolygonNode,
)
from vibmo.charts.chart_pareto_curve_suite import (
    CriticalThresholdLine,
    Cumulative8020Curve,
    CumulativeCurve,
    FrequencyBarChart,
    ParetoAnalysisChart,
)
from vibmo.charts.chart_polar_rose_suite import (
    AngularCategoryAxis,
    ConcentricRadiusRings,
    PolarRoseAreaChart,
    PolarRoseCoxcombChart,
    ProportionalRadiusWedge,
    RoseWedgeNode,
)
from vibmo.charts.chart_sankey_flow_suite import (
    BezierFlowRibbon,
    ConversionDropoffIndicator,
    FlowRibbonNode,
    RevenuePathHighlighter,
    SankeyFlowDiagram,
)
from vibmo.charts.chart_speedometer_hud_suite import (
    DigitalSpeedNumberTicker,
    KpiMetricGauge,
    RedlineRpmArc,
    SpeedometerHudDial,
    SpeedometerNeedleGauge,
    TurboBoostBar,
)
from vibmo.charts.chart_streamgraph_wave_suite import (
    FlowingStreamgraphArea,
    OrganicWaveBand,
    OrganicWaveStreamgraph,
    StackedWaveRibbon,
    StreamgraphLegend,
    TimeAxisScrubber,
)
from vibmo.charts.chart_sunburst_radial_suite import (
    BreadcrumbPathTrail,
    ExpandingRingArc,
    RadialSliceHighlight,
    RadialSunburstHierarchy,
    SunburstRadialHierarchy,
    SunburstRing,
)
from vibmo.charts.chart_surface_mesh_3d_suite import (
    Animated3DSurfaceMesh,
    CameraRotationRig,
    ElevationColorGradient,
    SurfaceMesh3DPlot,
    WireframeContourGrid,
    WireframeTopology,
)
from vibmo.charts.chart_treemap_market_suite import (
    MarketCapTreemap,
    MarketSectorLegend,
    PercentageDeltaColor,
    TreemapCellNode,
    TreemapMarketCapGrid,
    ZoomableTreemapTile,
)
from vibmo.charts.chart_violin_density_suite import (
    KdeEnvelopeCurve,
    MedianQuartileMarker,
    OutlierJitterDots,
    ProbabilityDensityKernel,
    ViolinDensityPlot,
    ViolinDistributionPlot,
)
from vibmo.charts.chart_waterfall_flow_suite import (
    CumulativeBridgeConnector,
    DeductionColumn,
    FlowBarNode,
    NetGainColumn,
    WaterfallCostChart,
    WaterfallFinancialChart,
)

__all__ = [
    # Box and Whisker
    "AnimatedOutlierPings",
    "BoxAndWhiskerPlot",
    "InterquartileBox",
    "OutlierDotNode",
    "StatisticalBoxPlot",
    "WhiskersErrorBars",
    # Bubble Scatter
    "BubbleScaleLegend",
    "BubbleScatter4DPlot",
    "MotionTrailBubble",
    "MultiVariableBubbleScatter",
    "QuadrantPartitionLines",
    "RegressionCurve",
    # Candlestick
    "CandlestickChartPro",
    "CrosshairPriceTracker",
    "MovingAverageCurves",
    "ProCandlestickChart",
    "VolumeBarSubplot",
    "VolumeProfileOverlay",
    # Choropleth
    "ChoroplethGeoMap",
    "ChoroplethWorldMiniMap",
    "CountryRankLeaderboard",
    "GeoDataTooltip",
    "RegionalHeatPolygon",
    "RegionPolygonNode",
    # Pareto
    "CriticalThresholdLine",
    "Cumulative8020Curve",
    "CumulativeCurve",
    "FrequencyBarChart",
    "ParetoAnalysisChart",
    # Polar Rose
    "AngularCategoryAxis",
    "ConcentricRadiusRings",
    "PolarRoseAreaChart",
    "PolarRoseCoxcombChart",
    "ProportionalRadiusWedge",
    "RoseWedgeNode",
    # Sankey Flow
    "BezierFlowRibbon",
    "ConversionDropoffIndicator",
    "FlowRibbonNode",
    "RevenuePathHighlighter",
    "SankeyFlowDiagram",
    # Speedometer HUD
    "DigitalSpeedNumberTicker",
    "KpiMetricGauge",
    "RedlineRpmArc",
    "SpeedometerHudDial",
    "SpeedometerNeedleGauge",
    "TurboBoostBar",
    # Streamgraph
    "FlowingStreamgraphArea",
    "OrganicWaveBand",
    "OrganicWaveStreamgraph",
    "StackedWaveRibbon",
    "StreamgraphLegend",
    "TimeAxisScrubber",
    # Sunburst
    "BreadcrumbPathTrail",
    "ExpandingRingArc",
    "RadialSliceHighlight",
    "RadialSunburstHierarchy",
    "SunburstRadialHierarchy",
    "SunburstRing",
    # Surface Mesh 3D
    "Animated3DSurfaceMesh",
    "CameraRotationRig",
    "ElevationColorGradient",
    "SurfaceMesh3DPlot",
    "WireframeContourGrid",
    "WireframeTopology",
    # Treemap
    "MarketCapTreemap",
    "MarketSectorLegend",
    "PercentageDeltaColor",
    "TreemapCellNode",
    "TreemapMarketCapGrid",
    "ZoomableTreemapTile",
    # Violin Density
    "KdeEnvelopeCurve",
    "MedianQuartileMarker",
    "OutlierJitterDots",
    "ProbabilityDensityKernel",
    "ViolinDensityPlot",
    "ViolinDistributionPlot",
    # Waterfall Flow
    "CumulativeBridgeConnector",
    "DeductionColumn",
    "FlowBarNode",
    "NetGainColumn",
    "WaterfallCostChart",
    "WaterfallFinancialChart",
]
