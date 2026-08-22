"""
✦ Vibmo: The AI-Agent Native Semantic Motion-Design Framework for Python.
"""

from __future__ import annotations

# Core Types & Signals
from vibmo.core.vector import Vector2D, Vector3D
from vibmo.core.matrix import Matrix3x3, Matrix4x4
from vibmo.core.color import Color, LinearGradient, RadialGradient, colors
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc, CubicBezier
from vibmo.core.spring import Spring, SpringEasing

# Scene Graph, Camera & Choreography
from vibmo.scene.scene import Scene, Param
from vibmo.scene.node import Node
from vibmo.scene.camera import Camera2D, Camera3D, Camera
from vibmo.timeline.scheduler import all, sequence, wait, Choreographer

# Layout & Flexbox
from vibmo.layout.alignment import Align
from vibmo.layout.container import FlexContainer, AutoResizeBox
from vibmo.layout.flexbox import FlexLayout

# Primitives & Morphing
from vibmo.primitives.rect import Rect, RoundedRect
from vibmo.primitives.circle import Circle, Ellipse
from vibmo.primitives.polygon import Polygon, Star, Line
from vibmo.primitives.path import Path
from vibmo.primitives.morph import MorphPath, Shape

# Typography & Captions
from vibmo.typography.text import Text
from vibmo.typography.kinetic import KineticText, GlyphNode
from vibmo.typography.captions import KineticCaptions, CaptionWord
from vibmo.typography.effects import (
    NeonText,
    GradientText,
    Text3D,
    TextStroke,
    WarpText,
)
from vibmo.typography.animations import (
    WordReveal,
    TextScramble,
    TextTypewriter,
    TextPathFollower,
)
from vibmo.typography.captions_advanced import (
    TimedWord,
    AdvancedKaraokeCaptions,
)

# Importers & Assets
from vibmo.importers.fonts import FontManager
from vibmo.importers.icons import Icon
from vibmo.importers.lottie import LottieAnimation
from vibmo.importers.web import WebNode
from vibmo.assets.asset import Asset, ImageNode
from vibmo.assets.video import VideoNode, VideoClip
from vibmo.assets.video_advanced import AdvancedVideoNode
from vibmo.assets.icons import BuiltinIcon, ICON_REGISTRY
from vibmo.assets.gradients import Gradients, GRADIENT_PRESETS
from vibmo.assets.library import (
    AssetLibrary,
    AssetMetadata,
    AssetType,
    AssetCategory,
    get_asset_library,
)
from vibmo.studio.asset_browser import AssetBrowser, get_asset_browser, BrowserFilter

# Compositing Graph & Mattes
from vibmo.compositing.graph import Precomp, AlphaMatte, LumaMatte, AdjustmentLayer, precomp
from vibmo.compositing.blend_modes import BlendMode
from vibmo.compositing.mask import Mask

# Product Mockups, Charts & UI Components
from vibmo.product.mockups import BrowserWindow, PhoneFrame
from vibmo.product.mockups_expanded import (
    TabletFrame,
    LaptopFrame,
    WatchFrame,
    DesktopFrame,
)
from vibmo.product.cursor import Cursor, ClickIndicator
from vibmo.product.callouts import Spotlight, Callout, Tooltip
from vibmo.product.charts import AreaChart, Sparkline, BarChart, PieChart, DonutChart, GaugeChart
from vibmo.product.charts_advanced import (
    LineChart,
    ScatterChart,
    RadarChart,
    FunnelChart,
    Heatmap,
    CandlestickChart,
)
from vibmo.product.ui_components import (
    ProgressBar,
    Slider,
    Tabs,
    Accordion,
    Modal,
    Dropdown,
    Breadcrumbs,
    Pagination,
)
from vibmo.product.form_components import (
    InputField,
    SelectBox,
    RadioButton,
    Checkbox,
    ToggleButton,
    Switch,
    RangeSlider,
)
from vibmo.product.feedback_components import (
    NotificationToast,
    AlertBanner,
    LoadingSpinner,
    SkeletonScreen,
    EmptyState,
    ErrorBoundary,
)
from vibmo.product.ai_components import (
    GradientBackdrop,
    ModelCard,
    ChatInputBar,
    KineticSnapText,
    FileAttachmentBadge,
    EditorialDoc,
    PillLaunchButton,
)
from vibmo.product.command_palette import CommandPalette, CommandItem
from vibmo.product.tables import DataTable, TimelineView
from vibmo.product.social import Avatar, AvatarGroup, Badge, ChatBubble, TypingIndicator
from vibmo.product.cards import StatCard

