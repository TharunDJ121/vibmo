"""
✦ NEXUS: Autonomous Intelligence & Global Compute
World-Class Multi-Scene Motion Graphics Showcase in Motio / Vibmo.
Demonstrates procedural audio, dynamic backdrops, hardware enclosures,
interactive AI UI, high-precision charts, kinetic typography, and post-FX shaders.
"""

from __future__ import annotations
import math
import numpy as np

# Single-Line God Import
from motio.agent_api import *


# ==============================================================================
# ACT 1: The Quantum Ignition (Cinematic Sci-Fi Intro)
# ==============================================================================
def create_act_1() -> Scene:
    scene = Scene(
        width=1920,
        height=1080,
        fps=60,
        duration=3.5,
        background=colors.DARK_NAVY,
    )

    # 1. Non-Static Animated Cosmic Backdrop & Post-FX
    nebula = CosmicNebula(width=1920, height=1080, seed=42)
    particles = ParticleConstellation(num_particles=45, connection_distance=140.0, speed=18.0)
    scene.add(nebula, particles)
    scene.add_post_fx(
        Vignette(intensity=0.35),
        FilmGrain(amount=0.015),
    )

    # 2. Hero Cyberpunk Kinetic Typography
    title_box = GlassCard(direction="column", gap=16, padding=36, corner_radius=24, position=(960, 520))
    title = GlitchDecryptorText("NEXUS OS 3.0", font_size=56, color=colors.CYAN)
    subtitle = KineticText("Autonomous Neural Compute & Global Swarm", font_size=26, color=colors.SLATE_400, bold=True)
    status_pill = GlassCard(direction="row", gap=10, padding=12, corner_radius=12, fill=colors.CYAN.with_alpha(0.12))
    status_icon = Icon("lucide:cpu", size=22, color=colors.CYAN)
    status_text = KineticText("QUANTUM CORES: SYNCHRONIZED", font_size=16, bold=True, color=colors.CYAN)
    status_pill.add(status_icon, status_text)

    title_box.add(title, subtitle, status_pill)
    scene.add(title_box)

    @scene.animate
    def main():
        yield title_box.pop_in(delay=0.1, duration=0.8)
        yield scene.all(
            title.decrypt(duration=1.6),
            subtitle.reveal_characters(stagger=0.02, duration=0.7),
            status_icon.bounce(amplitude=1.4, count=2),
        )
        title_box.float_idle(amplitude=6, speed=1.2)
        yield scene.wait(0.8)

    return scene


# ==============================================================================
# ACT 2: Interactive AI Agent & Developer Platform
# ==============================================================================
def create_act_2() -> Scene:
    scene = Scene(
        width=1920,
        height=1080,
        fps=60,
        duration=4.0,
        background=colors.DARK_NAVY,
    )

    # 1. Mesh Gradient Dynamic Flow
    bg = MeshGradientFlow(width=1920, height=1080, colors_list=[colors.INDIGO, colors.CYAN, colors.DARK_NAVY])
    scene.add(bg)
    scene.add_post_fx(Vignette(intensity=0.25), FilmGrain(amount=0.01))

    # 2. Super Ultrawide Hardware Monitor Frame
    monitor = SuperUltrawideMonitorFrame(height=420.0, position=(960, 540))
    
    # 3. Interactive AI UI Elements
    left_card = GlassCard(direction="column", gap=18, padding=32, corner_radius=20, position=(520, 540))
    ai_header = KineticText("Lattice Reasoning Tree", font_size=24, bold=True, color=colors.WHITE)
    streamer = StreamingTokenOutput(width=520, height=180)
    counter = MetricCounter(start_val=0, end_val=4850000, prefix="THROUGHPUT: ", suffix=" TOK/S", font_size=28, bold=True, color=colors.EMERALD)
    left_card.add(ai_header, streamer, counter)

    right_card = GlassCard(direction="column", gap=16, padding=32, corner_radius=20, position=(1400, 540))
    pr_pill = GlassCard(direction="row", gap=12, padding=14, corner_radius=14, fill=colors.EMERALD.with_alpha(0.15))
    pr_icon = Icon("lucide:git-pull-request", size=24, color=colors.EMERALD)
    pr_title = KineticText("PR #100: Auto-Merge", font_size=20, bold=True, color=colors.EMERALD)
    pr_pill.add(pr_icon, pr_title)
    
    tier_info = KineticText("Cluster: Tier 1 Enterprise Distributed", font_size=18, color=colors.SLATE_400)
    right_card.add(pr_pill, tier_info)

    cursor = Cursor(position=(300, 900))

    scene.add(monitor, left_card, right_card, cursor)

    @scene.animate
    def main():
        yield scene.all(
            left_card.pop_in(delay=0.1, duration=0.7),
            right_card.pop_in(delay=0.2, duration=0.7),
            cursor.move_to(left_card, duration=0.8),
        )
        yield cursor.click()
        yield scene.all(
            streamer.stream_text("Evaluating 128 parallel branches... Optimal latency route found: 0.84ms.", duration=1.6),
            counter.count_to(duration=1.8, ease=Ease.out_expo),
            cursor.move_to(right_card, duration=1.0),
        )
        yield cursor.click()
        yield pr_icon.bounce(amplitude=1.5, count=2)
        left_card.float_idle(amplitude=4, speed=1.0)
        right_card.float_idle(amplitude=4, speed=1.0)
        yield scene.wait(0.6)

    return scene


