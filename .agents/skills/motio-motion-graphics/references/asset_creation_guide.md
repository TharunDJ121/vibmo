# ✦ Asset Creation & Registration Guide for Motio / Vibmo

This comprehensive guide details how to create, load, generate, and register **every type of asset** in Motio / Vibmo—from bitmap images and screen recording videos to procedural foley SFX, custom vector icons, dynamic Tailwind widgets, custom shaders, and plugin components.

---

## 📑 Asset Types Overview

| Asset Type | Factory / Class | Formats / Sources | Primary Use Case |
| :--- | :--- | :--- | :--- |
| **Images & SVGs** | `Asset.image()`, `ImageNode` | PNG, JPG, WebP, SVG | Logos, avatars, badges, backdrop textures |
| **Videos** | `Asset.video()`, `VideoNode` | MP4, WebM, MOV, ProRes | Screen recordings, product walkthroughts, camera feeds |
| **Vector Icons** | `Icon()`, `BuiltinIcon` | 200,000+ Iconify, Custom SVG tuples | UI buttons, feature lists, indicators |
| **Audio Tracks & Stems** | `Asset.audio()`, `AudioTrack` | MP3, WAV, FLAC, OGG, URLs | Background music, voiceover tracks, stem mixing |
| **Procedural SFX** | `ProceduralSFX`, `SFXTrack` | Synthetic 48kHz NumPy | Zero-asset pops, clicks, whooshes, risers, bass drops |
| **Gradients** | `LinearGradient`, `Gradients` | Multi-stop Color tuples | Backdrop fills, glowing card borders, text fills |
| **Procedural Patterns** | `Checkerboard`, `Gridlines` | Algorithmic Cairo textures | Technical grids, dot matrices, CRT scanlines |
| **Lottie Animations** | `Asset.lottie()`, `LottieAnimation` | JSON Bodymovin vector files | Vector stickers, complex character motion |
| **Web & HTML Nodes** | `Asset.web()`, `Asset.html()` | Live URLs, Tailwind HTML | Live website frames, high-DPI frontend widgets |
| **Custom Components** | Subclass `Node`, `@register_component` | Python classes with `Signal` | Reusable branded UI elements and cards |
| **Custom Post-FX Shaders**| Subclass `Filter`, `@register_filter` | ModernGL GLSL Shaders | Custom chromatic distortions, lens effects |

---

## 1. Images & Bitmap Assets

### Loading and Configuring Images
Use the `Asset.image()` factory or `ImageNode` directly.

```python
# 1. Standard Image with auto-aspect scaling
logo = Asset.image("assets/logo.png", width=180)

# 2. Image with explicit dimensions and rounded corners
avatar = Asset.image(
    "assets/user_profile.jpg",
    width=96,
    height=96,
    corner_radius=48,  # Circular avatar
    position=(100, 200)
)

# 3. Animate image properties on timeline
@scene.animate
def anim():
    yield avatar.pop_in()
    yield avatar.scale.to((1.2, 1.2), duration=0.4, ease=Ease.out_back)
```

### Supported Image Formats & Transparency
- Supported formats: `.png`, `.jpg`, `.jpeg`, `.webp`, `.svg`, `.bmp`.
- PNG and WebP full 32-bit alpha transparency is preserved automatically.

---

## 2. Videos & Screen Recordings

### Loading and Animating Video Tracks
`Asset.video()` loads video files with frame-accurate indexing, trimming, speed scaling, and region zooming.

```python
# 1. Embedded Video Node
demo_video = Asset.video(
    "assets/screen_recording.mp4",
    width=1280,
    height=720,
    trim=(1.5, 8.5),      # Trim from 1.5s to 8.5s mark
    speed=1.25,            # Play back at 1.25x speed
    loop=True,             # Loop continuously if scene exceeds duration
    corner_radius=16,
)

# 2. Embed inside BrowserWindow mockup
browser = BrowserWindow(url="https://app.pulsemetrics.io", width=1400, height=840)
browser.add_content(demo_video)
scene.add(browser)

# 3. Dynamic Region Zooming (Focusing into a UI button on video)
@scene.animate
def video_choreography():
    yield browser.pop_in()
    
    # Zoom into top-right region of the video: (norm_x, norm_y, norm_w, norm_h)
    yield demo_video.zoom_to_region((0.55, 0.20, 0.40, 0.40), duration=1.0, ease=Ease.out_expo)
    yield scene.wait(1.5)
    
    # Reset video zoom back to full screen
    yield demo_video.reset_zoom(duration=0.8, ease=Ease.in_out_cubic)
```

