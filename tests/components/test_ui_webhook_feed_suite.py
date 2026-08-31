import pytest
import cairo
from vibmo.product.ai.ui_webhook_feed_suite import (
    WebhookEventStreamCard,
    HttpStatusBadge,
    PayloadJsonInspector,
    RetryEventButton,
    WebhookActivityFeed,
    HttpRequestInspector,
)

def test_webhook_event_stream_card():
    card = WebhookEventStreamCard(event="payment.succeeded", status_code=200)
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 600, 100)
    ctx = cairo.Context(surface)
    card.draw(ctx, time=0.0)
    assert card.event == "payment.succeeded"

def test_http_status_badge_200():
    badge = HttpStatusBadge(status_code=200)
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 100, 40)
    ctx = cairo.Context(surface)
    badge.draw(ctx, time=0.0)
    assert badge.status_code == 200

def test_http_status_badge_404():
    badge = HttpStatusBadge(status_code=404)
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 100, 40)
    ctx = cairo.Context(surface)
    badge.draw(ctx, time=0.0)
    assert badge.status_code == 404

def test_http_status_badge_500():
    badge = HttpStatusBadge(status_code=500)
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 100, 40)
    ctx = cairo.Context(surface)
    badge.draw(ctx, time=0.0)
    assert badge.status_code == 500

def test_payload_json_inspector():
    insp = PayloadJsonInspector(payload='{\n  "id": "evt_123",\n  "amount": 9900\n}')
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 500, 200)
    ctx = cairo.Context(surface)
    insp.draw(ctx, time=0.0)
    assert insp is not None

def test_retry_event_button():
    btn = RetryEventButton(label="Re-deliver Event")
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 180, 50)
    ctx = cairo.Context(surface)
    btn.draw(ctx, time=0.0)
    assert btn.label == "Re-deliver Event"
