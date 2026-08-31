"""
API Key Vault & Secrets Management UI Suite for Vibmo / Motio.
Components:
- ApiKeyVault (ApiKeyVaultCard)
- KeySecretRow
- MaskedTokenRevealField
- CopyClipboardPill
- RevokeConfirmModal
"""

from __future__ import annotations
import math
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
import cairo

from vibmo.core.color import Color, colors
from vibmo.core.vector import Vector2D
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.scene.node import Node
from vibmo.components.glass import GlassCard
from vibmo.spatial.shadows import DropShadow


class MaskedTokenRevealField(Node):
    """Field that animates unmasking secret tokens (`sk-live-••••••••` -> `sk-live-a89f...`)."""

    def __init__(
        self,
        clear_text: str = "sk-live-a1b2c3d4e5f6g7h8i9j0k1l2m3",
        masked_text: str = "sk-live-••••••••••••••••••••••••",
        width: float = 280.0,
        height: float = 36.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.clear_text = clear_text
        self.masked_text = masked_text
        self.width_val = float(width)
        self.height_val = float(height)
        self.reveal_progress = Signal(0.0, f"{self.name}.reveal_progress")

    def trigger_reveal(self, duration: float = 0.6, ease: EasingFunc = Ease.in_out_quad) -> AnimationAction:
        return self.reveal_progress.to(1.0, duration=duration, ease=ease)

    def trigger_hide(self, duration: float = 0.6, ease: EasingFunc = Ease.in_out_quad) -> AnimationAction:
        return self.reveal_progress.to(0.0, duration=duration, ease=ease)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        prog = max(0.0, min(1.0, self.reveal_progress.get(time)))

        ctx.save()
        r = 6.0
        ctx.new_path()
        ctx.arc(w - r, r, r, -math.pi * 0.5, 0)
        ctx.arc(w - r, h - r, r, 0, math.pi * 0.5)
        ctx.arc(r, h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(r, r, r, math.pi, math.pi * 1.5)
        ctx.close_path()

        ctx.set_source_rgba(0.05, 0.07, 0.12, 0.95)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.18, 0.25, 0.35, 0.6)
        ctx.set_line_width(1.0)
        ctx.stroke()

        # Render characters with partial reveal
        num_chars = len(self.clear_text)
        revealed_count = int(prog * num_chars)
        displayed = self.clear_text[:revealed_count] + self.masked_text[revealed_count:]

        ctx.select_font_face("Consolas", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(11.0)
        ctx.set_source_rgba(0.2, 0.85, 1.0, 0.95 if prog > 0.5 else 0.7)
        ctx.move_to(10.0, 22.0)
        ctx.show_text(displayed[:32])
        ctx.restore()


class CopyClipboardPill(Node):
    """Interactive button that pulses and displays 'Copied!' toast on trigger."""

    def __init__(self, width: float = 65.0, height: float = 32.0, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.width_val = float(width)
        self.height_val = float(height)
        self.copy_progress = Signal(0.0, f"{self.name}.copy_progress")
        self.copied_signal = self.copy_progress
        self.is_copied = self.copy_progress

    def trigger_copy(self, duration: float = 0.5, ease: EasingFunc = Ease.out_quad) -> AnimationAction:
        return self.copy_progress.to(1.0, duration=duration, ease=ease)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        is_copied = self.copied_signal.get(time) > 0.5

        ctx.save()
        r = 6.0
        ctx.new_path()
        ctx.arc(w - r, r, r, -math.pi * 0.5, 0)
        ctx.arc(w - r, h - r, r, 0, math.pi * 0.5)
        ctx.arc(r, h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(r, r, r, math.pi, math.pi * 1.5)
        ctx.close_path()

        if is_copied:
            ctx.set_source_rgba(0.08, 0.3, 0.18, 0.9)
            ctx.fill_preserve()
            ctx.set_source_rgba(0.1, 0.85, 0.45, 0.9)
            ctx.stroke()
            text = "Copied"
            text_color = (0.2, 1.0, 0.5, 1.0)
        else:
            ctx.set_source_rgba(0.12, 0.16, 0.24, 0.85)
            ctx.fill_preserve()
            ctx.set_source_rgba(0.25, 0.35, 0.5, 0.6)
            ctx.stroke()
            text = "Copy"
            text_color = (0.8, 0.9, 1.0, 0.9)

        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(11.0)
        ctx.set_source_rgba(*text_color)
        ext = ctx.text_extents(text)
        ctx.move_to((w - ext.width) * 0.5, h * 0.5 + ext.height * 0.35)
        ctx.show_text(text)
        ctx.restore()


class RevokeConfirmModal(Node):
    """Modal dialog asking user to confirm API key revoking with red button glow."""

    def __init__(self, key_name: str = "Production API Key", width: float = 320.0, height: float = 140.0, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.key_name = key_name
        self.width_val = float(width)
        self.height_val = float(height)
        self.opacity = Signal(0.0, f"{self.name}.opacity")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        op = max(0.0, min(1.0, self.opacity.get(time)))
        if op <= 0.0:
            return

        w, h = self.width_val, self.height_val
        ctx.save()
        r = 12.0
        ctx.new_path()
        ctx.arc(w - r, r, r, -math.pi * 0.5, 0)
        ctx.arc(w - r, h - r, r, 0, math.pi * 0.5)
        ctx.arc(r, h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(r, r, r, math.pi, math.pi * 1.5)
        ctx.close_path()

        ctx.set_source_rgba(0.12, 0.04, 0.06, 0.98 * op)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.9, 0.2, 0.3, 0.8 * op)
        ctx.set_line_width(1.5)
        ctx.stroke()

    """Revocation security modal overlay with confirmation actions."""

    def __init__(self, key_name: str = "Production API Key", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.key_name = key_name
        self.width_val = 320.0
        self.height_val = 140.0
        self.opacity = Signal(1.0, f"{self.name}.opacity")

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        ctx.save()
        r = 10.0
        if hasattr(ctx, "new_path"):
            ctx.new_path()
        if hasattr(ctx, "arc"):
            ctx.arc(w - r, r, r, -math.pi * 0.5, 0)
            ctx.arc(w - r, h - r, r, 0, math.pi * 0.5)
            ctx.arc(r, h - r, r, math.pi * 0.5, math.pi)
            ctx.arc(r, r, r, math.pi, math.pi * 1.5)
        if hasattr(ctx, "close_path"):
            ctx.close_path()

        ctx.set_source_rgba(0.18, 0.06, 0.08, 0.95)
        if hasattr(ctx, "fill_preserve"):
            ctx.fill_preserve()
        else:
            ctx.fill()
        ctx.set_source_rgba(0.85, 0.2, 0.3, 0.8)
        if hasattr(ctx, "set_line_width"):
            ctx.set_line_width(1.0)
        ctx.stroke()
        ctx.restore()


class KeySecretRow(Node):
    """Single API key row item with secret masking, metadata, and controls."""

    def __init__(
        self,
        name: str = "Production Key",
        clear_text: str = "sk-live-000000000000000000",
        created_at: str = "recently",
        width: float = 670.0,
        height: float = 54.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.name_str = name
        self.clear_text = clear_text
        self.created_at = created_at
        self.width_val = float(width)
        self.height_val = float(height)

        # Masked field
        self.reveal_field = MaskedTokenRevealField(clear_text=clear_text, width=320.0, height=32.0)
        self.reveal_field.position.set(Vector2D(200.0, 11.0))
        self.add(self.reveal_field)

        # Copy button
        self.copy_btn = CopyClipboardPill()
        self.copy_btn.position.set(Vector2D(self.width_val - 76.0, 14.0))
        self.add(self.copy_btn)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        ctx.save()

        # Row background
        r = 8.0
        if hasattr(ctx, "new_path"):
            ctx.new_path()
        if hasattr(ctx, "arc"):
            ctx.arc(w - r, r, r, -math.pi * 0.5, 0)
            ctx.arc(w - r, h - r, r, 0, math.pi * 0.5)
            ctx.arc(r, h - r, r, math.pi * 0.5, math.pi)
            ctx.arc(r, r, r, math.pi, math.pi * 1.5)
        if hasattr(ctx, "close_path"):
            ctx.close_path()

        ctx.set_source_rgba(0.06, 0.09, 0.14, 0.9)
        if hasattr(ctx, "fill_preserve"):
            ctx.fill_preserve()
        else:
            ctx.fill()
        ctx.set_source_rgba(0.18, 0.24, 0.35, 0.5)
        if hasattr(ctx, "set_line_width"):
            ctx.set_line_width(1.0)
        ctx.stroke()

        # Key Name
        if hasattr(ctx, "select_font_face"):
            ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        if hasattr(ctx, "set_font_size"):
            ctx.set_font_size(12.5)
        ctx.set_source_rgba(0.9, 0.95, 1.0, 0.95)
        ctx.move_to(16.0, 24.0)
        if hasattr(ctx, "show_text"):
            ctx.show_text(self.name_str)

        # Created timestamp
        if hasattr(ctx, "set_font_size"):
            ctx.set_font_size(10.0)
        ctx.set_source_rgba(0.5, 0.6, 0.7, 0.8)
        ctx.move_to(16.0, 42.0)
        if hasattr(ctx, "show_text"):
            ctx.show_text(f"Created {self.created_at}")

        # Status badge (Active)
        if hasattr(ctx, "arc"):
            ctx.arc(580.0, 27.0, 4.0, 0, 2 * math.pi)
        ctx.set_source_rgba(0.1, 0.85, 0.45, 0.95)
        ctx.fill()

        super().draw(ctx, time)
        ctx.restore()


class ApiKeyVault(Node):
    """
    API Key Vault & Security Credentials Suite.
    Manages cryptographic secret tokens, masked string reveals, copy actions,
    and revocation confirmation modals.
    """

    def __init__(
        self,
        keys: Optional[Union[List[Dict[str, Any]], List[str]]] = None,
        key_name: str = "Production AI Router",
        width: float = 720.0,
        height: float = 460.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.key_name = key_name
        self.width_val = float(width)
        self.height_val = float(height)
        self.shadow = DropShadow(color=Color(0.0, 0.0, 0.0, 0.5), blur=32.0, offset=(0.0, 16.0))

        raw_keys = keys or [
            {"name": "Production Core API", "clear_text": "sk-live-94a8f12c6e73b092da15e98b", "created": "Yesterday"},
            {"name": "Development Staging", "clear_text": "sk-test-47bc1890a23ef45d61081a29", "created": "3 days ago"},
            {"name": "CI/CD Deployment Bot", "clear_text": "sk-ci-0021ff893bca4198ee124588", "created": "1 week ago"},
        ]

        self.rows: List[KeySecretRow] = []
        for i, k_data in enumerate(raw_keys):
            if isinstance(k_data, str):
                name = f"Key {i+1}"
                clear_text = k_data
                created = "recently"
            else:
                name = k_data.get("name", f"Key {i+1}")
                clear_text = k_data.get("clear_text", "sk-live-000000000000000000")
                created = k_data.get("created", "recently")
            row = KeySecretRow(
                name=name,
                clear_text=clear_text,
                created_at=created,
                width=self.width_val - 48.0,
            )
            row.position.set(Vector2D(24.0, 80.0 + i * 66.0))
            self.add(row)
            self.rows.append(row)

    def reveal_key(self, index: int = 1, duration: float = 0.6) -> AnimationAction:
        """
        Fluent generator animation verb to trigger unmasking token characters.
        """
        idx = max(0, min(len(self.rows) - 1, index))
        return self.rows[idx].reveal_field.trigger_reveal(duration=duration)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w, h = self.width_val, self.height_val
        ctx.save()

        # Card container
        r = 16.0
        ctx.new_path()
        ctx.arc(w - r, r, r, -math.pi * 0.5, 0)
        ctx.arc(w - r, h - r, r, 0, math.pi * 0.5)
        ctx.arc(r, h - r, r, math.pi * 0.5, math.pi)
        ctx.arc(r, r, r, math.pi, math.pi * 1.5)
        ctx.close_path()

        ctx.set_source_rgba(0.04, 0.06, 0.1, 0.95)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.18, 0.25, 0.38, 0.8)
        ctx.set_line_width(1.5)
        ctx.stroke()

        # Title
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(15.0)
        ctx.set_source_rgba(0.95, 0.98, 1.0, 0.95)
        ctx.move_to(24.0, 42.0)
        ctx.show_text("API Keys & Secret Credentials Vault")

        # Subtitle
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(11.0)
        ctx.set_source_rgba(0.5, 0.6, 0.75, 0.8)
        ctx.move_to(24.0, 60.0)
        ctx.show_text("Secure encrypted storage for LLM inference keys")

        super().draw(ctx, time)
        ctx.restore()


ApiKeyVaultCard = ApiKeyVault
