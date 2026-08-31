"""
Unit and Integration Tests for Section 4: AI & SaaS Interactive UI Suites.
Covers all 15 suites, component classes, aliases, reactive signals, and generator animation verbs.
"""

from __future__ import annotations
import math
from typing import Any
import cairo
import pytest

from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease
from vibmo.scene.scene import Scene

# Import all suites directly from module files and package
from vibmo.product.ai import (
    StreamingTokenOutput,
    TokenStreamerSuite,
    TokenStreamerBox,
    ShimmeringCaretIndicator,
    TokenSpeedVelocityCounter,
    StopGenerationButton,
    TreeOfThoughtTree,
    ReasoningBranchNode,
    ReasoningNodeBranch,
    ExplorationScoreBadge,
    PrunedBranchFade,
    DiffusionCanvas,
    DiffusionGenerationCanvas,
    DenoisingProgress,
    PromptAspectSelector,
    SeedVariationPills,
    MagicPromptEnhanceBar,
    AgentTeamThread,
    AgentMessageBubble,
    AgentConversationBubble,
    AgentStatusPill,
    AgentTypingWave,
    ToolCallingPayloadCard,
    VectorEmbeddingsVisualizer,
    ClusterPoint,
    EmbeddingScatterCluster,
    CosineSimilarityLink,
    VectorDimensionBar,
    SearchQueryProbe,
    PricingTierMatrix,
    PricingTierGrid,
    PricingTierColumn,
    FeatureChecklistRow,
    AnnualBillingToggle,
    PopularGlowBadge,
    ApiKeyVault,
    ApiKeyVaultCard,
    KeySecretRow,
    MaskedTokenRevealField,
    CopyClipboardPill,
    RevokeConfirmModal,
    GitPrTimeline,
    MergeStatusPill,
    GitPullRequestCard,
    CommitShaBadge,
    CiCdCheckStatusPill,
    MergeSquashButton,
    TelemetryDialHUD,
    RadialGaugeDial,
    CircularCpuGaugeDial,
    RamMemoryMeterBar,
    NetworkPingLatencyLine,
    UptimePercentageBadge,
    VisualSqlQueryBuilder,
    SchemaTableNode,
    VisualSqlQueryBlock,
    TableJoinConnectorCurve,
    SqlSyntaxHighlightView,
    ExecutionTimePill,
    WebhookActivityFeed,
    WebhookEventStreamCard,
    HttpRequestInspector,
    PayloadJsonInspector,
    HttpStatusBadge,
    RetryEventButton,
    TokenQuotaMeter,
    UsageRingGauge,
    CircularTokenQuotaRing,
    OverLimitWarningBanner,
    UsageThresholdPill,
    UpgradeCtaButton,
    CodeSandboxPlayground,
    SplitCodePlayground,
    SplitConsoleOutput,
    InteractiveTerminalLogs,
    RunCodeSuccessIndicator,
    DependencyInstallPill,
    FeatureComparisonMatrix,
    InteractiveFeatureMatrix,
    CheckmarkCell,
    CompetitorComparisonRow,
    TooltipFeatureExplanation,
    StickyHeaderColumn,
    PromptDiffViewer,
    PromptDiffCard,
    SideBySideDiffPane,
    InlineDiffHighlighter,
    PromptTokenCostBadge,
    MergePromptButton,
)


@pytest.fixture
def cairo_ctx() -> cairo.Context:
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1920, 1080)
    return cairo.Context(surface)


# 1. StreamingTokenOutput Tests
def test_streaming_token_output(cairo_ctx: cairo.Context):
    streamer = StreamingTokenOutput(text="Analyzing model weights...", speed=30.0, width=600.0, height=350.0)
    assert streamer.width_val == 600.0
    assert streamer.height_val == 350.0
    assert streamer.full_text == "Analyzing model weights..."
    assert TokenStreamerSuite is StreamingTokenOutput
    assert TokenStreamerBox is StreamingTokenOutput

    # Test verb
    action = streamer.stream_tokens(speed=45.0)
    assert isinstance(action, AnimationAction)
    assert streamer.speed.get(0.0) == 45.0

    # Test bounds & draw
    bounds = streamer.local_bounds()
    assert bounds == (0.0, 0.0, 600.0, 350.0)
    streamer.draw(cairo_ctx, time=0.5)

    # Subcomponents
    caret = ShimmeringCaretIndicator()
    caret.draw(cairo_ctx, time=0.2)
    counter = TokenSpeedVelocityCounter(speed=40.0)
    counter.draw(cairo_ctx, time=0.2)
    stop_btn = StopGenerationButton()
    stop_btn.draw(cairo_ctx, time=0.2)