# Themes & High-Vibe Cards
from vibmo.themes import Themes, Theme
from vibmo.components.glass import GlassCard
from vibmo.components.counter import MetricCounter
from vibmo.components.code import CodeWindow

# Physics & Particles
from vibmo.physics.particles import ParticleEmitter
from vibmo.physics.particles_advanced import AdvancedParticleEmitter
from vibmo.physics.spring import SpringSimulation, SpringParameters
from vibmo.physics.dynamics import PendulumDynamics, BounceDynamics
from vibmo.physics.path_animation import CubicBezierCurve, PathFollower
from vibmo.physics.forces import (
    ForceField,
    GravityField,
    VortexForce,
    TurbulentNoiseField,
    AttractorPoint,
)

# Audio Reactivity & SFX
from vibmo.audio.track import AudioTrack, TimelineAudioClip
from vibmo.audio.analyzer import AudioAnalyzer
from vibmo.audio.sfx import ProceduralSFX, SFXTrack
from vibmo.audio.library import fetch_online_audio, CURATED_AUDIO_PRESETS
from vibmo.audio.visualizers import (
    SpectrumBars,
    CircularSpectrum,
    WaveformRibbon,
    VinylRecord,
    AudioProgressBar,
)
from vibmo.audio.visualization import (
    SpectrumVisualizer,
    CircularEqualizer,
    AudioReactivePulse,
)
from vibmo.audio.sfx_library import (
    ProceduralSFXGenerator,
    AudioDucker,
)
from vibmo.audio.stems import AudioStemMixer

# Math & Plots
from vibmo.math.formula import MathFormula
from vibmo.math.plots import Axes

# Spatial 2.5D & Shadows
from vibmo.spatial.perspective import Matrix3D
from vibmo.spatial.shadows import DropShadow
from vibmo.spatial.motion_path import MotionPathAction

# Visual FX, Shaders & Filters
from vibmo.fx.filters import (
    FilmGrain,
    Vignette,
    BackdropBlur,
    MotionBlur,
    Bloom,
    Glow,
    ChromaticAberration,
    DepthOfField,
    TiltShift,
    Dither,
    ColorCorrection,
    LensFlare,
    GodRays,
    Glitch,
    Pixelate,
    RadialBlur,
    ZoomBlur,
    EdgeGlow,
    Halftone,
    Duotone,
)
from vibmo.fx.patterns import (
    Checkerboard,
    Gridlines,
    Rings,
    Starburst,
    Pattern,
    Tile,
    Zigzag,
    checkerboard,
    gridlines,
    rings,
    starburst,
    pattern,
    tile,
    zigzag,
)
from vibmo.fx.color_advanced import (
    Duotone as DuotoneAdvanced,
    Tint,
    ColorCorrection as ColorCorrectionAdvanced,
    WhiteBalance,
    Saturation,
    Vibrance,
    Levels,
    Curves,
    duotone,
    tint,
    color_correction,
    white_balance,
    saturation,
    vibrance,
    levels,
    curves,
)
from vibmo.fx.distortion import (
    BarrelDistortion,
    Fisheye,
    Wave,
    Waves,
    LiquidContours,
    Skew,
    CornerPin,
    barrel_distortion,
    fisheye,
    wave,
    waves,
    liquid_contours,
    skew,
    corner_pin,
)
from vibmo.fx.edge_effects import (
    Outline,
    ContourLines,
    RoughenEdges,
    outline,
    contour_lines,
    roughen_edges,
)
from vibmo.fx.noise_effects import (
    Noise,
    WhiteNoise,
    Speckle,
    Scanlines,
    TVSignalOff,
    noise,
    white_noise,
    speckle,
    scanlines,
    tv_signal_off,
)
from vibmo.fx.digital_effects import (
    Pixelate as PixelateAdvanced,
    PixelDissolve,
    Halftone as HalftoneAdvanced,
    DotGrid,
    Dither as DitherAdvanced,
    pixelate,
    pixel_dissolve,
    halftone,
    dot_grid,
    dither,
)
from vibmo.fx.light_effects import (
    LightLeak as LightLeakFX,
    Shine,
    LensFlare as LensFlareAdvanced,
    GodRays as GodRaysAdvanced,
    ThermalVision,
    light_leak,
    shine,
    lens_flare,
    god_rays,
    thermal_vision,
)
from vibmo.fx.blur_suite import (
    LinearProgressiveBlur,
    RadialProgressiveBlur,
    RegionBlur,
    ZoomBlur as ZoomBlurAdvanced,
    MotionBlur as MotionBlurAdvanced,
    linear_progressive_blur,
    radial_progressive_blur,
    region_blur,
    zoom_blur,
    motion_blur,
)

