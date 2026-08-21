"""
Interactive Python Scripting, Code Editor & REPL Console Workspace for Vibmo Desktop.
Enables creators and AI agents to write, execute, and live-preview Vibmo Python scripts.
Synchronizes executed Scene objects directly into the Timeline, Player, Fusion DAG, and Color Grading.
"""

from __future__ import annotations
import io
import sys
import time
import traceback
from typing import Any, Optional
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPlainTextEdit,
    QTextEdit,
    QPushButton,
    QComboBox,
    QLabel,
    QSplitter,
    QFileDialog,
    QMessageBox,
)
from PySide6.QtGui import QFont, QColor, QShortcut, QKeySequence

from vibmo.graph.engine import VibmoStateGraph
from vibmo.graph.scene_sync import SceneGraphSyncEngine
from vibmo.scene.scene import Scene


CANONICAL_RECIPE_CODE = """# ✦ Vibmo Canonical Motion Script
from vibmo.agent_api import *

# 1. Initialize Scene (1080p @ 60 FPS, Dark Navy aesthetic)
scene = Scene(
    width=1920,
    height=1080,
    fps=60,
    duration=4.5,
    background=colors.DARK_NAVY,
)

# 2. Assemble Semantic Components with Auto-Layout
card = GlassCard(direction="column", gap=16, padding=32, corner_radius=24, position=(960, 540))
icon = Icon("lucide:sparkles", size=36, color=colors.INDIGO)
title = KineticText("Automated Motion in Python", font_size=32, bold=True)
counter = MetricCounter(start_val=0, end_val=250000, prefix="$", suffix=" MRR", font_size=52, bold=True, color=colors.EMERALD)

card.add(icon, title, counter)
scene.add(card)

# 3. Add Film Grain & Vignette for Cinematic Feel
scene.add_post_fx(Vignette(intensity=0.25), FilmGrain(amount=0.02))

# 4. Choreograph with Natural Verbs
@scene.animate
def main():
    yield card.pop_in(delay=0.1, duration=0.8)
    yield scene.all(
        title.reveal_characters(stagger=0.025),
        counter.count_to(duration=1.8, ease=Ease.out_expo),
        icon.bounce(amplitude=1.3, count=2),
    )
    card.float_idle(amplitude=6, speed=1.2)
    yield scene.wait(1.5)

print("✦ Scene choreographed successfully! Total Duration:", scene.duration, "seconds")
"""

KINETIC_CAPTIONS_CODE = """# ✦ Vibmo Word-by-Word Kinetic Captions Script
from vibmo.agent_api import *

scene = Scene(width=1080, height=1920, duration=3.5, background=colors.SLATE_950)

captions = KineticCaptions(
    words=[
        {"text": "Create", "start": 0.0, "end": 0.3},
        {"text": "Viral", "start": 0.3, "end": 0.6, "color": "#00E5FF"},
        {"text": "Motion", "start": 0.6, "end": 0.9},
        {"text": "Graphics", "start": 0.9, "end": 1.4, "color": "#FF5A5F"},
        {"text": "With", "start": 1.4, "end": 1.6},
        {"text": "Python", "start": 1.6, "end": 2.2, "color": "#10B981"},
    ],
    style_preset="tiktok_bounce",
    words_per_line=3,
    position=(540, 960),
)

scene.add(captions)
print("✦ Subtitles generated with TikTok bounce presets.")
"""

