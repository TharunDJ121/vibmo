"""
Social, Identity, User Profiles, Avatars, Badges, and Conversational Chat UI Components.
"""

from __future__ import annotations
import math
from typing import Any, List, Optional, Sequence, Tuple, Union
import cairo

from vibmo.core.vector import Vector2D
from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.scene.node import Node
from vibmo.layout.container import FlexContainer
from vibmo.typography.kinetic import KineticText


class Avatar(Node):
    """
    User profile avatar badge with initials or photo, border ring, and live status indicator dot.
    """

    def __init__(
        self,
        name: str = "Alex Rivera",
        size: float = 48.0,
        status: Optional[str] = "online",  # "online", "busy", "offline", None
        color: Optional[Union[Color, str]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.user_name = str(name)
        self.size_val = float(size)
        self.status = status.lower() if status else None

        # Auto-derive initials (e.g. "Alex Rivera" -> "AR")
        parts = self.user_name.split()
        if len(parts) >= 2:
            self.initials = f"{parts[0][0]}{parts[1][0]}".upper()
        elif parts:
            self.initials = parts[0][:2].upper()
        else:
            self.initials = "U"

        # Unique color based on name hash if not provided
        if color:
            self.bg_color = Color.from_any(color)
        else:
            palette = [colors.INDIGO, colors.CYAN, colors.VIOLET, colors.EMERALD, colors.ROSE, colors.AMBER]
            idx = sum(ord(c) for c in self.user_name) % len(palette)
            self.bg_color = palette[idx]

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.size_val, self.size_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        sz = self.size_val
        r = sz * 0.5
        c = self.bg_color

        # 1. Outer Disc
        ctx.save()
        ctx.arc(r, r, r - 1.0, 0, math.pi * 2)
        ctx.set_source_rgba(c.r, c.g, c.b, 0.95)
        ctx.fill_preserve()
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.25)
        ctx.set_line_width(1.5)
        ctx.stroke()

        # 2. Initials Typography
        ctx.set_source_rgba(1.0, 1.0, 1.0, 1.0)
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(sz * 0.38)
        ext = ctx.text_extents(self.initials)
        ctx.move_to(r - ext.width * 0.5, r + ext.height * 0.35)
        ctx.show_text(self.initials)

        # 3. Status Indicator Dot
        if self.status:
            dot_r = max(3.5, sz * 0.14)
            dot_x = sz - dot_r - 1.0
            dot_y = sz - dot_r - 1.0

            status_colors = {
                "online": colors.EMERALD,
                "busy": colors.ROSE,
                "away": colors.AMBER,
                "offline": Color.hex("#64748b"),
            }
            sc = status_colors.get(self.status, colors.EMERALD)

            ctx.arc(dot_x, dot_y, dot_r, 0, math.pi * 2)
            ctx.set_source_rgba(sc.r, sc.g, sc.b, 1.0)
            ctx.fill_preserve()
            ctx.set_source_rgba(0.04, 0.07, 0.12, 1.0)  # Dark border ring around dot
            ctx.set_line_width(2.0)
            ctx.stroke()

        ctx.restore()


class AvatarGroup(Node):
    """
    Overlapping Stack of User Avatars with '+N' overflow badge and staggered pop-in.
    """

    def __init__(
        self,
        users: Sequence[str] = ("Alex Rivera", "Sarah Chen", "Marcus Vance", "Elena Rostova"),
        max_visible: int = 3,
        avatar_size: float = 42.0,
        overlap: float = 14.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.users = list(users)
        self.max_visible = max_visible
        self.avatar_size = float(avatar_size)
        self.overlap = float(overlap)

        visible_count = min(len(self.users), self.max_visible)
        self.avatars: List[Avatar] = []
        for i in range(visible_count):
            av = Avatar(name=self.users[i], size=self.avatar_size, position=(i * (self.avatar_size - self.overlap), 0.0))
            self.avatars.append(av)
            self.add(av)

        self.overflow_count = max(0, len(self.users) - self.max_visible)

    def pop_in_all(
        self,
        duration: float = 0.6,
        stagger: float = 0.08,
        delay: float = 0.0,
    ) -> Any:
        """Pops in each avatar in sequence with spring bounce."""
        from vibmo.timeline.scheduler import ParallelGroup
        actions = []
        for i, av in enumerate(self.avatars):
            actions.append(av.pop_in(duration=duration, delay=delay + i * stagger))
        return ParallelGroup(actions)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        visible_count = min(len(self.users), self.max_visible)
        extra_w = (self.avatar_size - self.overlap) if self.overflow_count > 0 else 0.0
        w = visible_count * (self.avatar_size - self.overlap) + self.overlap + extra_w
        return (0.0, 0.0, w, self.avatar_size)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        # Children draw automatically; draw +N overflow if needed
        if self.overflow_count > 0:
            visible_count = min(len(self.users), self.max_visible)
            x = visible_count * (self.avatar_size - self.overlap)
            sz = self.avatar_size
            r = sz * 0.5

            ctx.save()
            ctx.arc(x + r, r, r - 1.0, 0, math.pi * 2)
            ctx.set_source_rgba(0.2, 0.25, 0.35, 0.95)
            ctx.fill_preserve()
            ctx.set_source_rgba(0.04, 0.07, 0.12, 1.0)
            ctx.set_line_width(2.0)
            ctx.stroke()

            ctx.set_source_rgba(1.0, 1.0, 1.0, 0.95)
            ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(sz * 0.32)
            txt = f"+{self.overflow_count}"
            ext = ctx.text_extents(txt)
            ctx.move_to(x + r - ext.width * 0.5, r + ext.height * 0.35)
            ctx.show_text(txt)
            ctx.restore()


class Badge(Node):
    """
    Status Tag / Pill Badge with live glowing pulse dot and border.
    """

    def __init__(
        self,
        text: str = "LIVE",
        color: Optional[Union[Color, str]] = colors.EMERALD,
        pulse: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.text = str(text)
        self.color = Color.from_any(color) if color else colors.EMERALD
        self.pulse = pulse

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        w = len(self.text) * 8.5 + 36.0
        return (0.0, 0.0, w, 26.0)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = len(self.text) * 8.5 + 36.0
        h = 26.0
        r = h * 0.5
        c = self.color

        ctx.save()
        # Capsule background
        ctx.new_sub_path()
        ctx.arc(w - r, r, r, -math.pi / 2, math.pi / 2)
        ctx.arc(r, r, r, math.pi / 2, 3 * math.pi / 2)
        ctx.close_path()

        ctx.set_source_rgba(c.r, c.g, c.b, 0.15)
        ctx.fill_preserve()
        ctx.set_source_rgba(c.r, c.g, c.b, 0.6)
        ctx.set_line_width(1.0)
        ctx.stroke()

        # Pulsating glowing dot
        dot_rad = 3.5 + (math.sin(time * 6.0) * 1.0 if self.pulse else 0.0)
        ctx.arc(12.0, r, dot_rad, 0, math.pi * 2)
        ctx.set_source_rgba(c.r, c.g, c.b, 0.95)
        ctx.fill()

        # Text label
        ctx.set_source_rgba(c.r, c.g, c.b, 1.0)
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(11.0)
        ctx.move_to(22.0, r + 4.0)
        ctx.show_text(self.text)

        ctx.restore()


class ChatBubble(Node):
    """
    Conversational Speech Bubble (Slack / iMessage / Discord style) with sender tag and animated entrance.
    """

    def __init__(
        self,
        message: str = "Deploying autonomous AI agents to production 🚀",
        sender: str = "Claude",
        is_me: bool = False,
        width: float = 380.0,
        color: Optional[Union[Color, str]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.message = str(message)
        self.sender = str(sender)
        self.is_me = is_me
        self.width_val = float(width)

        if color:
            self.bubble_color = Color.from_any(color)
        elif is_me:
            self.bubble_color = Color.hex("#6366f1")  # Indigo for sender
        else:
            self.bubble_color = Color.hex("#1e293b")  # Slate for incoming

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        # Approximate height based on message length
        lines = max(1, len(self.message) // 38 + 1)
        h = 36.0 + lines * 20.0
        return (0.0, 0.0, self.width_val, h)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width_val
        lines = max(1, len(self.message) // 38 + 1)
        h = 36.0 + lines * 20.0
        r = 16.0
        c = self.bubble_color

        ctx.save()
        # 1. Rounded Bubble Card
        ctx.new_sub_path()
        ctx.arc(w - r, r, r, -math.pi / 2, 0)
        ctx.arc(w - r, h - r, r, 0, math.pi / 2)
        ctx.arc(r, h - r, r, math.pi / 2, math.pi)
        ctx.arc(r, r, r, math.pi, 3 * math.pi / 2)
        ctx.close_path()

        ctx.set_source_rgba(c.r, c.g, c.b, 0.95)
        ctx.fill_preserve()
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.15)
        ctx.set_line_width(1.0)
        ctx.stroke()

        # 2. Sender Tag
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.6)
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(11.0)
        ctx.move_to(16.0, 18.0)
        ctx.show_text(self.sender)

        # 3. Message Text
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.95)
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(14.0)
        ctx.move_to(16.0, 38.0)
        ctx.show_text(self.message)

        ctx.restore()


class TypingIndicator(Node):
    """
    3-Dot Harmonic Bouncing Typing Indicator Bubble.
    """

    def __init__(
        self,
        color: Optional[Union[Color, str]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.bubble_color = Color.from_any(color) if color else Color.hex("#1e293b")

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, 72.0, 36.0)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = 72.0, 36.0
        r = h * 0.5
        c = self.bubble_color

        ctx.save()
        # Capsule background
        ctx.new_sub_path()
        ctx.arc(w - r, r, r, -math.pi / 2, math.pi / 2)
        ctx.arc(r, r, r, math.pi / 2, 3 * math.pi / 2)
        ctx.close_path()

        ctx.set_source_rgba(c.r, c.g, c.b, 0.95)
        ctx.fill()

        # 3 Bouncing Dots
        for i in range(3):
            dx = 24.0 + i * 12.0
            bounce_y = math.sin(time * 8.0 - i * 0.8) * 4.0
            ctx.arc(dx, r + bounce_y, 3.5, 0, math.pi * 2)
            ctx.set_source_rgba(1.0, 1.0, 1.0, 0.85)
            ctx.fill()

        ctx.restore()
