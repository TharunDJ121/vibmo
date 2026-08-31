"""
Tier 1 E2E Tests: AI & SaaS Interactive UI Suites (Section 4).
Covers all 15 AI and developer UI components with >=5 tests per feature.
"""

import pytest
import cairo
from .conftest import assert_cairo_draw_safe

from vibmo.scene.scene import Scene
from vibmo.core.color import Color, colors

from vibmo.product.ai.ui_token_streamer_suite import StreamingTokenOutput, TokenStreamerBox
from vibmo.product.ai.ui_tree_of_thought_suite import TreeOfThoughtTree, ReasoningNodeBranch
from vibmo.product.ai.ui_diffusion_canvas_suite import DiffusionCanvas, DiffusionGenerationCanvas
from vibmo.product.ai.ui_agent_team_thread_suite import AgentConversationBubble
from vibmo.product.ai.ui_embeddings_space_suite import VectorEmbeddingsVisualizer, EmbeddingScatterCluster
from vibmo.product.ai.ui_pricing_matrix_suite import PricingTierMatrix, PricingTierGrid
from vibmo.product.ai.ui_api_key_vault_suite import ApiKeyVault, ApiKeyVaultCard
from vibmo.product.ai.ui_git_pr_timeline_suite import GitPrTimeline, GitPullRequestCard
from vibmo.product.ai.ui_telemetry_dial_suite import TelemetryDialHUD, CircularCpuGaugeDial
from vibmo.product.ai.ui_sql_query_builder_suite import VisualSqlQueryBlock
from vibmo.product.ai.ui_webhook_feed_suite import WebhookActivityFeed, WebhookEventStreamCard
from vibmo.product.ai.ui_quota_meter_suite import TokenQuotaMeter, CircularTokenQuotaRing
from vibmo.product.ai.ui_code_sandbox_suite import CodeSandboxPlayground, SplitCodePlayground
from vibmo.product.ai.ui_matrix_comparison_suite import FeatureComparisonMatrix, InteractiveFeatureMatrix
from vibmo.product.ai.ui_prompt_diff_suite import PromptDiffViewer, PromptDiffCard


# ============================================================================
# 1. Streaming Token Output Suite (>=5 tests)
# ============================================================================

def test_token_streamer_defaults():
    streamer = StreamingTokenOutput(text="Analyzing model weights and token probabilities...")
    assert_cairo_draw_safe(streamer)


def test_token_streamer_empty_and_short_text():
    s_empty = StreamingTokenOutput(text="")
    s_short = StreamingTokenOutput(text="OK")
    assert_cairo_draw_safe(s_empty)
    assert_cairo_draw_safe(s_short)


def test_token_streamer_speed_and_cursor():
    streamer = StreamingTokenOutput(text="Generating response...", speed=40.0, show_cursor=True)
    assert_cairo_draw_safe(streamer)


def test_token_streamer_custom_colors():
    streamer = StreamingTokenOutput(
        text="Cost per token: $0.00002",
        text_color=colors.EMERALD,
        bg_color=colors.SLATE_900
    )
    assert_cairo_draw_safe(streamer)


def test_token_streamer_stream_tokens_action():
    streamer = StreamingTokenOutput(text="Choreographed token stream")
    action = streamer.stream_tokens(duration=2.0)
    assert action is not None
    assert_cairo_draw_safe(streamer, timestamps=(0.0, 1.0, 2.0))


# ============================================================================
# 2. Tree-of-Thought AI Suite (>=5 tests)
# ============================================================================

def test_tree_of_thought_defaults():
    tot = TreeOfThoughtTree()
    assert_cairo_draw_safe(tot)


def test_tree_of_thought_expand_branch():
    tot = TreeOfThoughtTree()
    action = tot.expand_branch(0)
    assert action is not None
    assert_cairo_draw_safe(tot)


def test_tree_of_thought_custom_nodes():
    tot = TreeOfThoughtTree(root_text="Initial Prompt Evaluation")
    assert_cairo_draw_safe(tot)


def test_tree_of_thought_branch_node_colors():
    node = ReasoningNodeBranch(text="Exploring Branch A", score=0.92, status="optimal")
    assert_cairo_draw_safe(node)


def test_tree_of_thought_multi_step_evolution():
    tot = TreeOfThoughtTree()
    assert_cairo_draw_safe(tot, timestamps=(0.0, 0.5, 1.5, 3.0))


# ============================================================================
# 3. Diffusion Canvas Suite (>=5 tests)
# ============================================================================

def test_diffusion_canvas_defaults():
    canvas = DiffusionCanvas()
    assert_cairo_draw_safe(canvas)


