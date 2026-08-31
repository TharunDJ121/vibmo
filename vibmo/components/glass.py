"""
Glassmorphic Card UI container with frosted translucent fill, directional specular border, and gleam animations.
"""

from __future__ import annotations
import math
from typing import Any, List, Optional, Union
import cairo
from vibmo.core.color import Color, LinearGradient, colors
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.layout.container import FlexContainer
from vibmo.spatial.shadows import DropShadow


class GlassCard(FlexContainer):
    """
    Frosted glass UI card with directional specular highlights, elevated Gaussian depth, and gleam animations.
    """

    def __init__(
        self,
        corner_radius: float = 24.0,
        fill: Optional[Union[Color, str]] = None,
        stroke: Optional[Union[Color, LinearGradient, str]] = None,
        stroke_width: float = 1.5,
        padding: float = 28.0,
        glow: bool = False,
        backdrop_blur: float = 0.0,
        shadow: Optional[Union[DropShadow, bool]] = True,
        specular_rim: bool = True,
        **kwargs: Any,
    ) -> None:
        resolved_fill = fill if fill is not None else Color.WHITE.with_alpha(0.06)
        
        # Directional rim lighting: brighter top-left catching the key light, darker bottom-right
        if stroke is None and specular_rim:
            resolved_stroke = LinearGradient(
                start=(0.0, 0.0),
                end=(1.0, 1.0),
                stops=[
                    (0.0, Color.WHITE.with_alpha(0.25)),
                    (0.4, Color.WHITE.with_alpha(0.12)),
                    (1.0, Color.WHITE.with_alpha(0.03)),
                ],
            )
        elif stroke is not None:
            resolved_stroke = Color.from_any(stroke) if isinstance(stroke, (str, Color)) else stroke
        else:
            resolved_stroke = Color.WHITE.with_alpha(0.12)

        super().__init__(
            corner_radius=corner_radius,
            fill=resolved_fill,
            stroke=resolved_stroke,
            stroke_width=stroke_width,
            padding=padding,
            **kwargs,
        )
        self.backdrop_blur = backdrop_blur
        self.specular_rim = specular_rim
        
        # Gleam light sweep progress (-1.0: idle, 0.0 to 1.0: sweeping across)
        self.gleam_progress = Signal(-1.0, f"{self.name}.gleam_progress")
        self.gleam_color = Color.WHITE

        if shadow is True:
            self.shadow = DropShadow.elevated(blur=28.0, offset=(0, 12), color=Color.BLACK.with_alpha(0.42))
        elif isinstance(shadow, DropShadow):
            self.shadow = shadow
        else:
            self.shadow = None

    def gleam(
        self,
        duration: float = 1.0,
        delay: float = 0.0,
        color: Union[Color, str] = Color.WHITE,
        ease: Optional[EasingFunc] = None,
    ) -> AnimationAction:
        """
        Sweeps a brilliant specular light glint across the card surface and glass border.
        """
        self.gleam_color = Color.from_any(color) if isinstance(color, (str, Color)) else Color.WHITE
        self.gleam_progress.set(-0.2)
        e = ease or Ease.in_out_cubic
        return self.gleam_progress.to(1.2, duration=duration, ease=e, delay=delay)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        bx, by, bw, bh = self.local_bounds(time)
        cr = float(self.corner_radius.get(time))

        # 1. Render true Gaussian drop shadow
        if self.shadow is not None:
            self.shadow.render_shadow(ctx, (bx, by, bw, bh), cr)

        # 2. Render frosted backdrop blur
        if self.backdrop_blur > 0.0:
            import numpy as np
            from PIL import Image, ImageFilter

            surf = ctx.get_target()
            surf.flush()
            w, h = surf.get_width(), surf.get_height()

            if w > 4 and h > 4:
                buf = surf.get_data()
                arr = np.ndarray(shape=(h, w, 4), dtype=np.uint8, buffer=buf)
                
                # Cairo ARGB32 in memory is BGRA on little-endian platforms; convert to RGBA
                rgba_temp = np.zeros_like(arr)
                rgba_temp[:, :, 0] = arr[:, :, 2]  # R
                rgba_temp[:, :, 1] = arr[:, :, 1]  # G
                rgba_temp[:, :, 2] = arr[:, :, 0]  # B
                rgba_temp[:, :, 3] = arr[:, :, 3]  # A
                
                img = Image.fromarray(rgba_temp, "RGBA")
                
                scale_fac = 0.25
                sw, sh = max(1, int(w * scale_fac)), max(1, int(h * scale_fac))
                img_small = img.resize((sw, sh), Image.Resampling.BILINEAR)
                blurred_small = img_small.filter(ImageFilter.GaussianBlur(self.backdrop_blur * scale_fac))
                blurred = blurred_small.resize((w, h), Image.Resampling.BILINEAR)
                
                blurred_rgba = np.array(blurred)
                # Convert back to Cairo BGRA
                blurred_bgra = np.zeros_like(blurred_rgba)
                blurred_bgra[:, :, 0] = blurred_rgba[:, :, 2]  # B
                blurred_bgra[:, :, 1] = blurred_rgba[:, :, 1]  # G
                blurred_bgra[:, :, 2] = blurred_rgba[:, :, 0]  # R
                blurred_bgra[:, :, 3] = blurred_rgba[:, :, 3]  # A
                blurred_bgra = np.ascontiguousarray(blurred_bgra)
                
                blurred_surf = cairo.ImageSurface.create_for_data(blurred_bgra, cairo.FORMAT_ARGB32, w, h)
                pattern = cairo.SurfacePattern(blurred_surf)
                inv_matrix = ctx.get_matrix()
                inv_matrix.invert()
                pattern.set_matrix(inv_matrix)

                ctx.save()
                self._build_path(ctx, time)
                ctx.set_source(pattern)
                ctx.fill()
                ctx.restore()

        # 3. Base draw (Fill and directional stroke)
        super().draw(ctx, time)

        # 4. Top hairline specular highlight (Apple glass style)
        if self.specular_rim and bw > 10.0 and bh > 10.0:
            ctx.save()
            self._build_path(ctx, time)
            ctx.clip()
            
            # Subtle 1px inner top highlight
            pat = cairo.LinearGradient(bx, by, bx + bw, by)
            pat.add_color_stop_rgba(0.0, 1.0, 1.0, 1.0, 0.0)
            pat.add_color_stop_rgba(0.2, 1.0, 1.0, 1.0, 0.20)
            pat.add_color_stop_rgba(0.5, 1.0, 1.0, 1.0, 0.28)
            pat.add_color_stop_rgba(0.8, 1.0, 1.0, 1.0, 0.20)
            pat.add_color_stop_rgba(1.0, 1.0, 1.0, 1.0, 0.0)
            
            ctx.set_source(pat)
            ctx.set_line_width(1.5)
            ctx.move_to(bx + cr * 0.5, by + 1.0)
            ctx.line_to(bx + bw - cr * 0.5, by + 1.0)
            ctx.stroke()
            ctx.restore()

        # 5. Specular Gleam Sweep Pass
        gp = float(self.gleam_progress.get(time))
        if 0.0 <= gp <= 1.0:
            ctx.save()
            self._build_path(ctx, time)
            ctx.clip()

            diag = math.hypot(bw, bh)
            center_dist = gp * (bw + bh)
            angle = math.pi / 4.0  # 45 degrees
            
            # Calculate sweep gradient line
            lx1 = center_dist - 60.0
            ly1 = 0.0
            lx2 = center_dist + 60.0
            ly2 = 0.0
            
            # Rotate line by 45 deg
            rot_pat = cairo.LinearGradient(
                center_dist - 80.0, -40.0,
                center_dist + 80.0, bh + 40.0,
            )
            gc = self.gleam_color
            rot_pat.add_color_stop_rgba(0.0, gc.r, gc.g, gc.b, 0.0)
            rot_pat.add_color_stop_rgba(0.4, gc.r, gc.g, gc.b, 0.15)
            rot_pat.add_color_stop_rgba(0.5, gc.r, gc.g, gc.b, 0.45)  # Bright beam center
            rot_pat.add_color_stop_rgba(0.6, gc.r, gc.g, gc.b, 0.15)
            rot_pat.add_color_stop_rgba(1.0, gc.r, gc.g, gc.b, 0.0)

            ctx.set_source(rot_pat)
            ctx.paint_with_alpha(0.85)
            ctx.restore()

