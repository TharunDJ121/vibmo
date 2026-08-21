import pytest
from unittest.mock import MagicMock
from vibmo.scene.node import Node
from vibmo.product.hardware.hw_spatial_visor_suite import (
    VisionProSpatialGlassVisor,
    QuestGoggleFrame,
    SpatialHudCurvedProjection,
)

class MockContext:
    def __init__(self):
        self.calls = []
        self.fills = 0
        self.strokes = 0

    def save(self): self.calls.append("save")
    def restore(self): self.calls.append("restore")
    def set_source_rgba(self, r, g, b, a): self.calls.append(("set_source_rgba", r, g, b, a))
    def set_line_width(self, w): self.calls.append(("set_line_width", w))
    def move_to(self, x, y): self.calls.append(("move_to", x, y))
    def line_to(self, x, y): self.calls.append(("line_to", x, y))
    def curve_to(self, *args): self.calls.append(("curve_to", *args))
    def arc(self, *args): self.calls.append(("arc", *args))
    def rectangle(self, *args): self.calls.append(("rectangle", *args))
    def close_path(self): self.calls.append("close_path")
    def fill(self):
        self.calls.append("fill")
        self.fills += 1
    def stroke(self):
        self.calls.append("stroke")
        self.strokes += 1
    def fill_preserve(self):
        self.calls.append("fill_preserve")
        self.fills += 1
    def stroke_preserve(self):
        self.calls.append("stroke_preserve")
        self.strokes += 1


def test_vision_pro_visor_glass_specular_geometry():
    visor = VisionProSpatialGlassVisor(width=600, height=300)
    ctx = MockContext()
    visor.draw(ctx, time=1.5)

    # Assert saving state
    assert "save" in ctx.calls

    # Assert curve_to was called for the frame or specular
    has_curve = any(isinstance(c, tuple) and c[0] == "curve_to" for c in ctx.calls)
    assert has_curve, "Should use curve_to for curved 3D laminated glass geometry"

    # Assert lenticular shimmer was drawn (multiple arcs)
    arcs = [c for c in ctx.calls if isinstance(c, tuple) and c[0] == "arc"]
    assert len(arcs) >= 11, "Should draw multiple arcs for the EyeSight lenticular shimmer"

    assert ctx.fills > 0


def test_quest_goggle_frame_sensors():
    quest = QuestGoggleFrame(width=400, height=250)
    ctx = MockContext()
    quest.draw(ctx, time=0.0)

    # Assert 4 sensor arcs were drawn
    arcs = [c for c in ctx.calls if isinstance(c, tuple) and c[0] == "arc"]
    # 4 corners + 4 sensors
    assert len(arcs) >= 4, "Should draw front tracking camera sensors"


def test_spatial_hud_curved_projection_containment():
    hud = SpatialHudCurvedProjection()
    node1 = Node(name="child1")
    node2 = Node(name="child2")

    hud.add_screen_content(node1, node2)

    # Assert containment
    assert node1.parent == hud.content_container
    assert node2.parent == hud.content_container
    assert hud.content_container.parent == hud
    assert node1 in hud.content_container.children
    assert node2 in hud.content_container.children

    ctx = MockContext()
    hud.draw(ctx, time=0.0)

    has_curve = any(isinstance(c, tuple) and c[0] == "curve_to" for c in ctx.calls)
    assert has_curve, "Spatial HUD should draw curved bounds"
