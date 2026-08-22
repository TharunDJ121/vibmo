from __future__ import annotations
import math
import cairo
from typing import Any, Tuple, Union, Optional

from vibmo.core.vector import Vector2D
from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal
from vibmo.core.easing import Ease
from vibmo.scene.node import Node
from vibmo.typography.text import Text


def _format_k_m(num: float) -> str:
    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1000:
        return f"{num / 1000:.0f}k"
    return str(int(num))


class CircularTokenQuotaRing(Node):
    """
    Thick circular progress ring showing tokens used vs total quota.
    """
    def __init__(
        self,
        used: float = 842000,
        total: float = 1000000,
        radius: float = 120.0,
        thickness: float = 24.0,
        track_color: Union[Color, str] = colors.SLATE_800,
        fill_color: Union[Color, str] = colors.BLUE,
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.used = Signal(float(used), f"{self.name}.used")
        self.total = Signal(float(total), f"{self.name}.total")
        self.radius = Signal(float(radius), f"{self.name}.radius")
        self.thickness = Signal(float(thickness), f"{self.name}.thickness")
        self.track_color = Color.from_any(track_color)
        self.fill_color = Color.from_any(fill_color)
        
        # We will add text dynamically during draw to reflect current signal values
        self._text_node = Text("", font_size=24, align="center")
        self.children.append(self._text_node)

    def draw(self, ctx: cairo.Context, time: float = 0.0) -> None:
        used_val = self.used.get(time)
        total_val = self.total.get(time)
        r = self.radius.get(time)
        t = self.thickness.get(time)
        
        ratio = max(0.0, min(1.0, used_val / total_val)) if total_val > 0 else 0.0
        
        ctx.save()
        
        # Track
        ctx.set_line_width(t)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.arc(0, 0, r, 0, 2 * math.pi)
        ctx.set_source_rgba(self.track_color.r, self.track_color.g, self.track_color.b, self.track_color.a)
        ctx.stroke()
        
        # Fill
        if ratio > 0.001:
            start_angle = -math.pi / 2
            end_angle = start_angle + (ratio * 2 * math.pi)
            ctx.arc(0, 0, r, start_angle, end_angle)
            ctx.set_source_rgba(self.fill_color.r, self.fill_color.g, self.fill_color.b, self.fill_color.a)
            ctx.stroke()
            
        ctx.restore()
        
        text_str = f"{_format_k_m(used_val)} / {_format_k_m(total_val)}"
        self._text_node.text.set(text_str)
        # We need to manually draw the child here if it's not being traversed or just let the scene graph do it.
        # But wait, Scene Graph automatically traverses children after drawing this node. So we are good.


class OverLimitWarningBanner(Node):
    """
    Animated warning notification bar when quota exceeds 90%.
    """
    def __init__(
        self,
        ratio: float = 0.95,
        width: float = 400.0,
        height: float = 48.0,
        color: Union[Color, str] = colors.RED,
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.ratio = Signal(float(ratio), f"{self.name}.ratio")
        self.width_val = Signal(float(width), f"{self.name}.width")
        self.height_val = Signal(float(height), f"{self.name}.height")
        self.color = Color.from_any(color)
        
        self._text_node = Text("Warning: Quota Exceeds 90%", font_size=16, align="center")
        self.children.append(self._text_node)

    def draw(self, ctx: cairo.Context, time: float = 0.0) -> None:
        ratio_val = self.ratio.get(time)
        
        if ratio_val <= 0.9:
            self._text_node.opacity.set(0.0)
            return
            
        self._text_node.opacity.set(1.0)
        
        w = self.width_val.get(time)
        h = self.height_val.get(time)
        
        # Pulse animation if over 95%
        opacity = 1.0
        if ratio_val > 0.95:
            opacity = 0.7 + 0.3 * math.sin(time * math.pi * 2.0)
            
        ctx.save()
        
        # Background
        corner_radius = 8.0
        
        # Center origin
        x = -w / 2
        y = -h / 2
        
        ctx.new_path()
        ctx.arc(x + w - corner_radius, y + corner_radius, corner_radius, -math.pi/2, 0)
        ctx.arc(x + w - corner_radius, y + h - corner_radius, corner_radius, 0, math.pi/2)
        ctx.arc(x + corner_radius, y + h - corner_radius, corner_radius, math.pi/2, math.pi)
        ctx.arc(x + corner_radius, y + corner_radius, corner_radius, math.pi, 3*math.pi/2)
        ctx.close_path()
        
        ctx.set_source_rgba(self.color.r, self.color.g, self.color.b, self.color.a * opacity)
        ctx.fill()
        
        ctx.restore()


class UsageThresholdPill(Node):
    """
    Small badge indicating remaining days in billing cycle.
    """
    def __init__(
        self,
        days_left: int = 14,
        width: float = 80.0,
        height: float = 24.0,
        bg_color: Union[Color, str] = colors.SLATE_800,
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.days_left = Signal(float(days_left), f"{self.name}.days_left")
        self.width_val = Signal(float(width), f"{self.name}.width")
        self.height_val = Signal(float(height), f"{self.name}.height")
        self.bg_color = Color.from_any(bg_color)
        
        self._text_node = Text("", font_size=12, align="center")
        self.children.append(self._text_node)

    def draw(self, ctx: cairo.Context, time: float = 0.0) -> None:
        w = self.width_val.get(time)
        h = self.height_val.get(time)
        days = int(self.days_left.get(time))
        
        self._text_node.text.set(f"{days}d left")
        
        ctx.save()
        
        x = -w / 2
        y = -h / 2
        r = h / 2
        
        ctx.new_path()
        ctx.arc(x + w - r, y + r, r, -math.pi/2, 0)
        ctx.arc(x + w - r, y + h - r, r, 0, math.pi/2)
        ctx.arc(x + r, y + h - r, r, math.pi/2, math.pi)
        ctx.arc(x + r, y + r, r, math.pi, 3*math.pi/2)
        ctx.close_path()
        
        ctx.set_source_rgba(self.bg_color.r, self.bg_color.g, self.bg_color.b, self.bg_color.a)
        ctx.fill()
        
        ctx.restore()


class UpgradeCtaButton(Node):
    """
    Gradient "Upgrade to Unlimited" button with spring hover bounce.
    """
    def __init__(
        self,
        width: float = 200.0,
        height: float = 48.0,
        color_start: Union[Color, str] = colors.INDIGO,
        color_end: Union[Color, str] = colors.PURPLE,
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.width_val = Signal(float(width), f"{self.name}.width")
        self.height_val = Signal(float(height), f"{self.name}.height")
        self.color_start = Color.from_any(color_start)
        self.color_end = Color.from_any(color_end)
        self.hover_progress = Signal(0.0, f"{self.name}.hover")
        
        self._text_node = Text("Upgrade to Unlimited", font_size=16, align="center")
        self.children.append(self._text_node)

    def draw(self, ctx: cairo.Context, time: float = 0.0) -> None:
        w = self.width_val.get(time)
        h = self.height_val.get(time)
        hover = self.hover_progress.get(time)
        
        scale = 1.0 + (0.05 * hover) # Spring bounce effect based on hover progress
        
        ctx.save()
        ctx.scale(scale, scale)
        
        # Also need to scale the text
        self._text_node.scale.set((scale, scale))
        
        x = -w / 2
        y = -h / 2
        r = 12.0
        
        ctx.new_path()
        ctx.arc(x + w - r, y + r, r, -math.pi/2, 0)
        ctx.arc(x + w - r, y + h - r, r, 0, math.pi/2)
        ctx.arc(x + r, y + h - r, r, math.pi/2, math.pi)
        ctx.arc(x + r, y + r, r, math.pi, 3*math.pi/2)
        ctx.close_path()
        
        pat = cairo.LinearGradient(x, y, x + w, y + h)
        pat.add_color_stop_rgba(0, self.color_start.r, self.color_start.g, self.color_start.b, self.color_start.a)
        pat.add_color_stop_rgba(1, self.color_end.r, self.color_end.g, self.color_end.b, self.color_end.a)
        
        ctx.set_source(pat)
        ctx.fill()
        
        ctx.restore()
