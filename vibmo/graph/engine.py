"""
Vibmo V2 Live State Graph Engine.
Thread-safe, observable Directed Acyclic Graph (DAG) state manager
with transaction logging, Undo/Redo, and direct MCP tool bridges.
"""

from __future__ import annotations
import os
import json
import copy
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from threading import RLock

from vibmo.graph.schema import (
    VibmoProjectFile,
    MediaItem,
    TimelineTrack,
    TimelineClip,
    FusionGraph,
    FusionNode,
    FusionConnection,
    AnimatableProperty,
    NodeSocket,
    ColorGradeNode,
    ColorWheelParams,
    AudioChannelStrip,
    EQBand,
    DeliveryJob,
    generate_id,
)


class StateGraphObserver:
    """Callback listener for state mutations."""
    def on_state_changed(self, event_type: str, payload: Dict[str, Any]) -> None:
        pass


class VibmoStateGraph:
    """
    Central State Graph singleton and state manager for Vibmo V2.
    Serves as the single source of truth for Web Studio / Desktop UI and AI Agents.
    """

    def __init__(self, project: Optional[VibmoProjectFile] = None) -> None:
        self._lock = RLock()
        self.project: VibmoProjectFile = project or VibmoProjectFile()
        self._observers: List[Callable[[str, Dict[str, Any]], None]] = []
        self._undo_stack: List[str] = []
        self._redo_stack: List[str] = []
        self._max_history = 50
        self.active_scene: Optional[Any] = None

        # Initialize default video & audio tracks if empty
        if not self.project.timeline.tracks:
            self.add_track("Video 1", track_type="video")
            self.add_track("Audio 1", track_type="audio")

    # -------------------------------------------------------------------------
    # Observation & History (Undo / Redo)
    # -------------------------------------------------------------------------

    def subscribe(self, observer_fn: Callable[[str, Dict[str, Any]], None]) -> None:
        """Register a callback for state changes."""
        with self._lock:
            if observer_fn not in self._observers:
                self._observers.append(observer_fn)

    def unsubscribe(self, observer_fn: Callable[[str, Dict[str, Any]], None]) -> None:
        """Remove a callback."""
        with self._lock:
            if observer_fn in self._observers:
                self._observers.remove(observer_fn)

    def _notify(self, event_type: str, payload: Dict[str, Any]) -> None:
        """Broadcast state event to all subscribers."""
        for obs in list(self._observers):
            try:
                obs(event_type, payload)
            except Exception as err:
                print(f"[StateGraph] Observer error: {err}")

    def _push_undo_snapshot(self) -> None:
        """Save JSON snapshot to undo stack."""
        snapshot = self.project.to_json_str()
        self._undo_stack.append(snapshot)
        if len(self._undo_stack) > self._max_history:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    def undo(self) -> bool:
        """Undo last mutation."""
        with self._lock:
            if not self._undo_stack:
                return False
            self._redo_stack.append(self.project.to_json_str())
            snapshot = self._undo_stack.pop()
            self.project = VibmoProjectFile.from_json_str(snapshot)
            self._notify("undo", {})
            return True

    def redo(self) -> bool:
        """Redo previously undone mutation."""
        with self._lock:
            if not self._redo_stack:
                return False
            self._undo_stack.append(self.project.to_json_str())
            snapshot = self._redo_stack.pop()
            self.project = VibmoProjectFile.from_json_str(snapshot)
            self._notify("redo", {})
            return True

    # -------------------------------------------------------------------------
    # Serialization & Project I/O
    # -------------------------------------------------------------------------

    def save_to_file(self, file_path: str) -> None:
        """Save project state graph to .vibmo or .json file."""
        with self._lock:
            abs_path = os.path.abspath(file_path)
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(self.project.to_json_str(indent=2))

    @classmethod
    def load_from_file(cls, file_path: str) -> VibmoStateGraph:
        """Load project state graph from .vibmo or .json file."""
        with open(file_path, "r", encoding="utf-8") as f:
            data_str = f.read()
        proj = VibmoProjectFile.from_json_str(data_str)
        return cls(project=proj)

    # -------------------------------------------------------------------------
    # Media Pool APIs
    # -------------------------------------------------------------------------

    def import_media(self, file_path: str, name: Optional[str] = None, kind: Optional[str] = None) -> MediaItem:
        """Registers a media file into the project Media Pool."""
        with self._lock:
            self._push_undo_snapshot()
            abs_path = os.path.abspath(file_path)
            base_name = name or os.path.basename(file_path)
            ext = os.path.splitext(file_path)[1].lower()

            if not kind:
                if ext in [".mp4", ".mov", ".mkv", ".webm", ".avi"]:
                    kind = "video"
                elif ext in [".mp3", ".wav", ".aac", ".flac", ".ogg"]:
                    kind = "audio"
                elif ext in [".png", ".jpg", ".jpeg", ".webp", ".svg"]:
                    kind = "image"
                elif ext in [".cube"]:
                    kind = "lut"
                elif ext in [".ttf", ".otf", ".woff2"]:
                    kind = "font"
                else:
                    kind = "video"

            width = None
            height = None
            fps = None
            duration_frames = None
            duration_seconds = None
            metadata = {}

            # Probe media metadata and thumbnail
            if kind == "video":
                try:
                    import cv2
                    cap = cv2.VideoCapture(abs_path)
                    if cap.isOpened():
                        fps = float(cap.get(cv2.CAP_PROP_FPS) or 30.0)
                        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 1920)
                        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 1080)
                        duration_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 120)
                        duration_seconds = float(duration_frames / max(1.0, fps))
                        
                        # Extract representative thumbnail frame at ~10% duration
                        cap.set(cv2.CAP_PROP_POS_FRAMES, min(duration_frames - 1, int(fps * 1.0)))
                        ret, thumb_frame = cap.read()
                        if ret and thumb_frame is not None:
                            # Resize thumbnail to 160x90
                            thumb_small = cv2.resize(thumb_frame, (160, 90))
                            _, enc = cv2.imencode(".jpg", thumb_small, [cv2.IMWRITE_JPEG_QUALITY, 80])
                            import base64
                            metadata["thumbnail_b64"] = base64.b64encode(enc).decode("utf-8")
                        
                        mins = int(duration_seconds // 60)
                        secs = int(duration_seconds % 60)
                        metadata["duration_formatted"] = f"{mins:02d}:{secs:02d}"
                        cap.release()
                except Exception as probe_err:
                    print(f"[StateGraph] Video probe error: {probe_err}")

            elif kind == "image":
                try:
                    from PIL import Image
                    with Image.open(abs_path) as img:
                        width, height = img.size
                        duration_frames = 150
                        duration_seconds = 5.0
                        metadata["duration_formatted"] = "IMAGE"
                except Exception:
                    pass

            item = MediaItem(
                name=base_name,
                file_path=abs_path,
                kind=kind, # type: ignore
                width=width,
                height=height,
                fps=fps,
                duration_frames=duration_frames,
                duration_seconds=duration_seconds,
                metadata=metadata,
            )
            self.project.media_pool.append(item)
            self._notify("media_imported", {"media_id": item.id, "name": item.name})
            return item

    # -------------------------------------------------------------------------
    # Motion Timeline APIs (NLE)
    # -------------------------------------------------------------------------

    def add_track(self, name: str, track_type: str = "video") -> TimelineTrack:
        """Adds a new timeline track."""
        with self._lock:
            self._push_undo_snapshot()
            track = TimelineTrack(
                name=name,
                type=track_type, # type: ignore
                index=len(self.project.timeline.tracks)
            )
            self.project.timeline.tracks.append(track)
            self._notify("track_added", {"track_id": track.id, "name": track.name})
            return track

    def add_clip(
        self,
        track_id: str,
        name: str,
        start_frame: int,
        duration_frames: int,
        media_id: Optional[str] = None,
        fusion_graph_id: Optional[str] = None,
    ) -> TimelineClip:
        """Adds a clip to a specific timeline track."""
        with self._lock:
            self._push_undo_snapshot()
            clip = TimelineClip(
                name=name,
                track_id=track_id,
                start_frame=start_frame,
                duration_frames=duration_frames,
                media_id=media_id,
                fusion_graph_id=fusion_graph_id,
            )
            self.project.timeline.clips[clip.id] = clip
            self._notify("clip_added", {"clip_id": clip.id, "track_id": track_id})
            return clip

    def split_clip(self, clip_id: str, split_frame: int) -> Tuple[TimelineClip, TimelineClip]:
        """Performs a razor blade cut on a clip at split_frame."""
        with self._lock:
            self._push_undo_snapshot()
            clip = self.project.timeline.clips.get(clip_id)
            if not clip:
                raise ValueError(f"Clip {clip_id} not found")

            if not (clip.start_frame < split_frame < clip.start_frame + clip.duration_frames):
                raise ValueError(f"Split frame {split_frame} out of clip bounds")

            offset = split_frame - clip.start_frame
            left_duration = offset
            right_duration = clip.duration_frames - offset

            # Mutate left
            clip.duration_frames = left_duration

            # Create right
            right_clip = TimelineClip(
                name=f"{clip.name}_cut",
                track_id=clip.track_id,
                start_frame=split_frame,
                duration_frames=right_duration,
                source_in_frame=clip.source_in_frame + offset,
                media_id=clip.media_id,
                fusion_graph_id=clip.fusion_graph_id,
                color_tag=clip.color_tag,
            )
            self.project.timeline.clips[right_clip.id] = right_clip
            self._notify("clip_split", {"orig_id": clip_id, "new_id": right_clip.id})
            return clip, right_clip

    # -------------------------------------------------------------------------
    # Fusion Node Graph APIs (VFX & Compositing)
    # -------------------------------------------------------------------------

    def create_fusion_graph(self, name: str = "New Composition") -> FusionGraph:
        """Creates an empty Fusion node graph composition."""
        with self._lock:
            self._push_undo_snapshot()
            graph = FusionGraph(name=name)
            
            # Add MediaIn and MediaOut default nodes
            media_in = FusionNode(
                name="MediaIn1",
                category="io",
                node_type="MediaIn",
                pos_x=100.0,
                pos_y=200.0,
                outputs=[NodeSocket(id="output", name="Output", type="image", is_input=False)],
            )
            media_out = FusionNode(
                name="MediaOut1",
                category="io",
                node_type="MediaOut",
                pos_x=700.0,
                pos_y=200.0,
                inputs=[NodeSocket(id="input", name="Input", type="image", is_input=True)],
            )
            graph.nodes[media_in.id] = media_in
            graph.nodes[media_out.id] = media_out
            graph.active_output_node = media_out.id

            # Connect MediaIn -> MediaOut initially
            conn = FusionConnection(
                from_node=media_in.id,
                from_socket="output",
                to_node=media_out.id,
                to_socket="input",
            )
            graph.connections.append(conn)

            self.project.fusion_graphs[graph.id] = graph
            self._notify("fusion_graph_created", {"graph_id": graph.id, "name": graph.name})
            return graph

    def add_fusion_node(
        self,
        graph_id: str,
        node_type: str,
        name: Optional[str] = None,
        category: str = "filter",
        pos_x: float = 300.0,
        pos_y: float = 200.0,
        properties: Optional[Dict[str, Any]] = None,
    ) -> FusionNode:
        """Adds a VFX node into a Fusion composition."""
        with self._lock:
            self._push_undo_snapshot()
            graph = self.project.fusion_graphs.get(graph_id)
            if not graph:
                raise ValueError(f"Fusion graph {graph_id} not found")

            node_name = name or f"{node_type}_{len(graph.nodes) + 1}"
            
            # Setup default sockets based on category
            inputs = [NodeSocket(id="input", name="Background", type="image", is_input=True)]
            if category in ["matte", "filter", "color"]:
                inputs.append(NodeSocket(id="mask", name="Effect Mask", type="mask", is_input=True))
            if node_type == "Merge":
                inputs.append(NodeSocket(id="foreground", name="Foreground", type="image", is_input=True))

            outputs = [NodeSocket(id="output", name="Output", type="image", is_input=False)]

            node = FusionNode(
                name=node_name,
                category=category, # type: ignore
                node_type=node_type,
                pos_x=pos_x,
                pos_y=pos_y,
                inputs=inputs,
                outputs=outputs,
            )

            if properties:
                for k, v in properties.items():
                    node.properties[k] = AnimatableProperty(name=k, value=v)

            graph.nodes[node.id] = node
            self._notify("node_added", {"graph_id": graph_id, "node_id": node.id, "node_type": node_type})
            return node

    def connect_fusion_nodes(
        self,
        graph_id: str,
        from_node_id: str,
        to_node_id: str,
        from_socket: str = "output",
        to_socket: str = "input",
    ) -> FusionConnection:
        """Connects two nodes in a Fusion composition DAG."""
        with self._lock:
            self._push_undo_snapshot()
            graph = self.project.fusion_graphs.get(graph_id)
            if not graph:
                raise ValueError(f"Fusion graph {graph_id} not found")

            # Remove existing connection to target socket if any
            graph.connections = [
                c for c in graph.connections if not (c.to_node == to_node_id and c.to_socket == to_socket)
            ]

            conn = FusionConnection(
                from_node=from_node_id,
                from_socket=from_socket,
                to_node=to_node_id,
                to_socket=to_socket,
            )
            graph.connections.append(conn)
            self._notify("nodes_connected", {
                "graph_id": graph_id,
                "from_node": from_node_id,
                "to_node": to_node_id,
            })
            return conn

    # -------------------------------------------------------------------------
    # Color Grading Pipeline APIs
    # -------------------------------------------------------------------------

    def set_primary_grade(
        self,
        lift: Optional[Tuple[float, float, float, float]] = None,
        gamma: Optional[Tuple[float, float, float, float]] = None,
        gain: Optional[Tuple[float, float, float, float]] = None,
        contrast: float = 1.0,
        saturation: float = 1.0,
    ) -> ColorGradeNode:
        """Configures primary color grading node."""
        with self._lock:
            self._push_undo_snapshot()
            if not self.project.color_pipeline.nodes:
                primary = ColorGradeNode(name="Primary Grade 1")
                self.project.color_pipeline.nodes.append(primary)
            else:
                primary = self.project.color_pipeline.nodes[0]

            if lift:
                primary.lift = ColorWheelParams(red=lift[0], green=lift[1], blue=lift[2], master=lift[3])
            if gamma:
                primary.gamma = ColorWheelParams(red=gamma[0], green=gamma[1], blue=gamma[2], master=gamma[3])
            if gain:
                primary.gain = ColorWheelParams(red=gain[0], green=gain[1], blue=gain[2], master=gain[3])

            primary.contrast = contrast
            primary.saturation = saturation

            self._notify("color_grade_updated", {"node_id": primary.id})
            return primary

    # -------------------------------------------------------------------------
    # Fairlight Audio Mixer APIs
    # -------------------------------------------------------------------------

    def configure_track_strip(
        self,
        track_id: str,
        fader_gain_db: float = 0.0,
        pan: float = 0.0,
        compressor_enabled: bool = False,
        sidechain_source_track: Optional[str] = None,
    ) -> AudioChannelStrip:
        """Sets channel strip parameters on a specific audio track."""
        with self._lock:
            self._push_undo_snapshot()
            strip = self.project.fairlight.channels.get(track_id)
            if not strip:
                strip = AudioChannelStrip(track_id=track_id)
                self.project.fairlight.channels[track_id] = strip

            strip.fader_gain_db = fader_gain_db
            strip.pan = pan
            strip.compressor_enabled = compressor_enabled
            strip.sidechain_source_track = sidechain_source_track

            self._notify("audio_strip_updated", {"track_id": track_id})
            return strip

    # -------------------------------------------------------------------------
    # Delivery Render Queue APIs
    # -------------------------------------------------------------------------

    def queue_render_job(
        self,
        output_path: str,
        preset_name: str = "YouTube 4K Master",
        format_name: str = "mp4",
        width: int = 3840,
        height: int = 2160,
        fps: float = 60.0,
    ) -> DeliveryJob:
        """Adds a job to the Delivery render queue."""
        with self._lock:
            self._push_undo_snapshot()
            job = DeliveryJob(
                preset_name=preset_name,
                output_path=os.path.abspath(output_path),
                format=format_name, # type: ignore
                width=width,
                height=height,
                fps=fps,
            )
            self.project.render_queue.append(job)
            self._notify("render_job_queued", {"job_id": job.id, "output": job.output_path})
            return job
