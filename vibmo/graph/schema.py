"""
Vibmo V2 Unified State Graph Schema.
High-precision JSON/YAML Directed Acyclic Graph (DAG) specification
for Motion (NLE), Fusion (VFX), Color, Fairlight (Audio), and Delivery.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple, Union, Literal
from pydantic import BaseModel, Field, ConfigDict
import json
import uuid


def generate_id(prefix: str = "id") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


# -----------------------------------------------------------------------------
# 1. Media Pool & Asset Management
# -----------------------------------------------------------------------------

class MediaItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str = Field(default_factory=lambda: generate_id("media"))
    name: str
    file_path: str
    kind: Literal["video", "audio", "image", "font", "lut", "vector", "3d"] = "video"
    width: Optional[int] = None
    height: Optional[int] = None
    fps: Optional[float] = None
    duration_frames: Optional[int] = None
    duration_seconds: Optional[float] = None
    audio_channels: Optional[int] = None
    sample_rate: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


# -----------------------------------------------------------------------------
# 2. Keyframes & Animation Expressions
# -----------------------------------------------------------------------------

class Keyframe(BaseModel):
    frame: int
    value: Any
    easing: Literal["linear", "ease_in", "ease_out", "ease_in_out", "spring", "bezier", "step"] = "ease_in_out"
    handle_left: Optional[Tuple[float, float]] = None
    handle_right: Optional[Tuple[float, float]] = None


class AnimatableProperty(BaseModel):
    name: str
    value: Any
    is_animated: bool = False
    keyframes: List[Keyframe] = Field(default_factory=list)
    expression: Optional[str] = None  # e.g., "Math.sin(time * 3.0) * 100"


# -----------------------------------------------------------------------------
# 3. Fusion VFX & Compositing Node Graph (DAG)
# -----------------------------------------------------------------------------

class NodeSocket(BaseModel):
    id: str
    name: str
    type: Literal["image", "mask", "vector", "audio", "value", "3d_scene"] = "image"
    is_input: bool = True


class FusionNode(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str = Field(default_factory=lambda: generate_id("node"))
    name: str
    category: Literal[
        "generator", "color", "filter", "transform", "matte", "tracking", "time", "3d", "io"
    ]
    node_type: str  # e.g. "Background", "GaussianBlur", "Merge", "DeltaKeyer", "Transform3D"
    pos_x: float = 100.0
    pos_y: float = 100.0
    enabled: bool = True
    properties: Dict[str, AnimatableProperty] = Field(default_factory=dict)
    inputs: List[NodeSocket] = Field(default_factory=list)
    outputs: List[NodeSocket] = Field(default_factory=list)


class FusionConnection(BaseModel):
    id: str = Field(default_factory=lambda: generate_id("edge"))
    from_node: str
    from_socket: str = "output"
    to_node: str
    to_socket: str = "input"


class FusionGraph(BaseModel):
    id: str = Field(default_factory=lambda: generate_id("fusion"))
    name: str = "Fusion Composition"
    nodes: Dict[str, FusionNode] = Field(default_factory=dict)
    connections: List[FusionConnection] = Field(default_factory=list)
    active_output_node: Optional[str] = None


# -----------------------------------------------------------------------------
# 4. Motion (NLE) Timeline
# -----------------------------------------------------------------------------

class Transition(BaseModel):
    id: str = Field(default_factory=lambda: generate_id("trans"))
    type: Literal["cross_dissolve", "dip_to_black", "dip_to_white", "wipe", "slide", "zoom_blur"] = "cross_dissolve"
    duration_frames: int = 15


class TimelineClip(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str = Field(default_factory=lambda: generate_id("clip"))
    name: str
    media_id: Optional[str] = None
    fusion_graph_id: Optional[str] = None
    track_id: str
    start_frame: int = 0
    duration_frames: int = 120
    source_in_frame: int = 0
    speed: float = 1.0
    enabled: bool = True
    color_tag: str = "#6366F1"
    transition_in: Optional[Transition] = None
    transition_out: Optional[Transition] = None
    transform: Dict[str, AnimatableProperty] = Field(default_factory=dict)


class TimelineTrack(BaseModel):
    id: str = Field(default_factory=lambda: generate_id("track"))
    name: str
    type: Literal["video", "audio", "fusion", "subtitle"] = "video"
    index: int = 0
    muted: bool = False
    solo: bool = False
    locked: bool = False
    height: int = 40
    volume_db: float = 0.0
    pan: float = 0.0


class Timeline(BaseModel):
    tracks: List[TimelineTrack] = Field(default_factory=list)
    clips: Dict[str, TimelineClip] = Field(default_factory=dict)
    markers: List[Dict[str, Any]] = Field(default_factory=list)


# -----------------------------------------------------------------------------
# 5. Color Grading (DaVinci-Style Node Pipeline)
# -----------------------------------------------------------------------------

class ColorWheelParams(BaseModel):
    red: float = 0.0
    green: float = 0.0
    blue: float = 0.0
    master: float = 0.0


class ColorGradeNode(BaseModel):
    id: str = Field(default_factory=lambda: generate_id("color_node"))
    name: str = "Primary Grade"
    type: Literal["serial", "parallel", "layer_mixer", "lut"] = "serial"
    enabled: bool = True
    lift: ColorWheelParams = Field(default_factory=ColorWheelParams)
    gamma: ColorWheelParams = Field(default_factory=ColorWheelParams)
    gain: ColorWheelParams = Field(default_factory=ColorWheelParams)
    offset: ColorWheelParams = Field(default_factory=ColorWheelParams)
    contrast: float = 1.0
    saturation: float = 1.0
    pivot: float = 0.435
    temperature: float = 0.0
    tint: float = 0.0
    lut_path: Optional[str] = None
    curves: Dict[str, List[Tuple[float, float]]] = Field(default_factory=dict)


class ColorPipeline(BaseModel):
    color_space: Literal["ACEScg", "DaVinci_Wide_Gamut", "Rec709", "sRGB"] = "ACEScg"
    nodes: List[ColorGradeNode] = Field(default_factory=list)


# -----------------------------------------------------------------------------
# 6. Fairlight Audio (DAW & Mixer Architecture)
# -----------------------------------------------------------------------------

class EQBand(BaseModel):
    band_type: Literal["low_shelf", "bell", "high_shelf", "notch", "high_pass", "low_pass"] = "bell"
    frequency_hz: float = 1000.0
    gain_db: float = 0.0
    q_factor: float = 1.0
    enabled: bool = True


class AudioChannelStrip(BaseModel):
    track_id: str
    eq_enabled: bool = True
    eq_bands: List[EQBand] = Field(default_factory=lambda: [
        EQBand(band_type="high_pass", frequency_hz=80.0),
        EQBand(band_type="low_shelf", frequency_hz=200.0),
        EQBand(band_type="bell", frequency_hz=800.0),
        EQBand(band_type="bell", frequency_hz=2500.0),
        EQBand(band_type="high_shelf", frequency_hz=8000.0),
        EQBand(band_type="low_pass", frequency_hz=16000.0),
    ])
    compressor_enabled: bool = False
    compressor_threshold_db: float = -20.0
    compressor_ratio: float = 4.0
    compressor_attack_ms: float = 15.0
    compressor_release_ms: float = 100.0
    limiter_enabled: bool = True
    limiter_ceiling_db: float = -0.5
    fader_gain_db: float = 0.0
    pan: float = 0.0
    sidechain_source_track: Optional[str] = None


class FairlightMixer(BaseModel):
    sample_rate: int = 48000
    channels: Dict[str, AudioChannelStrip] = Field(default_factory=dict)
    master_gain_db: float = 0.0
    master_limiter: bool = True


# -----------------------------------------------------------------------------
# 7. Delivery & Export Queue
# -----------------------------------------------------------------------------

class DeliveryJob(BaseModel):
    id: str = Field(default_factory=lambda: generate_id("job"))
    preset_name: str = "YouTube 4K Master"
    format: Literal["mp4", "prores4444", "prores422", "dnxhr", "webm", "gif", "wav_stems"] = "mp4"
    codec: str = "libx264"
    width: int = 3840
    height: int = 2160
    fps: float = 60.0
    bitrate_kbps: int = 45000
    output_path: str
    status: Literal["queued", "rendering", "done", "failed"] = "queued"
    progress: float = 0.0
    error_message: Optional[str] = None


# -----------------------------------------------------------------------------
# 8. Master Vibmo Project File Model (.vibmo)
# -----------------------------------------------------------------------------

class VibmoProjectFile(BaseModel):
    model_config = ConfigDict(extra="allow")

    schema_version: str = "2.0.0"
    id: str = Field(default_factory=lambda: generate_id("proj"))
    name: str = "Untitled Project"
    width: int = 1920
    height: int = 1080
    fps: float = 60.0
    duration_frames: int = 600  # 10.0s @ 60 FPS

    media_pool: List[MediaItem] = Field(default_factory=list)
    timeline: Timeline = Field(default_factory=Timeline)
    fusion_graphs: Dict[str, FusionGraph] = Field(default_factory=dict)
    color_pipeline: ColorPipeline = Field(default_factory=ColorPipeline)
    fairlight: FairlightMixer = Field(default_factory=FairlightMixer)
    render_queue: List[DeliveryJob] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def to_json_str(self, indent: int = 2) -> str:
        return self.model_dump_json(indent=indent)

    @classmethod
    def from_json_str(cls, json_str: str) -> VibmoProjectFile:
        return cls.model_validate_json(json_str)
