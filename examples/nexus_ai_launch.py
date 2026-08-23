"""
NEXUS AI - Cinematic Multi-Scene Launch Video (30 seconds)
==========================================================
6 Acts covering all 7 Vibmo asset catalog sections.

ACT I   (0.0-4.5s)  - Cold Open: Cosmic Genesis
ACT II  (4.5-9.0s)  - Holographic Title Reveal
ACT III (9.0-16.0s) - Multi-Agent AI Dashboard
ACT IV  (16.0-21.0s)- Live Performance Metrics & Charts
ACT V   (21.0-26.0s)- Hardware Ecosystem Showcase
ACT VI  (26.0-30.0s)- Grand Finale CTA & Logo Hold
"""

from motio.agent_api import *

# ===========================================================================
# SCENE SETUP
# ===========================================================================
scene = Scene(
    width=1920,
    height=1080,
    fps=60,
    duration=30.0,
    background=Color.hex("#020408"),
)

# ===========================================================================
# ACT I  - Cold Open: Cosmic Genesis  (0.0 - 4.5s)
# ===========================================================================

# Volumetric nebula clouds drifting in deep space
cosmos = CosmicNebulaBackdrop(width=1920, height=1080, seed=7)
cosmos.opacity.set(0.0)
scene.add(cosmos)

# Particle constellation web for depth
constellation = ParticleConstellationNetwork(
    num_particles=80,
    connection_distance=140,
    speed=18,
    width=1920,
    height=1080,
)
constellation.opacity.set(0.0)
scene.add(constellation)

# Hyperspace warp tunnel - dramatic burst bridging Acts I and II
warp = HyperspaceWarpTunnel(
    speed=3.0,
    rings=24,
    ring_color=colors.CYAN,
    thickness=2.5,
)
warp.opacity.set(0.0)
scene.add(warp)

# ===========================================================================
# ACT II - Holographic Title Reveal  (4.5 - 9.0s)
# ===========================================================================

# Main brand hologram title
holo_nexus = HologramChromaText(
    text="NEXUS",
    font_size=180,
    position=(960, 460),
)
holo_nexus.anchor.set((0.5, 0.5))
holo_nexus.opacity.set(0.0)
scene.add(holo_nexus)

# Tagline with glitch decryptor effect
glitch_tagline = GlitchDecryptorText(
    text="INFRASTRUCTURE FOR SUPERINTELLIGENCE",
    font_size=26,
    color=colors.CYAN,
    position=(960, 610),
)
glitch_tagline.anchor.set((0.5, 0.5))
glitch_tagline.opacity.set(0.0)
scene.add(glitch_tagline)

# Version badge using NeonText
neon_badge = NeonText(
    text="v2.0  LIVE",
    color=colors.EMERALD,
    font_size=22,
    flicker=False,
    position=(960, 680),
)
neon_badge.anchor.set((0.5, 0.5))
neon_badge.opacity.set(0.0)
scene.add(neon_badge)

# ===========================================================================
# ACT III - Multi-Agent AI Dashboard  (9.0 - 16.0s)
# ===========================================================================

# PCB circuit traces backdrop
circuit_bg = PcbCircuitTracesFlow(
    width=1920,
    height=1080,
    board_color=Color.hex("#030812"),
    trace_color=colors.INDIGO,
    pulse_color=colors.CYAN,
    num_traces=18,
)
circuit_bg.opacity.set(0.0)
scene.add(circuit_bg)

# Left panel: agent conversation thread (3 stacked bubbles)
bubble_planner = AgentConversationBubble(
    name="Planner",
    role="Task Orchestrator",
    body="Decomposing goal into 7 parallel sub-tasks...",
    avatar_color=colors.INDIGO,
    position=(60, 200),
    width=480,
)
bubble_planner.opacity.set(0.0)
scene.add(bubble_planner)

bubble_coder = AgentConversationBubble(
    name="Coder",
    role="CUDA Engineer",
    body="Generating optimized fused attention kernel.",
    avatar_color=colors.EMERALD,
    position=(60, 380),
    width=480,
)
bubble_coder.opacity.set(0.0)
scene.add(bubble_coder)

