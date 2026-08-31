---
name: vibmo-vibmon-graphics
description: >-
  Expert guide for generating aesthetic vibmon graphics, SaaS launch videos, app UI demos,
  kinetic typography, audio visualizers, and creating/managing all asset types using the Vibmo / Vibmo Python framework.
  Use this skill whenever the user asks to create, animate, edit, style, or render vibmon graphics, UI mockups,
  charts, kinetic text, video scenes, or custom assets in Vibmo or Vibmo.
---

# ✦ Vibmo / Vibmo Vibmon Graphics Skill

This skill guides AI agents and developers in creating production-grade, 60 FPS vibmon graphics using `vibmo` (`vibmo`). It enforces zero-boilerplate semantic authoring, beautiful spring physics defaults, GPU shader post-processing, and a structured workflow for generating and registering all types of assets.

---

## 🧭 The 5 Core Principles

1. **Single-Line God Import**: Always begin scripts with:
   ```python
   from vibmo.agent_api import *
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
from vibmo.agent_api import *

# 1. Initialize Canvas
scene = Scene(
    width=1920,
    height=1080,
    fps=60,
    duration=5.0,
    background=colors.DARK_NAVY,
)

# 2. Add Background & Cinematic Post-Processing
bg = MeshGradientFlow(speed=0.6, complexity=4)
scene.add(bg)
scene.add_post_fx(Vignette(intensity=0.25), FilmGrain(amount=0.015))

# 3. Assemble Semantic UI Components
card = GlassCard(direction="column", gap=16, padding=32, corner_radius=24, position=(240, 200))
icon = Icon("lucide:sparkles", size=36, color=colors.CYAN)
title = KineticText("Automated Vibmon in Python", font_size=32, bold=True)
counter = MetricCounter(start_val=0, end_val=250000, prefix="$", suffix=" MRR", font_size=52, bold=True, color=colors.EMERALD)

card.add(icon, title, counter)
scene.add(card)

# 4. Choreograph Vibmon Verbs
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
    # scene.preview()                           # Live Web Studio inspector
    scene.render("output.mp4", quality="high")  # Master 1080p 60FPS export
```

---

## 📖 Master Asset Suite Catalog Across All 7 Sections

Every asset below is available directly via `from vibmo.agent_api import *`.

### 1. 🔊 Procedural Audio & Sound Effects (`vibmo.audio.generators`)
- `WhooshDesignerSuite`: `WhooshDesignerSuite.cinematic_passby()`
- `CyberUiSuite`: `CyberUiSuite.holographic_click()`
- `GlitchStutterSuite`: `GlitchStutterSuite.digital_stutter_burst()`
- `ImpactSubSuite`: `ImpactSubSuite.cinematic_trailer_sub_drop()`
- `KeyboardFoleySuite`: `KeyboardFoleySuite.mechanical_keystroke()`
- `RiserTensionSuite`: `RiserTensionSuite.shepard_tone_riser()`
- `AmbientDroneSuite`: `AmbientDroneSuite.sci_fi_deep_space_drone()`
- `VinylCrackleSuite`: `VinylCrackleSuite.vintage_turntable_hiss()`
- `LaserPlasmaSuite`: `LaserPlasmaSuite.plasma_beam_fire()`
- `LiquidBubblesSuite`: `LiquidBubblesSuite.water_bubble_pop()`
- `PaperCardSuite`: `PaperCardSuite.card_flip_shuffle()`
- `Retro8bitSuite`: `Retro8bitSuite.arcade_coin_jump()`
- `AlarmSirenSuite`: `AlarmSirenSuite.emergency_klaxon_sweep()`
- `ChimesHarmonicSuite`: `ChimesHarmonicSuite.celestial_wind_chime()`
- `CameraShutterSuite`: `CameraShutterSuite.dslr_rapid_burst()`

### 2. 🌌 Non-Static Animated Backdrops (`vibmo.fx.backgrounds`)
- `MeshGradientFlow`, `CyberGridHorizon`, `DigitalMatrixRain`, `FluidCaustics`, `TopographicContours`
- `CircuitBoardTraces`, `CosmicNebula`, `RetroCrtScanlines`, `SunsetHorizonGlow`, `GeometricTessellation`
- `BokehLightBubbles`, `HyperspaceTunnel`, `MinimalStudioInfinity`, `IsometricCityGrid`, `ParticleConstellation`

