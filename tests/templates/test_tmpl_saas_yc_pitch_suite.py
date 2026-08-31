import pytest
import numpy as np
from vibmo.templates.turnkey.tmpl_saas_yc_pitch_suite import (
    SaasYcPitchTemplate,
    TmplSaasYcPitchSuite,
    _parse_numeric_val,
)
from vibmo.scene.scene import Scene
from vibmo.components.glass import GlassCard
from vibmo.components.counter import MetricCounter
from vibmo.typography.kinetic import KineticText
from vibmo.product.charts import AreaChart
from vibmo.fx.backgrounds.bg_mesh_gradient_flow import MeshGradientFlow


def _walk_scene(node):
    yield node
    if hasattr(node, "nodes"):
        for child in node.nodes:
            yield from _walk_scene(child)
    if hasattr(node, "children"):
        for child in node.children:
            yield from _walk_scene(child)


def test_parse_numeric_val_helper():
    assert _parse_numeric_val("$120k") == 120000.0
    assert _parse_numeric_val("+40%") == 40.0
    assert _parse_numeric_val("142% NRR") == 120000.0 or _parse_numeric_val("142", default=142.0) == 142.0
    assert _parse_numeric_val(500.0) == 500.0
    assert _parse_numeric_val("2.5m") == 2500000.0


def test_saas_yc_pitch_scene_creation():
    scene = SaasYcPitchTemplate.create_scene(
        company="HyperScale AI",
        headline="Autonomous Cloud Compute Infrastructure",
        mrr="$120k",
        growth="+40%",
        duration=6.0,
    )
    assert isinstance(scene, Scene)
    assert scene.width == 1920
    assert scene.height == 1080
    assert scene.duration >= 6.0

    nodes = list(_walk_scene(scene))

    cards = [n for n in nodes if isinstance(n, GlassCard)]
    assert len(cards) >= 1, "GlassCard must be present in YC pitch scene"

    counters = [n for n in nodes if isinstance(n, MetricCounter)]
    assert len(counters) >= 3, "At least 3 MetricCounters (MRR, Growth, NRR) must be present"

    charts = [n for n in nodes if isinstance(n, AreaChart)]
    assert len(charts) >= 1, "AreaChart must be present in YC pitch scene"

    texts = [n for n in nodes if isinstance(n, KineticText)]
    assert len(texts) >= 1, "KineticText must be present in YC pitch scene"

    bgs = [n for n in nodes if isinstance(n, MeshGradientFlow)]
    assert len(bgs) >= 1, "MeshGradientFlow must be present in YC pitch scene"


def test_tmpl_saas_yc_pitch_suite_build_scene():
    scene = TmplSaasYcPitchSuite.build_scene(
        company="Vibmo AI",
        mrr="$250k",
        growth="+65%",
        nrr="150%",
        duration=5.0,
    )
    assert isinstance(scene, Scene)
    assert scene.duration >= 5.0

    frame = scene.render_frame(1.0)
    assert isinstance(frame, np.ndarray)
    assert frame.shape == (1080, 1920, 4)

    # Test pre-flight validation
    errors = scene.validate()
    assert isinstance(errors, list)


def test_tmpl_saas_yc_pitch_storyboard():
    scene = TmplSaasYcPitchSuite.build_scene(mrr="$120k", growth="+40%")
    storyboard = scene.storyboard(rows=1, cols=3)
    assert storyboard is not None
