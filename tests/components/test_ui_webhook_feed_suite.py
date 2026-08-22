import pytest
import math
from unittest.mock import Mock, call, ANY

from vibmo.product.ai.ui_webhook_feed_suite import (
    WebhookEventStreamCard,
    HttpStatusBadge,
    PayloadJsonInspector,
    RetryEventButton
)

class MockContext:
    def __init__(self):
        self.operations = []
        self.current_color = None
        self._font_size = 10
        self._line_width = 1

    def save(self): self.operations.append(('save',))
    def restore(self): self.operations.append(('restore',))
    def rectangle(self, x, y, w, h): self.operations.append(('rectangle', x, y, w, h))
    def clip(self): self.operations.append(('clip',))
    def fill(self): self.operations.append(('fill',))
    def stroke(self): self.operations.append(('stroke',))
    def set_source_rgba(self, r, g, b, a):
        self.current_color = (r, g, b, a)
        self.operations.append(('set_source_rgba', r, g, b, a))
    def set_font_size(self, size):
        self._font_size = size
        self.operations.append(('set_font_size', size))
    def move_to(self, x, y): self.operations.append(('move_to', x, y))
    def show_text(self, text): self.operations.append(('show_text', text))
    def arc(self, xc, yc, radius, angle1, angle2): self.operations.append(('arc', xc, yc, radius, angle1, angle2))
    def close_path(self): self.operations.append(('close_path',))
    def text_extents(self, text):
        mock_extents = Mock()
        mock_extents.width = len(text) * self._font_size * 0.6
        mock_extents.height = self._font_size
        mock_extents.y_bearing = -self._font_size
        mock_extents.x_advance = mock_extents.width
        return mock_extents
    def translate(self, tx, ty): self.operations.append(('translate', tx, ty))
    def rotate(self, angle): self.operations.append(('rotate', angle))
    def set_line_width(self, width):
        self._line_width = width
        self.operations.append(('set_line_width', width))
    def line_to(self, x, y): self.operations.append(('line_to', x, y))

def test_webhook_event_stream_card():
    events = [
        {"timestamp": "10:00:00", "event": "payment.succeeded"},
        {"timestamp": "10:00:05", "event": "user.created"}
    ]
    card = WebhookEventStreamCard(events=events, width=500.0, height=400.0)
    ctx = MockContext()
    card.draw(ctx, 0.0)

    assert ('save',) in ctx.operations
    assert ('rectangle', 0, 0, 500.0, 400.0) in ctx.operations
    assert ('show_text', "10:00:00") in ctx.operations
    assert ('show_text', "payment.succeeded") in ctx.operations
    assert ('show_text', "10:00:05") in ctx.operations
    assert ('show_text', "user.created") in ctx.operations
    assert ('restore',) in ctx.operations

def test_http_status_badge_200():
    badge = HttpStatusBadge(status_code=200)
    ctx = MockContext()
    badge.draw(ctx, 0.0)

    # 200 OK should be green (#D1FAE5)
    r = 209/255; g = 250/255; b = 229/255
    has_green_bg = any(
        op[0] == 'set_source_rgba' and abs(op[1] - r) < 0.01 and abs(op[2] - g) < 0.01 and abs(op[3] - b) < 0.01
        for op in ctx.operations
    )
    assert has_green_bg
    assert ('show_text', "200 OK") in ctx.operations

def test_http_status_badge_404():
    badge = HttpStatusBadge(status_code=404)
    ctx = MockContext()
    badge.draw(ctx, 0.0)

    # 404 should be amber (#FEF3C7)
    r = 254/255; g = 243/255; b = 199/255
    has_amber_bg = any(
        op[0] == 'set_source_rgba' and abs(op[1] - r) < 0.01 and abs(op[2] - g) < 0.01 and abs(op[3] - b) < 0.01
        for op in ctx.operations
    )
    assert has_amber_bg
    assert ('show_text', "404 Not Found") in ctx.operations

def test_http_status_badge_500():
    badge = HttpStatusBadge(status_code=500)
    ctx = MockContext()
    badge.draw(ctx, 0.0)

    # 500 should be red (#FEE2E2)
    r = 254/255; g = 226/255; b = 226/255
    has_red_bg = any(
        op[0] == 'set_source_rgba' and abs(op[1] - r) < 0.01 and abs(op[2] - g) < 0.01 and abs(op[3] - b) < 0.01
        for op in ctx.operations
    )
    assert has_red_bg
    assert ('show_text', "500 Server Error") in ctx.operations

def test_payload_json_inspector():
    payload = '{\n  "id": "evt_123",\n  "type": "charge.succeeded"\n}'
    inspector = PayloadJsonInspector(payload=payload, width=300.0, height=200.0, is_open=True)
    ctx = MockContext()
    inspector.draw(ctx, 0.0)

    assert ('clip',) in ctx.operations
    assert ('show_text', '{') in ctx.operations
    assert ('show_text', '  "id":') in ctx.operations
    assert ('show_text', ' "evt_123",') in ctx.operations

    # Test closed state
    inspector.is_open.set(0.0)
    ctx_closed = MockContext()
    inspector.draw(ctx_closed, 0.0)
    assert ('clip',) not in ctx_closed.operations

def test_retry_event_button():
    button = RetryEventButton()
    ctx = MockContext()
    button.draw(ctx, 0.0)

    assert ('show_text', "Retry") in ctx.operations

    # Test retrying state
    button.is_retrying.set(0.5)
    ctx_retrying = MockContext()
    button.draw(ctx_retrying, 0.0)

    assert ('show_text', "Retry") not in ctx_retrying.operations
    assert ('arc', 0, 0, 8, 0, math.pi * 1.5) in ctx_retrying.operations
    # Should have a rotate operation
    has_rotate = any(op[0] == 'rotate' for op in ctx_retrying.operations)
    assert has_rotate
