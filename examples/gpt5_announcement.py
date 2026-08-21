"""
Pixel-Perfect OpenAI/Apple GPT-5 Model Selector UI Reel (YouTube Short / 9:16).
Features smooth sunset pastel gradient, elevated Apple-style white pill card,
kinetic typography, and smooth micro-interactions.
"""

from vibmo.agent_api import *

# 1. Initialize Vertical 9:16 Scene (1080x1920 @ 60 FPS)
scene = Scene(
    width=1080,
    height=1920,
    fps=60,
    duration=4.5,
)

# 2. Pixel-Exact Warm Sunset Pastel Vertical Gradient
bg_gradient = LinearGradient(
    start=(540, 0),
    end=(540, 1920),
    stops=[
        (0.00, Color.hex("#ECA282")),  # Warm Peach
        (0.25, Color.hex("#DC7A85")),  # Coral Rose
        (0.55, Color.hex("#C779A1")),  # Dusty Pink
        (0.80, Color.hex("#9476B6")),  # Soft Lavender
        (1.00, Color.hex("#7471BA")),  # Periwinkle Indigo
    ],
)

bg_rect = Rect(
    width=1080,
    height=1920,
    fill=bg_gradient,
)
scene.add(bg_rect)

# 3. Apple-Style Elevated White Model Selector Card
card = GlassCard(
    direction="row",
    gap=0,
    padding=(36, 40),
    corner_radius=40,
    width=740,
    position=(170, 860),
    fill=Color.WHITE,
    stroke=Color.WHITE.with_alpha(0.85),
    stroke_width=1.0,
    justify_content="space_between",
    align_items="center",
    shadow=DropShadow(
        color=Color.hex("#381822").with_alpha(0.14),
        blur=42.0,
        offset=(0, 18),
        spread=0.0,
    ),
)

# 3a. Left Text Stack: Title & Subtitle
text_column = FlexContainer(
    direction="column",
    gap=6,
    padding=0,
    align_items="start",
)

title = KineticText(
    "GPT-5",
    font_size=38,
    bold=True,
    color=Color.hex("#09090b"),
)

subtitle = KineticText(
    "Flagship model",
    font_size=24,
    color=Color.hex("#94a3b8"),
)

text_column.add(title, subtitle)

# 3b. Right Checkmark Indicator Badge
check_badge = FlexContainer(
    direction="row",
    align_items="center",
    justify_content="center",
    width=48,
    height=48,
    corner_radius=24,
    fill=Color.hex("#09090b"),
)
check_icon = Icon("lucide:check", size=24, color=Color.WHITE)
check_badge.add(check_icon)

card.add(text_column, check_badge)
scene.add(card)

# 4. Cinematic Micro-Grain Texture
scene.add_post_fx(
    FilmGrain(amount=0.003),
)


# 5. Smooth Apple-Style Kinetic Choreography
@scene.animate
def main():
    # 0.0s - 0.9s: Card pops up from scale 0.88 with spring deceleration
    yield card.pop_in(duration=0.9, scale_from=0.88, ease=Ease.spring(stiffness=140, damping=14))

    # 0.9s - 1.8s: Subtitle glyph wave reveal + Checkmark pulse
    yield scene.all(
        subtitle.reveal_characters(stagger=0.025),
        check_badge.bounce(amplitude=1.2, count=1, duration=0.6),
    )

    # 1.8s - 2.8s: Subtle model selection tap bounce
    yield scene.wait(0.4)
    yield scene.all(
        card.bounce(amplitude=1.03, count=1, duration=0.5),
        check_badge.bounce(amplitude=1.12, count=1, duration=0.4),
    )

    # 2.8s - 4.5s: Floating organic idle drift
    card.float_idle(amplitude=5.0, speed=1.0)
    yield scene.wait(1.7)


if __name__ == "__main__":
    scene.storyboard("gpt5_storyboard.png")
    scene.render("gpt5_announcement.mp4", quality="high")
