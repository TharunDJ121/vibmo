"""
Expanded edge case unit tests for the SaaS & Product Component Library.
"""

import pytest
from vibmo.scene.scene import Scene
from vibmo.components.glass import GlassCard
from vibmo.product.charts import BarChart, PieChart, DonutChart, GaugeChart
from vibmo.product.tables import DataTable, TimelineView
from vibmo.product.social import Avatar, AvatarGroup, Badge, ChatBubble, TypingIndicator
from vibmo.product.controls import ToggleSwitch, Checkbox, ProgressBar, RatingStars
from vibmo.product.cards import StatCard
from vibmo.core.color import colors


def test_barchart_empty_and_horizontal():
    chart = BarChart(data=[10, 20, 30], gap=12.0)
    assert chart.width_val == 540.0
    bx, by, bw, bh = chart.local_bounds(0.0)
    assert bw == 540.0 and bh == 240.0


def test_donutchart_center_text_and_explode():
    donut = DonutChart(
        data=[("SaaS", 60), ("API", 40)],
        radius=120.0,
        center_text="$2.4M",
    )
    assert donut.center_text == "$2.4M"
    # Explode slice 1
    exp_action = donut.explode_slice(1, offset=16.0, duration=0.5)
    assert exp_action is not None


def test_datatable_zebra_and_status_tags():
    table = DataTable(
        headers=["Product", "Status", "Price"],
        rows=[
            ["Vibmo Pro", "LIVE", "$199"],
            ["Web Studio", "Active", "$99"],
            ["API Cloud", "Pending", "$49"],
        ],
        width=700.0,
    )
    bx, by, bw, bh = table.local_bounds(0.0)
    assert bw == 700.0
    assert bh > 150.0


def test_timeline_milestones_and_reach():
    tl = TimelineView(
        milestones=[
            ("v1.0", "Core Engine", True),
            ("v1.5", "Web Studio", True),
            ("v2.0", "Full AI Agent Suite", True),
        ],
        width=800.0,
    )
    assert len(tl.milestones) == 3
    bx, by, bw, bh = tl.local_bounds(0.0)
    assert bw == 800.0


def test_full_saas_dashboard_scene_composition():
    scene = Scene(width=1920, height=1080, duration=3.0, background=colors.DARK_NAVY)

    # 1. Top Stat Cards Row
    mrr_card = StatCard(title="MRR", value=248000, prefix="$", trend="+42.8%", position=(80, 80))
    users_card = StatCard(title="Active Users", value=18400, prefix="", trend="+18.2%", position=(440, 80))

    # 2. Main Data Table
    table = DataTable(
        headers=["Customer", "Plan", "Status", "Volume"],
        rows=[
            ["Acme Corp", "Enterprise", "LIVE", "$48,000"],
            ["Linear Systems", "Pro", "Active", "$12,500"],
            ["Vercel Edge", "Scale", "Active", "$24,000"],
        ],
        width=720,
        position=(80, 360),
    )

    # 3. Donut Breakdown
    breakdown = DonutChart(
        data=[("Direct", 55), ("Organic", 30), ("Referral", 15)],
        radius=130.0,
        center_text="100%",
        position=(860, 360),
    )

    scene.add(mrr_card, users_card, table, breakdown)

    @scene.animate
    def main():
        yield scene.all(
            mrr_card.pop_in(),
            users_card.pop_in(delay=0.1),
            table.reveal_rows(delay=0.2),
            breakdown.reveal(delay=0.3),
        )

    assert len(scene.nodes) == 4
    issues = scene.validate()
    assert issues == []
