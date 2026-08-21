---
name: motio-motion-graphics
description: >-
  Expert guide for generating aesthetic motion graphics, SaaS launch videos, app UI demos,
  kinetic typography, audio visualizers, and creating/managing all asset types using the Motio / Vibmo Python framework.
  Use this skill whenever the user asks to create, animate, edit, style, or render motion graphics, UI mockups,
  charts, kinetic text, video scenes, or custom assets in Motio or Vibmo.
---

# ✦ Motio / Vibmo Motion Graphics Skill

This skill guides AI agents and developers in creating production-grade, 60 FPS motion graphics using `motio` (`vibmo`). It enforces zero-boilerplate semantic authoring, beautiful spring physics defaults, GPU shader post-processing, and a structured workflow for generating and registering all types of assets.

---

## 🧭 The 5 Core Principles

1. **Single-Line God Import**: Always begin scripts with:
   ```python
   from motio.agent_api import *
   ```
2. **High-Level Intent & Method Chaining**: Never write per-frame math or coordinates. Use fluent actions:
   ```python
   scene.add(GlassCard()).align("center").pop_in()
   ```
3. **Beautiful Defaults**: All built-in components include natural spring overshoot, smooth deceleration, frosted glass shaders, and subtle drop shadows. Do not override defaults unless explicitly asked.
4. **Visual Feedback Loop**: Always generate a storyboard contact sheet (`scene.storyboard("storyboard.png")`) or preflight check (`scene.validate()`) before final video rendering.
5. **Centralized Asset Management**: Use `Asset.*` factories and `AssetLibrary` to load images, videos, audio, procedural SFX, icons, gradients, and fonts.

---

## ⚡ Canonical Scene Recipe

```python
from motio.agent_api import *

# 1. Initialize Canvas
scene = Scene(
    width=1920,
    height=1080,
    fps=60,
    duration=5.0,
    background=colors.DARK_NAVY,
)

# 2. Cinematic Post-Processing
scene.add_post_fx(Vignette(intensity=0.25), FilmGrain(amount=0.01))

# 3. Assemble Semantic UI Components
card = GlassCard(direction="column", gap=16, padding=32, corner_radius=24, position=(240, 200))
icon = Icon("lucide:sparkles", size=36, color=colors.CYAN)
title = KineticText("Automated Motion in Python", font_size=32, bold=True)
counter = MetricCounter(start_val=0, end_val=250000, prefix="$", suffix=" MRR", font_size=52, bold=True, color=colors.EMERALD)

card.add(icon, title, counter)
scene.add(card)

# 4. Choreograph Motion Verbs
@scene.animate
def main():
    # Pop in the card with spring physics
    yield card.pop_in(delay=0.1, duration=0.8)
    
    # Staggered wave reveal of characters, counter ticker, and icon bounce
    yield scene.all(
        title.reveal_characters(stagger=0.025),
        counter.count_to(duration=1.8, ease=Ease.out_expo),
        icon.bounce(amplitude=1.3, count=2),
    )
    
    # Harmonic idle floating
    card.float_idle(amplitude=6, speed=1.2)
    yield scene.wait(1.5)

# 5. Output
if __name__ == "__main__":
    scene.storyboard("storyboard.png")          # Instant 6-frame progression
    scene.render("output.mp4", quality="high")  # Master 1080p 60FPS export
```

---

## 📚 Deep-Dive Specialized References

For full specifications on assets, components, verbs, and templates, consult the dedicated reference manuals:

- 🎨 **[Asset Creation & Registration Guide](./references/asset_creation_guide.md)**: How to create, generate, load, and register every single asset type (Images, Videos, Vector Icons, Audio Tracks, Procedural SFX, Gradients, Textures, HTML/Tailwind, Lottie, Custom Components, and Shaders).
- 🧩 **[Component Catalog](./references/component_catalog.md)**: Complete catalog of all Mockups, Hardware Frames, UI Cards, AI Badges, Form Controls, Tables, and Charts.
- 🎬 **[Motion Verbs & Transitions Cheat Sheet](./references/motion_verbs_cheat_sheet.md)**: All motion actions, 17+ transition types, spring parameters, easing curves, and physics force fields.
- 🚀 **[Showcase Recipes & Scenarios](./examples/recipes.md)**: End-to-end production scripts for SaaS launches, mobile demos, audio visualizers, and shape morphing.

---

## 🛠️ Step-by-Step Agent Workflow

When fulfilling a user request for motion graphics or video assets:

1. **Identify the Scene Requirements**:
   - Canvas resolution (`1920x1080` widescreen, `1080x1920` vertical reel, `1080x1080` square).
   - Theme and aesthetic palette (`DARK_NAVY`, `SLATE_900`, `CYBERPUNK`, `MINIMAL_LIGHT`).
   - Assets needed (Icons, mockups, audio, logos, charts).
2. **Assemble the Hierarchy**:
   - Nest child elements inside containers (`GlassCard`, `FlexContainer`, `BrowserWindow`, `PhoneFrame`).
   - Use `scene.add()` to register top-level elements and post-processing filters (`Vignette`, `FilmGrain`, `BackdropBlur`).
3. **Decorate the Choreography**:
   - Write `@scene.animate` generator functions.
   - Use `yield scene.all(...)` for concurrent actions and `yield action` for sequential steps.
   - Use `yield scene.wait(seconds)` for idle pauses.
4. **Validate & Inspect**:
   - Run `scene.validate()` to catch duration overflows (`delay + duration > scene.duration`).
   - Export `scene.storyboard("storyboard.png")` to verify 6-frame composition progression.
5. **Render Final Output**:
   - Use `scene.render("output.mp4", quality="high")` or `--resume` for fast resumption.

---

## ⚠️ Critical Pitfalls & Agent Rules

| Pitfall | Incorrect | Correct |
| :--- | :--- | :--- |
| Import individual symbols | `from motio import Scene` | `from motio.agent_api import *` |
| Direct property assignment | `node.position = (100, 200)` | `node.position.set((100, 200))` or `node.at(100, 200)` |
| Unpacking generator yield | `yield *cursor.click()` | `yield cursor.click()` or `yield scene.all(cursor.click(), ...)` |
| Undecorated animation | `def main(): yield ...` | `@scene.animate\ndef main():\n    yield ...` |
| Non-reactive custom state | `self.custom_val = 10` | `self.custom_val = Signal(10.0, "name.val")` |
| Missing fonts | Hardcoding uninstalled fonts | Use standard fonts (`"Inter"`, `"Roboto"`, `"Space Grotesk"`) |
