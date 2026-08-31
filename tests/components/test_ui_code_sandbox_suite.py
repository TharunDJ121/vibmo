import pytest
import math
import cairo
from vibmo.core.color import Color, colors
from vibmo.product.ai.ui_code_sandbox_suite import (
    SplitCodePlayground,
    InteractiveTerminalLogs,
    RunCodeSuccessIndicator,
    DependencyInstallPill,
    CodeSandboxPlayground,
    SplitConsoleOutput,
)

def test_split_code_playground_draw():
    comp = SplitCodePlayground(width=1000.0, height=600.0)
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1000, 600)
    ctx = cairo.Context(surface)
    comp.draw(ctx, time=0.0)
    assert comp.width_val == 1000.0
    assert comp.height_val == 600.0

def test_interactive_terminal_logs_draw():
    comp = InteractiveTerminalLogs(logs=["Log 1", "Log 2"], execution_time="1.0s")
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 800, 400)
    ctx = cairo.Context(surface)
    comp.draw(ctx, time=0.0)
    assert comp is not None

def test_run_code_success_indicator_draw():
    comp = RunCodeSuccessIndicator(radius=20.0, success=False)
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 100, 100)
    ctx = cairo.Context(surface)
    comp.draw(ctx, time=0.0)
    comp.draw(ctx, time=math.pi / 10.0)
    action = comp.animate_success()
    assert action is not None
    comp.draw(ctx, time=0.0)

def test_dependency_install_pill_draw():
    comp = DependencyInstallPill(package_str="Done!")
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 220, 50)
    ctx = cairo.Context(surface)
    comp.draw(ctx, time=0.0)
    assert comp.package_str == "Done!"
