"""
OpenTimelineIO (OTIO) Universal NLE Adapter & Exporter.
Serializes Vibmo timelines (video/audio tracks, shots, clips, gaps, markers) into Pixar's .otio JSON format.
Compatible with DaVinci Resolve, Adobe Premiere Pro, Final Cut Pro X, Avid Media Composer, and Blender VSE.
"""

from __future__ import annotations
import json
import math
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from vibmo.core.schema import VibmoProject, LayerType


def _make_rational_time(value_frames: Union[int, float], rate: float) -> Dict[str, Any]:
    return {
        "OTIO_SCHEMA": "RationalTime.1",
        "rate": float(rate),
        "value": float(value_frames),
    }


def _make_time_range(start_frame: Union[int, float], duration_frames: Union[int, float], rate: float) -> Dict[str, Any]:
    return {
        "OTIO_SCHEMA": "TimeRange.1",
        "start_time": _make_rational_time(start_frame, rate),
        "duration": _make_rational_time(duration_frames, rate),
    }


def _make_marker(name: str, start_frame: Union[int, float], duration_frames: Union[int, float], rate: float, color: str = "CYAN", comment: str = "") -> Dict[str, Any]:
    return {
        "OTIO_SCHEMA": "Marker.1",
        "name": str(name),
        "color": str(color).upper(),
        "comment": str(comment),
        "marked_range": _make_time_range(start_frame, duration_frames, rate),
        "metadata": {},
    }


