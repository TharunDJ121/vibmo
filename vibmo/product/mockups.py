"""
Device & Software UI Mockup components (BrowserWindow, MacWindow, PhoneFrame, LaptopFrame) for product demos.
"""

from __future__ import annotations
import math
from typing import Any, Optional, Sequence, Tuple, Union
import cairo

from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D
from vibmo.scene.node import Node
from vibmo.layout.container import FlexContainer
from vibmo.primitives.rect import RoundedRect, Rect
from vibmo.typography.kinetic import KineticText


from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.spatial.shadows import DropShadow


class BrowserWindow(Node):
    """
    Polished Browser Window mockup with macOS traffic light buttons, URL bar, and content container.
    """

    def __init__(
        self,
        url: str = "https://vibmo.design",
        title: str = "Vibmo — Motion Design",
        width: float = 1280.0,
        height: float = 800.0,
        corner_radius: float = 16.0,
        bg_color: Optional[Union[Color, str]] = None,
        header_color: Optional[Union[Color, str]] = None,
        border_color: Optional[Union[Color, str]] = None,
        dark_mode: bool = True,
        shadow: Optional[Union[DropShadow, bool]] = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.url = url
        self.title_text = title
        self.width_val = float(width)
        self.height_val = float(height)
        self.corner_radius = float(corner_radius)
        self.dark_mode = dark_mode

        # Colors
        if dark_mode:
            self.bg = Color.from_any(bg_color) if bg_color else Color.hex("#090d16")
            self.header_bg = Color.from_any(header_color) if header_color else Color.hex("#0f172a")
            self.border = Color.from_any(border_color) if border_color else Color.hex("#1e293b")
            self.url_bg = Color.hex("#1e293b")
            self.url_text_color = Color.hex("#94a3b8")
        else:
            self.bg = Color.from_any(bg_color) if bg_color else Color.WHITE
            self.header_bg = Color.from_any(header_color) if header_color else Color.hex("#f1f5f9")
            self.border = Color.from_any(border_color) if border_color else Color.hex("#e2e8f0")
            self.url_bg = Color.WHITE
            self.url_text_color = Color.hex("#64748b")

        if shadow is True:
            self.shadow = DropShadow.elevated(blur=36.0, offset=(0, 18), color=Color.BLACK.with_alpha(0.50))
        elif isinstance(shadow, DropShadow):
            self.shadow = shadow
        else:
            self.shadow = None

        # Gleam light sweep progress
        self.gleam_progress = Signal(-1.0, f"{self.name}.gleam_progress")
        self.gleam_color = Color.WHITE

        # Content container where user nodes can be added
        self.header_height = 54.0
        self.content = FlexContainer(
            direction="column",
            gap=16.0,
            padding=24.0,
            width=self.width_val,
            height=self.height_val - self.header_height,
            position=(0.0, self.header_height),
            fill=Color.TRANSPARENT,
            stroke=Color.TRANSPARENT,
        )
        self.add(self.content)

    def add_content(self, *nodes: Node) -> BrowserWindow:
        """Adds child nodes directly into the browser body viewport."""
        self.content.add(*nodes)
        return self

    def gleam(
        self,
        duration: float = 1.2,
        delay: float = 0.0,
        color: Union[Color, str] = Color.WHITE,
        ease: Optional[EasingFunc] = None,
    ) -> AnimationAction:
        """Sweeps a specular light gleam across the browser window."""
        self.gleam_color = Color.from_any(color) if isinstance(color, (str, Color)) else Color.WHITE
        self.gleam_progress.set(-0.2)
        return self.gleam_progress.to(1.2, duration=duration, ease=ease or Ease.in_out_cubic, delay=delay)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width_val
        h = self.height_val
        cr = self.corner_radius
        hh = self.header_height

        ctx.save()

        # 0. Render elevated Gaussian drop shadow
        if self.shadow is not None:
            self.shadow.render_shadow(ctx, (0, 0, w, h), cr)

        # 1. Outer Window Background
        self._rounded_rect(ctx, 0, 0, w, h, cr)
        ctx.set_source_rgba(self.bg.r, self.bg.g, self.bg.b, self.bg.a)
        ctx.fill_preserve()
        
        # Directional rim stroke (brighter top-left, subtler bottom)
        stroke_pat = cairo.LinearGradient(0, 0, w, h)
        stroke_pat.add_color_stop_rgba(0.0, 1.0, 1.0, 1.0, 0.20 if self.dark_mode else 0.40)
        stroke_pat.add_color_stop_rgba(0.5, self.border.r, self.border.g, self.border.b, self.border.a)
        stroke_pat.add_color_stop_rgba(1.0, 0.0, 0.0, 0.0, 0.30)
        ctx.set_source(stroke_pat)
        ctx.set_line_width(1.5)
        ctx.stroke()

        # 2. Header Bar Background
        ctx.save()
        self._rounded_rect_top(ctx, 0, 0, w, hh, cr)
        ctx.set_source_rgba(self.header_bg.r, self.header_bg.g, self.header_bg.b, self.header_bg.a)
        ctx.fill_preserve()
        ctx.set_source_rgba(self.border.r, self.border.g, self.border.b, 0.8)
        ctx.set_line_width(1.0)
        ctx.stroke()
        ctx.restore()

        # 3. Top hairline specular highlight
        ctx.save()
        self._rounded_rect_top(ctx, 0, 0, w, hh, cr)
        ctx.clip()
        top_hl = cairo.LinearGradient(0, 0, w, 0)
        top_hl.add_color_stop_rgba(0.0, 1.0, 1.0, 1.0, 0.0)
        top_hl.add_color_stop_rgba(0.3, 1.0, 1.0, 1.0, 0.25)
        top_hl.add_color_stop_rgba(0.7, 1.0, 1.0, 1.0, 0.25)
        top_hl.add_color_stop_rgba(1.0, 1.0, 1.0, 1.0, 0.0)
        ctx.set_source(top_hl)
        ctx.set_line_width(1.2)
        ctx.move_to(cr, 1.0)
        ctx.line_to(w - cr, 1.0)
        ctx.stroke()
        ctx.restore()

        # 4. macOS Traffic Light Buttons (Close, Minimize, Maximize)
        btn_y = hh * 0.5
        btn_r = 6.0
        # Red
        ctx.set_source_rgba(0.95, 0.32, 0.32, 1.0)
        ctx.arc(24.0, btn_y, btn_r, 0, math.pi * 2)
        ctx.fill()
        # Yellow
        ctx.set_source_rgba(0.97, 0.74, 0.20, 1.0)
        ctx.arc(44.0, btn_y, btn_r, 0, math.pi * 2)
        ctx.fill()
        # Green
        ctx.set_source_rgba(0.18, 0.80, 0.44, 1.0)
        ctx.arc(64.0, btn_y, btn_r, 0, math.pi * 2)
        ctx.fill()

        # 5. Search / URL Pill Input Bar
        url_w = min(480.0, w * 0.5)
        url_h = 30.0
        url_x = (w - url_w) * 0.5
        url_y = (hh - url_h) * 0.5
        
        self._rounded_rect(ctx, url_x, url_y, url_w, url_h, 8.0)
        ctx.set_source_rgba(self.url_bg.r, self.url_bg.g, self.url_bg.b, self.url_bg.a)
        ctx.fill_preserve()
        ctx.set_source_rgba(self.border.r, self.border.g, self.border.b, 0.6)
        ctx.set_line_width(1.0)
        ctx.stroke()

        # URL Text (with lock symbol)
        ctx.set_source_rgba(self.url_text_color.r, self.url_text_color.g, self.url_text_color.b, 0.9)
        ctx.select_font_face("Segoe UI", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(13.0)
        
        display_text = f"🔒  {self.url}"
        ext = ctx.text_extents(display_text)
        ctx.move_to(url_x + (url_w - ext.width) * 0.5, url_y + (url_h + ext.height) * 0.5 - 2.0)
        ctx.show_text(display_text)

        # 6. Specular Gleam Sweep Pass
        gp = float(self.gleam_progress.get(time))
        if 0.0 <= gp <= 1.0:
            ctx.save()
            self._rounded_rect(ctx, 0, 0, w, h, cr)
            ctx.clip()

            center_dist = gp * (w + h)
            rot_pat = cairo.LinearGradient(
                center_dist - 100.0, -50.0,
                center_dist + 100.0, h + 50.0,
            )
            gc = self.gleam_color
            rot_pat.add_color_stop_rgba(0.0, gc.r, gc.g, gc.b, 0.0)
            rot_pat.add_color_stop_rgba(0.4, gc.r, gc.g, gc.b, 0.12)
            rot_pat.add_color_stop_rgba(0.5, gc.r, gc.g, gc.b, 0.40)  # Bright gleam core
            rot_pat.add_color_stop_rgba(0.6, gc.r, gc.g, gc.b, 0.12)
            rot_pat.add_color_stop_rgba(1.0, gc.r, gc.g, gc.b, 0.0)

            ctx.set_source(rot_pat)
            ctx.paint_with_alpha(0.85)
            ctx.restore()

        ctx.restore()


    def _rounded_rect(self, ctx: Any, x: float, y: float, w: float, h: float, r: float) -> None:
        r = min(r, w * 0.5, h * 0.5)
        ctx.new_path()
        ctx.arc(x + w - r, y + r, r, -math.pi * 0.5, 0)
        ctx.arc(x + w - r, y + h - r, r, 0, math.pi * 0.5)
        ctx.arc(x + r, y + h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(x + r, y + r, r, math.pi, math.pi * 1.5)
        ctx.close_path()

    def _rounded_rect_top(self, ctx: Any, x: float, y: float, w: float, h: float, r: float) -> None:
        r = min(r, w * 0.5, h * 0.5)
        ctx.new_path()
        ctx.arc(x + w - r, y + r, r, -math.pi * 0.5, 0)
        ctx.line_to(x + w, y + h)
        ctx.line_to(x, y + h)
        ctx.arc(x + r, y + r, r, math.pi, math.pi * 1.5)
        ctx.close_path()


class PhoneFrame(Node):
    """
    Smartphone device mockup (iPhone / Modern mobile bezel) with dynamic island / notch and screen slot.
    """

    def __init__(
        self,
        width: float = 380.0,
        height: float = 780.0,
        bezel_width: float = 12.0,
        corner_radius: float = 48.0,
        bezel_color: Optional[Union[Color, str]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.width_val = float(width)
        self.height_val = float(height)
        self.bezel_width = float(bezel_width)
        self.corner_radius = float(corner_radius)
        self.bezel_color = Color.from_any(bezel_color) if bezel_color else Color.hex("#1e293b")

        # Screen container for child elements
        inner_w = self.width_val - self.bezel_width * 2
        inner_h = self.height_val - self.bezel_width * 2
        self.screen = FlexContainer(
            direction="column",
            gap=12.0,
            padding=20.0,
            width=inner_w,
            height=inner_h,
            position=(self.bezel_width, self.bezel_width),
            fill=Color.hex("#090d16"),
            stroke=Color.TRANSPARENT,
            corner_radius=self.corner_radius - 8.0,
        )
        self.add(self.screen)

    def add_screen_content(self, *nodes: Node) -> PhoneFrame:
        self.screen.add(*nodes)
        return self

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width_val
        h = self.height_val
        cr = self.corner_radius

        ctx.save()

        # 1. Outer Bezel Body
        self._rounded_rect(ctx, 0, 0, w, h, cr)
        ctx.set_source_rgba(self.bezel_color.r, self.bezel_color.g, self.bezel_color.b, self.bezel_color.a)
        ctx.fill_preserve()
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.15)
        ctx.set_line_width(2.0)
        ctx.stroke()

        # 2. Dynamic Island / Pill Notch
        island_w = 110.0
        island_h = 28.0
        island_x = (w - island_w) * 0.5
        island_y = self.bezel_width + 12.0
        
        self._rounded_rect(ctx, island_x, island_y, island_w, island_h, 14.0)
        ctx.set_source_rgba(0.0, 0.0, 0.0, 1.0)
        ctx.fill()

        # Speaker & Camera Lens dots
        ctx.set_source_rgba(0.12, 0.14, 0.2, 1.0)
        ctx.arc(island_x + island_w - 20.0, island_y + 14.0, 5.0, 0, math.pi * 2)
        ctx.fill()

        ctx.restore()

    def _rounded_rect(self, ctx: Any, x: float, y: float, w: float, h: float, r: float) -> None:
        r = min(r, w * 0.5, h * 0.5)
        ctx.new_path()
        ctx.arc(x + w - r, y + r, r, -math.pi * 0.5, 0)
        ctx.arc(x + w - r, y + h - r, r, 0, math.pi * 0.5)
        ctx.arc(x + r, y + h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(x + r, y + r, r, math.pi, math.pi * 1.5)
        ctx.close_path()
