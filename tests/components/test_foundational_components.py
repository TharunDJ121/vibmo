import pytest
import cairo
import numpy as np

from vibmo.components.glass import GlassCard
from vibmo.components.counter import MetricCounter
from vibmo.components.code import CodeWindow
from vibmo.components.toast import NotificationToast
from vibmo.components.code_stream import SyntaxHighlightCode
from vibmo.product.mockups import BrowserWindow
from vibmo.product.cursor import Cursor, ClickIndicator
from vibmo.product.callouts import Spotlight, Callout, Tooltip
from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D
from vibmo.scene.scene import Scene
from vibmo.scene.node import Node
from vibmo.typography.text import Text


def test_glass_card_modernization():
    card = GlassCard(
        direction="column",
        gap=16.0,
        padding=32.0,
        corner_radius=24.0,
        specular_rim=True,
        position=(100.0, 150.0),
    )
    t1 = Text("Title", font_size=24.0)
    t2 = Text("Subtitle", font_size=16.0)
    card.add(t1, t2)

    action = card.gleam(duration=1.2)
    assert action is not None

    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, 800, 600)
    ctx = cairo.Context(surf)
    card.draw(ctx, 0.0)
    card.draw(ctx, 0.6)
    card.draw(ctx, 1.2)

    bx, by, bw, bh = card.local_bounds(0.0)
    assert bw > 0
    assert bh > 0


def test_metric_counter_signals_and_easing():
    counter = MetricCounter(
        start_val=0,
        end_val=250000,
        prefix="$",
        suffix=" MRR",
        decimals=0,
        font_size=48.0,
        bold=True,
        color=colors.EMERALD,
    )
    assert counter.start_val == 0
    assert counter.end_val == 250000

    action = counter.count_to(duration=1.8)
    assert action is not None

    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, 600, 200)
    ctx = cairo.Context(surf)
    
    counter.draw(ctx, 0.0)
    assert "$" in counter.text.get()
    
    # Mid-flight
    action.apply_at(0.0)
    counter.draw(ctx, 1.0)
    val_mid = counter.numeric_val.get(1.0)
    assert val_mid > 0

    counter.draw(ctx, 2.0)
    assert "250,000" in counter.text.get()


def test_browser_window_mockup():
    win = BrowserWindow(
        url="https://vibmo.design",
        title="Vibmo Demo",
        width=1280,
        height=720,
        dark_mode=True,
        corner_radius=16.0,
    )
    assert win.width_val == 1280
    assert win.height_val == 720

    content_node = Text("Inside Browser Viewport", font_size=20.0)
    win.add_content(content_node)
    assert content_node in win.content.children

    action = win.gleam(duration=1.0)
    assert action is not None

    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1300, 800)
    ctx = cairo.Context(surf)
    win.draw(ctx, 0.0)
    win.draw(ctx, 0.5)


def test_cursor_and_pointer_navigation():
    cursor = Cursor(position=(500, 400), style="arrow", size=24.0)
    target_node = Node(position=(800, 600))
    
    glide_action = cursor.glide_to(target_node, duration=0.8)
    assert glide_action is not None

    click_actions = cursor.click(duration=0.35)
    assert isinstance(click_actions, list)
    assert len(click_actions) == 2

    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1000, 1000)
    ctx = cairo.Context(surf)
    cursor.draw(ctx, 0.0)

    # Pointer hand style
    hand_cursor = Cursor(style="pointer")
    hand_cursor.draw(ctx, 0.0)


def test_spotlight_focus_highlight():
    target = Node(position=(960, 540))
    spotlight = Spotlight(target=target, radius=200.0, scene_width=1920, scene_height=1080)
    
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1920, 1080)
    ctx = cairo.Context(surf)
    spotlight.draw(ctx, 0.0)

    lb = spotlight.local_bounds(0.0)
    assert lb == (0.0, 0.0, 1920.0, 1080.0)


def test_components_module_exports():
    from vibmo.components import (
        GlassCard,
        MetricCounter,
        CodeWindow,
        NotificationToast,
        SyntaxHighlightCode,
        BrowserWindow,
        Cursor,
        ClickIndicator,
        Spotlight,
        Callout,
        Tooltip,
    )
    assert GlassCard is not None
    assert MetricCounter is not None
    assert BrowserWindow is not None
    assert Cursor is not None
    assert Spotlight is not None