class OtioExporter:
    """
    Exports Vibmo projects and scenes to OpenTimelineIO (.otio) JSON interchange format.
    """

    @classmethod
    def to_dict(cls, project: VibmoProject, timeline_name: str = "Vibmo Sequence") -> Dict[str, Any]:
        """Converts a VibmoProject intermediate representation to an OTIO Timeline dictionary."""
        fps = float(project.fps or 30.0)
        total_duration_frames = int(round(project.duration * fps))

        track_children: List[Dict[str, Any]] = []

        # 1. Process Video Tracks
        for t_idx, track_data in enumerate(project.tracks, start=1):
            track_clips: List[Dict[str, Any]] = []
            current_time = 0.0

            # Sort shots by start_time
            sorted_shots = sorted(track_data.shots, key=lambda s: s.start_time)

            for s_idx, shot in enumerate(sorted_shots, start=1):
                # Check for gap before shot
                if shot.start_time > current_time + 1e-4:
                    gap_duration = shot.start_time - current_time
                    gap_frames = int(round(gap_duration * fps))
                    if gap_frames > 0:
                        track_clips.append({
                            "OTIO_SCHEMA": "Gap.1",
                            "name": f"Gap-{s_idx}",
                            "source_range": _make_time_range(0, gap_frames, fps),
                            "effects": [],
                            "markers": [],
                            "metadata": {},
                            "enabled": True,
                        })

                shot_frames = max(1, int(round(shot.duration * fps)))
                start_frame_in_media = 0

                # Check if shot contains media layers
                media_path = ""
                for layer in shot.layers:
                    if layer.type in [LayerType.VIDEO, LayerType.IMAGE]:
                        media_path = layer.properties.get("image_path", layer.properties.get("video_path", ""))
                        if media_path:
                            break

                target_url = f"file://localhost/{Path(media_path).absolute().as_posix()}" if media_path else f"vibmo://layers/{shot.id}"
                media_name = Path(media_path).name if media_path else shot.name

                clip_dict: Dict[str, Any] = {
                    "OTIO_SCHEMA": "Clip.1",
                    "name": shot.name or f"Shot-{s_idx}",
                    "enabled": True,
                    "effects": [],
                    "markers": [],
                    "metadata": {
                        "vibmo": {
                            "shot_id": shot.id,
                            "layer_count": len(shot.layers),
                        }
                    },
                    "media_reference": {
                        "OTIO_SCHEMA": "ExternalReference.1",
                        "name": media_name,
                        "target_url": target_url,
                        "available_range": _make_time_range(0, shot_frames, fps),
                        "metadata": {},
                    },
                    "source_range": _make_time_range(start_frame_in_media, shot_frames, fps),
                }

                track_clips.append(clip_dict)
                current_time = shot.start_time + shot.duration

            video_track: Dict[str, Any] = {
                "OTIO_SCHEMA": "Track.1",
                "name": track_data.name or f"Video-{t_idx}",
                "kind": "Video",
                "enabled": True,
                "children": track_clips,
                "effects": [],
                "markers": [],
                "metadata": {},
                "source_range": None,
            }
            track_children.append(video_track)

        # 2. Build Top-Level Stack
        tracks_stack: Dict[str, Any] = {
            "OTIO_SCHEMA": "Stack.1",
            "name": "tracks",
            "enabled": True,
            "children": track_children,
            "effects": [],
            "markers": [],
            "metadata": {},
            "source_range": None,
        }

        # 3. Assemble Root Timeline
        timeline: Dict[str, Any] = {
            "OTIO_SCHEMA": "Timeline.1",
            "name": timeline_name,
            "global_start_time": _make_rational_time(0, fps),
            "tracks": tracks_stack,
            "metadata": {
                "vibmo": {
                    "version": project.version,
                    "width": project.width,
                    "height": project.height,
                    "fps": fps,
                    "duration_seconds": project.duration,
                }
            },
        }

        return timeline

    @classmethod
    def export(cls, project: VibmoProject, output_path: str, timeline_name: str = "Vibmo Sequence", indent: int = 2) -> str:
        """Serializes a VibmoProject to an .otio file."""
        data = cls.to_dict(project, timeline_name=timeline_name)
        out_dir = os.path.dirname(output_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent)

        return output_path

    @classmethod
    def export_scene(cls, scene: Any, output_path: str, timeline_name: Optional[str] = None, indent: int = 2) -> str:
        """Serializes a Scene instance to an .otio file."""
        fps = float(getattr(scene, "fps", 60.0))
        dur = float(getattr(scene, "duration", 5.0))
        w = int(getattr(scene, "width", 1920))
        h = int(getattr(scene, "height", 1080))
        name = timeline_name or "Vibmo Scene"

        total_frames = int(round(dur * fps))
        track_children: List[Dict[str, Any]] = []

        # Video Track from scene nodes
        video_clips: List[Dict[str, Any]] = []
        nodes = getattr(scene, "nodes", [])

        # Collect markers
        timeline_markers: List[Dict[str, Any]] = []
        for m in getattr(scene, "markers", []):
            m_time = getattr(m, "time", 0.0)
            m_name = getattr(m, "name", "Marker")
            m_color = getattr(m, "color", "CYAN")
            m_comment = getattr(m, "comment", "")
            m_dur = getattr(m, "duration", 0.0)
            timeline_markers.append(
                _make_marker(
                    name=m_name,
                    start_frame=int(round(m_time * fps)),
                    duration_frames=max(0, int(round(m_dur * fps))),
                    rate=fps,
                    color=str(m_color),
                    comment=m_comment,
                )
            )

        # Build Main Video Track clip
        video_clips.append({
            "OTIO_SCHEMA": "Clip.1",
            "name": f"{name} (Motion Comp)",
            "enabled": True,
            "effects": [],
            "markers": [],
            "metadata": {
                "vibmo": {
                    "node_count": len(nodes),
                }
            },
            "media_reference": {
                "OTIO_SCHEMA": "ExternalReference.1",
                "name": f"{name}.mov",
                "target_url": f"vibmo://scene/{name}",
                "available_range": _make_time_range(0, total_frames, fps),
                "metadata": {},
            },
            "source_range": _make_time_range(0, total_frames, fps),
        })

        track_children.append({
            "OTIO_SCHEMA": "Track.1",
            "name": "Video 1",
            "kind": "Video",
            "enabled": True,
            "children": video_clips,
            "effects": [],
            "markers": [],
            "metadata": {},
            "source_range": None,
        })

        # Audio Tracks (if scene has audio)
        audio_tracks = getattr(scene, "audio_tracks", [])
        main_audio = getattr(scene, "audio_path", None)

        if main_audio or audio_tracks:
            audio_clips: List[Dict[str, Any]] = []
            if main_audio and os.path.exists(main_audio):
                a_name = Path(main_audio).name
                audio_clips.append({
                    "OTIO_SCHEMA": "Clip.1",
                    "name": a_name,
                    "enabled": True,
                    "effects": [],
                    "markers": [],
                    "metadata": {},
                    "media_reference": {
                        "OTIO_SCHEMA": "ExternalReference.1",
                        "name": a_name,
                        "target_url": f"file://localhost/{Path(main_audio).absolute().as_posix()}",
                        "available_range": _make_time_range(0, total_frames, fps),
                        "metadata": {},
                    },
                    "source_range": _make_time_range(0, total_frames, fps),
                })

            for a_idx, a_track in enumerate(audio_tracks, start=1):
                fpath = getattr(a_track, "file_path", "")
                if fpath and os.path.exists(fpath):
                    aname = getattr(a_track, "name", Path(fpath).name)
                    audio_clips.append({
                        "OTIO_SCHEMA": "Clip.1",
                        "name": aname,
                        "enabled": True,
                        "effects": [],
                        "markers": [],
                        "metadata": {},
                        "media_reference": {
                            "OTIO_SCHEMA": "ExternalReference.1",
                            "name": Path(fpath).name,
                            "target_url": f"file://localhost/{Path(fpath).absolute().as_posix()}",
                            "available_range": _make_time_range(0, total_frames, fps),
                            "metadata": {},
                        },
                        "source_range": _make_time_range(0, total_frames, fps),
                    })

            if audio_clips:
                track_children.append({
                    "OTIO_SCHEMA": "Track.1",
                    "name": "Audio 1",
                    "kind": "Audio",
                    "enabled": True,
                    "children": audio_clips,
                    "effects": [],
                    "markers": [],
                    "metadata": {},
                    "source_range": None,
                })

        timeline = {
            "OTIO_SCHEMA": "Timeline.1",
            "name": name,
            "global_start_time": _make_rational_time(0, fps),
            "tracks": {
                "OTIO_SCHEMA": "Stack.1",
                "name": "tracks",
                "enabled": True,
                "children": track_children,
                "effects": [],
                "markers": timeline_markers,
                "metadata": {},
                "source_range": None,
            },
            "metadata": {
                "vibmo": {
                    "width": w,
                    "height": h,
                    "fps": fps,
                    "duration_seconds": dur,
                }
            },
        }

        out_dir = os.path.dirname(output_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(timeline, f, indent=indent)

        return output_path