# 2. TreeOfThoughtTree Tests
def test_tree_of_thought_tree(cairo_ctx: cairo.Context):
    tot = TreeOfThoughtTree(root_thought="Root Reasoning", width=800.0, height=500.0)
    assert tot.width_val == 800.0
    assert tot.height_val == 500.0
    assert ReasoningBranchNode is ReasoningNodeBranch

    # Test expand_branch verb
    actions = tot.expand_branch(0)
    assert isinstance(actions, list)
    assert len(actions) > 0

    # Test expand_node
    actions_node = tot.expand_node("root", [])
    assert isinstance(actions_node, list)

    bounds = tot.local_bounds()
    assert bounds == (0.0, 0.0, 800.0, 500.0)
    tot.draw(cairo_ctx, time=0.5)

    # Subcomponents
    node_card = ReasoningBranchNode(node_id="n1", thought="Test Thought", status="Valid")
    node_card.draw(cairo_ctx, time=0.0)
    badge = ExplorationScoreBadge(score=0.95, is_winner=True)
    badge.draw(cairo_ctx, time=0.0)
    fade_edge = PrunedBranchFade(start_pos=(0.0, 0.0), end_pos=(100.0, 100.0))
    fade_edge.draw(cairo_ctx, time=0.0)


# 3. DiffusionCanvas Tests
def test_diffusion_canvas(cairo_ctx: cairo.Context):
    canvas = DiffusionCanvas(total_steps=25, width=640.0, height=540.0)
    assert canvas.width_val == 640.0
    assert canvas.total_steps == 25
    assert DiffusionGenerationCanvas is DiffusionCanvas

    # Test verb
    action = canvas.denoise_steps(steps=20)
    assert isinstance(action, AnimationAction)

    action2 = canvas.denoise_to(15)
    assert isinstance(action2, AnimationAction)

    bounds = canvas.local_bounds()
    assert bounds == (0.0, 0.0, 640.0, 540.0)
    canvas.draw(cairo_ctx, time=0.5)

    # Subcomponents
    prog = DenoisingProgress(current_step=12.0, total_steps=25)
    prog.draw(cairo_ctx, time=0.0)
    aspect = PromptAspectSelector()
    aspect.draw(cairo_ctx, time=0.0)
    seeds = SeedVariationPills()
    seeds.draw(cairo_ctx, time=0.0)
    enhance = MagicPromptEnhanceBar()
    enhance.draw(cairo_ctx, time=0.0)


# 4. AgentTeamThread Tests
def test_agent_team_thread(cairo_ctx: cairo.Context):
    chat = AgentTeamThread(title="Autonomous Swarm", width=680.0, height=520.0)
    assert chat.width_val == 680.0
    assert AgentMessageBubble is AgentConversationBubble

    # Test verb
    actions = chat.post_agent_message(sender="Coder", text="Fixed.", role="Engineer")
    assert isinstance(actions, list)
    assert len(actions) == 2

    bounds = chat.local_bounds()
    assert bounds == (0.0, 0.0, 680.0, 520.0)
    chat.draw(cairo_ctx, time=0.5)

    # Subcomponents
    bubble = AgentMessageBubble(name="Tester", role="QA", body="Test message body")
    bubble.draw(cairo_ctx, time=0.0)
    pill = AgentStatusPill(name="Reviewer", status="Active")
    pill.draw(cairo_ctx, time=0.0)
    wave = AgentTypingWave()
    wave.draw(cairo_ctx, time=0.5)
    tool_card = ToolCallingPayloadCard(tool_name="git_push", params="{}")
    tool_card.draw(cairo_ctx, time=0.0)