### 3. 💻 Hardware Chassis & Device Enclosures (`vibmo.product.hardware`)
- `FoldableDeviceFrame`, `RuggedSmartwatchFrame`, `SuperUltrawideMonitorFrame`, `PosTerminalFrame`, `CameraViewfinderOverlay`
- `MinimalistEInkTabletFrame`, `SmartHomeHubFrame`, `RetroArcadeCrtCabinet`, `CctvQuadViewOverlay`, `SpatialVisorFrame`
- `OledCinemaTvFrame`, `AutomotiveCockpitDash`, `HandheldGamingConsoleFrame`, `CyberdeckChassisFrame`, `MultiMonitorDeveloperRig`

### 4. 🤖 AI & SaaS Interactive UI Suites (`vibmo.product.ai`)
- `StreamingTokenOutput`, `TreeOfThoughtTree`, `DiffusionCanvas`, `AgentTeamThread`, `VectorEmbeddingsVisualizer`
- `PricingTierMatrix`, `ApiKeyVault`, `GitPrTimeline`, `TelemetryDialHUD`, `VisualSqlQueryBuilder`
- `WebhookActivityFeed`, `TokenQuotaMeter`, `CodeSandboxPlayground`, `FeatureComparisonMatrix`, `PromptDiffViewer`

### 5. 📈 Financial, 3D Spatial & Vibmon Charts (`vibmo.charts`)
- `CandlestickChartPro`, `RadialSunburstHierarchy`, `SpeedometerHudDial`, `SurfaceMesh3DPlot`, `BubbleScatter4DPlot`
- `WaterfallFinancialChart`, `ChoroplethGeoMap`, `ViolinDensityPlot`, `MarketCapTreemap`, `SankeyFlowDiagram`
- `OrganicWaveStreamgraph`, `PolarRoseCoxcombChart`, `BoxAndWhiskerPlot`, `ParetoAnalysisChart`

### 6. ✍️ Kinetic Typography & Title Sequences (`vibmo.typography.kinetic`)
- `GlitchDecryptorText`, `LiquidWaveText`, `IsometricExtruded3DText`, `RealisticNeonStrobeSign`, `ParticleFlameText`
- `SplitFlapAirportBoard`, `MatrixRainTypography`, `SlitScanVideoSynthText`, `OdometerTumblerCounter`, `RubberStampTitleSlam`
- `MagneticGravityLetters`, `HologramChromaText`, `PhosphorTerminalTypewriter`, `BrushCalligraphyPathReveal`, `ElasticSquashBounceTitle`

### 7. 🔮 Visual Post-FX Shaders & Turnkey Suites (`vibmo.fx.shaders` & `vibmo.templates`)
- Shaders: `CrtPhosphorBloomShader`, `VhsTapeTrackingShader`, `AnamorphicStreakFlare`, `LiquidGlassRefractionFilter`, `AsciiMatrixArtFilter`
- Turnkey Scenes: `TmplAiCodeAssistantSuite`, `TmplFintechCryptoCardSuite`, `TmplDeveloperCliLaunchSuite`, `TmplSaasYcPitchSuite`, `TmplSocialAudiogramSuite`

---

## 🛠️ Step-by-Step Agent Workflow

When fulfilling a user request for vibmon graphics or video assets:

1. **Identify the Scene Requirements**:
   - Canvas resolution (`1920x1080` widescreen, `1080x1920` vertical reel, `1080x1080` square).
   - Theme and aesthetic palette (`DARK_NAVY`, `SLATE_900`, `CYBERPUNK`, `MINIMAL_LIGHT`).
   - Assets needed (Icons, mockups, audio, logos, charts).
2. **Assemble the Hierarchy**:
   - Nest child elements inside containers (`GlassCard`, `FlexContainer`, `BrowserWindow`, `PhoneFrame`, `FoldableDeviceFrame`).
   - Use `scene.add()` to register top-level elements and post-processing filters (`Vignette`, `FilmGrain`, `CrtPhosphorBloomShader`).
3. **Decorate the Choreography**:
   - Write `@scene.animate` generator functions.
   - Use `yield scene.all(...)` for concurrent actions and `yield action` for sequential steps.
   - Use `yield scene.wait(seconds)` for idle pauses.