def test_diffusion_canvas_denoise_steps():
    canvas = DiffusionCanvas()
    action = canvas.denoise_steps(steps=20, duration=1.5)
    assert action is not None
    assert_cairo_draw_safe(canvas)


def test_diffusion_canvas_aspect_ratios():
    c_square = DiffusionCanvas(width=512, height=512)
    c_wide = DiffusionCanvas(width=768, height=512)
    assert_cairo_draw_safe(c_square)
    assert_cairo_draw_safe(c_wide)


def test_diffusion_canvas_prompts_overlay():
    canvas = DiffusionCanvas(prompt="A futuristic neon cyber city in 8k")
    assert_cairo_draw_safe(canvas)


def test_diffusion_generation_canvas_alias():
    canvas = DiffusionGenerationCanvas()
    assert_cairo_draw_safe(canvas)


# ============================================================================
# 4. Multi-Agent Chat Thread Suite (>=5 tests)
# ============================================================================

def test_agent_chat_bubble_defaults():
    bubble = AgentConversationBubble(agent_name="CoderAgent", message="Refactored shader pipeline.")
    assert_cairo_draw_safe(bubble)


def test_agent_chat_bubble_avatar_and_roles():
    bubble_pm = AgentConversationBubble(agent_name="Product Lead", message="Release scheduled for 2 PM.")
    bubble_qa = AgentConversationBubble(agent_name="QA Auditor", message="All tests passing.")
    assert_cairo_draw_safe(bubble_pm)
    assert_cairo_draw_safe(bubble_qa)


def test_agent_chat_bubble_colors():
    bubble = AgentConversationBubble(
        agent_name="SecurityAgent",
        message="Vulnerability scan complete: 0 issues.",
        accent_color=colors.EMERALD
    )
    assert_cairo_draw_safe(bubble)


def test_agent_chat_bubble_long_text():
    long_msg = "Detailed analysis: The pipeline executes asynchronously across multiple Cairo contexts without memory leaks."
    bubble = AgentConversationBubble(agent_name="Architect", message=long_msg)
    assert_cairo_draw_safe(bubble)


def test_agent_chat_bubble_timestamps():
    bubble = AgentConversationBubble(agent_name="DevOps", message="Deployment green.")
    assert_cairo_draw_safe(bubble, timestamps=(0.0, 1.0, 2.0))


# ============================================================================
# 5. Vector Embeddings Visualizer Suite (>=5 tests)
# ============================================================================

def test_vector_embeddings_defaults():
    vec = VectorEmbeddingsVisualizer()
    assert_cairo_draw_safe(vec)


def test_vector_embeddings_rotate_cluster():
    vec = VectorEmbeddingsVisualizer()
    action = vec.rotate_cluster(duration=2.0)
    assert action is not None
    assert_cairo_draw_safe(vec)


def test_vector_embeddings_cluster_count():
    vec_small = VectorEmbeddingsVisualizer(num_points=30)
    vec_large = VectorEmbeddingsVisualizer(num_points=120)
    assert_cairo_draw_safe(vec_small)
    assert_cairo_draw_safe(vec_large)


def test_vector_embeddings_scatter_cluster_alias():
    cluster = EmbeddingScatterCluster()
    assert_cairo_draw_safe(cluster)


def test_vector_embeddings_multi_time_render():
    vec = VectorEmbeddingsVisualizer()
    for t in [0.0, 0.75, 1.5, 3.0]:
        assert_cairo_draw_safe(vec, timestamps=(t,))


# ============================================================================
# 6. SaaS Pricing Matrix Suite (>=5 tests)
# ============================================================================

def test_pricing_matrix_defaults():
    matrix = PricingTierMatrix()
    assert_cairo_draw_safe(matrix)


def test_pricing_matrix_highlight_tier():
    matrix = PricingTierMatrix()
    action = matrix.highlight_tier("Pro")
    assert action is not None
    assert_cairo_draw_safe(matrix)


def test_pricing_matrix_custom_tiers():
    tiers = [
        {"name": "Starter", "price": "$0/mo", "features": ["1 User", "Basic SFX"]},
        {"name": "Pro", "price": "$49/mo", "features": ["10 Users", "All 100+ Suites"]},
    ]
    matrix = PricingTierMatrix(tiers=tiers)
    assert_cairo_draw_safe(matrix)


def test_pricing_matrix_grid_alias():
    grid = PricingTierGrid()
    assert_cairo_draw_safe(grid)


def test_pricing_matrix_aspect_scaling():
    matrix = PricingTierMatrix(width=1400, height=700)
    assert_cairo_draw_safe(matrix)


