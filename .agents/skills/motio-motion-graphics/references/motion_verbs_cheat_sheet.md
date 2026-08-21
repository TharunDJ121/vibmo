# ✦ Motion Verbs & Transitions Cheat Sheet for Motio / Vibmo

This reference documents every motion action, transition type, easing curve, and physics force in the Motio engine.

---

## 🎬 1. Motion Verbs Reference

| Verb Method | Target Components | Description | Example |
| :--- | :--- | :--- | :--- |
| `node.pop_in(delay, duration)` | Any `Node`, `GlassCard`, `Icon` | Spring overshoot entrance from scale 0.6 + opacity fade | `yield card.pop_in(delay=0.1, duration=0.8)` |
| `node.fade_up(offset, duration)`| Any `Node`, `CodeWindow`, `Axes` | Smooth slide upward with cubic deceleration | `yield text.fade_up(offset=40, duration=0.7)` |
| `node.fade_in(duration)` | Any `Node` | Clean opacity 0.0 $\rightarrow$ 1.0 fade | `yield node.fade_in(duration=0.5)` |
| `node.fade_out(duration)` | Any `Node` | Clean opacity 1.0 $\rightarrow$ 0.0 fade | `yield node.fade_out(duration=0.5)` |
| `node.bounce(amplitude, count)`| Any `Node`, `Icon` | Elastic pulse for emphasis / beat drops | `yield icon.bounce(amplitude=1.3, count=2)` |
| `node.float_idle(amplitude, speed)`| Any `Node`, `GlassCard` | Continuous harmonic organic oscillation | `card.float_idle(amplitude=6, speed=1.2)` |
| `node.tilt_3d(pitch, yaw, roll)` | Any `Node`, `BrowserWindow` | 2.5D perspective tilt transformation | `yield node.tilt_3d(pitch=0.2, yaw=-0.25)` |
| `text.reveal_characters(stagger)` | `KineticText` | Staggers character glyphs in a fluid upward wave | `yield text.reveal_characters(stagger=0.025)` |
| `text.reveal_words(stagger)` | `KineticText` | Staggers entire words simultaneously | `yield text.reveal_words(stagger=0.08)` |
| `text.typewriter(speed)` | `KineticText` | Types out text sequentially character by character | `yield text.typewriter(speed=25)` |
| `counter.count_to(duration, ease)` | `MetricCounter` | Smooth numeric ticker with easing curve | `yield counter.count_to(duration=1.8)` |
| `morph.morph_to(shape, duration)` | `MorphPath` | Smooth Bézier metamorphosis between geometric shapes | `yield morph.morph_to(Shape.star(), duration=1.2)` |
| `video.zoom_to_region(bounds)` | `VideoNode`, `AdvancedVideoNode` | Smooth camera zoom into sub-rectangle of video frame | `yield video.zoom_to_region((0.4, 0.2, 0.4, 0.4))` |
| `video.reset_zoom(duration)` | `VideoNode` | Smoothly resets video zoom to full frame | `yield video.reset_zoom(duration=0.8)` |
| `cursor.move_to(node, duration)` | `Cursor` | Glides cursor to the center of any UI element | `yield cursor.move_to(button, duration=0.8)` |
| `cursor.click()` | `Cursor` | Simulates mouse press with spring bounce | `yield cursor.click()` |
| `camera.zoom_to(node, zoom)` | `Camera` | Focuses and zooms viewport onto a node or coordinate | `yield camera.zoom_to(card, zoom=2.0)` |
| `camera.pan_to(position)` | `Camera` | Smoothly repositions camera focus point | `yield camera.pan_to((1200, 500))` |
| `camera.reset()` | `Camera` | Pulls camera back to default full canvas view | `yield camera.reset()` |

---

## 🎞️ 2. Complete Transitions Catalog (18 Types)

Used in `Sequence(scene1, scene2, transition=...)` or composition cuts.

```python
from motio.agent_api import *

# 1. Standard Blends
CrossFade(duration=0.5)
CrossDissolve(duration=0.6)
Fade(duration=0.4)
Dissolve(dither=True, duration=0.5)
DipToColor(color=colors.BLACK, duration=0.5)

# 2. Geometric Motion
Slide(direction="left" | "right" | "up" | "down", duration=0.5, motion_blur=True)
PushCut(direction="left", duration=0.4)
Wipe(angle=45, feather=10, duration=0.5)
Iris(shape="circle" | "diamond" | "star", feather=20, duration=0.6)
ShapeWipe(shape="circle", duration=0.7)

# 3. 3D & Spatial Metamorphosis
Flip(axis="y", duration=0.8)
BookFlip(duration=0.9)
WhipPan(direction="left", duration=0.4)
ZoomPunch(scale=1.5, duration=0.45)
TransitionZoomBlur(strength=0.3, duration=0.5)
Ripple(frequency=12, amplitude=25, duration=0.7)

# 4. Cinematic & Stylized
GlitchTransition(intensity=0.8, duration=0.35)
LightLeak(color=colors.AMBER, duration=0.6)
```

---

## 📈 3. Easing & Timing Curves

```python
# Standard Presets
Ease.linear
Ease.in_quad, Ease.out_quad, Ease.in_out_quad
Ease.in_cubic, Ease.out_cubic, Ease.in_out_cubic
Ease.in_quart, Ease.out_quart, Ease.in_out_quart
Ease.in_expo, Ease.out_expo, Ease.in_out_expo
Ease.in_back, Ease.out_back, Ease.in_out_back
Ease.in_elastic, Ease.out_elastic, Ease.in_out_elastic
Ease.in_bounce, Ease.out_bounce, Ease.in_out_bounce

# Custom Bezier
Ease.bezier(0.16, 1.0, 0.3, 1.0)
```

---

## ⚡ 4. Spring Physics Configurations

```python
# Spring Parameters
Spring(stiffness=200.0, damping=15.0, mass=1.0)

# Typical Presets:
# Snappy / UI Click:   stiffness=300, damping=20
# Bouncy Pop:          stiffness=180, damping=12
# Gentle Float:        stiffness=90,  damping=14
```

---

## 🌪️ 5. Dynamic Physics Forces

```python
# Gravity
GravityField(g=980, direction=Vector2D(0, 1))

# Vortex Whirlwind
VortexForce(center=(960, 540), strength=400)

# Perlin Turbulence
TurbulentNoiseField(frequency=0.02, power=150)

# Point Attractor / Gravity Well
AttractorPoint(position=(960, 540), mass=1000)
```

---
*End of Motion Verbs & Transitions Cheat Sheet.*
