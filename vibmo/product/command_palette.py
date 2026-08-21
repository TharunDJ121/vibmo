"""
Raycast and Linear style Command Palette Modal for Silicon-Valley developer tool demos.
"""

from __future__ import annotations
import math
from typing import Any, List, Optional, Sequence, Tuple, Union
import cairo

from vibmo.core.vector import Vector2D
from vibmo.core.color import Color, LinearGradient, colors
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.scene.node import Node
from vibmo.spatial.shadows import DropShadow


class CommandItem:
    """Descriptor for an individual action row in a CommandPalette."""
    def __init__(
        self,
        title: str,
        subtitle: str = "",
        shortcut: str = "",
        icon: str = "⚡",
        category: str = "Actions",
    ) -> None:
        self.title = title
        self.subtitle = subtitle
        self.shortcut = shortcut
        self.icon = icon
        self.category = category


class CommandPalette(Node):
    """
    Polished macOS / Raycast / Linear style Command Palette launcher modal.
    Features live typing, keyboard badge pills, and smooth animated row selection.
    """

    def __init__(
        self,
        items: Optional[Sequence[CommandItem]] = None,
        width: float = 640.0,
        placeholder: str = "Type a command or search...",
        active_index: int = 0,
        corner_radius: float = 20.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.width_val = float(width)
        self.corner_radius = float(corner_radius)
        self.placeholder = placeholder
        
        default_items = [
            CommandItem("Deploy to Production", "Deploy latest commit to edge network", "⌘↵", "🚀"),
            CommandItem("Create New Project", "Scaffold motion design pipeline", "⌘N", "✨"),
            CommandItem("Open In Raycast", "Launch desktop extension", "⌥R", "⚡"),
            CommandItem("Toggle Dark Mode", "Switch editor color theme", "⌘D", "🌙"),
        ]
        self.items = list(items) if items else default_items
        
        # Calculate dynamic modal height
        self.header_h = 60.0
        self.row_h = 52.0
        self.height_val = self.header_h + len(self.items) * self.row_h + 16.0

        # Animatable signals
        self.search_text = Signal("", f"{self.name}.search_text")
        self.selected_index = Signal(float(active_index), f"{self.name}.selected_index")
        self.action_flash = Signal(0.0, f"{self.name}.action_flash")

        # Elevated drop shadow
        self.shadow = DropShadow.elevated(blur=45.0, offset=(0, 22), color=Color.BLACK.with_alpha(0.60))

    def type_search(
        self,
        query: str,
        speed: float = 20.0,
        delay: float = 0.0,
    ) -> List[AnimationAction]:
        """Simulates typing into the search input box."""
        actions: List[AnimationAction] = []
        dt = 1.0 / speed
        for i in range(1, len(query) + 1):
            sub = query[:i]
            actions.append(self.search_text.to(sub, duration=0.01, delay=delay + i * dt))
        return actions

    def select_item(
        self,
        index: int,
        duration: float = 0.4,
        delay: float = 0.0,
        ease: Optional[EasingFunc] = None,
    ) -> AnimationAction:
        """Smoothly slides the selection highlight pill to target row index."""
        e = ease or Ease.spring(stiffness=200, damping=15)
        return self.selected_index.to(float(index), duration=duration, ease=e, delay=delay)

    def hit_enter(self, duration: float = 0.3) -> List[AnimationAction]:
        """Triggers a brilliant select flash confirmation."""
        return [
            self.action_flash.to(1.0, duration=duration * 0.3, ease=Ease.out_quad),
            self.action_flash.to(0.0, duration=duration * 0.7, ease=Ease.in_quad, delay=duration * 0.3),
        ]

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def _rounded_rect(self, ctx: Any, x: float, y: float, w: float, h: float, r: float) -> None:
        r = min(r, w * 0.5, h * 0.5)
        ctx.new_path()
        ctx.arc(x + w - r, y + r, r, -math.pi * 0.5, 0)
        ctx.arc(x + w - r, y + h - r, r, 0, math.pi * 0.5)
        ctx.arc(x + r, y + h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(x + r, y + r, r, math.pi, math.pi * 1.5)
        ctx.close_path()

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width_val
        h = self.height_val
        cr = self.corner_radius

        ctx.save()

        # 1. Elevated Gaussian drop shadow
        if self.shadow is not None:
            self.shadow.render_shadow(ctx, (0, 0, w, h), cr)

        # 2. Main Modal Background (Deep Glass Charcoal)
        self._rounded_rect(ctx, 0, 0, w, h, cr)
        ctx.set_source_rgba(0.06, 0.08, 0.12, 0.94)
        ctx.fill_preserve()

        # Specular Directional Border Rim
        rim = cairo.LinearGradient(0, 0, w, h)
        rim.add_color_stop_rgba(0.0, 1.0, 1.0, 1.0, 0.25)
        rim.add_color_stop_rgba(0.4, 0.2, 0.3, 0.45, 0.50)
        rim.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.20)
        ctx.set_source(rim)
        ctx.set_line_width(1.5)
        ctx.stroke()

        # 3. Search Input Header
        # Search Icon 🔍
        ctx.select_font_face("Segoe UI", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(18.0)
        ctx.set_source_rgba(0.55, 0.62, 0.72, 0.8)
        ctx.move_to(24.0, 37.0)
        ctx.show_text("🔍")

        # Search Query Text or Placeholder
        query = str(self.search_text.get(time))
        ctx.set_font_size(16.0)
        if query:
            ctx.set_source_rgba(1.0, 1.0, 1.0, 0.95)
            ctx.move_to(56.0, 36.0)
            ctx.show_text(query)
            
            # Flashing Cursor Bar
            if int(time * 3) % 2 == 0:
                ext = ctx.text_extents(query)
                ctx.set_source_rgba(0.39, 0.40, 0.95, 1.0)
                ctx.rectangle(58.0 + ext.width, 21.0, 2.0, 20.0)
                ctx.fill()
        else:
            ctx.set_source_rgba(0.40, 0.47, 0.58, 0.65)
            ctx.move_to(56.0, 36.0)
            ctx.show_text(self.placeholder)

        # ⌘K Shortcut Badge (Right)
        badge_w = 42.0
        badge_h = 24.0
        badge_x = w - badge_w - 24.0
        badge_y = (self.header_h - badge_h) * 0.5
        self._rounded_rect(ctx, badge_x, badge_y, badge_w, badge_h, 6.0)
        ctx.set_source_rgba(0.15, 0.20, 0.30, 0.8)
        ctx.fill_preserve()
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.1)
        ctx.set_line_width(1.0)
        ctx.stroke()

        ctx.set_source_rgba(0.65, 0.72, 0.82, 0.9)
        ctx.set_font_size(12.0)
        ctx.move_to(badge_x + 9.0, badge_y + 16.0)
        ctx.show_text("⌘K")

        # Header Divider Line
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.08)
        ctx.set_line_width(1.0)
        ctx.move_to(0, self.header_h)
        ctx.line_to(w, self.header_h)
        ctx.stroke()

        # 4. Animated Active Row Selection Pill
        sel_idx = float(self.selected_index.get(time))
        pill_y = self.header_h + 8.0 + (sel_idx * self.row_h)
        pill_x = 12.0
        pill_w = w - 24.0
        pill_h = self.row_h - 4.0

        # Indigo selection highlight
        self._rounded_rect(ctx, pill_x, pill_y, pill_w, pill_h, 10.0)
        flash = float(self.action_flash.get(time))
        if flash > 0.01:
            ctx.set_source_rgba(0.25 + flash * 0.5, 0.35 + flash * 0.5, 0.95, 0.85)
        else:
            ctx.set_source_rgba(0.24, 0.28, 0.75, 0.45)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.39, 0.42, 0.95, 0.7)
        ctx.set_line_width(1.2)
        ctx.stroke()

        # 5. Render Command Rows
        for i, item in enumerate(self.items):
            row_y = self.header_h + 8.0 + (i * self.row_h)
            is_active = (abs(sel_idx - i) < 0.4)

            # Icon
            ctx.set_font_size(16.0)
            ctx.set_source_rgba(1.0, 1.0, 1.0, 0.9 if is_active else 0.6)
            ctx.move_to(28.0, row_y + 28.0)
            ctx.show_text(item.icon)

            # Title
            ctx.select_font_face("Segoe UI", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if is_active else cairo.FONT_WEIGHT_NORMAL)
            ctx.set_font_size(14.5)
            ctx.set_source_rgba(1.0, 1.0, 1.0, 0.95 if is_active else 0.80)
            ctx.move_to(60.0, row_y + 25.0)
            ctx.show_text(item.title)

            # Subtitle
            if item.subtitle:
                ctx.select_font_face("Segoe UI", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                ctx.set_font_size(12.0)
                ctx.set_source_rgba(0.55, 0.62, 0.74, 0.7 if is_active else 0.45)
                ctx.move_to(60.0, row_y + 41.0)
                ctx.show_text(item.subtitle)

            # Keyboard Shortcut (Right)
            if item.shortcut:
                ctx.select_font_face("Segoe UI", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                ctx.set_font_size(12.0)
                ctx.set_source_rgba(0.70, 0.78, 0.90, 0.85 if is_active else 0.45)
                ext = ctx.text_extents(item.shortcut)
                ctx.move_to(w - ext.width - 28.0, row_y + 29.0)
                ctx.show_text(item.shortcut)

        ctx.restore()
