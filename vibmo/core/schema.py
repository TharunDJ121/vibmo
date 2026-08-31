"""
Canonical Vibmo Project Schema (Intermediate Representation).
Provides a typed, validated, and serializable format for AI and UI editors.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from enum import Enum


class OpType(str, Enum):
    ADD_LAYER = "add_layer"
    UPDATE_LAYER = "update_layer"
    REMOVE_LAYER = "remove_layer"
    SET_KEYFRAME = "set_keyframe"
    UPDATE_SHOT = "update_shot"


class Keyframe(BaseModel):
    time: float
    value: Any
    ease: str = "linear"


class PropertyTrack(BaseModel):
    property_name: str
    keyframes: List[Keyframe] = Field(default_factory=list)


class LayerType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    SOLID = "solid"
    SHAPE = "shape"
    COMPONENT = "component"


class Layer(BaseModel):
    id: str
    type: LayerType
    name: str = "Layer"
    start_time: float = 0.0
    duration: float = 1.0
    properties: Dict[str, Any] = Field(default_factory=dict)
    animations: Dict[str, PropertyTrack] = Field(default_factory=dict)


class Shot(BaseModel):
    id: str
    name: str = "Shot"
    start_time: float
    duration: float
    layers: List[Layer] = Field(default_factory=list)


class Track(BaseModel):
    id: str
    name: str = "Video Track"
    shots: List[Shot] = Field(default_factory=list)


class VibmoProject(BaseModel):
    version: str = "1.0.0"
    width: int = 1920
    height: int = 1080
    fps: int = 60
    duration: float = 0.0
    tracks: List[Track] = Field(default_factory=list)
    assets: Dict[str, str] = Field(default_factory=dict)

    def add_shot(self, track_index: int, shot: Shot) -> None:
        while len(self.tracks) <= track_index:
            self.tracks.append(Track(id=f"track_{len(self.tracks)}"))
        self.tracks[track_index].shots.append(shot)
        
    def to_json(self) -> str:
        return self.model_dump_json(indent=2)
