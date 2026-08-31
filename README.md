# ✦ Vibmo / Motio: The AI-Agent Native Motion Design Framework in Python

> **Zero-boilerplate semantic motion graphics for developers, designers, and AI agents.**  
> Built for world-class SaaS launch videos, product UI demos, kinetic typography, 3D data visualization, vector metamorphosis, and procedural audio synthesis without manual keyframe math.

---

## 🧭 Why Vibmo?

Unlike math-only animators (such as Manim) or low-level video editors (such as MoviePy), **Vibmo** is built for **high-level semantic design** and **vibe coding**. You declare *what* you want using intuitive motion verbs (`.pop_in()`, `.tilt_3d()`, `.morph_to()`, `.zoom_to()`, `.reveal_characters()`), and Vibmo automatically computes the spring physics, easing curves, ModernGL GPU post-shaders, and FFmpeg streaming.

```python
from vibmo.agent_api import *

# 1. Initialize Scene (1080p @ 60 FPS, Dark aesthetic)
scene = Scene(
    width=1920,
    height=1080,
    fps=60,
    duration=5.0,
    background=colors.DARK_NAVY,
)

# 2. Add Background & Cinematic Post-FX
bg = MeshGradientFlow(speed=0.6, complexity=4)
scene.add(bg)
scene.add_post_fx(Vignette(intensity=0.25), FilmGrain(amount=0.015))

# 3. Assemble Semantic UI Components
card = GlassCard(direction="column", gap=16, padding=32, corner_radius=24, position=(240, 200))
icon = Icon("lucide:sparkles", size=36, color=colors.CYAN)
title = KineticText("Automated Motion in Python", font_size=32, bold=True)
counter = MetricCounter(start_val=0, end_val=250000, prefix="$", suffix=" MRR", font_size=52, bold=True, color=colors.EMERALD)

card.add(icon, title, counter)
scene.add(card)

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
    scene.storyboard("preview.png")                # Instant 6-frame progression
    # scene.preview()                             # Opens live interactive Web Studio in browser
    scene.render("output.mp4", quality="high")     # Master 1080p 60FPS export
```

---

## ⚡ Key Capabilities & Feature Matrix

* **📱 15+ Hardware Chassis & Device Enclosures**: `BrowserWindow`, `FoldableDeviceFrame`, `RuggedSmartwatchFrame`, `SuperUltrawideMonitorFrame`, `PosTerminalFrame`, `CameraViewfinderOverlay`, `MinimalistEInkTabletFrame`, `SmartHomeHubFrame`, `RetroArcadeCrtCabinet`, `SpatialVisorFrame`, `OledCinemaTvFrame`, `AutomotiveCockpitDash`, `HandheldGamingConsoleFrame`, `CyberdeckChassisFrame`, `MultiMonitorDeveloperRig`.
* **🔄 Vector Shape Metamorphosis**: `MorphPath` with deterministic arc-length resampling for seamless geometric morphing (Circle $\rightarrow$ Star $\rightarrow$ Heart $\rightarrow$ Play $\rightarrow$ Gear $\rightarrow$ Custom SVG).
* **🎥 Frame-Accurate Video Primitives**: `VideoNode` / `Asset.video()` with trimming, speed ramping, looping, and dynamic region zooming (`video.zoom_to_region()`).
* **🎭 Compositing Graph, Masks & Mattes**: `Precomp`, `AlphaMatte`, `LumaMatte`, `AdjustmentLayer`, and 18 layer blend modes (`Multiply`, `Screen`, `Overlay`, `ColorDodge`, etc.).
* **📐 2.5D Depth, Perspective & Soft Shadows**: `Matrix3D`, 3D camera tracker with rack focus, 3D tilt (`card.tilt_3d(pitch, yaw)`), and multi-pass soft `DropShadow`.
* **🎨 25+ Visual FX & Shaders**: `FilmGrain`, `Vignette`, `BackdropBlur`, `Bloom`, `Glow`, `ChromaticAberration`, `DepthOfField`, `TiltShift`, `Glitch`, `Pixelate`, `Halftone`, `Duotone`, `Gridlines`, `CrtPhosphorBloomShader`, `VhsTapeTrackingShader`, `AnamorphicStreakFlare`, `LiquidGlassRefractionFilter`, `AsciiMatrixArtFilter`.
* **🎞️ 18 Modern Transitions**: `Slide`, `PushCut`, `Iris`, `Wipe`, `BookFlip`, `Flip`, `Ripple`, `CrossFade`, `ZoomPunch`, `GlitchTransition`, `LightLeak`, and Remocn cinematic transitions.
* **🎵 Procedural Foley & Stem Mixer**: 15 procedural sound suites (Whoosh, Keystrokes, Bass Drops, UI Clicks, Ambient Drones, Risers), multi-track stem mixer (`AudioStemMixer`), dynamic audio ducking (`AudioDucker`), and 6 audio visualizers (`SpectrumBars`, `CircularSpectrum`, `VinylRecord`, `WaveformRibbon`).
* **🤖 AI & SaaS Interactive UI Suites**: `StreamingTokenOutput`, `TreeOfThoughtTree`, `DiffusionCanvas`, `AgentTeamThread`, `VectorEmbeddingsVisualizer`, `PricingTierMatrix`, `ApiKeyVault`, `GitPrTimeline`, `TelemetryDialHUD`, `VisualSqlQueryBuilder`, `WebhookActivityFeed`, `TokenQuotaMeter`, `CodeSandboxPlayground`, `FeatureComparisonMatrix`, `PromptDiffViewer`.
* **📊 Complete Financial & 3D Chart Engines**: `CandlestickChartPro`, `RadialSunburstHierarchy`, `SpeedometerHudDial`, `SurfaceMesh3DPlot`, `BubbleScatter4DPlot`, `WaterfallFinancialChart`, `ChoroplethGeoMap`, `ViolinDensityPlot`, `MarketCapTreemap`, `SankeyFlowDiagram`, `OrganicWaveStreamgraph`, `PolarRoseCoxcombChart`, `BoxAndWhiskerPlot`, `ParetoAnalysisChart`.
* **✍️ Kinetic Typography & Title Sequences**: `GlitchDecryptorText`, `LiquidWaveText`, `IsometricExtruded3DText`, `RealisticNeonStrobeSign`, `ParticleFlameText`, `SplitFlapAirportBoard`, `MatrixRainTypography`, `SlitScanVideoSynthText`, `OdometerTumblerCounter`, `RubberStampTitleSlam`, `MagneticGravityLetters`, `HologramChromaText`, `PhosphorTerminalTypewriter`, `BrushCalligraphyPathReveal`, `ElasticSquashBounceTitle`.
* **🌈 Color Science & HDR Mastering**: DaVinci Intermediate wide-gamut math, DaVinci DRT tone mapping, ITU-R BT.2408 203-nit diffuse white scaling, and Dolby Vision dynamic L1 metadata analysis.
* **💻 Interactive Web Studio Pro**: Real-time 60 FPS in-browser workstation with NLE timeline, live canvas drag handles, Fusion node graph, Fairlight audio mixer, and embedded Monaco Python IDE (`Ctrl+E`).
* **🤖 Model Context Protocol (MCP) & AI Agent Skill**: Built-in JSON-RPC 2.0 stdio MCP server enabling Claude Desktop, Cursor, Antigravity, and AI agents to validate scenes, generate animations, and render videos autonomously.

