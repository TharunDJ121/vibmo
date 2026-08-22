import pytest
from unittest.mock import MagicMock
import cairo

from vibmo.product.ai.ui_api_key_vault_suite import (
    MaskedTokenRevealField,
    CopyClipboardPill,
    ApiKeyVaultCard,
    RevokeConfirmModal
)

def test_masked_token_reveal_field():
    field = MaskedTokenRevealField()
    assert field.reveal_progress.get() == 0.0
    
    # Check default masking
    field.trigger_reveal(duration=1.0)
    assert field.reveal_progress.get() == 0.0
    field.reveal_progress.set(1.0) # simulate animation finish
    assert field.reveal_progress.get() == 1.0
    
    # Draw check
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 500, 100)
    ctx = cairo.Context(surface)
    
    field.reveal_progress.set(0.0)
    field.draw(ctx, time=0.0)
    field.reveal_progress.set(0.5)
    field.draw(ctx, time=0.5)
    field.reveal_progress.set(1.0)
    field.draw(ctx, time=1.0)


def test_copy_clipboard_pill():
    pill = CopyClipboardPill()
    assert pill.copy_progress.get() == 0.0
    
    pill.trigger_copy(duration=0.5)
    pill.copy_progress.set(1.0)
    assert pill.copy_progress.get() == 1.0
    
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 200, 100)
    ctx = cairo.Context(surface)
    
    pill.copy_progress.set(0.0)
    pill.draw(ctx, time=0.0)
    pill.copy_progress.set(0.6)
    pill.draw(ctx, time=0.6)


def test_api_key_vault_card():
    card = ApiKeyVaultCard()
    assert card.key_name == "Production AI Router"
    
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 800, 400)
    ctx = cairo.Context(surface)
    card.draw(ctx, time=0.0)


def test_revoke_confirm_modal():
    modal = RevokeConfirmModal()
    
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 600, 400)
    ctx = cairo.Context(surface)
    modal.draw(ctx, time=0.0)
