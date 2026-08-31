import pytest
import numpy as np
from vibmo.templates.turnkey.tmpl_fintech_crypto_card_suite import (
    FintechCryptoCardTemplate,
    TmplFintechCryptoCardSuite,
)
from vibmo.scene.scene import Scene
from vibmo.components.glass import GlassCard
from vibmo.components.counter import MetricCounter
from vibmo.typography.kinetic import KineticText
from vibmo.fx.backgrounds.bg_mesh_gradient_flow import MeshGradientFlow


def _walk_scene(node):
    yield node
    if hasattr(node, "nodes"):
        for child in node.nodes:
            yield from _walk_scene(child)
    if hasattr(node, "children"):
        for child in node.children:
            yield from _walk_scene(child)


def test_fintech_crypto_card_scene_creation():
    scene = FintechCryptoCardTemplate.create_scene(
        cardholder="SATOSHI NAKAMOTO",
        balance=250000.0,
        currency="USD",
        duration=5.0,
    )
    assert isinstance(scene, Scene)
    assert scene.width == 1920
    assert scene.height == 1080
    assert scene.duration >= 5.0

    nodes = list(_walk_scene(scene))

    cards = [n for n in nodes if isinstance(n, GlassCard)]
    assert len(cards) >= 1, "GlassCard must be present in crypto card scene"

    counters = [n for n in nodes if isinstance(n, MetricCounter)]
    assert len(counters) >= 1, "MetricCounter must be present in crypto card scene"

    texts = [n for n in nodes if isinstance(n, KineticText)]
    assert len(texts) >= 1, "KineticText must be present in crypto card scene"

    bgs = [n for n in nodes if isinstance(n, MeshGradientFlow)]
    assert len(bgs) >= 1, "MeshGradientFlow must be present in crypto card scene"


def test_tmpl_fintech_crypto_card_suite_build_scene():
    scene = TmplFintechCryptoCardSuite.build_scene(
        cardholder="HAL FINNEY",
        balance=1000000.0,
        currency="BTC",
        duration=4.0,
    )
    assert isinstance(scene, Scene)
    assert scene.duration >= 4.0

    frame = scene.render_frame(1.0)
    assert isinstance(frame, np.ndarray)
    assert frame.shape == (1080, 1920, 4)

    # Test pre-flight validation
    errors = scene.validate()
    assert isinstance(errors, list)


def test_tmpl_fintech_crypto_card_storyboard():
    scene = TmplFintechCryptoCardSuite.build_scene(cardholder="SATOSHI NAKAMOTO")
    storyboard = scene.storyboard(rows=1, cols=3)
    assert storyboard is not None