# 5. VectorEmbeddingsVisualizer Tests
def test_vector_embeddings_visualizer(cairo_ctx: cairo.Context):
    vec = VectorEmbeddingsVisualizer(dimension=3, num_points=60, radius=150.0)
    assert vec.dimension == 3
    assert len(vec.points) == 60

    # Test verb
    action = vec.rotate_cluster(angle=180.0)
    assert isinstance(action, AnimationAction)

    bounds = vec.local_bounds()
    assert bounds == (0.0, 0.0, 680.0, 500.0)
    vec.draw(cairo_ctx, time=0.5)

    # Subcomponents
    pt = ClusterPoint(x=10.0, y=20.0, z=30.0, cluster_id=1, color=colors.CYAN)
    assert pt.x == 10.0 and pt.z == 30.0
    scatter = EmbeddingScatterCluster(num_points=30)
    scatter.draw(cairo_ctx, time=0.0)
    link = CosineSimilarityLink(p1=(0.0, 0.0), p2=(50.0, 50.0), similarity=0.91)
    link.draw(cairo_ctx, time=0.5)
    dim_bar = VectorDimensionBar(width=200.0)
    dim_bar.draw(cairo_ctx, time=0.0)
    probe = SearchQueryProbe()
    probe.draw(cairo_ctx, time=0.5)


# 6. PricingTierMatrix Tests
def test_pricing_tier_matrix(cairo_ctx: cairo.Context):
    matrix = PricingTierMatrix(width=900.0, height=550.0)
    assert matrix.width_val == 900.0
    assert PricingTierGrid is PricingTierMatrix

    # Test verb
    actions = matrix.highlight_tier("Pro")
    assert isinstance(actions, list)
    assert len(actions) > 0

    bounds = matrix.local_bounds()
    assert bounds == (0.0, 0.0, 900.0, 550.0)
    matrix.draw(cairo_ctx, time=0.5)

    # Subcomponents
    col = PricingTierColumn(name="Starter", price="$0", interval="/mo", is_popular=False)
    col.draw(cairo_ctx, time=0.0)
    row = FeatureChecklistRow(text="Feature Test", active=True)
    row.draw(cairo_ctx, time=0.0)
    toggle = AnnualBillingToggle(is_annual=True)
    toggle.draw(cairo_ctx, time=0.0)
    badge = PopularGlowBadge(text="RECOMMENDED")
    badge.draw(cairo_ctx, time=0.0)


# 7. ApiKeyVault Tests
def test_api_key_vault(cairo_ctx: cairo.Context):
    vault = ApiKeyVault(width=720.0, height=460.0)
    assert vault.width_val == 720.0
    assert ApiKeyVaultCard is ApiKeyVault

    # Test verb
    action = vault.reveal_key(index=1)
    assert isinstance(action, AnimationAction)

    bounds = vault.local_bounds()
    assert bounds == (0.0, 0.0, 720.0, 460.0)
    vault.draw(cairo_ctx, time=0.5)

    # Subcomponents
    field = MaskedTokenRevealField(clear_text="sk-live-12345678")
    field.draw(cairo_ctx, time=0.5)
    action_hide = field.trigger_hide()
    assert isinstance(action_hide, AnimationAction)
    copy_btn = CopyClipboardPill()
    copy_btn.draw(cairo_ctx, time=0.0)
    modal = RevokeConfirmModal()
    modal.draw(cairo_ctx, time=0.0)
    secret_row = KeySecretRow(name="Test Key", clear_text="sk-test-abc")
    secret_row.draw(cairo_ctx, time=0.0)


# 8. GitPrTimeline Tests
def test_git_pr_timeline(cairo_ctx: cairo.Context):
    pr = GitPrTimeline(pr_number=88, title="feat(ai): Add SaaS suites", width=680.0, height=460.0)
    assert pr.pr_number == 88

    # Test verb
    actions = pr.animate_merge()
    assert isinstance(actions, list)
    assert len(actions) == 2

    bounds = pr.local_bounds()
    assert bounds == (0.0, 0.0, 680.0, 460.0)
    pr.draw(cairo_ctx, time=0.5)

    # Subcomponents
    status_pill = MergeStatusPill(status="Merged")
    status_pill.draw(cairo_ctx, time=0.0)
    sha_badge = CommitShaBadge(sha="c8491ae", message="Initial commit")
    sha_badge.draw(cairo_ctx, time=0.0)
    ci_status = CiCdCheckStatusPill(checks_count=50)
    ci_status.draw(cairo_ctx, time=0.0)
    merge_btn = MergeSquashButton(is_merged=False)
    merge_btn.draw(cairo_ctx, time=0.0)