# Composition & Sequence
from vibmo.composition.composition import Composition, Shot
from vibmo.composition.sequence import Sequence, Transition, CrossFade
from vibmo.composition.transitions import (
    CrossDissolve,
    WhipPan,
    ZoomPunch,
    GlitchTransition,
    LightLeak,
    ShapeWipe,
    DipToColor,
)
from vibmo.composition.transitions_expanded import (
    Slide,
    PushCut,
    Fade,
    Dissolve,
    Iris,
    Wipe,
    ZoomBlur as TransitionZoomBlur,
    Ripple,
    Flip,
    BookFlip,
    slide,
    push_cut,
    fade,
    dissolve,
    iris,
    wipe,
    zoom_blur as transition_zoom_blur,
    ripple,
    flip,
    book_flip,
)
from vibmo.composition.timing import (
    LinearTiming,
    SpringTiming,
    CubicBezierTiming,
    EaseInTiming,
    EaseOutTiming,
    EaseInOutTiming,
    spring_timing,
    linear_timing,
    bezier_timing,
)

# Turnkey Templates & Exporter
from vibmo.templates.turnkey import create_saas_launch_scene
from vibmo.templates.catalog import TEMPLATES
from vibmo.templates.library import SceneTemplateLibrary
from vibmo.render.export import Exporter, ExportQuality, QUALITY_PRESETS

# Rigging, Expressions & Constraints
from vibmo.rigging.constraints import Constraint, LookAtConstraint, FollowConstraint, PathConstraint
from vibmo.rigging.expression import ExpressionSignal, expression

# Color Management, HDR & Spaces
from vibmo.color.management import ColorSpace, ColorManager

# Tracking & Chroma Keying
from vibmo.tracking.chroma_key import ChromaKey
from vibmo.tracking.tracker import PointTracker

# Portable Projects & Relinker
from vibmo.project.project import VibmoProject, ProjectMediaItem

# Aesthetic Style Presets
from vibmo.styles.presets import StylePreset, Styles
from vibmo.styles.applicator import apply_style_to_scene

# Multi-Platform Aspect Ratio Auto-Reflow
from vibmo.layout.reflow import AspectRatio, SceneReflowEngine

# AI Agent Capabilities & Plugins
from vibmo.ai.agent_scene import AgentSceneGenerator
from vibmo.ai.schema import generate_component_schemas, export_llm_tool_definitions
from vibmo.plugins.registry import PluginRegistry, register_component, register_filter

# Timeline Tracks & Markers
from vibmo.timeline.marker import Marker
from vibmo.timeline.track import LayerTrack

# Production Asset Suites across Sections 1 to 7
from vibmo.audio.generators import *
from vibmo.fx.backgrounds import *
from vibmo.product.hardware import *
from vibmo.product.ai import *
from vibmo.charts import *
from vibmo.typography.kinetic import *
from vibmo.fx.shaders import *

import vibmo.audio.generators as _generators
import vibmo.fx.backgrounds as _backgrounds
import vibmo.product.hardware as _hardware
import vibmo.product.ai as _ai_ui
import vibmo.charts as _charts
import vibmo.typography.kinetic as _kinetic_typo
import vibmo.fx.shaders as _shaders

__version__ = "0.2.0"

