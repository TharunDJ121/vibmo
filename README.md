# ✦ Motio / Vibmo: The AI-Agent Native Motion Design Framework in Python

> **Zero-boilerplate semantic motion graphics for developers, designers, and AI agents.**  
> Built for world-class SaaS launch videos, product UI demos, kinetic typography, vector metamorphosis, and audio visualizations without manual keyframe math.

---

## 🧭 Why Motio?

Unlike math-only animators (such as Manim) or low-level video editors (such as MoviePy), **Motio** is built for **high-level semantic design** and **vibe coding**. You declare *what* you want using intuitive motion verbs (`.pop_in()`, `.tilt_3d()`, `.morph_to()`, `.zoom_to()`, `.reveal_characters()`), and Motio automatically computes the spring physics, easing curves, ModernGL GPU post-shaders, and FFmpeg streaming.

```python
from motio.agent_api import *

scene = Scene(width=1920, height=1080, fps=60, duration=4.5, background=colors.DARK_NAVY)
card = scene.add(GlassCard(padding=32, corner_radius=24, position=(240, 200)))
card.add(
    Icon("lucide:sparkles", size=36, color=colors.CYAN),
    KineticText("Automated Motion in Python", font_size=32, bold=True),
    MetricCounter(start_val=0, end_val=250000, prefix="$", suffix=" MRR", font_size=52, bold=True, color=colors.EMERALD),
)
scene.add_post_fx(Vignette(intensity=0.25), FilmGrain(amount=0.01))

@scene.animate
def main():
    yield card.pop_in()
    yield scene.all(
        card.children[1].reveal_characters(stagger=0.025),
        card.children[2].count_to(duration=1.8, ease=Ease.out_expo),
    )
    card.float_idle(amplitude=6, speed=1.2)
    yield scene.wait(1.5)

if __name__ == "__main__":
    scene.storyboard("preview.png")
    scene.render("output.mp4", quality="high")
```

---

## ⚡ Key Capabilities & Feature Matrix

* **📱 Hardware Frames & Device Mockups**: `BrowserWindow`, `PhoneFrame`, `TabletFrame`, `LaptopFrame`, `WatchFrame`, `DesktopFrame`.
* **🔄 Vector Shape Metamorphosis**: `MorphPath` with deterministic arc-length resampling for seamless geometric morphing (Circle $\rightarrow$ Star $\rightarrow$ Heart $\rightarrow$ Play $\rightarrow$ Gear $\rightarrow$ Custom SVG).
* **🎥 Frame-Accurate Video Primitives**: `VideoNode` / `Asset.video()` with trimming, speed ramping, looping, and dynamic region zooming (`video.zoom_to_region()`).
* **🎭 Compositing Graph, Masks & Mattes**: `Precomp`, `AlphaMatte`, `LumaMatte`, `AdjustmentLayer`, and 17 layer blend modes (`Multiply`, `Screen`, `Overlay`, etc.).
* **📐 2.5D Depth, Perspective & Soft Shadows**: `Matrix3D`, 3D tilt (`card.tilt_3d(pitch, yaw)`), and multi-pass soft `DropShadow`.
* **🎨 25+ Visual FX & Shaders**: `FilmGrain`, `Vignette`, `BackdropBlur`, `Bloom`, `Glow`, `ChromaticAberration`, `DepthOfField`, `TiltShift`, `Glitch`, `Pixelate`, `Halftone`, `Duotone`, `Gridlines`, `Checkerboard`, `Scanlines`.
* **🎞️ 18 Modern Transitions**: `Slide`, `PushCut`, `Iris`, `Wipe`, `BookFlip`, `Flip`, `Ripple`, `CrossFade`, `ZoomPunch`, `GlitchTransition`, `LightLeak`.
* **🎵 Audio Reactivity, Procedural SFX & Stem Mixer**: Procedural foley generator (pops, clicks, whooshes, risers, bass drops), multi-track stem mixer (`AudioStemMixer`), dynamic audio ducking (`AudioDucker`), and 6 audio visualizers (`SpectrumBars`, `CircularSpectrum`, `VinylRecord`, `WaveformRibbon`).
* **🤖 AI & Intelligent UI Components**: `ModelCard`, `ChatInputBar`, `EditorialDoc`, `PillLaunchButton`, `CommandPalette`, `DataTable`, `AvatarGroup`.
* **📊 Complete Data Visualization Suite**: `AreaChart`, `Sparkline`, `BarChart`, `PieChart`, `DonutChart`, `GaugeChart`, `LineChart`, `RadarChart`, `FunnelChart`, `CandlestickChart`, `MathFormula` (LaTeX), and `Axes` (2D plots).
* **💻 Interactive Web Studio Pro**: Real-time 60 FPS in-browser workstation with NLE timeline, live canvas drag handles, node graph, audio mixer, and embedded Python IDE (`Ctrl+E`).
* **🤖 Antigravity AI Agent Skill & MCP**: Full MCP server integration and dedicated Antigravity skill package for autonomous video generation.

