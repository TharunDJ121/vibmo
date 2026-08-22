# ✦ Motio: The AI Agent Vibe Coding Guide

> **For LLMs & AI Coding Agents (Claude, Codex, Antigravity, ChatGPT, Gemini, Cursor).**
> This guide teaches you how to generate world-class, aesthetic motion graphics with **zero boilerplate** using `motio` (and `vibmo`).

---

## 🧭 The 5 Motio Principles for Agents

1. **Single-Line God Import**: Always import everything in one line: `from motio.agent_api import *`.
2. **High-Level Intent & Method Chaining**: Never manually compute per-frame coordinates. Chain fluent helpers: `scene.add(GlassCard()).align("center").pop_in()`.
3. **Beautiful Defaults**: Every preset comes with natural spring overshoot, smooth deceleration, and visual polish. Keep default parameters unless explicitly requested.
4. **Semantic Primitives**: Think in design components (`BrowserWindow`, `GlassCard`, `MetricCounter`, `Cursor`, `Spotlight`, `MorphPath`, `Icon`, `CandlestickChartPro`, `SplitFlapAirportBoard`, `RealisticNeonStrobeSign`).
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
    scene.storyboard("storyboard.png")                # Instant 6-frame progression
    # scene.preview()                                 # Opens live interactive Web Studio in browser
    scene.render("output.mp4", quality="high")        # Master 1080p 60FPS export