SHOWCASE_SEQUENCE_CODE = '''# ✦ Multi-Scene Motion Graphics Showcase (Production Master)
import math
from vibmo.agent_api import *

def create_saas_scene() -> Scene:
    scene = Scene(width=1920, height=1080, fps=60, duration=4.5, background=Color.hex("#030712"))
    scene.add_post_fx(Bloom(threshold=0.65, intensity=0.35, radius=24.0), Vignette(intensity=0.25), FilmGrain(amount=0.005))
    title = KineticText("<bold>PulseMetrics</bold> <gradient:#6366f1:#06b6d4>Cloud Intelligence</gradient>", font_size=38, color=colors.WHITE, align="center").align("top_center", (1920, 1080)).at(450, 60)
    scene.add(title)
    browser = BrowserWindow(url="https://app.pulsemetrics.io", title="PulseMetrics — Live Analytics", width=1360, height=760).align("center", (1920, 1080)).at(280, 180)
    metrics_row = GlassCard(direction="row", gap=32, padding=24, width=1280)
    kpi_card = GlassCard(direction="column", gap=8, padding=20, width=360)
    kpi_label = KineticText("<#94a3b8>MONTHLY ACTIVE REVENUE</#94a3b8>", font_size=12, bold=True)
    kpi_counter = MetricCounter(start_val=10000, end_val=148500, prefix="$", font_size=44, bold=True, color=colors.EMERALD)
    kpi_card.add(kpi_label, kpi_counter)
    chart = AreaChart(data=[25, 40, 35, 65, 52, 88, 80, 120, 110, 160], width=780, height=200, color=colors.EMERALD)
    metrics_row.add(kpi_card, chart)
    browser.add_content(metrics_row)
    scene.add(browser)
    cursor = Cursor(position=(1750, 920))
    scene.add(cursor)

    @scene.animate
    def saas_anim():
        yield scene.all(title.reveal_characters(stagger=0.018, duration=0.7), browser.pop_in(delay=0.1, duration=0.8))
        yield scene.all(browser.tilt_3d(pitch=0.16, yaw=-0.18, duration=1.1), chart.trace(duration=1.3), kpi_counter.count_to(duration=1.4, ease=Ease.out_expo))
        yield cursor.move_to(kpi_card, duration=0.6)
        yield scene.all(cursor.click(), kpi_card.bounce(amplitude=1.08, count=1))
        browser.float_idle(amplitude=5, speed=1.2)
        yield scene.wait(1.0)
    return scene

def create_code_scene() -> Scene:
    scene = Scene(width=1920, height=1080, fps=60, duration=4.5, background=Color.hex("#090d16"))
    scene.add_post_fx(Bloom(threshold=0.6, intensity=0.45, radius=28.0), Vignette(intensity=0.3))
    heading = KineticText("<gradient:#38bdf8:#818cf8>Autonomous Agent Pipeline</gradient>", font_size=40, bold=True, align="center").align("top_center", (1920, 1080)).at(470, 70)
    scene.add(heading)
    code_win = CodeWindow(code="@agent.task(runtime='edge')\\nasync def synthesize_motion(prompt: str) -> Video:\\n    return await scene.render_async()", title="agent_executor.py", font_size=22, width=960, position=(480, 240))
    scene.add(code_win)
    toast = NotificationToast(title="Edge Deployment Live", description="Cluster ready in 14ms across 35 regions", icon_name="lucide:zap", icon_color=colors.AMBER, position=(1340, 100))
    scene.add(toast)

    @scene.animate
    def code_anim():
        yield scene.all(heading.reveal_words(stagger=0.08, duration=0.8), code_win.fade_up(offset=50, duration=0.8))
        yield scene.all(toast.pop_in(delay=0.2, duration=0.7), code_win.code_node.reveal_characters(stagger=0.01, duration=1.2))
        code_win.float_idle(amplitude=6.0, speed=1.0)
        yield scene.wait(1.5)
    return scene

def create_math_morph_scene() -> Scene:
    scene = Scene(width=1920, height=1080, fps=60, duration=4.5, background=Color.hex("#070a14"))
    scene.add_post_fx(Bloom(threshold=0.55, intensity=0.4, radius=22.0), Vignette(intensity=0.2))
    header = GlassCard(direction="column", gap=8, padding=24, corner_radius=20, position=(620, 60))
    header.add(KineticText("Vector Morphing & Harmonic Curves", font_size=30, bold=True))
    scene.add(header)
    morph = MorphPath(shape=Shape.circle(radius=90), fill=Color.hex("#06b6d4").with_alpha(0.25), stroke=Color.hex("#22d3ee"), stroke_width=3, position=(480, 560))
    scene.add(morph)
    formula = MathFormula(latex=r"\\mathcal{F}(\\omega) = \\int_{-\\infty}^{\\infty} f(t) e^{-i\\omega t} dt", font_size=36, color=colors.AMBER, position=(1020, 260))
    scene.add(formula)
    axes = Axes(x_range=(-3, 3), y_range=(-1.5, 1.5), width=650, height=340, grid=True, position=(980, 480))
    curve = axes.plot(lambda x: math.sin(2.5 * x) * math.exp(-0.35 * abs(x)), color=colors.CYAN)
    scene.add(axes)

    @scene.animate
    def math_anim():
        yield scene.all(header.pop_in(duration=0.7), morph.pop_in(duration=0.7), formula.pop_in(duration=0.8), axes.fade_in(duration=0.8))
        yield scene.all(morph.morph_to(Shape.star(outer_radius=110, inner_radius=50), duration=1.0, ease=Ease.in_out_back), curve.trim_end.to(1.0, duration=1.2, ease=Ease.out_cubic))
        yield morph.morph_to(Shape.gear(radius=95, teeth=8), duration=1.1, ease=Ease.in_out_cubic)
        yield scene.wait(0.8)
    return scene

def create_outro_scene() -> Scene:
    scene = Scene(width=1920, height=1080, fps=60, duration=4.0, background=Color.hex("#050811"))
    scene.add_post_fx(Bloom(threshold=0.6, intensity=0.5, radius=30.0), Vignette(intensity=0.35))
    card = GlassCard(direction="column", gap=20, padding=40, corner_radius=28, position=(520, 320))
    icon = Icon("lucide:sparkles", size=54, color=colors.INDIGO)
    title = KineticText("<gradient:#6366f1:#a855f7:#ec4899>The Future of Motion Graphics</gradient>", font_size=44, bold=True)
    subtitle = KineticText("<#94a3b8>Built for AI Agents, Developers, and Creators</#94a3b8>", font_size=22)
    badge = Badge(text="OPEN SOURCE • 60 FPS", color=colors.CYAN)
    card.add(icon, title, subtitle, badge)
    scene.add(card)

    @scene.animate
    def outro_anim():
        yield card.pop_in(duration=0.8)
        yield scene.all(title.reveal_characters(stagger=0.015, duration=0.8), subtitle.fade_in(duration=0.6), icon.bounce(amplitude=1.35, count=2))
        card.float_idle(amplitude=6, speed=1.0)
        yield scene.wait(1.5)
    return scene

# Build 4-Scene Broadcast Sequence
seq = Sequence(
    create_saas_scene(),
    create_code_scene(),
    create_math_morph_scene(),
    create_outro_scene(),
    transition=Slide(direction="left", duration=0.6, ease=Ease.in_out_cubic),
)
print(f"✦ Multi-Scene Sequence built! 4 Scenes, Total Duration: {seq.duration:.2f}s")
'''


