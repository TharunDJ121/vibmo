# Project: Motio / Vibmo 100+ Asset Expansion & Modernization

## Architecture
Motio/Vibmo is a high-performance Python motion graphics framework featuring declarative scene composition, reactive Signal bindings, physics-based springs, procedural 48kHz audio generation, PyCairo 2D rendering with ModernGL GPU shaders, and zero-boilerplate God-import API (`from motio.agent_api import *`).

### Module & Package Boundaries
- `motio/agent_api.py`: The single-line public API gateway exporting all 100+ production motion components and presets.
- `vibmo/audio/generators/`: Procedural sound synthesis engine generating 48kHz float32 NumPy audio arrays.
- `vibmo/fx/backgrounds/`: Procedural animated backdrops with dynamic time-varying canvas effects.
- `vibmo/product/hardware/`: Realistic device enclosures with screen viewports, glass reflections, and ambient shadows.
- `vibmo/product/ai/`: Interactive UI components for AI, SaaS, and developer tools.
- `vibmo/charts/`: High-precision animated 2D, 3D, and financial charts.
- `vibmo/typography/kinetic/`: Kinetic typography nodes with per-glyph physics, shaders, and reveal animations.
- `vibmo/fx/shaders/`: Viewport post-FX shaders with GPU ModernGL acceleration and CPU fallbacks.
- `vibmo/templates/turnkey/`: Ready-to-render 1-line production scene templates.
- `vibmo/core/` & `vibmo/components/`: Core layout engine (`FlexContainer`), reactive signals (`Signal`), physics springs (`Spring`, `Ease`), and glassmorphic styling (`GlassCard`).

