# ✦ Motio / Vibmo: Comprehensive API Reference Manual

Welcome to the definitive API reference for **Motio** (`vibmo`). Every single module, type, primitive, component, shader filter, transition, physics simulation, and audio/video feature is documented below with parameters, type signatures, and code examples.

---

## 📑 Table of Contents

1. [Single-Line God Import](#1-single-line-god-import)
2. [Core Types, Vectors, Matrices & Signals](#2-core-types-vectors-matrices--signals)
3. [Scene, Composition, Shot & Scheduler](#3-scene-composition-shot--scheduler)
4. [Primitives & Vector Morphing](#4-primitives--vector-morphing)
5. [Layout, Flexbox, Alignment & Multi-Platform Reflow](#5-layout-flexbox-alignment--multi-platform-reflow)
6. [Typography, Kinetic Text & Captions](#6-typography-kinetic-text--captions)
7. [Hardware Device Frames & Mockups](#7-hardware-device-frames--mockups)
8. [UI, Feedback, AI & Form Components](#8-ui-feedback-ai--form-components)
9. [Data Visualization & Mathematical Plotting](#9-data-visualization--mathematical-plotting)
10. [UI Navigation & Interactive Callouts](#10-ui-navigation--interactive-callouts)
11. [Visual FX, Shaders, Filters, Patterns & Distortion](#11-visual-fx-shaders-filters-patterns--distortion)
12. [Compositing Graph, Masks, Mattes & Blend Modes](#12-compositing-graph-masks-mattes--blend-modes)
13. [Sequences, Transitions & Timing Curves](#13-sequences-transitions--timing-curves)
14. [Physics, Dynamic Forces & Particle Emitters](#14-physics-dynamic-forces--particle-emitters)
15. [Audio Reactivity, Procedural SFX & Stem Mixer](#15-audio-reactivity-procedural-sfx--stem-mixer)
16. [Rigging, Constraints & Mathematical Expressions](#16-rigging-constraints--mathematical-expressions)
17. [Tracking, Chroma Keying & Portable Projects](#17-tracking-chroma-keying--portable-projects)
18. [Themes, Aesthetic Presets & Color Spaces](#18-themes-aesthetic-presets--color-spaces)
19. [Unified Asset Pipeline & Importers](#19-unified-asset-pipeline--importers)
20. [Turnkey Production Templates](#20-turnkey-production-templates)
21. [AI Agent Engine, Schema Generation & MCP](#21-ai-agent-engine-schema-generation--mcp)
22. [Web Studio, Desktop App & CLI Tooling](#22-web-studio-desktop-app--cli-tooling)

---

## 1. Single-Line God Import

```python
from motio.agent_api import *
# Alternatively: from vibmo.agent_api import *
```

This single line imports all components, types, verbs, colors, easing functions, transitions, and filters without namespace clutter or boilerplate.

---

## 2. Core Types, Vectors, Matrices & Signals

### `Color` & `colors`
Color representation supporting hex, RGBA, HSL, alpha modification, and interpolation.

```python
# Instantiation
c1 = Color.hex("#38bdf8")
c2 = Color.rgba(56, 189, 248, 1.0)
c3 = Color.hsla(199, 0.95, 0.60, 1.0)
c4 = Color.from_any("cyan")

# Methods
c5 = c1.with_alpha(0.5)      # Returns new Color with 50% opacity
c6 = c1.lerp(c2, t=0.5)       # Linear interpolation
hex_str = c1.to_hex()        # "#38bdf8"
rgba_tuple = c1.to_rgba()    # (0.22, 0.74, 0.97, 1.0)

# Built-in Colors Palette (colors.*)
# colors.WHITE, colors.BLACK, colors.DARK_NAVY, colors.CYAN, colors.INDIGO,
# colors.EMERALD, colors.ROSE, colors.AMBER, colors.PURPLE, colors.SLATE_900, etc.
```

### `LinearGradient` & `RadialGradient`
Smooth multi-stop gradients for vector fills and strokes.

```python
# Linear gradient
grad = LinearGradient(
    start=(0, 0),
    end=(1920, 1080),
    stops=[(0.0, colors.CYAN), (0.5, colors.INDIGO), (1.0, colors.PURPLE)]
)

# Radial gradient
radial = RadialGradient(
    center=(960, 540),
    radius=600,
    stops=[(0.0, Color.WHITE.with_alpha(0.8)), (1.0, Color.TRANSPARENT)]
)
```

### `Vector2D` & `Vector3D`
Immutable, math-overloaded vector classes.

```python
v1 = Vector2D(100.0, 200.0)
v2 = Vector2D(50.0, 50.0)
v3 = v1 + v2                  # Vector2D(150.0, 250.0)
dist = v1.distance_to(v2)
norm = v1.normalized()
dot_prod = v1.dot(v2)

p3d = Vector3D(100, 200, 50)
```

### `Matrix3x3` & `Matrix4x4`
Transformation matrices for 2D affine and 3D perspective calculations.

```python
m = Matrix3x3.identity().translate(100, 200).rotate(0.5).scale(1.5, 1.5)
m4 = Matrix4x4.perspective(fov=60, aspect=16/9, near=0.1, far=1000)
```

### `Signal[T]`
The reactive core of Motio. Every property on a `Node` (position, scale, rotation, opacity, color) is an animatable `Signal`.

```python
sig = Signal(0.0, name="opacity")

# Methods
sig.set(1.0)                        # Immediate change
action = sig.to(1.0, duration=0.8, ease=Ease.out_expo, delay=0.1) # Returns AnimationAction
val_at_t = sig.get(t=0.5)           # Evaluates value at timestamp t
sig.apply_spring(target=1.0, stiffness=180, damping=12)
```

### `Ease` & `CubicBezier`
Comprehensive library of easing curves.

```python
# Presets:
Ease.linear
Ease.in_quad, Ease.out_quad, Ease.in_out_quad
Ease.in_cubic, Ease.out_cubic, Ease.in_out_cubic
Ease.in_quart, Ease.out_quart, Ease.in_out_quart
Ease.in_expo, Ease.out_expo, Ease.in_out_expo
Ease.in_back, Ease.out_back, Ease.in_out_back
Ease.in_elastic, Ease.out_elastic, Ease.in_out_elastic
Ease.in_bounce, Ease.out_bounce, Ease.in_out_bounce

# Custom cubic bezier curve:
custom_ease = CubicBezier(0.16, 1.0, 0.3, 1.0)
```

### `Spring` & `SpringEasing`
Damped harmonic oscillator physics for organic motion.

```python
spring = Spring(stiffness=200.0, damping=15.0, mass=1.0)
spring_val = spring.evaluate(t=0.3)
```

---

## 3. Scene, Composition, Shot & Scheduler

### `Scene`
Top-level container representing a standalone motion graphics canvas.

```python
scene = Scene(
    width=1920,              # Canvas width in pixels (e.g. 1920, 1080, 3840)
    height=1080,            # Canvas height in pixels (e.g. 1080, 1920 for vertical reels)
    fps=60,                 # Frames per second (default: 60)
    duration=5.0,           # Total scene duration in seconds
    background=colors.DARK_NAVY, # Background color, gradient, or hex string
)

# Adding nodes & Post FX
scene.add(node1, node2)
scene.add_post_fx(Vignette(intensity=0.3), FilmGrain(amount=0.01))

# Audio Track
scene.set_audio("assets/soundtrack.mp3", volume=0.8)

# Choreography
@scene.animate
def main():
    yield node1.pop_in()
    yield scene.wait(1.0)

# Output methods
scene.validate()                       # Pre-flight timing & bounds verification
scene.storyboard("storyboard.png")     # Generates instant 6-frame progression PNG
scene.render("output.mp4", quality="high") # Master MP4 export ("draft", "high", "prores", "webm")
scene.preview()                        # Launches Web Studio on http://localhost:8000
```

### `Composition` & `Shot`
Continuous timeline composition supporting multi-shot narratives without raster hand-offs.

```python
film = Composition(width=1920, height=1080, fps=60, background=colors.DARK_NAVY)
card = film.add(GlassCard(position=(200, 200)))

with film.shot("intro", duration=2.0):
    @film.animate
    def intro():
        yield card.pop_in()

with film.shot("detail", duration=3.0):
    @film.animate
    def detail():
        yield card.position.to((900, 200), duration=1.5, ease=Ease.in_out_cubic)

film.render("narrative.mp4")
```

### `Choreographer` & Scheduler Verbs
- `scene.all(*actions)` / `all(*actions)`: Executes multiple animation actions concurrently; completes when the longest action completes.
- `scene.sequence(*actions)` / `sequence(*actions)`: Executes actions sequentially one after another.
- `scene.wait(seconds)` / `wait(seconds)`: Pauses execution on the timeline.

---

## 4. Primitives & Vector Morphing

### Vector Primitives
- `Rect(width, height, fill, stroke, stroke_width, corner_radius, position)`
- `RoundedRect(width, height, corner_radius=16, fill=colors.CYAN)`
- `Circle(radius=50, fill=colors.EMERALD, stroke=colors.WHITE)`
- `Ellipse(radius_x=80, radius_y=40, fill=colors.PURPLE)`
- `Polygon(points=[(0,0), (100,0), (50,80)], fill=colors.AMBER)`
- `Star(outer_radius=60, inner_radius=25, points=5, fill=colors.GOLD)`
- `Line(start=(0,0), end=(200,200), stroke=colors.CYAN, stroke_width=3)`
- `Path(d="M 10 10 H 90 V 90 H 10 Z", stroke=colors.WHITE, stroke_width=2)`

### `MorphPath` & `Shape`
Organic vector shape metamorphosis using arc-length resampling.

```python
# Geometric shape definitions
s_circle = Shape.circle(radius=80)
s_rect   = Shape.rect(width=160, height=120, corner_radius=16)
s_star   = Shape.star(outer_radius=90, inner_radius=40, points=5)
s_heart  = Shape.heart(size=100)
s_gear   = Shape.gear(radius=80, teeth=8)
s_play   = Shape.play_button(size=90)
s_svg    = Shape.from_svg_path("M12 2L2 22h20L12 2z")

# Morphing node
morph = MorphPath(shape=s_circle, fill=colors.CYAN.with_alpha(0.2), stroke=colors.CYAN, stroke_width=3)
scene.add(morph)

@scene.animate
def morph_demo():
    yield morph.morph_to(s_star, duration=1.2, ease=Ease.in_out_back)
    yield morph.morph_to(s_heart, duration=1.0, ease=Ease.in_out_cubic)
    yield morph.morph_to(s_gear, duration=1.2)
```

---

## 5. Layout, Flexbox, Alignment & Multi-Platform Reflow

### `Align`
Alignment helpers for positioning nodes relative to canvas or parent containers:
- `Align.TOP_LEFT`, `Align.TOP_CENTER`, `Align.TOP_RIGHT`
- `Align.CENTER_LEFT`, `Align.CENTER`, `Align.CENTER_RIGHT`
- `Align.BOTTOM_LEFT`, `Align.BOTTOM_CENTER`, `Align.BOTTOM_RIGHT`
- `node.align("center")` or `node.align(Align.CENTER, scene)`

### `FlexContainer` & `FlexLayout`
CSS Flexbox layout implementation for automatic spatial stacking and dynamic sizing.

```python
container = FlexContainer(
    direction="column" | "row",
    gap=16,
    padding=24,
    justify="center" | "start" | "end" | "space_between",
    align_items="center" | "stretch",
    position=(200, 100)
)
container.add(item1, item2, item3)
```

### `AutoResizeBox`
A bounding box container that dynamically recalculates its dimensions based on active child nodes.

### `SceneReflowEngine` & `AspectRatio`
Automatically converts 16:9 widescreen scenes into 9:16 vertical reels or 1:1 square posts.

```python
reflowed_scene = SceneReflowEngine.reflow(
    scene,
    target_aspect=AspectRatio.PORTRAIT_9_16 # AspectRatio.SQUARE_1_1, WIDESCREEN_16_9
)
```

---

## 6. Typography, Kinetic Text & Captions

### `Text`
Basic styled text node with typography controls.

```python
text = Text(
    text="Hello Motio",
    font_family="Inter",
    font_size=32,
    font_weight="bold",
    color=colors.WHITE,
    line_height=1.4,
    letter_spacing=0.5,
)
```

### `KineticText` & `GlyphNode`
High-end motion typography supporting staggered glyph and word animations.

```python
ktext = KineticText(
    "Automate Motion Design",
    font_size=48,
    bold=True,
    color=colors.WHITE,
    position=(300, 400)
)
scene.add(ktext)

@scene.animate
def text_anim():
    yield ktext.reveal_characters(stagger=0.03, duration=0.6, ease=Ease.out_expo)
    yield ktext.reveal_words(stagger=0.12, duration=0.8)
    yield ktext.typewriter(speed=30)
```

### Typography Shaders & FX
- `NeonText(text, glow_color=colors.CYAN, glow_radius=20)`
- `GradientText(text, gradient=LinearGradient(...))`
- `Text3D(text, depth=12, bevel=2)`
- `TextStroke(text, stroke_color=colors.WHITE, stroke_width=2)`
- `WarpText(text, curvature=0.3)`

### Kinetic Captions & Advanced Karaoke
- `KineticCaptions`: High-energy social captions with active word highlighting.
- `AdvancedKaraokeCaptions` & `TimedWord`: Millisecond-accurate lyric and transcript highlighting.

```python
captions = AdvancedKaraokeCaptions(
    words=[
        TimedWord("Generate", start=0.2, end=0.6),
        TimedWord("World-Class", start=0.6, end=1.1),
        TimedWord("Videos", start=1.1, end=1.8),
    ],
    highlight_color=colors.YELLOW,
    base_color=colors.WHITE,
    font_size=36
)
```

---

## 7. Hardware Device Frames & Mockups

Pixel-perfect hardware mockups with realistic chassis, camera bezels, reflection glare, and content viewports.

### `BrowserWindow`
```python
browser = BrowserWindow(
    url="https://motio.design",
    title="Motio — Motion Graphics",
    width=1440,
    height=880,
    position=(240, 100),
    dark_mode=True,
    corner_radius=16,
)
browser.add_content(ui_card, chart)
```

### Mobile, Tablet & Desktop Frames
- `PhoneFrame(model="iphone15_pro", width=380, height=780, color="titanium_black")`
- `TabletFrame(width=820, height=1100, orientation="portrait")`
- `LaptopFrame(model="macbook_pro_16", width=1280, height=800)`
- `WatchFrame(width=280, height=340)`
- `DesktopFrame(model="studio_display", width=1600, height=900)`

---

## 8. UI, Feedback, AI & Form Components

### `GlassCard`
Frosted glass card with specular rims, background blur, and customizable fills.

```python
card = GlassCard(
    direction="column",
    gap=16,
    padding=24,
    corner_radius=20,
    fill=Color.WHITE.with_alpha(0.06),
    stroke=Color.WHITE.with_alpha(0.12),
    specular_rim=True,
    position=(300, 200)
)
```

### `MetricCounter`
Animated numeric ticker with prefixes, suffixes, and exponential deceleration.

```python
counter = MetricCounter(
    start_val=0,
    end_val=148500,
    prefix="$",
    suffix=" ARR",
    font_size=52,
    bold=True,
    color=colors.EMERALD,
)
# Animate in generator:
yield counter.count_to(duration=1.8, ease=Ease.out_expo)
```

### `CodeWindow`
macOS terminal / IDE code block mockup with syntax highlighting simulation.

```python
code_win = CodeWindow(
    code="""import motio\nscene = motio.Scene()\nscene.render('output.mp4')""",
    title="demo.py",
    font_size=20,
    width=650,
)
```

### Feedback & Notification Badges
- `NotificationToast(title="Payment Received", description="$499.00 via Stripe", icon_name="lucide:check")`
- `AlertBanner(title="High Load Detected", level="warning")`
- `LoadingSpinner(size=32, color=colors.CYAN)`
- `SkeletonScreen(width=400, height=200)`
- `EmptyState(title="No Projects Found", description="Create a new motion project to begin.")`
- `ErrorBoundary(error_message="Connection timed out")`

### Form & UI Controls
- `ProgressBar(progress=0.75, width=400, color=colors.CYAN)`
- `Slider(value=42, min_val=0, max_val=100, width=300)`
- `Tabs(tabs=["Overview", "Analytics", "Settings"], active_index=0)`
- `Accordion(title="Deployment Configuration", is_open=True)`
- `Modal(title="Export Video", width=600, height=400)`
- `Dropdown(label="Resolution", options=["1080p", "4K", "Vertical 9:16"])`
- `Breadcrumbs(items=["Projects", "SaaS Promo", "Scene 1"])`
- `Pagination(current_page=2, total_pages=10)`
- Form Inputs: `InputField`, `SelectBox`, `RadioButton`, `Checkbox`, `ToggleButton`, `Switch`, `RangeSlider`

### AI & Next-Gen Product Primitives
- `GradientBackdrop`: Dynamic morphing mesh gradient.
- `ModelCard(name="Claude 3.5 Sonnet", provider="Anthropic", tokens_per_sec=84.2)`
- `ChatInputBar(placeholder="Ask AI anything...", has_voice=True, has_attachment=True)`
- `KineticSnapText(text="Reasoning...")`
- `FileAttachmentBadge(filename="revenue_q4.csv", size="1.2 MB")`
- `EditorialDoc(title="API Specification", word_count=1200)`
- `PillLaunchButton(text="Deploy to Production", icon="lucide:rocket")`
- `CommandPalette(query="> Export", items=[CommandItem("Render Video", "Ctrl+Enter"), ...])`
- `DataTable(columns=["User", "Role", "Status"], data=[["Alice", "Admin", "Active"], ...])`
- `TimelineView(events=[{"time": "10:00", "label": "Pipeline Started"}])`
- `Avatar(src="assets/avatar.jpg", size=48)`, `AvatarGroup(avatars=[...])`, `Badge(text="PRO", color=colors.INDIGO)`
- `ChatBubble(message="Can you add film grain?", is_user=False)`, `TypingIndicator()`
- `StatCard(title="Active Users", value="1.2M", change="+18.4%", is_positive=True)`

---

## 9. Data Visualization & Mathematical Plotting

### Charts Suite
- `AreaChart(data=[10, 25, 45, 30, 70, 95], fill=colors.CYAN.with_alpha(0.2), stroke=colors.CYAN)`
- `Sparkline(data=[12, 18, 14, 28, 35], color=colors.EMERALD)`
- `BarChart(categories=["Q1", "Q2", "Q3", "Q4"], values=[120, 190, 300, 500])`
- `PieChart(slices=[{"label": "Direct", "val": 40}, {"label": "Organic", "val": 60}])`
- `DonutChart(slices=[...], inner_radius=60)`
- `GaugeChart(value=78, min_val=0, max_val=100, label="GPU Load")`
- `LineChart(series=[{"name": "MRR", "data": [10, 20, 35, 60]}])`
- `ScatterChart(points=[(10, 20), (30, 45), (60, 80)])`
- `RadarChart(metrics=["Speed", "Quality", "Cost", "Scale"], values=[0.9, 0.95, 0.7, 0.85])`
- `FunnelChart(stages=[("Visitors", 10000), ("Signups", 2500), ("Paid", 600)])`
- `Heatmap(matrix=[[1, 5, 8], [4, 9, 2], [7, 3, 6]])`
- `CandlestickChart(candles=[{"open": 100, "high": 120, "low": 90, "close": 115}, ...])`

### Mathematical Equations & 2D Function Plots
- `MathFormula(latex=r"\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}", font_size=42, color=colors.AMBER)`
- `Axes(x_range=(-5, 5), y_range=(-2, 2), width=800, height=450, grid=True)`
- `axes.plot(func=lambda x: math.sin(x), color=colors.CYAN)`

---

## 10. UI Navigation & Interactive Callouts

- `Cursor(position=(960, 540))`: Simulates desktop mouse cursor.
  - `yield cursor.move_to(target_node, duration=0.8)`
  - `yield cursor.click()`
- `ClickIndicator()`: Radial shockwave particle pulse triggered on clicks.
- `Spotlight(target=node, radius=350)`: Dims canvas to spotlight attention on target node.
- `Callout(title="New Feature", description="One-click deploy", badge="NEW", position=(800, 300))`
- `Tooltip(text="Copy to Clipboard", target=button)`

---

## 11. Visual FX, Shaders, Filters, Patterns & Distortion

### Post-Processing Shaders & Cinematic Filters
- `FilmGrain(amount=0.015)`
- `Vignette(intensity=0.25, smoothness=0.5)`
- `BackdropBlur(radius=20)`
- `MotionBlur(samples=8, shutter_angle=180)`
- `Bloom(threshold=0.7, intensity=1.2)`
- `Glow(color=colors.CYAN, radius=30)`
- `ChromaticAberration(offset=3.0)`
- `DepthOfField(focus_distance=0.5, focal_length=50, aperture=2.8)`
- `TiltShift(blur_radius=15, focus_band=(0.4, 0.6))`
- `Dither(levels=8)`
- `ColorCorrection(brightness=0.0, contrast=1.1, saturation=1.2)`
- `LensFlare(position=(300, 200), intensity=0.8)`
- `GodRays(origin=(960, 0), intensity=0.6)`
- `Glitch(intensity=0.4, speed=10)`
- `Pixelate(pixel_size=12)`
- `RadialBlur(strength=0.15)`
- `ZoomBlur(amount=0.2)`
- `EdgeGlow(color=colors.INDIGO, width=4)`
- `Halftone(dot_size=6)`
- `Duotone(shadows=colors.DARK_NAVY, highlights=colors.CYAN)`

### Procedural Patterns & Textures
- `Checkerboard(tile_size=40, color1=colors.SLATE_900, color2=colors.SLATE_800)`
- `Gridlines(spacing=60, stroke=Color.WHITE.with_alpha(0.08))`
- `Rings(spacing=40, center=(960, 540))`
- `Starburst(rays=24, color=colors.CYAN)`
- `Tile(node, rows=4, cols=6)`
- `Zigzag(amplitude=20, frequency=10)`

### Distortion & Optical Effects
- `BarrelDistortion(amount=0.2)`
- `Fisheye(fov=120)`
- `Wave(amplitude=15, wavelength=80, speed=2.0)`
- `LiquidContours(scale=40, speed=1.5)`
- `Skew(angle_x=15, angle_y=0)`
- `CornerPin(tl=(100, 100), tr=(1800, 80), br=(1750, 1000), bl=(120, 980))`

### Edge & Noise Effects
- `Outline(width=2, color=colors.WHITE)`
- `ContourLines(levels=6)`
- `RoughenEdges(frequency=8, amplitude=4)`
- `Noise(scale=100, octaves=4)`
- `WhiteNoise(intensity=0.05)`
- `Scanlines(spacing=4, opacity=0.15)`
- `TVSignalOff()`

### Blur Suite
- `LinearProgressiveBlur(start=(0, 0), end=(0, 1080), max_radius=30)`
- `RadialProgressiveBlur(center=(960, 540), inner_radius=200, max_radius=40)`
- `RegionBlur(region=(200, 200, 600, 400), radius=25)`

---

## 12. Compositing Graph, Masks, Mattes & Blend Modes

### Compositing Graph Units
- `Precomp(*nodes, width=1200, height=800)`: Isolates subtree into a cached texture pass.
- `AlphaMatte(target=node, matte=shape)`: Stencils target using the alpha channel of matte.
- `LumaMatte(target=node, matte=texture)`: Stencils target using luminance values.
- `AdjustmentLayer(*effects)`: Applies shader post-processing to all underlying layers.
- `Mask(shape=Shape.circle(100), inverted=False)`: Vector clipping mask.

### 17 Layer Blend Modes (`BlendMode.*`)
- `NORMAL`, `MULTIPLY`, `SCREEN`, `OVERLAY`, `DARKEN`, `LIGHTEN`, `COLOR_DODGE`, `COLOR_BURN`, `HARD_LIGHT`, `SOFT_LIGHT`, `DIFFERENCE`, `EXCLUSION`, `HUE`, `SATURATION`, `COLOR`, `LUMINOSITY`, `ADD`.

### 2.5D Depth & Tilt
- `node.tilt_3d(pitch=0.25, yaw=-0.3, roll=0.0, perspective=1000)`
- `DropShadow(offset=(0, 16), blur=32, color=Color.BLACK.with_alpha(0.4))`
- `DropShadow.glow(color=colors.CYAN, radius=40)`

---

## 13. Sequences, Transitions & Timing Curves

### Multi-Scene Sequence
```python
seq = Sequence(
    scene_intro,
    scene_demo,
    scene_outro,
    transition=CrossFade(duration=0.6)
)
seq.render("full_video.mp4")
```

### Complete 17+ Transitions Catalog
1. `CrossFade(duration=0.5)`
2. `CrossDissolve(duration=0.6)`
3. `WhipPan(direction="left", duration=0.4)`
4. `ZoomPunch(scale=1.5, duration=0.45)`
5. `GlitchTransition(intensity=0.8, duration=0.35)`
6. `LightLeak(color=colors.AMBER, duration=0.6)`
7. `ShapeWipe(shape="circle" | "diamond" | "star", duration=0.7)`
8. `DipToColor(color=colors.BLACK, duration=0.5)`
9. `Slide(direction="left" | "right" | "up" | "down", duration=0.5, motion_blur=True)`
10. `PushCut(direction="left", duration=0.4)`
11. `Fade(duration=0.4)`
12. `Dissolve(dither=True, duration=0.5)`
13. `Iris(shape="circle", feather=20, duration=0.6)`
14. `Wipe(angle=45, feather=10, duration=0.5)`
15. `TransitionZoomBlur(strength=0.3, duration=0.5)`
16. `Ripple(frequency=12, amplitude=25, duration=0.7)`
17. `Flip(axis="y", duration=0.8)`
18. `BookFlip(duration=0.9)`

### Transition Timings
- `LinearTiming()`, `SpringTiming(stiffness=180, damping=12)`, `CubicBezierTiming(0.25, 1.0, 0.5, 1.0)`, `EaseInTiming()`, `EaseOutTiming()`, `EaseInOutTiming()`.

---

## 14. Physics, Dynamic Forces & Particle Emitters

### `ParticleEmitter` & `AdvancedParticleEmitter`
```python
particles = AdvancedParticleEmitter(
    rate=120,                # Particles spawned per second
    lifetime=(1.0, 2.5),     # Lifetime min/max in seconds
    speed=(100, 300),        # Initial speed range
    spread_angle=360,        # Emission angle in degrees
    colors=[colors.CYAN, colors.INDIGO, colors.PURPLE],
    size=(4, 12),
    gravity=Vector2D(0, 150),
    wind=Vector2D(50, 0),
    fade_out=True,
)
```

### Dynamic Force Fields
- `GravityField(g=980, direction=Vector2D(0, 1))`
- `VortexForce(center=(960, 540), strength=400)`
- `TurbulentNoiseField(frequency=0.02, power=150)`
- `AttractorPoint(position=(960, 540), mass=1000)`

### Physics Dynamics
- `SpringSimulation(stiffness=150, damping=10, initial_velocity=50)`
- `PendulumDynamics(length=200, gravity=980, damp=0.02)`
- `BounceDynamics(restitution=0.75, floor_y=900)`
- `PathFollower(path=bezier_curve, speed=200, orient_to_path=True)`

---

## 15. Audio Reactivity, Procedural SFX & Stem Mixer

### `ProceduralSFX` & `SFXTrack`
Zero-file synthetic procedural foley audio synthesizer (48kHz 32-bit float):
- `ProceduralSFX.pop(duration=0.12, freq_start=240, freq_end=880)`: Bubbly UI pop.
- `ProceduralSFX.click(duration=0.04, freq=1850)`: Crisp mechanical switch click.
- `ProceduralSFX.whoosh(duration=0.45)`: Smooth airy transitional whoosh.
- `ProceduralSFX.riser(duration=1.2, f_start=120, f_end=2400)`: Tension riser sweep.
- `ProceduralSFX.bass_drop(duration=0.6, freq_start=140, freq_end=35)`: Sub-bass impact thud.
- `ProceduralSFX.sparkle(duration=0.5)`: Magical frequency chime.

### `AudioStemMixer` & `AudioDucker`
```python
mixer = AudioStemMixer()
mixer.add_stem("music", "assets/soundtrack.mp3", volume=0.4)
mixer.add_stem("voice", "assets/voiceover.wav", volume=1.0)
mixer.add_stem("sfx", "assets/foley.wav", volume=0.7)
mixer.apply_ducking(duck_stem="music", trigger_stem="voice", reduction_db=-12.0)
mixer.export_stems("output_stems/") # Generates stem_music.wav, stem_vo.wav, stem_sfx.wav, stem_master.wav
```

### Audio Reactivity & Visualizers
- `AudioAnalyzer("track.mp3")`: Computes beat detection, spectral centroid, energy bands.
- `SpectrumBars(audio_path, bars=64, height=200, color=colors.CYAN)`
- `CircularSpectrum(audio_path, radius=180, bar_count=72)`
- `WaveformRibbon(audio_path, stroke=colors.EMERALD, stroke_width=3)`
- `VinylRecord(audio_path, rpm=33.3, radius=150)`
- `AudioProgressBar(audio_path, width=800)`
- `AudioReactivePulse(node, audio_path, scale_multiplier=1.25)`

---

## 16. Rigging, Constraints & Mathematical Expressions

- `LookAtConstraint(target=node_b)`: Automatically points rotation angle of node A toward node B.
- `FollowConstraint(target=node_b, lag=0.08, offset=(20, 20))`: Smooth follow-through rigging.
- `PathConstraint(path=bezier_curve, progress=sig)`: Constrains position along an arbitrary vector path.
- `ExpressionSignal(lambda t, ctx: math.sin(t * 4) * 50)`: Expression-driven reactive property.

---

## 17. Tracking, Chroma Keying & Portable Projects

- `ChromaKey(color=Color.hex("#00ff00"), tolerance=0.15, spill_suppression=0.5)`: Removes green/blue screens from video clips.
- `PointTracker(video_path, track_region=(100, 100, 50, 50))`: Tracks high-contrast feature points across video frames.
- `VibmoProject(root_dir=".")`: Packages and relinks external media assets into self-contained bundles.

---

## 18. Themes, Aesthetic Presets & Color Spaces

### Themes (`Themes.*`)
- `Themes.DARK_MODERN`: Deep navy/black backdrop, slate glass, cyan & emerald accents.
- `Themes.MINIMAL_LIGHT`: Clean white/grey backdrop, frosted light cards, indigo & rose accents.
- `Themes.CYBERPUNK`: Midnight black, neon magenta & electric cyan specular rims.
- `Themes.SUNSET_WARM`: Amber, coral, and deep violet gradients.
- `apply_style_to_scene(scene, Styles.CINEMATIC_GLOW)`

### Color Management & Spaces
- `ColorSpace.SRGB`, `ColorSpace.LINEAR_SRGB`, `ColorSpace.ACES_CG`, `ColorSpace.DISPLAY_P3`
- `ColorManager`: ACES filmic tone mapping and 32-bit linear floating point rasterization.

---

## 19. Unified Asset Pipeline & Importers

### The `Asset` Factory
- `Asset.image("assets/logo.png", width=120, corner_radius=8)`
- `Asset.video("assets/demo.mp4", trim=(1.0, 5.0), speed=1.2, loop=True)`
- `Asset.audio("assets/track.mp3")` or `Asset.audio("preset:cyberpunk")`
- `Asset.web("https://stripe.com", width=1440, height=900, scale=2.0)`: 4K retina web renderer.
- `Asset.html('<div class="p-4 bg-indigo-600 font-bold">Badge</div>')`: High-DPI HTML/Tailwind node.
- `Asset.lottie("assets/animation.json", speed=1.0)`: Bodymovin JSON animation.
- `Asset.font("assets/SpaceGrotesk-Bold.ttf", family_name="SpaceGrotesk")`
- `Asset.preload(*paths)`: Concurrently preloads assets.
- `Asset.bundle(scene, "project.zip")`: Bundles all dependencies into a portable zip.

### `AssetLibrary` & `AssetBrowser`
Central asset repository indexing built-in presets and user assets.
- Types: `AssetType.ICON`, `GRADIENT`, `TEXTURE`, `FONT`, `AUDIO`, `VIDEO`, `IMAGE`.
- Categories: `UI`, `NATURE`, `TECHNOLOGY`, `BUSINESS`, `ABSTRACT`, `PATTERNS`, `AUDIO`, `VIDEO`.

### `FontManager`
Auto-fetches and caches Google Fonts (e.g. `"Inter"`, `"Roboto"`, `"Space Grotesk"`, `"Fira Code"`).

---

## 20. Turnkey Production Templates

- `create_saas_launch_scene(title, subtitle, metrics, mockups)`: Complete SaaS launch video.
- `TEMPLATES["saas_launch"]`, `TEMPLATES["app_demo"]`, `TEMPLATES["kinetic_intro"]`
- CLI command: `vibmo create saas_launch my_project`

---

## 21. AI Agent Engine, Schema Generation & MCP

- `vibmo.agent_api`: Zero-boilerplate AI god module.
- `generate_component_schemas()`: Exports JSON schemas of all components for LLM tool calling.
- `export_llm_tool_definitions()`: OpenAI / Claude / Antigravity format function schemas.
- `PluginRegistry`: Allows third-party extension via `@register_component` and `@register_filter`.
- `VibmoMCPServer`: Model Context Protocol server exposing JSON-RPC stdio interface.

---

## 22. Web Studio, Desktop App & CLI Tooling

### CLI (`vibmo`)
```bash
vibmo render script.py -q high --resume   # Render MP4
vibmo studio script.py                    # Launch Web Studio
vibmo storyboard script.py -o preview.png # Generate 6-frame storyboard
vibmo doctor                              # Inspect FFmpeg, GPU OpenGL, Cairo, and fonts
vibmo templates                           # List available turnkey templates
vibmo create saas_launch demo_app         # Scaffold new project
```

### Web Studio Pro
Real-time 60 FPS in-browser DaVinci Resolve-grade workstation:
- **Workspaces**: Motion (NLE multi-track), Fusion (Node Graph), Color (Color grading), Fairlight (Audio mixer), Deliver (Render farm).
- **Interactive Canvas**: Direct drag-to-reposition handles, bounding box transform controls.
- **Embedded Python IDE**: Press `Ctrl+E` to edit script directly in browser with live hot-reloading.

---
*End of API Reference Manual.*
