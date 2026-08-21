# ✦ Motio: The AI Agent Vibe Coding Guide

> **For LLMs & AI Coding Agents (Claude, Codex, Antigravity, ChatGPT, Gemini, Cursor).**
> This guide teaches you how to generate world-class, aesthetic motion graphics with **zero boilerplate** using `motio`.

---

## 🧭 The 5 Motio Principles for Agents

1. **Single-Line God Import**: Always import everything in one line: `from motio.agent_api import *`.
2. **High-Level Intent & Method Chaining**: Never manually compute per-frame coordinates. Chain fluent helpers: `scene.add(GlassCard()).align("center").pop_in()`.
3. **Beautiful Defaults**: Every preset comes with natural spring overshoot, smooth deceleration, and visual polish. Keep default parameters unless explicitly requested.
4. **Semantic Primitives**: Think in design components (`BrowserWindow`, `GlassCard`, `MetricCounter`, `Cursor`, `Spotlight`, `MorphPath`, `Icon`).
5. **Visual Feedback**: Always generate a storyboard (`scene.storyboard("preview.png")`) so you or the user can inspect the 6-frame progression in 0.1 seconds.

---

## ⚡ Canonical Motio Recipe

```python
from motio.agent_api import *

# 1. Initialize Scene (1080p @ 60 FPS, Dark aesthetic)
scene = Scene(
    width=1920,
    height=1080,
    fps=60,
    duration=4.5,
    background=colors.DARK_NAVY,
)

# 2. Assemble Semantic Components with Auto-Layout
card = GlassCard(direction="column", gap=16, padding=32, corner_radius=24, position=(200, 200))
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
    # Pop in the card with spring physics
    yield card.pop_in(delay=0.1, duration=0.8)
    
    # Staggered wave reveal of heading characters while counting numbers
    yield scene.all(
        title.reveal_characters(stagger=0.025),
        counter.count_to(duration=1.8, ease=Ease.out_expo),
        icon.bounce(amplitude=1.3, count=2),
    )
    
    # Gentle continuous floating idle
    card.float_idle(amplitude=6, speed=1.2)
    yield scene.wait(1.5)

# 5. Visual Storyboard, Live Studio & Video Export
if __name__ == "__main__":
    scene.storyboard("storyboard.png")                # Instant 6-frame progression
    # scene.preview()                                 # Opens live interactive Web Studio in browser
    # scene.render("output.mp4", quality="draft")     # 2-second ultra-fast preview
    scene.render("output.mp4", quality="high")        # Master 1080p 60FPS export
```

---

## 📖 Motion Verb Reference

| Verb | Target Components | Description |
| :--- | :--- | :--- |
| `node.pop_in(delay=0.1, duration=0.8)` | Any `Node`, `GlassCard`, `Icon` | Bouncy spring entrance from scale 0.6 + opacity fade |
| `node.fade_up(offset=40, duration=0.7)` | Any `Node`, `CodeWindow`, `Axes` | Smooth slide upward with cubic deceleration |
| `node.fade_in(duration=0.5)` | Any `Node` | Clean opacity fade |
| `node.fade_out(duration=0.5)` | Any `Node` | Clean opacity fade out |
| `node.bounce(amplitude=1.2, count=2)` | Any `Node`, `Icon` | Elastic pulse for emphasis / beat drops |
| `node.float_idle(amplitude=6, speed=1.0)` | Any `Node`, `GlassCard` | Continuous organic harmonic oscillation |
| `text.reveal_characters(stagger=0.025)` | `KineticText` | Staggers character glyphs upward in a fluid wave |
| `text.reveal_words(stagger=0.08)` | `KineticText` | Staggers whole words simultaneously |
| `text.typewriter(speed=25)` | `KineticText` | Types out characters sequentially |
| `counter.count_to(duration=1.8)` | `MetricCounter` | Smooth numeric ticker with exponential deceleration |
| `formula.transform_to(latex)` | `MathFormula` | Smooth equation crossfade and scale morph |
| `curve.trim_end.to(1.0, duration=2.0)` | `Path`, `axes.plot()` | Traces out mathematical curves & SVG lines |

| `path.morph_to(target_shape)` | `MorphPath` | Smooth organic Bézier metamorphosis between arbitrary vector shapes |
| `camera.zoom_to(node, zoom=2.0)` | `Camera` | Focuses and zooms viewport onto a node or coordinate |
| `camera.pan_to(node)` | `Camera` | Smoothly repositions camera focus point |
| `camera.reset()` | `Camera` | Pulls camera back to default full canvas view |
| `cursor.move_to(node)` | `Cursor` | Glides cursor to the center of any UI component |
| `cursor.click()` | `Cursor` | Simulates mouse press with spring click bounce |
| `spotlight.opacity.to(1.0)` | `Spotlight` | Dims canvas and illuminates focus element |

---

## 🎨 Semantic Design & Product Primitives

### 1. `MorphPath` & `Shape` (Vector Shape Metamorphosis)
```python
# Create animatable morphing shape
morph = MorphPath(shape=Shape.circle(radius=80), fill=colors.CYAN.with_alpha(0.2), stroke=colors.CYAN)
scene.add(morph)

# Morph fluidly across geometric shapes
yield morph.morph_to(Shape.star(outer_radius=100, inner_radius=45), duration=1.2, ease=Ease.in_out_back)
yield morph.morph_to(Shape.heart(size=110), duration=1.0, ease=Ease.in_out_cubic)
yield morph.morph_to(Shape.gear(radius=85, teeth=8), duration=1.2)
```