---

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| **Section 1: Procedural Audio & Sound Synthesis** | | | | |
| 1 | `WhooshDesignerSuite` | Cinematic passbys, doppler whips, sub-bass flybys | M1 | AGENTS.md §1 |
| 2 | `CyberUiSuite` | Holographic clicks, data packets, chirps, pips | M1 | AGENTS.md §1 |
| 3 | `GlitchStutterSuite` | Digital stutter bursts, corruption glitches | M1 | AGENTS.md §1 |
| 4 | `ImpactSubSuite` | Cinematic trailer sub drops, 808 impacts | M1 | AGENTS.md §1 |
| 5 | `KeyboardFoleySuite` | Mechanical keystrokes with switch selection | M1 | AGENTS.md §1 |
| 6 | `RiserTensionSuite` | Shepard tone risers, tension sweeps | M1 | AGENTS.md §1 |
| 7 | `AmbientDroneSuite` | Sci-fi deep space drones, dark atmospheric pads | M1 | AGENTS.md §1 |
| 8 | `VinylCrackleSuite` | Vintage turntable hiss, dust pops | M1 | AGENTS.md §1 |
| 9 | `LaserPlasmaSuite` | Plasma beam fire, energy blasts | M1 | AGENTS.md §1 |
| 10 | `LiquidBubblesSuite` | Water bubble pops, liquid droplets | M1 | AGENTS.md §1 |
| 11 | `PaperCardSuite` | Card flip shuffles, paper slides | M1 | AGENTS.md §1 |
| 12 | `Retro8bitSuite` | Arcade coin jumps, 8-bit boings | M1 | AGENTS.md §1 |
| 13 | `AlarmSirenSuite` | Emergency klaxon sweeps, hazard alerts | M1 | AGENTS.md §1 |
| 14 | `ChimesHarmonicSuite` | Celestial wind chimes, sparkle glimmers | M1 | AGENTS.md §1 |
| 15 | `CameraShutterSuite` | DSLR rapid bursts, mirror slaps | M1 | AGENTS.md §1 |
| **Section 2: Non-Static Animated Backdrops** | | | | |
| 16 | `MeshGradientFlow` | Multi-color animated mesh gradient flow | M1 | AGENTS.md §2 |
| 17 | `CyberGridHorizon` | 3D perspective cyber grid horizon | M1 | AGENTS.md §2 |
| 18 | `DigitalMatrixRain` | Cascading matrix digital rain with glow | M1 | AGENTS.md §2 |
| 19 | `FluidCaustics` | Procedural fluid caustics refraction | M1 | AGENTS.md §2 |
| 20 | `TopographicContours` | Animated topographic contour lines | M1 | AGENTS.md §2 |
| 21 | `CircuitBoardTraces` | Pulsing PCB circuit board traces | M1 | AGENTS.md §2 |
| 22 | `CosmicNebula` | Swirling cosmic nebula with starfield | M1 | AGENTS.md §2 |
| 23 | `RetroCrtScanlines` | Curved CRT scanlines with phosphor glow | M1 | AGENTS.md §2 |
| 24 | `SunsetHorizonGlow` | Retro synthwave sunset horizon glow | M1 | AGENTS.md §2 |
| 25 | `GeometricTessellation` | Morphing polygon geometric tessellation | M1 | AGENTS.md §2 |
| 26 | `BokehLightBubbles` | Defocused floating bokeh light bubbles | M1 | AGENTS.md §2 |
| 27 | `HyperspaceTunnel` | Warp-speed hyperspace star streak tunnel | M1 | AGENTS.md §2 |
| 28 | `MinimalStudioInfinity` | Studio cyclorama infinity curve with rim light | M1 | AGENTS.md §2 |
| 29 | `IsometricCityGrid` | 3D isometric building grid with light pulses | M1 | AGENTS.md §2 |
| 30 | `ParticleConstellation` | Linked particle constellation network | M1 | AGENTS.md §2 |
| **Section 3: Hardware Chassis & Enclosures** | | | | |
| 31 | `FoldableDeviceSuite` / `FoldableDeviceFrame` | Dual-screen foldable phone chassis with fold angle | M2 | AGENTS.md §3 |
| 32 | `SmartwatchRuggedSuite` / `RuggedSmartwatchFrame` | Rugged outdoor smartwatch chassis with bezel | M2 | AGENTS.md §3 |
| 33 | `SuperUltrawideSuite` / `SuperUltrawideMonitorFrame` | 32:9 curved ultrawide desktop monitor | M2 | AGENTS.md §3 |
| 34 | `PosRetailSuite` / `PosTerminalFrame` | Point-of-sale retail countertop terminal | M2 | AGENTS.md §3 |
| 35 | `CameraViewfinderSuite` / `CameraViewfinderOverlay` | Broadcast camera HUD viewfinder overlay | M2 | AGENTS.md §3 |
| 36 | `EInkTabletSuite` / `MinimalistEInkTabletFrame` | Minimalist e-ink tablet chassis | M2 | AGENTS.md §3 |
| 37 | `SmartHomeHubSuite` / `SmartHomeHubFrame` | Smart home display hub with tilted stand | M2 | AGENTS.md §3 |
| 38 | `VintageCrtSuite` / `RetroArcadeCrtCabinet` | Retro arcade cabinet with curved CRT screen | M2 | AGENTS.md §3 |
| 39 | `CctvSurveillanceSuite` / `CctvQuadViewOverlay` | CCTV 4-way surveillance grid overlay | M2 | AGENTS.md §3 |
| 40 | `SpatialVisorSuite` / `SpatialVisorFrame` | Spatial computing VR/AR visor headset | M2 | AGENTS.md §3 |
| 41 | `SmartTvDisplaySuite` / `OledCinemaTvFrame` | Bezel-less OLED cinema TV display | M2 | AGENTS.md §3 |
| 42 | `AutomotiveCockpitSuite` / `AutomotiveCockpitDash` | Automotive digital cockpit dashboard | M2 | AGENTS.md §3 |
| 43 | `GamingHandheldSuite` / `HandheldGamingConsoleFrame` | Portable handheld gaming console | M2 | AGENTS.md §3 |
| 44 | `CyberdeckTerminalSuite` / `CyberdeckChassisFrame` | Cyberdeck terminal chassis with mechanical keys | M2 | AGENTS.md §3 |
| 45 | `MultiMonitorSuite` / `MultiMonitorDeveloperRig` | Multi-monitor triple display developer workstation | M2 | AGENTS.md §3 |
| **Section 4: AI & SaaS Interactive UI Suites** | | | | |
| 46 | `StreamingTokenOutput` / `TokenStreamerSuite` | Streaming LLM token generator animation | M2 | AGENTS.md §4 |
| 47 | `TreeOfThoughtTree` / `ReasoningBranchNode` | Tree-of-Thought reasoning graph visualizer | M2 | AGENTS.md §4 |
| 48 | `DiffusionCanvas` / `DenoisingProgress` | Latent diffusion denoising step generator | M2 | AGENTS.md §4 |
| 49 | `AgentTeamThread` / `AgentMessageBubble` | Multi-agent collaborative conversation feed | M2 | AGENTS.md §4 |
| 50 | `VectorEmbeddingsVisualizer` / `ClusterPoint` | 3D vector embeddings scatter cluster | M2 | AGENTS.md §4 |
| 51 | `PricingTierMatrix` / `PricingTierColumn` | Tiered SaaS pricing matrix with highlight | M2 | AGENTS.md §4 |
| 52 | `ApiKeyVault` / `KeySecretRow` | API key vault with reveal/mask animation | M2 | AGENTS.md §4 |
| 53 | `GitPrTimeline` / `MergeStatusPill` | GitHub PR workflow timeline with merge action | M2 | AGENTS.md §4 |
| 54 | `TelemetryDialHUD` / `RadialGaugeDial` | Real-time telemetry radial gauge HUD | M2 | AGENTS.md §4 |
| 55 | `VisualSqlQueryBuilder` / `SchemaTableNode` | Visual SQL query builder with join connectors | M2 | AGENTS.md §4 |
| 56 | `WebhookActivityFeed` / `HttpRequestInspector` | Live webhook activity event stream | M2 | AGENTS.md §4 |
| 57 | `TokenQuotaMeter` / `UsageRingGauge` | Circular token quota usage meter | M2 | AGENTS.md §4 |
| 58 | `CodeSandboxPlayground` / `SplitConsoleOutput` | Interactive code sandbox with split console | M2 | AGENTS.md §4 |
| 59 | `FeatureComparisonMatrix` / `CheckmarkCell` | SaaS feature matrix with animated checkmarks | M2 | AGENTS.md §4 |
| 60 | `PromptDiffViewer` / `SideBySideDiffPane` | Side-by-side prompt diff viewer | M2 | AGENTS.md §4 |
| **Section 5: Financial, 3D Spatial & Motion Charts** | | | | |
| 61 | `CandlestickChartPro` / `VolumeBarSubplot` | Professional candlestick chart with volume | M3 | AGENTS.md §5 |
| 62 | `RadialSunburstHierarchy` / `SunburstRing` | Radial multi-level sunburst hierarchy | M3 | AGENTS.md §5 |
| 63 | `SpeedometerHudDial` / `KpiMetricGauge` | High-precision speedometer KPI gauge | M3 | AGENTS.md §5 |
| 64 | `SurfaceMesh3DPlot` / `WireframeTopology` | 3D parametric surface mesh wireframe | M3 | AGENTS.md §5 |
| 65 | `BubbleScatter4DPlot` / `RegressionCurve` | 4D bubble scatter plot with regression curve | M3 | AGENTS.md §5 |
| 66 | `WaterfallFinancialChart` / `FlowBarNode` | Financial variance waterfall flow chart | M3 | AGENTS.md §5 |
| 67 | `ChoroplethGeoMap` / `RegionPolygonNode` | Choropleth geographic heatmap | M3 | AGENTS.md §5 |
| 68 | `ViolinDensityPlot` / `KdeEnvelopeCurve` | Statistical violin density probability plot | M3 | AGENTS.md §5 |
| 69 | `MarketCapTreemap` / `TreemapCellNode` | Hierarchical market cap treemap | M3 | AGENTS.md §5 |
| 70 | `SankeyFlowDiagram` / `BezierFlowRibbon` | Sankey ribbon flow diagram | M3 | AGENTS.md §5 |
| 71 | `OrganicWaveStreamgraph` / `StackedWaveRibbon`| Organic stacked wave streamgraph | M3 | AGENTS.md §5 |
| 72 | `PolarRoseCoxcombChart` / `RoseWedgeNode` | Nightingale polar rose coxcomb chart | M3 | AGENTS.md §5 |
| 73 | `BoxAndWhiskerPlot` / `OutlierDotNode` | Statistical box-and-whisker plot | M3 | AGENTS.md §5 |
| 74 | `ParetoAnalysisChart` / `CumulativeCurve` | 80/20 Pareto analysis chart with curve | M3 | AGENTS.md §5 |
| **Section 6: Kinetic Typography & Title Sequences** | | | | |
| 75 | `GlitchDecryptorText` / `HexMatrixCycle` | Hex matrix cycle glitch decryption text | M3 | AGENTS.md §6 |
| 76 | `LiquidWaveText` / `SubmergedTextRefraction` | Submerged ripple liquid wave text | M3 | AGENTS.md §6 |
| 77 | `IsometricExtruded3DText` / `BevelGleamLight`| 3D extruded isometric text with bevel gleam | M3 | AGENTS.md §6 |
| 78 | `RealisticNeonStrobeSign` / `BallastFlickerFailure`| Realistic flickering neon strobe sign | M3 | AGENTS.md §6 |
| 79 | `ParticleFlameText` / `DisintegratingEmbers` | Disintegrating fire embers particle flame text | M3 | AGENTS.md §6 |
| 80 | `SplitFlapAirportBoard` / `MechanicalFlapTile` | Airport mechanical split-flap display board | M3 | AGENTS.md §6 |
| 81 | `MatrixRainTypography` / `PhosphorTrailDecay` | Matrix phosphor trail text consolidation | M3 | AGENTS.md §6 |
| 82 | `SlitScanVideoSynthText` / `ChromaWarpWave` | Slit-scan video synth chromatic warp text | M3 | AGENTS.md §6 |
| 83 | `OdometerTumblerCounter` / `VerticalRollingGlyphs`| Vertical rolling glyphs odometer tumbler | M3 | AGENTS.md §6 |
| 84 | `RubberStampTitleSlam` / `DustPuffShockwave` | Heavy impact rubber stamp title slam | M3 | AGENTS.md §6 |
| 85 | `MagneticGravityLetters` / `MagnetPullReassembly`| Magnetic gravity letter pull & snap | M3 | AGENTS.md §6 |
| 86 | `HologramChromaText` / `InterferenceFringeLines`| Prismatic holographic interference text | M3 | AGENTS.md §6 |
| 87 | `PhosphorTerminalTypewriter` / `BlinkingBlockCaret`| Vintage terminal typewriter with block caret | M3 | AGENTS.md §6 |
| 88 | `BrushCalligraphyPathReveal` / `InkSplatterBleed`| Ink splatter brush calligraphy stroke reveal | M3 | AGENTS.md §6 |
| 89 | `ElasticSquashBounceTitle` / `JellyMorphTypography`| Elastic squash & stretch comic bounce title | M3 | AGENTS.md §6 |
| **Section 7: Visual Post-FX Shaders & Turnkey Templates** | | | | |
| 90 | `CrtPhosphorBloomShader` / `CurvedGlassBarrelDistortion` | CRT bloom with curved barrel distortion | M4 | AGENTS.md §7 |
| 91 | `VhsTapeTrackingShader` / `HeadSwitchJitter` | VHS tape noise with head switch jitter | M4 | AGENTS.md §7 |
| 92 | `AnamorphicStreakFlare` / `HorizontalBlueStreak` | Cinematic anamorphic horizontal blue streak | M4 | AGENTS.md §7 |
| 93 | `LiquidGlassRefractionFilter` / `ChromaticDispersion` | Liquid glass refraction with chromatic dispersion | M4 | AGENTS.md §7 |
| 94 | `AsciiMatrixArtFilter` / `LuminescenceGrid` | ASCII luminescence matrix filter | M4 | AGENTS.md §7 |
| 95 | `TmplAiCodeAssistantSuite` | Turnkey AI code assistant scene template | M4 | AGENTS.md §7 |
| 96 | `TmplFintechCryptoCardSuite` | Turnkey fintech crypto card scene template | M4 | AGENTS.md §7 |
| 97 | `TmplDeveloperCliLaunchSuite` | Turnkey developer CLI launch scene template | M4 | AGENTS.md §7 |
| 98 | `TmplSaasYcPitchSuite` | Turnkey YC SaaS pitch deck scene template | M4 | AGENTS.md §7 |
| 99 | `TmplSocialAudiogramSuite` | Turnkey social podcast audiogram template | M4 | AGENTS.md §7 |
| **God-Import Gateway, Core Refinements & Integration** | | | | |
| 100 | `motio.agent_api` Export Gateway | Full God-import export of all 100+ components | M4 | R1, R2 |
| 101 | Framework Bug Fixes & Refinements | Fix prompt f-string & rasterizer buffer bug | M5 | R2, Survey |
| 102 | Reactive Layout & Physics Modernization | Damped spring presets, Signals, and GlassCard styling | M5 | R2 |
| 103 | E2E Showcase & 100% Pytest Pass | Unit tests, `asset_expansion_full_showcase.py`, visual storyboard | M6 | R3 |

