"""
✦ Vibmo AI Suites: Interactive AI Prompt Flow & Model Composer
Inspired by Remocn ai-prompt-flow with attachment pills, model selector badges, and token streaming.
"""

from __future__ import annotations

import math
from typing import Any, List, Optional, Tuple, Union
import cairo

from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease
from vibmo.scene.node import Node
from vibmo.layout.container import FlexContainer
from vibmo.typography.text import Text
from vibmo.spatial.shadows import DropShadow
from vibmo.timeline.scheduler import all as sched_all, sequence as sched_seq


class ModelSelectorPill(FlexContainer):
    """Dropdown pill displaying active LLM model with sparkle icon."""
    def __init__(
        self,
        model_name: str = "Claude 3.7 Sonnet",
        color: Color = colors.CYAN,
        **kwargs: Any,
    ):
        super().__init__(
            direction="row",
            padding=(6, 12),
            gap=6,
            corner_radius=14.0,
            fill=Color(0.1, 0.15, 0.22, 0.9),
            stroke=Color(0.2, 0.35, 0.5, 0.8),
            stroke_width=1.0,
            align_items="center",
            **kwargs,
        )
        self.model_name = model_name
        self.pill_color = color
        self.text_label = Text(
            text=f"✦ {model_name}",
            font_size=13.0,
            font_family="Inter",
            color=color,
            bold=True,
        )
        self.add(self.text_label)


class AttachmentBadge(FlexContainer):
    """File attachment pill inside the prompt composer."""
    def __init__(
        self,
        filename: str = "schema.sql",
        file_size: str = "24 KB",
        **kwargs: Any,
    ):
        super().__init__(
            direction="row",
            padding=(5, 10),
            gap=6,
            corner_radius=8.0,
            fill=Color(0.12, 0.14, 0.18, 0.95),
            stroke=Color(0.25, 0.28, 0.35, 0.8),
            stroke_width=1.0,
            align_items="center",
            **kwargs,
        )
        self.add(
            Text(
                text=f"📄 {filename} ({file_size})",
                font_size=12.0,
                font_family="monospace",
                color=Color(0.8, 0.85, 0.9, 1.0),
            )
        )


class AiPromptFlow(FlexContainer):
    """
    Complete interactive AI prompt input box and streaming response container.
    """
    def __init__(
        self,
        prompt_text: str = "Generate a full-stack Next.js and Tailwind SaaS application...",
        response_text: str = "I'll generate the architecture, API endpoints, and React components for you.",
        model_name: str = "Claude 3.7 Sonnet",
        attachment: Optional[str] = "requirements.md",
        width: float = 780.0,
        **kwargs: Any,
    ):
        super().__init__(
            direction="column",
            padding=(20, 24),
            gap=16,
            corner_radius=20.0,
            fill=Color(0.06, 0.08, 0.12, 0.96),
            stroke=Color(0.2, 0.25, 0.35, 0.7),
            stroke_width=1.0,
            shadow=DropShadow(color=Color(0, 0, 0, 0.45), blur=24.0, offset=(0, 12)),
            **kwargs,
        )
        self.full_prompt = prompt_text
        self.full_response = response_text
        self.model_name = model_name
        self.custom_width = width

        # Top Bar: Attachment & Model Selector
        top_bar = FlexContainer(direction="row", gap=10, align_items="center")
        top_bar.add(ModelSelectorPill(model_name=model_name))
        if attachment:
            top_bar.add(AttachmentBadge(filename=attachment))
        self.add(top_bar)

        # Prompt Input Area
        self.prompt_progress = Signal(0.0, f"{self.name}.prompt_progress")
        self.prompt_node = Text(
            text="",
            font_size=16.0,
            font_family="Inter",
            color=colors.WHITE,
            line_height=1.4,
        )
        self.add(self.prompt_node)

        # Response Output Bubble
        self.response_progress = Signal(0.0, f"{self.name}.response_progress")
        self.response_container = FlexContainer(
            direction="column",
            padding=(14, 18),
            gap=8,
            corner_radius=12.0,
            fill=Color(0.1, 0.13, 0.19, 0.9),
            stroke=Color(0.2, 0.28, 0.4, 0.6),
            stroke_width=1.0,
        )
        self.response_node = Text(
            text="",
            font_size=15.0,
            font_family="Inter",
            color=Color(0.9, 0.95, 1.0, 1.0),
            line_height=1.4,
        )
        self.response_container.add(self.response_node)
        self.add(self.response_container)

    def type_prompt(self, duration: float = 1.5, ease: Any = Ease.linear) -> AnimationAction:
        """Types out the user prompt string."""
        return self.prompt_progress.to(1.0, duration=duration, ease=ease)

    def stream_response(self, duration: float = 2.0, ease: Any = Ease.linear) -> AnimationAction:
        """Streams the AI response tokens."""
        return self.response_progress.to(1.0, duration=duration, ease=ease)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        # Update dynamic typing slices
        pprog = self.prompt_progress.get(time)
        p_len = int(round(len(self.full_prompt) * pprog))
        caret = "▌" if (pprog < 1.0 and (int(time * 6) % 2 == 0)) else ""
        self.prompt_node.text.set(self.full_prompt[:p_len] + caret)

        rprog = self.response_progress.get(time)
        r_len = int(round(len(self.full_response) * rprog))
        r_caret = " ✦" if (rprog > 0.0 and rprog < 1.0) else ""
        self.response_node.text.set(self.full_response[:r_len] + r_caret)

        self.response_container.opacity.set(1.0 if rprog > 0.01 else 0.0)

        super().draw(ctx, time)
