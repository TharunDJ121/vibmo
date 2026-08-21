"""
Unit tests for SaaS product demo components and UI primitives.
"""

import pytest
from vibmo.product.mockups import BrowserWindow, PhoneFrame
from vibmo.product.cursor import Cursor, ClickIndicator
from vibmo.product.callouts import Spotlight, Callout, Tooltip
from vibmo.product.charts import AreaChart, Sparkline
from vibmo.product.command_palette import CommandPalette, CommandItem
from vibmo.components.glass import GlassCard
from vibmo.components.counter import MetricCounter
from vibmo.components.code import CodeWindow
from vibmo.components.toast import NotificationToast


def test_browser_and_phone_frames():
    browser = BrowserWindow(url="https://app.io", title="Analytics", width=1280, height=720)
    card = GlassCard(position=(50, 50))
    browser.add_content(card)
    assert len(browser.children) == 1

    gleam_action = browser.gleam(duration=1.0)
    assert gleam_action is not None

    phone = PhoneFrame(width=380, height=780)
    phone.add_screen_content(card)
    assert len(phone.children) == 1


def test_cursor_and_click():
    target = GlassCard(position=(300, 200), width=100, height=50)
    cursor = Cursor(position=(0, 0))

    # move_to auto-resolves target world bounds
    move_action = cursor.move_to(target, duration=0.6)
    assert move_action is not None

    click_action = cursor.click(duration=0.3)
    assert click_action is not None

    indicator = ClickIndicator(position=(300, 200))
    ind_action = indicator.trigger(duration=0.4)
    assert ind_action is not None


def test_spotlight_and_callout():
    card = GlassCard(position=(400, 300), width=200, height=150)
    spotlight = Spotlight(target=card, radius=200)
    assert spotlight.target == card

    callout = Callout(title="AI Surge", description="+48% boost", badge="LIVE")
    assert callout.title == "AI Surge"

    tooltip = Tooltip(text="Click to inspect")
    assert tooltip.text == "Click to inspect"


def test_area_chart_and_sparkline():
    data = [10, 25, 18, 45, 60, 80, 75, 110]
    chart = AreaChart(data=data, width=500, height=200)
    pts = chart._compute_points()
    assert len(pts) == len(data)

    trace_action = chart.trace(duration=1.5)
    assert trace_action is not None

    spark = Sparkline(data=[5, 12, 8, 20, 15, 30])
    assert spark.show_grid is False


def test_command_palette_modal():
    items = [
        CommandItem(title="Create Component", shortcut="⌘N", icon="✨"),
        CommandItem(title="Deploy to Edge", shortcut="⌘D", icon="⚡"),
    ]
    palette = CommandPalette(items=items, width=600)

    type_act = palette.type_search("Deploy", speed=15.0)
    assert type_act is not None

    sel_act = palette.select_item(1, duration=0.4)
    assert sel_act is not None

    enter_act = palette.hit_enter(duration=0.3)
    assert enter_act is not None


def test_bar_chart_and_grow_bars():
    from vibmo.product.charts import BarChart
    chart = BarChart(data=[("Mon", 50), ("Tue", 80), ("Wed", 65)], width=500, height=200)
    assert len(chart.values) == 3
    assert chart.max_val == 80.0

    grow_act = chart.grow_bars(duration=1.0, stagger=0.05)
    assert grow_act is not None
    grow_act.apply_at(0.0)
    assert chart.growth_signals[0].get(0.0) == 0.0


def test_pie_and_donut_charts():
    from vibmo.product.charts import PieChart, DonutChart
    pie = PieChart(data=[("A", 40), ("B", 60)], radius=100.0)
    assert pie.total == 100.0

    rev_act = pie.reveal(duration=1.2)
    assert rev_act is not None

    exp_act = pie.explode_slice(0, offset=12.0)
    assert exp_act is not None

    donut = DonutChart(data=[("Active", 70), ("Churn", 30)], center_text="70%")
    assert donut.donut_ratio == 0.65
    assert donut.center_text == "70%"


def test_gauge_chart_kpi():
    from vibmo.product.charts import GaugeChart
    gauge = GaugeChart(value=75.0, min_val=0.0, max_val=100.0, unit="%")
    assert gauge.current_value.get(0.0) == 75.0

    anim_act = gauge.animate_to(92.0, duration=1.0)
    assert anim_act is not None


def test_data_table_and_timeline():
    from vibmo.product.tables import DataTable, TimelineView
    table = DataTable(
        headers=["User", "Plan", "Revenue"],
        rows=[["Alex", "Pro", "$99"], ["Sarah", "Enterprise", "$499"]],
        width=600,
    )
    assert len(table.raw_rows) == 2
    rev_act = table.reveal_rows(duration=0.8)
    assert rev_act is not None

    tl = TimelineView(
        milestones=[("M1", "Core", True), ("M2", "Scale", False)],
        width=500,
    )
    prog_act = tl.animate_progress(duration=1.4)
    assert prog_act is not None


def test_avatar_and_avatar_group():
    from vibmo.product.social import Avatar, AvatarGroup
    av = Avatar(name="Alex Rivera", size=48.0, status="online")
    assert av.initials == "AR"
    assert av.status == "online"

    group = AvatarGroup(users=["Alex Rivera", "Sarah Chen", "Marcus Vance", "Elena Rostova"], max_visible=2)
    assert len(group.avatars) == 2
    assert group.overflow_count == 2
    pop_act = group.pop_in_all()
    assert pop_act is not None


def test_badge_and_chat_bubble():
    from vibmo.product.social import Badge, ChatBubble, TypingIndicator
    badge = Badge(text="BETA", pulse=True)
    assert badge.text == "BETA"
    assert badge.pulse is True

    bubble = ChatBubble(message="Automated motion graphics", sender="AI Agent", is_me=True)
    assert bubble.sender == "AI Agent"
    assert bubble.is_me is True

    typing = TypingIndicator()
    bx, by, bw, bh = typing.local_bounds(0.0)
    assert bw > 0 and bh > 0


def test_animated_form_controls():
    from vibmo.product.controls import ToggleSwitch, Checkbox, ProgressBar, RatingStars
    toggle = ToggleSwitch(checked=True)
    assert toggle.state_progress.get(0.0) == 1.0
    tog_act = toggle.toggle(on=False, duration=0.4)
    assert tog_act is not None

    chk = Checkbox(checked=False)
    assert chk.check_progress.get(0.0) == 0.0
    chk_act = chk.check(duration=0.4)
    assert chk_act is not None

    pb = ProgressBar(progress=0.5, width=300)
    assert pb.progress_signal.get(0.0) == 0.5
    pb_act = pb.progress_to(1.0, duration=1.0)
    assert pb_act is not None

    stars = RatingStars(rating=4.5)
    assert stars.rating == 4.5


def test_saas_stat_card():
    from vibmo.product.cards import StatCard
    card = StatCard(
        title="MRR",
        value=150000,
        prefix="$",
        trend="+32.4%",
        width=300,
    )
    assert card.width_val == 300
    assert card.counter.end_val == 150000
    count_act = card.count_up(duration=1.5)
    assert count_act is not None

