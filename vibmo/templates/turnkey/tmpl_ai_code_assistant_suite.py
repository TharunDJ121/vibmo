from __future__ import annotations
from typing import Any
from vibmo.scene.scene import Scene
from vibmo.core.color import Color, colors
from vibmo.core.easing import Ease
from vibmo.product.mockups import BrowserWindow
from vibmo.components.glass import GlassCard
from vibmo.components.code import CodeWindow
from vibmo.components.counter import MetricCounter
from vibmo.product.social import Badge
from vibmo.physics.particles import ParticleEmitter
from vibmo.product.ai.ui_token_streamer_suite import TokenStreamerBox


class AiCodeAssistantTemplate:
    @classmethod
    def create_scene(
        cls,
        title: str = "AI Code Assistant",
        code_snippet: str = "print('Hello world!')",
        duration: float = 6.0,
    ) -> Scene:
        scene = Scene(
            width=1920,
            height=1080,
            fps=60,
            duration=duration,
            background=colors.SLATE_950,
        )

        # Add ambient particles to the background (subtle ambient dust)
        particles = ParticleEmitter(preset="ambient_dust", position=(960, 540))
        scene.add(particles)

        # Stage 1: Entrance of BrowserWindow IDE containing CodeWindow and GlassCard.
        browser = BrowserWindow(url="https://ide.agent.ai", title=title, width=1400, height=820)
        browser.align("center", (1920, 1080)).at(260, 130)

        ide_layout = GlassCard(direction="row", gap=40, padding=24, width=1320, height=720)

        # Stage 2: Code window and TokenStreamerBox
        code_win = CodeWindow(code="", title="main.py", font_size=20, width=640, height=670)
        token_box = TokenStreamerBox(width=600, height=670)

        ide_layout.add(code_win, token_box)
        browser.add_content(ide_layout)
        scene.add(browser)

        # Stage 3: Instant execution with green checkmark test pass pill.
        pill = Badge(text="Test Passed \u2713", color=colors.EMERALD)
        # Position pill over the code window, initially scaled to 0.001 to prevent non-invertible matrix
        pill.position.set((300, 300))
        pill.scale.set((0.001, 0.001))
        scene.add(pill)

        # Stage 4: Celebration milestone with MetricCounter
        counter = MetricCounter(start_val=0, end_val=100, suffix="% Pass Rate", color=colors.EMERALD, font_size=48)
        counter.position.set((300, 400))
        counter.scale.set((0.001, 0.001))
        scene.add(counter)

        @scene.animate
        def script():
            # Stage 1: Entrance
            yield scene.all(
                browser.pop_in(duration=1.0)
            )

            # Stage 2: Realtime code autocompletion and token typing
            yield token_box.stream_text(code_snippet, duration=2.0)

            # Stage 3: Instant execution pill
            yield pill.scale.to((1.0, 1.0), duration=0.5, ease=Ease.out_back)

            # Stage 4: Celebration milestone counter
            yield scene.all(
                counter.scale.to((1.0, 1.0), duration=0.5, ease=Ease.out_back),
                counter.count_to(duration=1.0, ease=Ease.out_expo),
            )

            yield scene.wait(1.0)

        return scene


class TmplAiCodeAssistantSuite(AiCodeAssistantTemplate):
    @classmethod
    def build_scene(cls, **kwargs: Any) -> Scene:
        return cls.create_scene(
            title=kwargs.get("title", "AI Code Assistant"),
            code_snippet=kwargs.get("prompt", kwargs.get("code", "def solve():\n    return True")),
            duration=float(kwargs.get("duration", 6.0)),
        )


__all__ = [
    "AiCodeAssistantTemplate",
    "TmplAiCodeAssistantSuite",
]