4. **Validate & Inspect**:
   - Run `scene.validate()` to catch duration overflows (`delay + duration > scene.duration`).
   - Export `scene.storyboard("storyboard.png")` to verify 6-frame composition progression.
5. **Render Final Output**:
   - Use `scene.render("output.mp4", quality="high")` for full render or `quality="draft"` for instant preview.

---

## ⚠️ Critical Pitfalls & Agent Rules

| Pitfall | Incorrect | Correct |
| :--- | :--- | :--- |
| Import individual symbols | `from vibmo import Scene` | `from vibmo.agent_api import *` |
| Direct property assignment | `node.position = (100, 200)` | `node.position.set((100, 200))` or `node.at(100, 200)` |
| Unpacking generator yield | `yield *cursor.click()` | `yield cursor.click()` or `yield scene.all(cursor.click(), ...)` |
| Undecorated animation | `def main(): yield ...` | `@scene.animate\ndef main():\n    yield ...` |
| Non-reactive custom state | `self.custom_val = 10` | `self.custom_val = Signal(10.0, "name.val")` |
| Missing fonts | Hardcoding uninstalled fonts | Use standard fonts (`"Inter"`, `"Roboto"`, `"Space Grotesk"`) |


### 🚀 Section 9: HDR, Color Science & Resolution Independence (`vibmo/color/` & `vibmo/core/`)
Advanced pipeline tools for 32-bit float color science, HDR mastering, and dynamic resolution scaling.

| Suite | Component Classes | Usage Recipe |
| :--- | :--- | :--- |
| **Resolve Color Management** | `RCMPipeline`, `DRTMode` | `rgb = RCMPipeline.apply_drt_tone_mapping(rgb, mode=DRTMode.DAVINCI)` |
| **SDR to HDR Diffuse White** | `RCMPipeline` | `rgb = RCMPipeline.sdr_to_hdr_diffuse_white(rgb, target_nits=203.0)` |
| **Dolby Vision Analysis** | `DolbyVisionAnalyzer` | `l1_metrics = DolbyVisionAnalyzer.analyze_frame(rgb_nits)` |
| **MultiMaster Trim** | `MultiMasterTrimManager`, `TrimPass` | `trim = MultiMasterTrimManager(master_nits=4000); trim.add_trim_pass(TrimPass('SDR_Rec709'))` |
| **Dynamic Sizing Pipeline** | `SizingPipeline`, `FitMode` | `matrix = SizingPipeline.concatenate_affine_matrix(fit, edit, input)` |
| **HDR Light Level Report** | `HDRReportGenerator` | `report_md = HDRReportGenerator.generate_markdown_report(data)` |
| **Automated Audio Soft-Fades** | `FairlightAudioEngine` | `clean_audio = FairlightAudioEngine.apply_soft_fades(audio, fade_ms=1.5)` |
| **Hierarchical Render Cache**| `HierarchicalRenderCache`, `CacheTier`| `frame = cache.get_or_render(CacheTier.TIER2_NODE_GRAPH, key, fn)` |



### 🎨 Section 11: Remocn Motion Graphics, Shaders & 6-Beat Video Spine (`vibmo/templates/`, `vibmo/fx/shaders/`, `vibmo/typography/`, `vibmo/product/ai/`, `vibmo/quality/`)
Production suites inspired and optimized from the Remocn ecosystem for high-converting SaaS product demos and developer launches.

