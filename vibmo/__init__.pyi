"""
Type stubs for Vibmo: Modern, Design-First Motion Graphics Framework for Python.
"""

from typing import Any, Callable, Dict, Generator, List, Optional, Sequence, Tuple, Union
from vibmo.core.vector import Vector2D, Vector3D
from vibmo.core.matrix import Matrix3x3, Matrix4x4
from vibmo.core.color import Color, LinearGradient, RadialGradient, colors
from vibmo.core.easing import Ease, EasingFunc, CubicBezier
from vibmo.core.spring import Spring, SpringEasing
from vibmo.core.signal import Signal, AnimationAction, AnimationSegment

from vibmo.scene.node import Node
from vibmo.scene.camera import Camera2D, Camera3D, Camera
from vibmo.scene.scene import Scene, Param
from vibmo.timeline.scheduler import all, sequence, wait, Choreographer

from vibmo.layout.alignment import Align
from vibmo.layout.container import FlexContainer, AutoResizeBox
from vibmo.layout.flexbox import FlexLayout

from vibmo.primitives.rect import Rect, RoundedRect
from vibmo.primitives.circle import Circle, Ellipse
from vibmo.primitives.polygon import Polygon, Star, Line
from vibmo.primitives.path import Path
from vibmo.primitives.morph import MorphPath, Shape

from vibmo.typography.text import Text
from vibmo.typography.kinetic import KineticText

from vibmo.importers.fonts import FontManager
from vibmo.importers.icons import Icon
from vibmo.importers.lottie import LottieAnimation
from vibmo.importers.web import WebNode
from vibmo.assets.asset import Asset, ImageNode
from vibmo.assets.video import VideoNode, VideoClip

from vibmo.compositing.graph import Precomp, AlphaMatte, LumaMatte, AdjustmentLayer, precomp
from vibmo.product.mockups import BrowserWindow, PhoneFrame
from vibmo.product.cursor import Cursor, ClickIndicator
from vibmo.product.callouts import Spotlight, Callout, Tooltip
from vibmo.product.charts import AreaChart, Sparkline, BarChart, PieChart, DonutChart, GaugeChart
from vibmo.product.command_palette import CommandPalette, CommandItem
from vibmo.product.tables import DataTable, TimelineView
from vibmo.product.social import Avatar, AvatarGroup, Badge, ChatBubble, TypingIndicator
from vibmo.product.controls import ToggleSwitch, Checkbox, ProgressBar, RatingStars
from vibmo.product.cards import StatCard


from vibmo.composition.sequence import Sequence, Transition, CrossFade, Slide
from vibmo.physics.particles import ParticleEmitter

from vibmo.themes import Themes, Theme
from vibmo.components.glass import GlassCard
from vibmo.components.counter import MetricCounter
from vibmo.components.code import CodeWindow
from vibmo.components.toast import NotificationToast

from vibmo.audio.track import AudioTrack
from vibmo.audio.analyzer import AudioAnalyzer
from vibmo.audio.sfx import ProceduralSFX, SFXTrack
from vibmo.audio.visualizers import (
    SpectrumBars,
    CircularSpectrum,
    WaveformRibbon,
    VinylRecord,
    AudioProgressBar,
)

from vibmo.math.formula import MathFormula
from vibmo.math.plots import Axes

from vibmo.spatial.perspective import Matrix3D, Projective3DWarp
from vibmo.spatial.shadows import DropShadow
from vibmo.spatial.motion_path import MotionPathAction

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


from vibmo.templates.turnkey import create_saas_launch_scene
from vibmo.templates.catalog import TEMPLATES
from vibmo.ai.agent_scene import AgentSceneGenerator
from vibmo.ai.schema import generate_component_schemas, export_llm_tool_definitions
from vibmo.plugins.registry import PluginRegistry, register_component, register_filter

__all__: List[str]

