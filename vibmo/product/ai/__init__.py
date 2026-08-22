"""AI & SaaS Interactive UI Component Suites."""
from __future__ import annotations

from vibmo.product.ai.ui_agent_team_thread_suite import (
    AgentStatusPill,
    AgentTypingWave,
    ToolCallingPayloadCard,
    AgentConversationBubble,
)
from vibmo.product.ai.ui_api_key_vault_suite import (
    MaskedTokenRevealField,
    CopyClipboardPill,
    ApiKeyVaultCard,
    RevokeConfirmModal,
)
from vibmo.product.ai.ui_code_sandbox_suite import (
    SplitCodePlayground,
    InteractiveTerminalLogs,
    RunCodeSuccessIndicator,
    DependencyInstallPill,
)
from vibmo.product.ai.ui_diffusion_canvas_suite import (
    DiffusionGenerationCanvas,
    PromptAspectSelector,
    SeedVariationPills,
    MagicPromptEnhanceBar,
)
from vibmo.product.ai.ui_embeddings_space_suite import (
    EmbeddingScatterCluster,
    CosineSimilarityLink,
    VectorDimensionBar,
    SearchQueryProbe,
)
from vibmo.product.ai.ui_git_pr_timeline_suite import (
    GitPullRequestCard,
    CommitShaBadge,
    CiCdCheckStatusPill,
    MergeSquashButton,
)
from vibmo.product.ai.ui_matrix_comparison_suite import (
    InteractiveFeatureMatrix,
    CompetitorComparisonRow,
    TooltipFeatureExplanation,
    StickyHeaderColumn,
)
from vibmo.product.ai.ui_pricing_matrix_suite import (
    FeatureChecklistRow,
    AnnualBillingToggle,
    PopularGlowBadge,
    PricingTierGrid,
)
from vibmo.product.ai.ui_prompt_diff_suite import (
    PromptDiffCard,
    InlineDiffHighlighter,
    PromptTokenCostBadge,
    MergePromptButton,
)
from vibmo.product.ai.ui_quota_meter_suite import (
    CircularTokenQuotaRing,
    OverLimitWarningBanner,
    UsageThresholdPill,
    UpgradeCtaButton,
)
from vibmo.product.ai.ui_sql_query_builder_suite import (
    VisualSqlQueryBlock,
    TableJoinConnectorCurve,
    SqlSyntaxHighlightView,
    ExecutionTimePill,
)
from vibmo.product.ai.ui_telemetry_dial_suite import (
    CircularCpuGaugeDial,
    RamMemoryMeterBar,
    NetworkPingLatencyLine,
    UptimePercentageBadge,
)
from vibmo.product.ai.ui_token_streamer_suite import (
    ShimmeringCaretIndicator,
    TokenSpeedVelocityCounter,
    StopGenerationButton,
    TokenStreamerBox,
)
from vibmo.product.ai.ui_tree_of_thought_suite import (
    ExplorationScoreBadge,
    ReasoningNodeBranch,
    PrunedBranchFade,
    TreeOfThoughtTree,
)
from vibmo.product.ai.ui_webhook_feed_suite import (
    WebhookEventStreamCard,
    HttpStatusBadge,
    PayloadJsonInspector,
    RetryEventButton,
)

__all__ = [
    "AgentStatusPill",
    "AgentTypingWave",
    "ToolCallingPayloadCard",
    "AgentConversationBubble",
    "MaskedTokenRevealField",
    "CopyClipboardPill",
    "ApiKeyVaultCard",
    "RevokeConfirmModal",
    "SplitCodePlayground",
    "InteractiveTerminalLogs",
    "RunCodeSuccessIndicator",
    "DependencyInstallPill",
    "DiffusionGenerationCanvas",
    "PromptAspectSelector",
    "SeedVariationPills",
    "MagicPromptEnhanceBar",
    "EmbeddingScatterCluster",
    "CosineSimilarityLink",
    "VectorDimensionBar",
    "SearchQueryProbe",
    "GitPullRequestCard",
    "CommitShaBadge",
    "CiCdCheckStatusPill",
    "MergeSquashButton",
    "InteractiveFeatureMatrix",
    "CompetitorComparisonRow",
    "TooltipFeatureExplanation",
    "StickyHeaderColumn",
    "FeatureChecklistRow",
    "AnnualBillingToggle",
    "PopularGlowBadge",
    "PricingTierGrid",
    "PromptDiffCard",
    "InlineDiffHighlighter",
    "PromptTokenCostBadge",
    "MergePromptButton",
    "CircularTokenQuotaRing",
    "OverLimitWarningBanner",
    "UsageThresholdPill",
    "UpgradeCtaButton",
    "VisualSqlQueryBlock",
    "TableJoinConnectorCurve",
    "SqlSyntaxHighlightView",
    "ExecutionTimePill",
    "CircularCpuGaugeDial",
    "RamMemoryMeterBar",
    "NetworkPingLatencyLine",
    "UptimePercentageBadge",
    "ShimmeringCaretIndicator",
    "TokenSpeedVelocityCounter",
    "StopGenerationButton",
    "TokenStreamerBox",
    "ExplorationScoreBadge",
    "ReasoningNodeBranch",
    "PrunedBranchFade",
    "TreeOfThoughtTree",
    "WebhookEventStreamCard",
    "HttpStatusBadge",
    "PayloadJsonInspector",
    "RetryEventButton",
]

# Semantic Aliases
StreamingTokenOutput = TokenStreamerBox
DiffusionCanvas = DiffusionGenerationCanvas
VectorEmbeddingsVisualizer = EmbeddingScatterCluster
PricingTierMatrix = PricingTierGrid
ApiKeyVault = ApiKeyVaultCard
GitPrTimeline = GitPullRequestCard
TokenQuotaMeter = CircularTokenQuotaRing
CodeSandboxPlayground = SplitCodePlayground
FeatureComparisonMatrix = InteractiveFeatureMatrix
PromptDiffViewer = PromptDiffCard
WebhookActivityFeed = WebhookEventStreamCard

__all__.extend([
    "StreamingTokenOutput",
    "DiffusionCanvas",
    "VectorEmbeddingsVisualizer",
    "PricingTierMatrix",
    "ApiKeyVault",
    "GitPrTimeline",
    "TokenQuotaMeter",
    "CodeSandboxPlayground",
    "FeatureComparisonMatrix",
    "PromptDiffViewer",
    "WebhookActivityFeed",
])

