"""
Tests for Vibmo V2 State Graph Engine and .vibmo JSON Schema.
"""

import pytest
import os
import tempfile
from vibmo.graph import (
    VibmoStateGraph,
    VibmoProjectFile,
    MediaItem,
    TimelineTrack,
    TimelineClip,
    FusionNode,
)


def test_state_graph_initialization():
    graph = VibmoStateGraph()
    assert graph.project.name == "Untitled Project"
    assert len(graph.project.timeline.tracks) >= 2  # default video and audio tracks
    assert graph.project.timeline.tracks[0].type == "video"
    assert graph.project.timeline.tracks[1].type == "audio"


def test_timeline_clip_addition_and_split():
    graph = VibmoStateGraph()
    track_id = graph.project.timeline.tracks[0].id

    # Add clip
    clip = graph.add_clip(
        track_id=track_id,
        name="Intro_Hero.mp4",
        start_frame=0,
        duration_frames=120,
    )
    assert clip.id in graph.project.timeline.clips
    assert clip.duration_frames == 120

    # Razor blade split at frame 40
    left, right = graph.split_clip(clip.id, split_frame=40)
    assert left.duration_frames == 40
    assert right.duration_frames == 80
    assert right.start_frame == 40
    assert right.source_in_frame == 40


def test_fusion_graph_creation_and_node_wiring():
    graph = VibmoStateGraph()
    fg = graph.create_fusion_graph("Hero Glow Effect")
    assert len(fg.nodes) == 2  # MediaIn, MediaOut
    assert len(fg.connections) == 1

    # Add Gaussian Blur node
    blur = graph.add_fusion_node(
        graph_id=fg.id,
        node_type="GaussianBlur",
        name="Blur1",
        category="filter",
        properties={"radius": 24.5},
    )
    assert blur.id in fg.nodes
    assert blur.properties["radius"].value == 24.5

    # Connect MediaIn -> Blur1 -> MediaOut
    media_in_id = [nid for nid, n in fg.nodes.items() if n.node_type == "MediaIn"][0]
    media_out_id = [nid for nid, n in fg.nodes.items() if n.node_type == "MediaOut"][0]

    graph.connect_fusion_nodes(fg.id, from_node_id=media_in_id, to_node_id=blur.id)
    graph.connect_fusion_nodes(fg.id, from_node_id=blur.id, to_node_id=media_out_id)

    assert len(fg.connections) == 2


def test_color_and_fairlight_apis():
    graph = VibmoStateGraph()

    # Color grading
    grade = graph.set_primary_grade(
        lift=(0.02, -0.01, 0.05, 0.0),
        gamma=(0.0, 0.02, -0.01, 0.0),
        gain=(-0.05, 0.0, 0.08, 0.0),
        contrast=1.15,
        saturation=1.2,
    )
    assert grade.contrast == 1.15
    assert grade.saturation == 1.2
    assert grade.lift.blue == 0.05

    # Fairlight strip
    track_id = graph.project.timeline.tracks[1].id
    strip = graph.configure_track_strip(
        track_id=track_id,
        fader_gain_db=-3.5,
        pan=-0.2,
        compressor_enabled=True,
    )
    assert strip.fader_gain_db == -3.5
    assert strip.pan == -0.2
    assert strip.compressor_enabled is True


def test_undo_redo_history():
    graph = VibmoStateGraph()
    initial_tracks_count = len(graph.project.timeline.tracks)

    # Add a track
    new_track = graph.add_track("VFX 2", track_type="fusion")
    assert len(graph.project.timeline.tracks) == initial_tracks_count + 1

    # Undo
    assert graph.undo() is True
    assert len(graph.project.timeline.tracks) == initial_tracks_count

    # Redo
    assert graph.redo() is True
    assert len(graph.project.timeline.tracks) == initial_tracks_count + 1


def test_json_file_save_and_load():
    graph = VibmoStateGraph()
    graph.project.name = "Production Launch Movie"
    graph.add_track("Graphics 1", track_type="video")

    with tempfile.NamedTemporaryFile(suffix=".vibmo", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        graph.save_to_file(tmp_path)
        assert os.path.exists(tmp_path)

        loaded_graph = VibmoStateGraph.load_from_file(tmp_path)
        assert loaded_graph.project.name == "Production Launch Movie"
        assert len(loaded_graph.project.timeline.tracks) == len(graph.project.timeline.tracks)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