---

## 📦 Installation

```bash
# Clone repository
git clone https://github.com/TharunDJ121/vibmo.git
cd vibmo

# Install in editable mode with all dependencies
pip install -e .
```

*Prerequisite: `ffmpeg` installed and available on system `PATH`.*

---

## 🛠️ CLI Workflow

```bash
# 1. Browse and scaffold turnkey production templates
vibmo templates
vibmo create saas_launch my_launch_video
vibmo create app_demo my_mobile_app

# 2. Launch interactive Web Studio with live canvas drag handles
vibmo studio examples/saas_product_demo.py

# 3. Instant 6-frame storyboard contact sheet (0.1s)
vibmo storyboard examples/morph_showcase.py -o storyboard.png

# 4. Master 1080p/4K 60 FPS Render with frame caching
vibmo render examples/saas_product_demo.py -q high --resume
vibmo render examples/saas_product_demo.py -q draft       # 2-second fast preview
vibmo render examples/saas_product_demo.py -p prores      # Apple ProRes 4444 with Alpha
vibmo render examples/saas_product_demo.py -p webm        # WebM Transparent Overlay

# 5. Launch Model Context Protocol (MCP) Server for AI Agents
vibmo mcp
```

---

## 📚 Complete Documentation & Master Catalogs

- 📖 **[`PROJECT_CATALOG.md`](PROJECT_CATALOG.md)**: Exhaustive master reference covering all 13 Asset & Component Suites, complete parameter matrices, and runnable recipes.
- 🤖 **[`AGENTS.md`](AGENTS.md)**: AI Agent Vibe Coding Guide and inspection protocols for Claude, Antigravity, Cursor, and Codex.
- 🏛️ **[`ARCHITECTURE.md`](ARCHITECTURE.md)**: Deep dive into the 6 runtime engine layers (Authoring, Rigging, PyCairo Rasterizer, ModernGL Shaders, FFmpeg Streaming, and Studio Pro).
- 📖 **[`docs/API_REFERENCE.md`](docs/API_REFERENCE.md)**: Comprehensive API reference manual for all classes, methods, and types.

---

## 📂 Production Showcase Scripts (`examples/`)

| Script | Description |
| :--- | :--- |
| [`examples/saas_product_demo.py`](examples/saas_product_demo.py) | Flagship 130-line SaaS launch demo with `BrowserWindow`, `Cursor`, `Spotlight`, `MetricCounter`, and Camera directing. |
| [`examples/morph_showcase.py`](examples/morph_showcase.py) | Fluid vector shape metamorphosis across Circle $\rightarrow$ Star $\rightarrow$ Heart $\rightarrow$ Gear $\rightarrow$ Play $\rightarrow$ Check. |
| [`examples/audio_visualizer.py`](examples/audio_visualizer.py) | Advanced 360-degree radial music visualizer with `CircularSpectrum`, `VinylRecord`, `WaveformRibbon`, and beat reactivity. |
| [`examples/showcase_math.py`](examples/showcase_math.py) | Mathematical LaTeX animations (`MathFormula`) and dynamic 2D function plotting (`Axes.plot()`). |
| [`examples/showcase_advanced.py`](examples/showcase_advanced.py) | Glassmorphic cards, syntax-highlighted `CodeWindow`, and staggered kinetic typography. |
| [`examples/showcase_fintech_candlestick.py`](examples/showcase_fintech_candlestick.py) | Pro financial dashboard with `CandlestickChartPro`, volume subplots, and animated indicator overlays. |
| [`examples/showcase_kinetic_typography.py`](examples/showcase_kinetic_typography.py) | Multi-scene typography showcase with neon strobes, slit-scan, and glitch decryptions. |
| [`examples/showcase_saas_glass.py`](examples/showcase_saas_glass.py) | Modern dark-mode Bento grid and glassmorphism interface animations. |

---

## 🧪 Testing

```bash
# Run complete test suite (1,400+ unit & integration tests)
pytest tests/
```

---

## 📄 License
MIT License. Built for developers, designers, and AI agents.

