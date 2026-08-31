# ✦ Vibmo Master Reference Manual & Technical Catalog

**Document Version**: 2.0.0  
**Framework**: `vibmo` (Vibmo / Motio Motion Graphics Engine)  
**Target Audience**: AI Coding Agents (Antigravity, Claude, Cursor, ChatGPT, Gemini), Motion Graphics Engineers, SaaS Product Designers  
**Project Root**: `c:\Users\djtha\projects\motion graphics`  
**Evaluation & Assembly Date**: 2026-08-31  

---

## Table of Contents

1. [Executive Summary & Core Philosophy](#1-executive-summary--core-philosophy)
   - [1.1 The 5 Vibmo Principles for AI Agents & Developers](#11-the-5-vibmo-principles-for-ai-agents--developers)
   - [1.2 High-Level Architecture Overview & Subsystem Block Diagram](#12-high-level-architecture-overview--subsystem-block-diagram)
   - [1.3 Canonical Zero-Boilerplate Scene Recipe](#13-canonical-zero-boilerplate-scene-recipe)
2. [Deep Subsystems & Engine Architecture](#2-deep-subsystems--engine-architecture)
   - [2.1 Scene Graph, Node Hierarchy & Reactive Signal[T] System](#21-scene-graph-node-hierarchy--reactive-signalt-system)
   - [2.2 Analytical & Numerical Spring Physics Engine](#22-analytical--numerical-spring-physics-engine)
   - [2.3 Easing Curves & Newton-Raphson Cubic Bézier Curve Evaluator](#23-easing-curves--newton-raphson-cubic-bézier-curve-evaluator)
   - [2.4 Vector Rasterization Engine (PyCairo Subpixel Rasterizer)](#24-vector-rasterization-engine-pycairo-subpixel-rasterizer)
   - [2.5 Spatial Hierarchy & 2.5D Projection Engine](#25-spatial-hierarchy--25d-projection-engine)
   - [2.6 Compositing Blend Modes & Layer Masks](#26-compositing-blend-modes--layer-masks)
   - [2.7 ModernGL GPU Post-Processing Shader Pipeline & CPU Fallbacks](#27-moderngl-gpu-post-processing-shader-pipeline--cpu-fallbacks)
   - [2.8 Procedural Audio Synthesis, Dynamic Ducking & Fairlight Stem Mixer](#28-procedural-audio-synthesis-dynamic-ducking--fairlight-stem-mixer)
   - [2.9 Resolve Color Management (RCM) & HDR Mastering Pipeline](#29-resolve-color-management-rcm--hdr-mastering-pipeline)
   - [2.10 Hierarchical Render Cache & Concatenated Sizing Pipeline](#210-hierarchical-render-cache--concatenated-sizing-pipeline)
   - [2.11 End-to-End Frame Lifecycle & Data Flow](#211-end-to-end-frame-lifecycle--data-flow)
3. [Exhaustive Master Component Suites & Shader Catalog (Sections 1–13)](#3-exhaustive-master-component-suites--shader-catalog-sections-113)
   - [Section 1: Procedural Audio & Sound Synthesis](#section-1-procedural-audio--sound-synthesis-vibmoaudiogenerators)
   - [Section 2: Non-Static Animated Backdrops](#section-2-non-static-animated-backdrops-vibmofxbackgrounds)
   - [Section 3: Hardware Chassis & Device Enclosures](#section-3-hardware-chassis--device-enclosures-vibmoproducthardware)
   - [Section 4: AI & SaaS Interactive UI Suites](#section-4-ai--saas-interactive-ui-suites-vibmoproductai)
   - [Section 5: Financial, 3D Spatial & Motion Charts](#section-5-financial-3d-spatial--motion-charts-vibmocharts)
   - [Section 6: Kinetic Typography & Title Sequences](#section-6-kinetic-typography--title-sequences-vibmotypographykinetic)
   - [Section 7: Visual Post-FX Shaders & Turnkey Production Suites](#section-7-visual-post-fx-shaders--turnkey-production-suites-vibmofxshaders-vbmotemplates)
   - [Section 8: Quality Gates, Developer UI & Intelligent Video Post](#section-8-quality-gates-developer-ui--intelligent-video-post-vibmoquality-vibmocomponents-vibmorigging-vibmovideo_post)
   - [Section 9: HDR, Color Science & Resolution Independence](#section-9-hdr-color-science--resolution-independence-vibmocolor-vibmocore-vibmopendercache)
   - [Section 10 & 11: Remocn-Inspired Motion Graphics & 6-Beat Video Spine](#section-10--11-remocn-inspired-motion-graphics--6-beat-video-spine-vbmotemplates-vbmocomposition)
   - [Section 12 & 13: Video-Shotcraft Staging, Beat-Sync & Dark Magic UI](#section-12--13-video-shotcraft-staging-beat-sync--dark-magic-ui-vibmoproductshotcraft-vibmoproductmagic_ui-vibmoai)
4. [Developer Tooling & CLI Suite](#4-developer-tooling--cli-suite)
   - [4.1 Complete 15-Subcommand CLI Matrix](#41-complete-15-subcommand-cli-matrix)
   - [4.2 Script Ingestion & Dynamic Resolution Engine](#42-script-ingestion--dynamic-resolution-engine)
   - [4.3 `.vibmo` Project Archive Container Specification](#43-vibmo-project-archive-container-specification)
   - [4.4 System Diagnostics (`vibmo doctor`)](#44-system-diagnostics-vibmo-doctor)
5. [Web Studio Pro Architecture](#5-web-studio-pro-architecture)
   - [5.1 Full Client-Server Architecture Diagram](#51-full-client-server-architecture-diagram)
   - [5.2 FastAPI REST API & WebSocket Protocol (`/ws`)](#52-fastapi-rest-api--websocket-protocol-ws)
   - [5.3 High-Speed Multi-Tier Frame Server & Prewarmer](#53-high-speed-multi-tier-frame-server--prewarmer)
   - [5.4 The Five Studio Workspace Pages](#54-the-five-studio-workspace-pages)
   - [5.5 Specialized Frontend Controllers & Hotkeys](#55-specialized-frontend-controllers--hotkeys)
6. [Model Context Protocol (MCP) Interface](#6-model-context-protocol-mcp-interface)
   - [6.1 JSON-RPC 2.0 Server Architecture (`vibmo-mcp` v2.0.0)](#61-json-rpc-20-server-architecture-vibmo-mcp-v200)
   - [6.2 Complete 11 MCP Tools Catalog & Schemas](#62-complete-11-mcp-tools-catalog--schemas)
   - [6.3 MCP Knowledge Resources & Prompt Templates](#63-mcp-knowledge-resources--prompt-templates)
7. [Video Packaging, NLE Timeline Interchange & Quality Gates](#7-video-packaging-nle-timeline-interchange--quality-gates)
   - [7.1 FFmpeg Streaming Pipe Engine & Codec Configurations](#71-ffmpeg-streaming-pipe-engine--codec-configurations)
   - [7.2 Multi-Core Parallel Pipeline & Resumable Cache](#72-multi-core-parallel-pipeline--resumable-cache)
   - [7.3 Universal NLE Timeline Interchange (OTIO, FCP 7 XML, CapCut/JianYing)](#73-universal-nle-timeline-interchange-otio-fcp-7-xml-capcutjianying)
   - [7.4 Production Quality Gates & Golden Launch Scene Recipe](#74-production-quality-gates--golden-launch-scene-recipe)

---

# 1. Executive Summary & Core Philosophy

The **Vibmo** (`vibmo` / `motio`) framework is a high-performance, broadcast-grade, hybrid 2D/2.5D/3D procedural motion graphics engine written in Python. It is engineered specifically for AI agent vibe coding, programmatic video generation, developer tooling (CLI, Web Studio Pro, MCP), and broadcast post-production.

## 1.1 The 5 Vibmo Principles for AI Agents & Developers

1. **Single-Line God Import**: Every primitive, container, chart, shader, and sound effect is exported from a single unified namespace:
```python
from vibmo.agent_api import *
```
2. **High-Level Intent & Method Chaining**: Never write per-frame math or hardcoded coordinate calculations. Use fluent, semantic actions:
```python
scene.add(GlassCard()).align("center").pop_in()
```
3. **Beautiful Defaults**: Every component comes pre-configured with natural spring overshoot physics, smooth deceleration, frosted glass shaders, and subtle drop shadows. Keep default parameters unless explicitly required.
4. **Semantic Primitives**: Think in terms of high-level design components (`BrowserWindow`, `GlassCard`, `MetricCounter`, `CandlestickChartPro`, `GlitchDecryptorText`, `FoldableDeviceFrame`, `StreamingTokenOutput`).
5. **Agent Storyboard Inspection Loop**: Always validate scenes (`scene.validate()`) and generate multi-frame contact sheets (`scene.storyboard("preview.png")`) to inspect layout, typography, and pacing before committing to final video renders.

---

## 1.2 High-Level Architecture Overview & Subsystem Block Diagram

```
+---------------------------------------------------------------------------------------------------+
|                                          Scene Container                                          |
|                         (1920x1080 @ 60 FPS, Duration, Timeline Tracks, Props)                    |
+---------------------------------------------------------------------------------------------------+
                                                  |
                         +------------------------+------------------------+
                         |                                                 |
+-------------------------------------------------+       +-----------------------------------------+
|           Reactive Scene Graph Tree             |       |       Procedural Audio & SFX Track      |
| • Node Hierarchy (parent/children transforms)   |       | • 15 Procedural Generator Suites        |
| • Signal[T] Reactive Animated Properties        |       | • Dynamic Sidechain Voiceover Ducker    |
| • Analytical Spring Physics & Cubic Béziers     |       | • Fairlight Anti-Pop Soft Fades         |
| • Coroutine Choreographer Scheduler             |       | • AudioStemMixer (Music/VO/SFX/WAV)     |
+-------------------------------------------------+       +-----------------------------------------+
                         |                                                 |
+-------------------------------------------------+                        |
|        Spatial & 2.5D Transform Engine          |                        |
| • 2D Affine Matrix3x3 Composition               |                        |
| • 3D Homography Matrix3D Quad Warping           |                        |
| • Camera3D (Orbit, Depth-of-Field, Shake)       |                        |
| • Concatenated Sizing Pipeline (1-Pass)         |                        |
+-------------------------------------------------+                        |
                         |                                                 |
+-------------------------------------------------+                        |
|          Hybrid Vector Rasterizer               |                        |
| • Subpixel PyCairo ImageSurface (ARGB32)        |                        |
| • 18 Compositing Blend Modes                    |                        |
| • Alpha & Luminance Mask Feathering             |                        |
| • 3-Tier Hierarchical Render Cache              |                        |
+-------------------------------------------------+                        |
                         |                                                 |
+-------------------------------------------------+                        |
|         ModernGL GPU Shader Pipeline            |                        |
| • Quad VBO & FBO Ping-Pong Compositor           |                        |
| • 13-Tap Gaussian Blur & Multi-Octave Bloom     |                        |
| • Chromatic Aberration, Vignette, Film Grain    |                        |
| • Deterministic CPU Vectorized Fallbacks        |                        |
+-------------------------------------------------+                        |
                         |                                                 |
+-------------------------------------------------+                        |
|        Color Science & HDR Mastering            |                        |
| • Resolve Color Management (DaVinci Wide Gamut) |                        |
| • DaVinci DRT Highlight Tone Mapping            |                        |
| • ITU-R BT.2408 SDR->HDR 203-Nit White Scaling  |                        |
| • Dolby Vision L1 & SMPTE ST.2084 PQ Encoding   |                        |
+-------------------------------------------------+                        |
                         |                                                 |
                         +------------------------+------------------------+
                                                  |
+---------------------------------------------------------------------------------------------------+
|                                   FFmpeg Master Video Pipeline                                    |
|             (ProRes 4444 Alpha / H.264 / WebM VP9 Alpha + 48kHz Stereo Master Audio)              |
+---------------------------------------------------------------------------------------------------+
```

---

## 1.3 Canonical Zero-Boilerplate Scene Recipe

```python
from vibmo.agent_api import *

# 1. Initialize Scene (1080p @ 60 FPS, Dark Navy canvas)
scene = Scene(
    width=1920,
    height=1080,
    fps=60,
    duration=5.0,
    background=colors.DARK_NAVY,
)

# 2. Add Background & Cinematic Post-Processing
bg = MeshGradientFlow(colors=[colors.INDIGO, colors.CYAN, colors.PURPLE], speed=0.6, complexity=4)
scene.add(bg)
scene.add_post_fx(Vignette(intensity=0.25), FilmGrain(amount=0.015))

# 3. Assemble Semantic UI Components
card = GlassCard(direction="column", gap=16, padding=32, corner_radius=24)
card.align("center", (1920, 1080)).at(240, 200)

icon = Icon("lucide:sparkles", size=36, color=colors.CYAN)
title = KineticText("Automated Motion in Python", font_size=32, bold=True)
counter = MetricCounter(start_val=0, end_val=250000, prefix="$", suffix=" MRR", font_size=52, bold=True, color=colors.EMERALD)

card.add(icon, title, counter)
scene.add(card)

# 4. Synchronize Procedural Sound Design
whoosh = WhooshDesignerSuite.cinematic_passby(duration=1.0)
scene.add_sfx("whoosh", time=0.1)

# 5. Choreograph with Natural Verbs
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

# 6. Storyboard Contact Sheet & Master Video Export
if __name__ == "__main__":
    scene.validate()                                  # Pre-flight bounds & timing verification
    scene.storyboard("storyboard.png")                # Instant 6-frame contact sheet
    # scene.preview()                                 # Opens interactive Web Studio Pro in browser
    scene.render("output.mp4", quality="high")        # Broadcast 1080p 60FPS export
```

---

# 2. Deep Subsystems & Engine Architecture

---

## 2.1 Scene Graph, Node Hierarchy & Reactive Signal[T] System

The engine's scene graph decouples parameter definition from timeline evaluation. Every animatable node property (`position`, `scale`, `rotation`, `opacity`, `rotate_x`, `rotate_y`, `z`, `skew`, `anchor`) is encapsulated in a reactive generic container: `Signal[T]`.

### Key Classes & Architecture (`vibmo/core/signal.py`, `vibmo/scene/node.py`)

- **`Signal[T]`**:
  - Encapsulates static value, animated segments (`List[AnimationSegment]`), and procedural runtime bindings (`Callable[[float], T]`).
  - `get(time: Optional[float] = None) -> T`: Evaluates the property at timestamp `time`. If bound via `bind()`, invokes the callable; if keyframed via `to()`, evaluates active timeline segments; otherwise returns the static value.
  - `set(value: T) -> Signal[T]`: Sets static value and clears active segments.
  - `bind(func: Callable[[float], T]) -> None`: Connects evaluation to continuous procedural math (e.g. idle floating oscillations, FFT-reactive audio scalers).
  - `link_to(other_signal: Signal, map_fn: Optional[Callable]) -> Signal[T]`: Implements an Expression Engine linking one signal directly to another with an arbitrary transformation map.
  - `to(target_value, duration, ease, delay, start_time) -> AnimationAction`: Creates an interpolation keyframe segment scheduled in coroutine choreographers.
  - `from_value(start_value, duration, ease, delay) -> AnimationAction`: Sets property to `start_value` and animates back to previous state.
- **`AnimationSegment`**:
  - Encapsulates `start_time`, `duration`, `end_time = start_time + duration`, `start_value`, `end_value`, and `ease: EasingFunc`.
  - `evaluate(time: float)`: Computes normalized time $t_{\text{norm}} = \frac{\text{time} - \text{start\_time}}{\text{duration}}$, calculates progress $p = \text{ease}(t_{\text{norm}})$, and invokes polymorphic interpolation.
- **`_interpolate_any(v1, v2, progress)`**:
  - Polymorphic interpolator supporting:
    - Scalar `int` / `float`: $v_1 + (v_2 - v_1) \cdot p$
    - `Vector2D`: `v1.lerp(v2, progress)`
    - `Color`: `c1.lerp(c2, progress)` via OKLab or RGB
    - Sequence tuples / lists: recursive element-wise interpolation
    - Discrete types: step function jump at $p \ge 0.5$.

### Node Hierarchy & Transform Propagation (`vibmo/scene/node.py`)
- Nodes maintain `parent: Optional[Node]` and `children: List[Node]`.
- `local_matrix(time) -> Matrix3x3`: Composes local position, scale, rotation Z, rotation X/Y (orthographic projection), anchor point, and skew into an affine transform.
- `world_matrix(time) -> Matrix3x3`: Multiplies parent transforms recursively to root:
  $$\mathbf{M}_{\text{world}} = \mathbf{M}_{\text{root}} \cdots \mathbf{M}_{\text{parent}} \cdot \mathbf{M}_{\text{local}}$$
- `world_opacity(time) -> float`: Multiplies opacities along the parent chain with timeline `in_point` and `out_point` windowing.
- `world_bounds(time) -> (min_x, min_y, width, height)`: Transforms local bounding box corners by `world_matrix` and returns axis-aligned bounds.
- `hit_test(world_x, world_y, time) -> Optional[Node]`: Inverts `world_matrix` and performs hit detection against local bounds in reverse Z-order.

---

## 2.2 Analytical & Numerical Spring Physics Engine

Vibmo implements a physically accurate, analytical second-order damped harmonic oscillator (`vibmo/core/spring.py`).

### Mathematical Formulation
The governing differential equation for a spring-damper system with mass $m$, damping coefficient $c$, and spring stiffness $k$ displaced from target is:
$$m \ddot{x}(t) + c \dot{x}(t) + k (x(t) - x_{\text{target}}) = 0$$

Let $\Delta = x_{\text{start}} - x_{\text{target}}$ and $v_0 = \text{initial\_velocity}$.
1. **Undamped Angular Frequency**:
   $$\omega_0 = \sqrt{\frac{k}{m}}$$
2. **Damping Ratio**:
   $$\zeta = \frac{c}{2 \sqrt{k m}}$$

The analytical solution evaluates across three distinct physical regimes:
- **Underdamped ($\zeta < 1.0$)**:
  $$\omega_d = \omega_0 \sqrt{1 - \zeta^2}$$
  $$c_1 = \Delta, \quad c_2 = \frac{v_0 + \zeta \omega_0 \Delta}{\omega_d}$$
  $$x(t) = x_{\text{target}} + e^{-\zeta \omega_0 t} \left( c_1 \cos(\omega_d t) + c_2 \sin(\omega_d t) \right)$$
- **Critically Damped ($\zeta = 1.0$)**:
  $$c_1 = \Delta, \quad c_2 = v_0 + \omega_0 \Delta$$
  $$x(t) = x_{\text{target}} + e^{-\omega_0 t} (c_1 + c_2 t)$$
- **Overdamped ($\zeta > 1.0$)**:
  $$\alpha = \omega_0 \sqrt{\zeta^2 - 1}, \quad r_1 = -\zeta \omega_0 + \alpha, \quad r_2 = -\zeta \omega_0 - \alpha$$
  $$c_2 = \frac{v_0 - r_1 \Delta}{r_2 - r_1}, \quad c_1 = \Delta - c_2$$
  $$x(t) = x_{\text{target}} + c_1 e^{r_1 t} + c_2 e^{r_2 t}$$

### Settling Duration & Easing Adaptation
- `_compute_settling_time(threshold=0.001)`: Numerically scans time steps $t \in [0, 10.0]$ with $\Delta t = 0.02\text{ s}$ to determine when $|x(t) - 1.0| \le 0.001$, yielding an exact physical settling duration.
- **`SpringEasing`**: Wraps the analytical `Spring` into a normalized $t \in [0, 1]$ easing function by mapping $t_{\text{seconds}} = t_{\text{norm}} \cdot \text{settling\_duration}$.

---

## 2.3 Easing Curves & Newton-Raphson Cubic Bézier Curve Evaluator

`vibmo/core/easing.py` provides 25+ standard Penner easing functions and an industrial-grade cubic bézier curve evaluator.

### Easing Function Catalog
- **Polynomial**: `in_quad`, `out_quad`, `in_out_quad`, `in_cubic`, `out_cubic`, `in_out_cubic`, `in_quart`, `out_quart`, `in_out_quart`.
- **Exponential & Circular**: `in_expo`, `out_expo`, `in_out_expo`, `in_circ`, `out_circ`, `in_out_circ`.
- **Trigonometric Sine**: `in_sine`, `out_sine`, `in_out_sine`.
- **Overshoot / Back**: `in_back`, `out_back` ($s=1.70158$), `in_out_back`.
- **Elastic & Bounce**: `in_elastic`, `out_elastic`, `in_out_elastic`, `in_bounce`, `out_bounce`, `in_out_bounce`.
- **Design Presets**: `Ease.smooth` (`CubicBezier(0.4, 0.0, 0.2, 1.0)`), `Ease.anticipate` (`CubicBezier(0.36, 0.0, 0.66, -0.56)`), `Ease.snappy` (`CubicBezier(0.12, 0.8, 0.32, 1.0)`).

### High-Performance Cubic Bézier Inversion (`CubicBezier`)
Given control points $(x_1, y_1)$ and $(x_2, y_2)$:
$$B_x(t) = 3(1 - t)^2 t x_1 + 3(1 - t) t^2 x_2 + t^3 = (a_x t^2 + b_x t + c_x) t$$
where:
$$c_x = 3 x_1, \quad b_x = 3(x_2 - x_1) - c_x, \quad a_x = 1 - c_x - b_x$$

To evaluate $y(x)$, the algorithm solves $B_x(t) = x$ using Newton-Raphson iteration:
$$t_{n+1} = t_n - \frac{B_x(t_n) - x}{B'_x(t_n)}$$
where $B'_x(t) = 3 a_x t^2 + 2 b_x t + c_x$.
If the derivative $|B'_x(t)| < 10^{-6}$, it automatically falls back to binary subdivision. Once $t$ is resolved, $y = B_y(t)$ is computed directly.

---

## 2.4 Vector Rasterization Engine (PyCairo Subpixel Rasterizer)

Vibmo utilizes PyCairo (`vibmo/render/rasterizer.py`) for pixel-perfect, subpixel 2D vector drawing.

### Rasterization Pipeline Steps
1. **Thread-Safe Backend Acquisition**: Retrieves thread-local `RenderBackend` matching current dimensions.
2. **Cairo Image Surface Allocation**: Allocates `cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)`.
3. **Context Scaling & Background Clearing**: Sets scaling matrix and paints background color or clears to transparent using `cairo.OPERATOR_CLEAR`.
4. **Camera View Matrix Transform**: Transforms root Cairo context by `camera.view_matrix()`.
5. **Recursive Node Rendering**:
   - Skips invisible or zero-opacity nodes.
   - Evaluates active rigging constraints (`apply_constraints(time)`).
   - If node has 3D rotation (`rotate_x` or `rotate_y`), branches to the **Projective 3D Quad Pipeline** (renders offscreen with padding, projects quad in 3D, and blits back).
   - Applies local affine transformation: `ctx.transform(cairo.Matrix(*local_mat.to_cairo_tuple()))`.
   - Sets compositing blend mode via `cairo.OPERATOR_*`.
   - Uses `ctx.push_group()` for alpha isolation and layer clipping masks.
   - Calls `node.draw(ctx, time)`.
   - Recursively renders children sorted by `z_index`.
   - Clips to vector mask shape if present and calls `ctx.paint_with_alpha(op)`.
6. **Pixel Extraction & Channel Swapping**: Flushes Cairo surface, extracts raw byte buffer as uint8 array $(H, W, 4)$, and swaps channels from Cairo native BGRA to standard RGBA: `rgba = arr[:, :, [2, 1, 0, 3]].copy()`.
7. **Post-FX Pass**: Passes RGBA buffer through active GPU/CPU post-processing shaders.

---

## 2.5 Spatial Hierarchy & 2.5D Projection Engine

### 2D Affine Matrix ($3\times3$) (`vibmo/core/matrix.py`)
Stored as 6 components representing affine transformations:
$$\begin{bmatrix} x' \\ y' \\ 1 \end{bmatrix} = \begin{bmatrix} a & c & e \\ b & d & f \\ 0 & 0 & 1 \end{bmatrix} \begin{bmatrix} x \\ y \\ 1 \end{bmatrix}$$
- Translation: $e = t_x, f = t_y$.
- Scaling: $a = s_x, d = s_y$.
- Rotation: $a = \cos\theta, b = \sin\theta, c = -\sin\theta, d = \cos\theta$.
- Skew: $c = \tan(\text{skew}_x), b = \tan(\text{skew}_y)$.
- Determinant: $\det = ad - bc$.
- Inversion:
  $$\mathbf{M}^{-1} = \frac{1}{\det} \begin{bmatrix} d & -c & c f - d e \\ -b & a & b e - a f \\ 0 & 0 & \det \end{bmatrix}$$

### 3D Matrix & Perspective Foreshortening (`Matrix3D`) (`vibmo/spatial/perspective.py`)
A $4\times4$ homogeneous matrix for spatial projection:
$$\mathbf{M}_{\text{perspective}}(d) = \begin{bmatrix} 1 & 0 & 0 & 0 \\ 0 & 1 & 0 & 0 \\ 0 & 0 & 1 & 0 \\ 0 & 0 & -\frac{1}{d} & 1 \end{bmatrix}$$
Point projection with perspective division:
$$\begin{bmatrix} X \\ Y \\ Z \\ W \end{bmatrix} = \mathbf{M} \begin{bmatrix} x \\ y \\ z \\ 1 \end{bmatrix}, \quad x_{\text{screen}} = \frac{X}{W}, \quad y_{\text{screen}} = \frac{Y}{W}$$

### Homography Quad Warping (`find_perspective_coeffs`)
To project a 2D layer quad onto arbitrary 4-point screen coordinates $(p_0, p_1, p_2, p_3)$, Vibmo solves the 8-coefficient backward perspective mapping:
$$x_{\text{src}} = \frac{a x_{\text{dst}} + b y_{\text{dst}} + c}{g x_{\text{dst}} + h y_{\text{dst}} + 1}, \quad y_{\text{src}} = \frac{d x_{\text{dst}} + e y_{\text{dst}} + f}{g x_{\text{dst}} + h y_{\text{dst}} + 1}$$
Constructs an $8\times8$ linear system $\mathbf{A} \mathbf{x} = \mathbf{B}$ solved via `np.linalg.solve(A, B)`.

### Cinematic Camera System (`vibmo/scene/camera.py`)
`Camera3D` provides physical cinematography controls:
- **Pan & Zoom**: `position` (Vector2D), `zoom` (float).
- **3D Orbit Angles**: `yaw` (Y-axis), `pitch` (X-axis), `roll` (Z-axis).
- **Depth of Field & Rack Focus**: `focal_distance` (float) and `aperture` (float).
- **Screen Shake**: Damped exponential decay shake generator:
  $$\text{offset}(t) = \sum_i A_i \sin(\omega_i \Delta t_i) e^{-3 \frac{\Delta t_i}{\text{duration}_i}}$$
- **Dynamic Node Following**: Binds camera position to target node world center with automatic canvas centering.
- **View Matrix Assembly**:
  $$\mathbf{M}_{\text{view}} = \mathbf{T}(c_x + \text{tilt}_x, c_y + \text{tilt}_y) \cdot \mathbf{R}(\theta) \cdot \mathbf{S}(z, z) \cdot \mathbf{T}(-c_x - p_x, -c_y - p_y)$$

---

## 2.6 Compositing Blend Modes & Layer Masks

### Supported Blend Modes (`vibmo/compositing/blend_modes.py`)
Maps 18 blend modes to Cairo operators and ModernGL fragment shader branches:

| Blend Mode | Cairo Operator | Mathematical Transfer Formula |
| :--- | :--- | :--- |
| `normal` | `cairo.OPERATOR_OVER` | $C = C_{\text{src}} \alpha_{\text{src}} + C_{\text{dst}} (1 - \alpha_{\text{src}})$ |
| `multiply` | `cairo.OPERATOR_MULTIPLY` | $C = C_{\text{base}} \cdot C_{\text{layer}}$ |
| `screen` | `cairo.OPERATOR_SCREEN` | $C = 1 - (1 - C_{\text{base}}) \cdot (1 - C_{\text{layer}})$ |
| `overlay` | `cairo.OPERATOR_OVERLAY` | $C = 2 B L$ if $B < 0.5$ else $1 - 2(1 - B)(1 - L)$ |
| `darken` | `cairo.OPERATOR_DARKEN` | $C = \min(C_{\text{base}}, C_{\text{layer}})$ |
| `lighten` | `cairo.OPERATOR_LIGHTEN` | $C = \max(C_{\text{base}}, C_{\text{layer}})$ |
| `color_dodge` | `cairo.OPERATOR_COLOR_DODGE` | $C = \text{clamp}(B / (1 - L), 0, 1)$ |
| `color_burn` | `cairo.OPERATOR_COLOR_BURN` | $C = 1 - \text{clamp}((1 - B) / L, 0, 1)$ |
| `hard_light` | `cairo.OPERATOR_HARD_LIGHT` | $C = 2 B L$ if $L < 0.5$ else $1 - 2(1 - B)(1 - L)$ |
| `soft_light` | `cairo.OPERATOR_SOFT_LIGHT` | $C = (1 - 2L) B^2 + 2 L B$ |
| `difference` | `cairo.OPERATOR_DIFFERENCE` | $C = |C_{\text{base}} - C_{\text{layer}}|$ |
| `exclusion` | `cairo.OPERATOR_EXCLUSION` | $C = B + L - 2 B L$ |
| `hue` | `cairo.OPERATOR_HSL_HUE` | $\text{SetLum}(\text{SetSat}(C_{\text{layer}}, \text{Sat}(B)), \text{Lum}(B))$ |
| `saturation` | `cairo.OPERATOR_HSL_SATURATION` | $\text{SetLum}(\text{SetSat}(B, \text{Sat}(L)), \text{Lum}(B))$ |
| `color` | `cairo.OPERATOR_HSL_COLOR` | $\text{SetLum}(C_{\text{layer}}, \text{Lum}(B))$ |
| `luminosity` | `cairo.OPERATOR_HSL_LUMINOSITY` | $\text{SetLum}(B, \text{Lum}(L))$ |
| `add` | `cairo.OPERATOR_ADD` | $C = \min(1.0, C_{\text{base}} + C_{\text{layer}})$ |
| `subtract` | `cairo.OPERATOR_OVER` (GLSL custom) | $C = \max(0.0, C_{\text{base}} - C_{\text{layer}})$ |

### Layer Masking & Alpha Stenciling (`vibmo/compositing/mask.py`)
- Supports vector shape masks, luminance mattes, and alpha stencils.
- Optional Gaussian edge feathering (`feather > 0.5`) and inversion (`invert = True`).
- Renders mask to offscreen alpha surface, applies blur filter, and performs in-place pre-multiplied channel scaling on target surfaces.

---

## 2.7 ModernGL GPU Post-Processing Shader Pipeline & CPU Fallbacks

### ModernGL GPU Compositor Architecture (`vibmo/render/gpu/compositor.py`)
The GPU Compositor manages a dedicated OpenGL 3.3 headless context via `moderngl.create_context(standalone=True)`.

```
                    +--------------------------------+
                    | ModernGL GPU Layer Compositor  |
                    | (OpenGL 3.3 Standalone Context)|
                    +--------------------------------+
                                    |
            +-----------------------+-----------------------+
            |                                               |
+------------------------+                     +------------------------+
|   Mesh VBOs & VAOs     |                     |  VRAM Texture / FBOs   |
| • Full-Screen Quad VBO |                     | • tex_base / tex_layer |
| • Dynamic 3D Quad VBO  |                     | • tex_out & fbo_out    |
| • 7 Compiled Programs  |                     | • fbo_ping / fbo_pong  |
+------------------------+                     | • 3D Texture LUT Cache |
                                               +------------------------+
```

### Multi-Pass Post-FX Execution Flow
1. **Texture Upload**: Uploads master frame to VRAM `tex_base`.
2. **Pass A — Brightness Extraction**:
   - Uses `FRAGMENT_SHADER_BLOOM_EXTRACT` into quarter-resolution `fbo_bloom_raw`.
   - Threshold equation:
     $$\text{factor} = \text{clamp}\left(\frac{\text{luma} - \text{threshold}}{1 - \text{threshold}}, 0, 1\right)$$
3. **Pass B — Horizontal 13-Tap Gaussian Blur**:
   - Renders `fbo_bloom_raw` into `fbo_ping` using direction `vec2(1.0, 0.0)`.
4. **Pass C — Vertical 13-Tap Gaussian Blur**:
   - Renders `fbo_ping` into `fbo_pong` using direction `vec2(0.0, 1.0)`.
5. **Pass D — Master Composite & Viewport Shaders**:
   - Renders `tex_base` and blurred `tex_pong` through `FRAGMENT_SHADER_POST_FX`.
   - Evaluates:
     - **Chromatic Aberration**: Radial RGB UV displacement:
       $$\mathbf{uv}_R = \mathbf{uv} + \Delta, \quad \mathbf{uv}_B = \mathbf{uv} - \Delta, \quad \Delta = (\mathbf{uv} - 0.5) \cdot \|\mathbf{uv} - 0.5\| \cdot k$$
     - **Additive Bloom**: $\mathbf{C} = \mathbf{C}_{\text{base}} + \mathbf{C}_{\text{bloom}} \cdot I_{\text{bloom}}$
     - **Smooth Vignette**: Normalized distance falloff with configurable radius:
       $$\text{falloff} = \text{clamp}\left(\frac{\text{norm\_dist} - r}{1 - r}, 0, 1\right), \quad \mathbf{C} = \mathbf{C} \cdot (1 - \text{falloff} \cdot I_{\text{vignette}})$$
     - **Film Grain & Dither**: High-speed hash noise weighted by luminance:
       $$W(\text{luma}) = \text{clamp}(\sin(\text{luma} \cdot \pi) \cdot 1.2, 0, 1)$$
6. **Pixel Readback**: Reads back final pixels as uint8 RGBA array from `fbo_out`.

### Hardware 3D LUT Color Grading (`FRAGMENT_SHADER_LUT3D`)
- Allocates a ModernGL `Texture3D` $(N \times N \times N)$ with linear trilinear interpolation.
- Samples 3D texture directly using input RGB as texture coordinates:
  $$\mathbf{C}_{\text{graded}} = \text{texture}(\mathbf{u\_lut}, \mathbf{C}_{\text{rgb}}), \quad \mathbf{C}_{\text{final}} = \text{mix}(\mathbf{C}_{\text{rgb}}, \mathbf{C}_{\text{graded}}, \text{intensity})$$

### Deterministic CPU Fallback Pipeline (`vibmo/render/backend.py` & `vibmo/fx/filters.py`)
If dedicated GPU VRAM or ModernGL is unavailable (e.g. headless CI/CD, restricted cloud worker environments), Vibmo automatically switches to `CPURenderBackend`:
- **Compositing**: Emulates blend modes using PyCairo image surfaces.
- **3D Quad Warping**: Uses PIL `Image.Transform.PERSPECTIVE` with exact 8-term homography matrices.
- **Post-Processing Shaders**: Pure vectorized NumPy / SciPy / PIL implementations of all 20+ visual filters.

---

## 2.8 Procedural Audio Synthesis, Dynamic Ducking & Fairlight Stem Mixer

### Mathematical Sound Synthesis Architecture (`vibmo/audio/generators/`)
Generates broadcast-quality 48kHz float32 audio arrays in Python without requiring external asset files.

| SFX Suite | Primary Math Synthesis Models |
| :--- | :--- |
| **1. Whoosh Designer Suite** | Pink noise 1/f filter, exponential chirp sweeps, stereo panning laws: Left=$\cos(p \pi/2)$, Right=$\sin(p \pi/2)$ |
| **2. Cyber UI Suite** | Dual FM synthesis, exponential envelope sweeps, harmonic chiming, saw-wave buzzers |
| **3. Glitch Stutter Suite** | Tape motor power-down deceleration ($t/(c+1)$ integral), sample-and-hold bitcrushing, granular slices |
| **4. Impact Sub Suite** | Exponential pitch decay drops (160Hz -> 32Hz), tanh saturation, inharmonic partials (1.0, 1.18, 1.56, 2.51) |
| **5. Keyboard Foley Suite** | Switch click transients, keycap bottom-out thud, spring resonance |
| **6. Riser Tension Suite** | 5-octave Shepard-Risset glissando glides, state-variable 2-pole resonant filter noise sweeps (200Hz -> 12kHz) |
| **7. Ambient Drone Suite** | Detuned multi-oscillator pads, FFT phase loop hums, rotary phase spacecraft hums, minor9 / major9 chords |
| **8. Vinyl Crackle Suite** | Poisson distribution impulse crackle, turntable hiss |
| **9. Laser Plasma Suite** | Hyperbolic frequency sweeps, plasma beam ring modulation |
| **10. Liquid Bubbles Suite** | Minnaert resonant acoustic bubble oscillation |
| **11. Paper Card Suite** | Granular friction noise, textured card shuffle slaps |
| **12. Retro 8-Bit Suite** | 4-bit NES triangle/square arpeggios, noise pseudo-RNG |
| **13. Alarm Siren Suite** | Frequency-modulated emergency sweeps, klaxon gating |
| **14. Chimes Harmonic Suite** | Celestial wind chime triads, high-Q modal resonators |
| **15. Camera Shutter Suite** | Multi-stage mechanical shutter open/mirror/close foley |

### Dynamic Voiceover Ducker (`vibmo/audio/ducker.py`)
`VoiceoverDucker` prevents music from masking narration by computing dynamic sidechain volume compression envelopes.
For voiceover segments $[t_{\text{start}}, t_{\text{end}}]$ with pre-fade duration $T_{\text{in}}$ and post-fade duration $T_{\text{out}}$:
- Pre-duck fade in ($t_{\text{start}} - T_{\text{in}} \le t < t_{\text{start}}$):
  $$p = \frac{t - (t_{\text{start}} - T_{\text{in}})}{T_{\text{in}}}, \quad \text{duck}(t) = \frac{1}{2} - \frac{1}{2} \cos(p \pi)$$
- Fully ducked ($t_{\text{start}} \le t \le t_{\text{end}}$):
  $$\text{duck}(t) = 1.0$$
- Post-duck release ($t_{\text{end}} < t \le t_{\text{end}} + T_{\text{out}}$):
  $$p = \frac{t - t_{\text{end}}}{T_{\text{out}}}, \quad \text{duck}(t) = \frac{1}{2} + \frac{1}{2} \cos(p \pi)$$
- Final Volume:
  $$V(t) = V_{\text{normal}} \cdot (1 - \text{duck}(t)) + V_{\text{ducked}} \cdot \text{duck}(t)$$

### Anti-Pop & Fairlight Soft-Fades (`vibmo/audio/anti_pop.py`)
- **Equal-Power Boundary Soft-Fades**: Applies $1.5\text{ ms}$ (72 samples @ 48kHz) raised-cosine crossfades to clip boundaries:
  $$\text{fade}_{\text{in}}(n) = \frac{1}{2} \left( 1 - \cos\left( \frac{\pi n}{N} \right) \right), \quad \text{fade}_{\text{out}}(n) = \frac{1}{2} \left( 1 + \cos\left( \frac{\pi n}{N} \right) \right)$$
- **EBU R128 / BS.1770 Loudness Normalization**: Calculates integrated LUFS loudness:
  $$\text{LUFS} = 20 \log_{10}(\text{RMS}) - 0.691, \quad \text{Gain}_{\text{linear}} = 10^{\frac{\text{Target}_{\text{LUFS}} - \text{Current}_{\text{LUFS}}}{20}}$$

### Multi-Track Stem Mixer (`vibmo/audio/stems.py`)
`AudioStemMixer` groups audio clips into semantic stems: `music`, `vo`, `sfx`, and `master`. Exports individual stems to 16-bit PCM WAV files using FFmpeg `amix=inputs=N:duration=longest`.

---

## 2.9 Resolve Color Management (RCM) & HDR Mastering Pipeline

### Resolve Color Management (`vibmo/color/rcm_pipeline.py`)
Vibmo implements a full scene-referred 32-bit floating-point color pipeline centered on the **DaVinci Wide Gamut (DWG)** intermediate space.

#### Primary Conversion Matrices to DaVinci Wide Gamut
$$\begin{aligned}
\mathbf{M}_{\text{Rec.709}\to\text{DWG}} &= \begin{bmatrix} 0.6068 & 0.2878 & 0.1054 \\ 0.0818 & 0.8872 & 0.0310 \\ 0.0264 & 0.1070 & 0.8666 \end{bmatrix} \\
\mathbf{M}_{\text{Rec.2020}\to\text{DWG}} &= \begin{bmatrix} 0.8262 & 0.1444 & 0.0294 \\ 0.0526 & 0.9324 & 0.0150 \\ 0.0125 & 0.0483 & 0.9392 \end{bmatrix} \\
\mathbf{M}_{\text{DCI-P3}\to\text{DWG}} &= \begin{bmatrix} 0.7228 & 0.2116 & 0.0656 \\ 0.0620 & 0.9168 & 0.0212 \\ 0.0182 & 0.0768 & 0.9050 \end{bmatrix}
\end{aligned}$$

### DRT Tone Mapping & SDR-to-HDR Diffuse White
- **SDR to HDR Diffuse White (`sdr_to_hdr_diffuse_white`)**:
  - Implements the ITU-R BT.2408 broadcast standard.
  - Scales 100-nit standard dynamic range graphics and kinetic typography to **203 nits**:
    $$\mathbf{C}_{\text{HDR}} = \mathbf{C}_{\text{SDR}} \cdot \frac{203.0}{100.0} = \mathbf{C}_{\text{SDR}} \cdot 2.03$$
  - Ensures titles and UI cards remain crisp and legible against bright HDR backgrounds.
- **DaVinci DRT Mode (`DRTMode.DAVINCI`)**:
  - Compresses extreme highlights while preserving hue and saturation. Above $400\text{ nits}$, smoothly blends highlights toward achromatic white to prevent harsh clipping.

### Dolby Vision L1 & HDR10 Analysis (`vibmo/color/hdr_dolby.py`)
#### SMPTE ST.2084 Perceptual Quantizer (PQ)
Maps linear scene luminance $Y \in [0, 10000]\text{ cd/m}^2$ to normalized non-linear code values $N \in [0, 1]$:
$$y = \frac{Y}{10000.0}, \quad N = \left( \frac{c_1 + c_2 y^{m_1}}{1 + c_3 y^{m_1}} \right)^{m_2}$$
where constants are defined by SMPTE ST.2084:
$$m_1 = \frac{2610}{16384}, \quad m_2 = \frac{2523}{4096} \times 128, \quad c_1 = \frac{3424}{4096}, \quad c_2 = \frac{2413}{4096} \times 32, \quad c_3 = \frac{2392}{4096} \times 32$$

#### Metadata Extraction
- **Dolby Vision L1**: `min_pq` (min luminance), `max_pq` (peak luminance), `avg_pq` (average picture level).
- **HDR10 Static Metadata**: `MaxCLL` (Maximum Content Light Level in nits), `MaxFALL` (Maximum Frame Average Light Level).
- **HDR10+ JSON Sidecar Exporter**: Exports SMPTE ST 2094-40 Profile B metadata JSON.

### MultiMaster Trim Management (`vibmo/color/multimaster.py`)
Allows simultaneous mastering of multiple delivery formats from a single Hero Master grade:
- `TrimPass("SDR_Rec709", target_nits=100.0)`
- `TrimPass("HDR10_1000", target_nits=1000.0)`

---

## 2.10 Hierarchical Render Cache & Concatenated Sizing Pipeline

### Hierarchical Render Cache (`vibmo/render/cache/hierarchical.py`)
Provides three independent media cache tiers for high-speed timeline scrubbing and real-time studio playback:
1. **Tier 1 (`TIER1_SOURCE_FUSION`)**: Pre-grade sources, generative backgrounds, fluid caustics, and procedural meshes.
2. **Tier 2 (`TIER2_NODE_GRAPH`)**: Per-node expensive filters (Denoise, Bloom, Diffusion, Raytracing).
3. **Tier 3 (`TIER3_SEQUENCE`)**: Composite layer blends, timeline crossfades, and final master frames.
- `invalidate_node(node_id, downstream=True)`: Granular invalidation that flushes modified nodes and downstream stages while preserving upstream static assets.

### Concatenated Sizing Pipeline (`vibmo/core/sizing_pipeline.py`)
A 10-stage resolution-independent sizing engine that eliminates multi-pass interpolation blur:
- **Fit Modes**: `CONTAIN` (letterbox/pillarbox), `COVER` (fill with crop), `FILL` (stretch), `CENTER` (1:1 crop).
- `concatenate_affine_matrix()`: Combines Fit Scale, Edit Sizing (Pan/Zoom/Rotate/Anchor), Input Sizing, and dynamic keyframed Dynamic Zoom into a single $3\times3$ transform matrix evaluated in one single resampling pass.

---

## 2.11 End-to-End Frame Lifecycle & Data Flow

```
1. [Scene Definition] ──> Nodes, Background, Camera, SFX & Audio Tracks
       │
2. [Timeline Scheduler] ──> @scene.animate coroutines evaluate AnimationActions & Signals
       │
3. [Per-Frame Dispatch (time=t)]
       ├──> Camera view_matrix() computation (Pan, Zoom, 3D Orbit, Shake)
       ├──> Audio voiceover ducker & sound cues evaluation
       └──> Spatial Hierarchy traversal (local_matrix -> world_matrix)
             │
4. [Vector Rasterization]
       ├──> PyCairo ARGB32 ImageSurface allocation
       ├──> Subpixel drawing of shapes, typography, icons, charts
       ├──> 2.5D Projective quad warping (if 3D tilt angles active)
       └──> Layer masks & alpha group stencil clipping
             │
5. [GPU Post-Processing Passes]
       ├──> Texture upload to ModernGL VRAM
       ├──> 4-Octave Bloom extraction & 13-tap Gaussian blur ping-pong
       ├──> Layer blend modes & track matte shaders
       └──> Viewport shaders: Chromatic aberration, Vignette, Film grain
             │
6. [Color Science Pipeline]
       ├──> Conversion to DaVinci Wide Gamut
       ├──> Primary Lift/Gamma/Gain color grading
       ├──> SDR -> HDR 203-nit Diffuse White scaling (if HDR enabled)
       └──> DaVinci DRT Tone Mapping & ST.2084 PQ encoding
             │
7. [Delivery Output Encoding]
       ├──> FFmpeg pipe (H.264 / ProRes 4444 / WebM Alpha)
       ├──> Fairlight soft-fades & multi-track WAV stem mixing
       └──> Metadata sidecars (Dolby Vision XML / OTIO / FCP XML)
```

---

# 3. Exhaustive Master Component Suites & Shader Catalog (Sections 1–13)

---

## 🔊 Section 1: Procedural Audio & Sound Synthesis (`vibmo.audio.generators`)

Zero-dependency, 48kHz float32 NumPy audio synthesizer generating broadcast-quality UI clicks, cinematic whooshes, sub drops, foley keystrokes, risers, ambient pads, and retro sound effects.

### Class Matrix & Methods

| Suite Class | Key Static Methods | Key Parameters & Defaults | Output Format |
| :--- | :--- | :--- | :--- |
| `WhooshDesignerSuite` | `cinematic_passby`<br>`doppler_whip`<br>`sub_bass_flyby`<br>`airy_transition`<br>`quick_snap_whoosh` | `duration=1.2, speed=1.8, sub_impact=True`<br>`duration=0.35, speed=2.5`<br>`duration=0.75, sub_freq=55.0`<br>`duration=0.50, breath_noise=0.8`<br>`duration=0.18` | Stereo `np.ndarray` (2, N) float32 |
| `CyberUiSuite` / `CyberUISFXSuite` | `holographic_click`<br>`holo_chirp`<br>`data_ping`<br>`toggle_switch`<br>`modal_open_shimmer` | `pitch=800.0, duration=0.05`<br>`duration=0.08, freq_start=1800.0, freq_end=3200.0`<br>`pitch=1200.0, harmonics=3`<br>`state=True`<br>`duration=0.25` | Stereo `np.ndarray` (2, N) float32 |
| `GlitchStutterSuite` | `digital_stutter_burst`<br>`buffer_underrun`<br>`bit_crush_sweep` | `duration=0.8, stutter_rate=16.0`<br>`duration=0.4`<br>`duration=0.6` | Stereo `np.ndarray` (2, N) float32 |
| `ImpactSubSuite` | `cinematic_trailer_sub_drop`<br>`heavy_thud`<br>`sub_boom_reverb` | `decay=2.0, start_freq=110.0, end_freq=32.0`<br>`duration=0.8`<br>`duration=2.5` | Stereo `np.ndarray` (2, N) float32 |
| `KeyboardFoleySuite` | `mechanical_keystroke`<br>`laptop_chiclet_type`<br>`rapid_typing_burst`<br>`spacebar_hit` | `switch="blue"` ("blue", "brown", "red")<br>`None`<br>`word_length=8, wpm=90.0`<br>`switch="blue"` | Stereo `np.ndarray` (2, N) float32 |
| `RiserTensionSuite` | `shepard_tone_riser`<br>`white_noise_riser` | `duration=3.0`<br>`duration=2.5, cutoff_end=12000.0` | Stereo `np.ndarray` (2, N) float32 |
| `AmbientDroneSuite` | `sci_fi_deep_space_drone`<br>`warm_analog_pad` | `duration=10.0`<br>`duration=8.0, root_freq=130.81` | Stereo `np.ndarray` (2, N) float32 |
| `VinylCrackleSuite` | `vintage_turntable_hiss` | `duration=5.0, crackle_density=0.4` | Stereo `np.ndarray` (2, N) float32 |
| `LaserPlasmaSuite` | `plasma_beam_fire` | `duration=0.3, carrier_freq=1800.0` | Stereo `np.ndarray` (2, N) float32 |
| `LiquidBubblesSuite` | `water_bubble_pop` | `bubble_radius_mm=4.5` | Stereo `np.ndarray` (2, N) float32 |
| `PaperCardSuite` | `card_flip_shuffle` | `card_count=6, speed=1.2` | Stereo `np.ndarray` (2, N) float32 |
| `Retro8bitSuite` | `arcade_coin_jump` | `pitch_step=1.4` | Stereo `np.ndarray` (2, N) float32 |
| `AlarmSirenSuite` | `emergency_klaxon_sweep` | `sweep_rate=2.0, duration=3.0` | Stereo `np.ndarray` (2, N) float32 |
| `ChimesHarmonicSuite` | `celestial_wind_chime` | `tines=7, spread=0.5` | Stereo `np.ndarray` (2, N) float32 |
| `CameraShutterSuite` | `dslr_rapid_burst` | `burst_count=3, fps=10.0` | Stereo `np.ndarray` (2, N) float32 |

### Runnable Usage Recipe
```python
from vibmo.agent_api import *

scene = Scene(width=1920, height=1080, fps=60, duration=4.0)

# Generate Procedural 48kHz Sound Effects
whoosh = WhooshDesignerSuite.cinematic_passby(duration=1.2, speed=2.0)
click = CyberUISFXSuite.holographic_click(pitch=900.0)
drop = ImpactSubSuite.cinematic_trailer_sub_drop(decay=1.8)

# Schedule Audio & SFX on Timeline
scene.add_sfx("whoosh", time=0.2)
scene.add_sfx("click", time=1.4)
scene.add_sfx("bass_drop", time=2.2)
```

---

## 🌌 Section 2: Non-Static Animated Backdrops (`vibmo.fx.backgrounds`)

Continuous procedural dynamic backdrops driven by PyCairo canvas and mathematical field equations.

### Class Matrix & Parameters

| Backdrop Class | Constructor Signature & Defaults | Animatable Properties / Signals |
| :--- | :--- | :--- |
| `MeshGradientFlow` | `width=1920.0, height=1080.0, colors=None, speed=1.0, complexity=4` | `colors`, `speed_multiplier` |
| `CyberGridHorizon` | `width=1920, height=1080, grid_color=colors.CYAN, perspective=0.6, speed=1.0, glow=True` | `horizon_pitch`, `scroll_speed`, `glow_intensity` |
| `DigitalMatrixRain` | `density=40, glow_color=colors.EMERALD, speed=1.0, font_size=18` | `speed`, `density`, `glow_color` |
| `FluidCaustics` | `refraction=1.2, speed=0.5, caustic_scale=30.0, deep_water_color=None` | `speed`, `refraction` |
| `TopographicContours` | `line_spacing=24, speed=0.4, line_color=None, elevation_scale=1.5` | `speed`, `line_spacing` |
| `CircuitBoardTraces` | `pulse_speed=1.5, trace_color=colors.CYAN, density=25, junction_nodes=True` | `pulse_speed`, `trace_color` |
| `CosmicNebula` | `swirl_speed=0.2, star_count=120, nebula_palette=None, dust_density=0.6` | `swirl_speed`, `dust_density` |
| `RetroCrtScanlines` | `curvature=0.1, scanline_gap=4, flicker_rate=60, phosphor_mask="rgb"` | `curvature`, `flicker_rate` |
| `SunsetHorizonGlow` | `sun_radius=180, atmospheric_haze=0.3, horizon_y=700, sun_color=None` | `sun_radius`, `horizon_y` |
| `GeometricTessellation` | `poly_type="hexagon", morph_speed=1.0, grid_size=60, edge_glow=True` | `morph_speed`, `grid_size` |
| `BokehLightBubbles` | `bubble_count=35, blur_radius=40, orb_colors=None, speed=0.5` | `speed`, `bubble_count` |
| `HyperspaceTunnel` | `warp_speed=2.5, streak_color=colors.BLUE, tunnel_rings=16` | `warp_speed`, `field_of_view` |
| `MinimalStudioInfinity` | `horizon_y=700, rim_light=True, floor_reflection=0.2, cyclorama_curve=40` | `horizon_y`, `floor_reflection` |
| `IsometricCityGrid` | `building_count=50, pulse_lights=True, isometric_angle=30` | `pulse_lights`, `building_count` |
| `ParticleConstellation` | `particle_count=80, link_radius=120, drift_speed=0.5` | `drift_speed`, `link_radius` |

### Runnable Usage Recipe
```python
from vibmo.agent_api import *

scene = Scene(width=1920, height=1080, fps=60, duration=4.0)

# Cyber Grid Horizon with Glowing Topographic Overlay
grid = CyberGridHorizon(grid_color=colors.CYAN, perspective=0.75, speed=1.2, glow=True)
contours = TopographicContours(line_spacing=32, speed=0.3, line_color=colors.INDIGO.with_alpha(0.35))

scene.add(grid, contours)
```

---

## 💻 Section 3: Hardware Chassis & Device Enclosures (`vibmo.product.hardware`)

Photorealistic mockups with auto-clipping nested screen viewports, physical bezel chamfers, realistic glass reflections, and ambient cast shadows.

### Class Matrix & Specifications

| Chassis Class | Constructor Signature & Defaults | Core Screen Method | Key Features |
| :--- | :--- | :--- | :--- |
| `FoldableDeviceFrame` | `width=600.0, height=500.0, fold_angle=0.0, bezel_width=12.0, corner_radius=32.0` | `add_screen(*nodes)` | Animatable `fold_angle` Signal (0° to 180° book fold), specular hinge crease |
| `RuggedSmartwatchFrame` | `width=380.0, height=460.0, bezel_width=16.0, case_material="titanium"` | `add_screen(*nodes)` | Corner hex bolts, crown dial knob, rubberized strap mockups |
| `SuperUltrawideMonitorFrame` | `width=1600.0, height=450.0, curve_depth=45.0, stand=True` | `add_screen(*nodes)` | 32:9 aspect curve projection, brushed aluminum desk mount stand |
| `PosTerminalFrame` | `width=520.0, height=680.0, tilt_angle=25.0, receipt_slot=True` | `add_screen(*nodes)` | NFC tap glow indicator, thermal receipt printing feeder |
| `CameraViewfinderOverlay` | `width=1920.0, height=1080.0, hud_style="broadcast"` | Top-Level Overlay | Rule-of-thirds grid, battery/ISO dials, pulsing RED REC dot |
| `MinimalistEInkTabletFrame` | `width=640.0, height=860.0, paper_texture=True, pen_dock=True` | `add_screen(*nodes)` | Matte non-reflective screen texture, side magnetic stylus pen |
| `SmartHomeHubFrame` | `width=600.0, height=420.0, stand_tilt=20.0, speaker_fabric=True` | `add_screen(*nodes)` | Acoustic fabric wrapped base, top notification LED ring |
| `RetroArcadeCrtCabinet` | `width=680.0, height=880.0, marquee_text="VIBMO"` | `add_screen(*nodes)` | Backlit marquee, curved 4:3 CRT glass, dual joystick/button control deck |
| `CctvQuadViewOverlay` | `width=1920.0, height=1080.0, timestamp=True` | Quad Multi-Cam | 4-channel security feed grid, animated timestamp ticker, crosshairs |
| `SpatialVisorFrame` | `width=800.0, height=480.0, eye_tracking_glow=True` | `add_screen(*nodes)` | Vision-Pro style curved black glass, woven solo loop knit headband |
| `OledCinemaTvFrame` | `width=1400.0, height=800.0, stand_style="pedestal"` | `add_screen(*nodes)` | Razor-thin bezel, floating shadow, glass pedestal stand |
| `AutomotiveCockpitDash` | `width=1600.0, height=600.0, hud_gauges=True` | `add_screen(*nodes)` | Panoramic curved automotive cluster, dual RPM/Speed tachometers |
| `HandheldGamingConsoleFrame` | `width=1100.0, height=500.0, theme="cyber_neon"` | `add_screen(*nodes)` | Ergonomic left/right joycon grips, D-pad, dual thumbsticks, ABXY buttons |
| `CyberdeckChassisFrame` | `width=960.0, height=620.0, mechanical_switches=True` | `add_screen(*nodes)` | Heavy industrial bumper case, mechanical keyboard keys, patch cables |
| `MultiMonitorDeveloperRig` | `width=1800.0, height=900.0, left_vertical=True` | Multi-Screen | Dual/triple programmer setup with vertical code document monitor |

### Runnable Usage Recipe
```python
from vibmo.agent_api import *

scene = Scene(width=1920, height=1080, fps=60, duration=5.0)

phone = FoldableDeviceFrame(width=620, height=520, fold_angle=30.0, corner_radius=28)
phone.align("center", (1920, 1080))

app_ui = FlexContainer(direction="column", gap=16, padding=24, fill=colors.SLATE_950)
app_ui.add(Text("Vibmo Mobile Studio", font_size=24, bold=True, color=colors.CYAN))
app_ui.add(MetricCounter(start_val=0, end_val=94000, prefix="$", suffix=" Volume", font_size=36, color=colors.EMERALD))

phone.add_screen(app_ui)
scene.add(phone)

@scene.animate
def main():
    yield scene.all(
        phone.pop_in(duration=0.8),
        phone.fold_angle.to(0.0, duration=1.5, ease=Ease.out_expo),
    )
```

---

## 🤖 Section 4: AI & SaaS Interactive UI Suites (`vibmo.product.ai`)

Specialized interactive components engineered for AI products, developer platforms, SaaS product demos, and cloud services.

### Class Matrix & Methods

| Suite Component | Constructor Signature & Defaults | Primary Animation Methods |
| :--- | :--- | :--- |
| `StreamingTokenOutput` | `text="...", speed=30.0, width=650.0, height=360.0, font_size=16.0, bg_color="#0b101b", show_cursor=True` | `stream_tokens(speed=None, duration=None, ease=Ease.linear)`<br>`stream_text(text=None, duration=None)` |
| `TreeOfThoughtTree` | `branches=None, width=800.0, height=500.0, depth=3` | `expand_branch(index: int, duration=0.8)`<br>`prune_branch(index: int)`<br>`highlight_solution_path(path_indices)` |
| `DiffusionCanvas` | `width=512.0, height=512.0, steps=20, prompt="..."` | `denoise_steps(steps=20, duration=2.0)`<br>`reveal_latent(duration=1.2)` |
| `AgentTeamThread` | `width=720.0, height=480.0, agents=["Coder", "Architect", "Critic"]` | `post_agent_message(agent_name, message, duration=0.8)`<br>`show_tool_call(tool_name, payload)` |
| `VectorEmbeddingsVisualizer` | `dimension=3, point_count=120, cluster_count=4` | `rotate_cluster(yaw=45, pitch=30, duration=2.0)` |
| `PricingTierMatrix` | `tiers=None, highlight_index=1, width=960.0` | `highlight_tier(tier_name="Pro", duration=0.6)` |
| `ApiKeyVault` | `keys=None, width=600.0, height=340.0` | `reveal_key(index=1, duration=0.5)` |
| `GitPrTimeline` | `pr_number=88, title="...", author="vibmo"` | `animate_merge(duration=1.2)` |
| `TelemetryDialHUD` | `metrics=None, width=840.0, height=320.0` | `set_metric(name="CPU", target_val=88.5, duration=0.8)` |
| `VisualSqlQueryBuilder` | `tables=None, width=900.0, height=500.0` | `draw_join_relation(source_tbl, target_tbl, duration=1.0)` |
| `WebhookActivityFeed` | `width=640.0, height=400.0, max_items=6` | `simulate_event(event_name="payment.succeeded", duration=0.5)` |
| `TokenQuotaMeter` | `total=1000000, current=0, unit="tokens"` | `consume(tokens=250000, duration=1.2)` |
| `CodeSandboxPlayground` | `code="...", language="python", show_console=True` | `run_execution(duration=1.5)` |
| `FeatureComparisonMatrix` | `features=None, competitors=None, width=900.0` | `reveal_rows(duration=1.8, stagger=0.15)` |
| `PromptDiffViewer` | `v1="...", v2="...", width=880.0` | `highlight_diffs(duration=1.0)` |
| `AiPromptFlow` | `prompt_text="...", model_name="Claude 3.7"` | `type_prompt(duration=1.2)` |
| `ClaudeCodeSimulator` | `title="bash", theme="dark"` | `add_command("pip install vibmo").add_output("Installed ✓")` |
| `InteractiveCheckoutFlow` | `amount="$99/yr", plan_name="Pro Plan"` | `trigger_payment(duration=1.0)` |
| `XFollowCard` | `name="Vibmo", handle="@vibmo_ai", avatar=None` | `click_follow(duration=0.4)` |
| `InfiniteBentoPan` | `cards=None, width=1920.0, height=1080.0` | `pan_camera(offset=(100, 50), duration=2.0)` |

### Runnable Usage Recipe
```python
from vibmo.agent_api import *

scene = Scene(width=1920, height=1080, fps=60, duration=5.0)

streamer = StreamingTokenOutput(
    text="Analyzing neural weights... Optimized 60 FPS motion graphics compiled.",
    speed=35.0,
    width=600,
    height=400,
)
streamer.align("center", (1920, 1080))
scene.add(streamer)

@scene.animate
def main():
    yield streamer.pop_in(duration=0.6)
    yield streamer.stream_tokens(speed=40.0)
```

---

## 📈 Section 5: Financial, 3D Spatial & Motion Charts (`vibmo.charts`)

Precision data visualization engine with animated coordinate systems, smooth bezier curves, and statistical distributions.

### Class Matrix & Animation Verbs

| Chart Class | Key Constructor Arguments | Key Animation Methods |
| :--- | :--- | :--- |
| `CandlestickChartPro` | `ohlc_data: List[Dict], width=800.0, height=400.0` | `draw_bars(duration=1.5, delay=0.0, ease=Ease.out_expo)` |
| `RadialSunburstHierarchy` | `tree_data: Dict, radius=300.0, levels=3` | `expand_rings(duration=1.8)`, `highlight_sector(path)` |
| `SpeedometerHudDial` | `min_val=0, max_val=220, unit="MPH", current_val=0` | `needle_to(target_val=140, duration=1.2)` |
| `SurfaceMesh3DPlot` | `fn=Callable, grid_res=32, elevation_scale=100.0` | `rotate_3d(yaw=45, pitch=30, duration=2.0)` |
| `BubbleScatter4DPlot` | `points: List[Tuple], radius_range=(4, 32)` | `grow_bubbles(duration=1.4)`, `highlight_quadrant(1)` |
| `WaterfallFinancialChart` | `steps: List[Tuple[str, float]], base_val=0` | `reveal_steps(duration=1.6, stagger=0.15)` |
| `ChoroplethGeoMap` | `regions: Dict[str, float], color_scale="viridis"` | `animate_heat_gradient(duration=1.5)` |
| `ViolinDensityPlot` | `distributions: List[List[float]], kde_bandwidth=0.2` | `expand_kde(duration=1.2)` |
| `MarketCapTreemap` | `stocks: List[Dict], width=900.0, height=500.0` | `zoom_sector(sector_name="Tech", duration=1.0)` |
| `SankeyFlowDiagram` | `links: List[Tuple[str, str, float]], width=800.0` | `animate_flow_current(duration=2.0)` |
| `OrganicWaveStreamgraph` | `series: List[List[float]], tension=0.4` | `undulate_stream(duration=3.0)` |
| `PolarRoseCoxcombChart` | `sectors: List[float], max_radius=250.0` | `bloom_wedges(duration=1.5)` |
| `BoxAndWhiskerPlot` | `datasets: List[Dict], show_outliers=True` | `extend_whiskers(duration=1.0)` |
| `ParetoAnalysisChart` | `categories: List[str], values: List[float]` | `draw_80_20_cutoff(duration=1.8)` |

### Runnable Usage Recipe
```python
from vibmo.agent_api import *

scene = Scene(width=1920, height=1080, fps=60, duration=5.0)

ohlc = [
    {"open": 100, "high": 120, "low": 95, "close": 115},
    {"open": 115, "high": 130, "low": 110, "close": 125},
    {"open": 125, "high": 128, "low": 102, "close": 105},
    {"open": 105, "high": 140, "low": 104, "close": 138},
]
chart = CandlestickChartPro(ohlc_data=ohlc, width=1000, height=500)
chart.align("center", (1920, 1080))
scene.add(chart)

@scene.animate
def main():
    yield chart.draw_bars(duration=2.0, ease=Ease.out_expo)
```

---

## ✍️ Section 6: Kinetic Typography & Title Sequences (`vibmo.typography.kinetic`)

Per-glyph animated typography engine with shader refractions, particle embers, and kinetic reveals.

### Class Matrix & Signatures

| Typography Class | Constructor Signature & Defaults | Primary Animation Method |
| :--- | :--- | :--- |
| `GlitchDecryptorText` | `text: str, font_size=48.0, color=colors.CYAN, scramble_pool="0123456789ABCDEF"` | `decrypt(duration=1.8, delay=0.0)` |
| `LiquidWaveText` | `text: str, wave_freq=3.0, amplitude=12.0, color=colors.BLUE` | `ripple_reveal(duration=1.5)` |
| `IsometricExtruded3DText` | `text: str, depth=35.0, angle_deg=30.0, light_angle=45.0` | `gleam(duration=1.2)` |
| `RealisticNeonStrobeSign` | `text: str, color=colors.CYAN, tube_radius=4.0, flicker_chance=0.2` | `ignite(duration=1.0)` |
| `ParticleFlameText` | `text: str, particle_count=200, ember_color=colors.ORANGE` | `disintegrate(duration=2.0)` |
| `SplitFlapAirportBoard` | `rows=3, cols=16, flap_speed=20.0, bg_color="#18181b"` | `flip_to(lines=["SAN FRANCISCO", "GATE B24"])` |
| `MatrixRainTypography` | `text: str, font_size=36.0, trail_decay=0.85` | `consolidate(duration=2.2)` |
| `SlitScanVideoSynthText` | `text: str, scan_bands=16, feedback_gain=0.7` | `warp_scan(duration=1.8)` |
| `OdometerTumblerCounter` | `start_val=0, end_val=9999, tumbler_height=60.0` | `roll_to(8420, duration=2.0)` |
| `RubberStampTitleSlam` | `text="APPROVED", color=colors.ROSE, slam_scale=3.0` | `slam(duration=0.6)` |
| `MagneticGravityLetters` | `text: str, scatter_radius=300.0, magnet_pull=1.5` | `snap_reassemble(duration=1.4)` |
| `HologramChromaText` | `text: str, fringe_lines=True, chromatic_shift=6.0` | `project_emitter(duration=1.5)` |
| `PhosphorTerminalTypewriter`| `prompt="user@vibmo:~$ ", type_speed=0.04` | `typewriter("deploy --prod")` |
| `BrushCalligraphyPathReveal`| `text: str, stroke_width=6.0, splatter_bleed=True` | `draw_strokes(duration=2.0)` |
| `ElasticSquashBounceTitle` | `text="POW!", squash_factor=1.4, bounce_count=3` | `bounce_in(duration=1.0)` |
| `BlurOutUpText` | `text: str, blur_amount=24.0, travel_y=-80.0` | `blur_out_up(duration=0.8)` |
| `MatrixDecodeText` | `text: str, decode_duration=1.8` | `decode(duration=1.8)` |
| `RollingNumberWheel` | `start_val=0, end_val=5000, font_size=64.0` | `roll_to(4200, duration=1.6)` |
| `InlinePillTakeoverText` | `pill_text="zero boilerplate", original_text="..."` | `expand_pill(duration=1.0)` |

### Runnable Usage Recipe
```python
from vibmo.agent_api import *

scene = Scene(width=1920, height=1080, fps=60, duration=4.0)

title = GlitchDecryptorText("QUANTUM SECURE", font_size=52, color=colors.CYAN)
title.align("center", (1920, 1080))
scene.add(title)

@scene.animate
def main():
    yield title.decrypt(duration=1.8)
```

---

## 🔮 Section 7: Visual Post-FX Shaders & Turnkey Production Suites (`vibmo.fx.shaders`, `vibmo.templates`)

### Viewport Shaders (`vibmo.fx.shaders`)
- `CrtPhosphorBloomShader(intensity=0.5, radius=5.0, aperture_grille=True)`: Phosphor RGB triads with optical glass curve.
- `VhsTapeTrackingShader(noise=0.15, tracking_error=0.08, head_switch_jitter=True)`: VHS tape scan jitter and tape tear.
- `AnamorphicStreakFlare(threshold=0.8, streak_length=600, blue_tint=True)`: Hollywood horizontal anamorphic lens streak.
- `LiquidGlassRefractionFilter(refraction=0.3, chromatic_dispersion=0.05)`: Optical frosted glass distortion.
- `AsciiMatrixArtFilter(char_size=12, green_phosphor=True)`: Real-time luminance-mapped ASCII matrix console.
- `AsciiRenderFilter(glyph_size=16, ink="#00ff00")`: Full-viewport terminal character conversion.
- `SecurityCamOverlay(camera_name="CAM 01 // LOBBY", show_rec=True)`: CCTV telemetry overlay.
- `ShaderNeuroNoise(speed=0.8, color_core=(14, 165, 233))`: Procedural GLSL simplex/perlin plasma backdrop.
- `UnderwaterRippleFilter(frequency=0.02, amplitude=8.0)`: Caustic water wave displacement.

### Turnkey Production Template Suites (`vibmo.templates.turnkey`)
- `TmplAiCodeAssistantSuite.build_scene(prompt="Build a SaaS in Python", duration=6.0)`: IDE code editor + token streamer + celebration metric counter.
- `TmplFintechCryptoCardSuite.build_scene(cardholder="SATOSHI NAKAMOTO", balance="$1,250,000")`: 3D embossed glass credit card with holographic chip.
- `TmplSaasYcPitchSuite.build_scene(mrr="$120k", growth="+40%")`: High-stakes Y-Combinator SaaS deck launch video.
- `TmplSocialAudiogramSuite.build_scene(audio="podcast.mp3", title="The Future of AI")`: Waveform visualizer + kinetic captions + avatar ring.
- `TmplDeveloperCliLaunchSuite.build_scene(tool_name="vibmo", command="vibmo render")`: Interactive terminal launch video.

---

## 🧠 Section 8: Quality Gates, Developer UI & Intelligent Video Post (`vibmo.quality`, `vibmo.components`, `vibmo.rigging`, `vibmo.video_post`)

### Quality Gates (`vibmo.quality`)
- `SlideshowRiskScorer.evaluate(scenes)`: Analyzes 6 dimensions (`repetition`, `decorative_visuals`, `weak_motion`, `weak_shot_intent`, `typography_overreliance`, `unsupported_cinematic_claims`) to prevent static slide deck output. Verdicts: `"strong"`, `"acceptable"`, `"revise"`, `"fail"`.
- `ScenePacingVerifier.verify_alignment(steps, scene_start, scene_end, narration_cues)`: Prevents dead air and narration mismatch.
- `AntiSlopValidator.evaluate_scene(scene)`: Flags generic low-effort AI motion slop.
- `AestheticCaseLawValidator.evaluate_scene(scene)`: Enforces production-grade typography contrast, aspect bounds, and pacing.
- `VideoReplicaVerifier.evaluate_three_gates(result)`: 3-gate frame-level replica fidelity verifier (`structural_alignment`, `temporal_pacing`, `chromatic_fidelity`).

### Developer UI Components (`vibmo.components`)
- `TerminalWindow(title="bash", prompt="user@vibmo:~$ ", steps=[...])`:
  - `add_command("npm run build")`, `add_output("Build succeeded")`, `add_pause(0.5)`, `add_pill("✓ Ready")`.
- `CodeCard(code="import vibmo\nscene = Scene()", theme="dracula", title="app.py")`
- `CodeWindow(code="...", font_size=20, width=640, height=670)`
- `DiagramNode()`: Flowchart builder with `.add_box(id, label).connect(id1, id2)`.
- `GlassCard(direction="column", gap=16, padding=32, corner_radius=24)`: Frosted glass container with specular rim and drop shadows.
- `MetricCounter(start_val=0, end_val=250000, prefix="$", suffix=" MRR")`: Smooth ease-animated odometer number ticker.

### 2D Kinematic Rigging & Intelligent Video Post (`vibmo.rigging`, `vibmo.video_post`)
- `FabrikSolver2D`: 2D Forward And Backward Reaching Inverse Kinematics solver.
- `MocapStickFigure(action="dance")`: Kinematic rigged 2D figure with `.reach_left(target_pos)`, `.step_forward()`.
- `AutoReframe.reframe_video(input_path, output_path, target_aspect="portrait")`: Saliency-based subject tracking auto-crop.
- `SilenceCutter.detect_silence(audio_path, silence_threshold_db=-35)`: Automatic dead-air removal.
- `AudioEnergyAnalyzer.analyze("soundtrack.mp3")`: Detects rhythmic drops, peak transients, and BPM.
- `ColorHarmonizer.evaluate_contrast(fg_hex, bg_hex)`: WCAG 2.1 AAA contrast checker.

---

## 🚀 Section 9: HDR, Color Science & Resolution Independence (`vibmo.color`, `vibmo.core`, `vibmo.render.cache`)

- `RCMPipeline`: Scene-referred 32-bit float color transforms from `Rec.709`, `sRGB`, `Rec.2020`, `DCI-P3`, `ACEScg` to DaVinci Wide Gamut (DWG).
- `sdr_to_hdr_diffuse_white(rgb, target_nits=203.0)`: Maps 100-nit SDR motion graphics to BT.2408 HDR 203-nit target.
- `apply_drt_tone_mapping(rgb_linear, mode=DRTMode.DAVINCI, peak_nits=1000.0)`.
- `DolbyVisionAnalyzer.analyze_frame(rgb_linear_nits)`: Computes MinPQ, MaxPQ, AvgPQ (APL), and MaxFALL.
- `MultiMasterTrimManager`: Simultaneous mastering for 4000-nit HDR, 1000-nit OLED, and 100-nit SDR Rec.709 targets.
- `SizingPipeline.concatenate_affine_matrix()`: Single-pass 3x3 matrix multiplication on raw source pixels, eliminating intermediate resampling blur.
- `FairlightAudioEngine.apply_soft_fades()`: Equal-power 1.5ms crossfade at cut boundaries.
- `HierarchicalRenderCache`: 3-Tier cache for Source Fusion, Node Graph, and Sequence Timeline.

---

## 🎨 Section 10 & 11: Remocn-Inspired Motion Graphics & 6-Beat Video Spine (`vibmo.templates`, `vibmo.composition`)

### 6-Beat SaaS Product Demo Spine (`TmplSaasProductDemoSpineSuite`, `ProductDemoSpine`)
Structured 6-beat launch narrative:
1. **The Hook** (0.0s - 1.5s): Problem statement & kinetic punch.
2. **The Bottleneck** (1.5s - 3.0s): Friction demonstration.
3. **The Reveal** (3.0s - 4.5s): Hero product chassis entrance.
4. **The Feature Sprint** (4.5s - 7.0s): Rapid 3-feature choreography.
5. **The Social Proof** (7.0s - 8.5s): Metric counter & customer logos.
6. **The CTA Outro** (8.5s - 10.0s): Brand logo reveal & website URL.

### Remocn Camera Transitions (`vibmo.composition.transitions_remocn`)
- `PushThroughTransition(max_scale=3.0, blur=True, duration=0.55)`: Plunges camera forward through the incoming canvas with radial motion blur.
- `FocusPullTransition(max_blur=24.0, duration=0.60)`: Cinematic rack focus depth-of-field transition.
- `WhipPanTransition(direction="right", speed=2.5)`: High-velocity motion-blurred camera whip.
- `DitherDissolveTransition(dither_matrix="bayer8x8", duration=0.45)`: Retro pixel-dissolve matrix transition.

---

## 🎬 Section 12 & 13: Video-Shotcraft Staging, Beat-Sync & Dark Magic UI (`vibmo.product.shotcraft`, `vibmo.product.magic_ui`, `vibmo.ai`)

| Suite Class | Description & Key Methods | Usage Recipe |
| :--- | :--- | :--- |
| `DeckDealFlyIn` | Physical card deck dealing animation with spring fan-out | `deck = DeckDealFlyIn(cards=[...]); yield deck.deal_cards(); yield deck.fan_out()` |
| `DocParkPillDeal` | Document docking to left margin while dealing interactive action pills | `doc = DocParkPillDeal(doc_title="Research"); yield doc.dock_left(); yield doc.deal_pills()` |
| `SpotlightHeroCard` | Dark brushed metal ground floor with volumetric light cone | `hero = SpotlightHeroCard(title="Core Engine"); yield hero.ignite_spotlight()` |
| `DarkMetallicFloor` | Elliptical specular floor pool with realistic ambient roll-off | `floor = DarkMetallicFloor(floor_y=620.0, light_color=colors.CYAN)` |
| `AutolayoutGapDial` | Interactive flexbox padding/gap expansion dial | `dial = AutolayoutGapDial(block_labels=["A", "B", "C"]); yield dial.expand_gap(48.0)` |
| `ChipGridSelectBlackout`| Grid item selection with dramatic background blackout | `chips = ChipGridSelectBlackout(options=["A", "B"]); yield chips.trigger_select()` |
| `AvatarBracketCarousel`| Orbiting user roles carousel with bracket selection | `bracket = AvatarBracketCarousel(roles=["Coder", "Architect"]); yield bracket.cycle_to(1.0)` |
| `BezierSourceConvergeMerge`| Bezier convergence merging multiple pipelines into one | `merge = BezierSourceConvergeMerge(sources=["PRs", "DB"]); yield merge.animate_flow()` |
| `OutroGroupPhotoLaunch`| Keynote family portrait outro launching all active widgets | `outro = OutroGroupPhotoLaunch(brand_name="Vibmo"); yield outro.launch_family_portrait()` |
| `BeatCutAccelerando` | Accelerating rhythmic cuts aligned to musical beats | `cuts = BeatCutAccelerando(cut_labels=["CUT 1", "CUT 2"]); yield cuts.step_cut(1)` |
| `BeatSyncGrid` | 120-140 BPM musical transient quantization grid | `grid = BeatSyncGrid(bpm=126.0); sfx = TimelineSFXTable(grid); sfx.add_cue("whoosh", target_beat=4.0)` |
| `JianYingDraftExporter`| Exports native CapCut / JianYing project JSON drafts | `exporter = JianYingDraftExporter(); exporter.add_video_segment("Hero", 0, 120); exporter.export_to_file("draft.json")` |
| `DarkStarfieldStage` | Deep purple / violet cosmic dust stage with horizon glow | `scene.add(DarkStarfieldStage(particle_count=65, horizon_color="#7c3aed"))` |
| `PromptInvocationCard`| Glass prompt pill with token typing and magical glow border | `card = PromptInvocationCard(prompt_text="Build AI video"); yield card.type_prompt()` |
| `ModelCapabilityOrbit`| Radial orbiting model capability nodes (Claude, GPT, Llama) | `orbit = ModelCapabilityOrbit(models=["Claude 3.7", "GPT-4o"]); yield orbit.rotate_orbit()` |
| `AntiPptGate` | AI Meta-Director thesis evaluator validating motion hierarchy | `thesis = MotionThesis("river", "stream", "network", "speed"); graph = BeatGraph(thesis); graph.add_beat(0.0, 1.5, "hook", "data", "scattered", "flowing", "stream"); report = AntiPptGate.evaluate_beat_graph(graph)` |

---

# 4. Developer Tooling & CLI Suite

---

## 4.1 Complete 15-Subcommand CLI Matrix

The CLI is registered in `pyproject.toml` via `[project.scripts] vibmo = "vibmo.cli.main:cli"`.

```
                  ┌───────────────────────────────────────────────┐
                  │                 vibmo (CLI)                   │
                  └───────┬───────────────────────────────┬───────┘
                          │                               │
       ┌──────────────────┼──────────────────┐            │
       ▼                  ▼                  ▼            ▼
 ┌───────────┐      ┌───────────┐      ┌───────────┐ ┌───────────┐
 │ vibmo ai  │      │vibmo render│     │vibmo studio││vibmo mcp  │
 └───────────┘      └───────────┘      └───────────┘ └───────────┘
       │                  │                  │            │
       ▼                  ▼                  ▼            ▼
 Autonomous &      Multi-Core FFmpeg    FastAPI + WS    JSON-RPC 2.0
 Surgical LLM      Pipe Video Engine   Interactive NLE  Stdio Agent Server
 Pipeline          (MP4/ProRes/WebM)   Workstation     (11 Tools)
```

| Subcommand | Syntax / Key Arguments | Options & Flags | Execution Flow & Handlers | Exit Codes & Output |
| :--- | :--- | :--- | :--- | :--- |
| `vibmo ai` | `[prompt]` | `--edit <path>`<br>`-o, --output <path>` (default: `ai_output.mp4`)<br>`--chat` (interactive terminal)<br>`--provider <name>` (`openai`, `anthropic`, `gemini`, `groq`, `openrouter`) | 1. If `--chat`: enters interactive REPL using `get_global_memory()` and `run_motion_edit()`.<br>2. If `--edit`: reads existing script, applies AST surgical modifications via `run_motion_edit()`, rewrites file.<br>3. Else: triggers `AutonomousPipeline.generate_and_render()` with quality preset. | `0` on success, `1` on invalid prompt/script. Rich panel report. |
| `vibmo inspect` | `<script>` | None | 1. Loads runnable from script using `_load_runnable_from_file()`.<br>2. Displays Rich Table: Resolution, FPS, Duration, Background.<br>3. Generates Rich `Tree` of scene root hierarchy with class names, positions, opacities.<br>4. Lists Post-FX shaders.<br>5. Executes `runnable.validate()` and outputs diagnostics. | `0` on success, `1` if script missing or no scene found. |
| `vibmo watch` | `<script>` | `--studio` (auto-launch Web Studio)<br>`--port <int>` (default: 8000) | 1. If `--studio`: delegates to `launch_studio(script_path=script, port=port)`.<br>2. Else: runs 0.5s polling loop on `os.path.getmtime(abs_path)`. On modification, re-executes script, re-validates, and regenerates `storyboard_live.png`. | Runs continuously until `KeyboardInterrupt`. |
| `vibmo create` | `<template> [name]` | Choices: `saas_launch`, `app_demo`, `tech_intro` | 1. Queries `vibmo.templates.catalog.TEMPLATES`.<br>2. Creates directory structure: `assets/`, `fonts/`, `renders/`, `storyboard/`.<br>3. Writes `project.py` with template source code.<br>4. Generates `vibmo.toml` project manifest. | `0` on creation, `1` if target directory already exists. |
| `vibmo templates`| None | None | Iterates over `vibmo.templates.catalog.TEMPLATES` and prints template IDs and descriptions to stdout. | `0` |
| `vibmo init` | `<name>` | None | Scaffolds standard project folder with starter `BrowserWindow`, `GlassCard`, `MetricCounter`, `KineticText`, `vibmo.toml`, and subdirectories (`assets/`, `fonts/`, `scenes/`, `renders/`, `storyboard/`). | `0` on creation, `1` if directory exists. |
| `vibmo render` | `<script>` | `-o, --output <path>` (default: `output.mp4`)<br>`-q, --quality` (`draft`, `fast`, `high`, `4k`)<br>`-p, --preset` (`mp4`, `webm`, `prores`, `gif`, `instagram-reel`, `tiktok`, `youtube-short`, `twitter`, `linkedin`)<br>`--props <json/file>`<br>`--resume` (resume from cache)<br>`--motion-blur` (enable sub-frame blur) | 1. Loads `Scene` or `Sequence`.<br>2. Parses runtime props (JSON string or file) into `scene.props`.<br>3. Adjusts aspect ratio if social presets are passed (e.g. 1080x1920 for `instagram-reel`/`tiktok`).<br>4. Dispatches to `runnable.render(...)` via `Pipeline`. | `0` on render completion, `1` on error. |
| `vibmo storyboard`| `<script>` | `-o, --output <path>` (default: `storyboard.png`)<br>`--props <json/file>`<br>`--rows <int>` (default: 2)<br>`--cols <int>` (default: 3) | 1. Loads `Scene` or `Sequence`.<br>2. Injects runtime data props.<br>3. Dispatches to `runnable.storyboard(path, rows, cols)`. | `0` on generation, `1` on error. |
| `vibmo studio`<br>(alias: `preview`) | `[script]` | `--port <int>` (default: 8000) | Initializes FastAPI server via `create_studio_app(script_path=script)`, opens default web browser at `http://127.0.0.1:<port>`, and starts `uvicorn.run()`. | Blocks on Uvicorn server loop. |
| `vibmo schema` | None | `--format` (`openai`, `anthropic`, `gemini`, `json`) | Calls `vibmo.ai.schema.export_llm_tool_definitions(format)` and prints serialized JSON tool schema. | `0` |
| `vibmo mcp` | None | None | Starts Model Context Protocol stdio server (`MCPServer.run_stdio()`). Suppresses banner output to maintain JSON-RPC protocol purity. | Stdio event loop. |
| `vibmo desktop` | `[project]` | None | Initializes PySide6 desktop workstation application via `vibmo.desktop.app.launch_desktop_studio()`. | Returns Qt application exit code. |
| `vibmo package` | `<script>` | `-o, --output <path>`<br>`--no-assets`<br>`--no-preview` | Calls `ProjectArchive.package()`, bundles script, `assets/`, `fonts/`, `luts/`, and preview image into compressed `.vibmo` zip archive container with `manifest.json`. | `0` on success, outputs archive metadata. |
| `vibmo unpackage`| `<archive>` | `-d, --dest <path>` | Extracts `.vibmo` archive container via `ProjectArchive.unpackage()`, restores script and dependency assets. | `0` on extraction. |
| `vibmo doctor` | None | None | Executes comprehensive diagnostic suite: Python runtime version, PyCairo vector backend, NumPy/SciPy math libraries, FFmpeg binary existence and version check, Headless Chrome/Edge browser detection, ModernGL GPU shader acceleration, and configured AI provider API keys. | `0` |

---

## 4.2 Script Ingestion & Dynamic Resolution Engine

To allow zero-boilerplate authoring, `vibmo/cli/main.py:43-86` dynamically loads user Python scripts without requiring hardcoded class names or entrypoint functions:
1. **Dynamic Import**: Loads module via `importlib.util.spec_from_file_location("user_vibmo_script", abs_path)`.
2. **Priority 1**: Searches for an instantiated `Scene` or `Sequence` object assigned to the variable `scene` or having populated `nodes`.
3. **Priority 2**: Identifies any generic `Scene` or `Sequence` instance in module namespace.
4. **Priority 3**: Discovers and executes factory functions matching keywords (`create*`, `build*`, `make*`, `get_scene*`, `demo*`).

---

## 4.3 `.vibmo` Project Archive Container Specification

The `.vibmo` package format is an open container format (ZIP archive) inspired by DaVinci Resolve `.dra` project archives.

```
my_project.vibmo (ZIP Container)
├── manifest.json            # Version, entrypoint, timestamp, asset manifest
├── preview.png              # 6-frame storyboard contact sheet
├── src/
│   └── project.py           # Main Python motion graphics script
├── assets/                  # Bundled image and video plates
│   └── logo.png
├── fonts/                   # Bundled custom typography fonts (.ttf, .otf)
└── luts/                    # Bundled 3D LUT color tables (.cube)
```

**Manifest Structure (`manifest.json`)**:
```json
{
  "version": "2.0.0",
  "format": "vibmo_project_archive",
  "entry_script": "project.py",
  "created_at": "1725123456.78",
  "assets": [
    "assets/logo.png",
    "fonts/Inter-Bold.ttf"
  ],
  "extra_files": [],
  "has_preview": true
}
```

---

## 4.4 System Diagnostics (`vibmo doctor`)

`vibmo doctor` verifies all operational dependencies:
- **Python Runtime**: Python >= 3.10 verification.
- **PyCairo Subpixel Vector Backend**: Surface creation and subpixel text rendering tests.
- **NumPy & SciPy**: Vector math and FFT signal processing verification.
- **FFmpeg Binary**: Path resolution, version string check, codec support (`libx264`, `libvpx-vp9`, `prores_ks`, `aac`, `pcm_s16le`).
- **ModernGL GPU Engine**: Headless OpenGL 3.3 context initialization and shader compilation tests.
- **AI Provider Configuration**: Validates API keys for OpenAI, Anthropic, Gemini, Groq, and OpenRouter.

---

# 5. Web Studio Pro Architecture

---

## 5.1 Full Client-Server Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                   Web Studio Pro                                       │
│                                                                                        │
│ ┌───────────────────────────────────────┐  ┌─────────────────────────────────────────┐ │
│ │          Client Frontend              │  │             Backend Server              │ │
│ │  (HTML5 / Canvas / Vanilla JS / CSS)  │  │          (FastAPI / Uvicorn)            │ │
│ ├───────────────────────────────────────┤  ├─────────────────────────────────────────┤ │
│ │ • 5 Workspace Pages:                  │  │ • REST APIs:                            │ │
│ │   - Motion (NLE Dual Timeline)        │  │   - /api/meta, /api/script, /api/fusion │ │
│ │   - Fusion (Node Compositing Graph)   │  │   - /api/waveform, /api/sfx, /api/ai    │ │
│ │   - Color (Lift/Gamma/Gain Wheels)    │  │   - /api/render/queue (Batch Worker)    │ │
│ │   - Fairlight (Audio & Soundboard)    │  │ • WebSocket (/ws):                      │ │
│ │   - Deliver (Export Presets & Queue)  │  │   - Frame Streaming (Base64 JPEG)       │ │
│ │ • Subsystems:                         │  │   - Scene Property Live Mutation        │ │
│ │   - StudioSocket (Backpressure Queue) │  │ • FrameServer:                          │ │
│ │   - StudioViewport (Transform Gizmos) │  │   - Multi-Tier In-Memory Frame Cache    │ │
│ │   - SplineEditor (Bézier Handle UI)   │  │   - Background Timeline Prewarmer       │ │
│ │   - ScriptEditorManager (Python IDE)  │  │ • AudioServer:                          │ │
│ │   - AiDirectorModal (LangGraph Agent) │  │   - Procedural SFX & 400-pt Waveform    │ │
│ └───────────────────────────────────────┘  └─────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 5.2 FastAPI REST API & WebSocket Protocol (`/ws`)

### WebSocket Message Protocol (`/ws`)

| Inbound Message (Client -> Server) | Payload Parameters | Server Action & Response |
| :--- | :--- | :--- |
| `{"type": "init"}` | None | Dispatches `{"type": "meta", ...}` with complete scene metadata. |
| `{"type": "get_frame"}` | `time`: float, `scale`: float, `quality`: int | Calls `frame_server.get_frame_base64()`, returns `{"type": "frame", "time": t, "image": "<base64>"}`. |
| `{"type": "run_script"}` | `code`: string | Executes Python script, updates `FrameServer`/`AudioServer`, broadcasts metadata. |
| `{"type": "set_param"}` | `name`: string, `value`: any | Updates `scene.params[name]`, clears frame cache, responds `{"type": "param_updated"}`. |
| `{"type": "set_node_prop"}` | `node_id`: string, `prop`: string, `value`: any | Mutates layer transform, clears frame cache. |
| `{"type": "set_color_grade"}` | `lift`, `gamma`, `gain`, `exposure`, `contrast`, `saturation`, `temperature`, `tint` | Updates `ColorCorrection` shader filter, clears frame cache, responds `{"type": "color_grade_updated"}`. |
| `{"type": "start_render"}` | `preset`: string | Spawns background thread running `scene.render()`, returns `{"type": "render_started"}`. |

**Client-Side Backpressure (`StudioSocket` in `socket.js`)**:
The client maintains an `inFlight` semaphore. When the user scrubs rapidly, intermediate frame requests are coalesced into `pendingTime`. Only the latest frame is requested upon server response, preventing network queue congestion.

### Comprehensive REST API Endpoints

```
/ (GET)                           -> HTML5 Studio Single Page Application
/api/meta (GET)                   -> Scene configuration, layer bounds, SFX cues, parameters
/api/script (GET)                 -> Current Python code and disk file path
/api/script/run (POST)            -> Compiles and hot-reloads Python script
/api/script/save (POST)           -> Writes current script to disk
/api/templates (GET)              -> Available starter templates (SaaS, Kinetic, KPI, Canvas)
/api/prompt/generate (POST)       -> Synthesizes scene from natural language prompt
/api/audio (GET)                  -> Streams master WAV/MP3 audio track
/api/waveform (GET)               -> 400-point normalized peak array and timeline duration
/api/sfx/play/{sound_name} (GET)  -> Synthesizes and returns procedural SFX WAV buffer
/api/fusion (GET)                 -> Serialized node graph (generators, layers, shaders, media out)
/api/soundboard (GET)             -> Fairlight soundboard preset metadata
/api/presets (GET)                -> Export presets (1080p, 9:16 Reel, 1:1 Square, Alpha, 4K ProRes)
/api/render/queue (GET)           -> Active render jobs in batch queue
/api/render/queue/add (POST)      -> Enqueues export job
/api/render/queue/{id} (DELETE)   -> Cancels/deletes queued job
/api/render/queue/start_batch (POST) -> Launches background thread rendering all queued jobs
/api/export_code (GET)            -> Generated Python code overrides
/api/settings/keys (GET, POST)    -> AI provider API key configuration & validation
/api/ai/history (GET, POST)       -> LangGraph conversation memory management
/api/ai/edit (POST)               -> Surgical scene modification via LangGraph state machine
/api/ai/generate (POST)           -> Full sequence AI generation
/api/ai/stream (POST)             -> SSE stream for real-time AI code tokens
```

---

## 5.3 High-Speed Multi-Tier Frame Server & Prewarmer

- **In-Memory Cache**: Stores rendered frames indexed by `(scale_percent, frame_index) -> base64_jpeg`.
- **Thread Safety**: Uses separate `_lock` (cache read/write) and `_render_lock` (rasterizer invocation) to prevent concurrent frame race conditions during scrub.
- **Timeline Prewarmer (`prewarm_timeline`)**: Spawns a low-priority background thread to pre-render the full timeline at 50% scale, sleeping 10ms between frames to yield CPU to interactive playback requests.
- **Crash-Proof Fallback**: If an unhandled rasterizer exception occurs, the server returns the last valid cached frame or a solid dark fallback canvas (`rgb(11, 17, 32)`).

---

## 5.4 The Five Studio Workspace Pages

1. **Motion Workspace (`static/js/pages/motion.js`)**:
   - **Dual Timeline**: Macro Sequence Overview bar (DaVinci Cut Page inspired) for whole-project scrubbing + Micro detailed track lanes.
   - **Keyframe Editing**: Draggable keyframe diamond handles with 80ms magnetic snapping to seconds, clip boundaries, and neighbouring markers.
   - **Audio Track Ribbon**: Waveform peak visualizer rendered directly inside the audio track lane.
2. **Fusion Workspace (`static/js/pages/fusion.js`, `vibmo/studio/pages/fusion.py`)**:
   - **Node-Based Compositing**: Automatically transforms scene layers, background generators, and post-processing shaders into a DAG.
   - **Interactive Graph**: Draggable nodes connected via dynamic SVG cubic Bézier wires (`M x1 y1 C ... x2 y2`).
3. **Color Workspace (`static/js/pages/color.js`, `vibmo/studio/pages/color.py`)**:
   - **3-Way Color Wheels**: Primary color grading wheels for Lift (shadows), Gamma (midtones), and Gain (highlights).
   - **Color Balance Controls**: Sliders for Exposure, Contrast, Saturation, Temperature, and Tint with real-time viewport update.
4. **Fairlight Workspace (`static/js/pages/fairlight.js`, `vibmo/studio/pages/fairlight.py`)**:
   - **Foley Soundboard**: Interactive soundboard triggering procedural audio synthesis (`pop`, `click`, `whoosh`, `riser`, `bass_drop`, `sparkle`).
5. **Deliver Workspace (`static/js/pages/deliver.js`, `vibmo/studio/pages/deliver.py`)**:
   - **Export Presets**: Master 1080p, Social Reel (9:16), Square Feed (1:1), WebM Alpha, ProRes 4K, Looping GIF.
   - **Batch Queue Manager (`RenderQueueManager`)**: Thread-safe job queue supporting sequential background execution, progress tracking, and error reporting.

---

## 5.5 Specialized Frontend Controllers & Hotkeys

- **Bézier Spline Editor (`static/js/core/spline.js`)**: Interactive modal featuring tangent control arms, dual control handles (P1, P2), grid reference diagonals, preset easing chips (`Out Expo`, `Out Cubic`, `In-Out Cubic`, `In-Out Back`, `Spring Overshoot`, `Linear`), and live Python expression generation (`Ease.bezier(0.25, 0.10, 0.25, 1.00)`).
- **Virtual Scrubbers (`static/js/app.js:175-218`)**: Drag-to-scrub number inputs on all inspector properties. Holding `Shift` activates fine sub-decimal adjustment (0.1x), while `Ctrl`/`Alt` enables coarse stepping (5.0x). Double-clicking labels resets properties to defaults.
- **J-K-L Shuttle & Cinema Controls**:
  - `Space`: Play / Pause toggle.
  - `L`: Shuttle forward (1x -> 2x -> 4x).
  - `J`: Shuttle reverse (-1x -> -2x -> -4x).
  - `K`: Stop playback.
  - `K + L`: Jog forward 1 frame.
  - `K + J`: Jog backward 1 frame.
  - `Ctrl + K`: Toggle AI Director modal.
  - `Ctrl + E`: Toggle Python Script Editor.
  - `Ctrl + F`: Fullscreen Cinema Viewer.

---

# 6. Model Context Protocol (MCP) Interface

---

## 6.1 JSON-RPC 2.0 Server Architecture (`vibmo-mcp` v2.0.0)

Vibmo provides an official MCP server implementing the JSON-RPC 2.0 specification over standard I/O (stdin/stdout), enabling autonomous AI agents to build, validate, preview, and edit motion graphics.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   AI Coding Agent (Client)                             │
│          (Claude Desktop / Cursor / Antigravity / Cline)               │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ Stdio (JSON-RPC 2.0)
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                     Vibmo MCP Server (`vibmo/mcp/`)                    │
│                                                                        │
│  Protocol Version: 2024-11-05                                          │
│  Capabilities: Tools, Resources, Prompts                               │
│                                                                        │
│  ┌───────────────────────┐ ┌───────────────────┐ ┌───────────────────┐ │
│  │     11 MCP Tools      │ │   4 MCP Resources │ │   3 MCP Prompts   │ │
│  ├───────────────────────┤ ├───────────────────┤ ├───────────────────┤ │
│  │ • list_components     │ │ • vibmo://docs/   │ │ • saas-launch     │ │
│  │ • search_icons        │ │   agents-guide    │ │ • kpi-dashboard   │ │
│  │ • validate_scene      │ │ • vibmo://compo-  │ │ • kinetic-typo    │ │
│  │ • inspect_storyboard  │ │   nents/catalog   │ └───────────────────┘ │
│  │ • get_frame_preview   │ │ • vibmo://docs/   │                       │
│  │ • generate_scene_...  │ │   verbs           │                       │
│  │ • ai_edit             │ │ • vibmo://docs/   │                       │
│  │ • autonomous_render   │ │   colors          │                       │
│  │ • render_scene        │ └───────────────────┘                       │
│  │ • get_project_state   │                                             │
│  │ • mutate_state_graph  │                                             │
│  └───────────────────────┘                                             │
└────────────────────────────────────────────────────────────────────────┘
```

- **Transport**: Standard I/O loop (`sys.stdin` / `sys.stdout`). Windows streams are reconfigured to UTF-8 with error replacement to prevent encoding crashes.
- **Protocol Version**: `"2024-11-05"`.
- **Supported Methods**: `initialize`, `ping`, `tools/list`, `tools/call`, `resources/list`, `resources/read`, `prompts/list`.

---

## 6.2 Complete 11 MCP Tools Catalog & Schemas

### Tool 1: `list_components`
- **Description**: Returns an inventory of all available semantic components, charts, cards, and motion verbs.
- **Input Schema**: `{ "type": "object", "properties": {} }`
- **Return Type**: `{ "count": int, "components": list[dict], "motion_verbs": list[dict] }`

### Tool 2: `search_icons`
- **Description**: Searches 200,000+ vector icons (Lucide, Tabler, Phosphor, Heroicons, Material) with offline caching.
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "query": { "type": "string", "description": "Icon keyword search (e.g. 'sparkles', 'rocket')" },
      "limit": { "type": "integer", "default": 10 }
    },
    "required": ["query"]
  }
  ```
- **Return Type**: `{ "query": str, "results": list[dict] }`

### Tool 3: `validate_scene`
- **Description**: Sandboxes and checks Python Vibmo scripts for layout collisions, timing overflows, and asset integrity.
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "code": { "type": "string", "description": "Python code snippet containing a Vibmo Scene" }
    },
    "required": ["code"]
  }
  ```
- **Return Type**: `{ "valid": bool, "issues": list[str], "duration": float, "fps": float, "node_count": int, "structure": dict }`

### Tool 4: `inspect_storyboard`
- **Description**: Executes a script and renders a multi-frame contact sheet returned as base64 PNG for visual AI inspection.
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "code": { "type": "string", "description": "Python code snippet" },
      "rows": { "type": "integer", "default": 2 },
      "cols": { "type": "integer", "default": 3 }
    },
    "required": ["code"]
  }
  ```
- **Return Type**: `{ "success": bool, "storyboard_path": str, "image_base64": str, "issues": list[str], "duration": float, "frames_rendered": int }`

### Tool 5: `get_frame_preview`
- **Description**: Renders a single frame at timestamp `time` and returns base64 JPEG for instant frame inspection.
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "code": { "type": "string", "description": "Python code snippet" },
      "time": { "type": "number", "default": 1.0 },
      "scale": { "type": "number", "default": 0.5 }
    },
    "required": ["code"]
  }
  ```
- **Return Type**: `{ "success": bool, "time": float, "scale": float, "image_base64": str }`

### Tool 6: `generate_scene_from_prompt`
- **Description**: Synthesizes an animated scene from a text prompt and generates a storyboard / video preview.
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "prompt": { "type": "string", "description": "Natural language motion graphics description" },
      "duration": { "type": "number", "default": 4.0 },
      "output_video": { "type": "string" },
      "output_storyboard": { "type": "string" },
      "provider": { "type": "string" }
    },
    "required": ["prompt"]
  }
  ```
- **Return Type**: `{ "success": bool, "prompt": str, "duration": float, "node_count": int, "storyboard_base64": str }`

### Tool 7: `ai_edit`
- **Description**: Surgically modifies existing Vibmo code using LLM reasoning and AST precision.
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "prompt": { "type": "string", "description": "Surgical modification instruction" },
      "current_code": { "type": "string", "description": "Current script source code" },
      "provider": { "type": "string" }
    },
    "required": ["prompt", "current_code"]
  }
  ```
- **Return Type**: `{ "success": bool, "updated_code": str, "message": str, "errors": list[str], "logs": list[str] }`

### Tool 8: `autonomous_render`
- **Description**: End-to-end autonomous pipeline: prompts -> generates code -> validates -> renders master video.
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "prompt": { "type": "string" },
      "output_video": { "type": "string", "default": "output.mp4" },
      "quality": { "type": "string", "default": "high" },
      "provider": { "type": "string" },
      "visual_critique": { "type": "boolean", "default": false }
    },
    "required": ["prompt"]
  }
  ```
- **Return Type**: `{ "success": bool, "video_path": str, "storyboard_path": str, "duration": float }`

### Tool 9: `render_scene`
- **Description**: Executes Vibmo code and renders the final video file (MP4, WebM, ProRes, GIF).
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "code": { "type": "string" },
      "output_path": { "type": "string", "default": "output.mp4" },
      "quality": { "type": "string", "default": "high" },
      "preset": { "type": "string", "default": "mp4" }
    },
    "required": ["code"]
  }
  ```
- **Return Type**: `{ "success": bool, "output_path": str, "file_size_bytes": int, "duration": float }`

### Tool 10: `get_project_state`
- **Description**: Returns the complete V2 State Graph (Timeline, Fusion DAG, Color, Fairlight, Media Pool) of a project.
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "project_path": { "type": "string" }
    }
  }
  ```
- **Return Type**: `{ "success": bool, "project_name": str, "tracks": list[dict], "clips_count": int, "media_pool_count": int, "fusion_graphs_count": int, "schema_json": dict }`

### Tool 11: `mutate_state_graph`
- **Description**: Safely executes atomic structural mutations on the State Graph DAG.
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "action": { "type": "string", "description": "import_media | add_clip | add_fusion_node | connect_fusion_nodes | set_primary_grade" },
      "params": { "type": "object" },
      "project_path": { "type": "string" },
      "save_path": { "type": "string" }
    },
    "required": ["action", "params"]
  }
  ```
- **Return Type**: `{ "success": bool, "action": str, "result": dict }`

---

## 6.3 MCP Knowledge Resources & Prompt Templates

### Resources (`vibmo/mcp/resources.py`)
- `vibmo://docs/agents-guide`: The complete `AGENTS.md` motion design guide for LLM agents.
- `vibmo://components/catalog`: Complete JSON schema catalog of semantic primitives and charts.
- `vibmo://docs/verbs`: Quick reference guide for all motion verbs (`pop_in`, `fade_up`, `count_to`, `reveal_characters`, `float_idle`).
- `vibmo://docs/colors`: Curated hex tokens for aesthetic dark/light palettes.

### Prompts (`vibmo/mcp/resources.py`)
- `create-saas-launch-video`: Generates high-converting dark-aesthetic SaaS product launch videos (`product_name`, `mrr_value`, `headline`).
- `create-kpi-dashboard`: Builds multi-card KPI dashboards with bar charts and status tables (`title`, `primary_metric`).
- `create-kinetic-typography`: Creates title reveal sequences with synced sound design (`title`, `subtitle`).

---

# 7. Video Packaging, NLE Timeline Interchange & Quality Gates

---

## 7.1 FFmpeg Streaming Pipe Engine & Codec Configurations

Rather than writing intermediate PNG frames to disk, `FFmpegPipeWriter` pipes raw uncompressed RGBA pixel buffers directly into an FFmpeg subprocess via standard input (`stdin`).

```
                     ┌────────────────────────────────────────┐
                     │             Scene Instance             │
                     └───────────────────┬────────────────────┘
                                         │
                 ┌───────────────────────┴───────────────────────┐
                 ▼                                               ▼
     ┌───────────────────────┐                       ┌───────────────────────┐
     │  Frame Render Engine  │                       │ Timeline Interchanges │
     ├───────────────────────┤                       ├───────────────────────┤
     │ • Rasterizer (Cairo)  │                       │ • OpenTimelineIO      │
     │ • Multi-core Pool     │                       │   (.otio JSON)        │
     │ • Motion Blur Worker  │                       │ • FCP 7 XML (.xml)    │
     │ • Resume Cache (.raw) │                       │ • CapCut/JianYing     │
     └───────────┬───────────┘                       │   (Microsecond Draft) │
                 │                                   └───────────────────────┘
                 │ Raw RGBA Stream (stdin)
                 ▼
     ┌───────────────────────┐
     │   FFmpegPipeWriter    │
     ├───────────────────────┤
     │ • H.264 (libx264)     │
     │ • ProRes 4444 (Alpha) │
     │ • WebM VP9 (Alpha)    │
     │ • 2-Pass Palette GIF  │
     │ • Multi-Track Audio   │
     │   amix Normalization  │
     └───────────────────────┘
```

### Codec & Preset Matrix

| Format Preset | Video Codec (`-c:v`) | Pixel Format (`-pix_fmt`) | Audio Codec (`-c:a`) | Transparency Support | Target Use Case |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **MP4 Master** | `libx264` (`-preset fast`, `-crf 18`, `-movflags +faststart`) | `yuv420p` | `aac` (`192k`) | No | Universal web streaming, YouTube, X, SaaS landing pages. |
| **WebM Alpha** | `libvpx-vp9` (`-crf 20`, `-b:v 0`) | `yuva420p` | `libopus` (`128k`) | **Yes** (8-bit Alpha) | Overlaying animations on transparent web pages and web apps. |
| **ProRes 4444** | `prores_ks` (`-profile:v 4`) | `yuva444p10le` | `pcm_s16le` | **Yes** (10-bit Alpha) | Broadcast uncompressed master, DaVinci Resolve / Premiere VFX plates. |
| **Animated GIF** | 2-pass palette (`[0:v] split [a][b];[a] palettegen=reserve_transparent=on [p];[b][p] paletteuse=dither=bayer:bayer_scale=3`) | RGB / Indexed | None | **Yes** (1-bit Alpha) | GitHub READMEs, documentation, lightweight chat previews. |

---

## 7.2 Multi-Core Parallel Pipeline & Resumable Cache

- **Multi-Processing Architecture**: Uses `concurrent.futures.ProcessPoolExecutor` with process initializer `_init_worker(scene)` to distribute frame rendering across CPU cores (default: `min(cpu_count - 1, 16)`).
- **Thread Safety Configuration**: Sets `OPENBLAS_NUM_THREADS=1`, `OMP_NUM_THREADS=1`, and `MKL_NUM_THREADS=1` in workers to eliminate thread contention and OpenBLAS thread-bombing.
- **Chunked In-Order Streaming**: Processes frames in chunks of `max_workers * 4`, ensuring strictly ordered writes to the FFmpeg pipe while maximizing parallel throughput.
- **Resumable Cache Engine (`--resume`)**: Caches rendered raw RGBA frames in `.vibmo_cache/<output_stem>/f_XXXXXX.raw`. If a render is interrupted, it resumes from the last completed frame and automatically cleans up the cache on successful finish.
- **Sub-Frame Motion Blur**: Simulates optical camera shutter blur using multi-sampling across shutter angles (e.g. 180° = 0.5 frame exposure time).

---

## 7.3 Universal NLE Timeline Interchange (OTIO, FCP 7 XML, CapCut/JianYing)

### 1. OpenTimelineIO Universal Exporter (`vibmo/render/otio_exporter.py`)
Serializes Vibmo timelines into Pixar's `.otio` specification:
- Converts timestamps to `RationalTime.1` and `TimeRange.1` structures.
- Maps video layers and plate assets into `Track.1` and `Clip.1` elements with `ExternalReference.1` URLs.
- Automatically calculates timeline gaps (`Gap.1`) between non-contiguous clips.
- Exports colored sequence markers (`Marker.1`) with comments and frame ranges.

### 2. Final Cut Pro 7 XML Exporter (`vibmo/render/fcp_exporter.py`)
Generates standardized `xmeml` version 5 XML documents compatible with DaVinci Resolve and Adobe Premiere Pro. Exports sequence duration, frame rates, sample characteristics (width/height), clip items, and media references.

### 3. CapCut / JianYing Desktop Draft Exporter (`vibmo/exporters/jianying_draft_exporter.py`)
Converts timelines into native CapCut/JianYing JSON drafts using exact microsecond timing calculations:
$$\text{start\_us} = \text{round}\left(\frac{f_0 \times 1\,000\,000}{\text{fps}}\right), \quad \text{duration\_us} = \text{round}\left(\frac{f_1 \times 1\,000\,000}{\text{fps}}\right) - \text{start\_us}$$
Generates video tracks, subtitle text cues, and multi-track audio cues with volume controls.

---

## 7.4 Production Quality Gates & Golden Launch Scene Recipe

### SlideshowRiskScorer 6-Dimensional Metric
The `SlideshowRiskScorer` analyzes 6 failure modes to prevent low-effort static AI output:
1. `repetition`: Excessive static framing without dynamic camera motion.
2. `decorative_visuals`: Superficial fluff without semantic narrative intent.
3. `weak_motion`: Absence of spring dynamics or linear robotic transitions.
4. `weak_shot_intent`: Unclear visual hierarchy or ambiguous subject focus.
5. `typography_overreliance`: Relying on wall-of-text slides rather than spatial UI.
6. `unsupported_cinematic_claims`: Unjustified heavy post-processing over weak layouts.

### 6-Beat Golden Launch Scene Recipe
The following script demonstrates the complete coordination of all Vibmo engine subsystems in a standalone broadcast deliverable:

```python
from vibmo.agent_api import *

# 1. Initialize Canvas (1080p @ 60 FPS, Dark Navy canvas)
scene = Scene(
    width=1920,
    height=1080,
    fps=60,
    duration=6.0,
    background=colors.DARK_NAVY,
)

# 2. Add Animated Procedural Backdrop & Viewport Post-FX
bg = MeshGradientFlow(colors=[colors.INDIGO, colors.PURPLE, colors.CYAN], speed=0.7)
scene.add(bg)
scene.add_post_fx(
    CrtPhosphorBloomShader(intensity=0.35, aperture_grille=False),
    Vignette(intensity=0.20),
    FilmGrain(amount=0.015),
)

# 3. Add Hardware Device Enclosure with Nested App UI
laptop = LaptopFrame(width=1100, height=650)
laptop.align("center", (1920, 1080)).at(410, 180)

screen_container = FlexContainer(direction="row", gap=24, padding=24, fill=colors.SLATE_950)
streamer = StreamingTokenOutput(
    text="Analyzing neural weights... Zero-boilerplate motion graphics compiled.",
    speed=35.0,
    width=520,
    height=500,
)
counter = MetricCounter(start_val=0, end_val=500000, prefix="$", suffix=" MRR", font_size=36, color=colors.EMERALD)

screen_container.add(streamer, counter)
laptop.add_screen_content(screen_container)
scene.add(laptop)

# 4. Add Kinetic Title Sequence
title = GlitchDecryptorText("VIBMO AI STUDIO", font_size=42, color=colors.CYAN)
title.at(410, 90)
scene.add(title)

# 5. Synchronized Procedural SFX
whoosh = WhooshDesignerSuite.cinematic_passby(duration=1.0)
click = CyberUISFXSuite.holographic_click()
scene.add_sfx("whoosh", time=0.1)

# 6. Choreograph with Natural Verbs
@scene.animate
def main():
    # Pop in laptop and decrypt title
    yield scene.all(
        laptop.pop_in(duration=0.9),
        title.decrypt(duration=1.4),
    )
    
    # Stream AI tokens and count revenue metrics concurrently
    yield scene.all(
        streamer.stream_tokens(speed=40.0),
        counter.count_to(duration=2.2, ease=Ease.out_expo),
    )
    
    yield scene.wait(1.5)

# 7. Quality Assurance Pre-Flight & Master Video Export
if __name__ == "__main__":
    report = SlideshowRiskScorer.evaluate([{"name": "MasterScene", "nodes": len(scene.nodes)}])
    print(f"Quality Gate Verdict: {report.verdict} (Score: {report.average_score:.2f})")
    scene.storyboard("master_storyboard.png")
    scene.render("master_video.mp4", quality="high")
```

---

# 8. Document Verification & Conformance Statement

This master reference manual `PROJECT_CATALOG.md` has been assembled and verified against the complete Vibmo / Motio codebase. It contains:
- Complete mathematical definitions and architectural workflows for all 5 core engine subsystems.
- Exhaustive class matrices, typed constructor signatures, default parameter values, and runnable Python recipes across all 13 production catalog sections (100+ component suites, 160+ classes).
- Comprehensive developer tooling documentation for the 15-subcommand CLI, Web Studio Pro NLE architecture (FastAPI/WebSocket/Canvas/Node Graph), and Model Context Protocol (MCP) JSON-RPC 2.0 interface.
- Complete video packaging specifications (FFmpeg pipes, OpenTimelineIO, FCP 7 XML, CapCut/JianYing draft JSON), color science standards (RCM, DWG, BT.2408 203-nit white, Dolby Vision L1), and automated quality gates.

*End of Vibmo Master Reference Manual.*
