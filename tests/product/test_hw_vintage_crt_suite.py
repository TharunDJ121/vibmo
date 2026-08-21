"""
Unit tests for the Retro 1990s Computer & Arcade Hardware mockup suite.
"""

import pytest
import cairo
from typing import Any, List
from vibmo.product.hardware.hw_vintage_crt_suite import (
    BeigeCrtMonitor1990s,
    ArcadeCabinetBezel,
    RetroPortableTvAntenna
)


class MockContext:
    """A minimal mock for testing PyCairo context operations."""
    def __init__(self) -> None:
        self.operations: List[str] = []

    def save(self) -> None:
        self.operations.append("save")

    def restore(self) -> None:
        self.operations.append("restore")

    def new_path(self) -> None:
        self.operations.append("new_path")

    def close_path(self) -> None:
        self.operations.append("close_path")

    def arc(self, xc: float, yc: float, radius: float, angle1: float, angle2: float) -> None:
        self.operations.append(f"arc({xc}, {yc}, {radius})")

    def clip(self) -> None:
        self.operations.append("clip")

    def set_source_rgba(self, r: float, g: float, b: float, a: float) -> None:
        self.operations.append(f"set_source_rgba({r}, {g}, {b}, {a})")

    def fill(self) -> None:
        self.operations.append("fill")

    def fill_preserve(self) -> None:
        self.operations.append("fill_preserve")

    def stroke(self) -> None:
        self.operations.append("stroke")

    def set_line_width(self, width: float) -> None:
        self.operations.append(f"set_line_width({width})")

    def paint(self) -> None:
        self.operations.append("paint")

    def move_to(self, x: float, y: float) -> None:
        self.operations.append(f"move_to({x}, {y})")

    def line_to(self, x: float, y: float) -> None:
        self.operations.append(f"line_to({x}, {y})")

    def select_font_face(self, family: str, slant: Any, weight: Any) -> None:
        self.operations.append(f"select_font_face({family})")

    def set_font_size(self, size: float) -> None:
        self.operations.append(f"set_font_size({size})")

    def show_text(self, text: str) -> None:
        self.operations.append(f"show_text({text})")


def test_beige_crt_monitor_rendering() -> None:
    monitor = BeigeCrtMonitor1990s(width=400, height=350)
    ctx = MockContext()
    monitor.draw(ctx)

    ops = ctx.operations
    assert "save" in ops
    assert "clip" in ops  # Ensures the screen mask setup is called
    assert "paint" in ops  # Background paint
    assert "restore" in ops

    # Check chassis outline arc usage (rounded rect helper creates arcs)
    arcs = [op for op in ops if op.startswith("arc")]
    assert len(arcs) > 0

def test_arcade_cabinet_bezel_rendering() -> None:
    arcade = ArcadeCabinetBezel(width=600, height=800)
    ctx = MockContext()
    arcade.draw(ctx)

    ops = ctx.operations
    assert "save" in ops
    assert "show_text(ARCADE)" in ops
    assert "clip" in ops
    assert "restore" in ops

def test_retro_portable_tv_antenna_rendering() -> None:
    tv = RetroPortableTvAntenna(width=350, height=280)
    ctx = MockContext()
    tv.draw(ctx)

    ops = ctx.operations
    assert "save" in ops
    assert "clip" in ops

    # Check lines (antennas)
    lines = [op for op in ops if op.startswith("line_to")]
    assert len(lines) > 0
    assert "restore" in ops
