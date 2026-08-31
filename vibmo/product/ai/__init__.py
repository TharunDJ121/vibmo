"""AI & SaaS Interactive UI Component Suites for Vibmo / Motio."""
from __future__ import annotations

# Suite 1: Streaming LLM Token
from vibmo.product.ai.ui_token_streamer_suite import (
    StreamingTokenOutput,
    TokenStreamerSuite,
    TokenStreamerBox,
    ShimmeringCaretIndicator,
    TokenSpeedVelocityCounter,
    StopGenerationButton,
)

# Suite 2: Tree-of-Thought AI
from vibmo.product.ai.ui_tree_of_thought_suite import (
    TreeOfThoughtTree,
    ReasoningBranchNode,
    ReasoningNodeBranch,
    ExplorationScoreBadge,
    PrunedBranchFade,
)

# Suite 3: Diffusion Canvas
from vibmo.product.ai.ui_diffusion_canvas_suite import (
    DiffusionCanvas,
    DiffusionGenerationCanvas,
    DenoisingProgress,
    PromptAspectSelector,
    SeedVariationPills,
    MagicPromptEnhanceBar,
)

# Suite 4: Multi-Agent Chat
from vibmo.product.ai.ui_agent_team_thread_suite import (
    AgentTeamThread,
    AgentMessageBubble,
    AgentConversationBubble,
    AgentStatusPill,
    AgentTypingWave,
    ToolCallingPayloadCard,
)

# Suite 5: Vector Embeddings
from vibmo.product.ai.ui_embeddings_space_suite import (
    VectorEmbeddingsVisualizer,
    ClusterPoint,
    EmbeddingScatterCluster,
    CosineSimilarityLink,
    VectorDimensionBar,
    SearchQueryProbe,
)

# Suite 6: SaaS Pricing Matrix
from vibmo.product.ai.ui_pricing_matrix_suite import (
    PricingTierMatrix,
    PricingTierGrid,
    PricingTierColumn,
    FeatureChecklistRow,
    AnnualBillingToggle,
    PopularGlowBadge,
)

# Suite 7: API Key Vault
from vibmo.product.ai.ui_api_key_vault_suite import (
    ApiKeyVault,
    ApiKeyVaultCard,
    KeySecretRow,
    MaskedTokenRevealField,
    CopyClipboardPill,
    RevokeConfirmModal,
)

# Suite 8: GitHub PR Timeline
from vibmo.product.ai.ui_git_pr_timeline_suite import (
    GitPrTimeline,
    MergeStatusPill,
    GitPullRequestCard,
    CommitShaBadge,
    CiCdCheckStatusPill,
    MergeSquashButton,
)

# Suite 9: Telemetry HUD
from vibmo.product.ai.ui_telemetry_dial_suite import (
    TelemetryDialHUD,
    RadialGaugeDial,
    CircularCpuGaugeDial,
    RamMemoryMeterBar,
    NetworkPingLatencyLine,
    UptimePercentageBadge,
)

# Suite 10: Visual SQL Builder
from vibmo.product.ai.ui_sql_query_builder_suite import (
    VisualSqlQueryBuilder,
    SchemaTableNode,
    VisualSqlQueryBlock,
    TableJoinConnectorCurve,
    SqlSyntaxHighlightView,
    ExecutionTimePill,
)

# Suite 11: Webhook Live Feed
from vibmo.product.ai.ui_webhook_feed_suite import (
    WebhookActivityFeed,
    WebhookEventStreamCard,
    HttpRequestInspector,
    PayloadJsonInspector,
    HttpStatusBadge,
    RetryEventButton,
)

# Suite 12: Token Quota Ring
from vibmo.product.ai.ui_quota_meter_suite import (
    TokenQuotaMeter,
    UsageRingGauge,
    CircularTokenQuotaRing,
    OverLimitWarningBanner,
    UsageThresholdPill,
    UpgradeCtaButton,
)

# Suite 13: Code Sandbox
from vibmo.product.ai.ui_code_sandbox_suite import (
    CodeSandboxPlayground,
    SplitCodePlayground,
    SplitConsoleOutput,
    InteractiveTerminalLogs,
    RunCodeSuccessIndicator,
    DependencyInstallPill,
)

# Suite 14: Feature Comparison
from vibmo.product.ai.ui_matrix_comparison_suite import (
    FeatureComparisonMatrix,
    InteractiveFeatureMatrix,
    CheckmarkCell,
    CompetitorComparisonRow,
    TooltipFeatureExplanation,
    StickyHeaderColumn,
)

# Suite 15: Prompt Diff Suite
from vibmo.product.ai.ui_prompt_diff_suite import (
    PromptDiffViewer,
    PromptDiffCard,
    SideBySideDiffPane,
    InlineDiffHighlighter,
    PromptTokenCostBadge,
    MergePromptButton,
)

