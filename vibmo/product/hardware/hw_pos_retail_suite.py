import math
from typing import Any, Tuple, Optional
from vibmo.scene.node import Node
from vibmo.core.signal import Signal
from vibmo.core.color import Color
from vibmo.core.vector import Vector2D
from vibmo.core.easing import Ease

class NfcHandheldPosTerminal(Node):
    """
    Square / Stripe style sleek handheld touchscreen POS terminal with angled display.
    """
    def __init__(
        self,
        width: float = 80.0,
        height: float = 150.0,
        color: Color = Color.hex("#111111"),
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.width = Signal(float(width), name="width")
        self.height = Signal(float(height), name="height")
        self.base_color = Signal(color, name="base_color")
        self.screen_color = Signal(Color.hex("#2A2A2A"), name="screen_color")
        self.payment_approved = Signal(0.0, name="payment_approved")

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        w = self.width.get(time)
        h = self.height.get(time)
        return (-w/2, -h/2, w, h)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width.get(time)
        h = self.height.get(time)
        bc = self.base_color.get(time)
        sc = self.screen_color.get(time)
        approved = self.payment_approved.get(time)

        # Draw base
        ctx.set_source_rgba(bc.r, bc.g, bc.b, bc.a * self.world_opacity(time))
        radius = 10.0

        # Rounded rectangle for base
        x = -w/2
        y = -h/2
        ctx.new_path()
        ctx.arc(x + radius, y + radius, radius, math.pi, 1.5 * math.pi)
        ctx.arc(x + w - radius, y + radius, radius, 1.5 * math.pi, 2 * math.pi)
        ctx.arc(x + w - radius, y + h - radius, radius, 0, 0.5 * math.pi)
        ctx.arc(x + radius, y + h - radius, radius, 0.5 * math.pi, math.pi)
        ctx.close_path()
        ctx.fill()

        # Draw screen
        sw = w * 0.9
        sh = h * 0.7
        sx = -sw/2
        sy = -h/2 + h * 0.05

        screen_bg = sc
        if approved > 0:
            screen_bg = sc.lerp(Color.hex("#10b981"), approved)

        ctx.set_source_rgba(screen_bg.r, screen_bg.g, screen_bg.b, screen_bg.a * self.world_opacity(time))
        ctx.rectangle(sx, sy, sw, sh)
        ctx.fill()

    def approve_payment(self, duration: float = 0.5) -> Any:
        return self.payment_approved.to(1.0, duration=duration, ease=Ease.out_quad)


class CountertopRegisterScreen(Node):
    """
    Angled merchant/customer dual-sided countertop register stand.
    """
    def __init__(
        self,
        width: float = 240.0,
        height: float = 160.0,
        stand_height: float = 80.0,
        color: Color = Color.hex("#e5e7eb"),
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.width = Signal(float(width), name="width")
        self.height = Signal(float(height), name="height")
        self.stand_height = Signal(float(stand_height), name="stand_height")
        self.base_color = Signal(color, name="base_color")
        self.screen_color = Signal(Color.hex("#ffffff"), name="screen_color")

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        w = self.width.get(time)
        h = self.height.get(time)
        sh = self.stand_height.get(time)
        return (-w/2, -h - sh, w, h + sh)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width.get(time)
        h = self.height.get(time)
        sh = self.stand_height.get(time)
        bc = self.base_color.get(time)
        sc = self.screen_color.get(time)
        op = self.world_opacity(time)

        # Stand base
        ctx.set_source_rgba(bc.r, bc.g, bc.b, bc.a * op)
        ctx.move_to(-w*0.2, 0)
        ctx.line_to(w*0.2, 0)
        ctx.line_to(w*0.1, -sh)
        ctx.line_to(-w*0.1, -sh)
        ctx.close_path()
        ctx.fill()

        # Main screen body
        sx = -w/2
        sy = -h - sh
        radius = 8.0

        ctx.set_source_rgba(bc.r * 0.9, bc.g * 0.9, bc.b * 0.9, bc.a * op)
        ctx.new_path()
        ctx.arc(sx + radius, sy + radius, radius, math.pi, 1.5 * math.pi)
        ctx.arc(sx + w - radius, sy + radius, radius, 1.5 * math.pi, 2 * math.pi)
        ctx.arc(sx + w - radius, sy + h - radius, radius, 0, 0.5 * math.pi)
        ctx.arc(sx + radius, sy + h - radius, radius, 0.5 * math.pi, math.pi)
        ctx.close_path()
        ctx.fill()

        # Screen
        ctx.set_source_rgba(sc.r, sc.g, sc.b, sc.a * op)
        ctx.rectangle(sx + w*0.05, sy + h*0.05, w*0.9, h*0.9)
        ctx.fill()


class ThermalReceiptSlot(Node):
    """
    Top receipt printer slot with animated paper receipt sliding out.
    """
    def __init__(
        self,
        slot_width: float = 120.0,
        receipt_length: float = 150.0,
        color: Color = Color.hex("#333333"),
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.slot_width = Signal(float(slot_width), name="slot_width")
        self.receipt_length = Signal(float(receipt_length), name="receipt_length")
        self.base_color = Signal(color, name="base_color")
        self.print_progress = Signal(0.0, name="print_progress")

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        sw = self.slot_width.get(time)
        rl = self.receipt_length.get(time)
        return (-sw/2, 0, sw, rl + 10)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        sw = self.slot_width.get(time)
        rl = self.receipt_length.get(time)
        bc = self.base_color.get(time)
        prog = self.print_progress.get(time)
        op = self.world_opacity(time)

        current_length = rl * prog

        # Slot
        ctx.set_source_rgba(bc.r, bc.g, bc.b, bc.a * op)
        ctx.rectangle(-sw/2, 0, sw, 10)
        ctx.fill()

        if current_length > 0:
            # Receipt paper
            ctx.set_source_rgba(1, 1, 1, op)
            rw = sw * 0.9
            rx = -rw/2
            ctx.rectangle(rx, 10, rw, current_length)
            ctx.fill()

            # Text lines on receipt
            ctx.set_source_rgba(0.2, 0.2, 0.2, op * 0.5)
            line_height = 8.0
            num_lines = int(current_length / (line_height * 2))
            for i in range(num_lines):
                ly = 10 + line_height + i * (line_height * 2)
                if ly + line_height > 10 + current_length:
                    break
                ctx.rectangle(rx + 10, ly, rw - 20, line_height)
                ctx.fill()

    def print_receipt(self, duration: float = 1.0) -> Any:
        return self.print_progress.to(1.0, duration=duration, ease=Ease.out_quad)


class TapPaymentSensor(Node):
    """
    Contactless NFC wave target with pulsing green/blue LED payment indicators.
    """
    def __init__(
        self,
        radius: float = 30.0,
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.radius = Signal(float(radius), name="radius")
        self.pulse = Signal(0.0, name="pulse")
        self.approved = Signal(0.0, name="approved")

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        r = self.radius.get(time)
        return (-r, -r, r*2, r*2)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        r = self.radius.get(time)
        pulse = self.pulse.get(time)
        approved = self.approved.get(time)
        op = self.world_opacity(time)

        # Background
        ctx.set_source_rgba(0.1, 0.1, 0.1, op)
        ctx.arc(0, 0, r, 0, 2 * math.pi)
        ctx.fill()

        # Wave symbol (NFC)
        ctx.set_source_rgba(1, 1, 1, op * 0.8)
        ctx.set_line_width(2.0)

        for i in range(1, 4):
            arc_r = r * 0.2 * i
            ctx.new_path()
            ctx.arc(0, r * 0.2, arc_r, -math.pi * 0.75, -math.pi * 0.25)
            ctx.stroke()

        # LED indicators
        led_color = Color.hex("#3b82f6") # Blue
        if approved > 0:
            led_color = led_color.lerp(Color.hex("#10b981"), approved) # Green

        ctx.set_source_rgba(led_color.r, led_color.g, led_color.b, led_color.a * op * (0.2 + 0.8 * pulse))

        led_r = 3.0
        for i in range(4):
            lx = -r * 0.6 + i * (r * 1.2 / 3)
            ly = -r * 0.6
            ctx.new_path()
            ctx.arc(lx, ly, led_r, 0, 2 * math.pi)
            ctx.fill()

    def pulse_led(self, duration: float = 1.0) -> Any:
        from vibmo.timeline.scheduler import SequentialGroup
        return SequentialGroup([
            self.pulse.to(1.0, duration=duration/2, ease=Ease.in_out_quad),
            self.pulse.to(0.0, duration=duration/2, ease=Ease.in_out_quad)
        ])

    def approve(self, duration: float = 0.3) -> Any:
        return self.approved.to(1.0, duration=duration, ease=Ease.out_quad)