bubble_reviewer = AgentConversationBubble(
    name="Reviewer",
    role="Quality Gate",
    body="All 1,248 tests passing. Merging to main.",
    avatar_color=colors.AMBER,
    position=(60, 560),
    width=480,
)
bubble_reviewer.opacity.set(0.0)
scene.add(bubble_reviewer)

# Center panel: streaming LLM token output
token_streamer = StreamingTokenOutput(
    width=680,
    height=560,
    position=(590, 200),
)
token_streamer.opacity.set(0.0)
scene.add(token_streamer)

# Right panel: Tree-of-Thought reasoning graph
tot_tree = TreeOfThoughtTree(
    root_thought="Deploy gpt5-nexus globally",
    position=(1330, 200),
)
tot_tree.opacity.set(0.0)
scene.add(tot_tree)

# Bottom HUD: digital gauge cluster (GPU/VRAM/throughput/latency)
gauge_hud = DigitalGaugeClusterHud(
    width=1760,
    height=90,
    corner_radius=14,
    speed=1840.0,
    battery_percentage=98.5,
    position=(960, 970),
)
gauge_hud.anchor.set((0.5, 0.5))
gauge_hud.opacity.set(0.0)
scene.add(gauge_hud)

# ===========================================================================
# ACT IV - Live Performance Metrics & Charts  (16.0 - 21.0s)
# ===========================================================================

# Animated mesh gradient background
mesh_bg = MeshGradientFlow(
    width=1920,
    height=1080,
    colors_list=[Color.hex("#0a0f2e"), Color.hex("#060d1a"), Color.hex("#0d0a2e")],
    speed_multiplier=0.5,
)
mesh_bg.opacity.set(0.0)
scene.add(mesh_bg)

# Flowing streamgraph - revenue by segment (left)
wave_stream = FlowingStreamgraphArea(
    data=[
        [12, 18, 28, 42, 64, 98, 148],
        [8,  15, 22, 35, 50, 72, 104],
        [22, 30, 38, 45, 55, 63, 78],
        [5,  8,  11, 14, 17, 20, 24],
    ],
    colors_list=[colors.INDIGO, colors.CYAN, colors.EMERALD, colors.AMBER],
    width=860,
    height=380,
    position=(80, 180),
)
wave_stream.opacity.set(0.0)
scene.add(wave_stream)

# Sankey flow diagram - data pipeline (right)
sankey_nodes = {
    "Raw Data":   {"label": "Raw Data",   "color": colors.SLATE_400},
    "Ingestion":  {"label": "Ingestion",  "color": colors.INDIGO},
    "Processing": {"label": "Processing", "color": colors.CYAN},
    "Embeddings": {"label": "Embeddings", "color": colors.EMERALD},
    "FineTuning": {"label": "Fine-Tuning","color": colors.AMBER},
    "Inference":  {"label": "Inference",  "color": colors.ROSE},
    "Response":   {"label": "Response",   "color": colors.WHITE},
}
sankey_links = [
    {"source": "Raw Data",   "target": "Ingestion",  "value": 980},
    {"source": "Ingestion",  "target": "Processing", "value": 860},
    {"source": "Processing", "target": "Embeddings", "value": 540},
    {"source": "Processing", "target": "FineTuning", "value": 320},
    {"source": "Embeddings", "target": "Inference",  "value": 540},
    {"source": "FineTuning", "target": "Inference",  "value": 320},
    {"source": "Inference",  "target": "Response",   "value": 860},
]
sankey = SankeyFlowDiagram(
    nodes_data=sankey_nodes,
    links_data=sankey_links,
    position=(980, 180),
)
sankey.opacity.set(0.0)
scene.add(sankey)

# 4 metric cards in a row at the bottom
def make_card(label, start, end, prefix="", suffix="", col=colors.CYAN):
    card = GlassCard(
        corner_radius=14,
        padding=22,
        position=(0, 0),
        width=340,
    )
    card.add(
        KineticText(label, font_size=11, bold=True, color=colors.SLATE_400),
        MetricCounter(
            start_val=start, end_val=end,
            prefix=prefix, suffix=suffix,
            font_size=40, bold=True, color=col,
        ),
    )
    card.opacity.set(0.0)
    return card