```

---

## 📖 Complete Master Asset Suite Catalog (Sections 1 through 7)

Every class below is directly available via `from motio.agent_api import *`.

### 🔊 Section 1: Procedural Audio & Sound Synthesis (`vibmo/audio/generators/`)
Procedural 48kHz sound effects with zero external audio assets required.

| Suite | Component Classes | Usage Recipe |
| :--- | :--- | :--- |
| **Whoosh Designer** | `WhooshDesignerSuite` | `audio = WhooshDesignerSuite.cinematic_passby(duration=1.2)` |
| **Cyber UI** | `CyberUiSuite` | `click_sfx = CyberUiSuite.holographic_click(pitch=800)` |
| **Glitch Stutter** | `GlitchStutterSuite` | `glitch_audio = GlitchStutterSuite.digital_stutter_burst(duration=0.8)` |
| **Impact Sub** | `ImpactSubSuite` | `boom = ImpactSubSuite.cinematic_trailer_sub_drop(decay=2.0)` |
| **Keyboard Foley** | `KeyboardFoleySuite` | `typing_sfx = KeyboardFoleySuite.mechanical_keystroke(switch="blue")` |
| **Riser Tension** | `RiserTensionSuite` | `riser = RiserTensionSuite.shepard_tone_riser(duration=3.0)` |
| **Ambient Drone** | `AmbientDroneSuite` | `drone = AmbientDroneSuite.sci_fi_deep_space_drone(duration=10.0)` |
| **Vinyl Crackle** | `VinylCrackleSuite` | `lofi = VinylCrackleSuite.vintage_turntable_hiss(duration=5.0)` |
| **Laser Plasma** | `LaserPlasmaSuite` | `pew = LaserPlasmaSuite.plasma_beam_fire()` |
| **Liquid Bubbles** | `LiquidBubblesSuite` | `pop = LiquidBubblesSuite.water_bubble_pop()` |
| **Paper Card** | `PaperCardSuite` | `card_sfx = PaperCardSuite.card_flip_shuffle()` |
| **Retro 8-Bit** | `Retro8bitSuite` | `coin = Retro8bitSuite.arcade_coin_jump()` |
| **Alarm Siren** | `AlarmSirenSuite` | `alarm = AlarmSirenSuite.emergency_klaxon_sweep()` |
| **Chimes Harmonic** | `ChimesHarmonicSuite` | `sparkle_sfx = ChimesHarmonicSuite.celestial_wind_chime()` |
| **Camera Shutter** | `CameraShutterSuite` | `photo = CameraShutterSuite.dslr_rapid_burst()` |

---

### 🌌 Section 2: Non-Static Animated Backdrops (`vibmo/fx/backgrounds/`)
Procedural animated canvas backgrounds with dynamic procedural motion over time.

| Suite | Component Classes | Usage Recipe |
| :--- | :--- | :--- |
| **Mesh Gradient** | `MeshGradientFlow` | `scene.add(MeshGradientFlow(colors=[colors.INDIGO, colors.CYAN], speed=0.8))` |
| **Cyber Grid Horizon** | `CyberGridHorizon` | `scene.add(CyberGridHorizon(grid_color=colors.CYAN, perspective=0.8))` |
| **Matrix Code Rain** | `DigitalMatrixRain` | `scene.add(DigitalMatrixRain(density=40, glow_color=colors.EMERALD))` |
| **Fluid Caustics** | `FluidCaustics` | `scene.add(FluidCaustics(refraction=1.2, speed=0.5))` |
| **Topographic Contours** | `TopographicContours` | `scene.add(TopographicContours(line_spacing=24, speed=0.4))` |
| **Circuit Board Traces** | `CircuitBoardTraces` | `scene.add(CircuitBoardTraces(pulse_speed=1.5, trace_color=colors.CYAN))` |
| **Cosmic Nebula** | `CosmicNebula` | `scene.add(CosmicNebula(swirl_speed=0.2, star_count=120))` |
| **Retro CRT Scanlines** | `RetroCrtScanlines` | `scene.add(RetroCrtScanlines(curvature=0.1, scanline_gap=4))` |
| **Sunset Horizon Glow** | `SunsetHorizonGlow` | `scene.add(SunsetHorizonGlow(sun_radius=180, atmospheric_haze=0.3))` |
| **Geometric Tessellation**| `GeometricTessellation`| `scene.add(GeometricTessellation(poly_type="hexagon", morph_speed=1.0))` |
| **Bokeh Light Bubbles** | `BokehLightBubbles` | `scene.add(BokehLightBubbles(bubble_count=35, blur_radius=40))` |
| **Hyperspace Tunnel** | `HyperspaceTunnel` | `scene.add(HyperspaceTunnel(warp_speed=2.5, streak_color=colors.BLUE))` |
| **Studio Cyclorama** | `MinimalStudioInfinity`| `scene.add(MinimalStudioInfinity(horizon_y=700, rim_light=True))` |
| **Isometric City Grid** | `IsometricCityGrid` | `scene.add(IsometricCityGrid(building_count=50, pulse_lights=True))` |
| **Particle Constellation**| `ParticleConstellation`| `scene.add(ParticleConstellation(particle_count=80, link_radius=120))` |

---

### 💻 Section 3: Hardware Chassis & Device Enclosures (`vibmo/product/hardware/`)
Realistic hardware mockups with screen viewports, glass reflections, and ambient shadows.

| Suite | Component Classes | Usage Recipe |
| :--- | :--- | :--- |
| **Foldable Device** | `FoldableDeviceSuite`, `FoldableDeviceFrame` | `phone = FoldableDeviceFrame(fold_angle=30.0); phone.add_screen(app_ui)` |
| **Rugged Smartwatch** | `SmartwatchRuggedSuite`, `RuggedSmartwatchFrame` | `watch = RuggedSmartwatchFrame(); watch.add_screen(health_ui)` |
| **Super Ultrawide 32:9**| `SuperUltrawideSuite`, `SuperUltrawideMonitorFrame` | `monitor = SuperUltrawideMonitorFrame(width=1600, curve_depth=45)` |
| **Point-of-Sale Retail**| `PosRetailSuite`, `PosTerminalFrame` | `pos = PosTerminalFrame(); pos.add_screen(checkout_ui)` |
| **Camera Viewfinder** | `CameraViewfinderSuite`, `CameraViewfinderOverlay` | `rig = CameraViewfinderOverlay(hud_style="broadcast")` |
| **E-Ink Tablet** | `EInkTabletSuite`, `MinimalistEInkTabletFrame` | `tablet = MinimalistEInkTabletFrame(); tablet.add_screen(notes_ui)` |
| **Smart Home Hub** | `SmartHomeHubSuite`, `SmartHomeHubFrame` | `hub = SmartHomeHubFrame(stand_tilt=20); hub.add_screen(home_ui)` |
| **Retro Arcade CRT** | `VintageCrtSuite`, `RetroArcadeCrtCabinet` | `arcade = RetroArcadeCrtCabinet(); arcade.add_screen(game_node)` |
| **CCTV Surveillance** | `CctvSurveillanceSuite`, `CctvQuadViewOverlay` | `cctv = CctvQuadViewOverlay(timestamp=True, rec_indicator=True)` |
| **Spatial Visor VR** | `SpatialVisorSuite`, `SpatialVisorFrame` | `visor = SpatialVisorFrame(eye_tracking_glow=True)` |
| **OLED Cinema TV** | `SmartTvDisplaySuite`, `OledCinemaTvFrame` | `tv = OledCinemaTvFrame(stand_style="center_pedestal")` |
| **Automotive Cockpit** | `AutomotiveCockpitSuite`, `AutomotiveCockpitDash` | `dash = AutomotiveCockpitDash(hud_gauges=True)` |
| **Gaming Handheld** | `GamingHandheldSuite`, `HandheldGamingConsoleFrame` | `switch_mock = HandheldGamingConsoleFrame(theme="cyber_neon")` |
| **Cyberdeck Terminal**| `CyberdeckTerminalSuite`, `CyberdeckChassisFrame` | `deck = CyberdeckChassisFrame(mechanical_switches=True)` |
| **Multi-Monitor Rig** | `MultiMonitorSuite`, `MultiMonitorDeveloperRig` | `rig = MultiMonitorDeveloperRig(left_vertical=True)` |

---

### 🤖 Section 4: AI & SaaS Interactive UI Suites (`vibmo/product/ai/`)
Modern interactive components designed for AI tools, developer platforms, and SaaS products.

| Suite | Component Classes | Usage Recipe |
| :--- | :--- | :--- |
| **Streaming LLM Token**| `StreamingTokenOutput`, `TokenStreamerSuite` | `streamer = StreamingTokenOutput(text="Analyzing model weights..."); yield streamer.stream_tokens(speed=30)` |
| **Tree-of-Thought AI**| `TreeOfThoughtTree`, `ReasoningBranchNode` | `tot = TreeOfThoughtTree(branches=[...]); yield tot.expand_branch(0)` |
| **Diffusion Canvas** | `DiffusionCanvas`, `DenoisingProgress` | `canvas = DiffusionCanvas(); yield canvas.denoise_steps(steps=20)` |
| **Multi-Agent Chat** | `AgentTeamThread`, `AgentMessageBubble` | `chat = AgentTeamThread(); yield chat.post_agent_message("Coder", "Fixed.")` |
| **Vector Embeddings** | `VectorEmbeddingsVisualizer`, `ClusterPoint`| `vec = VectorEmbeddingsVisualizer(dimension=3); yield vec.rotate_cluster()` |
| **SaaS Pricing Matrix**| `PricingTierMatrix`, `PricingTierColumn` | `matrix = PricingTierMatrix(tiers=[...]); yield matrix.highlight_tier("Pro")` |
| **API Key Vault** | `ApiKeyVault`, `KeySecretRow` | `vault = ApiKeyVault(); yield vault.reveal_key(index=1)` |
| **GitHub PR Timeline**| `GitPrTimeline`, `MergeStatusPill` | `pr = GitPrTimeline(pr_number=88); yield pr.animate_merge()` |
| **Telemetry HUD** | `TelemetryDialHUD`, `RadialGaugeDial` | `hud = TelemetryDialHUD(); yield hud.set_metric("CPU", 88.5)` |
| **Visual SQL Builder** | `VisualSqlQueryBuilder`, `SchemaTableNode`| `sql = VisualSqlQueryBuilder(); yield sql.draw_join_relation("users", "orders")` |
| **Webhook Live Feed** | `WebhookActivityFeed`, `HttpRequestInspector`| `hook = WebhookActivityFeed(); yield hook.simulate_event("payment.succeeded")` |
| **Token Quota Ring** | `TokenQuotaMeter`, `UsageRingGauge` | `meter = TokenQuotaMeter(total=1000000); yield meter.consume(250000)` |
| **Code Sandbox** | `CodeSandboxPlayground`, `SplitConsoleOutput`| `box = CodeSandboxPlayground(code="print('vibe')"); yield box.run_execution()` |
| **Feature Comparison**| `FeatureComparisonMatrix`, `CheckmarkCell` | `comp = FeatureComparisonMatrix(); yield comp.reveal_rows()` |
| **Prompt Diff Suite** | `PromptDiffViewer`, `SideBySideDiffPane` | `diff = PromptDiffViewer(v1="...", v2="..."); yield diff.highlight_diffs()` |

---

### 📈 Section 5: Financial, 3D Spatial & Motion Charts (`vibmo/charts/`)
High-precision animated chart engines with smooth interpolations and metric axes.

| Suite | Component Classes | Usage Recipe |
| :--- | :--- | :--- |
| **Candlestick & Volume**| `CandlestickChartPro`, `VolumeBarSubplot` | `chart = CandlestickChartPro(ohlc_data=[...]); yield chart.draw_bars(duration=1.5)` |
| **Radial Sunburst** | `RadialSunburstHierarchy`, `SunburstRing` | `sun = RadialSunburstHierarchy(tree_data={...}); yield sun.expand_rings()` |
| **Speedometer HUD** | `SpeedometerHudDial`, `KpiMetricGauge` | `gauge = SpeedometerHudDial(min_val=0, max_val=220); yield gauge.needle_to(140)` |
| **3D Surface Mesh** | `SurfaceMesh3DPlot`, `WireframeTopology` | `surf = SurfaceMesh3DPlot(fn=lambda x,y: math.sin(x)*math.cos(y)); yield surf.rotate_3d()` |
| **4D Bubble Scatter** | `BubbleScatter4DPlot`, `RegressionCurve` | `scatter = BubbleScatter4DPlot(points=[...]); yield scatter.grow_bubbles()` |
| **Waterfall Variance** | `WaterfallFinancialChart`, `FlowBarNode` | `waterfall = WaterfallFinancialChart(steps=[...]); yield waterfall.reveal_steps()` |
| **Choropleth Geo Map** | `ChoroplethGeoMap`, `RegionPolygonNode` | `geo = ChoroplethGeoMap(regions={...}); yield geo.animate_heat_gradient()` |
| **Violin Probability**| `ViolinDensityPlot`, `KdeEnvelopeCurve` | `violin = ViolinDensityPlot(distributions=[...]); yield violin.expand_kde()` |
| **Market Cap Treemap** | `MarketCapTreemap`, `TreemapCellNode` | `treemap = MarketCapTreemap(stocks={...}); yield treemap.zoom_sector("Tech")` |
| **Sankey Flow Diagram**| `SankeyFlowDiagram`, `BezierFlowRibbon` | `sankey = SankeyFlowDiagram(links=[...]); yield sankey.animate_flow_current()` |
| **Wave Streamgraph** | `OrganicWaveStreamgraph`, `StackedWaveRibbon`| `stream = OrganicWaveStreamgraph(series=[...]); yield stream.undulate_stream()` |
| **Polar Rose Coxcomb** | `PolarRoseCoxcombChart`, `RoseWedgeNode` | `rose = PolarRoseCoxcombChart(sectors=[...]); yield rose.bloom_wedges()` |
| **Box-and-Whisker** | `BoxAndWhiskerPlot`, `OutlierDotNode` | `box = BoxAndWhiskerPlot(datasets=[...]); yield box.extend_whiskers()` |
| **Pareto Analysis** | `ParetoAnalysisChart`, `CumulativeCurve` | `pareto = ParetoAnalysisChart(categories=[...]); yield pareto.draw_80_20_cutoff()` |

---

### ✍️ Section 6: Kinetic Typography & Title Sequences (`vibmo/typography/kinetic/`)
Dynamic typography nodes with per-glyph physics, custom shaders, and reveal animations.

| Suite | Component Classes | Usage Recipe |
| :--- | :--- | :--- |
| **Glitch Decryptor** | `GlitchDecryptorText`, `HexMatrixCycle` | `text = GlitchDecryptorText("QUANTUM SECURE"); yield text.decrypt(duration=1.8)` |
| **Liquid Wave Refraction**| `LiquidWaveText`, `SubmergedTextRefraction`| `wave_text = LiquidWaveText("FLUID DYNAMICS"); yield wave_text.ripple_reveal()` |
| **3D Isometric Extruded**| `IsometricExtruded3DText`, `BevelGleamLight`| `iso = IsometricExtruded3DText("FUTURE TECH", depth=35); yield iso.gleam()` |
| **Neon Strobe Sign** | `RealisticNeonStrobeSign`, `BallastFlickerFailure`| `neon = RealisticNeonStrobeSign("OPEN 24/7", color=colors.CYAN); yield neon.ignite()` |
| **Particle Flame Embers**| `ParticleFlameText`, `DisintegratingEmbers` | `fire = ParticleFlameText("BURNING PASSION"); yield fire.disintegrate()` |
| **Split-Flap Board** | `SplitFlapAirportBoard`, `MechanicalFlapTile` | `board = SplitFlapAirportBoard(rows=3, cols=16); yield board.flip_to(["SAN FRANCISCO", "GATE B24"])` |
| **Matrix Code Rain** | `MatrixRainTypography`, `PhosphorTrailDecay` | `matrix_title = MatrixRainTypography("THE CONSTRUCT"); yield matrix_title.consolidate()` |
| **Slit-Scan Video Synth**| `SlitScanVideoSynthText`, `ChromaWarpWave` | `synth = SlitScanVideoSynthText("SYNTHESIZER"); yield synth.warp_scan()` |
| **Mechanical Odometer** | `OdometerTumblerCounter`, `VerticalRollingGlyphs`| `odo = OdometerTumblerCounter(start_val=0, end_val=9999); yield odo.roll_to(8420)` |
| **Rubber Stamp Slam** | `RubberStampTitleSlam`, `DustPuffShockwave` | `stamp = RubberStampTitleSlam("APPROVED", color=colors.ROSE); yield stamp.slam()` |
| **Magnetic Gravity Snap**| `MagneticGravityLetters`, `MagnetPullReassembly`| `magnet = MagneticGravityLetters("MAGNETIC FORCE"); yield magnet.snap_reassemble()` |
| **Prismatic Hologram** | `HologramChromaText`, `InterferenceFringeLines`| `holo = HologramChromaText("HOLOGRAPHIC"); yield holo.project_emitter()` |
| **Terminal Typewriter** | `PhosphorTerminalTypewriter`, `BlinkingBlockCaret`| `term = PhosphorTerminalTypewriter(prompt="user@vibmo:~$ "); yield term.typewriter("deploy --prod")` |
| **Brush Calligraphy** | `BrushCalligraphyPathReveal`, `InkSplatterBleed`| `brush = BrushCalligraphyPathReveal("Zenith"); yield brush.draw_strokes()` |
| **Squash & Stretch Bounce**| `ElasticSquashBounceTitle`, `JellyMorphTypography`| `comic = ElasticSquashBounceTitle("POW!"); yield comic.bounce_in()` |

---

### 🔮 Section 7: Visual Post-FX Shaders & Turnkey Production Suites (`vibmo/fx/shaders/` & `vibmo/templates/`)
Cinematic viewport shaders and turnkey 1-line scene setups.

| Suite | Component Classes | Usage Recipe |
| :--- | :--- | :--- |
| **CRT Monitor Bloom** | `CrtPhosphorBloomShader`, `CurvedGlassBarrelDistortion` | `scene.add_post_fx(CrtPhosphorBloomShader(bloom=1.4, aperture_grille=True))` |
| **VHS Tape Tracking** | `VhsTapeTrackingShader`, `HeadSwitchJitter` | `scene.add_post_fx(VhsTapeTrackingShader(noise=0.15, tracking_error=0.08))` |
| **Anamorphic Lens Flare**| `AnamorphicStreakFlare`, `HorizontalBlueStreak` | `scene.add_post_fx(AnamorphicStreakFlare(threshold=0.8, streak_length=600))` |
| **Liquid Glass Refraction**| `LiquidGlassRefractionFilter`, `ChromaticDispersion` | `scene.add_post_fx(LiquidGlassRefractionFilter(refraction=0.3))` |
| **ASCII Matrix Art** | `AsciiMatrixArtFilter`, `LuminescenceGrid` | `scene.add_post_fx(AsciiMatrixArtFilter(char_size=12, green_phosphor=True))` |
| **AI Coding Assistant** | `TmplAiCodeAssistantSuite` | `scene = TmplAiCodeAssistantSuite.build_scene(prompt="Build a SaaS in Python")` |
| **Fintech Crypto Card**| `TmplFintechCryptoCardSuite` | `scene = TmplFintechCryptoCardSuite.build_scene(cardholder="SATOSHI NAKAMOTO")` |
| **Developer CLI Launch**| `TmplDeveloperCliLaunchSuite` | `scene = TmplDeveloperCliLaunchSuite.build_scene(command="npm install -g vibmo")` |
| **YC SaaS Pitch Deck** | `TmplSaasYcPitchSuite` | `scene = TmplSaasYcPitchSuite.build_scene(mrr="$120k", growth="+40%")` |
| **Podcast Audiogram** | `TmplSocialAudiogramSuite` | `scene = TmplSocialAudiogramSuite.build_scene(audio="podcast.mp3", title="The Future of AI")` |

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
