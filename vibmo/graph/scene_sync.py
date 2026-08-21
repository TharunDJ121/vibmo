"""
Bidirectional Scene & Sequence to StateGraph Synchronizer for Vibmo.
Translates Python Scene, Sequence, and Composition objects into the live VibmoStateGraph
(Timeline Tracks, Multi-Scene Clips, Fusion DAG, Color Grade, and Player Canvas).
"""

from __future__ import annotations
from typing import Any, Optional, Dict, List, Union
import uuid

from vibmo.scene.scene import Scene
from vibmo.composition.sequence import Sequence
from vibmo.graph.engine import VibmoStateGraph
from vibmo.graph.schema import TimelineTrack, TimelineClip


class SceneGraphSyncEngine:
    """Synchronizes Python Scene or Multi-Scene Sequence objects into the central VibmoStateGraph."""

    @classmethod
    def sync_to_state_graph(cls, target: Union[Scene, Sequence, Any], state_graph: VibmoStateGraph) -> None:
        """Translates a Scene or Sequence into tracks, clips, fusion nodes, and state graph properties."""
        if isinstance(target, Sequence):
            cls._sync_sequence(target, state_graph)
        else:
            cls._sync_scene(target, state_graph)

    # Legacy alias
    sync_scene_to_state_graph = sync_to_state_graph

    @classmethod
    def _sync_scene(cls, scene: Scene, state_graph: VibmoStateGraph) -> None:
        with state_graph._lock:
            # 1. Project Dimensions & Timing
            state_graph.project.width = int(scene.width)
            state_graph.project.height = int(scene.height)
            state_graph.project.fps = float(scene.fps)
            state_graph.project.duration_seconds = float(scene.duration)
            state_graph.project.duration_frames = int(round(scene.duration * scene.fps))

            # 2. Synchronize Timeline Tracks
            tracks: List[TimelineTrack] = []
            v_track = TimelineTrack(id="track_v1", name="Video 1 (Motion)", type="video", index=0)
            tracks.append(v_track)

            has_captions = any("caption" in n.__class__.__name__.lower() or "text" in n.__class__.__name__.lower() for n in scene.nodes)
            if has_captions:
                sub_track = TimelineTrack(id="track_sub1", name="Captions / Typography", type="subtitle", index=1)
                tracks.append(sub_track)

            has_audio = bool(scene.audio_path or scene.audio_tracks or (hasattr(scene, "sfx") and len(scene.sfx.cues) > 0))
            if has_audio:
                a_track = TimelineTrack(id="track_a1", name="Audio 1 (Master)", type="audio", index=len(tracks))
                tracks.append(a_track)

            state_graph.project.timeline.tracks = tracks

            # 3. Synchronize Timeline Clips
            clips: Dict[str, TimelineClip] = {}
            for i, node in enumerate(scene.nodes):
                is_sub = "caption" in node.__class__.__name__.lower() or "text" in node.__class__.__name__.lower()
                target_track_id = "track_sub1" if (is_sub and has_captions) else "track_v1"
                
                start_f = int(round(getattr(node, "in_point", 0.0) * scene.fps))
                out_sec = getattr(node, "out_point", None)
                if out_sec is not None:
                    dur_f = int(round((out_sec - getattr(node, "in_point", 0.0)) * scene.fps))
                else:
                    dur_f = state_graph.project.duration_frames - start_f

                dur_f = max(1, dur_f)
                color = "#FF5A5F" if is_sub else ("#00E5FF" if i % 2 == 0 else "#8B5CF6")

                clip_id = f"clip_{uuid.uuid4().hex[:8]}"
                clips[clip_id] = TimelineClip(
                    id=clip_id,
                    track_id=target_track_id,
                    name=f"{node.__class__.__name__}: {getattr(node, 'name', 'Layer')}",
                    start_frame=start_f,
                    duration_frames=dur_f,
                    source_in=0,
                    source_out=dur_f,
                    color_tag=color,
                )

            if has_audio:
                if scene.audio_path:
                    a_id = f"audio_{uuid.uuid4().hex[:8]}"
                    clips[a_id] = TimelineClip(
                        id=a_id,
                        track_id="track_a1",
                        name="Master Audio Track",
                        start_frame=0,
                        duration_frames=state_graph.project.duration_frames,
                        color_tag="#10B981",
                    )
                for tr in scene.audio_tracks:
                    a_id = f"audio_{uuid.uuid4().hex[:8]}"
                    start_f = int(round(tr.start * scene.fps))
                    dur_f = int(round((tr.duration or (scene.duration - tr.start)) * scene.fps))
                    clips[a_id] = TimelineClip(
                        id=a_id,
                        track_id="track_a1",
                        name=tr.name or "Timeline Audio",
                        start_frame=start_f,
                        duration_frames=dur_f,
                        color_tag="#10B981",
                    )

            state_graph.project.timeline.clips = clips

            # 4. Synchronize Post FX into Fusion Graph
            if not state_graph.project.fusion_graphs:
                fg = state_graph.create_fusion_graph("Scene VFX Compositor")
            else:
                fg = list(state_graph.project.fusion_graphs.values())[0]

            if scene.post_fx:
                fg.nodes.clear()
                fg.connections.clear()
                n_in = state_graph.add_fusion_node(fg.id, "MediaIn", "io", pos_x=80, pos_y=160)
                last_id = n_in.id

                for idx, fx in enumerate(scene.post_fx):
                    fx_name = fx.__class__.__name__
                    n_fx = state_graph.add_fusion_node(
                        graph_id=fg.id,
                        node_type=fx_name if fx_name in ["GaussianBlur", "Glow", "FastNoise", "Transform2D", "DeltaKeyer"] else "OpticalGlow",
                        category="filter",
                        pos_x=280 + idx * 200,
                        pos_y=160,
                    )
                    state_graph.connect_fusion_nodes(fg.id, last_id, n_fx.id)
                    last_id = n_fx.id

                n_out = state_graph.add_fusion_node(fg.id, "MediaOut", "io", pos_x=280 + len(scene.post_fx) * 200, pos_y=160)
                state_graph.connect_fusion_nodes(fg.id, last_id, n_out.id)

            state_graph.active_scene = scene
            state_graph._notify("SCENE_SYNCED", {"scene": scene})

    @classmethod
    def _sync_sequence(cls, seq: Sequence, state_graph: VibmoStateGraph) -> None:
        with state_graph._lock:
            # 1. Sequence Timing & Dimensions
            state_graph.project.width = int(seq.width)
            state_graph.project.height = int(seq.height)
            state_graph.project.fps = float(seq.fps)
            state_graph.project.duration_seconds = float(seq.duration)
            state_graph.project.duration_frames = int(round(seq.duration * seq.fps))

            # 2. Sequence Timeline Tracks
            tracks: List[TimelineTrack] = [
                TimelineTrack(id="track_seq_scenes", name="🎬 Scenes (Sequence)", type="video", index=0),
                TimelineTrack(id="track_seq_layers", name="✨ Graphics & Typography", type="subtitle", index=1),
                TimelineTrack(id="track_seq_audio", name="🎵 Master Soundtrack", type="audio", index=2),
            ]
            state_graph.project.timeline.tracks = tracks

            # 3. Create Timeline Clips for each scene and component
            clips: Dict[str, TimelineClip] = {}
            palette = ["#00E5FF", "#8B5CF6", "#10B981", "#EC4899", "#F59E0B"]

            for i, scene in enumerate(seq.scenes):
                start_t = seq.scene_starts[i] if i < len(seq.scene_starts) else 0.0
                start_f = int(round(start_t * seq.fps))
                dur_f = int(round(scene.duration * seq.fps))
                color = palette[i % len(palette)]

                # Main Scene Block Clip
                c_id = f"scene_clip_{i + 1}"
                clips[c_id] = TimelineClip(
                    id=c_id,
                    track_id="track_seq_scenes",
                    name=f"Scene {i + 1} ({scene.duration:.1f}s)",
                    start_frame=start_f,
                    duration_frames=dur_f,
                    source_in=0,
                    source_out=dur_f,
                    color_tag=color,
                )

                # Sub-layer components
                for j, node in enumerate(scene.nodes[:3]):
                    sub_id = f"sub_{i}_{j}_{uuid.uuid4().hex[:4]}"
                    clips[sub_id] = TimelineClip(
                        id=sub_id,
                        track_id="track_seq_layers",
                        name=f"S{i+1}: {node.__class__.__name__}",
                        start_frame=start_f + j * 10,
                        duration_frames=max(30, dur_f - j * 10),
                        color_tag="#FF5A5F" if "text" in node.__class__.__name__.lower() else "#38BDF8",
                    )

            if seq.audio_path:
                clips["seq_audio"] = TimelineClip(
                    id="seq_audio",
                    track_id="track_seq_audio",
                    name="Sequence Audio",
                    start_frame=0,
                    duration_frames=state_graph.project.duration_frames,
                    color_tag="#10B981",
                )

            state_graph.project.timeline.clips = clips

            # 4. Sync Fusion VFX Graph
            if not state_graph.project.fusion_graphs:
                fg = state_graph.create_fusion_graph("Multi-Scene VFX Pipeline")
            else:
                fg = list(state_graph.project.fusion_graphs.values())[0]

            fg.nodes.clear()
            fg.connections.clear()
            n_in = state_graph.add_fusion_node(fg.id, "MediaIn", "io", pos_x=60, pos_y=160)
            n_noise = state_graph.add_fusion_node(fg.id, "FastNoise", "generator", pos_x=280, pos_y=100)
            n_glow = state_graph.add_fusion_node(fg.id, "OpticalGlow", "filter", pos_x=500, pos_y=160)
            n_trans = state_graph.add_fusion_node(fg.id, "Transform2D", "transform", pos_x=720, pos_y=160)
            n_out = state_graph.add_fusion_node(fg.id, "MediaOut", "io", pos_x=940, pos_y=160)

            state_graph.connect_fusion_nodes(fg.id, n_in.id, n_noise.id)
            state_graph.connect_fusion_nodes(fg.id, n_noise.id, n_glow.id)
            state_graph.connect_fusion_nodes(fg.id, n_glow.id, n_trans.id)
            state_graph.connect_fusion_nodes(fg.id, n_trans.id, n_out.id)

            # 5. Store Sequence as active scene
            state_graph.active_scene = seq
            state_graph._notify("SCENE_SYNCED", {"scene": seq})