# ============================================================================
# 7. API Key Vault Suite (>=5 tests)
# ============================================================================

def test_api_key_vault_defaults():
    vault = ApiKeyVault()
    assert_cairo_draw_safe(vault)


def test_api_key_vault_reveal_key():
    vault = ApiKeyVault()
    action = vault.reveal_key(index=0)
    assert action is not None
    assert_cairo_draw_safe(vault)


def test_api_key_vault_custom_keys():
    keys = ["sk-live-motio-989218491", "sk-test-vibmo-818291039"]
    vault = ApiKeyVault(keys=keys)
    assert_cairo_draw_safe(vault)


def test_api_key_vault_card_alias():
    card = ApiKeyVaultCard()
    assert_cairo_draw_safe(card)


def test_api_key_vault_toggle_obscurity():
    vault = ApiKeyVault()
    assert_cairo_draw_safe(vault, timestamps=(0.0, 1.0, 2.0))


# ============================================================================
# 8. GitHub PR Timeline Suite (>=5 tests)
# ============================================================================

def test_git_pr_timeline_defaults():
    pr = GitPrTimeline()
    assert_cairo_draw_safe(pr)


def test_git_pr_timeline_animate_merge():
    pr = GitPrTimeline()
    action = pr.animate_merge()
    assert action is not None
    assert_cairo_draw_safe(pr)


def test_git_pr_timeline_custom_pr_info():
    pr = GitPrTimeline(pr_number=102, title="Feat: 100+ Asset Expansion in Motio", author="AntigravityAgent")
    assert_cairo_draw_safe(pr)


def test_git_pr_card_alias():
    card = GitPullRequestCard()
    assert_cairo_draw_safe(card)


def test_git_pr_timeline_checks_status():
    pr_green = GitPrTimeline(checks_passing=True)
    pr_pending = GitPrTimeline(checks_passing=False)
    assert_cairo_draw_safe(pr_green)
    assert_cairo_draw_safe(pr_pending)


# ============================================================================
# 9. Telemetry Dial HUD Suite (>=5 tests)
# ============================================================================

def test_telemetry_dial_defaults():
    hud = TelemetryDialHUD()
    assert_cairo_draw_safe(hud)


def test_telemetry_dial_set_metric():
    hud = TelemetryDialHUD()
    action = hud.set_metric("CPU", 88.5)
    assert action is not None
    assert_cairo_draw_safe(hud)


def test_telemetry_dial_custom_gauges():
    hud = TelemetryDialHUD(metrics={"GPU": 92.0, "VRAM": 64.0, "FPS": 60.0})
    assert_cairo_draw_safe(hud)


def test_circular_cpu_gauge_alias():
    dial = CircularCpuGaugeDial()
    assert_cairo_draw_safe(dial)


def test_telemetry_dial_dial_range():
    hud = TelemetryDialHUD()
    for t in [0.0, 0.5, 1.5, 3.0]:
        assert_cairo_draw_safe(hud, timestamps=(t,))


# ============================================================================
# 10. Visual SQL Query Builder Suite (>=5 tests)
# ============================================================================

def test_visual_sql_builder_defaults():
    sql = VisualSqlQueryBlock()
    assert_cairo_draw_safe(sql)


def test_visual_sql_builder_join_relation():
    sql = VisualSqlQueryBlock()
    action = sql.draw_join_relation("users.id", "orders.user_id")
    assert action is not None
    assert_cairo_draw_safe(sql)


def test_visual_sql_builder_custom_tables():
    sql = VisualSqlQueryBlock(tables=["users", "orders", "invoices"])
    assert_cairo_draw_safe(sql)


def test_visual_sql_builder_dimensions():
    sql = VisualSqlQueryBlock(width=1000, height=600)
    assert_cairo_draw_safe(sql)


def test_visual_sql_builder_query_syntax():
    sql = VisualSqlQueryBlock(query="SELECT u.name, SUM(o.amount) FROM users u JOIN orders o ON u.id = o.user_id")
    assert_cairo_draw_safe(sql)


# ============================================================================
# 11. Webhook Activity Feed Suite (>=5 tests)
# ============================================================================

def test_webhook_activity_feed_defaults():
    hook = WebhookActivityFeed()
    assert_cairo_draw_safe(hook)


def test_webhook_activity_feed_simulate_event():
    hook = WebhookActivityFeed()
    action = hook.simulate_event("payment_intent.succeeded")
    assert action is not None
    assert_cairo_draw_safe(hook)