---

## 📦 Installation

```bash
# Clone repository
git clone https://github.com/vibmo-engine/vibmo.git
cd "motion graphics"

# Install in editable mode
pip install -e .
```

*Prerequisite: `ffmpeg` installed and available on system PATH.*

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
```

---

## 📚 Complete Documentation & Skill References

- 📖 **[Comprehensive API Reference Manual](file:///c:/Users/djtha/projects/motion%20graphics/docs/API_REFERENCE.md)**: Exhaustive documentation for every single class, method, argument, and type in the framework.
- 🎨 **[Asset Creation & Registration Guide](file:///c:/Users/djtha/projects/motion%20graphics/.agents/skills/motio-motion-graphics/references/asset_creation_guide.md)**: How to create, generate, load, and register every asset type (Images, Videos, Icons, Audio, Procedural Foley, Gradients, Textures, HTML/Tailwind, Lottie, Custom Components, Shaders).
- 🧩 **[Component Catalog Reference](file:///c:/Users/djtha/projects/motion%20graphics/.agents/skills/motio-motion-graphics/references/component_catalog.md)**: Visual components, hardware frames, mockups, AI widgets, and charts.
- 🎬 **[Motion Verbs & Transitions Cheat Sheet](file:///c:/Users/djtha/projects/motion%20graphics/.agents/skills/motio-motion-graphics/references/motion_verbs_cheat_sheet.md)**: All motion actions, 18 transition types, and physics force fields.
- 🚀 **[Showcase Production Recipes](file:///c:/Users/djtha/projects/motion%20graphics/.agents/skills/motio-motion-graphics/examples/recipes.md)**: Copy-pasteable recipes for SaaS demos, mobile features, shape morphs, and audio visualizers.
- 🤖 **[Antigravity Agent Skill](file:///c:/Users/djtha/projects/motion%20graphics/.agents/skills/motio-motion-graphics/SKILL.md)**: Agent instructions and inspection loops.

---

## 📂 Production Showcase Scripts (`examples/`)

| Script | Description |
| :--- | :--- |
| [`examples/saas_product_demo.py`](file:///c:/Users/djtha/projects/motion%20graphics/examples/saas_product_demo.py) | Flagship 130-line SaaS launch demo with `BrowserWindow`, `Cursor`, `Spotlight`, `MetricCounter`, and Camera directing. |
| [`examples/morph_showcase.py`](file:///c:/Users/djtha/projects/motion%20graphics/examples/morph_showcase.py) | Fluid vector shape metamorphosis across Circle $\rightarrow$ Star $\rightarrow$ Heart $\rightarrow$ Gear $\rightarrow$ Play $\rightarrow$ Check. |
| [`examples/audio_visualizer.py`](file:///c:/Users/djtha/projects/motion%20graphics/examples/audio_visualizer.py) | Advanced 360-degree radial music visualizer with `CircularSpectrum`, `VinylRecord`, `WaveformRibbon`, and beat reactivity. |
| [`examples/showcase_math.py`](file:///c:/Users/djtha/projects/motion%20graphics/examples/showcase_math.py) | Mathematical LaTeX animations (`MathFormula`) and dynamic 2D function plotting (`Axes.plot()`). |
| [`examples/showcase_advanced.py`](file:///c:/Users/djtha/projects/motion%20graphics/examples/showcase_advanced.py) | Glassmorphic cards, syntax-highlighted `CodeWindow`, and staggered kinetic typography. |
| [`examples/asset_expansion_demo.py`](file:///c:/Users/djtha/projects/motion%20graphics/examples/asset_expansion_demo.py) | Full demonstration of expanded transitions, pattern effects, and the asset library. |

---

## 🧪 Testing

```bash
# Run test suite
pytest tests/
```

---

## 📄 License
MIT License. Built for developers, designers, and AI agents.
