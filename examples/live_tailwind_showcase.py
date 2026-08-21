"""
✦ Live Tailwind & Web Ingestion Showcase
Demonstrates:
- Ingesting a real, pixel-perfect Tailwind CSS dashboard at 4K retina resolution via Asset.html()
- Embedding it inside a 3D BrowserWindow mockup
- 3D Perspective Tilt, Specular Rim Gleam, and Magnetic Cursor Click
- Audio Foley SFX synchronization
"""

from vibmo.agent_api import *

# 1. Initialize Scene
scene = Scene(
    width=1920,
    height=1080,
    fps=60,
    duration=5.0,
    background=Color.hex("#030712"),
)

# 2. Cinematic Shaders
scene.add_post_fx(
    Bloom(threshold=0.65, intensity=0.35, radius=24.0),
    Vignette(intensity=0.25),
    FilmGrain(amount=0.005),
    Dither(amount=0.8),
)

# 3. Kinetic Headline
title = KineticText(
    "<bold>Native Web & Tailwind</bold> <gradient:#6366f1:#06b6d4>In Python Motion Graphics</gradient>",
    font_size=38,
    color=colors.WHITE,
).align("top_center", (1920, 1080)).at(360, 50)
scene.add(title)

# 4. 3D Browser Window
browser = BrowserWindow(
    url="https://cloud.vibmo.design/analytics",
    title="Vibmo Cloud — Live Tailwind UI",
    width=1380,
    height=800,
).align("center", (1920, 1080)).at(270, 150)

# 5. Ingest Real Live Tailwind CSS Component
live_ui = Asset.html("""
<div class="p-8 bg-slate-900/90 text-white min-h-screen flex flex-col justify-between font-sans">
  <div class="flex items-center justify-between pb-6 border-b border-slate-800">
    <div class="flex items-center gap-3">
      <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-cyan-500 flex items-center justify-center font-bold text-base shadow-lg shadow-indigo-500/30">✦</div>
      <div>
        <h2 class="text-base font-bold text-white tracking-tight">Vibmo Autonomous Cluster</h2>
        <p class="text-xs text-slate-400">Production • us-east-1</p>
      </div>
    </div>
    <div class="flex items-center gap-2">
      <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
        <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 mr-2 animate-pulse"></span>
        99.99% Uptime
      </span>
      <button class="px-4 py-1.5 text-xs font-bold bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg shadow-md shadow-indigo-600/30">Upgrade Plan</button>
    </div>
  </div>

  <div class="grid grid-cols-3 gap-6 my-6">
    <div class="p-5 rounded-2xl bg-slate-800/50 border border-slate-700/60 shadow-xl">
      <p class="text-xs font-medium text-slate-400 uppercase tracking-wider">Active Instances</p>
      <p class="text-3xl font-extrabold text-white mt-2">1,420 <span class="text-xs font-semibold text-emerald-400">+18%</span></p>
    </div>
    <div class="p-5 rounded-2xl bg-slate-800/50 border border-slate-700/60 shadow-xl">
      <p class="text-xs font-medium text-slate-400 uppercase tracking-wider">Avg Latency</p>
      <p class="text-3xl font-extrabold text-white mt-2">0.84ms <span class="text-xs font-semibold text-cyan-400">Global</span></p>
    </div>
    <div class="p-5 rounded-2xl bg-slate-800/50 border border-slate-700/60 shadow-xl">
      <p class="text-xs font-medium text-slate-400 uppercase tracking-wider">Monthly Run Rate</p>
      <p class="text-3xl font-extrabold text-emerald-400 mt-2">$248,500</p>
    </div>
  </div>

  <div class="p-6 rounded-2xl bg-gradient-to-br from-indigo-950/40 to-slate-900 border border-indigo-500/20 flex items-center justify-between">
    <div>
      <h3 class="text-sm font-bold text-white">Automated Motion Generation Engine</h3>
      <p class="text-xs text-slate-400 mt-1">Render broadcast-ready videos in sub-seconds with AI.</p>
    </div>
    <button class="px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-cyan-600 text-white text-xs font-bold rounded-xl shadow-lg shadow-indigo-600/40">
      Launch Pipeline →
    </button>
  </div>
</div>
""", width=1380, height=740, scale=2.0)

browser.add_content(live_ui)
scene.add(browser)

# 6. Cursor
cursor = Cursor(position=(1800, 950))
scene.add(cursor)

# 7. Choreography
@scene.animate
def script():
    scene.add_sfx("whoosh", 0.0)
    yield scene.all(
        *title.reveal_characters(stagger=0.018, duration=0.7),
        *browser.pop_in(delay=0.1, duration=0.8),
    )

    # 3D Tilt + Specular Rim Gleam
    scene.add_sfx("pop", 0.8)
    yield scene.all(
        *browser.tilt_3d(pitch=0.18, yaw=-0.20, duration=1.2),
        browser.gleam(duration=1.2, delay=0.1),
    )

    # Move cursor and click button
    yield cursor.move_to((1280, 780), duration=0.8)
    scene.add_sfx("click", 2.8)
    yield cursor.click()

    browser.float_idle(amplitude=6, speed=1.2)
    yield scene.wait(1.5)


if __name__ == "__main__":
    scene.storyboard("tailwind_storyboard.png")
    print("Storyboard saved to tailwind_storyboard.png")