def test_webhook_activity_feed_custom_endpoints():
    hook = WebhookActivityFeed(endpoint="https://api.vibmo.dev/v1/webhooks")
    assert_cairo_draw_safe(hook)


def test_webhook_event_stream_card_alias():
    card = WebhookEventStreamCard()
    assert_cairo_draw_safe(card)


def test_webhook_activity_feed_multi_events():
    hook = WebhookActivityFeed()
    assert_cairo_draw_safe(hook, timestamps=(0.0, 1.0, 2.0, 3.0))


# ============================================================================
# 12. Token Quota Meter Suite (>=5 tests)
# ============================================================================

def test_token_quota_meter_defaults():
    meter = TokenQuotaMeter()
    assert_cairo_draw_safe(meter)


def test_token_quota_meter_consume():
    meter = TokenQuotaMeter(total=1000000)
    action = meter.consume(250000)
    assert action is not None
    assert_cairo_draw_safe(meter)


def test_token_quota_meter_percentages():
    meter_low = TokenQuotaMeter(used=10000, total=100000)
    meter_full = TokenQuotaMeter(used=99000, total=100000)
    assert_cairo_draw_safe(meter_low)
    assert_cairo_draw_safe(meter_full)


def test_circular_token_quota_ring_alias():
    ring = CircularTokenQuotaRing()
    assert_cairo_draw_safe(ring)


def test_token_quota_meter_glow_and_colors():
    meter = TokenQuotaMeter(glow_color=colors.CYAN)
    assert_cairo_draw_safe(meter)


# ============================================================================
# 13. Code Sandbox Playground Suite (>=5 tests)
# ============================================================================

def test_code_sandbox_defaults():
    box = CodeSandboxPlayground()
    assert_cairo_draw_safe(box)


def test_code_sandbox_run_execution():
    box = CodeSandboxPlayground(code="from motio.agent_api import *\nscene = Scene()")
    action = box.run_execution()
    assert action is not None
    assert_cairo_draw_safe(box)


def test_code_sandbox_split_console_alias():
    box = SplitCodePlayground()
    assert_cairo_draw_safe(box)


def test_code_sandbox_terminal_logs():
    box = CodeSandboxPlayground(console_output="[Vibmo Studio] Rendered 300 frames in 0.82s.")
    assert_cairo_draw_safe(box)


def test_code_sandbox_custom_theme():
    box = CodeSandboxPlayground(theme="dark_slate")
    assert_cairo_draw_safe(box)


# ============================================================================
# 14. Feature Comparison Matrix Suite (>=5 tests)
# ============================================================================

def test_feature_comparison_defaults():
    comp = FeatureComparisonMatrix()
    assert_cairo_draw_safe(comp)


def test_feature_comparison_reveal_rows():
    comp = FeatureComparisonMatrix()
    action = comp.reveal_rows()
    assert action is not None
    assert_cairo_draw_safe(comp)


def test_feature_comparison_interactive_alias():
    comp = InteractiveFeatureMatrix()
    assert_cairo_draw_safe(comp)


def test_feature_comparison_custom_features():
    features = [
        {"feature": "60 FPS Render", "free": False, "pro": True},
        {"feature": "Single-Line God Import", "free": True, "pro": True},
    ]
    comp = FeatureComparisonMatrix(features=features)
    assert_cairo_draw_safe(comp)


def test_feature_comparison_scaling():
    comp = FeatureComparisonMatrix(width=1200, height=600)
    assert_cairo_draw_safe(comp)


# ============================================================================
# 15. Prompt Diff Viewer Suite (>=5 tests)
# ============================================================================

def test_prompt_diff_viewer_defaults():
    diff = PromptDiffViewer(v1="Initial draft prompt for SaaS video", v2="Refined prompt with GlassCard and MetricCounter")
    assert_cairo_draw_safe(diff)


def test_prompt_diff_viewer_highlight_diffs():
    diff = PromptDiffViewer(v1="Version 1.0", v2="Version 2.0 with Spring overshoot")
    action = diff.highlight_diffs()
    assert action is not None
    assert_cairo_draw_safe(diff)


def test_prompt_diff_card_alias():
    card = PromptDiffCard()
    assert_cairo_draw_safe(card)


def test_prompt_diff_viewer_identical_text():
    diff = PromptDiffViewer(v1="Identical Prompt", v2="Identical Prompt")
    assert_cairo_draw_safe(diff)


def test_prompt_diff_viewer_custom_colors():
    diff = PromptDiffViewer(
        v1="Removed feature",
        v2="Added feature",
        add_color=colors.EMERALD,
        remove_color=colors.ROSE
    )
    assert_cairo_draw_safe(diff)
