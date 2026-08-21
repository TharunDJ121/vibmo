import pytest
import math
from unittest.mock import MagicMock
from vibmo.core.color import Color



from vibmo.fx.backgrounds.bg_circuit_board_traces import (
    PcbCircuitTracesFlow,
    MicrochipLogicPulse,
    CopperBusCurrentBackdrop,
)

def test_pcb_circuit_traces_flow_initialization():
    node = PcbCircuitTracesFlow(num_traces=5)
    assert node.num_traces == 5
    assert len(node.traces) == 5
    
    # Check that traces are generated properly
    for trace in node.traces:
        assert isinstance(trace, dict)
        assert "path" in trace
        assert "offset" in trace
        assert "speed" in trace
        assert isinstance(trace["path"], list)
        assert len(trace["path"]) >= 2
        for pt in trace["path"]:
            assert isinstance(pt, tuple)
            assert len(pt) == 2

def test_pcb_circuit_traces_flow_draw():
    node = PcbCircuitTracesFlow(num_traces=3)
    
    ctx = MagicMock()
    # Call draw with some time
    node.draw(ctx, time=1.0)
    
    # Ensure drawing calls were made
    assert ctx.set_source_rgba.called
    assert ctx.rectangle.called
    assert ctx.fill.called
    assert ctx.move_to.called
    assert ctx.line_to.called
    assert ctx.stroke.called

def test_microchip_logic_pulse_initialization():
    node = MicrochipLogicPulse(num_pins=16)
    assert node.num_pins == 16
    assert node.center_x == 960.0
    assert node.center_y == 540.0

def test_microchip_logic_pulse_draw():
    node = MicrochipLogicPulse(num_pins=16)
    ctx = MagicMock()
    node.draw(ctx, time=0.5)
    
    assert ctx.save.called
    assert ctx.restore.called
    assert ctx.translate.called
    assert ctx.rectangle.called
    assert ctx.fill.called
    assert ctx.stroke.called

def test_copper_bus_current_backdrop_initialization():
    node = CopperBusCurrentBackdrop(num_buses=8)
    assert node.num_buses == 8
    assert len(node.buses) == 8
    
    for bus in node.buses:
        assert isinstance(bus, dict)
        assert "horizontal" in bus
        assert "pos" in bus
        assert "thickness" in bus
        assert "speed" in bus

def test_copper_bus_current_backdrop_draw():
    node = CopperBusCurrentBackdrop(num_buses=5)
    ctx = MagicMock()
    node.draw(ctx, time=2.0)
    
    assert ctx.set_source_rgba.called
    assert ctx.rectangle.called
    assert ctx.fill.called
    assert ctx.move_to.called
    assert ctx.line_to.called
    assert ctx.stroke.called

def test_pcb_traces_geometry():
    node = PcbCircuitTracesFlow(num_traces=1)
    # Check that the segments are 45 degree angles or straight lines
    trace = node.traces[0]["path"]
    for i in range(len(trace) - 1):
        dx = trace[i+1][0] - trace[i][0]
        dy = trace[i+1][1] - trace[i][1]
        
        # Check angle is multiple of 45 deg
        if dx == 0 or dy == 0:
            continue # 0, 90, 180, 270 deg
        
        # for 45 deg angles, abs(dx) should be close to abs(dy)
        assert math.isclose(abs(dx), abs(dy), rel_tol=1e-3)

def test_pulse_motion():
    # Test that pulse actually moves over time
    node = PcbCircuitTracesFlow(num_traces=1)
    # Force the trace to be something simple
    node.traces = [{"path": [(0, 0), (100, 0)], "offset": 0.0, "speed": 1.0}]
    
    ctx1 = MagicMock()
    node.draw(ctx1, time=0.0)
    # Find the arc call to see where the pulse is drawn
    arc_calls_0 = [call for call in ctx1.arc.call_args_list]
    
    ctx2 = MagicMock()
    node.draw(ctx2, time=0.5)
    arc_calls_0_5 = [call for call in ctx2.arc.call_args_list]
    
    assert len(arc_calls_0) > 0
    assert len(arc_calls_0_5) > 0
    
    # Extract positions from the arc calls. Call signature: arc(x, y, radius, angle1, angle2)
    pos1 = arc_calls_0[0][0][:2]
    pos2 = arc_calls_0_5[0][0][:2]
    
    # Since speed=1.0, length=100. time=0.0 -> pos=(0, 0). time=0.5 -> pos=(50, 0).
    assert pos1 != pos2
    assert math.isclose(pos1[0], 0, abs_tol=1e-5)
    assert math.isclose(pos2[0], 50.0, abs_tol=1e-5)
