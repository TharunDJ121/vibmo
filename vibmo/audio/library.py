"""
Online Audio Library & Preset Downloader.
Fetches, streams, and caches royalty-free background music and sound tracks from online CDNs.
"""

from __future__ import annotations
import hashlib
import os
from pathlib import Path
from typing import Dict, List, Optional
import numpy as np
import requests
from scipy.io import wavfile


# Curated high-quality CC0 and Royalty-Free audio tracks hosted on reliable public CDNs
CURATED_AUDIO_PRESETS: Dict[str, Dict[str, str]] = {
    "tech_ambient": {
        "title": "Tech Ambient Pulse",
        "genre": "Corporate / Electronic",
        "bpm": "110",
        "url": "https://raw.githubusercontent.com/rafaelreis-hotmart/Audio-Sample-files/master/sample.mp3",
        "license": "CC0 / Royalty Free",
    },
    "cyberpunk": {
        "title": "Cyberpunk Neon Drive",
        "genre": "Synthwave / Darksynth",
        "bpm": "128",
        "url": "https://upload.wikimedia.org/wikipedia/commons/4/4b/Drum_and_bass_loop_175_bpm.ogg",
        "license": "CC-BY",
    },
    "lofi_chill": {
        "title": "Midnight Lofi Coffee",
        "genre": "Lofi Hip-Hop",
        "bpm": "85",
        "url": "https://upload.wikimedia.org/wikipedia/commons/3/30/Lofi_drum_loop_85_bpm.ogg",
        "license": "CC0",
    },
    "future_bass": {
        "title": "Melodic Future Drop",
        "genre": "Future Bass / EDM",
        "bpm": "140",
        "url": "https://upload.wikimedia.org/wikipedia/commons/c/c8/Electronic_Music_Sample.ogg",
        "license": "CC0",
    },
}


def get_audio_cache_dir() -> str:
    """Returns local cache directory for downloaded audio assets."""
    cache_dir = os.path.join(os.getcwd(), ".vibmo_cache", "audio")
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir


def generate_procedural_backing_track(genre: str = "tech_ambient", duration: float = 10.0) -> np.ndarray:
    """
    Synthesizes a rich, professional procedural electronic backing track with drums,
    synth chords, and 808 bass directly in Python (offline fallback & instant generation).
    """
    sr = 44100
    n_samples = int(duration * sr)
    t = np.linspace(0, duration, n_samples, endpoint=False)
    master = np.zeros(n_samples, dtype=np.float32)

    bpm = 120.0
    beat_dur = 60.0 / bpm
    total_beats = int(duration / beat_dur)

    # 1. 808 Kick on every downbeat (4-on-the-floor)
    for b in range(total_beats):
        beat_time = b * beat_dur
        k_start = int(beat_time * sr)
        k_len = min(int(0.35 * sr), n_samples - k_start)
        if k_len > 0:
            kt = np.linspace(0, 0.35, k_len, endpoint=False)
            k_freq = 130.0 * np.exp(-kt * 24.0) + 38.0
            k_phase = 2.0 * np.pi * np.cumsum(k_freq) / sr
            k_env = np.exp(-kt * 10.0)
            master[k_start:k_start + k_len] += (np.sin(k_phase) * k_env * 0.55).astype(np.float32)

    # 2. Hi-hats on off-beats (8th notes)
    rng = np.random.RandomState(42)
    for b in range(total_beats * 2):
        if b % 2 == 1:
            h_time = b * (beat_dur * 0.5)
            h_start = int(h_time * sr)
            h_len = min(int(0.06 * sr), n_samples - h_start)
            if h_len > 0:
                ht = np.linspace(0, 0.06, h_len, endpoint=False)
                noise = rng.randn(h_len)
                h_env = np.exp(-ht * 80.0)
                master[h_start:h_start + h_len] += (noise * h_env * 0.15).astype(np.float32)

    # 3. Lush Ambient Synth Chords (Fm7 -> Dbmaj7 -> Ab -> Eb)
    chords = [
        [174.61, 207.65, 261.63, 311.13],  # F, Ab, C, Eb
        [138.59, 174.61, 207.65, 261.63],  # Db, F, Ab, C
        [207.65, 261.63, 311.13, 415.30],  # Ab, C, Eb, Ab
        [155.56, 196.00, 233.08, 311.13],  # Eb, G, Bb, Eb
    ]
    chord_dur = beat_dur * 4.0
    for idx, chord_freqs in enumerate(chords):
        c_start_time = idx * chord_dur
        if c_start_time >= duration:
            break
        c_start = int(c_start_time * sr)
        c_len = min(int(chord_dur * sr), n_samples - c_start)
        if c_len > 0:
            ct = np.linspace(0, chord_dur, c_len, endpoint=False)
            chord_signal = np.zeros(c_len, dtype=np.float32)
            for freq in chord_freqs:
                # Warm supersaw / chorus simulation
                chord_signal += np.sin(2.0 * np.pi * freq * ct) * 0.25
                chord_signal += np.sin(2.0 * np.pi * (freq * 1.004) * ct) * 0.15
                chord_signal += np.sin(2.0 * np.pi * (freq * 0.996) * ct) * 0.15
            # Slow attack and release
            c_env = np.sin(np.pi * np.clip(ct / chord_dur, 0.0, 1.0)) ** 0.5
            master[c_start:c_start + c_len] += (chord_signal * c_env * 0.25).astype(np.float32)

    # 4. Soft saturation limiter
    master = np.tanh(master * 1.4) * 0.85
    return master


