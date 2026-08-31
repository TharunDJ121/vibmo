"""
✦ Vibmo Turnkey: SaaS Changelog & Feature Release Video Suite
Inspired by Remocn changelog archetype for rapid product drop announcements.
"""

from __future__ import annotations

from typing import Any, List, Optional, Sequence, Union

from vibmo.scene.scene import Scene
from vibmo.core.color import Color, colors
from vibmo.core.easing import Ease
from vibmo.components.glass import GlassCard
from vibmo.typography.kinetic import KineticText
from vibmo.product.social import Badge
from vibmo.fx.backgrounds.bg_mesh_gradient_flow import MeshGradientFlow
from vibmo.fx.filters import Vignette, FilmGrain


class TmplChangelogReleaseSuite:
    """
    Turnkey template builder for software changelog and version release videos.
    """
    @classmethod
    def build_scene(
        cls,
        version: str = "v2.4.0",
        release_title: str = "Hardware Shaders & Interactive UI Simulators",
        features: Optional[List[str]] = None,
        duration: float = 5.0,
        **kwargs: Any,
    ) -> Scene:
        scene = Scene(
            width=1920,
            height=1080,
            fps=60,
            duration=duration,
            background=Color.hex("#06080e"),
        )

        # 1. Background & Post FX
        bg = MeshGradientFlow(
            width=1920,
            height=1080,
            colors=[Color.hex("#06080e"), Color.hex("#0b1220"), Color.hex("#13233c"), Color.hex("#04060a")],
            speed=0.4,
        )
        scene.add(bg)
        scene.add_post_fx(Vignette(intensity=0.2), FilmGrain(amount=0.01))

        # 2. Release Pill
        badge = Badge(text=f"RELEASE UPDATE ✦ {version}", color=colors.CYAN)
        badge.align("top_center", (1920, 1080)).at(780, 60)
        scene.add(badge)

        # 3. Main Title
        title = KineticText(
            f"<bold>{release_title}</bold>",
            font_size=42,
            color=colors.WHITE,
            align="center",
        ).align("top_center", (1920, 1080)).at(400, 120)
        scene.add(title)

        # 4. Feature Cards
        items = features if features else [
            "⚡ 23+ WebGL & Post-FX Shaders (ASCII, CCTV, Neural Noise)",
            "✦ 6-Beat Product Demo Video Spine & Archetypes",
            "🚀 Interactive Claude Code & SaaS UI Simulators",
            "📈 Mechanical Rolling Number Wheels & Decoders",
        ]

        card = GlassCard(
            direction="column",
            gap=18,
            padding=32,
            corner_radius=24,
            position=(480, 220),
            width=960,
        )
        for item in items:
            card.add(KineticText(item, font_size=18, color=colors.WHITE))
        scene.add(card)

        # 5. Footer Update Command
        footer = GlassCard(
            direction="row",
            gap=12,
            padding=(14, 24),
            corner_radius=14,
            position=(680, 780),
            align_items="center",
        )
        footer.add(KineticText("Install update:", font_size=15, color=Color.hex("#94a3b8")))
        footer.add(KineticText("<#22c55e>pip install --upgrade vibmo</#22c55e>", font_size=16, bold=True))
        scene.add(footer)

        @scene.animate
        def main():
            yield card.pop_in(duration=0.8)
            yield footer.pop_in(delay=0.2, duration=0.6)
            yield scene.wait(2.0)

        return scene
