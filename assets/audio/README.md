# Vibmo Royalty-Free Motion Graphics Sound Library

All audio files in this directory are **100% royalty-free, public domain, and CC0 1.0 Universal licensed**.
They are engineered specifically for motion design, UI product demos, video editing, and AI agent video generation at broadcast standard **48,000 Hz (48kHz)**.

---

## Sound Library Index

### 1. UI & Foley Sounds (`assets/audio/sfx/ui/`)
- `ui_click_soft.wav` - Soft mouse click for subtle button interactions.
- `ui_click_mechanical.wav` - Tactile switch mechanical click.
- `ui_pop_bubble.wav` - Bouncy pitch-rising pop for notification tags & badges.
- `ui_toggle_switch.wav` - Dual-state toggle switch snap.
- `ui_keyboard_typing.wav` - Mechanical keystroke sound for code windows & typing effects.
- `ui_camera_shutter.wav` - Clean camera shutter snap.
- `ui_slider_tick.wav` - Precision slider notch click.

### 2. Motion Transitions (`assets/audio/sfx/transitions/`)
- `whoosh_fast.wav` - Crisp whip whoosh for swift sliding cuts.
- `whoosh_cinematic.wav` - Deep cinematic sub-whoosh for card fly-ins.
- `whoosh_air.wav` - Airy breath whoosh for smooth fade reveals.
- `whoosh_heavy.wav` - Heavy sub-bass whoosh for dramatic transitions.
- `swoosh_transition.wav` - Dynamic camera swipe transition.
- `riser_tension_build.wav` - 1.6s tension-building pitch riser sweep.
- `riser_cyber_pitch.wav` - Cyber modulated pitch sweep riser.
- `reverse_cymbal_sweep.wav` - Swelling reverse cymbal rush.

### 3. Impacts & Drops (`assets/audio/sfx/impacts/`)
- `bass_drop_impact.wav` - Heavy 808 cinematic sub bass drop.
- `sub_hit_punch.wav` - Tight acoustic sub punch hit.
- `card_thud_impact.wav` - Solid physical impact for landing cards.
- `cinematic_boom_hit.wav` - Epic cinematic trailer boom.

### 4. Chimes & Glitches (`assets/audio/sfx/chimes/`, `assets/audio/sfx/glitch/`)
- `success_bell_chime.wav` - Harmonic 3-note major chime for milestone celebrations.
- `sparkle_magic_glimmer.wav` - Shimmering magic sparkle cascade.
- `notification_ping.wav` - Crisp mobile notification ping.
- `error_alert_beep.wav` - Descending two-tone error notification alert.
- `digital_glitch_stutter.wav` - Cyberpunk digital data stutter and glitch burst.
- `cyber_data_burst.wav` - Fast network data packet glitch burst.
- `analog_tape_stop.wav` - Analog tape motor slowdown effect.

### 5. Background Soundtracks (`assets/audio/music/`)
- `tech_ambient_pulse.wav` - 120 BPM electronic tech ambient track with 808s and lush pads.
- `lofi_chill_groove.wav` - 85 BPM warm Rhodes lofi groove with vinyl crackle.
- `cyberpunk_synth_drive.wav` - 130 BPM driving synthwave bassline for futuristic intros.
- `tech_corporate_ambient.mp3` - Full-length modern corporate electronic track (7.3 MB).
- `electronic_upbeat_groove.mp3` - Full-length upbeat energetic groove (1.8 MB).

---

## Agent Usage Example

```python
from motio.agent_api import *

scene = Scene(duration=5.0)

# Add background music
scene.add_audio("assets/audio/music/tech_ambient_pulse.wav", volume=0.6)

# Add synchronized SFX cues
scene.add_sfx("assets/audio/sfx/transitions/whoosh_cinematic.wav", time=0.1)
scene.add_sfx("assets/audio/sfx/ui/ui_click_mechanical.wav", time=1.2)
scene.add_sfx("assets/audio/sfx/chimes/success_bell_chime.wav", time=2.0)
```