__all__ = [
    # 1. Streaming LLM Token
    "StreamingTokenOutput",
    "TokenStreamerSuite",
    "TokenStreamerBox",
    "ShimmeringCaretIndicator",
    "TokenSpeedVelocityCounter",
    "StopGenerationButton",
    # 2. Tree-of-Thought AI
    "TreeOfThoughtTree",
    "ReasoningBranchNode",
    "ReasoningNodeBranch",
    "ExplorationScoreBadge",
    "PrunedBranchFade",
    # 3. Diffusion Canvas
    "DiffusionCanvas",
    "DiffusionGenerationCanvas",
    "DenoisingProgress",
    "PromptAspectSelector",
    "SeedVariationPills",
    "MagicPromptEnhanceBar",
    # 4. Multi-Agent Chat
    "AgentTeamThread",
    "AgentMessageBubble",
    "AgentConversationBubble",
    "AgentStatusPill",
    "AgentTypingWave",
    "ToolCallingPayloadCard",
    # 5. Vector Embeddings
    "VectorEmbeddingsVisualizer",
    "ClusterPoint",
    "EmbeddingScatterCluster",
    "CosineSimilarityLink",
    "VectorDimensionBar",
    "SearchQueryProbe",
    # 6. SaaS Pricing Matrix
    "PricingTierMatrix",
    "PricingTierGrid",
    "PricingTierColumn",
    "FeatureChecklistRow",
    "AnnualBillingToggle",
    "PopularGlowBadge",
    # 7. API Key Vault
    "ApiKeyVault",
    "ApiKeyVaultCard",
    "KeySecretRow",
    "MaskedTokenRevealField",
    "CopyClipboardPill",
    "RevokeConfirmModal",
    # 8. GitHub PR Timeline
    "GitPrTimeline",
    "MergeStatusPill",
    "GitPullRequestCard",
    "CommitShaBadge",
    "CiCdCheckStatusPill",
    "MergeSquashButton",
    # 9. Telemetry HUD
    "TelemetryDialHUD",
    "RadialGaugeDial",
    "CircularCpuGaugeDial",
    "RamMemoryMeterBar",
    "NetworkPingLatencyLine",
    "UptimePercentageBadge",
    # 10. Visual SQL Builder
    "VisualSqlQueryBuilder",
    "SchemaTableNode",
    "VisualSqlQueryBlock",
    "TableJoinConnectorCurve",
    "SqlSyntaxHighlightView",
    "ExecutionTimePill",
    # 11. Webhook Live Feed
    "WebhookActivityFeed",
    "WebhookEventStreamCard",
    "HttpRequestInspector",
    "PayloadJsonInspector",
    "HttpStatusBadge",
    "RetryEventButton",
    # 12. Token Quota Ring
    "TokenQuotaMeter",
    "UsageRingGauge",
    "CircularTokenQuotaRing",
    "OverLimitWarningBanner",
    "UsageThresholdPill",
    "UpgradeCtaButton",
    # 13. Code Sandbox
    "CodeSandboxPlayground",
    "SplitCodePlayground",
    "SplitConsoleOutput",
    "InteractiveTerminalLogs",
    "RunCodeSuccessIndicator",
    "DependencyInstallPill",
    # 14. Feature Comparison
    "FeatureComparisonMatrix",
    "InteractiveFeatureMatrix",
    "CheckmarkCell",
    "CompetitorComparisonRow",
    "TooltipFeatureExplanation",
    "StickyHeaderColumn",
    # 15. Prompt Diff Suite
    "PromptDiffViewer",
    "PromptDiffCard",
    "SideBySideDiffPane",
    "InlineDiffHighlighter",
    "PromptTokenCostBadge",
    "MergePromptButton",
    # 16. AI Prompt Flow & Model Composer
    "AiPromptFlow",
    "ModelSelectorPill",
    # 17. Claude Code & Terminal Simulator
    "ClaudeCodeSimulator",
    "TerminalCursorZoom",
    # 18. Interactive Checkout Flow
    "InteractiveCheckoutFlow",
    "PaymentCreditCardField",
    # 19. Social Follow & GitHub Stars Cards
    "XFollowCard",
    "GitHubStarsCard",
    # 20. Infinite Bento Pan Grid
    "InfiniteBentoPan",
    "BentoGridCard",
]
from vibmo.product.ai.ui_ai_prompt_flow_suite import (
    AiPromptFlow,
    ModelSelectorPill,
)
from vibmo.product.ai.ui_claude_code_sim_suite import (
    ClaudeCodeSimulator,
    TerminalCursorZoom,
)
from vibmo.product.ai.ui_checkout_flow_suite import (
    InteractiveCheckoutFlow,
    PaymentCreditCardField,
)
from vibmo.product.ai.ui_social_follow_card_suite import (
    XFollowCard,
    GitHubStarsCard,
)
from vibmo.product.ai.ui_infinite_bento_pan_suite import (
    InfiniteBentoPan,
    BentoGridCard,
)