---

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Section 1 (Audio) & Section 2 (Backdrops) Alignment | Ensure all 15 audio suites & 15 backdrops match AGENTS.md recipes & exports | none | PLANNED |
| M2 | Section 3 (Hardware) & Section 4 (AI/SaaS UI) Alignment | Standardize `.add_screen(*nodes)` across 15 frames + 15 UI animation generator verbs & aliases | none | PLANNED |
| M3 | Section 5 (Charts) & Section 6 (Typography) Alignment | Complete 14 chart animation verbs & aliases + verify 15 kinetic typo suites | none | PLANNED |
| M4 | Section 7 (Post-FX & Turnkey Templates) & `motio.agent_api` | Implement 2 missing turnkey templates + Post-FX aliases + 100% `agent_api.py` God-import | M1, M2, M3 | PLANNED |
| M5 | Core Framework Bug Fixes & Modernization Refinements | Fix prompt f-string & rasterizer proxy scale bug; refine auto-layout & spring physics | none | PLANNED |
| M6 | E2E Test Suite, Visual Storyboard & Full Showcase Integration | Pass 100% pytest suite, execute visual showcase, generate storyboards, pre-flight checks | M1, M2, M3, M4, M5 | PLANNED |

---

## Interface Contracts
### `motio.agent_api` Gateway
- Single import line: `from motio.agent_api import *` exposes every class in Feature Inventory.
- All classes support fluent chaining (`.align()`, `.pop_in()`, `.at()`, `.add()`).
- All animations return generators or tween lists composable via `yield` or `scene.all(...)`.

