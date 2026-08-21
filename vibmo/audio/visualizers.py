"""
Audio-Reactive visualizer nodes (Spectrum Equalizer Bars, Circular Radial Visualizers, Waveforms, Vinyl Disc).
"""

from __future__ import annotations
import math
import numpy as np
from typing import Any, List, Optional, Tuple, Union
import cairo

from vibmo.core.color import Color, colors
from vibmo.scene.node import Node
from vibmo.audio.track import AudioTrack
from vibmo.audio.analyzer import AudioAnalyzer


class SpectrumBars(Node):
    """Animated equalizer frequency bars reacting to audio in real time."""

    def __init__(
        self,
        audio: AudioTrack,
        bar_count: int = 32,
        width: float = 600.0,
        height: float = 120.0,
        bar_gap: float = 4.0,
        color: Optional[Union[Color, str]] = colors.INDIGO,
        corner_radius: float = 4.0,
        mirror: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.audio = audio
        self.analyzer = AudioAnalyzer(audio)
        self.bar_count = int(bar_count)
        self.width = float(width)
        self.height = float(height)
        self.bar_gap = float(bar_gap)
        self.corner_radius = float(corner_radius)
        self.mirror = mirror
        
        resolved_color = Color.from_any(color) if isinstance(color, (str, Color)) else color
        self.color = resolved_color or colors.INDIGO

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width, self.height)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        spec = self.analyzer.get_spectrum(time)
        if len(spec) == 0:
            return

        total_gaps = self.bar_gap * (self.bar_count - 1)
        bar_w = max(2.0, (self.width - total_gaps) / self.bar_count)

        indices = np.linspace(2, len(spec) - 1, self.bar_count, dtype=int)
        magnitudes = spec[indices]

        ctx.save()
        ctx.set_source_rgba(self.color.r, self.color.g, self.color.b, self.color.a)

        curr_x = 0.0
        for mag in magnitudes:
            bar_h = max(4.0, float(mag) * self.height)
            
            if self.mirror:
                bar_y = (self.height - bar_h) * 0.5
            else:
                bar_y = self.height - bar_h

            ctx.new_path()
            if self.corner_radius > 0:
                r = min(self.corner_radius, bar_w * 0.5, bar_h * 0.5)
                ctx.arc(curr_x + bar_w - r, bar_y + r, r, -math.pi * 0.5, 0)
                ctx.arc(curr_x + bar_w - r, bar_y + bar_h - r, r, 0, math.pi * 0.5)
                ctx.arc(curr_x + r, bar_y + bar_h - r, r, math.pi * 0.5, math.pi)
                ctx.arc(curr_x + r, bar_y + r, r, math.pi, math.pi * 1.5)
                ctx.close_path()
            else:
                ctx.rectangle(curr_x, bar_y, bar_w, bar_h)

            ctx.fill()
            curr_x += bar_w + self.bar_gap

        ctx.restore()


