# ✦ Component Catalog Reference for Motio / Vibmo

This catalog documents every built-in semantic component, device mockup, chart, and AI widget available in Motio / Vibmo with instantiation parameters and motion tips.

---

## 📑 Component Categories

1. [Hardware Mockups & Frames](#1-hardware-mockups--frames)
2. [High-Vibe UI Cards & Displays](#2-high-vibe-ui-cards--displays)
3. [Kinetic Typography & Captions](#3-kinetic-typography--captions)
4. [Data Visualization & Charts](#4-data-visualization--charts)
5. [AI & Intelligent Product Primitives](#5-ai--intelligent-product-primitives)
6. [UI Controls & Form Elements](#6-ui-controls--form-elements)
7. [Feedback & Status Indicators](#7-feedback--status-indicators)
8. [Social & Community Elements](#8-social--community-elements)

---

## 1. Hardware Mockups & Frames

### `BrowserWindow`
macOS/Modern style browser window with top chrome, navigation buttons, and URL bar.
```python
browser = BrowserWindow(
    url="https://app.example.com",
    title="Analytics Dashboard",
    width=1400,
    height=840,
    dark_mode=True,
    corner_radius=18,
    position=(260, 120),
)
browser.add_content(my_ui_card)
```

### `PhoneFrame`
Mobile phone mockup with dynamic island / notch and speaker grille.
```python
phone = PhoneFrame(
    model="iphone15_pro",
    width=380,
    height=780,
    color="titanium_black",
    position=(770, 150),
)
phone.add_content(mobile_app_content)
```

### `LaptopFrame`, `TabletFrame`, `WatchFrame`, `DesktopFrame`
```python
laptop = LaptopFrame(model="macbook_pro_16", width=1280, height=800)
tablet = TabletFrame(width=820, height=1100, orientation="portrait")
watch = WatchFrame(width=280, height=340)
desktop = DesktopFrame(model="studio_display", width=1600, height=900)
```

---

## 2. High-Vibe UI Cards & Displays

### `GlassCard`
Frosted glass card with real backdrop blur simulation and specular highlights.
```python
card = GlassCard(
    direction="column", # "row" or "column"
    gap=16,
    padding=28,
    corner_radius=20,
    fill=Color.WHITE.with_alpha(0.06),
    stroke=Color.WHITE.with_alpha(0.14),
    specular_rim=True,
    width=420,
    position=(200, 200),
)
```

### `MetricCounter`
Animated numeric ticker with prefixes, suffixes, and exponential deceleration.
```python
counter = MetricCounter(
    start_val=0,
    end_val=1500000,
    prefix="$",
    suffix=" ARR",
    font_size=48,
    bold=True,
    color=colors.EMERALD,
)
# Animate:
yield counter.count_to(duration=1.6, ease=Ease.out_expo)
```

### `CodeWindow`
Terminal / code editor block mockup with title bar.
```python
code_win = CodeWindow(
    code='''@scene.animate
def reveal():
    yield card.pop_in()''',
    title="demo.py",
    font_size=18,
    width=600,
)
```

---

## 3. Kinetic Typography & Captions

### `KineticText`
Per-character and per-word wave reveals.
```python
heading = KineticText(
    "Next-Generation Motion Engine",
    font_size=42,
    bold=True,
    color=colors.WHITE,
    position=(300, 300)
)
# Verbs:
yield heading.reveal_characters(stagger=0.025, ease=Ease.out_expo)
yield heading.reveal_words(stagger=0.08)
yield heading.typewriter(speed=25)
```

### `NeonText` & `GradientText`
```python
neon = NeonText("CYBERPUNK", glow_color=colors.CYAN, glow_radius=25, font_size=54)
grad_text = GradientText("PREMIUM", gradient=Gradients.SUNSET, font_size=54)
```

### `AdvancedKaraokeCaptions`
```python
karaoke = AdvancedKaraokeCaptions(
    words=[
        TimedWord("Build", 0.0, 0.4),
        TimedWord("Stunning", 0.4, 0.9),
        TimedWord("Videos", 0.9, 1.5),
    ],
    highlight_color=colors.CYAN,
    font_size=40,
)
```

---

## 4. Data Visualization & Charts

### `AreaChart` & `Sparkline`
```python
area = AreaChart(
    data=[20, 35, 30, 60, 85, 110, 140],
    width=600,
    height=240,
    fill=colors.CYAN.with_alpha(0.18),
    stroke=colors.CYAN,
)
spark = Sparkline(data=[10, 15, 12, 22, 30], width=120, height=40, color=colors.EMERALD)
```

### `BarChart`, `PieChart` & `DonutChart`
```python
bar = BarChart(categories=["Jan", "Feb", "Mar", "Apr"], values=[40, 75, 110, 190], width=500, height=260)
pie = PieChart(slices=[{"label": "Web", "val": 60}, {"label": "Mobile", "val": 40}])
donut = DonutChart(slices=[{"label": "Tier 1", "val": 50}, {"label": "Tier 2", "val": 50}], inner_radius=50)
```

### `LineChart`, `RadarChart`, `FunnelChart`, `CandlestickChart`
```python
line = LineChart(series=[{"name": "Growth", "data": [10, 25, 45, 80]}])
radar = RadarChart(metrics=["Speed", "Accuracy", "Uptime", "Scale"], values=[0.95, 0.90, 0.99, 0.85])
funnel = FunnelChart(stages=[("Impression", 10000), ("Click", 1200), ("Conversion", 340)])
candlestick = CandlestickChart(candles=[{"open": 100, "high": 115, "low": 95, "close": 110}])
```

### `MathFormula` & `Axes`
```python
formula = MathFormula(latex=r"\sigma(z) = \frac{1}{1 + e^{-z}}", font_size=38, color=colors.AMBER)
axes = Axes(x_range=(-4, 4), y_range=(-1, 1), width=700, height=350, grid=True)
sin_curve = axes.plot(lambda x: math.sin(x), color=colors.CYAN)
```

---

## 5. AI & Intelligent Product Primitives

### `ModelCard`
```python
model_badge = ModelCard(
    name="Claude 3.5 Sonnet",
    provider="Anthropic",
    tokens_per_sec=82.4,
    latency_ms=180,
    width=360,
)
```

### `ChatInputBar`
```python
chat_bar = ChatInputBar(
    placeholder="Ask anything or generate animations...",
    has_attachment=True,
    has_voice=True,
    width=680,
)
```

### `EditorialDoc`, `PillLaunchButton`, `CommandPalette`
```python
doc = EditorialDoc(title="API Blueprint v2", word_count=2400, width=540)
launch_btn = PillLaunchButton(text="Run Benchmark", icon="lucide:zap")
cmd = CommandPalette(
    query="> Optimize",
    items=[
        CommandItem("Optimize Frame Buffers", "Ctrl+O"),
        CommandItem("Export ProRes 4444", "Ctrl+E"),
    ],
    width=520,
)
```

---

## 6. UI Controls & Form Elements

```python
progress = ProgressBar(progress=0.68, width=380, color=colors.CYAN)
slider = Slider(value=75, min_val=0, max_val=100, width=280)
tabs = Tabs(tabs=["Design", "Code", "Telemetry"], active_index=1)
modal = Modal(title="Confirm Export", width=540, height=320)
input_field = InputField(label="Email Address", placeholder="alex@acme.com", width=320)
switch = Switch(is_active=True, color=colors.EMERALD)
```

---

## 7. Feedback & Status Indicators

```python
toast = NotificationToast(
    title="Deployment Complete",
    description="Live in 34 regions worldwide.",
    icon_name="lucide:check",
    icon_color=colors.EMERALD,
)
banner = AlertBanner(title="High GPU Load", level="warning", width=600)
spinner = LoadingSpinner(size=36, color=colors.CYAN)
skeleton = SkeletonScreen(width=360, height=180, corner_radius=16)
```

---

## 8. Social & Community Elements

```python
avatar = Avatar(src="assets/user.jpg", size=48)
group = AvatarGroup(avatars=["assets/u1.jpg", "assets/u2.jpg", "assets/u3.jpg"], size=40)
badge = Badge(text="ENTERPRISE", color=colors.INDIGO)
bubble = ChatBubble(message="Can we refactor this transition?", is_user=True)
typing = TypingIndicator()
stat = StatCard(title="Active Nodes", value="24,891", change="+31.2%", is_positive=True)
```

---
*End of Component Catalog Reference.*