card_tokens   = make_card("TOKENS / SEC",    0,      1_240_000, suffix=" k/s", col=colors.CYAN)
card_uptime   = make_card("UPTIME SLA",      99.0,   99.998,    suffix="%",    col=colors.EMERALD)
card_clusters = make_card("ACTIVE CLUSTERS", 0,      2_840,                    col=colors.AMBER)
card_cost     = make_card("COST / M TOKENS", 8.00,   0.38,      prefix="$",   col=colors.ROSE)

metrics_row = GlassCard(
    corner_radius=0,
    padding=0,
    fill=Color.TRANSPARENT,
    stroke=Color.TRANSPARENT,
    position=(960, 670),
)
metrics_row.anchor.set((0.5, 0.5))
metrics_row.add(card_tokens, card_uptime, card_clusters, card_cost)
metrics_row.opacity.set(0.0)
scene.add(metrics_row)

# ===========================================================================
# ACT V - Hardware Ecosystem Showcase  (21.0 - 26.0s)
# ===========================================================================

# Multi-monitor developer rig - the hero device
dev_rig = MultiMonitorDeveloperRig(
    screen_width=620,
    screen_height=350,
    gap=18,
    position=(960, 530),
)
dev_rig.anchor.set((0.5, 0.5))
dev_rig.scale.set((0.0, 0.0))
dev_rig.opacity.set(0.0)
scene.add(dev_rig)

# Spatial visor - floating upper-right
visor = SpatialVisorFrame(
    width=460,
    height=240,
    position=(1540, 290),
)
visor.anchor.set((0.5, 0.5))
visor.opacity.set(0.0)
scene.add(visor)

# Handheld gaming console - mobile edge device, lower-left
handheld = HandheldGamingConsoleFrame(
    position=(300, 760),
)
handheld.anchor.set((0.5, 0.5))
handheld.opacity.set(0.0)
scene.add(handheld)

# Token quota meter - context window ring, lower-right
quota_ring = TokenQuotaMeter(
    used=7_600_000,
    total=10_000_000,
    radius=100,
    thickness=20,
    fill_color=colors.CYAN,
    position=(1640, 800),
)
quota_ring.opacity.set(0.0)
scene.add(quota_ring)

# Speedometer needle gauge - P99 latency, upper-left
latency_gauge = SpeedometerNeedleGauge(
    min_val=0,
    max_val=500,
    radius=110,
    position=(270, 310),
)
latency_gauge.opacity.set(0.0)
scene.add(latency_gauge)

# ===========================================================================
# ACT VI - Grand Finale CTA & Logo Hold  (26.0 - 30.0s)
# ===========================================================================

# Terminal logs - deploy command
terminal = InteractiveTerminalLogs(
    logs=[
        "$ nexus deploy --model gpt5-nexus --scale global",
        "[  OK  ] Connecting to 1024 inference nodes...",
        "[  OK  ] Health checks passing on all regions.",
        "[  OK  ] Traffic routing: 100% live. Deploy complete.",
    ],
    execution_time="3.2s",
    width=960,
    height=220,
    position=(960, 790),
)
terminal.anchor.set((0.5, 0.5))
terminal.opacity.set(0.0)
scene.add(terminal)

# Magnetic gravity letters for CTA
cta_text = MagneticGravityLetters(
    text="GET STARTED FREE",
    font_size=38,
    color=colors.WHITE,
    gravity=1800.0,
    floor_y=920.0,
    stagger_time=0.06,
    position=(960, 920),
)
cta_text.anchor.set((0.5, 0.5))
cta_text.opacity.set(0.0)
scene.add(cta_text)

# Digital speed ticker - 8.84B API calls served
api_counter = MetricCounter(
    start_val=0,
    end_val=8_840_000_000,
    suffix=" API Calls Served",
    font_size=32,
    bold=True,
    color=colors.CYAN,
    position=(960, 560),
)
api_counter.anchor.set((0.5, 0.5))
api_counter.opacity.set(0.0)
scene.add(api_counter)

