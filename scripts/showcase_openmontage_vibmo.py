"""
Showcase Scene Demonstrating OpenMontage Capabilities in Vibmo / Motio.

Features:
  - TerminalWindow with live typing simulation and status pills.
  - CodeCard with syntax highlighting.
  - MocapStickFigure playing procedural vector motion capture.
  - DiagramNode vector architecture flow.
  - Pre-flight quality inspection (SlideshowRiskScorer & PreflightValidator).
"""

from motio.agent_api import *

# 1. Initialize 1080p Scene
scene = Scene(
    width=1920,
    height=1080,
    fps=60,
    duration=4.0,
    background=colors.DARK_NAVY,
)

# 2. Add Background Mesh Flow & Cinematic Shaders
bg = MeshGradientFlow(colors=[colors.INDIGO, colors.CYAN], speed=0.5)
scene.add(bg)
scene.add_post_fx(Vignette(intensity=0.25), FilmGrain(amount=0.015))

# 3. Assemble Components
# Header Glass Card
header_card = GlassCard(direction="row", gap=16, padding=20, corner_radius=18, position=(960, 90))
icon = Icon("lucide:terminal", size=32, color=colors.CYAN)
title = KineticText("Vibmo + OpenMontage Intelligence Suite", font_size=28, bold=True)
header_card.add(icon, title)
scene.add(header_card)

# Terminal Window (Left)
term = TerminalWindow(
    title="dev@vibmo: ~",
    prompt="vibmo> ",
    width=680,
    height=400,
    position=(500, 400),
    font_size=15,
)
term.add_command("vibmo init saas_launch --preset=clean", type_speed=0.03, hold_seconds=0.4)
term.add_output("✓ Compiled 6 scenes with 60 FPS GPU acceleration", hold_seconds=0.3)
term.add_command("vibmo quality --slideshow-check", type_speed=0.03, hold_seconds=0.3)
term.add_output("✓ Slideshow Risk Score: 1.20 (STRONG / CINEMATIC)", hold_seconds=0.2)
term.add_pill("Build Succeeded", color=colors.EMERALD, duration=2.5)
scene.add(term)

# Code Card (Right)
code_str = """from motio.agent_api import *

# 2D Mocap Stick Figure & IK
figure = MocapStickFigure(action="dance")
figure.reach_left((100, -50))
scene.add(figure)

# Quality Pre-flight Gate
report = SlideshowRiskScorer.evaluate_scene(scene)"""

code_card = CodeCard(
    code=code_str,
    language="python",
    filename="pipeline.py",
    theme="dracula",
    width=680,
    height=400,
    position=(1400, 400),
    font_size=15,
)
scene.add(code_card)

# Diagram Flowchart (Bottom Left)
diag = DiagramNode(position=(640, 840))
diag.add_box("1", "OpenMontage Tools", subtext="Analysis & Mocap", x=-320, y=0, width=220, color=colors.CYAN)
diag.add_box("2", "Vibmo Engine", subtext="PyCairo + ModernGL", x=0, y=0, width=220, color=colors.EMERALD)
diag.add_box("3", "Master 60FPS Video", subtext="ProRes & H.264", x=320, y=0, width=220, color=colors.PURPLE)
diag.connect("1", "2", label="Bridge", color=colors.CYAN)
diag.connect("2", "3", label="Render", color=colors.EMERALD)
scene.add(diag)

# 2D Vector Mocap Character (Bottom Right)
char = MocapStickFigure(
    height=240,
    color=colors.WHITE,
    action="dance",
    action_speed=1.0,
    position=(1500, 840),
    boil=True,
)
scene.add(char)

# 4. Choreography
@scene.animate
def main():
    yield scene.all(
        header_card.pop_in(duration=0.6),
        term.pop_in(delay=0.1, duration=0.7),
        code_card.pop_in(delay=0.2, duration=0.7),
        diag.pop_in(delay=0.3, duration=0.7),
        char.pop_in(delay=0.4, duration=0.7),
    )
    yield scene.wait(2.5)

# 5. Pre-flight Quality Verification
report = SlideshowRiskScorer.evaluate_scene(scene)
print(f"Pre-flight Slideshow Risk Score: {report.average_score} ({report.verdict.upper()})")

preflight = PreflightValidator.validate_scene(scene)
print(f"Preflight Validation: Passed={preflight.passed}, Total Issues={preflight.total_issues}")

if __name__ == "__main__":
    scene.storyboard("openmontage_vibmo_storyboard.png")
    print("Storyboard generated: openmontage_vibmo_storyboard.png")
