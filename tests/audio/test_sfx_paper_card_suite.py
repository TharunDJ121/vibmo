import numpy as np
from vibmo.audio.generators.sfx_paper_card_suite import PaperCardSuite

def test_card_shuffle_slide():
    duration = 0.22
    audio = PaperCardSuite.card_shuffle_slide(duration)

    # Check shape and type
    assert len(audio) == int(PaperCardSuite.SAMPLE_RATE * duration)
    assert audio.dtype == np.float32

    # Check range
    assert np.max(np.abs(audio)) <= 1.0 + 1e-6

    # Check start and end envelope (should be close to 0)
    assert abs(audio[0]) < 1e-3
    assert abs(audio[-1]) < 1e-3

def test_paper_flip_rustle():
    duration = 0.18
    audio = PaperCardSuite.paper_flip_rustle(duration)

    # Check shape and type
    assert len(audio) == int(PaperCardSuite.SAMPLE_RATE * duration)
    assert audio.dtype == np.float32

    # Check range
    assert np.max(np.abs(audio)) <= 1.0 + 1e-6

    # Check envelope start and end
    assert abs(audio[0]) < 1e-3
    assert abs(audio[-1]) < 1e-3

def test_sheet_unfold_crinkle():
    duration = 0.35
    audio = PaperCardSuite.sheet_unfold_crinkle(duration)

    # Check shape and type
    assert len(audio) == int(PaperCardSuite.SAMPLE_RATE * duration)
    assert audio.dtype == np.float32

    # Check range
    assert np.max(np.abs(audio)) <= 1.0 + 1e-6

    # Check fade in/out
    assert abs(audio[0]) < 1e-3
    assert abs(audio[-1]) < 1e-3

def test_deck_snap_slide():
    duration = 0.12
    audio = PaperCardSuite.deck_snap_slide(duration)

    # Check shape and type
    assert len(audio) == int(PaperCardSuite.SAMPLE_RATE * duration)
    assert audio.dtype == np.float32

    # Check range
    assert np.max(np.abs(audio)) <= 1.0 + 1e-6

    # Check envelope start and end
    assert abs(audio[0]) < 1e-3
    assert abs(audio[-1]) < 1e-3