# Final holographic brand logo
final_logo = HologramChromaText(
    text="NEXUS AI",
    font_size=100,
    position=(960, 440),
)
final_logo.anchor.set((0.5, 0.5))
final_logo.opacity.set(0.0)
scene.add(final_logo)

# ===========================================================================
# POST-FX - Cinematic global grade
# ===========================================================================
scene.add_post_fx(
    ChromaticAberration(offset=2.5),   # lightweight — fringe aberration only
    Vignette(intensity=0.42, radius=0.62),
    FilmGrain(amount=0.009),
)

# ===========================================================================
# PROCEDURAL AUDIO - Layered 30-second soundtrack
# ===========================================================================

# Sci-fi ambient drone - continuous underscoring
ambient = AmbientDroneSuite.dark_scifi_drone(duration=30.0)
scene.add_audio(ambient, volume=0.30)

# Act I: Shepard-tone tension riser from silence
riser_intro = RiserTensionSuite.shepard_tone_riser(duration=4.2)
scene.add_audio(riser_intro, volume=0.55)

# Act II: cinematic 808 sub drop on hologram reveal
sub_drop = ImpactSubSuite.cinematic_808_drop(duration=2.0)
scene.add_audio(sub_drop, volume=0.88)

# Act II->III: doppler whip transition
whoosh_12 = WhooshDesignerSuite.doppler_whip(duration=0.7)
scene.add_audio(whoosh_12, volume=0.60)

# Act III: holographic UI clicks as panels spawn
for _ in range(4):
    click = CyberUISFXSuite.holo_chirp()
    scene.add_audio(click, volume=0.45)

# Act IV: crystal bell chime sparkle on metrics reveal
chime = ChimesHarmonicSuite.crystal_bell_chime()
scene.add_audio(chime, volume=0.65)

# Act V->VI: cyber pitch riser builds finale tension
riser_fin = RiserTensionSuite.cyber_pitch_riser(duration=2.8)
scene.add_audio(riser_fin, volume=0.50)

# Act VI: massive impact slam on final logo
final_slam = ImpactSubSuite.card_slam_impact()
scene.add_audio(final_slam, volume=0.95)

