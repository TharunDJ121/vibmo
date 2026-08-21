# 🚀 Master Catalog: 100 Jules Tasks (350–500 Total Assets)

> **Execution Standard**: All tasks are strictly isolated to **1 dedicated implementation file** and **1 dedicated unit test file**. No shared files or `__init__.py` are modified during batch execution, guaranteeing zero merge conflicts across parallel sessions.
>
> **Command Format**: `jules new --repo TharunDJ121/vibmo "<PROMPT>"`

---

## 📑 Quick Navigation
- [Section 1: Procedural Audio & Foley Suites (Tasks 01–15)](#section-1-procedural-audio--foley-suites-tasks-0115)
- [Section 2: Non-Static Animated Backgrounds & Dynamic Backdrops (Tasks 16–30)](#section-2-non-static-animated-backgrounds--dynamic-backdrops-tasks-1630)
- [Section 3: Hardware Chassis, Device Enclosures & Mockup Suites (Tasks 31–45)](#section-3-hardware-chassis-device-enclosures--mockup-suites-tasks-3145)
- [Section 4: AI & SaaS Interactive UI Component Suites (Tasks 46–60)](#section-4-ai--saas-interactive-ui-component-suites-tasks-4660)
- [Section 5: Financial, 3D Spatial & Motion Chart Suites (Tasks 61–75)](#section-5-financial-3d-spatial--motion-chart-suites-tasks-6175)
- [Section 6: Kinetic Typography & Title Sequence Suites (Tasks 76–90)](#section-6-kinetic-typography--title-sequence-suites-tasks-7690)
- [Section 7: Visual Post-FX Shaders & Turnkey Production Suites (Tasks 91–100)](#section-7-visual-post-fx-shaders--turnkey-production-suites-tasks-91100)

---

## Section 1: Procedural Audio & Foley Suites (Tasks 01–15)
*Target: 50–65 procedural sound generators at 48kHz float32*

### Task 01: Cyberpunk Holographic UI SFX Suite
- **Implementation File**: `vibmo/audio/generators/sfx_cyber_ui_suite.py`
- **Test File**: `tests/audio/test_sfx_cyber_ui_suite.py`
- **Prompt**:
```text
Implement a procedural Cyberpunk Holographic UI sound generator suite in `vibmo/audio/generators/sfx_cyber_ui_suite.py` producing 48kHz float32 NumPy audio arrays.
Create a class `CyberUISFXSuite` with static methods:
1. `holo_chirp(duration=0.08, freq_start=1800, freq_end=3200)`: Dual-frequency resonant FM chirp for button hover/touch.
2. `data_packet_burst(duration=0.15, count=6, freq=2400)`: Rapid granular data stream burst.
3. `access_granted_tone(duration=0.45, chord=[523.25, 659.25, 783.99, 1046.50])`: Euphoric ascending harmonic major 7th chime.
4. `access_denied_klaxon(duration=0.35, freq=180)`: Harsh saw-wave dual-tone warning buzzer with rapid envelope decay.
5. `cyber_pip(duration=0.04, freq=2200)`: Crisp micro-tap feedback.
Export standalone convenience functions and include complete type annotations.
Write isolated pytest unit tests in `tests/audio/test_sfx_cyber_ui_suite.py` verifying non-zero waveforms, 48000 sample rate, normalized amplitudes (-1.0 to 1.0), and valid durations. Do not modify any other existing files.
```

### Task 02: Cinematic Doppler & Whip Whoosh Designer Suite
- **Implementation File**: `vibmo/audio/generators/sfx_whoosh_designer_suite.py`
- **Test File**: `tests/audio/test_sfx_whoosh_designer_suite.py`
- **Prompt**:
```text
Implement a procedural Doppler & Whip Whoosh sound generator suite in `vibmo/audio/generators/sfx_whoosh_designer_suite.py` producing 48kHz float32 NumPy audio arrays.
Create a class `WhooshDesignerSuite` with static methods:
1. `doppler_whip(duration=0.35, speed=2.5)`: High-velocity whip whoosh with dynamic pitch sweep and stereo-panned frequency shift.
2. `sub_bass_flyby(duration=0.75, sub_freq=55.0)`: Heavy low-end sub-bass fly-by with resonant low-pass filter sweep.
3. `airy_transition(duration=0.50, breath_noise=0.8)`: Soft, airy transition whoosh using filtered white/pink noise envelope.
4. `quick_snap_whoosh(duration=0.18)`: Fast swipe whoosh for rapid slide cuts and card fly-ins.
Write isolated pytest unit tests in `tests/audio/test_sfx_whoosh_designer_suite.py` validating array bounds, sample rate, peak normalization, and duration tolerances. Do not modify any other existing files.
```

### Task 03: Heavy Cinematic 808 & Impact Sub Suite
- **Implementation File**: `vibmo/audio/generators/sfx_impact_sub_suite.py`
- **Test File**: `tests/audio/test_sfx_impact_sub_suite.py`
- **Prompt**:
```text
Implement a procedural Sub-Bass Impact & Hit sound generator suite in `vibmo/audio/generators/sfx_impact_sub_suite.py` producing 48kHz float32 NumPy audio arrays.
Create a class `ImpactSubSuite` with static methods:
1. `cinematic_808_drop(duration=1.2, start_freq=160.0, end_freq=32.0, saturation=1.4)`: Heavy saturated 808 sub-bass drop with exponential pitch decay.
2. `punch_thud_impact(duration=0.45, attack_click=True)`: Tight punchy acoustic impact with transient click and low-mid resonance.
3. `metallic_anvil_hit(duration=0.9, ring_freq=880.0)`: Metallic cinematic hit with harmonic bell-like ring resonance.
4. `card_slam_impact(duration=0.35)`: Solid organic UI card impact on virtual canvas.
Write isolated unit tests in `tests/audio/test_sfx_impact_sub_suite.py` verifying proper waveform decay, sample rate adherence, non-clipping, and correct array lengths. Do not modify any other existing files.
```

### Task 04: Shepard Tone & Tension Pitch Riser Suite
- **Implementation File**: `vibmo/audio/generators/sfx_riser_tension_suite.py`
- **Test File**: `tests/audio/test_sfx_riser_tension_suite.py`
- **Prompt**:
```text
Implement an illusionary Shepard Tone & Tension Pitch Riser generator suite in `vibmo/audio/generators/sfx_riser_tension_suite.py` producing 48kHz float32 NumPy audio arrays.
Create a class `RiserTensionSuite` with static methods:
1. `shepard_tone_riser(duration=2.5, base_freq=65.4, octaves=5)`: Infinitely ascending Shepard-Risset glissando illusion.
2. `cyber_pitch_riser(duration=1.8, start_f=100.0, end_f=3500.0, lfo_rate=8.0)`: Modulated cyber synth pitch sweep with accelerating LFO vibrato.
3. `white_noise_sweep(duration=1.5, resonance=4.0)`: Resonant band-pass filtered white noise sweep from 200Hz to 12kHz.
4. `tension_alarm_build(duration=2.0, pulses=8)`: Accelerating pulsing alarm siren riser leading up to a beat drop.
Write isolated unit tests in `tests/audio/test_sfx_riser_tension_suite.py` testing pitch evolution, frequency bounds, and length validity. Do not modify any other existing files.
```

### Task 05: Bitcrush, Glitch & Tape Stop Stutter Suite
- **Implementation File**: `vibmo/audio/generators/sfx_glitch_stutter_suite.py`
- **Test File**: `tests/audio/test_sfx_glitch_stutter_suite.py`
- **Prompt**:
```text
Implement a procedural Glitch, Bitcrush & Tape Stop generator suite in `vibmo/audio/generators/sfx_glitch_stutter_suite.py` producing 48kHz float32 NumPy audio arrays.
Create a class `GlitchStutterSuite` with static methods:
1. `tape_motor_stop(audio_in: np.ndarray, slowdown_curve=2.0)`: Analog vinyl/tape machine power-down deceleration and exponential pitch drop.
2. `bitcrush_buffer_freeze(duration=0.4, bit_depth=4, sample_rate_reduction=8)`: Lo-fi digital bitcrusher with quantization distortion.
3. `digital_glitch_stutter(duration=0.5, slice_count=12, randomize=True)`: Granular buffer stutter and micro-repeats.
4. `data_corruption_burst(duration=0.3)`: Synthetic high-entropy digital data packet burst.
Write isolated unit tests in `tests/audio/test_sfx_glitch_stutter_suite.py` verifying glitch algorithms, distortion transforms, and array outputs. Do not modify any other existing files.
```

### Task 06: Crystal Chimes, Celesta & Fanfare Suite
- **Implementation File**: `vibmo/audio/generators/sfx_chimes_harmonic_suite.py`
- **Test File**: `tests/audio/test_sfx_chimes_harmonic_suite.py`
- **Prompt**:
```text
Implement a procedural Crystal Chimes & Harmonic Sparkle generator suite in `vibmo/audio/generators/sfx_chimes_harmonic_suite.py` producing 48kHz float32 NumPy audio arrays.
Create a class `ChimesHarmonicSuite` with static methods:
1. `crystal_bell_chime(duration=1.2, fundamental=1046.50)`: Physical modeled crystal bell strike with harmonic overtones (1.0, 2.76, 5.4, 8.9).
2. `sparkle_magic_glimmer(duration=0.8, density=16)`: Cascading random micro-bell sparkle shimmer.
3. `dream_harp_glissando(duration=1.4, scale="pentatonic_major")`: Rapidly ascending harp arpeggio sweep.
4. `celebration_fanfare_tone(duration=1.0)`: Rich harmonic brass-style synth triumph chord.
Write isolated unit tests in `tests/audio/test_sfx_chimes_harmonic_suite.py` testing overtone frequencies, envelope decays, and output arrays. Do not modify any other existing files.
```

### Task 07: Mechanical Keyboard & Switch Foley Suite
- **Implementation File**: `vibmo/audio/generators/sfx_keyboard_foley_suite.py`
- **Test File**: `tests/audio/test_sfx_keyboard_foley_suite.py`
- **Prompt**:
```text
Implement a procedural Mechanical Keyboard & Switch Foley generator suite in `vibmo/audio/generators/sfx_keyboard_foley_suite.py` producing 48kHz float32 NumPy audio arrays.
Create a class `KeyboardFoleySuite` with static methods:
1. `clicky_blue_switch(duration=0.06)`: Cherry MX Blue clicky tactile switch with dual click mechanism (click + bottom-out).
2. `tactile_brown_switch(duration=0.05)`: Muffled tactile bump switch sound.
3. `linear_red_switch(duration=0.04)`: Smooth acoustic linear switch bottom-out thud.
4. `spacebar_thud(duration=0.09)`: Deep acoustic stabilizer bar resonance and key rebound.
5. `typewriter_bell(duration=0.6)`: Classic mechanical typewriter carriage return bell ding.
Write isolated unit tests in `tests/audio/test_sfx_keyboard_foley_suite.py` testing attack transients and duration checks. Do not modify any other existing files.
```

### Task 08: Sci-Fi Drone & Spacecraft Atmosphere Suite
- **Implementation File**: `vibmo/audio/generators/sfx_ambient_drone_suite.py`
- **Test File**: `tests/audio/test_sfx_ambient_drone_suite.py`
- **Prompt**:
```text
Implement a procedural Sci-Fi Drone & Atmospheric Sound generator suite in `vibmo/audio/generators/sfx_ambient_drone_suite.py` producing 48kHz float32 NumPy audio arrays.
Create a class `AmbientDroneSuite` with static methods:
1. `dark_scifi_drone(duration=5.0, root_freq=55.0)`: Multi-oscillator detuned sub drone with slow harmonic phase movement.
2. `warp_drive_hum(duration=4.0, rpm=120.0)`: Throbbing spacecraft hyperdrive hum with stereo rotary phase.
3. `server_room_fan_hum(duration=4.0)`: Realistic server farm cooling air ventilation noise with low frequency resonant hums.
4. `ethereal_sub_pad(duration=6.0, chord="minor9")`: Warm lush evolving analog synth pad.
Write isolated unit tests in `tests/audio/test_sfx_ambient_drone_suite.py` verifying continuous looping stability, sample rate, and stereo/mono channels. Do not modify any other existing files.
```

### Task 09: Camera Shutter, Mirror Slap & Film Advance Suite
- **Implementation File**: `vibmo/audio/generators/sfx_camera_shutter_suite.py`
- **Test File**: `tests/audio/test_sfx_camera_shutter_suite.py`
- **Prompt**:
```text
Implement a procedural Camera Shutter & Mechanical Foley generator suite in `vibmo/audio/generators/sfx_camera_shutter_suite.py` producing 48kHz float32 NumPy audio arrays.
Create a class `CameraShutterSuite` with static methods:
1. `dslr_mirror_slap(duration=0.16)`: Professional DSLR reflex mirror flip-up and mechanical curtain snap.
2. `vintage_motor_advance(duration=0.65)`: 1980s 35mm camera motorized film winding motor buzz.
3. `smartphone_snap_flash(duration=0.12)`: Crisp synthetic digital camera shutter snapshot.
4. `polaroid_eject(duration=0.85)`: Instant camera motorized print ejection whir and gear friction.
Write isolated unit tests in `tests/audio/test_sfx_camera_shutter_suite.py` testing envelope parameters and audio bounds. Do not modify any other existing files.
```

### Task 10: Analog Vinyl Crackle, Dust & Needle Suite
- **Implementation File**: `vibmo/audio/generators/sfx_vinyl_crackle_suite.py`
- **Test File**: `tests/audio/test_sfx_vinyl_crackle_suite.py`
- **Prompt**:
```text
Implement a procedural Analog Vinyl Crackle & Lo-Fi Texture generator suite in `vibmo/audio/generators/sfx_vinyl_crackle_suite.py` producing 48kHz float32 NumPy audio arrays.
Create a class `VinylCrackleSuite` with static methods:
1. `vinyl_surface_hiss(duration=4.0, noise_floor=0.08)`: Warm analog turntable vinyl surface noise and groove friction.
2. `dust_pops(duration=4.0, pop_density=12.0)`: Random non-periodic micro vinyl pops and clicks.
3. `needle_drop_thump(duration=0.6)`: Acoustic turntable stylus landing on record groove with low-end rumble.
4. `analog_tape_hiss(duration=4.0, warm_color=True)`: 1/4-inch magnetic tape saturation and subtle wow/flutter.
Write isolated unit tests in `tests/audio/test_sfx_vinyl_crackle_suite.py` testing noise characteristics, sample rate, and output format. Do not modify any other existing files.
```

### Task 11: Retro Arcade Laser & Plasma Pulse Suite
- **Implementation File**: `vibmo/audio/generators/sfx_laser_plasma_suite.py`
- **Test File**: `tests/audio/test_sfx_laser_plasma_suite.py`
- **Prompt**:
```text
Implement a procedural Retro Laser & Energy Weapon sound generator suite in `vibmo/audio/generators/sfx_laser_plasma_suite.py` producing 48kHz float32 NumPy audio arrays.
Create a class `LaserPlasmaSuite` with static methods:
1. `arcade_laser_zap(duration=0.18, f_start=3000.0, f_end=150.0)`: Classic fast downward exponential pitch zap.
2. `plasma_pulse_blast(duration=0.32)`: Resonant sci-fi plasma rifle blast with trailing energy ionization sizzle.
3. `energy_beam_charge(duration=1.2)`: Accelerating ascending oscillator charge-up hum.
4. `shield_deflect_ping(duration=0.25)`: High-energy magnetic shield deflection ping with harmonic ring.
Write isolated unit tests in `tests/audio/test_sfx_laser_plasma_suite.py` verifying frequency modulation and output validities. Do not modify any other existing files.
```

### Task 12: Liquid Droplet, Viscous Bubbles & Water Flow Suite
- **Implementation File**: `vibmo/audio/generators/sfx_liquid_bubbles_suite.py`
- **Test File**: `tests/audio/test_sfx_liquid_bubbles_suite.py`
- **Prompt**:
```text
Implement a procedural Liquid & Bubble Foley sound generator suite in `vibmo/audio/generators/sfx_liquid_bubbles_suite.py` producing 48kHz float32 NumPy audio arrays.
Create a class `LiquidBubblesSuite` with static methods:
1. `liquid_drop_splash(duration=0.15, resonant_pitch=1200.0)`: Single water droplet impact with rising pitch bubble ring.
2. `viscous_pop_bubble(duration=0.09)`: Playful bubbly UI toggle pop with rounded low-mid resonance.
3. `submerged_bubble_cluster(duration=0.6, bubble_count=10)`: Effervescent sparkling soda bubble stream.
4. `water_pour_stream(duration=2.0)`: Continuous organic pouring liquid stream with fluctuating frequency modes.
Write isolated unit tests in `tests/audio/test_sfx_liquid_bubbles_suite.py` testing wave outputs and physical model parameters. Do not modify any other existing files.
```

### Task 13: Emergency Klaxon, Alert & Siren Suite
- **Implementation File**: `vibmo/audio/generators/sfx_alarm_siren_suite.py`
- **Test File**: `tests/audio/test_sfx_alarm_siren_suite.py`
- **Prompt**:
```text
Implement a procedural Emergency Alarm & Siren sound generator suite in `vibmo/audio/generators/sfx_alarm_siren_suite.py` producing 48kHz float32 NumPy audio arrays.
Create a class `AlarmSirenSuite` with static methods:
1. `emergency_klaxon_sweep(duration=1.5, f_low=350.0, f_high=950.0)`: Industrial warning klaxon horn with triangle frequency modulation.
2. `nuclear_countdown_beep(duration=0.25, freq=1400.0)`: Urgent electronic security countdown beep with square sub-harmonic.
3. `security_chirp_alarm(duration=0.8, pulses=4)`: Fast multi-burst car security chirp sequence.
4. `biohazard_pulse_siren(duration=2.0)`: Dystopian deep sci-fi biohazard strobe siren.
Write isolated unit tests in `tests/audio/test_sfx_alarm_siren_suite.py` testing modulation cycles and array consistency. Do not modify any other existing files.
```

### Task 14: Card Shuffling, Paper Rustle & Flip Suite
- **Implementation File**: `vibmo/audio/generators/sfx_paper_card_suite.py`
- **Test File**: `tests/audio/test_sfx_paper_card_suite.py`
- **Prompt**:
```text
Implement a procedural Card & Paper Foley sound generator suite in `vibmo/audio/generators/sfx_paper_card_suite.py` producing 48kHz float32 NumPy audio arrays.
Create a class `PaperCardSuite` with static methods:
1. `card_shuffle_slide(duration=0.22)`: Crisp poker card sliding off a deck across a smooth surface.
2. `paper_flip_rustle(duration=0.18)`: Organic notebook paper turn rustle with high-frequency friction noise.
3. `sheet_unfold_crinkle(duration=0.35)`: Origami/map paper unfolding crinkle texture.
4. `deck_snap_slide(duration=0.12)`: Snappy tactile card snap on a UI dashboard.
Write isolated unit tests in `tests/audio/test_sfx_paper_card_suite.py` testing envelope curves and noise filters. Do not modify any other existing files.
```

### Task 15: Chiptune 8-Bit Retro Game SFX Suite
- **Implementation File**: `vibmo/audio/generators/sfx_retro_8bit_suite.py`
- **Test File**: `tests/audio/test_sfx_retro_8bit_suite.py`
- **Prompt**:
```text
Implement an authentic 8-Bit Chiptune sound generator suite in `vibmo/audio/generators/sfx_retro_8bit_suite.py` producing 48kHz float32 NumPy audio arrays using NES-style pulse (12.5%, 25%, 50% duty), triangle, and 1-bit LFSR noise channels.
Create a class `Retro8BitSuite` with static methods:
1. `jump_boing(duration=0.20, f_start=150.0, f_end=600.0)`: 8-bit Mario-style jump sweep.
2. `coin_pickup(duration=0.30)`: Two-tone rapid arpeggio (B5 -> E6) pulse wave coin collect.
3. `power_down_slide(duration=0.45)`: Descending chromatic death/failure slide.
4. `level_up_fanfare(duration=0.8)`: 4-note victory flourish with square wave harmonics.
Write isolated unit tests in `tests/audio/test_sfx_retro_8bit_suite.py` verifying duty cycles, pulse waves, and output integrity. Do not modify any other existing files.
```

---

## Section 2: Non-Static Animated Backgrounds & Dynamic Backdrops (Tasks 16–30)
*Target: 50–60 dynamic living backdrops with continuous time-varying Cairo/NumPy motion*

### Task 16: Fluid Mesh Gradient & Organic Plasma Waves
- **Implementation File**: `vibmo/fx/backgrounds/bg_mesh_gradient_flow.py`
- **Test File**: `tests/fx/test_bg_mesh_gradient_flow.py`
- **Prompt**:
```text
Implement continuous, non-static Animated Mesh Gradient Backdrops in `vibmo/fx/backgrounds/bg_mesh_gradient_flow.py` subclassing `vibmo.scene.node.Node`.
Implement 3 animated background classes:
1. `MeshGradientFlow`: 4-point to 9-point multi-color control mesh where gradient color control nodes orbit organically using harmonic sine/cosine paths as time advances.
2. `AuroraGradientWave`: Ethereal green/cyan/purple ribbon wave curtains that undulate across dark backdrops.
3. `LiquidPlasmaBackdrop`: Animated Perlin/Simplex-style organic color plasma field.
Support configurable color stops, speed multiplier, resolution scale, and auto-resize.
Write isolated unit tests in `tests/fx/test_bg_mesh_gradient_flow.py` rendering frames at t=0.0 and t=1.5, asserting non-identical pixel surface outputs (verifying dynamic non-static movement). Do not modify any other existing files.
```

### Task 17: 3D Synthwave Cyber Grid Horizon & Neon Sun
- **Implementation File**: `vibmo/fx/backgrounds/bg_cyber_grid_horizon.py`
- **Test File**: `tests/fx/test_bg_cyber_grid_horizon.py`
- **Prompt**:
```text
Implement an animated 3D Synthwave Perspective Grid & Neon Sun backdrop suite in `vibmo/fx/backgrounds/bg_cyber_grid_horizon.py` subclassing `Node`.
Implement 3 animated classes:
1. `CyberGridHorizon`: Perspective 3D ground plane with moving neon glowing grid lines scrolling toward the camera with adjustable speed and horizon pitch.
2. `NeonSunBackdrop`: Segmented Venetian-blind style sunset orb with animated horizontal stripe bars and radial corona glow.
3. `WireframeMountainHorizon`: Distant wireframe neon mountain terrain silhouettes undulating with low-frequency noise.
Write isolated unit tests in `tests/fx/test_bg_cyber_grid_horizon.py` testing frame rendering, signal parameters, and non-static temporal progression. Do not modify any other existing files.
```

### Task 18: Cosmic Nebula & Starfield Warp Drift
- **Implementation File**: `vibmo/fx/backgrounds/bg_cosmic_nebula.py`
- **Test File**: `tests/fx/test_bg_cosmic_nebula.py`
- **Prompt**:
```text
Implement continuous deep-space animated backdrops in `vibmo/fx/backgrounds/bg_cosmic_nebula.py` subclassing `Node`.
Implement 3 animated classes:
1. `CosmicNebulaBackdrop`: Multi-layered volumetric cosmic interstellar gas clouds drifting and rotating with deep purple, magenta, and cyan hues.
2. `StarfieldWarpDrift`: 3D perspective stars accelerating and streaking outward from center with parallax depth layers.
3. `ConstellationGrid`: Drifting geometric stars connected by dynamic proximity-based glowing line segments.
Write isolated unit tests in `tests/fx/test_bg_cosmic_nebula.py` validating node instantiation, Cairo context drawing, and time-dependent star positions. Do not modify any other existing files.
```

### Task 19: Isometric City Grid & Pulsing Data Highways
- **Implementation File**: `vibmo/fx/backgrounds/bg_isometric_city_grid.py`
- **Test File**: `tests/fx/test_bg_isometric_city_grid.py`
- **Prompt**:
```text
Implement an animated Isometric Tech City Grid backdrop suite in `vibmo/fx/backgrounds/bg_isometric_city_grid.py` subclassing `Node`.
Implement 3 animated classes:
1. `IsometricCityGridBackdrop`: Isometric 2.5D grid of minimalist building monoliths with glowing rooftop lights.
2. `PulsingDataHighways`: Glowing neon data packets racing along grid lines and intersecting pathways.
3. `ServerRackMatrixBackdrop`: Isometric datacenter rack towers with blinking green/cyan status LEDs.
Write isolated unit tests in `tests/fx/test_bg_isometric_city_grid.py` verifying layout bounds, cairo isometric projection transforms, and animation frames. Do not modify any other existing files.
```

### Task 20: Animated Fluid Water Caustics & Prismatic Rays
- **Implementation File**: `vibmo/fx/backgrounds/bg_fluid_caustics.py`
- **Test File**: `tests/fx/test_bg_fluid_caustics.py`
- **Prompt**:
```text
Implement realistic animated Underwater Caustics & Light Rays in `vibmo/fx/backgrounds/bg_fluid_caustics.py` subclassing `Node`.
Implement 3 animated classes:
1. `FluidWaterCaustics`: Interlocking shimmering swimming pool water caustics with refractive voronoi cell boundaries animated over time.
2. `UnderwaterLightRays`: Volumetric sunbeams piercing water surface from top-down with gentle angular swaying.
3. `PrismaticIridescentWaves`: Shifting rainbow oil-slick sheen flowing organically over dark canvas.
Write isolated unit tests in `tests/fx/test_bg_fluid_caustics.py` asserting pixel rendering, color channels, and time variance. Do not modify any other existing files.
```

### Task 21: Matrix Digital Rain & Binary Stream Columns
- **Implementation File**: `vibmo/fx/backgrounds/bg_digital_matrix_rain.py`
- **Test File**: `tests/fx/test_bg_digital_matrix_rain.py`
- **Prompt**:
```text
Implement an authentic animated Matrix Digital Code Rain backdrop suite in `vibmo/fx/backgrounds/bg_digital_matrix_rain.py` subclassing `Node`.
Implement 3 animated classes:
1. `DigitalMatrixRainBackdrop`: Cascading vertical columns of glowing green katakana/alphanumeric glyphs with bright white leading drops and fading phosphor trails.
2. `BinaryStreamBackdrop`: Futuristic high-speed cyan stream of 0s and 1s with variable column speeds.
3. `HexCodeColumnBackdrop`: Cryptographic hexadecimal memory dump columns with random character mutating glitches.
Write isolated unit tests in `tests/fx/test_bg_digital_matrix_rain.py` validating column state management, glyph recycling, and drawing correctness. Do not modify any other existing files.
```

### Task 22: Animated Topographic Elevation Contours
- **Implementation File**: `vibmo/fx/backgrounds/bg_topographic_contours.py`
- **Test File**: `tests/fx/test_bg_topographic_contours.py`
- **Prompt**:
```text
Implement animated Topographic Map & Elevation Contour backdrops in `vibmo/fx/backgrounds/bg_topographic_contours.py` subclassing `Node`.
Implement 3 animated classes:
1. `AnimatedTopographicContours`: Smooth vector isolines derived from multi-octave 2D noise slowly shifting and breathing over time.
2. `BathymetricMapBackdrop`: Tiered depth-colored stepped elevation slices with subtle edge glow.
3. `RadarElevationSweep`: Topographic map illuminated by a rotating 360-degree radar beam sweep.
Write isolated unit tests in `tests/fx/test_bg_topographic_contours.py` validating curve generation, cairo path closing, and animation progression. Do not modify any other existing files.
```

### Task 23: Neural Synapse & Plexus Constellation Network
- **Implementation File**: `vibmo/fx/backgrounds/bg_particle_constellation.py`
- **Test File**: `tests/fx/test_bg_particle_constellation.py`
- **Prompt**:
```text
Implement an animated Neural Network & Plexus Constellation backdrop suite in `vibmo/fx/backgrounds/bg_particle_constellation.py` subclassing `Node`.
Implement 3 animated classes:
1. `ParticleConstellationNetwork`: Autonomous 2D particle nodes drifting with Brownian motion; dynamic glowing connection lines form when nodes come within proximity distance.
2. `SynapseNeuralGraph`: Layered AI neural network nodes with animated action potential pulses firing along synaptic connections.
3. `PlexusDistanceLines`: Geometric floating polyhedron nodes with distance-attenuated alpha line webbing.
Write isolated unit tests in `tests/fx/test_bg_particle_constellation.py` verifying particle velocity updates, boundary bouncing, and distance threshold filtering. Do not modify any other existing files.
```

### Task 24: Drifting Bokeh Orbs & Anamorphic Lens Flare Ambience
- **Implementation File**: `vibmo/fx/backgrounds/bg_bokeh_light_bubbles.py`
- **Test File**: `tests/fx/test_bg_bokeh_light_bubbles.py`
- **Prompt**:
```text
Implement continuous cinematic Bokeh & Ambient Particle backdrops in `vibmo/fx/backgrounds/bg_bokeh_light_bubbles.py` subclassing `Node`.
Implement 3 animated classes:
1. `DriftingBokehOrbs`: Soft, out-of-focus hexagonal and circular aperture bokeh discs drifting vertically and floating with depth-of-field blur.
2. `AnamorphicLensGleamBackdrop`: Subtle horizontal chromatic streaks and lens glints drifting across dark background.
3. `GoldenDustAmbience`: Shimmering micro-dust motes catching directional light rays with organic turbulence.
Write isolated unit tests in `tests/fx/test_bg_bokeh_light_bubbles.py` testing blend modes, opacity gradients, and particle lifecycle. Do not modify any other existing files.
```

### Task 25: Voronoi Cell Evolution & Geometric Tessellation
- **Implementation File**: `vibmo/fx/backgrounds/bg_geometric_tessellation.py`
- **Test File**: `tests/fx/test_bg_geometric_tessellation.py`
- **Prompt**:
```text
Implement animated Geometric Tessellations & Cellular backdrops in `vibmo/fx/backgrounds/bg_geometric_tessellation.py` subclassing `Node`.
Implement 3 animated classes:
1. `VoronoiCellEvolution`: Real-time evolving 2D Voronoi cellular diagram with undulating cell seed points and glowing borders.
2. `PenroseTilingFlow`: Aperiodic Penrose tile patterns morphing with non-repeating rotational symmetry.
3. `HexagonalHoneyGridPulse`: Hexagonal honeycomb lattice with breathing radial color waves rippling outward.
Write isolated unit tests in `tests/fx/test_bg_geometric_tessellation.py` testing mathematical tessellation formulas and cairo polygon drawing. Do not modify any other existing files.
```

### Task 26: CRT Phosphor Scanlines & VHS Noise Ambience
- **Implementation File**: `vibmo/fx/backgrounds/bg_retro_crt_scanlines.py`
- **Test File**: `tests/fx/test_bg_retro_crt_scanlines.py`
- **Prompt**:
```text
Implement an animated Retro CRT & Analog Video Noise backdrop suite in `vibmo/fx/backgrounds/bg_retro_crt_scanlines.py` subclassing `Node`.
Implement 3 animated classes:
1. `CrtPhosphorScanlineBackdrop`: Moving horizontal cathode ray tube scanlines with rolling vertical retrace sync bars and subtle curvature vignette.
2. `TVSignalNoiseStatic`: Dynamic analog TV static snow with adjustable grain coarseness and frequency hum.
3. `VcrBlueScreenGlitch`: Nostalgic 1990s VCR bright blue screen with animated tracking noise bars at bottom.
Write isolated unit tests in `tests/fx/test_bg_retro_crt_scanlines.py` verifying scanline math, noise generation, and non-static temporal output. Do not modify any other existing files.
```

### Task 27: Hyperspace Warp Tunnel & Vortex Flight
- **Implementation File**: `vibmo/fx/backgrounds/bg_hyperspace_tunnel.py`
- **Test File**: `tests/fx/test_bg_hyperspace_tunnel.py`
- **Prompt**:
```text
Implement an animated Hyperspace Warp Tunnel backdrop suite in `vibmo/fx/backgrounds/bg_hyperspace_tunnel.py` subclassing `Node`.
Implement 3 animated classes:
1. `HyperspaceWarpTunnel`: Concentric rotating wireframe rings rushing towards camera creating an infinite fly-through wormhole effect.
2. `HexagonalSpeedTunnel`: Sci-fi hexagonal corridor panels speeding past with neon edge trim.
3. `InfiniteZoomVortex`: Spiral logarithmic vortex rotating and drawing the eye inward toward a center event horizon.
Write isolated unit tests in `tests/fx/test_bg_hyperspace_tunnel.py` verifying 3D perspective projection math and infinite loop continuity. Do not modify any other existing files.
```

### Task 28: Golden Hour Horizon Glow & Atmospheric Haze
- **Implementation File**: `vibmo/fx/backgrounds/bg_sunset_horizon_glow.py`
- **Test File**: `tests/fx/test_bg_sunset_horizon_glow.py`
- **Prompt**:
```text
Implement an animated Golden Hour & California Sunset horizon backdrop suite in `vibmo/fx/backgrounds/bg_sunset_horizon_glow.py` subclassing `Node`.
Implement 3 animated classes:
1. `CalifornianSunsetBackdrop`: Deep amber, coral, and violet multi-stop horizon gradient with warm breathing sun glow and subtle heat shimmer.
2. `GoldenHourSkyGradient`: Shifting twilight sky with slow diurnal cycle time color transition.
3. `AtmosphericHazeHorizon`: Minimalist misty horizon with layered silhouetted mountain waves.
Write isolated unit tests in `tests/fx/test_bg_sunset_horizon_glow.py` validating color stop interpolation, gradient rendering, and parameters. Do not modify any other existing files.
```

### Task 29: Circuit Board Traces & Microchip Current Flow
- **Implementation File**: `vibmo/fx/backgrounds/bg_circuit_board_traces.py`
- **Test File**: `tests/fx/test_bg_circuit_board_traces.py`
- **Prompt**:
```text
Implement an animated Printed Circuit Board (PCB) & Microchip Current Flow backdrop in `vibmo/fx/backgrounds/bg_circuit_board_traces.py` subclassing `Node`.
Implement 3 animated classes:
1. `PcbCircuitTracesFlow`: Matt dark green/black PCB substrate with golden 45-degree angle circuit traces and electric current pulses traveling along routes.
2. `MicrochipLogicPulse`: Central silicon die radiating electric logic bus signals across surrounding trace pins.
3. `CopperBusCurrentBackdrop`: Glowing bus lines pulsing with digital clock signals.
Write isolated unit tests in `tests/fx/test_bg_circuit_board_traces.py` testing trace path geometry, pulse motion, and cairo stroke rendering. Do not modify any other existing files.
```

### Task 30: Minimalist Apple Studio Cyclorama & Frosted Glass Horizon
- **Implementation File**: `vibmo/fx/backgrounds/bg_minimal_studio_infinity.py`
- **Test File**: `tests/fx/test_bg_minimal_studio_infinity.py`
- **Prompt**:
```text
Implement an ultra-clean Minimalist Studio Cyclorama & Horizon backdrop suite in `vibmo/fx/backgrounds/bg_minimal_studio_infinity.py` subclassing `Node`.
Implement 3 animated classes:
1. `AppleStudioInfinityCyc`: Infinite curved photography cyclorama studio with soft overhead softbox lighting falloff and floor contact reflection.
2. `SoftStageSpotlightBackdrop`: Gentle elliptical stage spotlight that breathes and glides with camera focus.
3. `FrostedGlassHorizon`: Minimalist split horizon with frosted glass blur separation line.
Write isolated unit tests in `tests/fx/test_bg_minimal_studio_infinity.py` testing lighting falloff shaders, gradient radius math, and cairo drawing. Do not modify any other existing files.
```

---

## Section 3: Hardware Chassis, Device Enclosures & Mockup Suites (Tasks 31–45)
*Target: 45–60 hardware mockups and physical device frames*

### Task 31: Foldable & Dual-Screen Device Mockup Suite
- **Implementation File**: `vibmo/product/hardware/hw_foldable_device_suite.py`
- **Test File**: `tests/product/test_hw_foldable_device_suite.py`
- **Prompt**:
```text
Implement a complete Foldable & Dual-Screen Device Mockup suite in `vibmo/product/hardware/hw_foldable_device_suite.py` subclassing `vibmo.scene.node.Node`.
Implement 4 components:
1. `FoldableBookPhone`: Samsung Galaxy Fold-style device with inner continuous display, subtle center hinge crease shadow, and slim bezels.
2. `ClamshellFlipPhone`: Vertical flip phone with top/bottom split view and dynamic hinge angle.
3. `DualScreenBookDevice`: Surface Duo style dual display with physical center hinge separation.
4. `HingeCreaseIndicator`: Animatable glass specular sheen running down the folding seam.
Include `.add_screen_content(*nodes)` methods with automatic content clipping and drop shadows.
Write isolated unit tests in `tests/product/test_hw_foldable_device_suite.py` testing dimensions, inner screen bounds, and cairo drawing. Do not modify any other existing files.
```

### Task 32: OLED Smart TV & Cinema Display Frame Suite
- **Implementation File**: `vibmo/product/hardware/hw_smart_tv_display_suite.py`
- **Test File**: `tests/product/test_hw_smart_tv_display_suite.py`
- **Prompt**:
```text
Implement an OLED Smart TV & Cinema Display Mockup suite in `vibmo/product/hardware/hw_smart_tv_display_suite.py` subclassing `Node`.
Implement 4 components:
1. `OledSmartTvFrame`: 65-inch ultra-thin razor bezel TV with aluminum bottom lip and status indicator LED.
2. `CurvedCinemaDisplay`: Wide curved display with subtle panoramic edge compression.
3. `WallMountedDisplayShadow`: Deep soft ambient wall-cast drop shadow for wall-mounted TV demos.
4. `FloatingTvStand`: Minimalist metallic desktop pedestal stand.
Support `.add_screen_content(*nodes)` with 16:9 aspect auto-scaling.
Write isolated unit tests in `tests/product/test_hw_smart_tv_display_suite.py` verifying aspect ratios, bezel calculations, and cairo drawing. Do not modify any other existing files.
```

### Task 33: Multi-Monitor Dual & Triple Developer Rig Suite
- **Implementation File**: `vibmo/product/hardware/hw_multi_monitor_suite.py`
- **Test File**: `tests/product/test_hw_multi_monitor_suite.py`
- **Prompt**:
```text
Implement a Multi-Monitor Developer Rig Mockup suite in `vibmo/product/hardware/hw_multi_monitor_suite.py` subclassing `Node`.
Implement 3 components:
1. `DualDeveloperMonitors`: Side-by-side dual 27-inch 4K developer monitors with configurable inward angle.
2. `VerticalSidecarDisplay`: Horizontal primary display paired with a vertical 9:16 portrait code monitor.
3. `TripleCurvedSimulatorDeck`: Triple panoramic wrap-around display cockpit.
Support assigning distinct content trees to `.left_screen`, `.center_screen`, and `.right_screen`.
Write isolated unit tests in `tests/product/test_hw_multi_monitor_suite.py` validating screen coordinates, content nesting, and drawing. Do not modify any other existing files.
```

### Task 34: Spatial Computing Glass Visor (Vision Pro / Quest) Suite
- **Implementation File**: `vibmo/product/hardware/hw_spatial_visor_suite.py`
- **Test File**: `tests/product/test_hw_spatial_visor_suite.py`
- **Prompt**:
```text
Implement a Spatial Computing & VR Visor mockup suite in `vibmo/product/hardware/hw_spatial_visor_suite.py` subclassing `Node`.
Implement 3 components:
1. `VisionProSpatialGlassVisor`: Apple Vision Pro style curved 3D laminated glass visor with aluminum frame, headband straps, and EyeSight lenticular shimmer.
2. `QuestGoggleFrame`: VR headset frame with front tracking camera sensors.
3. `SpatialHudCurvedProjection`: Floating cylindrical HUD projection plane with spatial depth blur.
Support `.add_screen_content(*nodes)` inside the spatial HUD window.
Write isolated unit tests in `tests/product/test_hw_spatial_visor_suite.py` testing glass specular geometry and content containment. Do not modify any other existing files.
```

### Task 35: Rugged Titanium Smartwatch & Classic Round Dial Suite
- **Implementation File**: `vibmo/product/hardware/hw_smartwatch_rugged_suite.py`
- **Test File**: `tests/product/test_hw_smartwatch_rugged_suite.py`
- **Prompt**:
```text
Implement a Smartwatch Hardware Mockup suite in `vibmo/product/hardware/hw_smartwatch_rugged_suite.py` subclassing `Node`.
Implement 3 components:
1. `TitaniumRuggedWatch`: Apple Watch Ultra style aerospace titanium casing with orange action button, raised bezel, and ribbed ocean band.
2. `MinimalistSquareWatch`: Sleek aluminum square rounded smartwatch with glass 2.5D curve edge.
3. `ClassicRoundSmartwatchFace`: Circular smartwatch dial with rotating bezel notches.
Support `.add_screen_content(*nodes)` with circular and rounded-rect screen clipping masks.
Write isolated unit tests in `tests/product/test_hw_smartwatch_rugged_suite.py` verifying screen bounds and cairo clipping. Do not modify any other existing files.
```

### Task 36: 49-Inch Super Ultrawide Curved Monitor Suite
- **Implementation File**: `vibmo/product/hardware/hw_super_ultrawide_suite.py`
- **Test File**: `tests/product/test_hw_super_ultrawide_suite.py`
- **Prompt**:
```text
Implement a 49-Inch 32:9 Super Ultrawide Curved Monitor mockup suite in `vibmo/product/hardware/hw_super_ultrawide_suite.py` subclassing `Node`.
Implement 3 components:
1. `Curved49InchUltrawide`: 32:9 aspect curved gaming/productivity monitor with subtle 1000R panoramic curvature and slim bezels.
2. `GamerBackGlowRgbLed`: Rear ambient RGB bias lighting aura projecting against the back wall.
3. `MonitorArmPivotingBase`: Heavy-duty gas-spring desk clamp monitor arm.
Support `.add_screen_content(*nodes)` with optional 3-column split layout slots (`col_1`, `col_2`, `col_3`).
Write isolated unit tests in `tests/product/test_hw_super_ultrawide_suite.py` verifying dimensions, 32:9 ratio, and cairo rendering. Do not modify any other existing files.
```

### Task 37: POS Retail Payment Terminal & NFC Reader Suite
- **Implementation File**: `vibmo/product/hardware/hw_pos_retail_suite.py`
- **Test File**: `tests/product/test_hw_pos_retail_suite.py`
- **Prompt**:
```text
Implement a Point-of-Sale (POS) & Retail Payment Hardware suite in `vibmo/product/hardware/hw_pos_retail_suite.py` subclassing `Node`.
Implement 4 components:
1. `NfcHandheldPosTerminal`: Square / Stripe style sleek handheld touchscreen POS terminal with angled display.
2. `CountertopRegisterScreen`: Angled merchant/customer dual-sided countertop register stand.
3. `ThermalReceiptSlot`: Top receipt printer slot with animated paper receipt sliding out.
4. `TapPaymentSensor`: Contactless NFC wave target with pulsing green/blue LED payment indicators.
Write isolated unit tests in `tests/product/test_hw_pos_retail_suite.py` testing payment animations, card screen bounds, and drawing. Do not modify any other existing files.
```

### Task 38: Handheld Gaming Console (Steam Deck / Switch) Suite
- **Implementation File**: `vibmo/product/hardware/hw_gaming_handheld_suite.py`
- **Test File**: `tests/product/test_hw_gaming_handheld_suite.py`
- **Prompt**:
```text
Implement a Handheld Gaming Console hardware mockup suite in `vibmo/product/hardware/hw_gaming_handheld_suite.py` subclassing `Node`.
Implement 3 components:
1. `SteamDeckHandheldChassis`: Ergonomic dual-grip PC gaming handheld with left/right thumbsticks, D-pad, ABXY buttons, and trackpads.
2. `SwitchJoyConFrame`: Nintendo Switch style console with detachable red and neon blue Joy-Con rails.
3. `RetroGameBoyEnclosure`: 1989 vertical classic dot-matrix handheld chassis with purple A/B buttons.
Support `.add_screen_content(*nodes)` with screen display clipping.
Write isolated unit tests in `tests/product/test_hw_gaming_handheld_suite.py` validating controller button coordinates and screen dimensions. Do not modify any other existing files.
```

### Task 39: Cyberdeck Retro-Futuristic Terminal Suite
- **Implementation File**: `vibmo/product/hardware/hw_cyberdeck_terminal_suite.py`
- **Test File**: `tests/product/test_hw_cyberdeck_terminal_suite.py`
- **Prompt**:
```text
Implement a Cyberpunk Cyberdeck Hardware Mockup suite in `vibmo/product/hardware/hw_cyberdeck_terminal_suite.py` subclassing `Node`.
Implement 4 components:
1. `CyberdeckMechanicalKeyboard`: Rugged industrial military-grade chassis with exposed mechanical keycaps and carry handle.
2. `PopUpLcdScreen`: Angled ultra-wide articulating LCD screen connected via heavy metal hinges.
3. `IndustrialBumperCase`: Shock-absorbent rubberized corner bumpers and hazard stripe accents.
4. `PatchCablesAndAntenna`: Decorative coiled BNC patch cables and pivoting brass antenna.
Write isolated unit tests in `tests/product/test_hw_cyberdeck_terminal_suite.py` testing component hierarchy and cairo drawing. Do not modify any other existing files.
```

### Task 40: Automotive Touchscreen & CarPlay Dashboard Suite
- **Implementation File**: `vibmo/product/hardware/hw_automotive_cockpit_suite.py`
- **Test File**: `tests/product/test_hw_automotive_cockpit_suite.py`
- **Prompt**:
```text
Implement an Automotive Cockpit & Infotainment Screen mockup suite in `vibmo/product/hardware/hw_automotive_cockpit_suite.py` subclassing `Node`.
Implement 3 components:
1. `TeslaCenterTouchscreen`: 15-inch landscape floating center console touchscreen with minimal matte black bezels.
2. `CarPlayDashboardPill`: Rounded dashboard cluster with horizontal split widget layout (maps + music + navigation pill).
3. `DigitalGaugeClusterHud`: Driver instrument digital cluster with speed needle, battery percentage, and ADAS car lane visualization.
Write isolated unit tests in `tests/product/test_hw_automotive_cockpit_suite.py` validating infotainment screen dimensions and drawing. Do not modify any other existing files.
```

### Task 41: DSLR Camera Viewfinder & Cinema HUD Suite
- **Implementation File**: `vibmo/product/hardware/hw_camera_viewfinder_suite.py`
- **Test File**: `tests/product/test_hw_camera_viewfinder_suite.py`
- **Prompt**:
```text
Implement a Camera Viewfinder & Production Rig Mockup suite in `vibmo/product/hardware/hw_camera_viewfinder_suite.py` subclassing `Node`.
Implement 3 components:
1. `DslrCameraViewfinderHud`: Professional camera viewfinder overlay with autofocus target brackets, rule-of-thirds grid, battery, ISO, shutter speed, and audio VU meters.
2. `CinemaCameraCageRig`: Aluminum camera cage with top handle, 15mm rails, matte box, and side battery plate.
3. `DroneGimbalTelemetryHud`: Aerial drone flight telemetry HUD with artificial horizon, altitude tape, and GPS coordinate satellites.
Write isolated unit tests in `tests/product/test_hw_camera_viewfinder_suite.py` testing HUD layout geometry, cairo stroke drawing, and overlay modes. Do not modify any other existing files.
```

### Task 42: Minimalist E-Ink Tablet & Stylus Pen Suite
- **Implementation File**: `vibmo/product/hardware/hw_eink_tablet_suite.py`
- **Test File**: `tests/product/test_hw_eink_tablet_suite.py`
- **Prompt**:
```text
Implement a Minimalist E-Ink Tablet & Stylus Mockup suite in `vibmo/product/hardware/hw_eink_tablet_suite.py` subclassing `Node`.
Implement 3 components:
1. `PaperEInkReaderFrame`: ReMarkable / Kindle Scribe style paper-like e-ink digital notepad with wide left leather grip bezel and textured white screen.
2. `StylusPenMockup`: Precision digital stylus pen magnetically docked to side bezel.
3. `TextureMatteScreenBezel`: Subtle paper tooth grain texture and low-contrast e-ink refresh artifact simulator.
Write isolated unit tests in `tests/product/test_hw_eink_tablet_suite.py` testing tablet bounds, stylus geometry, and cairo drawing. Do not modify any other existing files.
```

### Task 43: Smart Home Hub & Acoustic Speaker Display Suite
- **Implementation File**: `vibmo/product/hardware/hw_smart_home_hub_suite.py`
- **Test File**: `tests/product/test_hw_smart_home_hub_suite.py`
- **Prompt**:
```text
Implement a Smart Home Hub & IoT Device Mockup suite in `vibmo/product/hardware/hw_smart_home_hub_suite.py` subclassing `Node`.
Implement 3 components:
1. `FabricAcousticSmartHub`: Google Nest Hub style angled touchscreen mounted on a woven fabric acoustic speaker base.
2. `RoundThermostatDial`: Nest style circular glass smart thermostat with rotating temperature ring and temperature status display.
3. `WallMountSecurityKeypad`: Smart home alarm panel with numerical keypad and status LED icons.
Write isolated unit tests in `tests/product/test_hw_smart_home_hub_suite.py` validating screen slots and cairo drawing. Do not modify any other existing files.
```

### Task 44: Vintage 1990s Beige CRT Monitor & Arcade Cabinet Suite
- **Implementation File**: `vibmo/product/hardware/hw_vintage_crt_suite.py`
- **Test File**: `tests/product/test_hw_vintage_crt_suite.py`
- **Prompt**:
```text
Implement a Retro 1990s Computer & Arcade Hardware mockup suite in `vibmo/product/hardware/hw_vintage_crt_suite.py` subclassing `Node`.
Implement 3 components:
1. `1990sBeigeCrtMonitor`: Chunky beige PC monitor chassis with power button, brightness thumbwheels, degauss button, and curved glass tube.
2. `ArcadeCabinetBezel`: Retro arcade machine wooden cabinet side art and CRT bezel mask.
3. `RetroPortableTvAntenna`: 1970s portable television with rabbit-ear telescopic antennas and dual VHF/UHF rotary dials.
Write isolated unit tests in `tests/product/test_hw_vintage_crt_suite.py` validating retro enclosure proportions and screen clipping. Do not modify any other existing files.
```

### Task 45: CCTV Multi-Camera Surveillance Grid Suite
- **Implementation File**: `vibmo/product/hardware/hw_cctv_surveillance_suite.py`
- **Test File**: `tests/product/test_hw_cctv_surveillance_suite.py`
- **Prompt**:
```text
Implement a CCTV Surveillance & Security Monitoring mockup suite in `vibmo/product/hardware/hw_cctv_surveillance_suite.py` subclassing `Node`.
Implement 3 components:
1. `CctvQuadCameraGrid`: 2x2 multi-camera split matrix display with camera labels ("CAM 01 - LOBBY", "CAM 02 - VAULT"), live timestamps, and flashing red "● REC" indicator.
2. `PtzCameraTargetingHud`: Pan-tilt-zoom motion tracking target crosshairs with automated bounding box identification.
3. `BodyCamRecOverlay`: Law enforcement / security bodycam perspective overlay with date, time, and watermark.
Write isolated unit tests in `tests/product/test_hw_cctv_surveillance_suite.py` verifying grid dimensions, timestamp formatting, and cairo drawing. Do not modify any other existing files.
```

---

## Section 4: AI & SaaS Interactive UI Component Suites (Tasks 46–60)
*Target: 50–65 animated product cards and AI UI widgets*

### Task 46: LLM Token Streamer & Speed Ticker Suite
- **Implementation File**: `vibmo/product/ai/ui_token_streamer_suite.py`
- **Test File**: `tests/components/test_ui_token_streamer_suite.py`
- **Prompt**:
```text
Implement a real-time Streaming LLM Output UI Component suite in `vibmo/product/ai/ui_token_streamer_suite.py` subclassing `vibmo.scene.node.Node`.
Implement 4 components:
1. `TokenStreamerBox`: Frosted glass container that renders markdown/code tokens as they stream in sequentially.
2. `ShimmeringCaretIndicator`: Glowing cyan terminal cursor block that pulses at the insertion point.
3. `TokenSpeedVelocityCounter`: Live metric badge calculating real-time tokens/second ticker (`118.4 tok/s`).
4. `StopGenerationButton`: Compact square pill button with pulsating red stop icon and subtle hover glow.
Include `.stream_text(text: str, duration: float)` animation generator.
Write isolated unit tests in `tests/components/test_ui_token_streamer_suite.py` testing text buffer appending, token speed math, and drawing. Do not modify any other existing files.
```

### Task 47: Generative Diffusion Canvas & Prompt Suite
- **Implementation File**: `vibmo/product/ai/ui_diffusion_canvas_suite.py`
- **Test File**: `tests/components/test_ui_diffusion_canvas_suite.py`
- **Prompt**:
```text
Implement a Generative AI Image Canvas UI suite in `vibmo/product/ai/ui_diffusion_canvas_suite.py` subclassing `Node`.
Implement 4 components:
1. `DiffusionGenerationCanvas`: Image viewport with progressive unblurring / denoising step counter (`Step 18/25`).
2. `PromptAspectSelector`: Segmented pill selector (1:1, 16:9, 9:16, 4:3) with smooth animated active indicator.
3. `SeedVariationPills`: Row of 4 thumbnail variant cards with selection highlight border.
4. `MagicPromptEnhanceBar`: Shimmering iridescent text input field with "Enhance Prompt" sparkles button.
Write isolated unit tests in `tests/components/test_ui_diffusion_canvas_suite.py` testing denoising steps, layout bounds, and cairo rendering. Do not modify any other existing files.
```

### Task 48: AI Reasoning Tree-of-Thought Visualizer Suite
- **Implementation File**: `vibmo/product/ai/ui_tree_of_thought_suite.py`
- **Test File**: `tests/components/test_ui_tree_of_thought_suite.py`
- **Prompt**:
```text
Implement an AI Reasoning Tree-of-Thought (ToT) Visualizer suite in `vibmo/product/ai/ui_tree_of_thought_suite.py` subclassing `Node`.
Implement 4 components:
1. `TreeOfThoughtTree`: Hierarchical node-link graph showing branching exploration of thought paths.
2. `ReasoningNodeBranch`: Individual thought bubble card with status state (Evaluating, Valid, Pruned).
3. `ExplorationScoreBadge`: Numeric evaluation score pill (`Score: 0.94`) with emerald fill for winner.
4. `PrunedBranchFade`: Red-tinted fading dashed branch indicating rejected reasoning path.
Include `.expand_node(parent_id, child_nodes, duration)` animation method.
Write isolated unit tests in `tests/components/test_ui_tree_of_thought_suite.py` verifying tree layout algorithms, connector curves, and drawing. Do not modify any other existing files.
```

### Task 49: Multi-Agent Autonomous Team Chat Thread Suite
- **Implementation File**: `vibmo/product/ai/ui_agent_team_thread_suite.py`
- **Test File**: `tests/components/test_ui_agent_team_thread_suite.py`
- **Prompt**:
```text
Implement a Multi-Agent Autonomous Conversation Thread suite in `vibmo/product/ai/ui_agent_team_thread_suite.py` subclassing `Node`.
Implement 4 components:
1. `AgentConversationBubble`: Rich chat bubble with agent avatar, name, role badge ("Architect", "Coder", "Reviewer"), timestamp, and markdown body.
2. `ToolCallingPayloadCard`: Collapsible JSON payload box showing function call args and live execution spinner.
3. `AgentTypingWave`: 3-dot harmonic bouncing typing indicator.
4. `AgentStatusPill`: Online/Busy/Thinking indicator badge.
Write isolated unit tests in `tests/components/test_ui_agent_team_thread_suite.py` testing bubble layout stacking, height auto-expansion, and cairo drawing. Do not modify any other existing files.
```

### Task 50: Vector Embeddings Cluster & Cosine Link Suite
- **Implementation File**: `vibmo/product/ai/ui_embeddings_space_suite.py`
- **Test File**: `tests/components/test_ui_embeddings_space_suite.py`
- **Prompt**:
```text
Implement a 2D/3D Vector Embeddings Cluster visualizer in `vibmo/product/ai/ui_embeddings_space_suite.py` subclassing `Node`.
Implement 4 components:
1. `EmbeddingScatterCluster`: Clustered point cloud of high-dimensional semantic vectors projected to 2D with distinct color groups.
2. `CosineSimilarityLink`: Glowing dashed connector line between 2 nearest neighbor points with similarity badge (`sim: 0.92`).
3. `VectorDimensionBar`: Horizontal bar breakdown of embedding dimension values.
4. `SearchQueryProbe`: Pulsing search query node that ripples into the cluster to highlight closest neighbors.
Write isolated unit tests in `tests/components/test_ui_embeddings_space_suite.py` validating point coordinates, distance math, and cairo drawing. Do not modify any other existing files.
```

### Task 51: Side-by-Side Prompt Diff & Token Cost Suite
- **Implementation File**: `vibmo/product/ai/ui_prompt_diff_suite.py`
- **Test File**: `tests/components/test_ui_prompt_diff_suite.py`
- **Prompt**:
```text
Implement a Side-by-Side Prompt Version Diff UI suite in `vibmo/product/ai/ui_prompt_diff_suite.py` subclassing `Node`.
Implement 4 components:
1. `PromptDiffCard`: Split card showing `Version A (Original)` vs `Version B (Optimized)`.
2. `InlineDiffHighlighter`: Text block with highlighted green additions (`+`) and strike-through red deletions (`-`).
3. `PromptTokenCostBadge`: Comparative badge showing token count reduction and cost savings (`-38% tokens`).
4. `MergePromptButton`: High-converting gradient action button to accept changes.
Write isolated unit tests in `tests/components/test_ui_prompt_diff_suite.py` testing diff parsing logic, layout stacking, and cairo drawing. Do not modify any other existing files.
```

### Task 52: Secure API Key Vault & Secret Reveal Suite
- **Implementation File**: `vibmo/product/ai/ui_api_key_vault_suite.py`
- **Test File**: `tests/components/test_ui_api_key_vault_suite.py`
- **Prompt**:
```text
Implement an API Key Vault & Security UI suite in `vibmo/product/ai/ui_api_key_vault_suite.py` subclassing `Node`.
Implement 4 components:
1. `ApiKeyVaultCard`: Glass container displaying secret API key name, created date, and last used status.
2. `MaskedTokenRevealField`: Password field with `sk-live-••••••••••••••••` that unmasks to clear text on demand with smooth transition.
3. `CopyClipboardPill`: Interactive button that flips from "Copy Key" to "Copied! ✓" with emerald green flash.
4. `RevokeConfirmModal`: Security modal warning badge for key revocation.
Write isolated unit tests in `tests/components/test_ui_api_key_vault_suite.py` testing unmasking state, copy triggers, and cairo drawing. Do not modify any other existing files.
```

### Task 53: SaaS 3-Column Pricing Tier Matrix Suite
- **Implementation File**: `vibmo/product/ai/ui_pricing_matrix_suite.py`
- **Test File**: `tests/components/test_ui_pricing_matrix_suite.py`
- **Prompt**:
```text
Implement a SaaS 3-Column Pricing Tier Matrix in `vibmo/product/ai/ui_pricing_matrix_suite.py` subclassing `Node`.
Implement 4 components:
1. `PricingTierGrid`: 3-card layout (Starter, Pro, Enterprise) with price headers, feature lists, and CTA buttons.
2. `PopularGlowBadge`: "MOST POPULAR" glowing badge atop the center Pro tier card with specular rim.
3. `AnnualBillingToggle`: Toggle switch for Monthly vs Annual pricing with "-20% DISCOUNT" badge.
4. `FeatureChecklistRow`: Feature items with green checkmarks and tooltip indicator dots.
Write isolated unit tests in `tests/components/test_ui_pricing_matrix_suite.py` validating 3-column flex sizing, toggle state price calculation, and drawing. Do not modify any other existing files.
```

### Task 54: GitHub PR Review Timeline & Merge Suite
- **Implementation File**: `vibmo/product/ai/ui_git_pr_timeline_suite.py`
- **Test File**: `tests/components/test_ui_git_pr_timeline_suite.py`
- **Prompt**:
```text
Implement a GitHub Pull Request Timeline & Merge UI suite in `vibmo/product/ai/ui_git_pr_timeline_suite.py` subclassing `Node`.
Implement 4 components:
1. `GitPullRequestCard`: Header with PR title (`#104: Add 100 motion assets`), status pill (`Open` / `Merged`), and author avatar.
2. `CommitShaBadge`: Monospace commit SHA pill with commit message and branch arrow.
3. `CiCdCheckStatusPill`: Green checkmark / spinning amber check indicator ("All checks passed").
4. `MergeSquashButton`: Vibrant green "Squash and Merge" button with dropdown arrow and confetti trigger.
Write isolated unit tests in `tests/components/test_ui_git_pr_timeline_suite.py` testing PR card layout, badge colors, and cairo rendering. Do not modify any other existing files.
```

### Task 55: Visual SQL Query Block & Schema Join Suite
- **Implementation File**: `vibmo/product/ai/ui_sql_query_builder_suite.py`
- **Test File**: `tests/components/test_ui_sql_query_builder_suite.py`
- **Prompt**:
```text
Implement a Visual SQL Query Builder & Schema Join suite in `vibmo/product/ai/ui_sql_query_builder_suite.py` subclassing `Node`.
Implement 4 components:
1. `VisualSqlQueryBlock`: Visual block with SELECT columns, FROM table, and WHERE conditions.
2. `TableJoinConnectorCurve`: Smooth Bézier curved link connecting foreign key column to primary key table.
3. `SqlSyntaxHighlightView`: Syntax-highlighted SQL preview code window below builder.
4. `ExecutionTimePill`: Badge showing query latency (`⚡ 14.2ms (Index Scan)`).
Write isolated unit tests in `tests/components/test_ui_sql_query_builder_suite.py` verifying block layout stacking, connector endpoints, and cairo drawing. Do not modify any other existing files.
```

### Task 56: Cloud Infrastructure Telemetry & Latency HUD Suite
- **Implementation File**: `vibmo/product/ai/ui_telemetry_dial_suite.py`
- **Test File**: `tests/components/test_ui_telemetry_dial_suite.py`
- **Prompt**:
```text
Implement a Cloud Infrastructure Telemetry HUD suite in `vibmo/product/ai/ui_telemetry_dial_suite.py` subclassing `Node`.
Implement 4 components:
1. `CircularCpuGaugeDial`: Radial gauge dial displaying live CPU load percentage with color transition (Green -> Amber -> Red).
2. `RamMemoryMeterBar`: Segmented horizontal RAM memory usage bar.
3. `NetworkPingLatencyLine`: Animated real-time latency line chart with ping spikes and 99th percentile marker.
4. `UptimePercentageBadge`: Emerald pill displaying `99.999% SLA Uptime`.
Write isolated unit tests in `tests/components/test_ui_telemetry_dial_suite.py` testing gauge angle math, memory bar fill calculations, and drawing. Do not modify any other existing files.
```

### Task 57: Webhooks Stream & HTTP Status Badge Suite
- **Implementation File**: `vibmo/product/ai/ui_webhook_feed_suite.py`
- **Test File**: `tests/components/test_ui_webhook_feed_suite.py`
- **Prompt**:
```text
Implement a Live Webhook Activity Feed & HTTP Inspector suite in `vibmo/product/ai/ui_webhook_feed_suite.py` subclassing `Node`.
Implement 4 components:
1. `WebhookEventStreamCard`: Streaming log list of HTTP webhook deliveries with timestamp and event name (`payment.succeeded`).
2. `HttpStatusBadge`: Pill with status codes (`200 OK` in green, `404 Not Found` in amber, `500 Server Error` in red).
3. `PayloadJsonInspector`: Collapsible JSON payload viewer with syntax coloring.
4. `RetryEventButton`: Compact retry button that triggers animated circular reload icon.
Write isolated unit tests in `tests/components/test_ui_webhook_feed_suite.py` validating log entry layout, color badge codes, and cairo drawing. Do not modify any other existing files.
```

### Task 58: AI Token Quota Ring & Usage Threshold Suite
- **Implementation File**: `vibmo/product/ai/ui_quota_meter_suite.py`
- **Test File**: `tests/components/test_ui_quota_meter_suite.py`
- **Prompt**:
```text
Implement an AI Token Quota Ring & Usage Threshold suite in `vibmo/product/ai/ui_quota_meter_suite.py` subclassing `Node`.
Implement 4 components:
1. `CircularTokenQuotaRing`: Thick circular progress ring showing tokens used vs total quota (`842k / 1.0M`).
2. `OverLimitWarningBanner`: Animated warning notification bar when quota exceeds 90%.
3. `UsageThresholdPill`: Small badge indicating remaining days in billing cycle.
4. `UpgradeCtaButton`: Gradient "Upgrade to Unlimited" button with spring hover bounce.
Write isolated unit tests in `tests/components/test_ui_quota_meter_suite.py` verifying progress ring arc math, threshold logic, and cairo drawing. Do not modify any other existing files.
```

### Task 59: Split Code Playground & Sandbox Suite
- **Implementation File**: `vibmo/product/ai/ui_code_sandbox_suite.py`
- **Test File**: `tests/components/test_ui_code_sandbox_suite.py`
- **Prompt**:
```text
Implement a Split Code Playground & Sandbox UI suite in `vibmo/product/ai/ui_code_sandbox_suite.py` subclassing `Node`.
Implement 4 components:
1. `SplitCodePlayground`: Split-pane container with Code Editor on left and Interactive Preview / Output on right.
2. `InteractiveTerminalLogs`: Bottom console output drawer with stdout logs and execution timer.
3. `RunCodeSuccessIndicator`: Pulsing green run button that transforms to checkmark upon completion.
4. `DependencyInstallPill`: Small pill badge displaying `npm packages installed in 1.2s`.
Write isolated unit tests in `tests/components/test_ui_code_sandbox_suite.py` testing split container proportions, editor layout, and cairo drawing. Do not modify any other existing files.
```

### Task 60: Interactive Feature Comparison Matrix Suite
- **Implementation File**: `vibmo/product/ai/ui_matrix_comparison_suite.py`
- **Test File**: `tests/components/test_ui_matrix_comparison_suite.py`
- **Prompt**:
```text
Implement an Interactive Feature Comparison Matrix suite in `vibmo/product/ai/ui_matrix_comparison_suite.py` subclassing `Node`.
Implement 4 components:
1. `InteractiveFeatureMatrix`: Table comparing "Our Product" vs 3 competitors across 10 feature categories.
2. `CompetitorComparisonRow`: Alternating striped table row with green checkmarks, red crosses, and partial score badges.
3. `TooltipFeatureExplanation`: Popover card detailing feature specifications.
4. `StickyHeaderColumn`: Highlighted column for "Our Product" with cyan glowing border.
Write isolated unit tests in `tests/components/test_ui_matrix_comparison_suite.py` verifying table cell grid calculations and cairo drawing. Do not modify any other existing files.
```

---

## Section 5: Financial, 3D Spatial & Motion Chart Suites (Tasks 61–75)
*Target: 50–60 animated data visualization and chart components*

### Task 61: OrderBook Market Depth & Price Spread Suite
- **Implementation File**: `vibmo/charts/chart_orderbook_depth_suite.py`
- **Test File**: `tests/charts/test_chart_orderbook_depth_suite.py`
- **Prompt**:
```text
Implement a Crypto/Stock Market Depth & OrderBook Chart suite in `vibmo/charts/chart_orderbook_depth_suite.py` subclassing `Node`.
Implement 4 components:
1. `OrderbookDepthChart`: Dual green (Bids) and red (Asks) cumulative step-area curves meeting at center market price.
2. `BidAskSpreadLine`: Center vertical spread line displaying live spread percentage (`Spread: 0.01%`).
3. `WallSizeCallout`: Interactive callout badge on large buy/sell resistance walls.
4. `CryptoMarketPriceTicker`: Animated large header price ticker with rapid green/red flashing on price ticks.
Include `.animate_depth_shift(duration)` generator.
Write isolated unit tests in `tests/charts/test_chart_orderbook_depth_suite.py` testing orderbook sorting, cumulative sums, and cairo drawing. Do not modify any other existing files.
```

### Task 62: Sankey Flow Ribbon & Revenue Stream Suite
- **Implementation File**: `vibmo/charts/chart_sankey_flow_suite.py`
- **Test File**: `tests/charts/test_chart_sankey_flow_suite.py`
- **Prompt**:
```text
Implement a Sankey Flow Diagram & Revenue Stream suite in `vibmo/charts/chart_sankey_flow_suite.py` subclassing `Node`.
Implement 4 components:
1. `SankeyFlowDiagram`: Multi-stage branching flow diagram with smooth Bézier ribbon paths connecting categorical nodes.
2. `FlowRibbonNode`: Vertical node pillar with label and total monetary value.
3. `ConversionDropoffIndicator`: Red branch highlighting customer/traffic drop-off.
4. `RevenuePathHighlighter`: Glow effect tracing flow from Income -> Gross Profit -> Net Margin.
Include `.trace_flow(duration)` animation.
Write isolated unit tests in `tests/charts/test_chart_sankey_flow_suite.py` validating flow conservation math, ribbon width calculations, and cairo drawing. Do not modify any other existing files.
```

### Task 63: Market Cap Treemap & Hierarchical Tiles Suite
- **Implementation File**: `vibmo/charts/chart_treemap_market_suite.py`
- **Test File**: `tests/charts/test_chart_treemap_market_suite.py`
- **Prompt**:
```text
Implement a Market Cap Treemap Chart suite in `vibmo/charts/chart_treemap_market_suite.py` subclassing `Node`.
Implement 4 components:
1. `TreemapMarketCapGrid`: Squarified treemap layout partitioning canvas by asset valuation (e.g. S&P 500 / Crypto sectors).
2. `ZoomableTreemapTile`: Individual company tile with ticker, market cap, and performance percentage.
3. `PercentageDeltaColor`: Tile background color scale (+5% bright emerald green to -5% bright crimson red).
4. `MarketSectorLegend`: Header bar breaking down Tech, Healthcare, Finance, and Energy.
Write isolated unit tests in `tests/charts/test_chart_treemap_market_suite.py` testing squarify algorithm partitioning, aspect ratio optimization, and cairo drawing. Do not modify any other existing files.
```

### Task 64: Violin Density & Statistical Distribution Suite
- **Implementation File**: `vibmo/charts/chart_violin_density_suite.py`
- **Test File**: `tests/charts/test_chart_violin_density_suite.py`
- **Prompt**:
```text
Implement a Violin Probability Density Plot suite in `vibmo/charts/chart_violin_density_suite.py` subclassing `Node`.
Implement 4 components:
1. `ViolinDistributionPlot`: Symmetrical vertical kernel density estimation (KDE) curve visualizer across multiple categories.
2. `ProbabilityDensityKernel`: Smooth outline curve representing continuous probability distribution.
3. `MedianQuartileMarker`: Inner box plot core showing median white dot, interquartile thick bar, and min/max whiskers.
4. `OutlierJitterDots`: Individual jittered data points plotted alongside the density curve.
Write isolated unit tests in `tests/charts/test_chart_violin_density_suite.py` testing Gaussian KDE calculation, symmetry math, and cairo drawing. Do not modify any other existing files.
```

### Task 65: Choropleth Mini Map & Regional Heatmap Suite
- **Implementation File**: `vibmo/charts/chart_choropleth_map_suite.py`
- **Test File**: `tests/charts/test_chart_choropleth_map_suite.py`
- **Prompt**:
```text
Implement a Choropleth Geographic Mini Map suite in `vibmo/charts/chart_choropleth_map_suite.py` subclassing `Node`.
Implement 4 components:
1. `ChoroplethWorldMiniMap`: Stylized world vector polygon map where countries/regions are colored based on metric values.
2. `RegionalHeatPolygon`: Smooth polygon boundary with animatable color heat fill.
3. `GeoDataTooltip`: Floating pointer tooltip displaying country name, user count, and revenue.
4. `CountryRankLeaderboard`: Mini ranking leaderboard table alongside the map.
Write isolated unit tests in `tests/charts/test_chart_choropleth_map_suite.py` validating polygon coordinates, color scale interpolation, and drawing. Do not modify any other existing files.
```

### Task 66: Waterfall Financial Cost Breakdown Suite
- **Implementation File**: `vibmo/charts/chart_waterfall_flow_suite.py`
- **Test File**: `tests/charts/test_chart_waterfall_flow_suite.py`
- **Prompt**:
```text
Implement a Waterfall Financial Breakdown Chart suite in `vibmo/charts/chart_waterfall_flow_suite.py` subclassing `Node`.
Implement 4 components:
1. `WaterfallCostChart`: Step-by-step financial bridge chart showing starting revenue, incremental additions, cost deductions, and net total.
2. `NetGainColumn`: Green floating pillar for positive revenue contributions.
3. `DeductionColumn`: Red floating pillar for operating expenses and taxes.
4. `CumulativeBridgeConnector`: Dashed horizontal connector lines linking top/bottom of consecutive pillars.
Write isolated unit tests in `tests/charts/test_chart_waterfall_flow_suite.py` verifying cumulative sum offsets, pillar heights, and cairo drawing. Do not modify any other existing files.
```

### Task 67: Multi-Variable Bubble Scatter & Trail Suite
- **Implementation File**: `vibmo/charts/chart_bubble_scatter_suite.py`
- **Test File**: `tests/charts/test_chart_bubble_scatter_suite.py`
- **Prompt**:
```text
Implement a Multi-Variable 4D Bubble Scatter Plot in `vibmo/charts/chart_bubble_scatter_suite.py` subclassing `Node`.
Implement 4 components:
1. `MultiVariableBubbleScatter`: 2D Cartesian scatter chart where bubbles represent X, Y, Size (Z), and Color (Category).
2. `MotionTrailBubble`: Animated bubbles with trailing history curves showing path evolution over time.
3. `QuadrantPartitionLines`: Crosshair lines dividing chart into 4 analytical quadrants (e.g. High Growth / High Margin).
4. `BubbleScaleLegend`: Visual size reference circles for data magnitude.
Write isolated unit tests in `tests/charts/test_chart_bubble_scatter_suite.py` testing coordinate normalization, radius scaling, and cairo drawing. Do not modify any other existing files.
```

### Task 68: 3D Surface Mesh & Elevation Contour Suite
- **Implementation File**: `vibmo/charts/chart_surface_mesh_3d_suite.py`
- **Test File**: `tests/charts/test_chart_surface_mesh_3d_suite.py`
- **Prompt**:
```text
Implement a 3D Animated Surface Mesh Plot in `vibmo/charts/chart_surface_mesh_3d_suite.py` subclassing `Node`.
Implement 4 components:
1. `Animated3DSurfaceMesh`: 3D isometric wireframe terrain surface mesh representing $Z = f(X, Y, t)$ with rotating elevation peaks.
2. `ElevationColorGradient`: Continuous color gradient mapping height to color (Blue valley -> Green plains -> White mountain peaks).
3. `WireframeContourGrid`: Top and bottom projection grid lines showing coordinate reference planes.
4. `CameraRotationRig`: Smooth interactive azimuth and elevation angle control for 3D rotation.
Write isolated unit tests in `tests/charts/test_chart_surface_mesh_3d_suite.py` testing 3D-to-2D projection matrix math, depth sorting, and drawing. Do not modify any other existing files.
```

### Task 69: High-Performance Speedometer & HUD Ticker Suite
- **Implementation File**: `vibmo/charts/chart_speedometer_hud_suite.py`
- **Test File**: `tests/charts/test_chart_speedometer_hud_suite.py`
- **Prompt**:
```text
Implement a High-Performance Speedometer & HUD Dial suite in `vibmo/charts/chart_speedometer_hud_suite.py` subclassing `Node`.
Implement 4 components:
1. `SpeedometerNeedleGauge`: 270-degree radial speedometer gauge with animated needle spring sweep and numeric tick marks.
2. `RedlineRpmArc`: Glowing redline zone with warning pulse.
3. `DigitalSpeedNumberTicker`: Large central digital speed counter with 3-digit rolling wheel.
4. `TurboBoostBar`: Curved auxiliary boost pressure meter bar with needle.
Write isolated unit tests in `tests/charts/test_chart_speedometer_hud_suite.py` testing angle trigonometric mappings, value damping, and cairo drawing. Do not modify any other existing files.
```

### Task 70: Pro Candlestick, Moving Averages & Volume Suite
- **Implementation File**: `vibmo/charts/chart_candlestick_pro_suite.py`
- **Test File**: `tests/charts/test_chart_candlestick_pro_suite.py`
- **Prompt**:
```text
Implement a Professional Financial Candlestick & Volume Chart in `vibmo/charts/chart_candlestick_pro_suite.py` subclassing `Node`.
Implement 4 components:
1. `ProCandlestickChart`: OHLC (Open, High, Low, Close) candlestick chart with crisp vertical wicks and color-filled bodies.
2. `MovingAverageCurves`: EMA 20 (Cyan) and EMA 50 (Amber) exponential moving average trend lines overlaying the candles.
3. `VolumeProfileOverlay`: Bottom bar chart showing trading volume with corresponding green/red color coding.
4. `CrosshairPriceTracker`: Interactive vertical/horizontal dashed crosshairs with price and date badges.
Write isolated unit tests in `tests/charts/test_chart_candlestick_pro_suite.py` validating OHLC coordinate calculations, EMA formulas, and drawing. Do not modify any other existing files.
```

### Task 71: Radial Sunburst Hierarchy & Expanding Rings Suite
- **Implementation File**: `vibmo/charts/chart_sunburst_radial_suite.py`
- **Test File**: `tests/charts/test_chart_sunburst_radial_suite.py`
- **Prompt**:
```text
Implement a Radial Sunburst Hierarchy Chart suite in `vibmo/charts/chart_sunburst_radial_suite.py` subclassing `Node`.
Implement 4 components:
1. `SunburstRadialHierarchy`: Multi-tiered concentric ring chart showing nested parent-child hierarchical proportions.
2. `ExpandingRingArc`: Smooth expanding arc segments animated from center outward on scene entrance.
3. `BreadcrumbPathTrail`: Breadcrumb text trail displaying current drill-down path (`Company > Engineering > Frontend`).
4. `RadialSliceHighlight`: Glowing hover highlight outline around focused wedge.
Write isolated unit tests in `tests/charts/test_chart_sunburst_radial_suite.py` testing annular sector arc geometry, angle splits, and cairo drawing. Do not modify any other existing files.
```

### Task 72: Pareto 80/20 Analysis & Cumulative Line Suite
- **Implementation File**: `vibmo/charts/chart_pareto_curve_suite.py`
- **Test File**: `tests/charts/test_chart_pareto_curve_suite.py`
- **Prompt**:
```text
Implement a Pareto Analysis & 80/20 Principle Chart in `vibmo/charts/chart_pareto_curve_suite.py` subclassing `Node`.
Implement 4 components:
1. `ParetoAnalysisChart`: Dual-axis chart combining sorted descending frequency bars with an ascending cumulative percentage line.
2. `FrequencyBarChart`: Descending categorical bar columns.
3. `Cumulative8020Curve`: Smooth cubic Bézier line showing cumulative contribution percentage (0% to 100%).
4. `CriticalThresholdLine`: Glowing horizontal marker at 80% line highlighting the vital few contributors.
Write isolated unit tests in `tests/charts/test_chart_pareto_curve_suite.py` verifying Pareto sort ordering, cumulative percentage math, and drawing. Do not modify any other existing files.
```

### Task 73: Flowing Streamgraph & Organic Wave Area Suite
- **Implementation File**: `vibmo/charts/chart_streamgraph_wave_suite.py`
- **Test File**: `tests/charts/test_chart_streamgraph_wave_suite.py`
- **Prompt**:
```text
Implement an Organic Streamgraph & Wave Area Chart in `vibmo/charts/chart_streamgraph_wave_suite.py` subclassing `Node`.
Implement 4 components:
1. `FlowingStreamgraphArea`: Stacked area graph with silhouette centered around a flowing organic baseline.
2. `OrganicWaveBand`: Individual smooth categorical color stream ribbon with cubic spline interpolation.
3. `TimeAxisScrubber`: Vertical vertical cursor line scrubbing across timestamps with data breakdown card.
4. `StreamgraphLegend`: Floating pills showing category names and total volumes.
Write isolated unit tests in `tests/charts/test_chart_streamgraph_wave_suite.py` validating Lee-Byron streamgraph baseline algorithm, stack math, and drawing. Do not modify any other existing files.
```

### Task 74: Statistical Box-and-Whisker Plot Suite
- **Implementation File**: `vibmo/charts/chart_box_whisker_suite.py`
- **Test File**: `tests/charts/test_chart_box_whisker_suite.py`
- **Prompt**:
```text
Implement a Statistical Box-and-Whisker Plot suite in `vibmo/charts/chart_box_whisker_suite.py` subclassing `Node`.
Implement 4 components:
1. `StatisticalBoxPlot`: Multi-category box plot comparing medians, interquartile ranges (IQR), and extremes.
2. `InterquartileBox`: Filled central rectangular box spanning 25th (Q1) to 75th (Q3) percentiles with prominent median line.
3. `WhiskersErrorBars`: T-bar whiskers extending to 1.5 * IQR minimum and maximum values.
4. `AnimatedOutlierPings`: Glowing circular dots marking data outliers beyond whiskers.
Write isolated unit tests in `tests/charts/test_chart_box_whisker_suite.py` verifying quantile calculations, whisker bounds, and cairo drawing. Do not modify any other existing files.
```

### Task 75: Polar Rose & Coxcomb Area Chart Suite
- **Implementation File**: `vibmo/charts/chart_polar_rose_suite.py`
- **Test File**: `tests/charts/test_chart_polar_rose_suite.py`
- **Prompt**:
```text
Implement a Polar Rose / Florence Nightingale Coxcomb Area Chart in `vibmo/charts/chart_polar_rose_suite.py` subclassing `Node`.
Implement 4 components:
1. `PolarRoseAreaChart`: Cyclic radial chart where sectors have equal angles and radius proportional to square root of metric area.
2. `ProportionalRadiusWedge`: Translucent colored wedge sectors layered by time/season.
3. `AngularCategoryAxis`: 360-degree radial spoke grid labeled by months or categories.
4. `ConcentricRadiusRings`: Background guide rings indicating scale thresholds.
Write isolated unit tests in `tests/charts/test_chart_polar_rose_suite.py` testing polar coordinate conversions, wedge area math, and cairo drawing. Do not modify any other existing files.
```

---

## Section 6: Kinetic Typography & Title Sequence Suites (Tasks 76–90)
*Target: 50–60 typographic animations, glyph effects, and kinetic title sequences*

### Task 76: Cyberpunk Glitch Decryptor Typography Suite
- **Implementation File**: `vibmo/typography/kinetic/typo_glitch_decryptor_suite.py`
- **Test File**: `tests/typography/test_typo_glitch_decryptor_suite.py`
- **Prompt**:
```text
Implement a Cyberpunk Glitch Decryptor Typography suite in `vibmo/typography/kinetic/typo_glitch_decryptor_suite.py` subclassing `Node`.
Implement 4 components:
1. `GlitchDecryptorText`: Title text that scrambles through random hexadecimal/katakana glyphs before resolving character-by-character from left to right.
2. `HexMatrixCycle`: Fast cycle animation where unsettled characters cycle with high frequency.
3. `LockInGlitchFlash`: Cyan/white chromatic flash upon each character successfully locking into final letter.
4. `PasswordUnmaskEffect`: Password mask unmasking animation with binary digital noise.
Include `.decrypt(duration=2.0)` animation generator.
Write isolated unit tests in `tests/typography/test_typo_glitch_decryptor_suite.py` verifying scramble algorithms, character progression, and cairo drawing. Do not modify any other existing files.
```

### Task 77: Liquid Wave & Submerged Text Refraction Suite
- **Implementation File**: `vibmo/typography/kinetic/typo_liquid_wave_suite.py`
- **Test File**: `tests/typography/test_typo_liquid_wave_suite.py`
- **Prompt**:
```text
Implement a Liquid Wave & Refractive Typography suite in `vibmo/typography/kinetic/typo_liquid_wave_suite.py` subclassing `Node`.
Implement 4 components:
1. `LiquidWaveText`: Kinetic text where glyph baselines undulate smoothly along a sinusoidal wave across time.
2. `ChromaticBaselineDrift`: RGB color splitting on crests and troughs of the text wave.
3. `SubmergedTextRefraction`: Text viewed through simulated water refraction with shimmering caustic reflections.
4. `RippleWordReveal`: Staggered wave splash reveal where words emerge from water surface.
Write isolated unit tests in `tests/typography/test_typo_liquid_wave_suite.py` testing wave sine offsets, per-character transforms, and cairo drawing. Do not modify any other existing files.
```

### Task 78: 3D Isometric Extruded Typography Suite
- **Implementation File**: `vibmo/typography/kinetic/typo_isometric_3d_suite.py`
- **Test File**: `tests/typography/test_typo_isometric_3d_suite.py`
- **Prompt**:
```text
Implement a 3D Isometric Extruded Typography suite in `vibmo/typography/kinetic/typo_isometric_3d_suite.py` subclassing `Node`.
Implement 4 components:
1. `IsometricExtruded3DText`: Bold 3D block lettering extruded along isometric 30-degree angles with shaded side facets.
2. `CastShadowExtrusion`: Deep floor contact cast shadow with soft directional blur.
3. `BevelGleamLight`: Animated light glint sliding across the top extruded bevel edges.
4. `IsometricFloatIdle`: Gentle floating levitation oscillation on the Z-axis.
Write isolated unit tests in `tests/typography/test_typo_isometric_3d_suite.py` testing extrusion depth layers, facet lighting calculations, and drawing. Do not modify any other existing files.
```

### Task 79: Realistic Gas Neon Strobe & Ballast Flicker Suite
- **Implementation File**: `vibmo/typography/kinetic/typo_neon_strobe_suite.py`
- **Test File**: `tests/typography/test_typo_neon_strobe_suite.py`
- **Prompt**:
```text
Implement a Realistic Gas Neon Strobe Sign suite in `vibmo/typography/kinetic/typo_neon_strobe_suite.py` subclassing `Node`.
Implement 4 components:
1. `RealisticNeonStrobeSign`: Glowing glass tube neon signage with multi-layer colored bloom halos.
2. `BallastFlickerFailure`: Intermittent realistic ballast ignition flicker sequence (quick double-blink, pause, buzz on).
3. `GasIgnitionSurge`: High-voltage ignition flash surge on startup.
4. `NeonTubeConnectors`: Black wiring and rubber connector caps between separate letter tubes.
Include `.ignite(delay=0.1)` animation.
Write isolated unit tests in `tests/typography/test_typo_neon_strobe_suite.py` testing flicker timing patterns, bloom radius math, and cairo rendering. Do not modify any other existing files.
```

### Task 80: Particle Flame & Disintegrating Embers Typography Suite
- **Implementation File**: `vibmo/typography/kinetic/typo_particle_flame_suite.py`
- **Test File**: `tests/typography/test_typo_particle_flame_suite.py`
- **Prompt**:
```text
Implement a Particle Flame & Disintegrating Typography suite in `vibmo/typography/kinetic/typo_particle_flame_suite.py` subclassing `Node`.
Implement 4 components:
1. `ParticleFlameText`: Text outlines that emit ascending heat shimmer, fiery orange sparks, and smoke trails.
2. `DisintegratingEmbers`: Letters disintegrating into glowing embers blown away by directional wind.
3. `IgnitionSparkBurst`: Initial explosion of spark particles outlining the typography.
4. `SmokeDissipateHeading`: Soft volumetric smoke plumes dissolving typography into darkness.
Write isolated unit tests in `tests/typography/test_typo_particle_flame_suite.py` testing particle generation from glyph outlines and cairo drawing. Do not modify any other existing files.
```

### Task 81: Airport Split-Flap Mechanical Display Suite
- **Implementation File**: `vibmo/typography/kinetic/typo_split_flap_suite.py`
- **Test File**: `tests/typography/test_typo_split_flap_suite.py`
- **Prompt**:
```text
Implement an authentic Airport/Train Station Split-Flap Display suite in `vibmo/typography/kinetic/typo_split_flap_suite.py` subclassing `Node`.
Implement 4 components:
1. `SplitFlapAirportBoard`: Matrix of mechanical split-flap character modules flipping through letters to form titles.
2. `MechanicalFlapTile`: Split top and bottom half-tiles with 3D folding perspective flap and center split gap.
3. `RapidLetterScramble`: Staggered flipping rhythm where letters flip rapidly before clattering into place.
4. `SplitFlapSoundSync`: Event hooks designed to trigger `sfx_paper_card_suite` click events per flap.
Include `.flip_to(target_text: str, duration=1.5)` animation.
Write isolated unit tests in `tests/typography/test_typo_split_flap_suite.py` validating letter cycle math, flap geometry, and cairo drawing. Do not modify any other existing files.
```

### Task 82: Matrix Code Rain Headline Consolidation Suite
- **Implementation File**: `vibmo/typography/kinetic/typo_matrix_code_rain_suite.py`
- **Test File**: `tests/typography/test_typo_matrix_code_rain_suite.py`
- **Prompt**:
```text
Implement a Matrix Code Rain Typography Consolidation suite in `vibmo/typography/kinetic/typo_matrix_code_rain_suite.py` subclassing `Node`.
Implement 4 components:
1. `MatrixRainTypography`: Cascading green digital code rain drops that freeze and solidify into high-contrast bold title letters.
2. `PhosphorTrailDecay`: Bright glowing leading glyphs with fading phosphor decay tails.
3. `HeadlineConsolidation`: Transition where rain drops snap into final letter shapes with a white flash.
4. `GlyphMatrixSubText`: Accompanying decoding subtitles in digital monospace font.
Write isolated unit tests in `tests/typography/test_typo_matrix_code_rain_suite.py` testing rain position tracking, consolidation triggers, and cairo drawing. Do not modify any other existing files.
```

### Task 83: Slit-Scan Analog Video Synth Typography Suite
- **Implementation File**: `vibmo/typography/kinetic/typo_slit_scan_synth_suite.py`
- **Test File**: `tests/typography/test_typo_slit_scan_synth_suite.py`
- **Prompt**:
```text
Implement a Slit-Scan Analog Video Synth Typography suite in `vibmo/typography/kinetic/typo_slit_scan_synth_suite.py` subclassing `Node`.
Implement 4 components:
1. `SlitScanVideoSynthText`: 1970s analog video synth typography with continuous horizontal and vertical spatial slit-scan stretching.
2. `AnalogFeedbackSmear`: Flowing temporal trails smearing behind moving letters with feedback decay.
3. `ChromaWarpWave`: Rainbow color cycle shifting through the smearing distortion bands.
4. `CRTScanBeamWipe`: High-voltage electron beam sweep drawing out the title text.
Write isolated unit tests in `tests/typography/test_typo_slit_scan_synth_suite.py` testing distortion displacement functions and cairo drawing. Do not modify any other existing files.
```

### Task 84: Mechanical Odometer Tumbler Counter Suite
- **Implementation File**: `vibmo/typography/kinetic/typo_odometer_tumbler_suite.py`
- **Test File**: `tests/typography/test_typo_odometer_tumbler_suite.py`
- **Prompt**:
```text
Implement a Mechanical Odometer Tumbler Typography suite in `vibmo/typography/kinetic/typo_odometer_tumbler_suite.py` subclassing `Node`.
Implement 4 components:
1. `OdometerTumblerCounter`: High-precision rolling numeric odometer where digit wheels roll vertically with realistic cylindrical perspective.
2. `VerticalRollingGlyphs`: Continuous vertical strip of digits (0-9) transitioning with exponential ease-out deceleration.
3. `MechanicalSeparatorCommas`: Fixed punctuation separators ($, commas, decimals, %) aligning with rolling wheels.
4. `TumblerBezelSlot`: Recessed metal dashboard frame with top/bottom shadow gradients masking wheel edges.
Include `.roll_to(target_value: float, duration=2.0)` animation.
Write isolated unit tests in `tests/typography/test_typo_odometer_tumbler_suite.py` testing rolling offset math, cylindrical perspective, and cairo drawing. Do not modify any other existing files.
```

### Task 85: Rubber Stamp Title Slam & Shockwave Suite
- **Implementation File**: `vibmo/typography/kinetic/typo_badge_stamp_slam_suite.py`
- **Test File**: `tests/typography/test_typo_badge_stamp_slam_suite.py`
- **Prompt**:
```text
Implement a Rubber Stamp Slam & Shockwave Typography suite in `vibmo/typography/kinetic/typo_badge_stamp_slam_suite.py` subclassing `Node`.
Implement 4 components:
1. `RubberStampTitleSlam`: Circular/rectangular badge title that drops from huge scale (3.0x) and slams down at 1.0x with camera shake.
2. `DustPuffShockwave`: Radial ring of dust and impact particles bursting outward upon stamp impact.
3. `InkedTextureMask`: Grungy worn rubber stamp ink texture overlay with distressed edges.
4. `SpringReboundSettling`: Bouncy elastic rebound physics settling into resting angle.
Include `.slam(delay=0.1, duration=0.6)` animation.
Write isolated unit tests in `tests/typography/test_typo_badge_stamp_slam_suite.py` testing slam physics scale curve, particle burst, and cairo drawing. Do not modify any other existing files.
```

### Task 86: Magnetic Gravity Drop & Reassembly Suite
- **Implementation File**: `vibmo/typography/kinetic/typo_magnetic_gravity_suite.py`
- **Test File**: `tests/typography/test_typo_magnetic_gravity_suite.py`
- **Prompt**:
```text
Implement a Physics Magnetic Gravity Typography suite in `vibmo/typography/kinetic/typo_magnetic_gravity_suite.py` subclassing `Node`.
Implement 4 components:
1. `MagneticGravityLetters`: Typography letters that drop individually under gravity, bounce elastically off canvas floor, and settle into place.
2. `ExplosiveScatterForce`: Force pulse that blasts letters into chaos before magnetic snapback.
3. `MagnetPullReassembly`: Strong magnetic attraction drawing scattered letters back into perfect headline alignment.
4. `FloorContactShadow`: Dynamic shadow expanding as letters approach ground.
Write isolated unit tests in `tests/typography/test_typo_magnetic_gravity_suite.py` testing gravity velocity, floor restitution bounces, and cairo drawing. Do not modify any other existing files.
```

### Task 87: Prismatic Hologram & Iridescent Chroma Suite
- **Implementation File**: `vibmo/typography/kinetic/typo_hologram_chroma_suite.py`
- **Test File**: `tests/typography/test_typo_hologram_chroma_suite.py`
- **Prompt**:
```text
Implement a Holographic & Prismatic Iridescent Typography suite in `vibmo/typography/kinetic/typo_hologram_chroma_suite.py` subclassing `Node`.
Implement 4 components:
1. `HologramChromaText`: Shimmering semi-transparent holographic typography with moving rainbow specular sheen.
2. `InterferenceFringeLines`: Horizontal optical thin-film interference lines drifting across letter surfaces.
3. `HologramEmitterCone`: Semi-transparent blue projection light beam radiating from floor emitter up to text.
4. `GlitchDeconstruct`: Subtle holographic signal flutter and glitch deconstruction.
Write isolated unit tests in `tests/typography/test_typo_hologram_chroma_suite.py` testing thin-film color shifts, alpha gradients, and cairo rendering. Do not modify any other existing files.
```

### Task 88: Vintage Terminal Typewriter & Caret Suite
- **Implementation File**: `vibmo/typography/kinetic/typo_terminal_typewriter_suite.py`
- **Test File**: `tests/typography/test_typo_terminal_typewriter_suite.py`
- **Prompt**:
```text
Implement a Vintage Phosphor Terminal Typewriter suite in `vibmo/typography/kinetic/typo_terminal_typewriter_suite.py` subclassing `Node`.
Implement 4 components:
1. `PhosphorTerminalTypewriter`: Monospace terminal typography that types sequentially with natural typing cadence variation.
2. `BlinkingBlockCaret`: Solid amber or green phosphor rectangular cursor blinking at 2 Hz.
3. `CommandPromptPrefix`: Monospace user prompt prefix (`user@vibmo:~$ `) in distinct accent color.
4. `TypingAudioSyncHook`: Event hook firing on each keypress character reveal.
Include `.typewriter(text: str, speed=35)` animation.
Write isolated unit tests in `tests/typography/test_typo_terminal_typewriter_suite.py` validating character typing indices, cursor positioning, and drawing. Do not modify any other existing files.
```

### Task 89: Brush Calligraphy & Splatter Path Reveal Suite
- **Implementation File**: `vibmo/typography/kinetic/typo_brush_calligraphy_suite.py`
- **Test File**: `tests/typography/test_typo_brush_calligraphy_suite.py`
- **Prompt**:
```text
Implement a Brush Calligraphy & Textured Ink Reveal suite in `vibmo/typography/kinetic/typo_brush_calligraphy_suite.py` subclassing `Node`.
Implement 4 components:
1. `BrushCalligraphyPathReveal`: Hand-painted fluid calligraphy letters traced out progressively along Bézier stroke paths.
2. `BristleTextureStroke`: Multi-strand bristle texture showing brush pressure width modulation.
3. `InkSplatterBleed`: Dynamic ink bleed splatters and wet paper edge diffusion.
4. `WaterColorWashBackdrop`: Soft colored watercolor wash pooling behind the lettering.
Write isolated unit tests in `tests/typography/test_typo_brush_calligraphy_suite.py` testing path trimming math, stroke width variations, and cairo drawing. Do not modify any other existing files.
```

### Task 90: Elastic Squash & Stretch Comic Bounce Suite
- **Implementation File**: `vibmo/typography/kinetic/typo_elastic_squash_bounce_suite.py`
- **Test File**: `tests/typography/test_typo_elastic_squash_bounce_suite.py`
- **Prompt**:
```text
Implement an Elastic Squash-and-Stretch Typographic suite in `vibmo/typography/kinetic/typo_elastic_squash_bounce_suite.py` subclassing `Node`.
Implement 4 components:
1. `ElasticSquashBounceTitle`: High-energy cartoon title that squashes horizontally and stretches vertically upon landing impacts.
2. `RhythmicImpactPumping`: Periodic scale pulse locked to musical beat tempo.
3. `JellyMorphTypography`: Elastic gelatin wobble oscillation settling into resting proportions.
4. `ComicSpeedLines`: Radial speed accent lines bursting around text upon punch hit.
Include `.bounce_in(duration=0.8)` animation generator.
Write isolated unit tests in `tests/typography/test_typo_elastic_squash_bounce_suite.py` validating squash/stretch volume conservation ($Scale_X \times Scale_Y = 1.0$) and cairo drawing. Do not modify any other existing files.
```

---

## Section 7: Visual Post-FX Shaders & Turnkey Production Suites (Tasks 91–100)
*Target: 35–45 shaders and multi-scene production video templates*

### Task 91: Authentic CRT Aperture Grille & Phosphor Bloom Suite
- **Implementation File**: `vibmo/fx/shaders/fx_crt_phosphor_bloom_suite.py`
- **Test File**: `tests/fx/test_fx_crt_phosphor_bloom_suite.py`
- **Prompt**:
```text
Implement an Authentic CRT Monitor Shader Suite in `vibmo/fx/shaders/fx_crt_phosphor_bloom_suite.py` subclassing `vibmo.fx.filters.Filter`.
Implement 4 shader filters (with CPU NumPy fallback and GPU ModernGL acceleration):
1. `CrtPhosphorBloomShader`: Multi-pass high-intensity phosphor bloom glow with RGB aperture grille shadow mask.
2. `CurvedGlassBarrelDistortion`: 3D spherical lens barrel bulge with darkened glass corners.
3. `PhosphorPersistenceTrail`: Green/amber decay ghosting trail simulating slow phosphor persistence.
4. `HorizontalRGBBeamBleed`: Horizontal color fringing across high-contrast luminance edges.
Write isolated unit tests in `tests/fx/test_fx_crt_phosphor_bloom_suite.py` validating shader compilation, filter apply transforms, and output array shapes. Do not modify any other existing files.
```

### Task 92: VHS Tape Tracking Noise & Head Switch Jitter Suite
- **Implementation File**: `vibmo/fx/shaders/fx_vhs_tape_tracking_suite.py`
- **Test File**: `tests/fx/test_fx_vhs_tape_tracking_suite.py`
- **Prompt**:
```text
Implement a VHS Tape Tracking & Analog Degradation Shader Suite in `vibmo/fx/shaders/fx_vhs_tape_tracking_suite.py` subclassing `Filter`.
Implement 4 shader filters:
1. `VhsTapeTrackingShader`: Realistic horizontal VHS tracking noise band rolling vertically across screen.
2. `HeadSwitchingJitterLine`: Bottom edge video head switching tear line and horizontal scanline shift.
3. `ColorBleedChromaShift`: Chroma subsampling 4:2:0 smear with red/cyan horizontal color phase displacement.
4. `AnalogStaticSnowBurst`: Random magnetic tape dropouts and white noise spark bursts.
Write isolated unit tests in `tests/fx/test_fx_vhs_tape_tracking_suite.py` testing frame processing, distortion offsets, and output validity. Do not modify any other existing files.
```

### Task 93: Anamorphic Blue Streak Lens Flare Suite
- **Implementation File**: `vibmo/fx/shaders/fx_anamorphic_flare_suite.py`
- **Test File**: `tests/fx/test_fx_anamorphic_flare_suite.py`
- **Prompt**:
```text
Implement a Cinematic Anamorphic Streak Lens Flare Suite in `vibmo/fx/shaders/fx_anamorphic_flare_suite.py` subclassing `Filter`.
Implement 4 shader filters:
1. `AnamorphicStreakFlareShader`: Horizontal cinematic cyan/cobalt blue streak flares radiating from bright highlight sources.
2. `ThresholdGlowPass`: High-pass luminance threshold filter isolating intense specular points.
3. `LensGhostArtifacts`: Secondary optical lens reflection rings and polygonal aperture ghosts along optical axis.
4. `StarburstSpikeCross`: 4-point star cross sparkle on direct pinpoint specular highlights.
Write isolated unit tests in `tests/fx/test_fx_anamorphic_flare_suite.py` testing threshold filtering, horizontal Gaussian blur convolution, and array blending. Do not modify any other existing files.
```

### Task 94: Frosted Liquid Glass Refraction & Dispersion Suite
- **Implementation File**: `vibmo/fx/shaders/fx_liquid_glass_refraction_suite.py`
- **Test File**: `tests/fx/test_fx_liquid_glass_refraction_suite.py`
- **Prompt**:
```text
Implement a Frosted Liquid Glass Refraction & Dispersion Suite in `vibmo/fx/shaders/fx_liquid_glass_refraction_suite.py` subclassing `Filter`.
Implement 4 shader filters:
1. `LiquidGlassRefractionShader`: Refractive normal-map distortion simulating thick frosted glass and lens warping.
2. `ChromaticDispersionFilter`: Wavelength-dependent chromatic dispersion splitting red, green, and blue light rays at boundary angles.
3. `SpecularRimSheen`: Dynamic specular edge rim reflection highlighting outer boundary contours.
4. `FrostedBackdropBlur`: Multi-pass dual Kawase blur with frosted surface roughness noise.
Write isolated unit tests in `tests/fx/test_fx_liquid_glass_refraction_suite.py` testing normal map refraction calculations and filter blends. Do not modify any other existing files.
```

### Task 95: ASCII Matrix Art & Character Luminescence Suite
- **Implementation File**: `vibmo/fx/shaders/fx_ascii_matrix_art_suite.py`
- **Test File**: `tests/fx/test_fx_ascii_matrix_art_suite.py`
- **Prompt**:
```text
Implement an ASCII Matrix Art & Character Shader Suite in `vibmo/fx/shaders/fx_ascii_matrix_art_suite.py` subclassing `Filter`.
Implement 4 shader filters:
1. `AsciiMatrixArtShader`: Converts full video frame luminance into real-time dynamic ASCII character grid (`@%#*+=-:. `).
2. `TerminalColorPaletteFilter`: Monochromatic color remapping (Matrix Green, Amber CRT, Cyberpunk Cyan/Magenta).
3. `DynamicCharResolutionGrid`: Adjustable grid cell granularity ($80\times 45$ up to $240\times 135$ terminal cells).
4. `EdgeContourAsciiOverlay`: Blends ASCII edge outlines with underlying video graphics.
Write isolated unit tests in `tests/fx/test_fx_ascii_matrix_art_suite.py` testing luminance quantization, character lookup tables, and cairo/NumPy rendering. Do not modify any other existing files.
```

### Task 96: Turnkey Scene: AI Coding Assistant Demo Suite
- **Implementation File**: `vibmo/templates/turnkey/tmpl_ai_code_assistant_suite.py`
- **Test File**: `tests/templates/test_tmpl_ai_code_assistant_suite.py`
- **Prompt**:
```text
Implement a complete Turnkey SaaS Video Production Scene in `vibmo/templates/turnkey/tmpl_ai_code_assistant_suite.py` using `motio.agent_api`.
Create a class `AiCodeAssistantTemplate` with classmethod:
`create_scene(title: str, code_snippet: str, duration=6.0) -> Scene`
The scene must choreograph:
1. Stage 1: Entrance of `BrowserWindow` IDE containing `CodeWindow` and `GlassCard`.
2. Stage 2: Realtime code autocompletion and token typing with `TokenStreamerBox`.
3. Stage 3: Instant execution with green checkmark test pass pill.
4. Stage 4: Celebration milestone with `MetricCounter` and subtle ambient dust particles.
Write isolated unit tests in `tests/templates/test_tmpl_ai_code_assistant_suite.py` verifying scene duration, node hierarchy, storyboard generation, and animation actions. Do not modify any other existing files.
```

### Task 97: Turnkey Scene: Titanium Crypto Debit Card Suite
- **Implementation File**: `vibmo/templates/turnkey/tmpl_fintech_crypto_card_suite.py`
- **Test File**: `tests/templates/test_tmpl_fintech_crypto_card_suite.py`
- **Prompt**:
```text
Implement a Turnkey Fintech Crypto Card Product Reveal in `vibmo/templates/turnkey/tmpl_fintech_crypto_card_suite.py` using `motio.agent_api`.
Create a class `FintechCryptoCardTemplate` with classmethod:
`create_scene(cardholder: str, balance: float, duration=5.0) -> Scene`
The scene must choreograph:
1. Stage 1: 3D floating titanium credit card reveal with laser-engraved chip and specular reflection sheen.
2. Stage 2: Contactless NFC wave animation and haptic payment sound event.
3. Stage 3: `NotificationToast` push alert sliding in with payment confirmation.
4. Stage 4: `MetricCounter` incrementing account balance.
Write isolated unit tests in `tests/templates/test_tmpl_fintech_crypto_card_suite.py` verifying complete scene validation, timing constraints, and rendering. Do not modify any other existing files.
```

### Task 98: Turnkey Scene: Open Source CLI Release Suite
- **Implementation File**: `vibmo/templates/turnkey/tmpl_developer_cli_launch_suite.py`
- **Test File**: `tests/templates/test_tmpl_developer_cli_launch_suite.py`
- **Prompt**:
```text
Implement a Turnkey Open Source CLI Launch Video Scene in `vibmo/templates/turnkey/tmpl_developer_cli_launch_suite.py` using `motio.agent_api`.
Create a class `DeveloperCliLaunchTemplate` with classmethod:
`create_scene(pkg_name: str, install_cmd: str, stars: int, duration=5.0) -> Scene`
The scene must choreograph:
1. Stage 1: `CodeWindow` terminal entrance with glowing ASCII art banner.
2. Stage 2: High-speed installation command typing with progress bar animation.
3. Stage 3: Benchmark comparison bar chart showing 10x performance boost.
4. Stage 4: GitHub Star milestone counter ticking up with sparkle particle explosion.
Write isolated unit tests in `tests/templates/test_tmpl_developer_cli_launch_suite.py` verifying scene structure and storyboard export. Do not modify any other existing files.
```

### Task 99: Turnkey Scene: YCombinator SaaS Pitch Deck Suite
- **Implementation File**: `vibmo/templates/turnkey/tmpl_saas_yc_pitch_suite.py`
- **Test File**: `tests/templates/test_tmpl_saas_yc_pitch_suite.py`
- **Prompt**:
```text
Implement a Turnkey YC Investor Pitch Deck Video Scene in `vibmo/templates/turnkey/tmpl_saas_yc_pitch_suite.py` using `motio.agent_api`.
Create a class `SaasYcPitchTemplate` with classmethod:
`create_scene(company_name: str, mrr_target: int, duration=6.0) -> Scene`
The scene must choreograph:
1. Stage 1: Problem statement glass card with red indicator badge.
2. Stage 2: `BrowserWindow` product dashboard popping in with smooth spring deceleration.
3. Stage 3: Exponential `LineChart` MRR growth curve tracing upwards alongside `MetricCounter`.
4. Stage 4: Call-to-action button and contact avatar group.
Write isolated unit tests in `tests/templates/test_tmpl_saas_yc_pitch_suite.py` testing complete scene validation and animation execution. Do not modify any other existing files.
```

### Task 100: Turnkey Scene: 9:16 Vertical Podcast Audiogram Suite
- **Implementation File**: `vibmo/templates/turnkey/tmpl_social_audiogram_suite.py`
- **Test File**: `tests/templates/test_tmpl_social_audiogram_suite.py`
- **Prompt**:
```text
Implement a Turnkey 9:16 Vertical Social Podcast Audiogram Scene in `vibmo/templates/turnkey/tmpl_social_audiogram_suite.py` using `motio.agent_api`.
Create a class `SocialAudiogramTemplate` with classmethod:
`create_scene(podcast_title: str, episode_name: str, duration=6.0) -> Scene`
Configured at $1080\times 1920$ vertical reel aspect ratio:
1. Stage 1: Floating circular guest `Avatar` with audio-reactive pulsating glow ring.
2. Stage 2: Animated `CircularSpectrum` / `WaveformRibbon` reacting to narration.
3. Stage 3: TikTok-style `KineticCaptions` displaying dynamic bouncing karaoke subtitles.
4. Stage 4: Subtle ambient floating dust particles and vignette lighting.
Write isolated unit tests in `tests/templates/test_tmpl_social_audiogram_suite.py` verifying $1080\times 1920$ vertical canvas, timeline choreography, and node hierarchy. Do not modify any other existing files.
```
