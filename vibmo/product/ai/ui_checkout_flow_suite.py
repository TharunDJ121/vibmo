"""
✦ Vibmo AI Suites: Interactive SaaS Checkout Flow
Inspired by Remocn checkout-flow with interactive credit card validation and payment state transitions.
"""

from __future__ import annotations

import math
from typing import Any, List, Optional, Tuple, Union
import cairo

from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease
from vibmo.scene.node import Node
from vibmo.layout.container import FlexContainer
from vibmo.typography.text import Text
from vibmo.spatial.shadows import DropShadow
from vibmo.timeline.scheduler import all as sched_all, sequence as sched_seq


class InteractiveCheckoutFlow(FlexContainer):
    """
    SaaS payment & checkout card with live card number validation, spinner, and success state.
    """
    def __init__(
        self,
        amount: str = "$99.00 / year",
        plan_name: str = "Pro Builder Tier",
        card_number: str = "4242  ••••  ••••  4242",
        expiry: str = "12 / 28",
        cvc: str = "•••",
        width: float = 460.0,
        **kwargs: Any,
    ):
        super().__init__(
            direction="column",
            padding=(24, 28),
            gap=18,
            corner_radius=20.0,
            fill=Color(0.08, 0.1, 0.14, 0.98),
            stroke=Color(0.2, 0.25, 0.35, 0.8),
            stroke_width=1.0,
            shadow=DropShadow(color=Color(0, 0, 0, 0.4), blur=28.0, offset=(0, 12)),
            **kwargs,
        )
        self.amount = amount
        self.plan_name = plan_name
        self.card_number = card_number
        self.expiry = expiry
        self.cvc = cvc

        # State Signals (0: Idle/Typing, 1: Processing/Spinning, 2: Success)
        self.payment_state = Signal(0.0, f"{self.name}.payment_state")
        self.type_progress = Signal(0.0, f"{self.name}.type_progress")

        # 1. Header: Plan Title & Amount
        hdr = FlexContainer(direction="row", justify="between", align_items="center")
        hdr.add(Text(text=plan_name, font_size=18.0, font_family="Inter", color=colors.WHITE, bold=True))
        hdr.add(Text(text=amount, font_size=18.0, font_family="Inter", color=colors.EMERALD, bold=True))
        self.add(hdr)

        # 2. Card Number Input Box
        self.card_input_box = FlexContainer(
            direction="row",
            padding=(12, 16),
            gap=10,
            corner_radius=10.0,
            fill=Color(0.12, 0.15, 0.22, 1.0),
            stroke=Color(0.25, 0.35, 0.5, 0.8),
            stroke_width=1.0,
            align_items="center",
        )
        self.card_text = Text(
            text="💳  " + card_number,
            font_size=15.0,
            font_family="monospace",
            color=Color(0.9, 0.95, 1.0, 1.0),
            bold=True,
        )
        self.card_input_box.add(self.card_text)
        self.add(self.card_input_box)

        # 3. Row: Expiry & CVC
        row = FlexContainer(direction="row", gap=12)
        exp_box = FlexContainer(
            direction="row",
            padding=(10, 14),
            corner_radius=8.0,
            fill=Color(0.12, 0.15, 0.22, 1.0),
            stroke=Color(0.22, 0.28, 0.4, 0.7),
            stroke_width=1.0,
        )
        exp_box.add(Text(text=f"Exp: {expiry}", font_size=13.0, font_family="monospace", color=Color(0.7, 0.75, 0.85, 1.0)))
        row.add(exp_box)

        cvc_box = FlexContainer(
            direction="row",
            padding=(10, 14),
            corner_radius=8.0,
            fill=Color(0.12, 0.15, 0.22, 1.0),
            stroke=Color(0.22, 0.28, 0.4, 0.7),
            stroke_width=1.0,
        )
        cvc_box.add(Text(text=f"CVC: {cvc}", font_size=13.0, font_family="monospace", color=Color(0.7, 0.75, 0.85, 1.0)))
        row.add(cvc_box)
        self.add(row)

        # 4. Pay Button
        self.pay_btn = FlexContainer(
            direction="row",
            padding=(14, 20),
            gap=8,
            corner_radius=12.0,
            fill=colors.EMERALD,
            justify="center",
            align_items="center",
        )
        self.btn_text = Text(
            text=f"Pay {amount}",
            font_size=16.0,
            font_family="Inter",
            color=Color(0.02, 0.15, 0.08, 1.0),
            bold=True,
        )
        self.pay_btn.add(self.btn_text)
        self.add(self.pay_btn)

    def trigger_payment(self, duration: float = 2.0) -> AnimationAction:
        """Transitions state: Idle (0) -> Processing (1) -> Succeeded (2)."""
        return sched_seq(
            self.payment_state.to(1.0, duration=0.1),
            self.payment_state.to(2.0, duration=duration, ease=Ease.out_expo),
        )

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        state = self.payment_state.get(time)
        if state >= 1.5:
            # Payment Succeeded State
            self.pay_btn.fill.set(Color(0.1, 0.8, 0.4, 1.0))
            self.btn_text.text.set("✓  Payment Successful")
            self.btn_text.color.set(Color(0.02, 0.15, 0.08, 1.0))
        elif state >= 0.5:
            # Processing Spinner State
            spin_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
            char = spin_chars[int(time * 12) % len(spin_chars)]
            self.pay_btn.fill.set(Color(0.2, 0.3, 0.4, 1.0))
            self.btn_text.text.set(f"{char}  Processing Payment...")
            self.btn_text.color.set(colors.WHITE)
        else:
            self.pay_btn.fill.set(colors.EMERALD)
            self.btn_text.text.set(f"Pay {self.amount}")

        super().draw(ctx, time)


class PaymentCreditCardField(InteractiveCheckoutFlow):
    """Alias for InteractiveCheckoutFlow."""
    pass
