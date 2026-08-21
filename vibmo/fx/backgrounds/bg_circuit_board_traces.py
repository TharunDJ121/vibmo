import math
import random
from typing import Any, List, Tuple
from motio.agent_api import *

class PcbCircuitTracesFlow(Node):
    """
    Matt dark green/black PCB substrate with golden 45-degree angle
    circuit traces and electric current pulses traveling along routes.
    """
    def __init__(
        self,
        width: float = 1920.0,
        height: float = 1080.0,
        board_color: Color = Color.from_hex("#0a150e"),
        trace_color: Color = Color.from_hex("#d4af37"),
        pulse_color: Color = Color.from_hex("#ffea8c"),
        num_traces: int = 20,
        name: str = "PcbCircuitTracesFlow"
    ):
        super().__init__(name=name)
        self.width = width
        self.height = height
        self.board_color = board_color
        self.trace_color = trace_color
        self.pulse_color = pulse_color
        self.num_traces = num_traces

        self.traces = self._generate_traces()

    def _generate_traces(self) -> List[dict]:
        # Generate some 45-degree angled paths
        traces = []
        for _ in range(self.num_traces):
            x = random.uniform(0, self.width)
            y = random.uniform(0, self.height)
            path = [(x, y)]
            segments = random.randint(2, 6)
            current_x, current_y = x, y
            for _ in range(segments):
                direction = random.choice([(1, 0), (0, 1), (1, 1), (1, -1), (-1, 0), (0, -1), (-1, 1), (-1, -1)])
                length = random.uniform(50, 200)
                next_x = current_x + direction[0] * length
                next_y = current_y + direction[1] * length

                # To maintain 45 degree angles, we can't clamp independently.
                # If we go out of bounds, we just stop the trace here.
                if next_x < 0 or next_x > self.width or next_y < 0 or next_y > self.height:
                    break

                path.append((next_x, next_y))
                current_x, current_y = next_x, next_y
            traces.append({"path": path, "offset": random.random(), "speed": random.uniform(0.3, 0.8)})
        return traces

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        # Draw board background
        ctx.set_source_rgba(self.board_color.r, self.board_color.g, self.board_color.b, self.board_color.a)
        ctx.rectangle(0, 0, self.width, self.height)
        ctx.fill()

        # Draw traces
        ctx.set_line_width(2.0)
        ctx.set_source_rgba(self.trace_color.r, self.trace_color.g, self.trace_color.b, self.trace_color.a * 0.5)

        for trace in self.traces:
            path = trace["path"]
            if not path:
                continue
            ctx.move_to(path[0][0], path[0][1])
            for pt in path[1:]:
                ctx.line_to(pt[0], pt[1])
            ctx.stroke()

            # Draw pulses on the path based on time
            pulse_progress = (time * trace["speed"] + trace["offset"]) % 1.0
            # A simple approach to find the pulse position
            total_length = sum(math.hypot(path[i+1][0] - path[i][0], path[i+1][1] - path[i][1]) for i in range(len(path)-1))
            if total_length == 0:
                continue

            target_length = total_length * pulse_progress
            current_length = 0.0
            for i in range(len(path)-1):
                seg_len = math.hypot(path[i+1][0] - path[i][0], path[i+1][1] - path[i][1])
                if current_length + seg_len >= target_length:
                    t = (target_length - current_length) / seg_len
                    px = path[i][0] + t * (path[i+1][0] - path[i][0])
                    py = path[i][1] + t * (path[i+1][1] - path[i][1])

                    ctx.set_source_rgba(self.pulse_color.r, self.pulse_color.g, self.pulse_color.b, self.pulse_color.a)
                    ctx.arc(px, py, 4.0, 0, 2 * math.pi)
                    ctx.fill()
                    # Reset trace color for next path
                    ctx.set_source_rgba(self.trace_color.r, self.trace_color.g, self.trace_color.b, self.trace_color.a * 0.5)
                    break
                current_length += seg_len