---

## 3. Vector Icons & Symbols

### A. Using 200,000+ Iconify Icons
The `Icon` node resolves icons on-the-fly from Iconify libraries (Lucide, Heroicons, Phosphor, FontAwesome, Tabler, Material Design) and caches them locally.

```python
# Lucide Icons
icon_sparkles = Icon("lucide:sparkles", size=32, color=colors.CYAN)
icon_rocket   = Icon("lucide:rocket", size=48, color=colors.EMERALD)
icon_shield   = Icon("lucide:shield", size=28, color=colors.INDIGO)
icon_chart    = Icon("lucide:arrow-right", size=24, color=colors.WHITE)

# Bounce or pulse icon
yield icon_sparkles.bounce(amplitude=1.4, count=2)
```

### B. Registering Custom SVG Vector Icons in `ICON_REGISTRY`
To add custom vector shapes or icons directly in Python with zero network calls:

```python
from vibmo.assets.icons import ICON_REGISTRY, BuiltinIcon
import math

# Register a custom icon named 'custom_chip' normalized to a 24x24 viewBox
ICON_REGISTRY["custom_chip"] = [
    ("rect", 4, 4, 16, 16),
    ("rect", 9, 9, 6, 6),
    ("move", 9, 1), ("line", 9, 4),
    ("move", 15, 1), ("line", 15, 4),
    ("move", 9, 20), ("line", 9, 23),
    ("move", 15, 20), ("line", 15, 23),
    ("move", 1, 9), ("line", 4, 9),
    ("move", 1, 15), ("line", 4, 15),
    ("move", 20, 9), ("line", 23, 9),
    ("move", 20, 15), ("line", 23, 15),
]

# Instantiate custom vector icon
chip_icon = BuiltinIcon("custom_chip", size=40, color=colors.AMBER)
scene.add(chip_icon)
```

Supported registry commands:
- `("move", x, y)`: Move pen to $(x, y)$.
- `("line", x, y)`: Draw line to $(x, y)$.
- `("rect", x, y, w, h)`: Draw rectangle.
- `("circle", cx, cy, r)`: Draw circle.
- `("arc_path", cx, cy, r, start_angle, end_angle)`: Draw arc.
- `("close",)`: Close subpath.

---

## 4. Audio Tracks, Music & Stems

### Loading Audio
```python
# Local file
track1 = Asset.audio("assets/soundtrack.mp3")

# Direct URL
track2 = Asset.audio("https://example.com/audio/upbeat_tech.mp3")

# Curated built-in presets
track_cyberpunk = Asset.audio("preset:cyberpunk")
track_ambient   = Asset.audio("tech_ambient")
track_lofi      = Asset.audio("lofi_chill")

# Attach to Scene
scene.set_audio(track1, volume=0.75, fade_in=0.5, fade_out=1.0)
```

### Multi-Track Stem Mixer & Audio Ducking
```python
from vibmo.audio.stems import AudioStemMixer

mixer = AudioStemMixer()
mixer.add_stem("music", "assets/music.mp3", volume=0.35)
mixer.add_stem("voice", "assets/narration.wav", volume=1.0)
mixer.add_stem("sfx", "assets/pops_clicks.wav", volume=0.8)

# Automatically duck music by -14dB whenever voiceover speaks
mixer.apply_ducking(duck_stem="music", trigger_stem="voice", reduction_db=-14.0, attack=0.05, release=0.3)

# Export stems for professional DAW / NLE mastering
mixer.export_stems("output_stems/")
```

---

## 5. Procedural Sound Effects & Foley (Zero-Asset Audio)