# 9. TelemetryDialHUD Tests
def test_telemetry_dial_hud(cairo_ctx: cairo.Context):
    hud = TelemetryDialHUD(cpu=45.0, ram=16.0, latency=20.0, uptime=99.99, width=750.0)
    assert RadialGaugeDial is CircularCpuGaugeDial

    # Test verb
    action_cpu = hud.set_metric("CPU", 88.5)
    assert isinstance(action_cpu, AnimationAction)
    action_ram = hud.set_metric("RAM", 28.0)
    assert isinstance(action_ram, AnimationAction)
    action_lat = hud.set_metric("latency", 15.0)
    assert isinstance(action_lat, AnimationAction)

    bounds = hud.local_bounds()
    assert bounds == (0.0, 0.0, 750.0, 400.0)
    hud.draw(cairo_ctx, time=0.5)

    # Subcomponents
    dial = RadialGaugeDial(label="Test Gauge", value=75.0)
    dial.draw(cairo_ctx, time=0.0)
    ram_bar = RamMemoryMeterBar(used_gb=12.0, total_gb=32.0)
    ram_bar.draw(cairo_ctx, time=0.0)
    lat_line = NetworkPingLatencyLine(latency=30.0)
    lat_line.draw(cairo_ctx, time=0.0)
    uptime_badge = UptimePercentageBadge(uptime=99.95)
    uptime_badge.draw(cairo_ctx, time=0.0)


# 10. VisualSqlQueryBuilder Tests
def test_visual_sql_query_builder(cairo_ctx: cairo.Context):
    sql = VisualSqlQueryBuilder(width=780.0, height=480.0)
    assert SchemaTableNode is VisualSqlQueryBlock

    # Test verb
    action = sql.draw_join_relation("users", "orders")
    assert isinstance(action, AnimationAction)

    bounds = sql.local_bounds()
    assert bounds == (0.0, 0.0, 780.0, 480.0)
    sql.draw(cairo_ctx, time=0.5)

    # Subcomponents
    table_node = SchemaTableNode(table_name="products", columns=[("id", "BIGINT", True), ("price", "FLOAT", False)])
    table_node.draw(cairo_ctx, time=0.0)
    curve = TableJoinConnectorCurve(p1=(0.0, 0.0), p2=(100.0, 50.0))
    curve.draw(cairo_ctx, time=0.5)
    syntax_view = SqlSyntaxHighlightView(sql_text="SELECT * FROM products;")
    syntax_view.draw(cairo_ctx, time=0.0)
    exec_pill = ExecutionTimePill(time_ms=1.8)
    exec_pill.draw(cairo_ctx, time=0.0)


# 11. WebhookActivityFeed Tests
def test_webhook_activity_feed(cairo_ctx: cairo.Context):
    hook = WebhookActivityFeed(width=720.0, height=480.0)
    assert WebhookEventStreamCard is WebhookActivityFeed
    assert HttpRequestInspector is PayloadJsonInspector

    # Test verb
    action = hook.simulate_event("payment.succeeded", status_code=200)
    assert isinstance(action, AnimationAction)

    bounds = hook.local_bounds()
    assert bounds == (0.0, 0.0, 720.0, 480.0)
    hook.draw(cairo_ctx, time=0.5)

    # Subcomponents
    inspector = HttpRequestInspector(event_name="test.event", method="POST")
    inspector.draw(cairo_ctx, time=0.0)
    status_badge = HttpStatusBadge(status_code=404)
    status_badge.draw(cairo_ctx, time=0.0)
    retry_btn = RetryEventButton()
    retry_btn.draw(cairo_ctx, time=0.0)