| Suite | Component Classes | Usage Recipe |
| :--- | :--- | :--- |
| **6-Beat Product Spine** | `TmplSaasProductDemoSpineSuite`, `ProductDemoSpine` | `scene = TmplSaasProductDemoSpineSuite.build_scene(spine=ProductDemoSpine(product_name="Vibmo"))` |
| **Changelog Video** | `TmplChangelogReleaseSuite` | `scene = TmplChangelogReleaseSuite.build_scene(version="v2.4.0", release_title="Hardware Shaders")` |
| **CLI Developer Launch** | `TmplCliDeveloperLaunchSuite` | `scene = TmplCliDeveloperLaunchSuite.build_scene(tool_name="vibmo-cli", command="vibmo build")` |
| **Claude Code & Terminal**| `ClaudeCodeSimulator`, `TerminalCursorZoom` | `term = ClaudeCodeSimulator(); term.add_command("pip install vibmo").add_output("Installed ✓")` |
| **AI Prompt Composer** | `AiPromptFlow`, `ModelSelectorPill` | `flow = AiPromptFlow(prompt_text="Build SaaS", model_name="Claude 3.7"); yield flow.type_prompt()` |
| **Interactive Checkout** | `InteractiveCheckoutFlow`, `PaymentCreditCardField` | `checkout = InteractiveCheckoutFlow(amount="$99/yr"); yield checkout.trigger_payment()` |
| **Social Follow & Stars** | `XFollowCard`, `GitHubStarsCard` | `card = XFollowCard(name="Vibmo"); yield card.click_follow()` |
| **Infinite Bento Pan** | `InfiniteBentoPan`, `BentoGridCard` | `bento = InfiniteBentoPan(); yield bento.pan_camera((100, 50))` |
| **ASCII Render Filter** | `AsciiRenderFilter`, `AsciiRenderShader` | `scene.add_post_fx(AsciiRenderFilter(glyph_size=16, ink="#00ff00"))` |
| **CCTV Security Cam** | `SecurityCamOverlay`, `CctvSurveillanceHud` | `scene.add_post_fx(SecurityCamOverlay(camera_name="CAM 01 // LOBBY", show_rec=True))` |
| **Neural Noise & Voronoi**| `ShaderNeuroNoise`, `ShaderVoronoiGrid` | `scene.add(ShaderNeuroNoise(speed=0.8, color_core=(14, 165, 233)))` |
| **Underwater Wave Ripple**| `UnderwaterRippleFilter` | `scene.add_post_fx(UnderwaterRippleFilter(frequency=0.02, amplitude=8.0))` |
| **Blur Out Up Title** | `BlurOutUpText`, `BlurOutUpCharacterNode` | `text = BlurOutUpText("Launch Week"); yield text.blur_out_up()` |
| **Matrix Cipher Decode** | `MatrixDecodeText`, `MatrixGlyphScrambler` | `matrix = MatrixDecodeText("QUANTUM SECURE"); yield matrix.decode()` |
| **Rolling Number Wheel** | `RollingNumberWheel`, `SlotMachineRoller` | `roller = RollingNumberWheel(start_val=0, end_val=5000); yield roller.roll_to(4200)` |
| **Inline Pill Takeover** | `InlinePillTakeoverText`, `StrikethroughReplaceText`| `pill = InlinePillTakeoverText(pill_text="zero boilerplate"); yield pill.expand_pill()` |
| **Push-Through Zoom** | `PushThroughTransition` | `trans = PushThroughTransition(max_scale=3.0)` |
| **Focus-Pull Rack Focus**| `FocusPullTransition` | `trans = FocusPullTransition(max_blur=24.0)` |
| **Anti-Slop Quality Gate**| `AntiSlopValidator`, `AntiSlopReport` | `report = AntiSlopValidator.evaluate_scene(scene); assert report.verdict != "fail"` |


### 🎬 Section 12: Video-Shotcraft Staging Suites, Beat-Sync & NLE Draft Export (`vibmo/product/shotcraft/`, `vibmo/audio/`, `vibmo/exporters/`, `vibmo/quality/`)
Cinematic staging suites, physical UI metaphors, audio transient beat-syncing, CapCut / JianYing export, and production aesthetic case law derived from `video-shotcraft`.

