"""
Turnkey Fintech & Crypto Card Motion Graphics Template Suite.
"""

from __future__ import annotations
from typing import Any, Optional, Sequence, Union
import math

from vibmo.scene.scene import Scene
from vibmo.core.color import Color, LinearGradient, colors
from vibmo.core.easing import Ease
from vibmo.components.glass import GlassCard
from vibmo.components.counter import MetricCounter
from vibmo.typography.kinetic import KineticText
from vibmo.product.social import Badge
from vibmo.physics.particles import ParticleEmitter
from vibmo.fx.backgrounds.bg_mesh_gradient_flow import MeshGradientFlow
from vibmo.fx.filters import Bloom, FilmGrain, Vignette


class FintechCryptoCardTemplate:
    """
    Broadcast-quality 3D holographic crypto/fintech card showcase scene builder.
    """

    @classmethod
    def create_scene(
        cls,
        cardholder: str = "SATOSHI NAKAMOTO",
        balance: float = 148500.0,
        currency: str = "USD",
        card_number: str = "•••• •••• •••• 4242",
        network: str = "APEX TITANIUM",
        duration: float = 6.0,
        **kwargs: Any,
    ) -> Scene:
        scene = Scene(
            width=1920,
            height=1080,
            fps=60,
            duration=duration,
            background=Color.hex("#050811"),
        )

        # 1. Background Mesh Gradient
        bg = MeshGradientFlow(
            width=1920,
            height=1080,
            colors=[Color.hex("#050811"), Color.hex("#0d1b2a"), Color.hex("#1b263b"), Color.hex("#000814")],
            speed=0.5,
        )
        scene.add(bg)

        # 2. Cinematic Post-Processing
        scene.add_post_fx(
            Bloom(threshold=0.7, intensity=0.35, radius=24.0),
            Vignette(intensity=0.3),
            FilmGrain(amount=0.01),
        )

        # 3. Heading / Header
        header = KineticText(
            f"<bold>✦ {network.upper()} CRYPTO VAULT</bold>",
            font_size=36,
            color=colors.WHITE,
            align="center",
        ).align("top_center", (1920, 1080)).at(560, 80)
        scene.add(header)

        # 4. Premium Crypto Debit Card
        card_stroke = LinearGradient(
            start=(0.0, 0.0),
            end=(1.0, 1.0),
            stops=[(0.0, Color.hex("#00f5d4")), (0.5, Color.hex("#7b2cbf")), (1.0, Color.hex("#f72585"))],
        )

        card = GlassCard(
            direction="column",
            gap=28,
            padding=36,
            width=680,
            height=420,
            corner_radius=28,
            fill=Color.hex("#0c1020").with_alpha(0.75),
            stroke=card_stroke,
            stroke_width=2.5,
            glow=True,
            specular_rim=True,
        ).align("center", (1920, 1080)).at(620, 310)

        # Top row of card: Chip & Network
        top_row = GlassCard(
            direction="row",
            gap=300,
            padding=0,
            width=600,
            fill=Color.TRANSPARENT,
            stroke=None,
            shadow=False,
            specular_rim=False,
        )
        chip_badge = Badge(text="EMV ◈ CHIP", color=Color.hex("#e0a96d"))
        network_badge = Badge(text="SOLANA ACTIVE", color=colors.CYAN)
        top_row.add(chip_badge, network_badge)

        # Middle row: Card Number
        num_text = KineticText(
            f"<mono>{card_number}</mono>",
            font_size=32,
            color=colors.WHITE,
            bold=True,
        )

        # Bottom row: Cardholder Name + Balance MetricCounter
        bottom_row = GlassCard(
            direction="row",
            gap=120,
            padding=0,
            width=600,
            fill=Color.TRANSPARENT,
            stroke=None,
            shadow=False,
            specular_rim=False,
        )

        holder_col = GlassCard(
            direction="column",
            gap=4,
            padding=0,
            fill=Color.TRANSPARENT,
            stroke=None,
            shadow=False,
            specular_rim=False,
        )
        holder_label = KineticText("<#94a3b8>CARDHOLDER</#94a3b8>", font_size=12, bold=True)
        holder_val = KineticText(f"<bold>{cardholder.upper()}</bold>", font_size=18, color=colors.WHITE)
        holder_col.add(holder_label, holder_val)

        bal_col = GlassCard(
            direction="column",
            gap=4,
            padding=0,
            fill=Color.TRANSPARENT,
            stroke=None,
            shadow=False,
            specular_rim=False,
        )
        bal_label = KineticText("<#94a3b8>VAULT BALANCE</#94a3b8>", font_size=12, bold=True)
        bal_counter = MetricCounter(
            start_val=0,
            end_val=balance,
            prefix="$" if currency == "USD" else f"{currency} ",
            font_size=28,
            bold=True,
            color=colors.EMERALD,
        )
        bal_col.add(bal_label, bal_counter)

        bottom_row.add(holder_col, bal_col)

        card.add(top_row, num_text, bottom_row)
        scene.add(card)

        # 5. Ambient Sparkle Particles
        sparkles = ParticleEmitter(preset="sparkles", position=(960, 540))
        scene.add(sparkles)

        # 6. Choreography
        @scene.animate
        def script():
            scene.add_sfx("whoosh", 0.0)
            yield scene.all(
                *header.reveal_characters(stagger=0.02, duration=0.8),
                *card.pop_in(delay=0.1, duration=0.9),
            )

            scene.add_sfx("pop", 0.9)
            yield scene.all(
                *card.tilt_3d(pitch=0.12, yaw=-0.18, duration=1.4),
                card.gleam(duration=1.4, delay=0.1),
                bal_counter.count_to(duration=1.6, ease=Ease.out_expo),
            )

            card.float_idle(amplitude=8, speed=1.1)
            yield scene.wait(1.5)

        return scene


class TmplFintechCryptoCardSuite(FintechCryptoCardTemplate):
    """
    Turnkey Production Suite for Fintech and Crypto Card motion graphics.
    """

    @classmethod
    def build_scene(
        cls,
        cardholder: str = "SATOSHI NAKAMOTO",
        balance: float = 148500.0,
        currency: str = "USD",
        card_number: Optional[str] = None,
        network: str = "APEX TITANIUM",
        duration: float = 6.0,
        **kwargs: Any,
    ) -> Scene:
        """
        Builds and returns a fully configured crypto card scene.
        """
        if card_number is None:
            card_number = kwargs.pop("number", "•••• •••• •••• 4242")
        return cls.create_scene(
            cardholder=cardholder,
            balance=balance,
            currency=currency,
            card_number=card_number,
            network=network,
            duration=duration,
            **kwargs,
        )


__all__ = [
    "FintechCryptoCardTemplate",
    "TmplFintechCryptoCardSuite",
]