class MicrochipLogicPulse(Node):
    """
    Central silicon die radiating electric logic bus signals across surrounding trace pins.
    """
    def __init__(
        self,
        center_x: float = 960.0,
        center_y: float = 540.0,
        die_size: float = 150.0,
        die_color: Color = Color.from_hex("#1a1a1a"),
        pin_color: Color = Color.from_hex("#8b8b8b"),
        signal_color: Color = Color.from_hex("#00ffcc"),
        num_pins: int = 32,
        name: str = "MicrochipLogicPulse"
    ):
        super().__init__(name=name)
        self.center_x = center_x
        self.center_y = center_y
        self.die_size = die_size
        self.die_color = die_color
        self.pin_color = pin_color
        self.signal_color = signal_color
        self.num_pins = num_pins

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        ctx.translate(self.center_x, self.center_y)

        # Draw central die
        ctx.set_source_rgba(self.die_color.r, self.die_color.g, self.die_color.b, self.die_color.a)
        ctx.rectangle(-self.die_size/2, -self.die_size/2, self.die_size, self.die_size)
        ctx.fill()

        ctx.set_source_rgba(0.2, 0.2, 0.2, 1.0)
        ctx.set_line_width(2.0)
        ctx.rectangle(-self.die_size/2, -self.die_size/2, self.die_size, self.die_size)
        ctx.stroke()

        # Draw pins and radiating signals
        pins_per_side = self.num_pins // 4
        pin_length = 40.0
        pin_spacing = self.die_size / (pins_per_side + 1)

        for side in range(4):
            ctx.save()
            ctx.rotate(side * math.pi / 2)

            for i in range(pins_per_side):
                offset = (i + 1) * pin_spacing - self.die_size / 2

                # Draw pin
                ctx.set_source_rgba(self.pin_color.r, self.pin_color.g, self.pin_color.b, self.pin_color.a)
                ctx.set_line_width(4.0)
                ctx.move_to(offset, self.die_size / 2)
                ctx.line_to(offset, self.die_size / 2 + pin_length)
                ctx.stroke()

                # Draw radiating signal
                # Offset by i so they don't all pulse at exactly the same time
                pulse_phase = (time * 2.0 + i * 0.2 + side * 0.5) % 1.0
                if pulse_phase < 0.3:
                    intensity = 1.0 - (pulse_phase / 0.3)
                    ctx.set_source_rgba(self.signal_color.r, self.signal_color.g, self.signal_color.b, intensity)
                    ctx.arc(offset, self.die_size / 2 + pin_length + 10.0, 5.0, 0, 2 * math.pi)
                    ctx.fill()

                    # Trace signal line outward
                    ctx.set_line_width(2.0)
                    ctx.move_to(offset, self.die_size / 2 + pin_length)
                    ctx.line_to(offset, self.die_size / 2 + pin_length + 50.0)
                    ctx.stroke()

            ctx.restore()

        ctx.restore()


class CopperBusCurrentBackdrop(Node):
    """
    Glowing bus lines pulsing with digital clock signals.
    """
    def __init__(
        self,
        width: float = 1920.0,
        height: float = 1080.0,
        bg_color: Color = Color.from_hex("#000000"),
        bus_color: Color = Color.from_hex("#b87333"),
        pulse_color: Color = Color.from_hex("#ffb366"),
        num_buses: int = 10,
        name: str = "CopperBusCurrentBackdrop"
    ):
        super().__init__(name=name)
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.bus_color = bus_color
        self.pulse_color = pulse_color
        self.num_buses = num_buses

        self.buses = self._generate_buses()

    def _generate_buses(self) -> List[dict]:
        buses = []
        for i in range(self.num_buses):
            horizontal = random.choice([True, False])
            if horizontal:
                y = random.uniform(0, self.height)
                buses.append({"horizontal": True, "pos": y, "thickness": random.uniform(4.0, 12.0), "speed": random.uniform(0.5, 2.0)})
            else:
                x = random.uniform(0, self.width)
                buses.append({"horizontal": False, "pos": x, "thickness": random.uniform(4.0, 12.0), "speed": random.uniform(0.5, 2.0)})
        return buses

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        # Draw background
        ctx.set_source_rgba(self.bg_color.r, self.bg_color.g, self.bg_color.b, self.bg_color.a)
        ctx.rectangle(0, 0, self.width, self.height)
        ctx.fill()

        for bus in self.buses:
            # Draw bus line
            ctx.set_source_rgba(self.bus_color.r, self.bus_color.g, self.bus_color.b, self.bus_color.a * 0.6)
            ctx.set_line_width(bus["thickness"])

            if bus["horizontal"]:
                ctx.move_to(0, bus["pos"])
                ctx.line_to(self.width, bus["pos"])
            else:
                ctx.move_to(bus["pos"], 0)
                ctx.line_to(bus["pos"], self.height)
            ctx.stroke()

            # Draw pulsing clock signal along the bus
            # Divide bus into segments that light up
            segment_length = 100.0
            gap = 50.0
            total_length = self.width if bus["horizontal"] else self.height

            offset = (time * 150.0 * bus["speed"]) % (segment_length + gap)

            ctx.set_source_rgba(self.pulse_color.r, self.pulse_color.g, self.pulse_color.b, self.pulse_color.a)

            pos = - (segment_length + gap) + offset
            while pos < total_length:
                if bus["horizontal"]:
                    ctx.move_to(pos, bus["pos"])
                    ctx.line_to(pos + segment_length, bus["pos"])
                else:
                    ctx.move_to(bus["pos"], pos)
                    ctx.line_to(bus["pos"], pos + segment_length)
                ctx.stroke()
                pos += segment_length + gap