Motio includes a built-in mathematical foley generator producing 48kHz float32 audio on-the-fly.

```python
from vibmo.audio.sfx import ProceduralSFX, SFXTrack

# 1. Generate individual procedural SFX waveforms
pop_audio    = ProceduralSFX.pop(duration=0.12, freq_start=240, freq_end=880)
click_audio  = ProceduralSFX.click(duration=0.04, freq=1850)
whoosh_audio = ProceduralSFX.whoosh(duration=0.45)
riser_audio  = ProceduralSFX.riser(duration=1.2, f_start=120, f_end=2400)
bass_audio   = ProceduralSFX.bass_drop(duration=0.6, freq_start=140, freq_end=35)
sparkle_snd  = ProceduralSFX.sparkle(duration=0.5)

# 2. Timeline SFX Track Choreography
sfx = SFXTrack()
sfx.trigger("whoosh", timestamp=0.1)
sfx.trigger("pop", timestamp=0.9)
sfx.trigger("click", timestamp=1.5)
sfx.trigger("bass_drop", timestamp=2.2)

scene.add_audio_track(sfx)
```

---

## 6. Custom Gradients & Color Presets

### Creating Gradients
```python
# Linear Gradient
linear = LinearGradient(
    start=(0, 0),
    end=(1920, 1080),
    stops=[
        (0.0, Color.hex("#0f172a")),
        (0.5, Color.hex("#1e1b4b")),
        (1.0, Color.hex("#0284c7")),
    ]
)

# Radial Gradient
radial = RadialGradient(
    center=(960, 540),
    radius=700,
    stops=[
        (0.0, Color.hex("#38bdf8").with_alpha(0.4)),
        (1.0, Color.TRANSPARENT),
    ]
)
```

### Built-in Gradients
```python
from vibmo.assets.gradients import Gradients, GRADIENT_PRESETS

bg_gradient = Gradients.SUNSET     # Orange -> Rose -> Purple
cyber_grad  = Gradients.MIDNIGHT   # Deep Indigo -> Cyan
forest_grad = Gradients.FOREST     # Emerald -> Teal
candy_grad  = Gradients.CANDY      # Pink -> Amber
```

---

## 7. Procedural Patterns & Textures

```python
# 1. Technical Grid Overlay
grid = Gridlines(spacing=40, stroke=Color.WHITE.with_alpha(0.06))
scene.add(grid)

# 2. Animated Checkerboard
checkers = Checkerboard(tile_size=48, color1=colors.SLATE_900, color2=colors.SLATE_800)
scene.add(checkers)

# 3. Concentric Rings
rings = Rings(spacing=32, center=(960, 540), stroke=colors.CYAN.with_alpha(0.15))
scene.add(rings)

# 4. CRT Scanlines & TV Static
scene.add_post_fx(Scanlines(spacing=4, opacity=0.1), FilmGrain(amount=0.015))
```

---

## 8. Lottie Vector Animations

```python
# Load Lottie JSON vector asset
lottie_node = Asset.lottie(
    "assets/success_burst.json",
    width=300,
    height=300,
    speed=1.0,
    loop=False,
    position=(810, 390)
)
scene.add(lottie_node)
```

---

## 9. Live Web & HTML/Tailwind Nodes

```python
# 1. 4K Retina Live Web Node
web_node = Asset.web(
    "https://linear.app",
    width=1440,
    height=900,
    scale=2.0,            # 2x Retina rendering
    corner_radius=16,
)

# 2. HTML / Tailwind Snippet Node
badge_ui = Asset.html(
    """
    <div class="flex items-center space-x-3 bg-slate-900/80 border border-cyan-500/30 px-6 py-3 rounded-full text-white">
        <span class="w-3 h-3 bg-cyan-400 rounded-full animate-ping"></span>
        <span class="font-mono text-sm tracking-wide">SYSTEM READY</span>
    </div>
    """,
    width=280,
    height=64,
)
scene.add(badge_ui)
```

---

## 10. Creating Custom Components

To create a new reusable component, subclass `Node`, declare reactive `Signal` fields, implement `draw()` and `local_bounds()`, and optionally register it:

```python
from vibmo.scene.node import Node
from vibmo.core.signal import Signal
from vibmo.core.color import Color, colors
from vibmo.plugins.registry import register_component

@register_component("StatusBadge")
class StatusBadge(Node):
    """Custom glowing status badge component."""

    def __init__(self, label: str = "ONLINE", color: Color = colors.EMERALD, **kwargs):
        super().__init__(**kwargs)
        self.label = label
        self.color = Signal(color, f"{self.name}.color")
        self.glow_radius = Signal(12.0, f"{self.name}.glow_radius")

    def local_bounds(self, time: float = 0.0):
        return (0.0, 0.0, 160.0, 44.0)

    def draw(self, ctx, time: float = 0.0):
        c = self.color.get(time)
        gr = self.glow_radius.get(time)
        
        # Draw background pill
        ctx.save()
        ctx.new_sub_path()
        ctx.arc(160 - 22, 22, 22, -1.57, 1.57)
        ctx.arc(22, 22, 22, 1.57, 4.71)
        ctx.close_path()
        
        ctx.set_source_rgba(*c.with_alpha(0.15).to_rgba())
        ctx.fill_preserve()
        ctx.set_source_rgba(*c.to_rgba())
        ctx.set_line_width(2.0)
        ctx.stroke()
        
        # Draw text label
        ctx.set_font_size(16.0)
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_source_rgba(1.0, 1.0, 1.0, 1.0)
        ctx.move_to(40, 28)
        ctx.show_text(self.label)
        ctx.restore()
```

---

## 11. Creating Custom Post-Processing Shaders / Filters

```python
from vibmo.fx.filters import Filter
from vibmo.plugins.registry import register_filter

@register_filter("CustomPrismGlitch")
class CustomPrismGlitch(Filter):
    """Custom RGB split distortion fragment shader."""

    def __init__(self, displacement: float = 8.0):
        self.displacement = displacement

    def apply_cpu(self, image_arr: np.ndarray, time: float) -> np.ndarray:
        # Software fallback for CPU rendering
        out = image_arr.copy()
        d = int(self.displacement)
        if d > 0:
            out[:, d:, 0] = image_arr[:, :-d, 0] # Shift Red channel
            out[:, :-d, 2] = image_arr[:, d:, 2] # Shift Blue channel
        return out

    def get_glsl_fragment_source(self) -> str:
        # ModernGL hardware shader pass
        return """
        #version 330
        uniform sampler2D u_texture;
        uniform float u_displacement;
        in vec2 v_uv;
        out vec4 f_color;
        
        void main() {
            float shift = u_displacement / 1920.0;
            float r = texture(u_texture, v_uv + vec2(shift, 0.0)).r;
            float g = texture(u_texture, v_uv).g;
            float b = texture(u_texture, v_uv - vec2(shift, 0.0)).b;
            float a = texture(u_texture, v_uv).a;
            f_color = vec4(r, g, b, a);
        }
        """
```

---

## 12. Central Asset Library (`AssetLibrary`) & Management

### Registering Assets into the Library
```python
from vibmo.assets.library import (
    get_asset_library,
    AssetMetadata,
    AssetType,
    AssetCategory,
)

lib = get_asset_library()

# Register a custom asset
lib.register_asset(AssetMetadata(
    id="custom-brand-logo",
    name="Acme Corp Logo",
    asset_type=AssetType.IMAGE,
    category=AssetCategory.BUSINESS,
    description="Official vector logo with transparent background",
    tags=["logo", "brand", "acme", "vector"],
    file_path="assets/acme_logo.png",
))

# Search assets by query or tag
results = lib.search_assets(query="logo", asset_type=AssetType.IMAGE)
print(f"Found {len(results)} matching assets.")
```

### Packaging Assets into a Portable Bundle
```python
# Packages all referenced images, audio, fonts, and videos into a single zip bundle
bundle_zip = Asset.bundle(scene, output_zip="my_campaign_assets.zip")
```

---
*End of Asset Creation & Registration Guide.*
