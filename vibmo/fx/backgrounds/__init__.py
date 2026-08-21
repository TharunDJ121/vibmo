"""
Non-static, continuously animated procedural backgrounds and dynamic backdrops.
"""

from __future__ import annotations

from vibmo.fx.backgrounds.bg_mesh_gradient_flow import (
    MeshGradientFlow,
    AuroraGradientWave,
    LiquidPlasmaBackdrop,
)
from vibmo.fx.backgrounds.bg_cyber_grid_horizon import (
    CyberGridHorizon,
    NeonSunBackdrop,
    WireframeMountainHorizon,
)
from vibmo.fx.backgrounds.bg_cosmic_nebula import (
    CosmicNebulaBackdrop,
    StarfieldWarpDrift,
    ConstellationGrid,
)
from vibmo.fx.backgrounds.bg_isometric_city_grid import (
    IsometricCityGridBackdrop,
    PulsingDataHighways,
    ServerRackMatrixBackdrop,
)
from vibmo.fx.backgrounds.bg_fluid_caustics import (
    FluidWaterCaustics,
    UnderwaterLightRays,
    PrismaticIridescentWaves,
)
from vibmo.fx.backgrounds.bg_digital_matrix_rain import (
    DigitalMatrixRainBackdrop,
    BinaryStreamBackdrop,
    HexCodeColumnBackdrop,
)
from vibmo.fx.backgrounds.bg_topographic_contours import (
    AnimatedTopographicContours,
    BathymetricMapBackdrop,
    RadarElevationSweep,
)
from vibmo.fx.backgrounds.bg_particle_constellation import (
    ParticleConstellationNetwork,
    SynapseNeuralGraph,
    PlexusDistanceLines,
)
from vibmo.fx.backgrounds.bg_bokeh_light_bubbles import (
    DriftingBokehOrbs,
    AnamorphicLensGleamBackdrop,
    GoldenDustAmbience,
)
from vibmo.fx.backgrounds.bg_geometric_tessellation import (
    VoronoiCellEvolution,
    PenroseTilingFlow,
    HexagonalHoneyGridPulse,
)
from vibmo.fx.backgrounds.bg_retro_crt_scanlines import (
    CrtPhosphorScanlineBackdrop,
    TVSignalNoiseStatic,
    VcrBlueScreenGlitch,
)
from vibmo.fx.backgrounds.bg_hyperspace_tunnel import (
    HyperspaceWarpTunnel,
    HexagonalSpeedTunnel,
    InfiniteZoomVortex,
)
from vibmo.fx.backgrounds.bg_sunset_horizon_glow import (
    CalifornianSunsetBackdrop,
    GoldenHourSkyGradient,
    AtmosphericHazeHorizon,
)
from vibmo.fx.backgrounds.bg_circuit_board_traces import (
    PcbCircuitTracesFlow,
    MicrochipLogicPulse,
    CopperBusCurrentBackdrop,
)

__all__ = [
    # Mesh Gradients & Plasma
    "MeshGradientFlow",
    "AuroraGradientWave",
    "LiquidPlasmaBackdrop",
    # Cyber Grid & Horizon
    "CyberGridHorizon",
    "NeonSunBackdrop",
    "WireframeMountainHorizon",
    # Cosmic & Space
    "CosmicNebulaBackdrop",
    "StarfieldWarpDrift",
    "ConstellationGrid",
    # Isometric City
    "IsometricCityGridBackdrop",
    "PulsingDataHighways",
    "ServerRackMatrixBackdrop",
    # Fluid Caustics
    "FluidWaterCaustics",
    "UnderwaterLightRays",
    "PrismaticIridescentWaves",
    # Digital Matrix Rain
    "DigitalMatrixRainBackdrop",
    "BinaryStreamBackdrop",
    "HexCodeColumnBackdrop",
    # Topographic Contours
    "AnimatedTopographicContours",
    "BathymetricMapBackdrop",
    "RadarElevationSweep",
    # Particle Constellations
    "ParticleConstellationNetwork",
    "SynapseNeuralGraph",
    "PlexusDistanceLines",
    # Bokeh & Light
    "DriftingBokehOrbs",
    "AnamorphicLensGleamBackdrop",
    "GoldenDustAmbience",
    # Geometric Tessellations
    "VoronoiCellEvolution",
    "PenroseTilingFlow",
    "HexagonalHoneyGridPulse",
    # Retro CRT Scanlines
    "CrtPhosphorScanlineBackdrop",
    "TVSignalNoiseStatic",
    "VcrBlueScreenGlitch",
    # Hyperspace Tunnels
    "HyperspaceWarpTunnel",
    "HexagonalSpeedTunnel",
    "InfiniteZoomVortex",
    # Sunset & Horizon
    "CalifornianSunsetBackdrop",
    "GoldenHourSkyGradient",
    "AtmosphericHazeHorizon",
    # Circuit Board Traces
    "PcbCircuitTracesFlow",
    "MicrochipLogicPulse",
    "CopperBusCurrentBackdrop",
]