class ScriptingWorkspace(QWidget):
    """Python Code Editor & Live REPL Execution Console with Scene Synchronization."""

    def __init__(self, state_graph: VibmoStateGraph, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.state_graph = state_graph

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        # 1. Top Action Toolbar
        tb = QHBoxLayout()
        tb.setSpacing(8)

        lbl = QLabel("🐍 Python Scripting & REPL")
        lbl.setStyleSheet("font-weight: 800; font-size: 13px; color: #00E5FF;")
        tb.addWidget(lbl)

        # Template Selector
        tb.addWidget(QLabel("Templates:"))
        self.template_combo = QComboBox()
        self.template_combo.addItems([
            "Canonical Motion Recipe",
            "Multi-Scene Showcase Sequence",
            "Kinetic Subtitles & Captions",
            "Fusion VFX Pipeline",
            "Blank Script",
        ])
        self.template_combo.currentIndexChanged.connect(self._on_template_selected)
        tb.addWidget(self.template_combo)

        tb.addStretch()

        # Action Buttons
        open_btn = QPushButton("📂 Open .py")
        open_btn.clicked.connect(self._open_script)
        save_btn = QPushButton("💾 Save .py")
        save_btn.clicked.connect(self._save_script)
        clear_btn = QPushButton("🧹 Clear Console")
        clear_btn.clicked.connect(self._clear_console)

        run_btn = QPushButton("▶ Run Script (Ctrl+Enter)")
        run_btn.setObjectName("PrimaryAction")
        run_btn.setFixedHeight(28)
        run_btn.clicked.connect(self.run_script)

        tb.addWidget(open_btn)
        tb.addWidget(save_btn)
        tb.addWidget(clear_btn)
        tb.addWidget(run_btn)

        layout.addLayout(tb)

        # 2. Main Vertical Splitter: Top Code Editor / Bottom Console
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Code Editor
        editor_box = QWidget()
        eb_layout = QVBoxLayout(editor_box)
        eb_layout.setContentsMargins(0, 0, 0, 0)
        eb_layout.setSpacing(2)

        ed_hdr = QLabel("Vibmo Code Editor (from vibmo.agent_api import *)")
        ed_hdr.setStyleSheet("color: #71717A; font-weight: bold; font-size: 11px;")
        eb_layout.addWidget(ed_hdr)

        self.editor = QPlainTextEdit()
        self.editor.setFont(QFont("Cascadia Code", 11) if "Cascadia Code" in QFont().families() else QFont("Consolas", 11))
        self.editor.setStyleSheet("""
            QPlainTextEdit {
                background-color: #0E0E12;
                color: #ECECED;
                border: 1px solid #282830;
                border-radius: 6px;
                padding: 8px;
                line-height: 1.4;
            }
            QPlainTextEdit:focus {
                border: 1px solid #00E5FF;
            }
        """)
        self.editor.setPlainText(CANONICAL_RECIPE_CODE)
        eb_layout.addWidget(self.editor)
        splitter.addWidget(editor_box)

        # Console Output
        console_box = QWidget()
        cb_layout = QVBoxLayout(console_box)
        cb_layout.setContentsMargins(0, 0, 0, 0)
        cb_layout.setSpacing(2)

        con_hdr = QLabel("Terminal Execution Output & REPL")
        con_hdr.setStyleSheet("color: #71717A; font-weight: bold; font-size: 11px;")
        cb_layout.addWidget(con_hdr)

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setFont(QFont("Consolas", 10))
        self.console.setStyleSheet("""
            QTextEdit {
                background-color: #09090C;
                color: #34D399;
                border: 1px solid #22222A;
                border-radius: 6px;
                padding: 6px;
            }
        """)
        self.console.append("✦ Vibmo REPL Interactive Python Console Initialized.")
        self.console.append("✦ Ready. Press '▶ Run Script' (or Ctrl+Enter) to evaluate code.\n")
        cb_layout.addWidget(self.console)
        splitter.addWidget(console_box)

        splitter.setSizes([520, 280])
        layout.addWidget(splitter, 1)

        # Keyboard Shortcut: Ctrl+Enter to Run
        QShortcut(QKeySequence("Ctrl+Return"), self, self.run_script)
        QShortcut(QKeySequence("Ctrl+Enter"), self, self.run_script)

    def run_script(self) -> None:
        code = self.editor.toPlainText()
        self.console.append("<span style='color: #00E5FF;'><b>▶ Executing Vibmo Script...</b></span>")

        # Capture stdout and stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        redirected_output = io.StringIO()
        redirected_error = io.StringIO()
        sys.stdout = redirected_output
        sys.stderr = redirected_error

        # Import all symbols from agent_api into execution scope
        from vibmo import agent_api
        scope = {k: getattr(agent_api, k) for k in dir(agent_api) if not k.startswith("_")}
        scope["__name__"] = "__main__"
        scope["state_graph"] = self.state_graph

        t_start = time.perf_counter()
        try:
            exec(code, scope)
            exec_time = (time.perf_counter() - t_start) * 1000.0

            out = redirected_output.getvalue()
            err = redirected_error.getvalue()
            if out:
                self.console.append(f"<span style='color: #E2E8F0;'>{out.replace(chr(10), '<br>')}</span>")
            if err:
                self.console.append(f"<span style='color: #F59E0B;'>{err.replace(chr(10), '<br>')}</span>")

            # 2. Extract active Sequence or Scene from scope
            from vibmo.scene.scene import Scene
            from vibmo.composition.sequence import Sequence

            found_target: Optional[Any] = None
            # Check for Sequence first
            for v in scope.values():
                if isinstance(v, Sequence):
                    found_target = v
                    break
            # Fallback to Scene
            if not found_target:
                for v in scope.values():
                    if isinstance(v, Scene):
                        found_target = v
                        break

            if found_target:
                SceneGraphSyncEngine.sync_to_state_graph(found_target, self.state_graph)
                target_type = "Multi-Scene Sequence" if isinstance(found_target, Sequence) else "Scene"
                self.console.append(
                    f"<span style='color: #00E5FF;'><b>✦ Synchronized {target_type} to Workstation:</b> "
                    f"{len(self.state_graph.project.timeline.tracks)} Tracks • "
                    f"{len(self.state_graph.project.timeline.clips)} Clips • "
                    f"{found_target.duration:.2f}s @ {int(found_target.fps)} FPS • "
                    f"({exec_time:.1f}ms)</span>"
                )

            self.console.append("<span style='color: #34D399;'><b>✔ Execution & State Graph Sync Completed.</b></span>\n")

        except Exception as e:
            tb = traceback.format_exc()
            self.console.append(f"<span style='color: #EF4444;'><b>✖ Execution Error:</b><br>{tb.replace(chr(10), '<br>')}</span>\n")
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

    def _on_template_selected(self, idx: int) -> None:
        if idx == 0:
            self.editor.setPlainText(CANONICAL_RECIPE_CODE)
        elif idx == 1:
            self.editor.setPlainText(SHOWCASE_SEQUENCE_CODE)
        elif idx == 2:
            self.editor.setPlainText(KINETIC_CAPTIONS_CODE)
        elif idx == 3:
            self.editor.setPlainText("""# ✦ Procedural Fusion Node Graph Script
from vibmo.agent_api import *

fg = state_graph.create_fusion_graph("Procedural VFX")
bg = state_graph.add_fusion_node(fg.id, "Background", "generator")
noise = state_graph.add_fusion_node(fg.id, "FastNoise", "generator")
glow = state_graph.add_fusion_node(fg.id, "Glow", "filter")

state_graph.connect_fusion_nodes(fg.id, bg.id, noise.id)
state_graph.connect_fusion_nodes(fg.id, noise.id, glow.id)
print("✦ Created Fusion Graph with ID:", fg.id)
""")
        else:
            self.editor.setPlainText("from vibmo.agent_api import *\n\n")

    def _open_script(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Open Python Script", "", "Python Files (*.py);;All Files (*)")
        if path:
            with open(path, "r", encoding="utf-8") as f:
                self.editor.setPlainText(f.read())

    def _save_script(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Save Python Script", "motion_script.py", "Python Files (*.py);;All Files (*)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.editor.toPlainText())
            QMessageBox.information(self, "Script Saved", f"Script saved successfully to:\n{path}")

    def _clear_console(self) -> None:
        self.console.clear()
