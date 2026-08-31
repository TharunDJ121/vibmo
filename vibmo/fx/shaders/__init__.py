"""Visual post-fx and shader filters."""
from __future__ import annotations

from vibmo.fx.shaders.fx_crt_phosphor_bloom_suite import (
    GpuFilterBase,
    CrtPhosphorBloomShader,
    CurvedGlassBarrelDistortion,
    PhosphorPersistenceTrail,
    HorizontalRGBBeamBleed,
)
from vibmo.fx.shaders.fx_ascii_matrix_art_suite import (
    AsciiMatrixArtShader,
    AsciiMatrixArtShader as AsciiMatrixArtFilter,
    TerminalColorPaletteFilter,
    DynamicCharResolutionGrid,
    DynamicCharResolutionGrid as LuminescenceGrid,
    EdgeContourAsciiOverlay,
)
from vibmo.fx.shaders.fx_liquid_glass_refraction_suite import (
    LiquidGlassRefractionShader,
    LiquidGlassRefractionShader as LiquidGlassRefractionFilter,
    ChromaticDispersionFilter,
    ChromaticDispersionFilter as ChromaticDispersion,
    SpecularRimSheen,
    FrostedBackdropBlur,
)
from vibmo.fx.shaders.fx_anamorphic_flare_suite import (
    ThresholdGlowPass,
    AnamorphicStreakFlareShader,
    AnamorphicStreakFlareShader as AnamorphicStreakFlare,
    AnamorphicStreakFlareShader as HorizontalBlueStreak,
    LensGhostArtifacts,
    StarburstSpikeCross,
)
from vibmo.fx.shaders.fx_vhs_tape_tracking_suite import (
    VhsTapeTrackingShader,
    HeadSwitchingJitterLine,
    HeadSwitchingJitterLine as HeadSwitchJitter,
    ColorBleedChromaShift,
    AnalogStaticSnowBurst,
)
from vibmo.fx.shaders.fx_ascii_render_filter import (
    AsciiRenderFilter,
    AsciiRenderShader,
)
from vibmo.fx.shaders.fx_security_cam_overlay import (
    SecurityCamOverlay,
    CctvSurveillanceHud,
)
from vibmo.fx.shaders.fx_shader_neural_voronoi import (
    ShaderNeuroNoise,
    ShaderVoronoiGrid,
)
from vibmo.fx.shaders.fx_underwater_ripple import (
    UnderwaterRippleFilter,
)

__all__ = [
    "GpuFilterBase",
    "CrtPhosphorBloomShader",
    "CurvedGlassBarrelDistortion",
    "PhosphorPersistenceTrail",
    "HorizontalRGBBeamBleed",
    "AsciiMatrixArtShader",
    "AsciiMatrixArtFilter",
    "TerminalColorPaletteFilter",
    "DynamicCharResolutionGrid",
    "LuminescenceGrid",
    "EdgeContourAsciiOverlay",
    "LiquidGlassRefractionShader",
    "LiquidGlassRefractionFilter",
    "ChromaticDispersionFilter",
    "ChromaticDispersion",
    "SpecularRimSheen",
    "FrostedBackdropBlur",
    "ThresholdGlowPass",
    "AnamorphicStreakFlareShader",
    "AnamorphicStreakFlare",
    "HorizontalBlueStreak",
    "LensGhostArtifacts",
    "StarburstSpikeCross",
    "VhsTapeTrackingShader",
    "HeadSwitchingJitterLine",
    "HeadSwitchJitter",
    "ColorBleedChromaShift",
    "AnalogStaticSnowBurst",
    "AsciiRenderFilter",
    "AsciiRenderShader",
    "SecurityCamOverlay",
    "CctvSurveillanceHud",
    "ShaderNeuroNoise",
    "ShaderVoronoiGrid",
    "UnderwaterRippleFilter",
]
