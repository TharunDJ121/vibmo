import pytest
import math
from vibmo.core.color import Color
from vibmo.fx.backgrounds.bg_sunset_horizon_glow import CalifornianSunsetBackdrop, GoldenHourSkyGradient, AtmosphericHazeHorizon

def test_californian_sunset_backdrop_initialization():
    node = CalifornianSunsetBackdrop(width=1000, height=500)
    assert node.width == 1000
    assert node.height == 500
    
    bounds = node.local_bounds()
    assert bounds == (0.0, 0.0, 1000.0, 500.0)

def test_golden_hour_sky_gradient_initialization():
    node = GoldenHourSkyGradient(width=800, height=600)
    assert node.width == 800
    assert node.height == 600
    
    bounds = node.local_bounds()
    assert bounds == (0.0, 0.0, 800.0, 600.0)

def test_atmospheric_haze_horizon_initialization():
    node = AtmosphericHazeHorizon(width=1920, height=1080)
    assert node.width == 1920
    assert node.height == 1080
    
    bounds = node.local_bounds()
    assert bounds == (0.0, 0.0, 1920.0, 1080.0)

class MockPattern:
    def __init__(self, *args, **kwargs):
        self.stops = []
        
    def add_color_stop_rgba(self, offset, r, g, b, a):
        self.stops.append((offset, r, g, b, a))

import cairo

class MockCtx:
    def __init__(self):
        self.ops = []
        self.current_pattern = None
        
    def save(self):
        self.ops.append("save")
        
    def restore(self):
        self.ops.append("restore")
        
    def rectangle(self, x, y, w, h):
        self.ops.append(("rectangle", x, y, w, h))
        
    def set_source(self, pat):
        self.current_pattern = pat
        self.ops.append(("set_source", pat))
        
    def fill(self):
        self.ops.append("fill")
        
    def set_operator(self, op):
        self.ops.append(("set_operator", op))
        
    def new_path(self):
        self.ops.append("new_path")
        
    def move_to(self, x, y):
        self.ops.append(("move_to", x, y))
        
    def line_to(self, x, y):
        self.ops.append(("line_to", x, y))
        
    def close_path(self):
        self.ops.append("close_path")
        
    def set_source_rgba(self, r, g, b, a):
        self.ops.append(("set_source_rgba", r, g, b, a))
        
    def stroke(self):
        self.ops.append("stroke")
        
    def set_line_width(self, w):
        self.ops.append(("set_line_width", w))

def test_californian_sunset_backdrop_rendering(monkeypatch):
    monkeypatch.setattr(cairo, "LinearGradient", MockPattern)
    monkeypatch.setattr(cairo, "RadialGradient", MockPattern)

    node = CalifornianSunsetBackdrop(width=800, height=600)
    ctx = MockCtx()
    node.draw(ctx, time=1.0)
    
    assert "save" in ctx.ops
    assert ("rectangle", 0, 0, 800.0, 600.0) in ctx.ops
    assert "fill" in ctx.ops
    assert "restore" in ctx.ops
    
    # Verify linear gradient stops
    linear_patterns = [op[1] for op in ctx.ops if isinstance(op, tuple) and op[0] == "set_source" and type(op[1]) == MockPattern and len(op[1].stops) == 3]
    assert len(linear_patterns) >= 2
    
    base_gradient = linear_patterns[0]
    assert len(base_gradient.stops) == 3
    assert base_gradient.stops[0][0] == 0.0 # violet
    assert base_gradient.stops[1][0] == 0.5 # coral
    assert base_gradient.stops[2][0] == 1.0 # amber
    
    sun_glow = linear_patterns[1]
    assert len(sun_glow.stops) == 3
    assert sun_glow.stops[0][0] == 0.0
    assert sun_glow.stops[1][0] == 0.4
    assert sun_glow.stops[2][0] == 1.0
    
    # heat shimmer stroke check
    assert "stroke" in ctx.ops

def test_golden_hour_sky_gradient_rendering(monkeypatch):
    monkeypatch.setattr(cairo, "LinearGradient", MockPattern)
    
    node = GoldenHourSkyGradient(width=800, height=600)
    ctx = MockCtx()
    node.draw(ctx, time=1.0)
    
    assert "save" in ctx.ops
    assert ("rectangle", 0, 0, 800.0, 600.0) in ctx.ops
    assert "fill" in ctx.ops
    assert "restore" in ctx.ops
    
    patterns = [op[1] for op in ctx.ops if isinstance(op, tuple) and op[0] == "set_source" and type(op[1]) == MockPattern]
    assert len(patterns) == 1
    grad = patterns[0]
    assert len(grad.stops) == 2
    assert grad.stops[0][0] == 0.0
    assert grad.stops[1][0] == 1.0

def test_atmospheric_haze_horizon_rendering(monkeypatch):
    monkeypatch.setattr(cairo, "LinearGradient", MockPattern)
    node = AtmosphericHazeHorizon(width=800, height=600)
    ctx = MockCtx()
    node.draw(ctx, time=1.0)
    
    assert "save" in ctx.ops
    assert ("rectangle", 0, 0, 800.0, 600.0) in ctx.ops
    
    # Verify linear gradient
    patterns = [op[1] for op in ctx.ops if isinstance(op, tuple) and op[0] == "set_source" and type(op[1]) == MockPattern]
    assert len(patterns) == 1
    grad = patterns[0]
    assert len(grad.stops) == 2
    assert grad.stops[0][0] == 0.0
    assert grad.stops[1][0] == 1.0
    
    # Expect 3 layers of mountains
    new_paths = [op for op in ctx.ops if op == "new_path"]
    assert len(new_paths) == 3
    
    assert "restore" in ctx.ops
