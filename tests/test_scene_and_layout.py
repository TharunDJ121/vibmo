"""
Integration tests for Scene Graph, Flexbox Layout, Kinetic Typography, Snapshots, and Storyboards.
"""

import os
from vibmo import Scene, FlexContainer, GlassCard, KineticText, Text, MetricCounter, Rect, Circle, Icon, Ease, colors


def test_flex_layout_computation():
    card = FlexContainer(direction="row", gap=10, padding=20)
    b1 = Rect(width=50, height=50)
    b2 = Rect(width=50, height=50)
    card.add(b1, b2)

    w, h = card.compute_layout(0.0)
    # Total width = padding_left(20) + 50 + gap(10) + 50 + padding_right(20) = 150
    # Total height = padding_top(20) + 50 + padding_bottom(20) = 90
    assert w == 150
    assert h == 90
    assert b2.position.get().x == 20 + 50 + 10


def test_scene_snapshot_and_storyboard(tmp_path):
    scene = Scene(width=800, height=450, fps=30, duration=2.0, background=colors.DARK_NAVY)
    
    card = GlassCard(direction="column", gap=12, padding=24, position=(200, 100))
    title = KineticText("Vibe Coding Engine", font_size=28, bold=True)
    icon = Icon("lucide:zap", size=32, color=colors.AMBER)
    counter = MetricCounter(start_val=0, end_val=1000, prefix="$")
    
    card.add(icon, title, counter)
    scene.add(card)

    @scene.animate
    def script():
        yield card.pop_in(delay=0.1)
        yield title.reveal_characters(stagger=0.02)
        yield counter.count_to(duration=1.0)

    snap_path = str(tmp_path / "snapshot.png")
    sb_path = str(tmp_path / "storyboard.png")

    img_snap = scene.snapshot(time=1.0, path=snap_path)
    assert os.path.exists(snap_path)
    assert img_snap.size == (800, 450)

    img_sb = scene.storyboard(path=sb_path, rows=2, cols=2)
    assert os.path.exists(sb_path)
    assert img_sb.width > 0 and img_sb.height > 0
