import math
from typing import Any, Optional, Union
import cairo

from vibmo.core.color import Color, colors, LinearGradient
from vibmo.core.vector import Vector2D
from vibmo.core.signal import Signal
from vibmo.core.easing import Ease
from vibmo.scene.node import Node
from vibmo.layout.container import FlexContainer
from vibmo.primitives.rect import Rect
from vibmo.typography.text import Text

class DiffusionGenerationCanvas(Node):
    """
    Image viewport with progressive unblurring / denoising step counter (Step 18/25).
    """
    def __init__(
        self,
        width: float = 800.0,
        height: float = 800.0,
        total_steps: int = 25,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.width = Signal(width, f"{self.name}.width")
        self.height = Signal(height, f"{self.name}.height")
        self.total_steps = total_steps
        self.current_step = Signal(0.0, f"{self.name}.current_step")
        
        self.container = Rect(
            width=width,
            height=height,
            corner_radius=24.0,
            fill=colors.SLATE_900,
            stroke=colors.SLATE_700,
            stroke_width=2.0
        )
        
        # Overlay to simulate noise/blur decreasing opacity as steps progress
        self.noise_overlay = Rect(
            width=width,
            height=height,
            corner_radius=24.0,
            fill=Color.WHITE.with_alpha(0.8)
        )
        
        self.step_text = Text(
            text="Step 0/25",
            font_size=24.0,
            color=colors.WHITE,
            bold=True,
            align="center"
        )
        
        # Link step_text to current_step
        self.step_text.text.bind(lambda t: f"Step {int(self.current_step.get(t))}/{self.total_steps}")
        # Link noise overlay opacity to current_step
        self.noise_overlay.opacity.bind(lambda t: 1.0 - (self.current_step.get(t) / self.total_steps))
        
        self.add(self.container, self.noise_overlay, self.step_text)
        
    def local_bounds(self, time: float = 0.0) -> tuple[float, float, float, float]:
        return (0.0, 0.0, self.width.get(time), self.height.get(time))
        
    def compute_layout(self, time: float = 0.0):
        w = self.width.get(time)
        h = self.height.get(time)
        self.container.width.set(w)
        self.container.height.set(h)
        self.noise_overlay.width.set(w)
        self.noise_overlay.height.set(h)
        # Position text at the bottom left
        self.step_text.position.set(Vector2D(24.0, h - 48.0))
        
    def draw(self, ctx: Any, time: float = 0.0) -> None:
        self.compute_layout(time)
        super().draw(ctx, time)
        
    def denoise_to(self, target_step: int, duration: float = 2.0):
        return self.current_step.to(float(target_step), duration=duration, ease=Ease.linear)


class PromptAspectSelector(FlexContainer):
    """
    Segmented pill selector (1:1, 16:9, 9:16, 4:3) with smooth animated active indicator.
    """
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            direction="row",
            gap=8.0,
            padding=8.0,
            corner_radius=32.0,
            fill=colors.SLATE_900,
            stroke=colors.SLATE_700,
            stroke_width=1.0,
            **kwargs
        )
        self.aspect_ratios = ["1:1", "16:9", "9:16", "4:3"]
        self.active_index = Signal(0.0, f"{self.name}.active_index")
        
        # Indicator pill
        self.indicator = Rect(
            width=80.0,
            height=40.0,
            corner_radius=20.0,
            fill=colors.INDIGO
        )
        
        # We'll override compute_layout to move the indicator
        self.pills = []
        for aspect in self.aspect_ratios:
            pill = FlexContainer(
                width=80.0,
                height=40.0,
                justify_content="center",
                align_items="center"
            )
            text = Text(aspect, font_size=16.0, color=colors.WHITE, bold=True)
            pill.add(text)
            self.pills.append(pill)
            
        self.add(self.indicator)
        for pill in self.pills:
            self.add(pill)
            
    def compute_layout(self, time: float = 0.0):
        # Let parent arrange the pills
        # But we need to place the indicator based on active_index
        # Hide indicator from standard flex layout
        self.indicator.visible = False
        res = super().compute_layout(time)
        self.indicator.visible = True
        
        idx = self.active_index.get(time)
        base_idx = int(math.floor(idx))
        next_idx = min(len(self.pills) - 1, base_idx + 1)
        fraction = idx - base_idx
        
        if self.pills:
            # Interpolate position
            base_pos = self.pills[base_idx].position.get(time)
            next_pos = self.pills[next_idx].position.get(time)
            interp_pos = Vector2D(
                base_pos.x + (next_pos.x - base_pos.x) * fraction,
                base_pos.y + (next_pos.y - base_pos.y) * fraction
            )
            self.indicator.position.set(interp_pos)
            
        return res
        
    def select(self, index: int, duration: float = 0.4):
        index = max(0, min(len(self.aspect_ratios) - 1, index))
        return self.active_index.to(float(index), duration=duration, ease=Ease.in_out_cubic)


