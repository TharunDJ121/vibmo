"""
MCP Resources and Prompt Templates for Vibmo.
"""

from __future__ import annotations
import os
import json
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
        {
            "uri": "vibmo://docs/verbs",
            "name": "Motion Verbs Quick Reference",
            "description": "Catalog of all fluent animation verbs (pop_in, reveal_characters, count_to, float_idle, etc.).",
            "mimeType": "application/json",
        },
        {
            "uri": "vibmo://docs/colors",
            "name": "Aesthetic Color Palette",
            "description": "Curated palette tokens for dark/light themes (DARK_NAVY, CYAN, EMERALD, INDIGO, etc.).",
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
        return {
            "uri": uri,
            "mimeType": "application/json",
            "text": json.dumps(tool_list_components(), indent=2),
        }
    elif uri == "vibmo://docs/verbs":
        from vibmo.mcp.tools import tool_list_components
        data = tool_list_components().get("motion_verbs", [])
        return {
            "uri": uri,
            "mimeType": "application/json",
            "text": json.dumps(data, indent=2),
        }
    elif uri == "vibmo://docs/colors":
        from vibmo.core.color import colors
        color_dict = {
            "DARK_NAVY": colors.DARK_NAVY.to_hex(),
            "SLATE_950": colors.SLATE_950.to_hex(),
            "CYAN": colors.CYAN.to_hex(),
            "EMERALD": colors.EMERALD.to_hex(),
            "INDIGO": colors.INDIGO.to_hex(),
            "VIOLET": colors.VIOLET.to_hex(),
            "ROSE": colors.ROSE.to_hex(),
            "AMBER": colors.AMBER.to_hex(),
            "BLUE": colors.BLUE.to_hex(),
            "WHITE": colors.WHITE.to_hex(),
        }
        return {
            "uri": uri,
            "mimeType": "application/json",
            "text": json.dumps(color_dict, indent=2),
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
        {
            "name": "create-kinetic-typography",
            "description": "Creates an expressive typography title reveal sequence with sound design.",
            "arguments": [
                {"name": "title", "description": "Main headline text", "required": True},
                {"name": "subtitle", "description": "Secondary tagline", "required": False},
            ],
        },
    ]
