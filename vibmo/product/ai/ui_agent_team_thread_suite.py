"""
Multi-Agent Chat & Orchestration UI Suite for Vibmo / Motio.
Components:
- AgentTeamThread
- AgentMessageBubble (AgentConversationBubble)
- AgentStatusPill
- AgentTypingWave
- ToolCallingPayloadCard
"""

from __future__ import annotations
import math
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
import cairo

from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.scene.node import Node
from vibmo.layout.container import FlexContainer
from vibmo.primitives.circle import Circle
from vibmo.primitives.rect import Rect, RoundedRect
from vibmo.typography.text import Text
from vibmo.spatial.shadows import DropShadow


class AgentStatusPill(FlexContainer):
    """Pill showing agent active state with pulsing status orb."""

    def __init__(
        self,
        name: Optional[str] = None,
        status: str = "Active",
        avatar_color: Optional[Union[Color, str]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            direction="row",
            gap=6.0,
            padding=(4.0, 10.0),
            corner_radius=12.0,
            fill=Color(0.08, 0.12, 0.18, 0.9),
            stroke=Color(0.2, 0.3, 0.45, 0.7),
            stroke_width=1.0,
            align_items="center",
            **kwargs,
        )
        s_lower = status.lower()
        if avatar_color is not None:
            col = Color.from_any(avatar_color)
        elif s_lower in ("online", "active"):
            col = colors.EMERALD_500
        elif s_lower in ("offline", "idle"):
            col = colors.SLATE_400
        else:
            col = colors.CYAN
        self.avatar_color = col
        self.dot = Circle(radius=4.0, fill=self.avatar_color)
        display_text = f"{name} ({status})" if name else status.capitalize()
        self.label = Text(display_text, font_size=11.0, color=colors.SLATE_200, bold=True)
        self.add(self.dot, self.label)


class AgentTypingWave(Node):
    """Three bouncing animated dots indicating agent actively thinking/generating."""

    def __init__(self, color: Union[Color, str] = colors.CYAN, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.color = Color.from_any(color)
        self.width = 48.0
        self.height = 20.0
        self.dots = [Circle(radius=3.5, fill=self.color) for _ in range(3)]
        for i, dot in enumerate(self.dots):
            dot.position.set(Vector2D(10.0 + i * 14.0, 10.0))
            self.add(dot)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        for i, dot in enumerate(self.dots):
            wave = math.sin(time * 6.0 + i * 1.2) * 4.0
            dot.position.set(Vector2D(10.0 + i * 14.0, 10.0 - wave))
        super().draw(ctx, time)


class ToolCallingPayloadCard(FlexContainer):
    """Card displaying structured JSON tool call parameters executed by an agent."""

    def __init__(
        self,
        tool_name: str = "search_codebase",
        payload: Optional[str] = None,
        params: Optional[str] = None,
        width: float = 340.0,
        height: float = 56.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            direction="column",
            gap=4.0,
            padding=8.0,
            corner_radius=8.0,
            fill=Color(0.04, 0.08, 0.12, 0.95),
            stroke=Color(0.15, 0.45, 0.7, 0.6),
            stroke_width=1.0,
            width=width,
            height=height,
            **kwargs,
        )
        self.tool_name = tool_name
        self.payload = payload or params or '{"query": "def render_frame", "limit": 5}'
        self.params = self.payload
        self.width_val = float(width)
        self.height_val = float(height)

        class _Spinner(Node):
            def __init__(self) -> None:
                super().__init__()
                self.rotation = Signal(0.0, "spinner_rotation")

        self.spinner = _Spinner()
        self.header = FlexContainer(direction="row", gap=6.0, align_items="center")
        self.header.add(self.spinner, Text(f"tool_call: {self.tool_name}()", font_size=11.0, color=colors.CYAN, bold=True))

        self.body_node = Text(self.payload, font_size=10.0, color=colors.SLATE_200)
        self.add(self.header, self.body_node)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        self.spinner.rotation.set(time * math.pi)
        super().draw(ctx, time)


class AgentMessageBubble(FlexContainer):
    """Message bubble card showing sender avatar, name, role badge, timestamp, and message body."""

    def __init__(
        self,
        name: Optional[str] = None,
        agent_name: Optional[str] = None,
        role: str = "Agent",
        timestamp: str = "10:42 AM",
        body: Optional[str] = None,
        message: Optional[str] = None,
        avatar_color: Optional[Union[Color, str]] = None,
        accent_color: Optional[Union[Color, str]] = None,
        width: float = 600.0,
        height: float = 80.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            direction="row",
            gap=12.0,
            padding=12.0,
            corner_radius=12.0,
            fill=Color(0.07, 0.1, 0.16, 0.95),
            stroke=Color(0.18, 0.25, 0.38, 0.7),
            stroke_width=1.0,
            width=width,
            height=height,
            **kwargs,
        )
        self.sender_name = agent_name or name or "AI Assistant"
        self.role = role
        self.timestamp = timestamp
        self.body = message or body or "Here is the fix."
        self.avatar_color = Color.from_any(accent_color or avatar_color or colors.CYAN)
        self.width_val = float(width)
        self.height_val = float(height)

        self.opacity = Signal(1.0, f"{self.name}.opacity")
        self.scale_sig = Signal(1.0, f"{self.name}.scale_sig")

        # Child 0: Avatar
        self.avatar = Circle(radius=14.0, fill=self.avatar_color)

        # Child 1: Content Column
        self.content_col = FlexContainer(direction="column", gap=4.0)

        # Header row: Name, Role badge, Timestamp
        self.header_row = FlexContainer(direction="row", gap=8.0, align_items="center")
        name_node = Text(self.sender_name, font_size=13.0, color=colors.WHITE, bold=True)
        role_node = Text(self.role.upper(), font_size=9.0, color=self.avatar_color, bold=True)
        time_node = Text(self.timestamp, font_size=10.0, color=colors.SLATE_400)
        self.header_row.add(name_node, role_node, time_node)

        # Body text
        self.body_text = Text(self.body, font_size=12.0, color=colors.SLATE_200)
        self.content_col.add(self.header_row, self.body_text)

        self.add(self.avatar, self.content_col)


AgentConversationBubble = AgentMessageBubble


class AgentTeamThread(Node):
    """
    Multi-Agent Team Thread UI Suite.
    Manages interactive conversations between autonomous agents (Coder, Architect, QA, Reviewer)
    with real-time typing indicators, tool execution callouts, and message animations.
    """

    def __init__(
        self,
        title: str = "Autonomous Agent Swarm",
        width: float = 680.0,
        height: float = 520.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.title = title
        self.width_val = float(width)
        self.height_val = float(height)
        self.shadow = DropShadow(color=Color(0.0, 0.0, 0.0, 0.5), blur=32.0, offset=(0.0, 16.0))

        self.messages: List[AgentMessageBubble] = []
        self.agent_colors: Dict[str, Color] = {
            "Coder": colors.CYAN,
            "Architect": colors.INDIGO_400,
            "QA": colors.EMERALD,
            "Reviewer": colors.AMBER,
            "User": colors.ROSE,
        }

        # Status pills in header
        pills_data = [("Architect", "Idle", colors.INDIGO_400), ("Coder", "Executing", colors.CYAN), ("QA", "Monitoring", colors.EMERALD)]
        for i, (name, status, color) in enumerate(pills_data):
            pill = AgentStatusPill(name=name, status=status, avatar_color=color)
            pill.position.set(Vector2D(self.width_val - 360.0 + i * 115.0, 16.0))
            self.add(pill)

        # Initial seed messages
        self._add_initial_messages()

    def _add_initial_messages(self) -> None:
        msg1 = AgentMessageBubble(
            name="Architect",
            role="Lead",
            body="Deconstructed mission into 15 UI suites. Assigning Section 4 to Coder.",
            avatar_color=colors.INDIGO_400,
            timestamp="10:40 AM",
            width=self.width_val - 48.0,
        )
        msg1.position.set(Vector2D(24.0, 75.0))
        self.add(msg1)
        self.messages.append(msg1)

        msg2 = AgentMessageBubble(
            name="Coder",
            role="Engineer",
            body="Implementing all 15 suites with reactive Signals, Cairo renderers, and fluent verbs.",
            avatar_color=colors.CYAN,
            timestamp="10:41 AM",
            width=self.width_val - 48.0,
        )
        msg2.position.set(Vector2D(24.0, 165.0))
        self.add(msg2)
        self.messages.append(msg2)

    def post_agent_message(
        self,
        sender: Optional[str] = None,
        text: str = "Fixed.",
        role: str = "Agent",
        timestamp: str = "10:43 AM",
        duration: float = 0.8,
        agent: Optional[str] = None,
    ) -> List[AnimationAction]:
        """
        Fluent generator animation verb to dynamically post a new agent message bubble.
        """
        sender_name = agent or sender or "Coder"
        color = self.agent_colors.get(sender_name, colors.CYAN)
        y_pos = 75.0 + len(self.messages) * 90.0
        if y_pos > self.height_val - 90.0:
            y_pos = self.height_val - 90.0

        new_bubble = AgentMessageBubble(
            name=sender_name,
            role=role,
            body=text,
            avatar_color=color,
            timestamp=timestamp,
            width=self.width_val - 48.0,
        )
        new_bubble.position.set(Vector2D(24.0, y_pos))
        new_bubble.opacity.set(0.0)
        new_bubble.scale_sig.set(0.7)
        self.add(new_bubble)
        self.messages.append(new_bubble)

        return [
            new_bubble.opacity.to(1.0, duration=duration, ease=Ease.out_quad),
            new_bubble.scale_sig.to(1.0, duration=duration, ease=Ease.out_back),
        ]

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        ctx.save()

        # Canvas card container
        r = 16.0
        ctx.new_path()
        ctx.arc(w - r, r, r, -math.pi * 0.5, 0)
        ctx.arc(w - r, h - r, r, 0, math.pi * 0.5)
        ctx.arc(r, h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(r, r, r, math.pi, math.pi * 1.5)
        ctx.close_path()

        ctx.set_source_rgba(0.04, 0.06, 0.1, 0.95)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.18, 0.25, 0.38, 0.8)
        ctx.set_line_width(1.5)
        ctx.stroke()

        # Header Title
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(14.0)
        ctx.set_source_rgba(0.9, 0.95, 1.0, 0.9)
        ctx.move_to(24.0, 36.0)
        ctx.show_text(self.title)

        # Header divider
        ctx.set_source_rgba(0.2, 0.25, 0.35, 0.4)
        ctx.set_line_width(1.0)
        ctx.move_to(20.0, 58.0)
        ctx.line_to(w - 20.0, 58.0)
        ctx.stroke()

        # Draw messages and child elements
        super().draw(ctx, time)
        ctx.restore()
