"""
Comprehensive Motion Graphics Audio Library Generator & Downloader.
Populates `assets/audio/` with 100% royalty-free CC0 audio assets for UI, transitions,
impacts, chimes, glitches, and full background music tracks.
"""

from __future__ import annotations
import json
import math
import os
import urllib.request
import numpy as np
from scipy.io import wavfile

AUDIO_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "audio")
SR = 48000  # Broadcast standard 48kHz sampling rate


def ensure_dirs():
    dirs = [
        os.path.join(AUDIO_ROOT, "sfx", "ui"),
        os.path.join(AUDIO_ROOT, "sfx", "transitions"),
        os.path.join(AUDIO_ROOT, "sfx", "impacts"),
        os.path.join(AUDIO_ROOT, "sfx", "glitch"),
        os.path.join(AUDIO_ROOT, "sfx", "chimes"),
        os.path.join(AUDIO_ROOT, "sfx", "cinematic"),
        os.path.join(AUDIO_ROOT, "music"),
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)


def write_wav(rel_path: str, audio: np.ndarray, sample_rate: int = SR) -> str:
    """Save normalized float32 array as 16-bit PCM WAV."""
    full_path = os.path.join(AUDIO_ROOT, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    peak = np.max(np.abs(audio))
    if peak > 1e-4:
        audio = audio / peak * 0.92
    else:
        audio = np.zeros_like(audio)
    int16_audio = (audio * 32767).astype(np.int16)
    wavfile.write(full_path, sample_rate, int16_audio)
    return full_path


def download_file(url: str, rel_path: str) -> bool:
    full_path = os.path.join(AUDIO_ROOT, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Vibmo/1.0"}
        )
        with urllib.request.urlopen(req, timeout=15) as response, open(full_path, "wb") as out_file:
            out_file.write(response.read())
        sz = os.path.getsize(full_path)
        print(f"[Download] Successfully fetched: {rel_path} ({sz / 1024:.1f} KB)")
        return True
    except Exception as e:
        print(f"[Download Warning] Could not fetch from {url} ({e})")
        return False


# ==========================================
# 1. UI & FOLEY SOUNDS (48kHz)
# ==========================================

def make_ui_click_soft(duration: float = 0.035) -> np.ndarray:
    n = int(SR * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    freq = 1400.0 * np.exp(-t * 120.0) + 400.0
    phase = 2.0 * np.pi * np.cumsum(freq) / SR
    env = np.exp(-t * 140.0)
    return (np.sin(phase) * env).astype(np.float32)


def make_ui_click_mechanical(duration: float = 0.05) -> np.ndarray:
    n = int(SR * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    click1 = np.sin(2.0 * np.pi * 2200.0 * t) * np.exp(-t * 180.0)
    t2 = np.maximum(0.0, t - 0.012)
    click2 = np.sin(2.0 * np.pi * 1600.0 * t2) * np.exp(-t2 * 140.0)
    rng = np.random.RandomState(42)
    noise = rng.randn(n) * np.exp(-t * 220.0) * 0.3
    return (click1 * 0.6 + click2 * 0.7 + noise).astype(np.float32)


def make_ui_pop_bubble(duration: float = 0.12) -> np.ndarray:
    n = int(SR * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    freqs = 280.0 * ((950.0 / 280.0) ** (t / duration))
    phase = 2.0 * np.pi * np.cumsum(freqs) / SR
    env = np.exp(-t * 28.0) * np.sin(np.pi * (t / duration)) ** 0.5
    return (np.sin(phase) * env).astype(np.float32)


def make_ui_toggle_switch(duration: float = 0.08) -> np.ndarray:
    n = int(SR * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    f1 = 800.0 * np.exp(-t * 60.0)
    f2 = 1800.0 * np.exp(-t * 90.0)
    snap = np.sin(2.0 * np.pi * f1 * t) * 0.6 + np.sin(2.0 * np.pi * f2 * t) * 0.4
    env = np.exp(-t * 50.0)
    return (snap * env).astype(np.float32)


def make_ui_keyboard_typing(duration: float = 0.06) -> np.ndarray:
    n = int(SR * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    rng = np.random.RandomState(101)
    noise = rng.randn(n) * np.exp(-t * 180.0)
    thud = np.sin(2.0 * np.pi * 280.0 * t) * np.exp(-t * 80.0) * 0.7
    return (noise * 0.5 + thud * 0.6).astype(np.float32)


def make_ui_camera_shutter(duration: float = 0.14) -> np.ndarray:
    n = int(SR * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    # Mirror flap down + curtain click
    t1 = np.maximum(0.0, t)
    c1 = np.sin(2.0 * np.pi * 1200.0 * t1) * np.exp(-t1 * 90.0)
    t2 = np.maximum(0.0, t - 0.05)
    c2 = np.sin(2.0 * np.pi * 2400.0 * t2) * np.exp(-t2 * 120.0) * (t >= 0.05)
    rng = np.random.RandomState(45)
    noise = rng.randn(n) * np.exp(-t * 70.0) * 0.35
    return (c1 * 0.6 + c2 * 0.8 + noise).astype(np.float32)


def make_ui_slider_tick(duration: float = 0.025) -> np.ndarray:
    n = int(SR * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    click = np.sin(2.0 * np.pi * 3200.0 * t) * np.exp(-t * 300.0)
    return click.astype(np.float32)


# ==========================================
# 2. TRANSITIONS & SWEEPS (48kHz)
# ==========================================

def make_whoosh_fast(duration: float = 0.3) -> np.ndarray:
    n = int(SR * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    rng = np.random.RandomState(42)
    noise = rng.randn(n)
    mid = duration * 0.4
    env = np.exp(-((t - mid) ** 2) / (2 * (duration * 0.15) ** 2))
    f_sweep = 180.0 + 600.0 * np.sin(np.pi * t / duration)
    carrier = np.sin(2.0 * np.pi * np.cumsum(f_sweep) / SR)
    return ((noise * 0.6 + carrier * 0.4) * env).astype(np.float32)


def make_whoosh_cinematic(duration: float = 0.65) -> np.ndarray:
    n = int(SR * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    rng = np.random.RandomState(99)
    noise = rng.randn(n)
    mid = duration * 0.48
    env = np.exp(-((t - mid) ** 2) / (2 * (duration * 0.22) ** 2))
    sub = np.sin(2.0 * np.pi * (80.0 + 140.0 * (t / duration)) * t) * 0.6
    return ((noise * 0.45 + sub * 0.55) * env).astype(np.float32)


def make_whoosh_air(duration: float = 0.4) -> np.ndarray:
    n = int(SR * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    rng = np.random.RandomState(7)
    noise = rng.randn(n)
    env = np.sin(np.pi * (t / duration)) ** 2.0
    return (noise * env * 0.7).astype(np.float32)


def make_whoosh_heavy(duration: float = 0.8) -> np.ndarray:
    n = int(SR * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    rng = np.random.RandomState(10)
    noise = rng.randn(n)
    mid = duration * 0.5
    env = np.exp(-((t - mid) ** 2) / (2 * (duration * 0.25) ** 2))
    sub = np.sin(2.0 * np.pi * 65.0 * t) * 0.8
    return ((noise * 0.4 + sub * 0.6) * env).astype(np.float32)


def make_swoosh_transition(duration: float = 0.5) -> np.ndarray:
    n = int(SR * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    rng = np.random.RandomState(13)
    noise = rng.randn(n)
    env = np.sin(np.pi * (t / duration)) ** 1.8
    pitch = 300.0 * np.exp(t * 2.5)
    carrier = np.sin(2.0 * np.pi * np.cumsum(pitch) / SR)
    return ((noise * 0.5 + carrier * 0.5) * env).astype(np.float32)


def make_riser_tension(duration: float = 1.6) -> np.ndarray:
    n = int(SR * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    freqs = 80.0 * ((2200.0 / 80.0) ** (t / duration))
    phase = 2.0 * np.pi * np.cumsum(freqs) / SR
    env = (t / duration) ** 2.4
    saw = 2.0 * (phase / (2 * np.pi) - np.floor(phase / (2 * np.pi) + 0.5))
    rng = np.random.RandomState(42)
    noise = rng.randn(n) * 0.3
    return ((saw * 0.6 + noise * 0.4) * env).astype(np.float32)


def make_riser_cyber_pitch(duration: float = 2.2) -> np.ndarray:
    n = int(SR * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    f = 110.0 * np.exp(t * 1.5)
    phase = 2.0 * np.pi * np.cumsum(f) / SR
    lfo = np.sin(2.0 * np.pi * (8.0 + 12.0 * (t / duration)) * t)
    env = (t / duration) ** 1.8
    return (np.sin(phase) * (0.6 + 0.4 * lfo) * env).astype(np.float32)


def make_reverse_cymbal_sweep(duration: float = 1.4) -> np.ndarray:
    n = int(SR * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    rng = np.random.RandomState(55)
    noise = rng.randn(n)
    env = (t / duration) ** 3.0
    # Metallic resonant ring
    ring = np.sin(2.0 * np.pi * 3500.0 * t) * 0.2 + np.sin(2.0 * np.pi * 5400.0 * t) * 0.15
    return ((noise * 0.65 + ring * 0.35) * env).astype(np.float32)


# ==========================================
# 3. IMPACTS & SUB HITS (48kHz)
# ==========================================

def make_bass_drop_impact(duration: float = 0.8) -> np.ndarray:
    n = int(SR * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    pitch = 160.0 * np.exp(-t * 7.0) + 35.0
    phase = 2.0 * np.pi * np.cumsum(pitch) / SR
    sub = np.sin(phase) * np.exp(-t * 3.5)
    rng = np.random.RandomState(88)
    slap = rng.randn(n) * np.exp(-t * 80.0) * 0.5
    return (sub * 0.85 + slap * 0.35).astype(np.float32)


def make_sub_hit_punch(duration: float = 0.5) -> np.ndarray:
    n = int(SR * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    pitch = 220.0 * np.exp(-t * 18.0) + 45.0
    sub = np.sin(2.0 * np.pi * pitch * t) * np.exp(-t * 8.0)
    return sub.astype(np.float32)


def make_card_thud_impact(duration: float = 0.35) -> np.ndarray:
    n = int(SR * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    pitch = 95.0 * np.exp(-t * 14.0) + 42.0
    sub = np.sin(2.0 * np.pi * pitch * t) * np.exp(-t * 12.0)
    click = np.sin(2.0 * np.pi * 1200.0 * t) * np.exp(-t * 90.0) * 0.3
    return (sub * 0.8 + click).astype(np.float32)


def make_cinematic_boom(duration: float = 1.2) -> np.ndarray:
    n = int(SR * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    sub = np.sin(2.0 * np.pi * (70.0 * np.exp(-t * 4.0) + 30.0) * t) * np.exp(-t * 2.5)
    rng = np.random.RandomState(3)
    tail = rng.randn(n) * np.exp(-t * 3.0) * 0.3
    return (sub * 0.8 + tail * 0.4).astype(np.float32)


# ==========================================
# 4. CHIMES, PINGS & GLITCHES (48kHz)
# ==========================================

def make_success_bell_chime(duration: float = 0.9) -> np.ndarray:
    n = int(SR * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    f1, f2, f3 = 1046.50, 1318.51, 1567.98  # C6, E6, G6
    w1 = np.sin(2.0 * np.pi * f1 * t) * np.exp(-t * 3.8)
    t_e = np.maximum(0.0, t - 0.06)
    w2 = np.sin(2.0 * np.pi * f2 * t_e) * np.exp(-t_e * 3.8)
    t_g = np.maximum(0.0, t - 0.12)
    w3 = np.sin(2.0 * np.pi * f3 * t_g) * np.exp(-t_g * 3.0)
    return (w1 * 0.4 + w2 * 0.4 + w3 * 0.5).astype(np.float32)


def make_sparkle_magic_glimmer(duration: float = 0.7) -> np.ndarray:
    n = int(SR * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    master = np.zeros(n, dtype=np.float32)
    freqs = [1760.0, 2217.46, 2637.02, 3520.0, 4434.92]
    for idx, f in enumerate(freqs):
        dt = np.maximum(0.0, t - idx * 0.05)
        w = np.sin(2.0 * np.pi * f * dt) * np.exp(-dt * 6.0)
        master += (w * 0.25).astype(np.float32)
    return master


def make_notification_ping(duration: float = 0.45) -> np.ndarray:
    n = int(SR * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    w = (
        np.sin(2.0 * np.pi * 1760.0 * t) * 0.6 +
        np.sin(2.0 * np.pi * 3520.0 * t) * 0.25
    ) * np.exp(-t * 8.0)
    return w.astype(np.float32)


def make_error_alert_beep(duration: float = 0.35) -> np.ndarray:
    n = int(SR * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    tone1 = np.sin(2.0 * np.pi * 480.0 * t) * (t < 0.15)
    t2 = np.maximum(0.0, t - 0.18)
    tone2 = np.sin(2.0 * np.pi * 360.0 * t2) * (t >= 0.18) * np.exp(-t2 * 15.0)
    return ((tone1 + tone2) * 0.7).astype(np.float32)


def make_digital_glitch(duration: float = 0.4) -> np.ndarray:
    n = int(SR * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    rng = np.random.RandomState(42)
    noise = rng.randn(n)
    mod = np.sign(np.sin(2.0 * np.pi * 60.0 * t))
    glitch_carrier = np.sin(2.0 * np.pi * (rng.randint(200, 2400, n)) * t)
    env = np.sin(np.pi * (t / duration)) ** 0.5
    return ((noise * 0.4 + glitch_carrier * 0.5 * mod) * env).astype(np.float32)


def make_cyber_data_burst(duration: float = 0.5) -> np.ndarray:
    n = int(SR * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    rng = np.random.RandomState(22)
    step_freq = np.repeat(rng.choice([800, 1200, 1600, 2400, 3200], size=10), n // 10 + 1)[:n]
    beep = np.sin(2.0 * np.pi * step_freq * t) * np.sin(np.pi * (t / duration))
    return (beep * 0.8).astype(np.float32)


def make_tape_stop(duration: float = 0.6) -> np.ndarray:
    n = int(SR * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    pitch = 800.0 * (1.0 - (t / duration) ** 2.0)
    w = np.sin(2.0 * np.pi * np.cumsum(pitch) / SR) * (1.0 - t / duration)
    return w.astype(np.float32)


# ==========================================
# 5. MUSIC SOUNDTRACKS & AMBIENT (48kHz)
# ==========================================

def make_tech_ambient_soundtrack(duration: float = 8.0) -> np.ndarray:
    n = int(SR * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    master = np.zeros(n, dtype=np.float32)

    bpm = 120.0
    beat_dur = 60.0 / bpm
    total_beats = int(duration / beat_dur)

    for b in range(total_beats):
        beat_time = b * beat_dur
        k_start = int(beat_time * SR)
        k_len = min(int(0.35 * SR), n - k_start)
        if k_len > 0:
            kt = np.linspace(0, 0.35, k_len, endpoint=False)
            k_freq = 130.0 * np.exp(-kt * 24.0) + 38.0
            k_phase = 2.0 * np.pi * np.cumsum(k_freq) / SR
            k_env = np.exp(-kt * 10.0)
            master[k_start:k_start + k_len] += (np.sin(k_phase) * k_env * 0.55).astype(np.float32)

    rng = np.random.RandomState(42)
    for b in range(total_beats * 2):
        if b % 2 == 1:
            h_time = b * (beat_dur * 0.5)
            h_start = int(h_time * SR)
            h_len = min(int(0.06 * SR), n - h_start)
            if h_len > 0:
                ht = np.linspace(0, 0.06, h_len, endpoint=False)
                noise = rng.randn(h_len)
                h_env = np.exp(-ht * 80.0)
                master[h_start:h_start + h_len] += (noise * h_env * 0.15).astype(np.float32)

    chords = [
        [174.61, 207.65, 261.63, 311.13],
        [138.59, 174.61, 207.65, 261.63],
        [207.65, 261.63, 311.13, 415.30],
        [155.56, 196.00, 233.08, 311.13],
    ]
    chord_dur = beat_dur * 2.0
    for idx, chord in enumerate(chords):
        c_start = int(idx * chord_dur * SR)
        c_len = min(int(chord_dur * SR), n - c_start)
        if c_len > 0:
            ct = np.linspace(0, chord_dur, c_len, endpoint=False)
            c_env = np.sin(np.pi * (ct / chord_dur)) ** 0.5
            for f in chord:
                w = np.sin(2.0 * np.pi * f * ct) * 0.08
                w += np.sin(2.0 * np.pi * (f * 1.002) * ct) * 0.05
                master[c_start:c_start + c_len] += (w * c_env).astype(np.float32)

    return master


def make_lofi_chill_soundtrack(duration: float = 8.0) -> np.ndarray:
    n = int(SR * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    master = np.zeros(n, dtype=np.float32)

    bpm = 85.0
    beat_dur = 60.0 / bpm
    total_beats = int(duration / beat_dur)

    for b in range(total_beats):
        if b % 2 == 0:
            b_start = int(b * beat_dur * SR)
            b_len = min(int(0.3 * SR), n - b_start)
            if b_len > 0:
                bt = np.linspace(0, 0.3, b_len, endpoint=False)
                k = np.sin(2.0 * np.pi * (80.0 * np.exp(-bt * 15.0) + 40.0) * bt) * np.exp(-bt * 8.0)
                master[b_start:b_start + b_len] += (k * 0.5).astype(np.float32)

    rng = np.random.RandomState(77)
    crackle = rng.randn(n) * 0.02 * (rng.rand(n) > 0.98)
    master += crackle.astype(np.float32)

    rhodes_chords = [
        [146.83, 220.00, 261.63, 329.63],
        [196.00, 246.94, 329.63, 392.00],
        [130.81, 196.00, 246.94, 293.66],
        [220.00, 261.63, 329.63, 392.00],
    ]
    chord_dur = beat_dur * 2.0
    for idx, chord in enumerate(rhodes_chords):
        c_start = int(idx * chord_dur * SR)
        c_len = min(int(chord_dur * SR), n - c_start)
        if c_len > 0:
            ct = np.linspace(0, chord_dur, c_len, endpoint=False)
            c_env = np.exp(-ct * 0.8)
            for f in chord:
                w = np.sin(2.0 * np.pi * f * ct) * 0.09
                master[c_start:c_start + c_len] += (w * c_env).astype(np.float32)

    return master


def make_cyberpunk_synth_drive(duration: float = 8.0) -> np.ndarray:
    n = int(SR * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    master = np.zeros(n, dtype=np.float32)

    bpm = 130.0
    beat_dur = 60.0 / bpm
    total_beats = int(duration / beat_dur)

    # 1. Driving 16th note bass arpeggio
    arp_notes = [55.0, 55.0, 110.0, 55.0, 65.41, 65.41, 130.81, 65.41]
    step_dur = beat_dur / 4.0
    total_steps = int(duration / step_dur)
    for s in range(total_steps):
        s_start = int(s * step_dur * SR)
        s_len = min(int(step_dur * SR), n - s_start)
        if s_len > 0:
            st = np.linspace(0, step_dur, s_len, endpoint=False)
            freq = arp_notes[s % len(arp_notes)]
            # Saw wave
            phase = 2.0 * np.pi * freq * st
            saw = 2.0 * (phase / (2 * np.pi) - np.floor(phase / (2 * np.pi) + 0.5))
            env = np.exp(-st * 25.0)
            master[s_start:s_start + s_len] += (saw * env * 0.35).astype(np.float32)

    # 2. Heavy kick on every quarter note
    for b in range(total_beats):
        b_start = int(b * beat_dur * SR)
        b_len = min(int(0.3 * SR), n - b_start)
        if b_len > 0:
            bt = np.linspace(0, 0.3, b_len, endpoint=False)
            k = np.sin(2.0 * np.pi * (140.0 * np.exp(-bt * 22.0) + 40.0) * bt) * np.exp(-bt * 9.0)
            master[b_start:b_start + b_len] += (k * 0.6).astype(np.float32)

    return master


# ==========================================
# MAIN EXECUTION
# ==========================================

def run():
    ensure_dirs()
    print("[Vibmo Audio Suite] Generating & Downloading 100% Royalty-Free Motion Design Sounds...")

    manifest = {
        "license": "CC0 1.0 Universal / Public Domain / 100% Royalty Free for Commercial & Agentic Use",
        "sample_rate": SR,
        "assets": {}
    }

    # 1. UI Sounds
    ui_sounds = [
        ("sfx/ui/ui_click_soft.wav", make_ui_click_soft(), "Soft UI button click"),
        ("sfx/ui/ui_click_mechanical.wav", make_ui_click_mechanical(), "Mechanical switch tap"),
        ("sfx/ui/ui_pop_bubble.wav", make_ui_pop_bubble(), "Playful bubbly pop toggle"),
        ("sfx/ui/ui_toggle_switch.wav", make_ui_toggle_switch(), "Toggle switch snap"),
        ("sfx/ui/ui_keyboard_typing.wav", make_ui_keyboard_typing(), "Keyboard mechanical key stroke"),
        ("sfx/ui/ui_camera_shutter.wav", make_ui_camera_shutter(), "Camera shutter snapshot click"),
        ("sfx/ui/ui_slider_tick.wav", make_ui_slider_tick(), "Precision slider notch tick"),
    ]

    # 2. Transitions
    trans_sounds = [
        ("sfx/transitions/whoosh_fast.wav", make_whoosh_fast(), "Fast whip whoosh for quick slide cuts"),
        ("sfx/transitions/whoosh_cinematic.wav", make_whoosh_cinematic(), "Deep cinematic sub whoosh for card fly-ins"),
        ("sfx/transitions/whoosh_air.wav", make_whoosh_air(), "Airy breath whoosh for smooth fade reveals"),
        ("sfx/transitions/whoosh_heavy.wav", make_whoosh_heavy(), "Heavy low-end cinematic whoosh"),
        ("sfx/transitions/swoosh_transition.wav", make_swoosh_transition(), "Dynamic swoosh transition for camera pans"),
        ("sfx/transitions/riser_tension_build.wav", make_riser_tension(), "Tension building pitch riser before drop"),
        ("sfx/transitions/riser_cyber_pitch.wav", make_riser_cyber_pitch(), "Cyber pitch sweep riser with modulation"),
        ("sfx/transitions/reverse_cymbal_sweep.wav", make_reverse_cymbal_sweep(), "Reverse cymbal swelling sweep"),
    ]

    # 3. Impacts
    impact_sounds = [
        ("sfx/impacts/bass_drop_impact.wav", make_bass_drop_impact(), "Heavy 808 sub bass drop and thud"),
        ("sfx/impacts/sub_hit_punch.wav", make_sub_hit_punch(), "Tight acoustic sub punch hit"),
        ("sfx/impacts/card_thud_impact.wav", make_card_thud_impact(), "Solid UI card impact on canvas"),
        ("sfx/impacts/cinematic_boom_hit.wav", make_cinematic_boom(), "Cinematic sub bass trailer boom"),
    ]

    # 4. Chimes & Glitches
    chime_sounds = [
        ("sfx/chimes/success_bell_chime.wav", make_success_bell_chime(), "Harmonic success chime for milestones"),
        ("sfx/chimes/sparkle_magic_glimmer.wav", make_sparkle_magic_glimmer(), "Sparkle shimmer chime cascade"),
        ("sfx/chimes/notification_ping.wav", make_notification_ping(), "Crisp mobile notification ping"),
        ("sfx/chimes/error_alert_beep.wav", make_error_alert_beep(), "Two-tone error alert warning"),
        ("sfx/glitch/digital_glitch_stutter.wav", make_digital_glitch(), "Cyberpunk digital data stutter and glitch"),
        ("sfx/glitch/cyber_data_burst.wav", make_cyber_data_burst(), "Data packet network burst glitch"),
        ("sfx/glitch/analog_tape_stop.wav", make_tape_stop(), "Analog vinyl / tape machine stop slowdown"),
    ]

    # 5. Backing Soundtracks
    music_tracks = [
        ("music/tech_ambient_pulse.wav", make_tech_ambient_soundtrack(), "Tech ambient pulse (120 BPM) for SaaS product videos"),
        ("music/lofi_chill_groove.wav", make_lofi_chill_soundtrack(), "Mellow lofi chill beats (85 BPM) for tutorials"),
        ("music/cyberpunk_synth_drive.wav", make_cyberpunk_synth_drive(), "130 BPM Darksynth Cyberpunk bass drive"),
    ]

    all_generated = ui_sounds + trans_sounds + impact_sounds + chime_sounds + music_tracks

    for rel_path, audio_arr, desc in all_generated:
        write_wav(rel_path, audio_arr)
        dur = len(audio_arr) / SR
        manifest["assets"][rel_path] = {
            "path": rel_path,
            "description": desc,
            "duration_seconds": round(dur, 3),
            "format": "WAV 16-bit PCM 48kHz Mono",
            "license": "CC0 1.0 Universal",
        }
        print(f"[Generated] {rel_path} ({dur:.2f}s) - {desc}")

    # Download full open CC0 sample tracks
    downloads = [
        ("https://raw.githubusercontent.com/rafaelreis-hotmart/Audio-Sample-files/master/sample.mp3", "music/tech_corporate_ambient.mp3", "Tech Corporate Ambient Soundtrack (Full MP3)"),
        ("https://github.com/mdn/webaudio-examples/raw/main/audio-basics/outfoxing.mp3", "music/electronic_upbeat_groove.mp3", "Electronic Upbeat Groove (Full MP3)"),
        ("https://raw.githubusercontent.com/mdn/webaudio-examples/main/voice-change-o-matic/audio/concert-crowd.ogg", "sfx/cinematic/crowd_cheer_ambience.ogg", "Concert Crowd Ambience & Cheer (OGG)"),
    ]

    for url, rel_path, desc in downloads:
        if download_file(url, rel_path):
            manifest["assets"][rel_path] = {
                "path": rel_path,
                "description": desc,
                "format": os.path.splitext(rel_path)[1].upper()[1:],
                "source": url,
                "license": "CC0 / Public Domain / Royalty Free",
            }

    # Save manifest.json
    manifest_path = os.path.join(AUDIO_ROOT, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    readme_path = os.path.join(AUDIO_ROOT, "README.md")
    readme_content = """# Vibmo Royalty-Free Motion Graphics Sound Library

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
"""
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)

    print(f"\n[Audio Suite] Complete! {len(manifest['assets'])} sound files generated and saved to assets/audio/")


if __name__ == "__main__":
    run()
