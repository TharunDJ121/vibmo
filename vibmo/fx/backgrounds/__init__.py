"""Procedural non-static animated backgrounds."""
from __future__ import annotations

from vibmo.fx.backgrounds.bg_bokeh_light_bubbles import (
    DriftingBokehOrbs,
    BokehLightBubbles,
    AnamorphicLensGleamBackdrop,
    GoldenDustAmbience,
)
from vibmo.fx.backgrounds.bg_circuit_board_traces import (
    PcbCircuitTracesFlow,
    CircuitBoardTraces,
    MicrochipLogicPulse,
    CopperBusCurrentBackdrop,
)
from vibmo.fx.backgrounds.bg_cosmic_nebula import (
    CosmicNebulaBackdrop,
    CosmicNebula,
    StarfieldWarpDrift,
    ConstellationGrid,
)
from vibmo.fx.backgrounds.bg_cyber_grid_horizon import (
    CyberGridHorizon,
    NeonSunBackdrop,
    WireframeMountainHorizon,
)
from vibmo.fx.backgrounds.bg_digital_matrix_rain import (
    _CodeColumn,
    _BaseRainBackdrop,
    DigitalMatrixRainBackdrop,
    DigitalMatrixRain,
    BinaryStreamBackdrop,
    HexCodeColumnBackdrop,
)
from vibmo.fx.backgrounds.bg_fluid_caustics import (
    FluidWaterCaustics,
    FluidCaustics,
    UnderwaterLightRays,
    PrismaticIridescentWaves,
)
from vibmo.fx.backgrounds.bg_geometric_tessellation import (
    VoronoiCellEvolution,
    PenroseTilingFlow,
    HexagonalHoneyGridPulse,
    GeometricTessellation,
)
from vibmo.fx.backgrounds.bg_hyperspace_tunnel import (
    HyperspaceWarpTunnel,
    HyperspaceTunnel,
    HexagonalSpeedTunnel,
    InfiniteZoomVortex,
)
from vibmo.fx.backgrounds.bg_isometric_city_grid import (
    IsometricCityGridBackdrop,
    IsometricCityGrid,
    PulsingDataHighways,
    ServerRackMatrixBackdrop,
)
from vibmo.fx.backgrounds.bg_mesh_gradient_flow import (
    MeshGradientFlow,
    AuroraGradientWave,
    LiquidPlasmaBackdrop,
)
from vibmo.fx.backgrounds.bg_minimal_studio_infinity import (
    AppleStudioInfinityCyc,
    MinimalStudioInfinity,
    SoftStageSpotlightBackdrop,
    FrostedGlassHorizon,
)
from vibmo.fx.backgrounds.bg_particle_constellation import (
    ParticleConstellationNetwork,
    ParticleConstellation,
    SynapseNeuralGraph,
    PlexusDistanceLines,
)
from vibmo.fx.backgrounds.bg_retro_crt_scanlines import (
    CrtPhosphorScanlineBackdrop,
    RetroCrtScanlines,
    TVSignalNoiseStatic,
    VcrBlueScreenGlitch,
)
from vibmo.fx.backgrounds.bg_sunset_horizon_glow import (
    CalifornianSunsetBackdrop,
    SunsetHorizonGlow,
    GoldenHourSkyGradient,
    AtmosphericHazeHorizon,
)
from vibmo.fx.backgrounds.bg_topographic_contours import (
    AnimatedTopographicContours,
    TopographicContours,
    BathymetricMapBackdrop,
    RadarElevationSweep,
)

__all__ = [
    # 15 Core Section 2 Backdrops
    "MeshGradientFlow",
    "CyberGridHorizon",
    "DigitalMatrixRain",
    "FluidCaustics",
    "TopographicContours",
    "CircuitBoardTraces",
    "CosmicNebula",
    "RetroCrtScanlines",
    "SunsetHorizonGlow",
    "GeometricTessellation",
    "BokehLightBubbles",
    "HyperspaceTunnel",
    "MinimalStudioInfinity",
    "IsometricCityGrid",
    "ParticleConstellation",
    # Underlying classes & specialized presets
    "DriftingBokehOrbs",
    "AnamorphicLensGleamBackdrop",
    "GoldenDustAmbience",
    "PcbCircuitTracesFlow",
    "MicrochipLogicPulse",
    "CopperBusCurrentBackdrop",
    "CosmicNebulaBackdrop",
    "StarfieldWarpDrift",
    "ConstellationGrid",
    "NeonSunBackdrop",
    "WireframeMountainHorizon",
    "_CodeColumn",
    "_BaseRainBackdrop",
    "DigitalMatrixRainBackdrop",
    "BinaryStreamBackdrop",
    "HexCodeColumnBackdrop",
    "FluidWaterCaustics",
    "UnderwaterLightRays",
    "PrismaticIridescentWaves",
    "VoronoiCellEvolution",
    "PenroseTilingFlow",
    "HexagonalHoneyGridPulse",
    "HyperspaceWarpTunnel",
    "HexagonalSpeedTunnel",
    "InfiniteZoomVortex",
    "IsometricCityGridBackdrop",
    "PulsingDataHighways",
    "ServerRackMatrixBackdrop",
    "AuroraGradientWave",
    "LiquidPlasmaBackdrop",
    "AppleStudioInfinityCyc",
    "SoftStageSpotlightBackdrop",
    "FrostedGlassHorizon",
    "ParticleConstellationNetwork",
    "SynapseNeuralGraph",
    "PlexusDistanceLines",
    "CrtPhosphorScanlineBackdrop",
    "TVSignalNoiseStatic",
    "VcrBlueScreenGlitch",
    "CalifornianSunsetBackdrop",
    "GoldenHourSkyGradient",
    "AtmosphericHazeHorizon",
    "AnimatedTopographicContours",
    "BathymetricMapBackdrop",
    "RadarElevationSweep",
]
