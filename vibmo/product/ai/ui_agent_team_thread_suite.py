from __future__ import annotations
import math
from typing import Any, Optional, Union

from vibmo.scene.node import Node
from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal
from vibmo.layout.container import FlexContainer
from vibmo.typography.text import Text
from vibmo.primitives.circle import Circle
from vibmo.primitives.rect import Rect, RoundedRect


class AgentStatusPill(FlexContainer):
    """Online/Busy/Thinking indicator badge."""
    def __init__(
        self,
        status: str = "online",  # "online", "busy", "thinking"
        **kwargs: Any,
    ) -> None:
        if status == "online":
            bg_color = colors.EMERALD_500.with_alpha(0.2)
            dot_color = colors.EMERALD_500
            text_str = "Online"
        elif status == "busy":
            bg_color = colors.AMBER_500.with_alpha(0.2)
            dot_color = colors.AMBER_500
            text_str = "Busy"
        elif status == "thinking":
            bg_color = colors.PURPLE_500.with_alpha(0.2)
            dot_color = colors.PURPLE_500
            text_str = "Thinking..."
        else:
            bg_color = colors.SLATE_800
            dot_color = colors.SLATE_400
            text_str = status.capitalize()

        super().__init__(
            direction="row",
            gap=6.0,
            padding=(4.0, 8.0),
            corner_radius=12.0,
            fill=bg_color,
            **kwargs,
        )
        self.dot = Circle(radius=4.0, fill=dot_color)
        self.label = Text(text=text_str, font_size=12.0, font_family="Inter", bold=True, color=dot_color)
        self.add(self.dot, self.label)


class AgentTypingWave(FlexContainer):
    """3-dot harmonic bouncing typing indicator."""
    def __init__(
        self,
        dot_color: Union[Color, str] = colors.SLATE_400,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            direction="row",
            gap=6.0,
            padding=8.0,
            corner_radius=16.0,
            fill=colors.SLATE_800,
            **kwargs,
        )
        self.dots = [
            Circle(radius=5.0, fill=dot_color) for _ in range(3)
        ]
        self.add(*self.dots)
        
    def draw(self, ctx: Any, time: float = 0.0) -> None:
        # compute layout first to establish baseline dot positions
        self.compute_layout(time)

        # modify Y offsets based on time for harmonic bounce
        speed = 2.0
        amplitude = 6.0
        for i, dot in enumerate(self.dots):
            # Staggered wave
            offset = math.sin(time * math.pi * speed - i * 0.5) * amplitude
            # the layout computation set the dot.position.get() exactly to the flex layout
            # we need to append the offset relative to that.
            base_x, base_y = dot.position.get(time)
            dot.position.set((base_x, base_y + offset))
            
        # call Node's draw to render (bypassing FlexContainer's compute_layout so we don't overwrite positions)
        super(FlexContainer, self).draw(ctx, time)


class ToolCallingPayloadCard(FlexContainer):
    """Collapsible JSON payload box showing function call args and live execution spinner."""
    def __init__(
        self,
        tool_name: str = "function_call",
        payload: str = "{}",
        is_executing: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            direction="column",
            gap=8.0,
            padding=12.0,
            corner_radius=8.0,
            fill=colors.SLATE_900,
            stroke=colors.SLATE_700,
            stroke_width=1.0,
            **kwargs,
        )
        
        header = FlexContainer(
            direction="row",
            gap=8.0,
            padding=0.0,
            fill=None,
        )
        # Mock spinner (simple circle for now)
        self.spinner = Circle(radius=6.0, stroke=colors.CYAN_500 if is_executing else colors.EMERALD_500, stroke_width=2.0, fill=None)
        title = Text(text=f"Tool: {tool_name}", font_size=14.0, font_family="Inter", bold=True, color=colors.CYAN_500)
        
        header.add(self.spinner, title)
        
        body = Text(
            text=payload,
            font_size=12.0,
            font_family="monospace",
            color=colors.SLATE_400,
            line_height=1.4,
        )
        
        self.add(header, body)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        # Simple rotation for the spinner
        if self.spinner:
            self.spinner.rotation.set(time * math.pi)
        super().draw(ctx, time)


class AgentConversationBubble(FlexContainer):
    """Rich chat bubble with agent avatar, name, role badge, timestamp, and markdown body."""
    def __init__(
        self,
        name: str = "Agent",
        role: str = "Architect", # "Architect", "Coder", "Reviewer"
        timestamp: str = "Just now",
        body: str = "Hello world!",
        avatar_color: Union[Color, str] = colors.INDIGO_500,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            direction="row",
            gap=16.0,
            padding=16.0,
            fill=None,
            align_items="start",
            **kwargs,
        )
        
        # Avatar
        self.avatar = Circle(radius=20.0, fill=avatar_color)
        
        # Right column
        self.content_col = FlexContainer(
            direction="column",
            gap=8.0,
            padding=0.0,
            fill=None,
            align_items="start",
        )
        
        # Header row
        header = FlexContainer(
            direction="row",
            gap=12.0,
            padding=0.0,
            fill=None,
            align_items="center",
        )
        
        name_text = Text(text=name, font_size=16.0, font_family="Inter", bold=True, color=colors.WHITE)
        
        # Role badge (simple rounded rect with text)
        role_badge = FlexContainer(
            direction="row",
            padding=(2.0, 6.0),
            corner_radius=6.0,
            fill=colors.SLATE_800,
            stroke=colors.SLATE_700,
            stroke_width=1.0,
        )
        role_text = Text(text=role, font_size=10.0, font_family="Inter", bold=True, color=colors.SLATE_200)
        role_badge.add(role_text)
        
        time_text = Text(text=timestamp, font_size=12.0, font_family="Inter", color=colors.SLATE_400)
        
        header.add(name_text, role_badge, time_text)
        
        # Message body
        self.message = Text(
            text=body,
            font_size=14.0,
            font_family="Inter",
            color=colors.SLATE_200,
            line_height=1.5,
        )
        
        self.content_col.add(header, self.message)
        
        self.add(self.avatar, self.content_col)