class CircularSpectrum(Node):
    """
    Radial 360-degree audio visualizer with outward radiating bars and color spectrum.
    """

    def __init__(
        self,
        audio: AudioTrack,
        radius: float = 180.0,
        bar_count: int = 64,
        max_bar_length: float = 140.0,
        bar_width: float = 4.0,
        colors_palette: Optional[List[Color]] = None,
        rotation_speed: float = 0.1,  # rotations per second
        mirror: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.audio = audio
        self.analyzer = AudioAnalyzer(audio)
        self.radius = float(radius)
        self.bar_count = int(bar_count)
        self.max_bar_length = float(max_bar_length)
        self.bar_width = float(bar_width)
        self.colors_palette = colors_palette or [
            colors.AMBER,
            colors.PINK,
            colors.PURPLE,
            colors.CYAN,
            colors.EMERALD,
        ]
        self.rotation_speed = float(rotation_speed)
        self.mirror = mirror

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        r_total = self.radius + self.max_bar_length
        return (-r_total, -r_total, r_total * 2, r_total * 2)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        spec = self.analyzer.get_spectrum(time)
        if len(spec) == 0:
            return

        # Sample frequency spectrum symmetrically
        half_count = self.bar_count // 2 if self.mirror else self.bar_count
        indices = np.linspace(2, len(spec) - 1, half_count, dtype=int)
        mags_half = spec[indices]
        
        if self.mirror:
            magnitudes = np.concatenate([mags_half, mags_half[::-1]])
        else:
            magnitudes = mags_half

        angle_step = (math.pi * 2) / len(magnitudes)
        base_rot = time * self.rotation_speed * math.pi * 2

        ctx.save()

        for i, mag in enumerate(magnitudes):
            angle = base_rot + i * angle_step
            bar_len = max(6.0, float(mag) * self.max_bar_length)

            # Color interpolation along the circle
            t_col = (i / len(magnitudes)) * (len(self.colors_palette) - 1)
            idx = int(t_col)
            frac = t_col - idx
            c1 = self.colors_palette[idx % len(self.colors_palette)]
            c2 = self.colors_palette[(idx + 1) % len(self.colors_palette)]
            
            r = c1.r + (c2.r - c1.r) * frac
            g = c1.g + (c2.g - c1.g) * frac
            b = c1.b + (c2.b - c1.b) * frac
            a = c1.a + (c2.a - c1.a) * frac

            ctx.save()
            ctx.rotate(angle)
            ctx.translate(self.radius, 0)

            # Draw rounded radial bar extending outwards
            ctx.set_source_rgba(r, g, b, a)
            
            bw = self.bar_width
            half_bw = bw * 0.5
            
            ctx.new_path()
            ctx.arc(bar_len - half_bw, 0, half_bw, -math.pi * 0.5, math.pi * 0.5)
            ctx.arc(half_bw, 0, half_bw, math.pi * 0.5, -math.pi * 0.5)
            ctx.close_path()
            ctx.fill()

            ctx.restore()

        ctx.restore()


class WaveformRibbon(Node):
    """Smooth dynamic waveform ribbon displaying actual audio wave fluctuations."""

    def __init__(
        self,
        audio: AudioTrack,
        width: float = 1200.0,
        height: float = 120.0,
        samples_count: int = 128,
        color: Optional[Union[Color, str]] = colors.CYAN,
        line_width: float = 3.0,
        glow: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.audio = audio
        self.width = float(width)
        self.height = float(height)
        self.samples_count = int(samples_count)
        self.color = Color.from_any(color) if isinstance(color, (str, Color)) else colors.CYAN
        self.line_width = float(line_width)
        self.glow = glow

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, -self.height * 0.5, self.width, self.height)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        if len(self.audio.samples) == 0:
            return

        sr = self.audio.sample_rate
        curr_idx = int(time * sr)
        window = int(0.04 * sr)  # 40ms window
        
        start = max(0, curr_idx - window // 2)
        end = min(len(self.audio.samples), start + window)
        chunk = self.audio.samples[start:end]
        
        if len(chunk) < 2:
            return

        # Subsample to smooth points
        step = max(1, len(chunk) // self.samples_count)
        sub_samples = chunk[::step]

        xs = np.linspace(0, self.width, len(sub_samples))
        ys = sub_samples * (self.height * 0.5)

        ctx.save()

        # Optional subtle ambient glow stroke
        if self.glow:
            ctx.set_source_rgba(self.color.r, self.color.g, self.color.b, 0.15)
            ctx.set_line_width(self.line_width * 3.5)
            self._trace_path(ctx, xs, ys)
            ctx.stroke()

        ctx.set_source_rgba(self.color.r, self.color.g, self.color.b, self.color.a)
        ctx.set_line_width(self.line_width)
        self._trace_path(ctx, xs, ys)
        ctx.stroke()

        ctx.restore()

    def _trace_path(self, ctx: Any, xs: np.ndarray, ys: np.ndarray) -> None:
        ctx.new_path()
        ctx.move_to(float(xs[0]), float(ys[0]))
        for x, y in zip(xs[1:], ys[1:]):
            ctx.line_to(float(x), float(y))


class VinylRecord(Node):
    """Stylized rotating vinyl disc with concentric grooves and customizable center label."""

    def __init__(
        self,
        radius: float = 160.0,
        groove_count: int = 12,
        disc_color: Optional[Union[Color, str]] = None,
        label_color: Optional[Union[Color, str]] = None,
        label_text: str = "MAAMADURA",
        sub_text: str = "SANTHOSH NARAYANAN",
        rotation_speed: float = 0.25,  # rotations per second
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.radius = float(radius)
        self.groove_count = int(groove_count)
        self.disc_color = Color.from_any(disc_color) if disc_color else Color(0.06, 0.07, 0.09, 1.0)
        self.label_color = Color.from_any(label_color) if label_color else colors.AMBER
        self.label_text = label_text
        self.sub_text = sub_text
        self.rotation_speed = float(rotation_speed)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (-self.radius, -self.radius, self.radius * 2, self.radius * 2)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        rot = time * self.rotation_speed * math.pi * 2

        ctx.save()
        ctx.rotate(rot)

        # 1. Vinyl Base Outer Disc
        ctx.set_source_rgba(self.disc_color.r, self.disc_color.g, self.disc_color.b, self.disc_color.a)
        ctx.arc(0, 0, self.radius, 0, math.pi * 2)
        ctx.fill()

        # 2. Vinyl Grooves (Concentric sheen rings)
        r_inner = self.radius * 0.42
        r_outer = self.radius * 0.95
        step_r = (r_outer - r_inner) / self.groove_count
        
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.04)
        ctx.set_line_width(1.0)
        for i in range(self.groove_count):
            r_cur = r_inner + i * step_r
            ctx.arc(0, 0, r_cur, 0, math.pi * 2)
            ctx.stroke()

        # 3. Outer Edge Highlight
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.12)
        ctx.set_line_width(2.0)
        ctx.arc(0, 0, self.radius - 1.0, 0, math.pi * 2)
        ctx.stroke()

        # 4. Center Label Circle
        label_r = self.radius * 0.38
        ctx.set_source_rgba(self.label_color.r, self.label_color.g, self.label_color.b, self.label_color.a)
        ctx.arc(0, 0, label_r, 0, math.pi * 2)
        ctx.fill()

        # Center Label Inner Ring
        ctx.set_source_rgba(0.0, 0.0, 0.0, 0.25)
        ctx.set_line_width(2.0)
        ctx.arc(0, 0, label_r * 0.85, 0, math.pi * 2)
        ctx.stroke()

        # Center Spindle Hole
        ctx.set_source_rgba(0.08, 0.08, 0.1, 1.0)
        ctx.arc(0, 0, self.radius * 0.06, 0, math.pi * 2)
        ctx.fill()

        # Center Label Typography
        ctx.set_source_rgba(0.08, 0.08, 0.1, 0.9)
        ctx.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(label_r * 0.22)
        
        extents = ctx.text_extents(self.label_text)
        ctx.move_to(-extents.width * 0.5, -label_r * 0.18)
        ctx.show_text(self.label_text)

        ctx.set_font_size(label_r * 0.14)
        extents2 = ctx.text_extents(self.sub_text)
        ctx.move_to(-extents2.width * 0.5, label_r * 0.32)
        ctx.show_text(self.sub_text)

        ctx.restore()


class AudioProgressBar(Node):
    """Interactive / animated progress scrubber showing current playback time and total track length."""

    def __init__(
        self,
        duration: float,
        width: float = 400.0,
        height: float = 6.0,
        color: Optional[Union[Color, str]] = colors.AMBER,
        bg_color: Optional[Union[Color, str]] = None,
        corner_radius: float = 3.0,
        show_time: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.track_duration = max(0.1, float(duration))
        self.width = float(width)
        self.height = float(height)
        self.color = Color.from_any(color) if isinstance(color, (str, Color)) else colors.AMBER
        self.bg_color = Color.from_any(bg_color) if bg_color else Color.WHITE.with_alpha(0.12)
        self.corner_radius = float(corner_radius)
        self.show_time = show_time

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width, self.height + (24.0 if self.show_time else 0.0))

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        progress = max(0.0, min(1.0, time / self.track_duration))
        fill_w = max(4.0, self.width * progress)

        ctx.save()

        # 1. Background Track
        ctx.set_source_rgba(self.bg_color.r, self.bg_color.g, self.bg_color.b, self.bg_color.a)
        self._rounded_rect(ctx, 0, 0, self.width, self.height, self.corner_radius)
        ctx.fill()

        # 2. Filled Progress Bar
        ctx.set_source_rgba(self.color.r, self.color.g, self.color.b, self.color.a)
        self._rounded_rect(ctx, 0, 0, fill_w, self.height, self.corner_radius)
        ctx.fill()

        # 3. Playhead scrubber knob
        ctx.arc(fill_w, self.height * 0.5, self.height * 1.3, 0, math.pi * 2)
        ctx.fill()

        # 4. Timestamps (e.g. 01:24 / 02:48)
        if self.show_time:
            ctx.set_source_rgba(1.0, 1.0, 1.0, 0.7)
            ctx.select_font_face("monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            ctx.set_font_size(14.0)

            cur_m, cur_s = divmod(int(time), 60)
            tot_m, tot_s = divmod(int(self.track_duration), 60)
            time_str = f"{cur_m:02d}:{cur_s:02d} / {tot_m:02d}:{tot_s:02d}"

            ctx.move_to(0, self.height + 20.0)
            ctx.show_text(time_str)

        ctx.restore()

    def _rounded_rect(self, ctx: Any, x: float, y: float, w: float, h: float, r: float) -> None:
        r = min(r, w * 0.5, h * 0.5)
        ctx.new_path()
        ctx.arc(x + w - r, y + r, r, -math.pi * 0.5, 0)
        ctx.arc(x + w - r, y + h - r, r, 0, math.pi * 0.5)
        ctx.arc(x + r, y + h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(x + r, y + r, r, math.pi, math.pi * 1.5)
        ctx.close_path()