__all__ = [
    # Core
    "Vector2D",
    "Vector3D",
    "Matrix3x3",
    "Matrix4x4",
    "Color",
    "LinearGradient",
    "RadialGradient",
    "colors",
    "Ease",
    "CubicBezier",
    "Spring",
    "SpringEasing",
    "Signal",
    "Node",
    "Camera2D",
    "Camera3D",
    "Camera",
    "Scene",
    "Param",
    "all",
    "sequence",
    "wait",
    "Align",
    "FlexContainer",
    "AutoResizeBox",
    "FlexLayout",
    "Rect",
    "RoundedRect",
    "Circle",
    "Ellipse",
    "Polygon",
    "Star",
    "Line",
    "Path",
    "MorphPath",
    "Shape",
    # Typography
    "Text",
    "KineticText",
    "GlyphNode",
    "KineticCaptions",
    "CaptionWord",
    "NeonText",
    "GradientText",
    "Text3D",
    "TextStroke",
    "WarpText",
    "WordReveal",
    "TextScramble",
    "TextTypewriter",
    "TextPathFollower",
    "TimedWord",
    "AdvancedKaraokeCaptions",
    # Importers & Assets
    "FontManager",
    "Icon",
    "BuiltinIcon",
    "Gradients",
    "Asset",
    "ImageNode",
    "VideoNode",
    "VideoClip",
    "AdvancedVideoNode",
    "AssetLibrary",
    "AssetMetadata",
    "AssetType",
    "AssetCategory",
    "get_asset_library",
    "AssetBrowser",
    "get_asset_browser",
    "BrowserFilter",
    "LottieAnimation",
    "WebNode",
    # Compositing
    "Precomp",
    "AlphaMatte",
    "LumaMatte",
    "AdjustmentLayer",
    "precomp",
    "BlendMode",
    "Mask",
    # Mockups & Products
    "BrowserWindow",
    "PhoneFrame",
    "TabletFrame",
    "LaptopFrame",
    "WatchFrame",
    "DesktopFrame",
    "Cursor",
    "ClickIndicator",
    "Spotlight",
    "Callout",
    "Tooltip",
    "AreaChart",
    "Sparkline",
    "BarChart",
    "PieChart",
    "DonutChart",
    "GaugeChart",
    "LineChart",
    "ScatterChart",
    "RadarChart",
    "FunnelChart",
    "Heatmap",
    "CandlestickChart",
    "CommandPalette",
    "CommandItem",
    "DataTable",
    "TimelineView",
    "Avatar",
    "AvatarGroup",
    "Badge",
    "ChatBubble",
    "TypingIndicator",
    "ProgressBar",
    "Slider",
    "Tabs",
    "Accordion",
    "Modal",
    "Dropdown",
    "Breadcrumbs",
    "Pagination",
    "InputField",
    "SelectBox",
    "RadioButton",
    "Checkbox",
    "ToggleButton",
    "Switch",
    "RangeSlider",
    "NotificationToast",
    "AlertBanner",
    "LoadingSpinner",
    "SkeletonScreen",
    "EmptyState",
    "ErrorBoundary",
    "StatCard",
    # AI & Modern SaaS Launch Components
    "GradientBackdrop",
    "ModelCard",
    "ChatInputBar",
    "KineticSnapText",
    "FileAttachmentBadge",
    "EditorialDoc",
    "PillLaunchButton",
    # Themes & Cards
    "Themes",
    "Theme",
    "GlassCard",
    "MetricCounter",
    "CodeWindow",
    # Physics & Particles
    "ParticleEmitter",
    "AdvancedParticleEmitter",
    "SpringSimulation",
    "SpringParameters",
    "PendulumDynamics",
    "BounceDynamics",
    "CubicBezierCurve",
    "PathFollower",
    "ForceField",
    "GravityField",
    "VortexForce",
    "TurbulentNoiseField",
    "AttractorPoint",
    # Audio & SFX
    "AudioTrack",
    "TimelineAudioClip",
    "AudioAnalyzer",
    "ProceduralSFX",
    "SFXTrack",
    "SpectrumBars",
    "CircularSpectrum",
    "WaveformRibbon",
    "VinylRecord",
    "AudioProgressBar",
    "SpectrumVisualizer",
    "CircularEqualizer",
    "AudioReactivePulse",
    "ProceduralSFXGenerator",
    "AudioDucker",
    "AudioStemMixer",
    # Math & Spatial
    "MathFormula",
    "Axes",
    "Matrix3D",
    "DropShadow",
    "MotionPathAction",
    # Visual FX & Filters
    "FilmGrain",
    "Vignette",
    "BackdropBlur",
    "MotionBlur",
    "Bloom",
    "Glow",
    "ChromaticAberration",
    "DepthOfField",
    "TiltShift",
    "Dither",
    "ColorCorrection",
    "LensFlare",
    "GodRays",
    "Glitch",
    "Pixelate",
    "RadialBlur",
    "ZoomBlur",
    "EdgeGlow",
    "Halftone",
    "Duotone",
    "Checkerboard",
    "Gridlines",
    "Rings",
    "Starburst",
    "Pattern",
    "Tile",
    "Zigzag",
    "checkerboard",
    "gridlines",
    "rings",
    "starburst",
    "pattern",
    "tile",
    "zigzag",
    "DuotoneAdvanced",
    "Tint",
    "ColorCorrectionAdvanced",
    "WhiteBalance",
    "Saturation",
    "Vibrance",
    "Levels",
    "Curves",
    "duotone",
    "tint",
    "color_correction",
    "white_balance",
    "saturation",
    "vibrance",
    "levels",
    "curves",
    "BarrelDistortion",
    "Fisheye",
    "Wave",
    "Waves",
    "LiquidContours",
    "Skew",
    "CornerPin",
    "barrel_distortion",
    "fisheye",
    "wave",
    "waves",
    "liquid_contours",
    "skew",
    "corner_pin",
    "Outline",
    "ContourLines",
    "RoughenEdges",
    "outline",
    "contour_lines",
    "roughen_edges",
    "Noise",
    "WhiteNoise",
    "Speckle",
    "Scanlines",
    "TVSignalOff",
    "noise",
    "white_noise",
    "speckle",
    "scanlines",
    "tv_signal_off",
    "PixelateAdvanced",
    "PixelDissolve",
    "HalftoneAdvanced",
    "DotGrid",
    "DitherAdvanced",
    "pixelate",
    "pixel_dissolve",
    "halftone",
    "dot_grid",
    "dither",
    "LightLeakFX",
    "Shine",
    "LensFlareAdvanced",
    "GodRaysAdvanced",
    "ThermalVision",
    "light_leak",
    "shine",
    "lens_flare",
    "god_rays",
    "thermal_vision",
    "LinearProgressiveBlur",
    "RadialProgressiveBlur",
    "RegionBlur",
    "ZoomBlurAdvanced",
    "MotionBlurAdvanced",
    "linear_progressive_blur",
    "radial_progressive_blur",
    "region_blur",
    # Transitions & Sequences
    "Composition",
    "Shot",
    "Sequence",
    "Transition",
    "CrossFade",
    "CrossDissolve",
    "WhipPan",
    "ZoomPunch",
    "GlitchTransition",
    "LightLeak",
    "ShapeWipe",
    "DipToColor",
    "Slide",
    "PushCut",
    "Fade",
    "Dissolve",
    "Iris",
    "Wipe",
    "TransitionZoomBlur",
    "Ripple",
    "Flip",
    "BookFlip",
    "slide",
    "push_cut",
    "fade",
    "dissolve",
    "iris",
    "wipe",
    "transition_zoom_blur",
    "ripple",
    "flip",
    "book_flip",
    "LinearTiming",
    "SpringTiming",
    "CubicBezierTiming",
    "EaseInTiming",
    "EaseOutTiming",
    "EaseInOutTiming",
    "spring_timing",
    "linear_timing",
    "bezier_timing",
    # Templates & Exporter
    "create_saas_launch_scene",
    "TEMPLATES",
    "SceneTemplateLibrary",
    "Exporter",
    "ExportQuality",
    "QUALITY_PRESETS",
    # Rigging & Tracking
    "Constraint",
    "LookAtConstraint",
    "FollowConstraint",
    "PathConstraint",
    "ExpressionSignal",
    "expression",
    "ColorSpace",
    "ColorManager",
    "ChromaKey",
    "PointTracker",
    "VibmoProject",
    "ProjectMediaItem",
    "StylePreset",
    "Styles",
    "apply_style_to_scene",
    "AspectRatio",
    "SceneReflowEngine",
    "AgentSceneGenerator",
    "generate_component_schemas",
    "export_llm_tool_definitions",
    "PluginRegistry",
    "register_component",
    "register_filter",
    "Marker",
    "LayerTrack",
]

__all__.extend(_generators.__all__)
__all__.extend(_backgrounds.__all__)
__all__.extend(_hardware.__all__)
__all__.extend(_ai_ui.__all__)
__all__.extend(_charts.__all__)
__all__.extend(_kinetic_typo.__all__)
__all__.extend(_shaders.__all__)

