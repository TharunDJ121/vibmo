"""
Turnkey Dark SaaS Magic Video Suite for Vibmo.
Inspired by video-production-skills dark-saas-magic-video.
Generates an 8-beat cinematic dark SaaS product launch promo in 1 line of code.
"""

from __future__ import annotations
from typing import Optional, Dict, Any, List

from vibmo.scene.scene import Scene
from vibmo.product.magic_ui.ui_dark_magic_stage import DarkStarfieldStage
from vibmo.product.magic_ui.ui_prompt_invocation_card import PromptInvocationCard
from vibmo.product.magic_ui.ui_model_orbit_ring import (
    ModelCapabilityOrbit,
    ExportBurstContainer,
    ConnectEcosystemSlot,
)


class TmplDarkSaasMagicSuite:
    """
    Turnkey generator for Presenton-style Dark SaaS Magic UI promo videos:
    Dark Starfield Stage + Purple Horizon + Prompt Invocation + Model Orbit + Export Burst.
    """

    @classmethod
    def build_scene(
        cls,
        product_name: str = "Vibmo Magic UI",
        prompt_text: str = "Generate high-converting SaaS product video in Python",
        models: Optional[List[str]] = None,
        duration: float = 6.0,
        fps: float = 60.0,
    ) -> Scene:
        scene = Scene(width=1920, height=1080, fps=fps, duration=duration)

        # 1. Background Stage
        stage = DarkStarfieldStage(particle_count=70)
        scene.add(stage)

        # 2. Hero Prompt Card
        card = PromptInvocationCard(
            prompt_text=prompt_text,
            cta_text="Generate Video ✨",
            position=(960.0, 480.0),
        )
        scene.add(card)

        # 3. Model Orbit Ring
        orbit = ModelCapabilityOrbit(
            center_title="MULTI-MODEL INTELLIGENCE",
            models=models or ["Claude 3.7", "GPT-4o", "DeepSeek R1", "Gemini 2.5"],
            position=(960.0, 520.0),
        )
        scene.add(orbit)

        # 4. Export Burst
        burst = ExportBurstContainer(
            headline="Universal Multi-Format Export",
            formats=["PDF", "Markdown", "MP4 60FPS", "REST API"],
            position=(960.0, 520.0),
        )
        scene.add(burst)

        @scene.animate
        def main():
            # Beat 1-3: Prompt Card Entry & Generation Trigger
            yield card.enter_card(duration=0.8)
            yield card.type_prompt(duration=1.4)
            yield card.click_cta(duration=0.5)

            # Beat 4-6: Multi-Model Orbit Expansion & Rotation
            yield orbit.open_ring(duration=0.8)
            yield orbit.rotate_orbit(revolutions=0.5, duration=1.2)

            # Beat 7-8: Export Burst Finale
            yield burst.trigger_burst(duration=1.0)
            yield scene.wait(0.5)

        return scene