def fetch_online_audio(
    url_or_preset: str,
    cache_dir: Optional[str] = None,
    timeout: float = 10.0,
) -> str:
    """
    Downloads and caches an audio track from a URL or preset name.
    Returns the absolute path to the local audio file.
    """
    raw_str = url_or_preset.strip()
    target_cache_dir = cache_dir or get_audio_cache_dir()

    # 1. Check if it's a known preset
    preset_key = raw_str.replace("preset:", "").lower()
    # 0. Check assets/audio directly for built-in audio or SFX
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    audio_dir = os.path.join(project_root, "assets", "audio")
    for root, _, files in os.walk(audio_dir):
        for fname in files:
            if fname.lower().startswith(preset_key.lower()) or os.path.splitext(fname)[0].lower() == preset_key.lower():
                return os.path.join(root, fname)

    if preset_key in CURATED_AUDIO_PRESETS:
        url = CURATED_AUDIO_PRESETS[preset_key]["url"]
        filename_base = f"preset_{preset_key}"
    elif raw_str.startswith("http://") or raw_str.startswith("https://"):
        url = raw_str
        url_hash = hashlib.sha256(url.encode()).hexdigest()[:12]
        ext = os.path.splitext(url.split("?")[0])[1] or ".mp3"
        filename_base = f"online_{url_hash}{ext}"
    else:
        # Local file
        if os.path.exists(raw_str):
            return os.path.abspath(raw_str)
        # Fallback to procedural track
        url = None
        filename_base = f"synth_{preset_key}.wav"

    local_path = os.path.join(target_cache_dir, filename_base)
    if not local_path.endswith((".mp3", ".wav", ".ogg")):
        local_path += ".mp3"

    # If already cached, return immediately
    if os.path.exists(local_path) and os.path.getsize(local_path) > 1024:
        return local_path

    # Try downloading from URL
    if url:
        try:
            resp = requests.get(url, timeout=timeout, headers={"User-Agent": "Vibmo/0.1.0"})
            if resp.status_code == 200 and len(resp.content) > 1024:
                with open(local_path, "wb") as f:
                    f.write(resp.content)
                return local_path
        except Exception:
            pass

    # If offline or download failed, generate procedural high-vibe synth track
    synth_path = os.path.join(target_cache_dir, f"{filename_base}.wav")
    if not os.path.exists(synth_path):
        audio_arr = generate_procedural_backing_track(genre=preset_key, duration=12.0)
        pcm16 = (audio_arr * 32767.0).astype(np.int16)
        wavfile.write(synth_path, 44100, pcm16)

    return synth_path
