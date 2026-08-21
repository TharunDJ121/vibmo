"""
Unit tests for multi-scene composition sequences, transitions, and layer mattes.
"""

import numpy as np
import pytest
from vibmo.scene.scene import Scene
from vibmo.composition.composition import Composition
from vibmo.composition.sequence import Sequence, CrossFade, Slide
from vibmo.compositing.graph import Precomp, AlphaMatte, LumaMatte, AdjustmentLayer
from vibmo.primitives.rect import Rect
from vibmo.primitives.circle import Circle
from vibmo.core.color import Color, colors
from vibmo.core.easing import Ease


def test_sequence_crossfade_and_slide():
    s1 = Scene(width=640, height=360, duration=2.0, background=colors.BLACK)
    s2 = Scene(width=640, height=360, duration=2.0, background=colors.WHITE)

    seq = Sequence(s1, s2, transition=CrossFade(duration=0.5))
    assert seq.total_duration == 3.5  # 2.0 + 2.0 - 0.5 transition overlap

    # The two scene frames must actually be blended during the overlap.
    frame = seq.render_frame(1.75)
    assert frame.shape == (360, 640, 4)
    assert frame.dtype == np.uint8
    assert 100 < frame[0, 0, 0] < 160

    seq_slide = Sequence(s1, s2, transition=Slide(duration=0.5, direction="left"))
    frame_slide = seq_slide.render_frame(1.8)
    assert frame_slide.shape == (360, 640, 4)


def test_composition_keeps_one_continuous_node_timeline():
    composition = Composition(width=640, height=360, duration=0.1)
    card = Rect(width=100, height=80, position=(0, 0))
    composition.add(card)

    with composition.shot("intro", duration=1.0):
        @composition.animate
        def intro():
            yield card.position.to((100, 0), duration=1.0, ease=Ease.linear)

    with composition.shot("reveal", duration=1.0):
        @composition.animate
        def reveal():
            yield card.position.to((200, 0), duration=1.0, ease=Ease.linear)

    assert composition.duration == 2.0
    assert card.position.get(1.0).x == 100.0
    assert card.position.get(1.5).x == 150.0
    assert composition.validate() == []


def test_mattes_and_adjustment_layer():
    target = Rect(width=300, height=200, fill=colors.CYAN)
    mask = Circle(radius=60, fill=colors.WHITE, position=(150, 100))

    alpha_matte = AlphaMatte(target=target, matte=mask)
    assert alpha_matte.target == target
    assert alpha_matte.matte == mask

    luma_matte = LumaMatte(target=target, matte=mask)
    assert luma_matte.target == target

    adj = AdjustmentLayer(tint=colors.INDIGO.with_alpha(0.3))
    assert adj.tint is not None