# ==============================================================================
# ACT 3: Real-Time High-Frequency Financial & Spatial Telemetry
# ==============================================================================
def create_act_3() -> Scene:
    scene = Scene(
        width=1920,
        height=1080,
        fps=60,
        duration=4.0,
        background=colors.DARK_NAVY,
    )

    # 1. Circuit Traces & Topographic Contours
    traces = CircuitBoardTraces(width=1920, height=1080, trace_color=colors.CYAN)
    scene.add(traces)
    scene.add_post_fx(Vignette(intensity=0.25), FilmGrain(amount=0.01))

    # 2. Simulated Financial OHLC Candlestick Data
    ohlc = [
        {"open": 100 + math.sin(i * 0.4) * 15 + i * 2,
         "high": 105 + math.sin(i * 0.4) * 15 + i * 2 + 6,
         "low": 96 + math.sin(i * 0.4) * 15 + i * 2 - 4,
         "close": 103 + math.sin(i * 0.4) * 15 + i * 2 + 3}
        for i in range(24)
    ]

    chart_box = GlassCard(direction="column", gap=16, padding=28, corner_radius=22, position=(580, 520))
    chart_title = KineticText("High-Frequency Liquidity & Execution Telemetry", font_size=22, bold=True, color=colors.CYAN)
    chart = ProCandlestickChart(data=ohlc, width=640, height=300)
    chart_box.add(chart_title, chart)

    stats_box = GlassCard(direction="column", gap=20, padding=32, corner_radius=22, position=(1380, 520))
    tvl_counter = MetricCounter(start_val=0, end_val=142500000, prefix="$", suffix=" TVL", font_size=44, bold=True, color=colors.EMERALD)
    latency_gauge = MetricCounter(start_val=250, end_val=0, prefix="P99: ", suffix=".8 ms", font_size=36, bold=True, color=colors.CYAN)
    board = SplitFlapAirportBoard(initial_text="INITIALIZING", tile_width=44, tile_height=66, gap=6)
    stats_box.add(tvl_counter, latency_gauge, board)

    scene.add(chart_box, stats_box)

    @scene.animate
    def main():
        yield scene.all(
            chart_box.pop_in(delay=0.1, duration=0.7),
            stats_box.pop_in(delay=0.2, duration=0.7),
        )
        board.flip_to("GLOBAL PROD OK", duration=1.6)
        yield scene.all(
            tvl_counter.count_to(duration=2.0, ease=Ease.out_expo),
            latency_gauge.count_to(duration=1.8, ease=Ease.out_expo),
        )
        chart_box.float_idle(amplitude=5, speed=1.1)
        stats_box.float_idle(amplitude=5, speed=1.1)
        yield scene.wait(0.8)

    return scene


# ==============================================================================
# ACT 4: Production Certification & Turnkey Outro
# ==============================================================================
def create_act_4() -> Scene:
    scene = Scene(
        width=1920,
        height=1080,
        fps=60,
        duration=3.5,
        background=colors.DARK_NAVY,
    )

    # 1. Digital Matrix Rain + CRT Post-Processing
    matrix_bg = DigitalMatrixRain(width=1920, height=1080, font_size=20)
    scene.add(matrix_bg)
    scene.add_post_fx(
        CrtPhosphorBloomShader(intensity=0.5, radius=4.0),
        Vignette(intensity=0.3),
        FilmGrain(amount=0.015),
    )

    # 2. Hero Outro Typographic Hierarchy & Stamp
    title_outro = KineticText("The Future of Motion Intelligence", font_size=46, bold=True, color=colors.WHITE, position=(960, 380))
    stamp = RubberStampTitleSlam("ENTERPRISE READY", color=colors.ROSE, font_size=48, position=(960, 520))
    
    cta_card = GlassCard(direction="row", gap=16, padding=24, corner_radius=18, position=(960, 720), fill=colors.CYAN.with_alpha(0.18), stroke=colors.CYAN)
    cta_icon = Icon("lucide:rocket", size=32, color=colors.CYAN)
    cta_text = ElasticSquashBounceTitle("DEPLOY WITH MOTIO", font_size=32, color=colors.WHITE)
    cta_card.add(cta_icon, cta_text)

    scene.add(title_outro, stamp, cta_card)

    @scene.animate
    def main():
        yield title_outro.reveal_characters(stagger=0.02, duration=0.8)
        yield stamp.slam(duration=0.6)
        yield cta_card.pop_in(duration=0.6)
        yield scene.all(
            cta_text.bounce_in(duration=0.8),
            cta_icon.bounce(amplitude=1.5, count=3),
        )
        cta_card.float_idle(amplitude=6, speed=1.4)
        yield scene.wait(0.7)

    return scene


# ==============================================================================
# MASTER SEQUENCE ORCHESTRATION & EXPORT
# ==============================================================================
def build_masterpiece_sequence() -> Sequence:
    act1 = create_act_1()
    act2 = create_act_2()
    act3 = create_act_3()
    act4 = create_act_4()

    # Chain scenes with smooth crossfade transitions
    seq = Sequence(act1, act2, act3, act4, transition=CrossFade(duration=0.5))
    return seq


if __name__ == "__main__":
    print("[*] Compiling NEXUS Multi-Scene Motion Graphics Masterpiece...")
    masterpiece = build_masterpiece_sequence()

    # 1. Generate Contact Sheet Storyboard Progression
    storyboard_path = "nexus_masterpiece_storyboard.png"
    print(f"[*] Generating 6-Frame Contact Sheet: {storyboard_path}...")
    masterpiece.storyboard(storyboard_path, rows=2, cols=3)
    print(f"[+] Storyboard saved to {storyboard_path}!")

    # 2. Render 60 FPS Video (or Fast Preview)
    output_mp4 = "nexus_masterpiece_showcase.mp4"
    print(f"[*] Rendering Master Video: {output_mp4}...")
    masterpiece.render(output_mp4, quality="fast")
    print(f"[+] Masterpiece successfully rendered: {output_mp4}!")
