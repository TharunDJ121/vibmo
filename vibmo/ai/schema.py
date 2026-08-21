"""
LLM Tool Calling & JSON-Schema Generator for AI Coding Agents (Claude, OpenAI, Gemini, Cursor).
"""

from __future__ import annotations
import inspect
import json
from typing import Any, Dict, List, Optional, Type


def generate_component_schemas() -> List[Dict[str, Any]]:
    """Generates JSON schemas for all semantic design primitives and motion verbs."""
    from vibmo.components.glass import GlassCard
    from vibmo.components.counter import MetricCounter
    from vibmo.components.code import CodeWindow
    from vibmo.components.toast import NotificationToast
    from vibmo.product.mockups import BrowserWindow, PhoneFrame
    from vibmo.product.cursor import Cursor
    from vibmo.product.charts import AreaChart, BarChart, PieChart, DonutChart, GaugeChart
    from vibmo.product.tables import DataTable, TimelineView
    from vibmo.product.social import Avatar, AvatarGroup, Badge, ChatBubble
    from vibmo.product.controls import ToggleSwitch, Checkbox, ProgressBar, RatingStars
    from vibmo.product.cards import StatCard

    components = [
        ("GlassCard", GlassCard, "Frosted glass UI container with auto-layout padding and corner radius."),
        ("MetricCounter", MetricCounter, "Animated numeric ticker with prefixes ($, €) and thousands formatting."),
        ("CodeWindow", CodeWindow, "macOS terminal and code editor mockup with syntax highlighting."),
        ("NotificationToast", NotificationToast, "Push notification popup with icon, title, and sound cue."),
        ("BrowserWindow", BrowserWindow, "macOS Safari/Chrome browser mockup window with URL address bar."),
        ("PhoneFrame", PhoneFrame, "iPhone/Android mobile mockup with speaker notch and rounded screen."),
        ("Cursor", Cursor, "macOS mouse pointer cursor with smooth move_to and spring click bounce."),
        ("AreaChart", AreaChart, "Glowing SVG spline area chart with gradient fill and path trace."),
        ("BarChart", BarChart, "Vertical or horizontal capsule bars with staggered spring growth."),
        ("PieChart", PieChart, "360-degree radial sweep pie chart with slice explosion."),
        ("DonutChart", DonutChart, "Donut chart with center KPI summary metric label."),
        ("GaugeChart", GaugeChart, "Speedometer dial with animated glowing arc and needle."),
        ("DataTable", DataTable, "Glassmorphic SaaS data table with headers, zebra rows, and status pills."),
        ("TimelineView", TimelineView, "Roadmap milestone track with animated node markers."),
        ("Avatar", Avatar, "User profile avatar badge with initials/photo and status indicator dot."),
        ("AvatarGroup", AvatarGroup, "Overlapping avatar stack with +N overflow pill badge."),
        ("Badge", Badge, "Pill badge with pulsating live status dot."),
        ("ChatBubble", ChatBubble, "Slack / iMessage conversational speech bubble with sender tag."),
        ("ToggleSwitch", ToggleSwitch, "iOS / macOS style toggle switch with animated spring thumb."),
        ("Checkbox", Checkbox, "Animated checkbox with SVG checkmark trace."),
        ("ProgressBar", ProgressBar, "Linear progress track with glowing gradient fill."),
        ("RatingStars", RatingStars, "5-star rating display with glowing gold stars."),
        ("StatCard", StatCard, "SaaS dashboard KPI metric card with header, trend badge, counter, and sparkline."),
    ]

    schemas = []
    for name, cls, desc in components:
        sig = inspect.signature(cls.__init__)
        properties: Dict[str, Any] = {}
        required: List[str] = []

        for p_name, param in sig.parameters.items():
            if p_name in ("self", "kwargs"):
                continue
            p_type = "string"
            if param.annotation in (int, float, Optional[int], Optional[float]):
                p_type = "number"
            elif param.annotation in (bool, Optional[bool]):
                p_type = "boolean"
            elif "Sequence" in str(param.annotation) or "List" in str(param.annotation):
                p_type = "array"

            properties[p_name] = {
                "type": p_type,
                "description": f"Parameter {p_name} for {name}",
            }
            if param.default == inspect.Parameter.empty:
                required.append(p_name)

        schemas.append({
            "name": name,
            "description": desc,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        })

    return schemas


def export_llm_tool_definitions(format_type: str = "openai") -> str:
    """Exports OpenAI, Anthropic, or Gemini tool call function definitions."""
    schemas = generate_component_schemas()
    if format_type.lower() == "anthropic":
        anthropic_tools = [
            {
                "name": s["name"],
                "description": s["description"],
                "input_schema": s["parameters"],
            }
            for s in schemas
        ]
        return json.dumps(anthropic_tools, indent=2)
    elif format_type.lower() == "gemini":
        gemini_tools = {
            "function_declarations": [
                {
                    "name": s["name"],
                    "description": s["description"],
                    "parameters": s["parameters"],
                }
                for s in schemas
            ]
        }
        return json.dumps(gemini_tools, indent=2)
    else:  # OpenAI standard
        openai_tools = [
            {
                "type": "function",
                "function": {
                    "name": s["name"],
                    "description": s["description"],
                    "parameters": s["parameters"],
                },
            }
            for s in schemas
        ]
        return json.dumps(openai_tools, indent=2)