# 12. TokenQuotaMeter Tests
def test_token_quota_meter(cairo_ctx: cairo.Context):
    meter = TokenQuotaMeter(total=1000000.0, used=500000.0, width=540.0, height=420.0)
    assert UsageRingGauge is CircularTokenQuotaRing

    # Test verb
    action = meter.consume(250000.0)
    assert isinstance(action, AnimationAction)

    bounds = meter.local_bounds()
    assert bounds == (0.0, 0.0, 540.0, 420.0)
    meter.draw(cairo_ctx, time=0.5)

    # Subcomponents
    ring = UsageRingGauge(used=800000.0, total=1000000.0)
    ring.draw(cairo_ctx, time=0.0)
    warn_banner = OverLimitWarningBanner(message="High usage warning")
    warn_banner.draw(cairo_ctx, time=0.0)
    thresh_pill = UsageThresholdPill(limit_str="Custom Plan")
    thresh_pill.draw(cairo_ctx, time=0.0)
    upgrade_btn = UpgradeCtaButton()
    upgrade_btn.draw(cairo_ctx, time=0.0)


# 13. CodeSandboxPlayground Tests
def test_code_sandbox_playground(cairo_ctx: cairo.Context):
    box = CodeSandboxPlayground(code="print('vibe')", width=840.0, height=500.0)
    assert SplitCodePlayground is CodeSandboxPlayground
    assert SplitConsoleOutput is InteractiveTerminalLogs

    # Test verb
    action = box.run_execution(output="Output executed.")
    assert isinstance(action, AnimationAction)

    bounds = box.local_bounds()
    assert bounds == (0.0, 0.0, 840.0, 500.0)
    box.draw(cairo_ctx, time=0.5)

    # Subcomponents
    console = SplitConsoleOutput(output_text="Log test line 1\nLog test line 2")
    console.draw(cairo_ctx, time=0.0)
    success_ind = RunCodeSuccessIndicator(exit_code=0, time_ms=18)
    success_ind.draw(cairo_ctx, time=0.0)
    dep_pill = DependencyInstallPill(package_str="pip: motio")
    dep_pill.draw(cairo_ctx, time=0.0)


# 14. FeatureComparisonMatrix Tests
def test_feature_comparison_matrix(cairo_ctx: cairo.Context):
    comp = FeatureComparisonMatrix(width=840.0, height=520.0)
    assert InteractiveFeatureMatrix is FeatureComparisonMatrix

    # Test verb
    actions = comp.reveal_rows()
    assert isinstance(actions, list)
    assert len(actions) > 0

    bounds = comp.local_bounds()
    assert bounds == (0.0, 0.0, 840.0, 520.0)
    comp.draw(cairo_ctx, time=0.5)

    # Subcomponents
    cell = CheckmarkCell(value=True, is_highlight=True)
    cell.draw(cairo_ctx, time=0.0)
    cell_false = CheckmarkCell(value=False)
    cell_false.draw(cairo_ctx, time=0.0)
    row = CompetitorComparisonRow(feature_name="Test Feat", values=[True, False, True])
    row.draw(cairo_ctx, time=0.0)
    tooltip = TooltipFeatureExplanation(text="Explanation text")
    tooltip.draw(cairo_ctx, time=0.0)
    header_col = StickyHeaderColumn()
    header_col.draw(cairo_ctx, time=0.0)


# 15. PromptDiffViewer Tests
def test_prompt_diff_viewer(cairo_ctx: cairo.Context):
    diff = PromptDiffViewer(v1="Version 1 text", v2="Version 2 improved text", width=840.0, height=480.0)
    assert PromptDiffCard is PromptDiffViewer

    # Test verb
    actions = diff.highlight_diffs()
    assert isinstance(actions, list)
    assert len(actions) == 3

    bounds = diff.local_bounds()
    assert bounds == (0.0, 0.0, 840.0, 480.0)
    diff.draw(cairo_ctx, time=0.5)

    # Subcomponents
    pane = SideBySideDiffPane(v1_text="Prompt A", v2_text="Prompt B")
    pane.draw(cairo_ctx, time=0.0)
    highlighter = InlineDiffHighlighter()
    highlighter.draw(cairo_ctx, time=0.0)
    badge = PromptTokenCostBadge(token_count=120, cost_usd=0.0024)
    badge.draw(cairo_ctx, time=0.0)
    merge_btn = MergePromptButton()
    merge_btn.draw(cairo_ctx, time=0.0)


