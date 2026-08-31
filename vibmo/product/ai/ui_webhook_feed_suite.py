"""
Webhook Live Activity Feed UI Suite for Vibmo / Motio.
Components:
- WebhookActivityFeed (WebhookEventStreamCard)
- HttpRequestInspector (PayloadJsonInspector)
- HttpStatusBadge
- RetryEventButton
"""

from __future__ import annotations
import math
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
import cairo

from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.scene.node import Node
from vibmo.spatial.shadows import DropShadow


class HttpStatusBadge(Node):
    """HTTP status code pill (e.g. `200 OK`, `404 Not Found`, `500 Error`)."""

    def __init__(self, status_code: int = 200, width: float = 68.0, height: float = 24.0, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.status_code = int(status_code)
        self.width_val = float(width)
        self.height_val = float(height)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        ctx.save()
        r = 6.0
        ctx.new_path()
        ctx.arc(w - r, r, r, -math.pi * 0.5, 0)
        ctx.arc(w - r, h - r, r, 0, math.pi * 0.5)
        ctx.arc(r, h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(r, r, r, math.pi, math.pi * 1.5)
        ctx.close_path()

        if 200 <= self.status_code < 300:
            ctx.set_source_rgba(0.05, 0.2, 0.1, 0.9)
            ctx.fill_preserve()
            ctx.set_source_rgba(0.1, 0.85, 0.45, 0.8)
            text_color = (0.2, 1.0, 0.5, 0.95)
        else:
            ctx.set_source_rgba(0.2, 0.05, 0.08, 0.9)
            ctx.fill_preserve()
            ctx.set_source_rgba(0.9, 0.25, 0.35, 0.8)
            text_color = (1.0, 0.3, 0.4, 0.95)

        ctx.set_line_width(1.0)
        ctx.stroke()

        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(10.5)
        ctx.set_source_rgba(*text_color)
        text = str(self.status_code)
        ext = ctx.text_extents(text)
        ctx.move_to((w - ext.width) * 0.5, h * 0.5 + ext.height * 0.35)
        ctx.show_text(text)
        ctx.restore()


class RetryEventButton(Node):
    """Button to manually re-send / simulate a webhook delivery attempt."""

    def __init__(self, width: float = 64.0, height: float = 24.0, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.width_val = float(width)
        self.height_val = float(height)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        ctx.save()
        r = 6.0
        ctx.new_path()
        ctx.arc(w - r, r, r, -math.pi * 0.5, 0)
        ctx.arc(w - r, h - r, r, 0, math.pi * 0.5)
        ctx.arc(r, h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(r, r, r, math.pi, math.pi * 1.5)
        ctx.close_path()

        ctx.set_source_rgba(0.12, 0.16, 0.24, 0.85)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.25, 0.35, 0.5, 0.6)
        ctx.set_line_width(1.0)
        ctx.stroke()

        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(10.0)
        ctx.set_source_rgba(0.8, 0.9, 1.0, 0.9)
        text = "↺ Retry"
        ext = ctx.text_extents(text)
        ctx.move_to((w - ext.width) * 0.5, h * 0.5 + ext.height * 0.35)
        ctx.show_text(text)
        ctx.restore()


class HttpRequestInspector(Node):
    """HTTP request & payload inspector pane."""

    def __init__(
        self,
        event_name: str = "payment.succeeded",
        method: str = "POST",
        endpoint: str = "https://api.vibmo.ai/v1/webhooks",
        payload: Optional[str] = None,
        width: float = 340.0,
        height: float = 360.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.event_name = Signal(event_name, f"{self.name}.event_name")
        self.method = method
        self.endpoint = endpoint
        self.payload = Signal(payload or '{\n  "id": "evt_984f1a",\n  "event": "payment.succeeded",\n  "amount_cents": 4900,\n  "currency": "usd",\n  "status": "paid"\n}', f"{self.name}.payload")
        self.width_val = float(width)
        self.height_val = float(height)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        ctx.save()
        r = 10.0
        ctx.new_path()
        ctx.arc(w - r, r, r, -math.pi * 0.5, 0)
        ctx.arc(w - r, h - r, r, 0, math.pi * 0.5)
        ctx.arc(r, h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(r, r, r, math.pi, math.pi * 1.5)
        ctx.close_path()

        ctx.set_source_rgba(0.03, 0.05, 0.09, 0.9)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.18, 0.24, 0.35, 0.6)
        ctx.set_line_width(1.0)
        ctx.stroke()

        # Method & Endpoint header
        ctx.select_font_face("Consolas", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(11.0)
        ctx.set_source_rgba(0.1, 0.85, 0.5, 0.95)
        ctx.move_to(14.0, 26.0)
        ctx.show_text(f"{self.method} ")

        ctx.set_source_rgba(0.7, 0.8, 0.9, 0.85)
        ctx.show_text(self.endpoint[:28] + "...")

        # JSON Payload
        ctx.select_font_face("Consolas", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(11.0)
        ctx.set_source_rgba(0.3, 0.85, 1.0, 0.9)

        payload_lines = self.payload.get(time).split("\n")
        for i, line in enumerate(payload_lines[:12]):
            ctx.move_to(14.0, 54.0 + i * 20.0)
            ctx.show_text(line)

        ctx.restore()


PayloadJsonInspector = HttpRequestInspector


class WebhookActivityFeed(Node):
    """
    Webhook Live Activity Feed Suite.
    Renders real-time incoming webhook event logs, status code badges,
    retry buttons, and structured HTTP JSON payload inspection.
    """

    def __init__(
        self,
        events: Optional[List[Dict[str, Any]]] = None,
        width: float = 720.0,
        height: float = 480.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.width_val = float(width)
        self.height_val = float(height)
        self.shadow = DropShadow(color=Color(0.0, 0.0, 0.0, 0.5), blur=32.0, offset=(0.0, 16.0))

        self.events_list: List[Dict[str, Any]] = events or [
            {"time": "12:04:18", "event": "user.signup", "status": 200},
            {"time": "12:04:12", "event": "subscription.renewed", "status": 200},
            {"time": "12:03:59", "event": "payment.succeeded", "status": 200},
            {"time": "12:03:45", "event": "invoice.generated", "status": 200},
            {"time": "12:02:30", "event": "api_key.created", "status": 200},
        ]

        # Inspector pane on right
        self.inspector = HttpRequestInspector(width=320.0, height=390.0)
        self.inspector.position.set(Vector2D(self.width_val - 344.0, 68.0))
        self.add(self.inspector)

        # Pulse signal for new events
        self.event_pulse = Signal(0.0, f"{self.name}.event_pulse")

    def simulate_event(
        self,
        event_name: str = "payment.succeeded",
        status_code: int = 200,
        duration: float = 0.8,
        ease: EasingFunc = Ease.out_quad,
    ) -> AnimationAction:
        """
        Fluent generator animation verb to trigger an incoming webhook event.
        """
        self.events_list.insert(0, {"time": "12:04:25", "event": event_name, "status": status_code})
        self.inspector.event_name.set(event_name)
        self.inspector.payload.set(f'{{\n  "id": "evt_{abs(hash(event_name)) % 100000:05x}",\n  "event": "{event_name}",\n  "status": "delivered",\n  "timestamp": "2026-08-30T12:04:25Z"\n}}')
        self.event_pulse.set(1.0)
        return self.event_pulse.to(0.0, duration=duration, ease=ease)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        ctx.save()

        # Canvas card
        r = 16.0
        ctx.new_path()
        ctx.arc(w - r, r, r, -math.pi * 0.5, 0)
        ctx.arc(w - r, h - r, r, 0, math.pi * 0.5)
        ctx.arc(r, h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(r, r, r, math.pi, math.pi * 1.5)
        ctx.close_path()

        ctx.set_source_rgba(0.04, 0.06, 0.1, 0.95)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.18, 0.25, 0.38, 0.8)
        ctx.set_line_width(1.5)
        ctx.stroke()

        # Header Title
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(15.0)
        ctx.set_source_rgba(0.95, 0.98, 1.0, 0.95)
        ctx.move_to(24.0, 42.0)
        ctx.show_text("Live Webhooks & Event Ingestion Stream")

        # Stream feed list on left
        pulse = self.event_pulse.get(time)
        for i, ev in enumerate(self.events_list[:6]):
            ey = 80.0 + i * 58.0
            ew = 330.0
            eh = 46.0

            ctx.new_path()
            er = 8.0
            ctx.arc(24.0 + ew - er, ey + er, er, -math.pi * 0.5, 0)
            ctx.arc(24.0 + ew - er, ey + eh - er, er, 0, math.pi * 0.5)
            ctx.arc(24.0 + er, ey + eh - er, er, math.pi * 0.5, math.pi)
            ctx.arc(24.0 + er, ey + er, er, math.pi, math.pi * 1.5)
            ctx.close_path()

            if i == 0 and pulse > 0.05:
                ctx.set_source_rgba(0.1, 0.25, 0.4, 0.95)
                ctx.fill_preserve()
                ctx.set_source_rgba(0.2, 0.8, 1.0, pulse)
                ctx.set_line_width(1.5)
                ctx.stroke()
            else:
                ctx.set_source_rgba(0.06, 0.09, 0.14, 0.7)
                ctx.fill_preserve()
                ctx.set_source_rgba(0.18, 0.24, 0.35, 0.5)
                ctx.set_line_width(1.0)
                ctx.stroke()

            # Event name
            ctx.select_font_face("Consolas", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(11.5)
            ctx.set_source_rgba(0.9, 0.95, 1.0, 0.95)
            ctx.move_to(36.0, ey + 22.0)
            ctx.show_text(ev.get("event", "event"))

            # Timestamp
            ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            ctx.set_font_size(10.0)
            ctx.set_source_rgba(0.5, 0.6, 0.75, 0.8)
            ctx.move_to(36.0, ey + 38.0)
            ctx.show_text(ev.get("time", "12:00:00"))

            # Status 200 badge
            status_x = 24.0 + ew - 50.0
            ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(11.0)
            ctx.set_source_rgba(0.1, 0.85, 0.45, 0.95)
            ctx.move_to(status_x, ey + 28.0)
            ctx.show_text(f"{ev.get('status', 200)}")

        super().draw(ctx, time)
        ctx.restore()


WebhookEventStreamCard = WebhookActivityFeed
