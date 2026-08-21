"""
MCP Resources and Prompt Templates for Vibmo.
"""

from __future__ import annotations
import os
from typing import Any, Dict, List


def get_mcp_resources() -> List[Dict[str, Any]]:
    """Returns available MCP resources."""
    return [
        {
            "uri": "vibmo://docs/agents-guide",
            "name": "Vibmo AI Agent Motion Graphics Guide",
            "description": "5 Principles and rules for AI agents coding high-converting motion graphics.",
            "mimeType": "text/markdown",
        },
        {
            "uri": "vibmo://components/catalog",
            "name": "Semantic Components Catalog",
            "description": "JSON inventory of all design primitives, charts, tables, cards, and motion verbs.",
            "mimeType": "application/json",
        },
    ]


def read_mcp_resource(uri: str) -> Dict[str, Any]:
    """Reads content for a specific MCP resource URI."""
    if uri == "vibmo://docs/agents-guide":
        guide_path = os.path.join(os.path.dirname(__file__), "..", "..", "AGENTS.md")
        content = ""
        if os.path.exists(guide_path):
            with open(guide_path, "r", encoding="utf-8") as f:
                content = f.read()
        return {
            "uri": uri,
            "mimeType": "text/markdown",
            "text": content,
        }
    elif uri == "vibmo://components/catalog":
        from vibmo.mcp.tools import tool_list_components
        import json
        return {
            "uri": uri,
            "mimeType": "application/json",
            "text": json.dumps(tool_list_components(), indent=2),
        }
    raise ValueError(f"Unknown resource URI: {uri}")


def get_mcp_prompts() -> List[Dict[str, Any]]:
    """Returns preset MCP prompt templates for AI motion graphic workflows."""
    return [
        {
            "name": "create-saas-launch-video",
            "description": "Generates a high-converting dark-aesthetic SaaS launch motion graphic video.",
            "arguments": [
                {"name": "product_name", "description": "Name of the software or AI product", "required": True},
                {"name": "mrr_value", "description": "Monthly Recurring Revenue to ticker animate (e.g. $148,000)", "required": False},
                {"name": "headline", "description": "Hero value proposition headline", "required": False},
            ],
        },
        {
            "name": "create-kpi-dashboard",
            "description": "Creates a multi-card metrics dashboard with bar charts, sparklines, and status tables.",
            "arguments": [
                {"name": "title", "description": "Dashboard title", "required": True},
                {"name": "primary_metric", "description": "Main KPI metric and value", "required": True},
            ],
        },
    ]