# 16. Integration test: All 15 suites in Scene with @scene.animate
def test_all_15_suites_scene_animate_integration():
    scene = Scene(width=1920, height=1080, fps=60, duration=10.0)

    streamer = StreamingTokenOutput(text="Streaming tokens test")
    tot = TreeOfThoughtTree()
    canvas = DiffusionCanvas()
    chat = AgentTeamThread()
    vec = VectorEmbeddingsVisualizer(dimension=3)
    matrix = PricingTierMatrix()
    vault = ApiKeyVault()
    pr = GitPrTimeline(pr_number=88)
    hud = TelemetryDialHUD()
    sql = VisualSqlQueryBuilder()
    hook = WebhookActivityFeed()
    meter = TokenQuotaMeter(total=1000000)
    box = CodeSandboxPlayground(code="print('vibe')")
    comp = FeatureComparisonMatrix()
    diff = PromptDiffViewer(v1="v1", v2="v2")

    scene.add(streamer, tot, canvas, chat, vec, matrix, vault, pr, hud, sql, hook, meter, box, comp, diff)

    @scene.animate
    def main():
        yield streamer.stream_tokens(speed=30)
        yield tot.expand_branch(0)
        yield canvas.denoise_steps(steps=20)
        yield chat.post_agent_message("Coder", "Fixed.")
        yield vec.rotate_cluster()
        yield matrix.highlight_tier("Pro")
        yield vault.reveal_key(index=1)
        yield pr.animate_merge()
        yield hud.set_metric("CPU", 88.5)
        yield sql.draw_join_relation("users", "orders")
        yield hook.simulate_event("payment.succeeded")
        yield meter.consume(250000)
        yield box.run_execution()
        yield comp.reveal_rows()
        yield diff.highlight_diffs()

    frame = scene.render_frame(time=2.5)
    assert frame is not None
    assert frame.shape == (1080, 1920, 4)


def test_all_15_suites_verb_kwargs_syntax():
    """Verify all 15 high-level animation generator verbs accept AGENTS.md named keyword arguments."""
    streamer = StreamingTokenOutput(text="Streaming tokens test")
    tot = TreeOfThoughtTree()
    canvas = DiffusionCanvas()
    chat = AgentTeamThread()
    vec = VectorEmbeddingsVisualizer(dimension=3)
    matrix = PricingTierMatrix()
    vault = ApiKeyVault()
    pr = GitPrTimeline(pr_number=88)
    hud = TelemetryDialHUD()
    sql = VisualSqlQueryBuilder()
    hook = WebhookActivityFeed()
    meter = TokenQuotaMeter(total=1000000)
    box = CodeSandboxPlayground(code="print('vibe')")
    comp = FeatureComparisonMatrix()
    diff = PromptDiffViewer(v1="v1", v2="v2")

    # Call each verb with exact AGENTS.md catalog signature
    act1 = streamer.stream_tokens(speed=30)
    assert act1 is not None
    act2 = tot.expand_branch(0)
    assert act2 is not None
    act3 = canvas.denoise_steps(steps=20)
    assert act3 is not None
    act4 = chat.post_agent_message(agent="Coder", text="Fixed.")
    assert act4 is not None
    act5 = vec.rotate_cluster()
    assert act5 is not None
    act6 = matrix.highlight_tier("Pro")
    assert act6 is not None
    act7 = vault.reveal_key(index=1)
    assert act7 is not None
    act8 = pr.animate_merge()
    assert act8 is not None
    act9 = hud.set_metric("CPU", 88.5)
    assert act9 is not None
    act10 = sql.draw_join_relation("users", "orders")
    assert act10 is not None
    act11 = hook.simulate_event("payment.succeeded")
    assert act11 is not None
    act12 = meter.consume(250000)
    assert act12 is not None
    act13 = box.run_execution()
    assert act13 is not None
    act14 = comp.reveal_rows()
    assert act14 is not None
    act15 = diff.highlight_diffs()
    assert act15 is not None
