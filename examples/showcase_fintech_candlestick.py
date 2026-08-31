"""
Showcase 2: Cyberpunk Fintech Candlestick Chart with Neon Emissive Glow & Anamorphic Streak.
Demonstrates CandlestickChartPro, CyberGridHorizon, Glow, and AnamorphicStreak post-fx.
"""

from motio.agent_api import *

# 1. Initialize Scene (1080p @ 60 FPS)
scene = Scene(
    width=1920,
    height=1080,
    fps=60,
    duration=4.0,
    background=Color.from_hex("#090a10"),
)

# 2. Cyber Horizon Background & Anamorphic Post-FX
grid = CyberGridHorizon(grid_color=colors.CYAN.with_alpha(0.35), perspective=0.85)
scene.add(grid)

scene.add_post_fx(
    Glow(intensity=0.8, radius=32.0, threshold=0.45),
    AnamorphicStreak(intensity=0.6, streak_length=150.0, tint=(0.2, 0.8, 1.2)),
    Vignette(intensity=0.35, radius=0.7),
    ColorGrade(contrast=1.15, saturation=1.12),
)

# 3. Candlestick Chart Node
ohlc_sample_data = [
    {"open": 42000, "high": 43500, "low": 41800, "close": 43200, "volume": 1200},
    {"open": 43200, "high": 44800, "low": 42900, "close": 44500, "volume": 1800},
    {"open": 44500, "high": 45200, "low": 43800, "close": 44100, "volume": 950},
    {"open": 44100, "high": 46500, "low": 43900, "close": 46200, "volume": 2400},
    {"open": 46200, "high": 47800, "low": 45800, "close": 47500, "volume": 3100},
]

chart = CandlestickChartPro(
    ohlc_data=ohlc_sample_data,
    position=(240, 200),
    width=1440,
    height=680,
)
scene.add(chart)

# 4. Laser sparks burst on breakout candle
sparks = ParticleEmitter(preset="laser_sparks", position=(1300, 380), blend_mode="add")
scene.add(sparks)

@scene.animate
def main():
    yield chart.draw_bars(duration=1.8)
    yield sparks.burst(count=40, time=1.8)
    yield scene.wait(1.5)

if __name__ == "__main__":
    import os
    os.makedirs("output", exist_ok=True)
    scene.storyboard("output/showcase_fintech_candlestick_storyboard.png")
    print("[+] Generated showcase_fintech_candlestick_storyboard.png successfully!")
