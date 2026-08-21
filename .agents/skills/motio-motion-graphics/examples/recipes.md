# ✦ End-to-End Showcase Recipes for Motio / Vibmo

This document provides production-ready, copy-pasteable recipes for common motion graphics use cases.

---

## 🚀 Recipe 1: SaaS Flagship Product Demo Video

```python
from motio.agent_api import *

# 1. Initialize Scene (1080p 60FPS)
scene = Scene(
    width=1920,
    height=1080,
    fps=60,
    duration=6.5,
    background=Color.hex("#030712"),
)

# 2. Cinematic Post-Processing
scene.add_post_fx(Vignette(intensity=0.25), FilmGrain(amount=0.008))

# 3. Assemble UI Mockup
browser = BrowserWindow(
    url="https://app.pulsemetrics.io",
    title="PulseMetrics — Revenue Intelligence",
    width=1400,
    height=840,
    position=(260, 120),
)

# UI Card with Metrics and Chart
card = GlassCard(direction="column", gap=12, padding=24, width=420)
icon = Icon("lucide:sparkles", size=32, color=colors.CYAN)
title = KineticText("ANNUAL RUN RATE", font_size=14, bold=True, color=colors.SLATE_400)
counter = MetricCounter(start_val=250000, end_val=1450000, prefix="$", font_size=44, bold=True, color=colors.EMERALD)
chart = Sparkline(data=[10, 25, 40, 35, 70, 95, 145], width=360, height=80, color=colors.CYAN)

card.add(icon, title, counter, chart)
browser.add_content(card)
scene.add(browser)

# Cursor & Spotlight
cursor = Cursor(position=(1700, 900))
click_fx = ClickIndicator()
spotlight = Spotlight(target=card, radius=340)
scene.add(cursor, click_fx, spotlight)

# 4. Choreograph Animation
@scene.animate
def main():
    yield browser.pop_in(duration=0.9)
    yield cursor.move_to(card, duration=0.7)
    yield scene.all(
        cursor.click(),
        click_fx.trigger(),
        card.bounce(amplitude=1.15, count=1),
    )
    yield scene.all(
        *browser.tilt_3d(pitch=0.18, yaw=-0.22, duration=1.2),
        counter.count_to(duration=1.8, ease=Ease.out_expo),
    )
    browser.float_idle(amplitude=6, speed=1.0)
    yield scene.wait(1.5)

if __name__ == "__main__":
    scene.storyboard("saas_demo_storyboard.png")
    scene.render("saas_demo.mp4", quality="high")
```

---

## 📱 Recipe 2: Mobile App Feature Showcase

```python
from motio.agent_api import *

scene = Scene(width=1920, height=1080, fps=60, duration=5.0, background=colors.DARK_NAVY)

# Phone frame with mobile card
phone = PhoneFrame(model="iphone15_pro", width=380, height=780, position=(770, 150))
toast = NotificationToast(
    title="Instant Transfer",
    description="$2,500 received from Stripe",
    icon_name="lucide:check",
    icon_color=colors.EMERALD,
)
phone.add_content(toast)
scene.add(phone)

@scene.animate
def main():
    yield phone.pop_in(duration=0.8)
    yield toast.fade_up(offset=30, duration=0.6)
    yield toast.bounce(amplitude=1.2, count=1)
    yield phone.tilt_3d(pitch=0.15, yaw=0.2, duration=1.0)
    yield scene.wait(1.5)

if __name__ == "__main__":
    scene.render("mobile_showcase.mp4")
```

---

## 🔄 Recipe 3: Vector Shape Metamorphosis

```python
from motio.agent_api import *

scene = Scene(width=1920, height=1080, fps=60, duration=5.5, background=Color.hex("#090d16"))
scene.add_post_fx(Vignette(intensity=0.3), FilmGrain(amount=0.01))

morph = MorphPath(
    shape=Shape.circle(radius=90),
    fill=colors.CYAN.with_alpha(0.25),
    stroke=colors.CYAN,
    stroke_width=4,
    position=(960, 540)
)
scene.add(morph)

@scene.animate
def morph_sequence():
    yield scene.wait(0.3)
    yield morph.morph_to(Shape.star(outer_radius=110, inner_radius=48), duration=1.0, ease=Ease.in_out_back)
    yield morph.morph_to(Shape.heart(size=120), duration=0.9, ease=Ease.in_out_cubic)
    yield morph.morph_to(Shape.gear(radius=95, teeth=8), duration=1.1, ease=Ease.in_out_expo)
    yield morph.morph_to(Shape.circle(radius=90), duration=0.8)
    yield scene.wait(0.8)

if __name__ == "__main__":
    scene.render("morph.mp4")
```

---

## 🎵 Recipe 4: Audio Reactive Visualizer

```python
from motio.agent_api import *

scene = Scene(width=1920, height=1080, fps=60, duration=8.0, background=Color.hex("#05050a"))
audio_file = "assets/track.mp3"
scene.set_audio(audio_file, volume=0.9)

spectrum = SpectrumBars(
    audio_path=audio_file,
    bars=48,
    width=900,
    height=240,
    color=colors.CYAN,
    position=(510, 420)
)
scene.add(spectrum)

if __name__ == "__main__":
    scene.render("audio_visualizer.mp4")
```

---

## 🎬 Recipe 5: Multi-Scene Composition with Stem Mixing

```python
from motio.agent_api import *

# Create individual scenes
intro = Scene(width=1920, height=1080, duration=3.0, background=colors.DARK_NAVY)
card1 = GlassCard(position=(700, 400)).add(KineticText("Scene 1: Intro"))
intro.add(card1)
@intro.animate
def anim1():
    yield card1.pop_in()

outro = Scene(width=1920, height=1080, duration=3.0, background=colors.SLATE_900)
card2 = GlassCard(position=(700, 400)).add(KineticText("Scene 2: Outro"))
outro.add(card2)
@outro.animate
def anim2():
    yield card2.pop_in()

# Sequence with slide transition
film = Sequence(intro, outro, transition=Slide(direction="left", duration=0.6))
film.add_audio_track("assets/soundtrack.mp3", volume=0.5)

if __name__ == "__main__":
    film.render("multi_scene.mp4")
```

---
*End of Showcase Recipes.*