| Suite | Component Classes | Usage Recipe |
| :--- | :--- | :--- |
| **Deck Deal Fly-In** | `DeckDealFlyIn` | `deck = DeckDealFlyIn(cards=[{"title": "AI", "metric": "99%"}]); yield deck.deal_cards(); yield deck.fan_out()` |
| **Doc Park & Pill Deal** | `DocParkPillDeal` | `doc = DocParkPillDeal(doc_title="Research"); yield doc.dock_left(); yield doc.deal_pills()` |
| **Spotlight Hero Card** | `SpotlightHeroCard`, `DarkMetallicFloor` | `hero = SpotlightHeroCard(title="Core Engine"); scene.add(hero); yield hero.ignite_spotlight()` |
| **Autolayout Gap Dial** | `AutolayoutGapDial` | `dial = AutolayoutGapDial(block_labels=["A", "B", "C"]); yield dial.expand_gap(48.0)` |
| **Chip Grid Blackout** | `ChipGridSelectBlackout` | `chips = ChipGridSelectBlackout(options=["A", "B"]); yield chips.trigger_select()` |
| **Avatar Bracket Carousel**| `AvatarBracketCarousel` | `bracket = AvatarBracketCarousel(roles=["Coder", "Architect"]); yield bracket.cycle_to(1.0)` |
| **Bezier Convergence** | `BezierSourceConvergeMerge` | `merge = BezierSourceConvergeMerge(sources=["PRs", "DB"]); yield merge.animate_flow()` |
| **Keynote Family Portrait**| `OutroGroupPhotoLaunch` | `outro = OutroGroupPhotoLaunch(brand_name="Vibmo"); yield outro.launch_family_portrait()` |
| **Brand Ink Open** | `BrandInkOpen` | `ink = BrandInkOpen(brand_name="VIBMO"); yield ink.animate_intro()` |
| **Brace Expand Reveal** | `BraceExpand` | `brace = BraceExpand(title_text="ZERO BOILERPLATE"); yield brace.expand()` |
| **Beat Cut Accelerando** | `BeatCutAccelerando` | `cuts = BeatCutAccelerando(cut_labels=["CUT 1", "CUT 2"]); yield cuts.step_cut(1)` |
| **Paparazzi Strobe Flash**| `PaparazziFlash` | `flash = PaparazziFlash(); yield flash.trigger_flash()` |
| **Musical Beat Grid** | `BeatSyncGrid`, `TimelineSFXTable` | `grid = BeatSyncGrid(bpm=126.0); sfx = TimelineSFXTable(grid); sfx.add_cue("whoosh", target_beat=4.0)` |
| **CapCut / JianYing Draft**| `JianYingDraftExporter` | `exporter = JianYingDraftExporter(); exporter.add_video_segment("Hero", 0, 120); exporter.export_to_file("draft.json")` |
| **Aesthetic Case Law** | `AestheticCaseLawValidator` | `report = AestheticCaseLawValidator.evaluate_scene(scene); assert report.verdict != "fail"` |


### 🌌 Section 13: Video Production Skills, Dark Magic UI & Anti-PPT Director (`vibmo/product/magic_ui/`, `vibmo/typography/`, `vibmo/ai/`, `vibmo/quality/`)
Presenton-style dark magic UI, black & white Foley typing openers, Anti-PPT meta-director, and full-frame replica QC.

| Suite | Component Classes | Usage Recipe |
| :--- | :--- | :--- |
| **Dark Starfield Stage** | `DarkStarfieldStage` | `scene.add(DarkStarfieldStage(particle_count=65, horizon_color="#7c3aed"))` |
| **Prompt Invocation** | `PromptInvocationCard` | `card = PromptInvocationCard(prompt_text="Build AI video"); yield card.enter_card(); yield card.type_prompt()` |
| **Model Orbit Ring** | `ModelCapabilityOrbit` | `orbit = ModelCapabilityOrbit(models=["Claude 3.7", "GPT-4o"]); yield orbit.open_ring(); yield orbit.rotate_orbit()` |
| **Export Burst** | `ExportBurstContainer` | `burst = ExportBurstContainer(headline="Instant Export"); yield burst.trigger_burst()` |
| **Connected Ecosystem** | `ConnectEcosystemSlot` | `slot = ConnectEcosystemSlot(hub_name="Cloud API"); yield slot.animate_connect()` |
| **Turnkey Dark Magic** | `TmplDarkSaasMagicSuite` | `scene = TmplDarkSaasMagicSuite.build_scene(prompt_text="Ship SaaS Promo in Python")` |
| **B&W Typing Opener** | `BlackWhiteTypingOpener` | `opener = BlackWhiteTypingOpener(title_prefix="AI Video Engine"); yield opener.type_intro()` |
| **Anti-PPT Meta-Director**| `MotionThesis`, `BeatGraph`, `AntiPptGate` | `thesis = MotionThesis("river", "stream", "network", "speed"); graph = BeatGraph(thesis); report = AntiPptGate.evaluate_beat_graph(graph)` |
| **Video Replica QC** | `VideoReplicaVerifier`, `FidelityLevel` | `verdict = VideoReplicaVerifier.evaluate_three_gates(result); assert verdict.overall_status == "aligned"` |




