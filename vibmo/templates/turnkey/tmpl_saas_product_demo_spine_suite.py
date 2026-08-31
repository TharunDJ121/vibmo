"""
✦ Vibmo Turnkey: 6-Beat Product Demo Video Spine & Archetype Suite
Inspired by Remocn product-demo archetype and the 6-beat spine:
Hook -> Positioning -> Product Reveal -> Features -> Proof -> CTA.
"""

from __future__ import annotations

from typing import Any, List, Optional, Sequence, Union
import math

from vibmo.scene.scene import Scene
from vibmo.core.color import Color, colors
from vibmo.core.easing import Ease
from vibmo.components.glass import GlassCard
from vibmo.components.counter import MetricCounter
from vibmo.typography.kinetic import KineticText
from vibmo.typography.kinetic.typo_blur_out_up_suite import BlurOutUpText
from vibmo.typography.kinetic.typo_inline_pill_takeover import InlinePillTakeoverText
from vibmo.product.ai.ui_ai_prompt_flow_suite import AiPromptFlow
from vibmo.product.ai.ui_social_follow_card_suite import XFollowCard
from vibmo.product.social import Badge
from vibmo.fx.backgrounds.bg_mesh_gradient_flow import MeshGradientFlow
from vibmo.fx.filters import Vignette, FilmGrain


class ProductDemoSpine:
    """
    Spine data structure holding the 6 standard narrative beats of a high-converting product demo.
    """
    def __init__(
        self,
        hook: str = "Traditional video editing takes hours of manual work",
        product_name: str = "Vibmo",
        tagline: str = "The AI-Agent Native Motion Design Framework",
        hero_prompt: str = "Generate an interactive SaaS launch video with live telemetry HUD",
        hero_response: str = "Assembled 6-beat product spine with WebGL shaders and spring physics in 0.4s",
        features: Optional[List[str]] = None,
        proof_metric: str = "120,000+ videos rendered",
        cta_url: str = "pip install vibmo && vibmo studio",
    ):
        self.hook = hook
        self.product_name = product_name
        self.tagline = tagline
        self.hero_prompt = hero_prompt
        self.hero_response = hero_response
        self.features = features if features else [
            "✦ Zero-Boilerplate God Import",
            "⚡ Hardware-Accelerated Shaders",
            "📈 45+ Financial & KPI Charts",
        ]
        self.proof_metric = proof_metric
        self.cta_url = cta_url


class TmplSaasProductDemoSpineSuite:
    """
    Turnkey builder that produces a broadcast-quality 6-beat product demo video scene.
    """
    @classmethod
    def build_scene(
        cls,
        spine: Optional[ProductDemoSpine] = None,
        duration: float = 6.0,
        accent_color: Color = colors.CYAN,
        **kwargs: Any,
    ) -> Scene:
        sp = spine if spine else ProductDemoSpine()

        scene = Scene(
            width=1920,
            height=1080,
            fps=60,
            duration=duration,
            background=Color.hex("#070a12"),
        )

        # 1. Mesh Gradient Backdrop
        bg = MeshGradientFlow(
            width=1920,
            height=1080,
            colors=[Color.hex("#070a12"), Color.hex("#0c1527"), Color.hex("#112240"), Color.hex("#050811")],
            speed=0.5,
        )
        scene.add(bg)

        # 2. Cinematic Post-Processing
        scene.add_post_fx(
            Vignette(intensity=0.22),
            FilmGrain(amount=0.012),
        )

        # Beat 1 & 2: Hook & Positioning Header Badge
        header_pill = Badge(text=f"✦ {sp.product_name.upper()} // PRODUCT LAUNCH", color=accent_color)
        header_pill.align("top_center", (1920, 1080)).at(760, 50)
        scene.add(header_pill)

        # Title Lockup
        title = KineticText(
            f"<bold>{sp.product_name}</bold>: {sp.tagline}",
            font_size=34,
            color=colors.WHITE,
            align="center",
        ).align("top_center", (1920, 1080)).at(480, 105)
        scene.add(title)

        # Beat 3: Hero Product Surface (AI Prompt Flow)
        hero_flow = AiPromptFlow(
            prompt_text=sp.hero_prompt,
            response_text=sp.hero_response,
            model_name="Claude 3.7 Sonnet",
            attachment="architecture.json",
        )
        hero_flow.position.set((240, 180))
        scene.add(hero_flow)

        # Beat 4: Features Showcase Card
        feat_card = GlassCard(
            direction="column",
            gap=14,
            padding=24,
            corner_radius=20,
            position=(1100, 180),
        )
        feat_card.add(KineticText("<bold>Core Capabilities</bold>", font_size=20, color=accent_color))
        for feat in sp.features:
            feat_card.add(KineticText(feat, font_size=15, color=colors.WHITE))
        scene.add(feat_card)

        # Beat 5: Proof Metric Counter
        proof_card = GlassCard(
            direction="column",
            gap=10,
            padding=24,
            corner_radius=20,
            position=(1100, 390),
        )
        proof_card.add(KineticText("<#94a3b8>PRODUCTION METRIC</#94a3b8>", font_size=13, bold=True))
        counter = MetricCounter(
            start_val=0,
            end_val=120000,
            prefix="",
            suffix=" videos",
            font_size=36,
            color=colors.EMERALD,
            bold=True,
        )
        proof_card.add(counter)
        proof_card.add(KineticText("Rendered by solo founders & devs", font_size=13, color=Color.hex("#94a3b8")))
        scene.add(proof_card)

        # Beat 6: CTA Bottom Banner
        cta_card = GlassCard(
            direction="row",
            gap=16,
            padding=(16, 28),
            corner_radius=16,
            position=(480, 880),
            align_items="center",
            justify="center",
        )
        cta_card.add(KineticText("🚀 Get Started:", font_size=18, color=colors.WHITE, bold=True))
        cta_card.add(KineticText(f"<#06b6d4>{sp.cta_url}</#06b6d4>", font_size=17, bold=True))
        scene.add(cta_card)

        # Animation Choreography
        @scene.animate
        def main():
            # Staggered pop-in
            yield scene.all(
                hero_flow.pop_in(duration=0.8),
                feat_card.pop_in(delay=0.15, duration=0.8),
                proof_card.pop_in(delay=0.3, duration=0.8),
                cta_card.pop_in(delay=0.45, duration=0.8),
            )
            # Interactive actions
            yield scene.all(
                hero_flow.type_prompt(duration=1.4),
                counter.count_to(duration=1.8, ease=Ease.out_expo),
            )
            yield hero_flow.stream_response(duration=1.6)
            yield scene.wait(1.0)

        return scene
