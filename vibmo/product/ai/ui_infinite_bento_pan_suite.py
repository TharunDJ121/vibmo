"""
✦ Vibmo AI Suites: Infinite Bento Pan 2.5D Dashboard Grid
Inspired by Remocn infinite-bento-pan with camera drift over interactive bento cards.
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


class BentoGridCard(FlexContainer):
    """Individual card inside the Bento Pan matrix."""
    def __init__(
        self,
        title: str,
        subtitle: str,
        value: str = "",
        accent_color: Color = colors.CYAN,
        card_width: float = 320.0,
        card_height: float = 200.0,
        **kwargs: Any,
    ):
        super().__init__(
            direction="column",
            padding=(20, 24),
            gap=10,
            width=card_width,
            height=card_height,
            corner_radius=18.0,
            fill=Color(0.07, 0.09, 0.14, 0.95),
            stroke=Color(0.2, 0.25, 0.38, 0.7),
            stroke_width=1.0,
            shadow=DropShadow(color=Color(0, 0, 0, 0.3), blur=16.0, offset=(0, 6)),
            **kwargs,
        )
        self.add(Text(text=title, font_size=16.0, font_family="Inter", color=colors.WHITE, bold=True))
        if value:
            self.add(Text(text=value, font_size=28.0, font_family="Inter", color=accent_color, bold=True))
        self.add(Text(text=subtitle, font_size=13.0, font_family="Inter", color=Color(0.65, 0.7, 0.8, 1.0), line_height=1.3))


class InfiniteBentoPan(Node):
    """
    Assembles a matrix of Bento Grid cards and executes a 2.5D camera drift across them.
    """
    def __init__(
        self,
        cards: Optional[List[BentoGridCard]] = None,
        pan_speed: float = 0.5,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.pan_speed = pan_speed
        self.pan_x = Signal(0.0, f"{self.name}.pan_x")
        self.pan_y = Signal(0.0, f"{self.name}.pan_y")

        self.cards = cards if cards else self._default_cards()
        self._arrange_cards()

    def _default_cards(self) -> List[BentoGridCard]:
        return [
            BentoGridCard("⚡ Automated Latency", "Global edge acceleration", "14ms", colors.EMERALD),
            BentoGridCard("✦ AI Orchestrator", "Autonomous multi-agent swarms", "99.9%", colors.CYAN),
            BentoGridCard("📈 MRR Acceleration", "Real-time revenue growth", "+48.2%", colors.AMBER),
            BentoGridCard("🔒 Zero-Trust Vault", "Hardware encryption keys", "AES-256", colors.INDIGO),
        ]

    def _arrange_cards(self) -> None:
        positions = [
            (0.0, 0.0),
            (350.0, 0.0),
            (0.0, 230.0),
            (350.0, 230.0),
        ]
        for i, card in enumerate(self.cards):
            if i < len(positions):
                card.position.set(positions[i])
            self.add(card)

    def pan_camera(self, target_offset: Tuple[float, float], duration: float = 2.5, ease: Any = Ease.out_cubic) -> AnimationAction:
        """Pans the 2.5D camera across the bento matrix."""
        return sched_all(
            self.pan_x.to(target_offset[0], duration=duration, ease=ease),
            self.pan_y.to(target_offset[1], duration=duration, ease=ease),
        )

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        px = self.pan_x.get(time)
        py = self.pan_y.get(time)

        ctx.save()
        # Apply camera pan translation
        ctx.translate(px, py)
        super().draw(ctx, time)
        ctx.restore()