### 1. `BrowserWindow` & `PhoneFrame` (Device Mockups)
```python
browser = BrowserWindow(
    url="https://app.pulsemetrics.io",
    title="PulseMetrics — Analytics",
    width=1440,
    height=880,
    position=(240, 100),
)
browser.add_content(metrics_row, chart_card)
```

### 2. `VideoNode` & Embedded Screen Recordings
```python
# Frame-accurate video track with speed scaling, trimming, and zooming
video = Asset.video("assets/demo.mp4", trim=(1.0, 8.0), speed=1.2, loop=True, corner_radius=16)

# Embed inside BrowserWindow
browser.add_content(video)

# Zoom into specific button or sub-region on the video screen
yield video.zoom_to_region((0.3, 0.2, 0.4, 0.4), duration=1.0, ease=Ease.out_expo)
yield video.reset_zoom(duration=0.8)
```

### 3. `Precomp` & `AlphaMatte` / `LumaMatte` (Compositing Graph)
```python
# Group a complex sub-tree of layers into a single compositing unit
dashboard = precomp(card1, card2, chart, width=1200, height=800)
scene.add(dashboard)
yield dashboard.pop_in()

# Stencil / mask target layer using a shape or text matte
masked_layer = AlphaMatte(target=video, matte=Shape.star(outer_radius=120, inner_radius=50))
scene.add(masked_layer)
```

### 4. `Cursor` & `Spotlight` / `Callout` (UI Navigation)
```python
cursor = Cursor(position=(960, 540))
spotlight = Spotlight(target=chart_card, radius=340)
callout = Callout(
    title="AI Anomaly Engine",
    description="+48.2% surge detected",
    badge="LIVE",
    position=(1020, 480),
)
```

### 3. `GlassCard` (Frosted Glass UI Card)
```python
card = GlassCard(
    direction="row" | "column",
    gap=16,
    padding=24,
    corner_radius=20,
    fill=Color.WHITE.with_alpha(0.07),
    stroke=Color.WHITE.with_alpha(0.15),
)
```

### 4. `MetricCounter` (Animated Numbers)
```python
counter = MetricCounter(
    start_val=0,
    end_val=148500,
    prefix="$",
    suffix=" / mo",
    font_size=48,
    bold=True,
    color=colors.EMERALD,
)
```

### 5. `CodeWindow` (macOS Terminal Mockup)
```python
code_win = CodeWindow(
    code="def hello():\n    return 'vibe'",
    title="script.py",
    font_size=20,
    width=650,
)
```

### 6. `NotificationToast` (Push Bubble)
```python
toast = NotificationToast(
    title="Payment Received",
    description="$250.00 from Stripe",
    icon_name="lucide:check",
    icon_color=colors.EMERALD,
)
```

### 7. `MathFormula` & `Axes` (Mathematical Rendering)
```python
# Math Equation with glowing symbols
formula = MathFormula(latex=r"\int_{0}^{\infty} e^{-x^2} dx = \frac{\sqrt{\pi}}{2}", font_size=42, color=colors.AMBER)

# 2D Coordinate Grid
axes = Axes(x_range=(-4, 4), y_range=(-2, 2), width=800, height=450, grid=True)
curve = axes.plot(lambda x: math.sin(x) * math.exp(-0.2*abs(x)), color=colors.CYAN)
```

### 8. `Asset` & `Sequence` (Assets & Multi-Scene Composition)
```python
# Asset Loading
logo = Asset.image("assets/logo.png", width=120)
music = Asset.audio("assets/track.mp3")

# Multi-Scene Composition
video = Sequence(intro_scene, demo_scene, outro_scene, transition=CrossFade(0.5))
```

---

## 🔄 Agent Storyboard Inspection Loop

When writing or editing a Motio scene:
1. Run `scene.validate()` to pre-flight check all assets, bounds, and timings.
2. Run `scene.storyboard("storyboard.png")`.
3. Inspect the generated 6-frame contact sheet.
4. If layout is cramped: increase padding, decrease font size, or adjust spacing.
5. If timing is too fast: increase duration or add `yield scene.wait(1.0)`.
6. Run `scene.render("output.mp4")` once the storyboard looks pristine.

---

## 🛠️ Common Agent Mistakes & Instant Fixes

| Pitfall | What Went Wrong | Correct Fix |
| :--- | :--- | :--- |
| `from motio import Scene, ...` | Importing individual symbols leads to missing imports | Always use: `from motio.agent_api import *` |
| `card.position = (100, 200)` | Direct assignment bypasses Signal reactivity | Use: `card.position.set((100, 200))` or `card.at(100, 200)` |
| `yield *cursor.click()` | Unpacking return list with `*` is not valid syntax in Python generators | Simply use: `yield cursor.click()` or `yield scene.all(cursor.click(), ...)` |
| `GlassCard(glow=True)` | Hallucinating invalid constructor parameters | Use: `GlassCard(specular_rim=True, shadow=DropShadow.glow(colors.CYAN))` |
| `scene.animate` not decorated | Calling animate function directly without `@scene.animate` | Decorate the generator: `@scene.animate\ndef main():\n    yield ...` |
| Animation ends after scene ends | `card.pop_in(delay=5.0, duration=2.0)` on a 4.0s scene | Call `scene.validate()` to catch timing overflows; ensure `delay + duration <= scene.duration` |
| Missing fonts crash | Requesting custom system fonts not installed | `FontManager` auto-fetches Google Fonts; prefer standard font names like `"Inter"`, `"Roboto"`, `"Space Grotesk"` |

