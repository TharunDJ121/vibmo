"""
Unit tests for Vibmo Studio Pro modular architecture and API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from vibmo.scene.scene import Scene
from vibmo.components.glass import GlassCard
from vibmo.typography.kinetic import KineticText
from vibmo.studio import create_studio_app
from vibmo.studio.frame_server import FrameServer
from vibmo.studio.audio_server import AudioServer
from vibmo.studio.state import StudioState
from vibmo.studio.pages.fusion import FusionGraph


@pytest.fixture
def sample_scene():
    scene = Scene(width=1920, height=1080, fps=60, duration=4.0)
    card = GlassCard(position=(200, 200), width=400, height=200)
    title = KineticText("Hello Studio Pro", font_size=32)
    card.add(title)
    scene.add(card)
    scene.param("test_speed", 1.5)
    scene.add_sfx("pop", 0.5)
    return scene


def test_studio_state_and_metadata(sample_scene):
    state = StudioState(sample_scene)
    meta = state.get_metadata(current_time=0.0)

    assert meta["type"] == "meta"
    assert meta["duration"] == 4.0
    assert meta["fps"] == 60.0
    assert len(meta["nodes"]) >= 2
    assert "test_speed" in meta["params"]
    assert len(meta["sfx_cues"]) == 1


def test_studio_frame_server(sample_scene):
    frame_server = FrameServer(sample_scene)
    b64_1 = frame_server.get_frame_base64(time=0.0, scale=0.25)
    assert isinstance(b64_1, str)
    assert len(b64_1) > 100

    # Cache hit check
    b64_2 = frame_server.get_frame_base64(time=0.0, scale=0.25)
    assert b64_1 == b64_2


def test_studio_fusion_graph(sample_scene):
    graph = FusionGraph.serialize_scene(sample_scene)
    assert "nodes" in graph
    assert "connections" in graph
    assert len(graph["nodes"]) >= 3


def test_fastapi_endpoints(sample_scene):
    app = create_studio_app(sample_scene)
    client = TestClient(app)

    # 1. Root index HTML
    res_index = client.get("/")
    assert res_index.status_code == 200
    assert "Vibmo Studio" in res_index.text

    # 2. Meta endpoint
    res_meta = client.get("/api/meta")
    assert res_meta.status_code == 200
    data = res_meta.json()
    assert data["duration"] == 4.0

    # 3. Waveform endpoint
    res_wave = client.get("/api/waveform")
    assert res_wave.status_code == 200
    assert len(res_wave.json()["peaks"]) > 0

    # 4. Fusion graph endpoint
    res_fusion = client.get("/api/fusion")
    assert res_fusion.status_code == 200
    assert "nodes" in res_fusion.json()

    # 5. Soundboard endpoint
    res_sb = client.get("/api/soundboard")
    assert res_sb.status_code == 200
    assert len(res_sb.json()["sounds"]) >= 5

    # 6. Presets endpoint
    res_presets = client.get("/api/presets")
    assert res_presets.status_code == 200
    assert len(res_presets.json()["presets"]) >= 4

    # 7. Code export endpoint
    res_code = client.get("/api/export_code")
    assert res_code.status_code == 200
    assert "code" in res_code.json()


def test_studio_keyframes_and_splines(sample_scene):
    app = create_studio_app(sample_scene)
    client = TestClient(app)

    # Verify static assets presence
    res_index = client.get("/")
    assert "spline.js" in res_index.text
    assert "history.js" in res_index.text
    assert "editor.js" in res_index.text
    assert "Snapping" in res_index.text


def test_studio_run_without_script():
    # Studio can be created with NO scene and NO script passed
    app = create_studio_app()
    client = TestClient(app)

    res_meta = client.get("/api/meta")
    assert res_meta.status_code == 200
    meta = res_meta.json()
    assert meta["duration"] > 0
    assert len(meta["nodes"]) > 0

    res_script = client.get("/api/script")
    assert res_script.status_code == 200
    assert "Scene" in res_script.json()["code"]


def test_studio_in_app_script_execution():
    app = create_studio_app()
    client = TestClient(app)

    # 1. Fetch templates
    res_tmpl = client.get("/api/templates")
    assert res_tmpl.status_code == 200
    templates = res_tmpl.json()["templates"]
    assert len(templates) >= 3

    # 2. Run new custom script inside studio
    custom_code = """
scene = Scene(width=1280, height=720, duration=2.5, background=colors.SLATE_950)
box = Rect(width=300, height=150, position=(100, 100), fill=colors.CYAN)
scene.add(box)
"""
    res_run = client.post("/api/script/run", json={"code": custom_code})
    assert res_run.status_code == 200
    res_data = res_run.json()
    assert res_data["success"] is True
    assert res_data["meta"]["width"] == 1280
    assert res_data["meta"]["duration"] == 2.5

    # 3. Verify invalid code error handling
    bad_code = "syntax error 123 !!!"
    res_bad = client.post("/api/script/run", json={"code": bad_code})
    assert res_bad.status_code == 400
    assert res_bad.json()["success"] is False
    assert "SyntaxError" in res_bad.json()["error"]


