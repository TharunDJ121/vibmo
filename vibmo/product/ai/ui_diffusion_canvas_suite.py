"""
Diffusion Canvas AI UI Suite for Vibmo / Motio.
Components:
- DiffusionCanvas (DiffusionGenerationCanvas)
- DenoisingProgress
- PromptAspectSelector
- SeedVariationPills
- MagicPromptEnhanceBar
"""

from __future__ import annotations
import math
import random
from typing import Any, List, Optional, Sequence, Tuple, Union
import cairo

from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.scene.node import Node
from vibmo.layout.container import FlexContainer
from vibmo.primitives.rect import Rect, RoundedRect
from vibmo.typography.text import Text
from vibmo.spatial.shadows import DropShadow


class DenoisingProgress(Node):
    """Progress indicator showing current step, total steps, and noise reduction ratio."""

    def __init__(
        self,
        current_step: Union[float, Signal] = 0.0,
        total_steps: int = 25,
        width: float = 240.0,
        height: float = 48.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.total_steps = int(total_steps)
        self.width_val = float(width)
        self.height_val = float(height)
        self.step_signal = current_step if isinstance(current_step, Signal) else Signal(float(current_step), f"{self.name}.step")

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        step = max(0.0, min(float(self.total_steps), self.step_signal.get(time)))
        fraction = step / max(1, self.total_steps)

        ctx.save()
        # Container
        r = 10.0
        ctx.new_path()
        ctx.arc(w - r, r, r, -math.pi * 0.5, 0)
        ctx.arc(w - r, h - r, r, 0, math.pi * 0.5)
        ctx.arc(r, h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(r, r, r, math.pi, math.pi * 1.5)
        ctx.close_path()

        ctx.set_source_rgba(0.06, 0.08, 0.14, 0.9)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.2, 0.3, 0.45, 0.6)
        ctx.set_line_width(1.0)
        ctx.stroke()

        # Step Text
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(12.0)
        ctx.set_source_rgba(0.9, 0.95, 1.0, 0.95)
        ctx.move_to(14.0, 22.0)
        ctx.show_text(f"Step {int(step)} / {self.total_steps}")

        # Percentage
        pct_text = f"{int(fraction * 100)}%"
        ext = ctx.text_extents(pct_text)
        ctx.move_to(w - ext.width - 14.0, 22.0)
        ctx.set_source_rgba(0.3, 0.8, 1.0, 0.95)
        ctx.show_text(pct_text)

        # Progress bar track
        bar_x = 14.0
        bar_y = 32.0
        bar_w = w - 28.0
        bar_h = 6.0
        br = 3.0

        ctx.new_path()
        ctx.arc(bar_x + bar_w - br, bar_y + br, br, -math.pi * 0.5, math.pi * 0.5)
        ctx.arc(bar_x + br, bar_y + br, br, math.pi * 0.5, math.pi * 1.5)
        ctx.close_path()
        ctx.set_source_rgba(0.15, 0.2, 0.3, 0.8)
        ctx.fill()

        # Progress fill
        fill_w = max(br * 2.0, bar_w * fraction)
        ctx.new_path()
        ctx.arc(bar_x + fill_w - br, bar_y + br, br, -math.pi * 0.5, math.pi * 0.5)
        ctx.arc(bar_x + br, bar_y + br, br, math.pi * 0.5, math.pi * 1.5)
        ctx.close_path()
        ctx.set_source_rgba(0.2, 0.7, 1.0, 0.95)
        ctx.fill()

        ctx.restore()


class DiffusionCanvas(Node):
    """
    Diffusion Generation Canvas Suite.
    Renders generative diffusion model progress with dynamic noise dissolution,
    aspect ratio selectors, seed variations, and prompt enhancement.
    """

    def __init__(
        self,
        prompt: str = "A futuristic cyberpunk metropolis at twilight, ultra-detailed raytraced reflections",
        total_steps: int = 25,
        width: float = 640.0,
        height: float = 540.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.prompt = prompt
        self.total_steps = int(total_steps)
        self.width_val = float(width)
        self.height_val = float(height)
        self.shadow = DropShadow(color=Color(0.0, 0.0, 0.0, 0.5), blur=32.0, offset=(0.0, 16.0))

        # Signals
        self.current_step = Signal(0.0, f"{self.name}.current_step")
        self.noise_alpha = Signal(1.0, f"{self.name}.noise_alpha")

        # Subcomponents
        self.progress_bar = DenoisingProgress(current_step=self.current_step, total_steps=self.total_steps)
        self.progress_bar.position.set(Vector2D(self.width_val - 260.0, 20.0))
        self.add(self.progress_bar)

    def denoise_steps(
        self,
        steps: int = 20,
        duration: float = 2.0,
        ease: EasingFunc = Ease.out_quad,
    ) -> AnimationAction:
        """
        Fluent generator animation verb to step through denoising iterations.
        """
        target = float(min(self.total_steps, max(1, steps)))
        self.noise_alpha.to(max(0.05, 1.0 - (target / self.total_steps)), duration=duration, ease=ease)
        return self.current_step.to(target, duration=duration, ease=ease)

    def denoise_to(self, target_step: int, duration: float = 2.0) -> AnimationAction:
        return self.denoise_steps(steps=target_step, duration=duration)

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

        ctx.set_source_rgba(0.05, 0.07, 0.12, 0.95)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.18, 0.25, 0.38, 0.8)
        ctx.set_line_width(1.5)
        ctx.stroke()

        # Header Title
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(14.0)
        ctx.set_source_rgba(0.9, 0.95, 1.0, 0.9)
        ctx.move_to(24.0, 36.0)
        ctx.show_text("Latent Diffusion Generation")

        # Viewport Preview Area
        vw = w - 48.0
        vh = h - 160.0
        vx = 24.0
        vy = 80.0
        vr = 12.0

        ctx.new_path()
        ctx.arc(vx + vw - vr, vy + vr, vr, -math.pi * 0.5, 0)
        ctx.arc(vx + vw - vr, vy + vh - vr, vr, 0, math.pi * 0.5)
        ctx.arc(vx + vr, vy + vh - vr, vr, math.pi * 0.5, math.pi)
        ctx.arc(vx + vr, vy + vr, vr, math.pi, math.pi * 1.5)
        ctx.close_path()
        ctx.clip()

        # Render generative artwork background gradient
        step_val = self.current_step.get(time)
        clarity = min(1.0, step_val / max(1, self.total_steps))

        # Base generative colors
        pat = cairo.LinearGradient(vx, vy, vx + vw, vy + vh)
        pat.add_color_stop_rgba(0.0, 0.15 * clarity + 0.05, 0.1 * clarity + 0.05, 0.35 * clarity + 0.1, 1.0)
        pat.add_color_stop_rgba(0.5, 0.4 * clarity + 0.1, 0.15 * clarity + 0.05, 0.5 * clarity + 0.1, 1.0)
        pat.add_color_stop_rgba(1.0, 0.1 * clarity + 0.05, 0.4 * clarity + 0.1, 0.6 * clarity + 0.15, 1.0)
        ctx.set_source(pat)
        ctx.paint()

        # Procedural latent shapes forming
        if clarity > 0.1:
            ctx.set_source_rgba(0.3, 0.8, 1.0, 0.3 * clarity)
            ctx.arc(vx + vw * 0.5, vy + vh * 0.5, 90.0 * clarity, 0, 2 * math.pi)
            ctx.fill()

            ctx.set_source_rgba(0.9, 0.4, 0.7, 0.25 * clarity)
            ctx.arc(vx + vw * 0.35, vy + vh * 0.4, 60.0 * clarity, 0, 2 * math.pi)
            ctx.fill()

        # Simulated Gaussian Noise Overlay based on remaining steps
        noise_amount = max(0.0, 1.0 - clarity)
        if noise_amount > 0.02:
            rng = random.Random(42 + int(time * 30))
            for _ in range(int(300 * noise_amount)):
                nx = vx + rng.random() * vw
                ny = vy + rng.random() * vh
                nr = 1.0 + rng.random() * 2.5
                ctx.set_source_rgba(0.8, 0.9, 1.0, rng.random() * 0.35 * noise_amount)
                ctx.arc(nx, ny, nr, 0, 2 * math.pi)
                ctx.fill()

        ctx.reset_clip()

        # Prompt caption bar at bottom
        py = h - 60.0
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(12.0)
        ctx.set_source_rgba(0.7, 0.8, 0.9, 0.85)
        ctx.move_to(24.0, py)
        prompt_preview = f'Prompt: "{self.prompt[:60]}..."'
        ctx.show_text(prompt_preview)

        # Draw subcomponents (progress bar, etc.)
        super().draw(ctx, time)
        ctx.restore()


DiffusionGenerationCanvas = DiffusionCanvas


class PromptAspectSelector(FlexContainer):
    """Segmented pill selector (1:1, 16:9, 9:16, 4:3) with smooth active indicator."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            direction="row",
            gap=8.0,
            padding=8.0,
            corner_radius=24.0,
            fill=colors.SLATE_900,
            stroke=colors.SLATE_700,
            stroke_width=1.0,
            **kwargs,
        )
        self.aspect_ratios = ["1:1", "16:9", "9:16", "4:3"]
        self.active_index = Signal(0.0, f"{self.name}.active_index")

        for aspect in self.aspect_ratios:
            pill = FlexContainer(
                direction="row",
                padding=(6, 14),
                corner_radius=16.0,
                fill=colors.SLATE_800,
                align_items="center",
                justify_content="center",
            )
            text = Text(aspect, font_size=13.0, color=colors.SLATE_50, bold=True)
            pill.add(text)
            self.add(pill)

    def select(self, index: int, duration: float = 0.4) -> AnimationAction:
        idx = max(0, min(len(self.aspect_ratios) - 1, index))
        return self.active_index.to(float(idx), duration=duration, ease=Ease.in_out_cubic)


class SeedVariationPills(FlexContainer):
    """Row of 4 thumbnail variant cards with selection highlight border."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            direction="row",
            gap=12.0,
            padding=12.0,
            corner_radius=16.0,
            fill=colors.SLATE_900,
            stroke=colors.SLATE_700,
            **kwargs,
        )
        self.cards: List[Rect] = []
        for i in range(4):
            card = Rect(
                width=64.0,
                height=64.0,
                corner_radius=10.0,
                fill=Color(0.12, 0.16, 0.24, 0.9),
                stroke=colors.SLATE_700,
                stroke_width=1.5,
            )
            self.cards.append(card)
            self.add(card)

    def highlight(self, index: int, duration: float = 0.3) -> List[AnimationAction]:
        actions = []
        for i, card in enumerate(self.cards):
            if i == index:
                actions.append(card.stroke.to(colors.CYAN, duration=duration))
                actions.append(card.stroke_width.to(3.0, duration=duration))
            else:
                actions.append(card.stroke.to(colors.SLATE_700, duration=duration))
                actions.append(card.stroke_width.to(1.5, duration=duration))
        return actions


class MagicPromptEnhanceBar(FlexContainer):
    """Iridescent prompt input field with 'Enhance Prompt' button."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            direction="row",
            gap=12.0,
            padding=(10.0, 16.0),
            corner_radius=20.0,
            fill=colors.SLATE_950,
            stroke=colors.INDIGO_500,
            stroke_width=1.5,
            align_items="center",
            **kwargs,
        )
        self.text_input = Text(
            text="cyberpunk metropolis neon volumetric fog 8k",
            font_size=14.0,
            color=colors.SLATE_200,
        )
        self.btn = FlexContainer(
            direction="row",
            padding=(6, 12),
            corner_radius=12.0,
            fill=colors.INDIGO_600,
            align_items="center",
        )
        self.btn.add(Text("✨ Enhance", font_size=12.0, color=colors.WHITE, bold=True))
        self.add(self.text_input, self.btn)
