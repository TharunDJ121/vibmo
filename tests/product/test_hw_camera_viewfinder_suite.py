import pytest
from vibmo.product.hardware.hw_camera_viewfinder_suite import (
    DslrCameraViewfinderHud,
    CinemaCameraCageRig,
    DroneGimbalTelemetryHud,
)

class MockContext:
    def __init__(self):
        self.operations = []
        self.saved_states = 0
        self.matrix = [(0, 0)]

    def save(self):
        self.saved_states += 1
        self.operations.append("save")

    def restore(self):
        if self.saved_states > 0:
            self.saved_states -= 1
        self.operations.append("restore")

    def set_source_rgba(self, r, g, b, a):
        self.operations.append(f"set_source_rgba({r}, {g}, {b}, {a})")

    def set_line_width(self, w):
        self.operations.append(f"set_line_width({w})")

    def move_to(self, x, y):
        self.operations.append(f"move_to({x}, {y})")

    def line_to(self, x, y):
        self.operations.append(f"line_to({x}, {y})")

    def rectangle(self, x, y, w, h):
        self.operations.append(f"rectangle({x}, {y}, {w}, {h})")

    def stroke(self):
        self.operations.append("stroke")

    def fill(self):
        self.operations.append("fill")

    def fill_preserve(self):
        self.operations.append("fill_preserve")

    def select_font_face(self, family, slant=None, weight=None):
        self.operations.append(f"select_font_face({family})")

    def set_font_size(self, size):
        self.operations.append(f"set_font_size({size})")

    def show_text(self, text):
        self.operations.append(f"show_text({text})")


def test_dslr_camera_viewfinder_hud_render():
    hud = DslrCameraViewfinderHud()
    ctx = MockContext()
    hud.draw(ctx, 0.0)

    assert "save" in ctx.operations
    assert "set_source_rgba(1, 0, 0, 0.8)" in ctx.operations
    assert "set_line_width(2)" in ctx.operations
    assert any(op.startswith("show_text(") for op in ctx.operations)
    assert "restore" in ctx.operations

def test_cinema_camera_cage_rig_render():
    rig = CinemaCameraCageRig()
    ctx = MockContext()
    rig.draw(ctx, 0.0)

    assert "save" in ctx.operations
    assert "set_line_width(4)" in ctx.operations
    assert any(op.startswith("rectangle(") for op in ctx.operations)
    assert "fill_preserve" in ctx.operations
    assert "restore" in ctx.operations

def test_drone_gimbal_telemetry_hud_render():
    hud = DroneGimbalTelemetryHud()
    ctx = MockContext()
    hud.draw(ctx, 0.0)

    assert "save" in ctx.operations
    assert "set_source_rgba(0, 1, 0, 0.8)" in ctx.operations
    assert any(op.startswith("line_to(") for op in ctx.operations)
    assert any(op.startswith("show_text(ALT:") for op in ctx.operations)
    assert "restore" in ctx.operations