### Hardware Chassis ↔ Screen Viewports
- Method: `frame.add_screen(*children)` or `frame.add_screen_content(*children)` wraps children in a clipped `FlexContainer` bound to the chassis screen bounds.

### Animation Generators
- All AI UI suites, charts, and text nodes support generator methods yielding sub-animations (e.g., `yield streamer.stream_tokens(speed=30)`, `yield chart.draw_bars(duration=1.5)`, `yield text.decrypt(duration=1.8)`).

---

## Code Layout
- `vibmo/audio/generators/`: `sfx_*.py`
- `vibmo/fx/backgrounds/`: `bg_*.py`
- `vibmo/product/hardware/`: `hw_*.py`
- `vibmo/product/ai/`: `ui_*.py`
- `vibmo/charts/`: `chart_*.py`
- `vibmo/typography/kinetic/`: `typo_*.py`
- `vibmo/fx/shaders/`: `shader_*.py`
- `vibmo/templates/turnkey/`: `tmpl_*.py`
- `motio/agent_api.py` & `vibmo/__init__.py`: Export definitions
- `tests/`: `tests/audio/`, `tests/charts/`, `tests/components/`, `tests/fx/`, `tests/product/`, `tests/templates/`, `tests/typography/`, `tests/e2e/`
- `examples/asset_expansion_full_showcase.py`: Master visual showcase script