class SeedVariationPills(FlexContainer):
    """
    Row of 4 thumbnail variant cards with selection highlight border.
    """
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            direction="row",
            gap=16.0,
            padding=16.0,
            **kwargs
        )
        self.cards = []
        for i in range(4):
            card = Rect(
                width=100.0,
                height=100.0,
                corner_radius=16.0,
                fill=colors.SLATE_800,
                stroke=colors.SLATE_700,
                stroke_width=2.0
            )
            self.cards.append(card)
            self.add(card)
            
    def highlight(self, index: int, duration: float = 0.3):
        # We need to return an animation that highlights one card and un-highlights others
        from vibmo.timeline.scheduler import ParallelGroup
        anims = []
        for i, card in enumerate(self.cards):
            if i == index:
                anims.append(card.stroke.to(colors.INDIGO, duration=duration))
                anims.append(card.stroke_width.to(4.0, duration=duration))
            else:
                anims.append(card.stroke.to(colors.SLATE_700, duration=duration))
                anims.append(card.stroke_width.to(2.0, duration=duration))
        return ParallelGroup(anims)


class MagicPromptEnhanceBar(FlexContainer):
    """
    Shimmering iridescent text input field with "Enhance Prompt" sparkles button.
    """
    def __init__(self, **kwargs: Any) -> None:
        self.gradient = LinearGradient(
            start=(0.0, 0.5), end=(1.0, 0.5),
            stops=[
                (0.0, Color.hex("#a855f7")),
                (0.5, Color.hex("#3b82f6")),
                (1.0, Color.hex("#a855f7"))
            ]
        )
        super().__init__(
            direction="row",
            gap=16.0,
            padding=16.0,
            corner_radius=32.0,
            fill=colors.SLATE_950,
            stroke=self.gradient,
            stroke_width=2.0,
            align_items="center",
            **kwargs
        )
        
        self.text_input = Text(
            text="cyberpunk city scape neon lights",
            font_size=18.0,
            color=colors.SLATE_400
        )
        
        self.button = FlexContainer(
            direction="row",
            padding=(10.0, 20.0),
            corner_radius=20.0,
            fill=self.gradient,
            align_items="center"
        )
        # Usually we would use Icon("lucide:sparkles"), but using Text to avoid missing imports
        btn_text = Text("Enhance", font_size=16.0, color=colors.WHITE, bold=True)
        self.button.add(btn_text)
        
        self.add(self.text_input, self.button)
        
    def shimmer(self, duration: float = 1.0):
        # Simulate shimmer by moving the gradient stops or something similar,
        # but gradient animation might require custom signal logic.
        # For now, let's just animate scale or opacity slightly as a shim.
        from vibmo.timeline.scheduler import SequentialGroup
        return SequentialGroup([
            self.button.scale.to(Vector2D(1.05, 1.05), duration=duration * 0.5),
            self.button.scale.to(Vector2D(1.0, 1.0), duration=duration * 0.5)
        ])

