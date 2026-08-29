import pytest
import sys
import importlib.util

spec = importlib.util.spec_from_file_location(
    "tmpl_developer_cli_launch_suite",
    "vibmo/templates/turnkey/tmpl_developer_cli_launch_suite.py"
)
module = importlib.util.module_from_spec(spec)
sys.modules["tmpl_developer_cli_launch_suite"] = module
spec.loader.exec_module(module)
DeveloperCliLaunchTemplate = module.DeveloperCliLaunchTemplate

from motio.agent_api import Scene, CodeWindow, BarChart, MetricCounter, ParticleEmitter

def test_developer_cli_launch_scene_structure():
    scene = DeveloperCliLaunchTemplate.create_scene(
        pkg_name="FastCLI",
        install_cmd="pip install fastcli",
        stars=10000,
        duration=2.0
    )

    assert isinstance(scene, Scene)
    assert scene.width == 1920
    assert scene.height == 1080

    # Check for core components
    windows = [c for c in scene.nodes if isinstance(c, CodeWindow)]
    assert len(windows) == 1

    charts = [c for c in scene.nodes if isinstance(c, BarChart)]
    assert len(charts) == 1

    counters = [c for c in scene.nodes if isinstance(c, MetricCounter)]
    assert len(counters) == 1

    emitters = [c for c in scene.nodes if isinstance(c, ParticleEmitter)]
    assert len(emitters) == 1

def test_developer_cli_launch_storyboard():
    scene = DeveloperCliLaunchTemplate.create_scene(
        pkg_name="TestCLI",
        install_cmd="npm i -g testcli",
        stars=5000,
        duration=0.1
    )
    frame = scene.render_frame(0.05)
    assert frame is not None