# ===========================================================================
# CHOREOGRAPHY - The full 30-second script
# ===========================================================================
@scene.animate
def main():

    # -- ACT I: Cold Open - Cosmic Genesis (0.0 - 4.5s) ---------------------
    yield scene.all(
        cosmos.opacity.to(1.0, duration=3.5, ease=Ease.in_out_quad),
        constellation.opacity.to(0.7, duration=3.0, ease=Ease.in_out_quad, delay=0.6),
    )
    # Hyperspace warp burst foreshadowing the reveal
    yield warp.opacity.to(0.85, duration=0.6, ease=Ease.out_expo)
    yield scene.wait(0.35)

    # -- ACT II: Holographic Title Reveal (4.5 - 9.0s) ----------------------
    yield scene.all(
        warp.opacity.to(0.0, duration=0.5),
        cosmos.opacity.to(0.40, duration=1.0),
        holo_nexus.opacity.to(1.0, duration=0.35),
        holo_nexus.pop_in(duration=0.9, scale_from=0.3, ease=Ease.out_expo),
    )
    yield scene.wait(0.4)

    # Tagline decrypts character by character
    yield scene.all(
        glitch_tagline.opacity.to(1.0, duration=0.2),
        glitch_tagline.decrypt(duration=1.8),
    )
    yield scene.wait(0.35)

    # Neon badge fades in
    yield neon_badge.opacity.to(1.0, duration=0.6, ease=Ease.out_quad)
    holo_nexus.float_idle(amplitude=9, speed=0.65)
    neon_badge.float_idle(amplitude=4, speed=0.9)
    yield scene.wait(0.9)

    # -- ACT III: Multi-Agent AI Dashboard (9.0 - 16.0s) --------------------
    # Wipe everything out, bring in circuit backdrop
    yield scene.all(
        holo_nexus.fade_out(duration=0.55),
        glitch_tagline.fade_out(duration=0.45),
        neon_badge.fade_out(duration=0.45),
        cosmos.opacity.to(0.0, duration=0.8),
        constellation.opacity.to(0.0, duration=0.7),
        circuit_bg.opacity.to(0.88, duration=1.0, delay=0.25),
    )

    # Staggered panel pop-ins - left column agents
    yield scene.all(
        bubble_planner.opacity.to(1.0, duration=0.4),
        bubble_planner.pop_in(duration=0.65),
    )
    yield scene.wait(0.15)
    yield scene.all(
        bubble_coder.opacity.to(1.0, duration=0.4),
        bubble_coder.pop_in(duration=0.65),
        token_streamer.opacity.to(1.0, duration=0.5),
        token_streamer.pop_in(duration=0.7),
    )
    yield scene.wait(0.15)
    yield scene.all(
        bubble_reviewer.opacity.to(1.0, duration=0.4),
        bubble_reviewer.pop_in(duration=0.65),
        tot_tree.opacity.to(1.0, duration=0.5),
        tot_tree.pop_in(duration=0.7),
    )
    yield scene.wait(0.2)

    # Token stream fires + ToT expands reasoning branches
    yield scene.all(
        token_streamer.stream_text(
            "Analyzing 1.2B parameter checkpoint...\n"
            "Loss: 0.881 -> 0.720 -> 0.599\n"
            "Validation perplexity: 12.4  [BEST]\n"
            "Checkpoint saved. Deploying to cluster.",
            duration=2.8,
        ),
        tot_tree.expand_node(
            parent_id="root",
            child_nodes=[
                {"id": "hyp_a", "thought": "Hypothesis A: Scale inference horizontally", "score": 0.91},
                {"id": "hyp_b", "thought": "Hypothesis B: Distil to smaller model", "score": 0.74},
            ],
            duration=1.2,
        ),
    )
    yield scene.wait(0.4)

    # Telemetry gauge cluster slides up
    yield scene.all(
        gauge_hud.opacity.to(1.0, duration=0.55),
        gauge_hud.pop_in(duration=0.7),
    )
    yield scene.wait(0.75)

    # -- ACT IV: Live Performance Metrics & Charts (16.0 - 21.0s) -----------
    # Clear dashboard, surface mesh gradient
    yield scene.all(
        bubble_planner.fade_out(duration=0.4),
        bubble_coder.fade_out(duration=0.4),
        bubble_reviewer.fade_out(duration=0.4),
        token_streamer.fade_out(duration=0.45),
        tot_tree.fade_out(duration=0.45),
        gauge_hud.fade_out(duration=0.35),
        circuit_bg.opacity.to(0.0, duration=0.75),
        mesh_bg.opacity.to(1.0, duration=0.75, delay=0.25),
    )

    # Streamgraph + Sankey reveal together
    yield scene.all(
        wave_stream.opacity.to(1.0, duration=0.5),
        wave_stream.pop_in(duration=0.7),
        sankey.opacity.to(1.0, duration=0.5, delay=0.2),
        sankey.pop_in(duration=0.7, delay=0.2),
    )
    # Animate the Sankey flow ribbons through the pipeline
    yield sankey.trace_flow(duration=1.6)
    yield scene.wait(0.3)

    # Metric cards cascade in with stagger
    yield scene.all(
        metrics_row.opacity.to(1.0, duration=0.35),
        card_tokens.pop_in(duration=0.6),
        card_uptime.pop_in(duration=0.6, delay=0.1),
        card_clusters.pop_in(duration=0.6, delay=0.2),
        card_cost.pop_in(duration=0.6, delay=0.3),
    )
    # All four counters fire simultaneously - the money shot
    yield scene.all(
        card_tokens.children[1].count_to(duration=1.8, ease=Ease.out_expo),
        card_uptime.children[1].count_to(duration=1.8, ease=Ease.out_expo),
        card_clusters.children[1].count_to(duration=1.8, ease=Ease.out_expo),
        card_cost.children[1].count_to(duration=1.8, ease=Ease.out_expo),
    )
    yield scene.wait(0.35)

    # -- ACT V: Hardware Ecosystem Showcase (21.0 - 26.0s) ------------------
    yield scene.all(
        wave_stream.fade_out(duration=0.45),
        sankey.fade_out(duration=0.45),
        metrics_row.fade_out(duration=0.4),
        mesh_bg.opacity.to(0.0, duration=0.65),
        # Cosmos returns as a subtle backdrop
        cosmos.opacity.to(0.35, duration=0.9, delay=0.2),
    )

    # Multi-monitor rig springs in as the hero shot
    yield scene.all(
        dev_rig.opacity.to(1.0, duration=0.55),
        dev_rig.scale.to((1.0, 1.0), duration=1.0, ease=Ease.spring(stiffness=80, damping=10)),
    )
    yield scene.wait(0.2)

    # Visor + handheld flank the rig from opposite sides
    yield scene.all(
        visor.opacity.to(1.0, duration=0.5),
        visor.pop_in(duration=0.7),
        handheld.opacity.to(1.0, duration=0.5, delay=0.12),
        handheld.pop_in(duration=0.7, delay=0.12),
    )

    # Overlay instruments animate on
    yield scene.all(
        quota_ring.opacity.to(1.0, duration=0.4),
        latency_gauge.opacity.to(1.0, duration=0.4),
        latency_gauge.sweep_to(38, duration=1.0),     # 38ms P99 latency
    )

    # Gentle continuous float on all hardware
    dev_rig.float_idle(amplitude=7, speed=0.85)
    visor.float_idle(amplitude=5, speed=1.1)
    handheld.float_idle(amplitude=6, speed=1.25)
    yield scene.wait(1.4)

    # -- ACT VI: Grand Finale CTA & Logo Hold (26.0 - 30.0s) ----------------
    # Clear hardware, nebula swells to full
    yield scene.all(
        dev_rig.fade_out(duration=0.5),
        visor.fade_out(duration=0.5),
        handheld.fade_out(duration=0.5),
        quota_ring.fade_out(duration=0.4),
        latency_gauge.fade_out(duration=0.4),
        cosmos.opacity.to(0.75, duration=1.0, delay=0.15),
        constellation.opacity.to(0.55, duration=1.0, delay=0.25),
    )

    # Terminal logs fade up - the deploy moment
    yield scene.all(
        terminal.opacity.to(1.0, duration=0.4),
        terminal.fade_up(offset=20, duration=0.6),
    )
    yield scene.wait(0.5)

    # API call odometer slams to 8.84B
    yield scene.all(
        api_counter.opacity.to(1.0, duration=0.4),
        api_counter.count_to(duration=1.4, ease=Ease.out_expo),
    )
    yield scene.wait(0.3)

    # Holographic logo materialises with spring entrance
    yield scene.all(
        final_logo.opacity.to(1.0, duration=0.4),
        final_logo.pop_in(duration=0.85, scale_from=0.2, ease=Ease.out_expo),
    )
    final_logo.float_idle(amplitude=5, speed=0.55)

    yield scene.wait(0.35)

    # Magnetic CTA letters drop from gravity into formation
    yield scene.all(
        cta_text.opacity.to(1.0, duration=0.3),
        cta_text.progress.to(1.0, duration=1.2, ease=Ease.out_expo),
    )

    # Grand hold - let the composition breathe
    yield scene.wait(1.15)


# ===========================================================================
# OUTPUT
# ===========================================================================
if __name__ == "__main__":
    print("NEXUS AI - Cinematic Multi-Scene Launch Video")
    print("=" * 52)

    print("[1/3] Pre-flight validation...")
    scene.validate()
    print("      OK\n")

    print("[2/3] Generating 6-frame storyboard contact sheet...")
    scene.storyboard("nexus_ai_storyboard.png", rows=2, cols=3)
    print("      Saved: nexus_ai_storyboard.png\n")

    print("[3/3] Rendering 1080p 60FPS master video (30s)...")
    scene.render("nexus_ai_launch.mp4", quality="high", resume=True, max_workers=1)
    print("      Saved: nexus_ai_launch.mp4  Ready for broadcast.")
