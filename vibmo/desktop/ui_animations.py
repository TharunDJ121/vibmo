"""
Production-grade Qt UI animation utilities for Vibmo Desktop.
Provides smooth workspace transitions, micro-interactions, and feedback effects.
"""

from __future__ import annotations
from typing import Callable, Optional

from PySide6.QtCore import (
    QEasingCurve,
    QParallelAnimationGroup,
    QPropertyAnimation,
    QSequentialAnimationGroup,
    QAbstractAnimation,
)
from PySide6.QtWidgets import QGraphicsOpacityEffect, QStackedWidget, QWidget


def fade_widget(
    widget: QWidget,
    *,
    start: float = 0.0,
    end: float = 1.0,
    duration_ms: int = 180,
    on_finished: Optional[Callable[[], None]] = None,
) -> QPropertyAnimation:
    """Fade a widget in or out using an opacity effect."""
    effect = widget.graphicsEffect()
    if not isinstance(effect, QGraphicsOpacityEffect):
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)

    anim = QPropertyAnimation(effect, b"opacity", widget)
    anim.setDuration(duration_ms)
    anim.setStartValue(start)
    anim.setEndValue(end)
    anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    if on_finished:
        anim.finished.connect(on_finished)
    anim.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
    return anim


def animate_stack_switch(
    stack: QStackedWidget,
    new_index: int,
    *,
    duration_ms: int = 160,
) -> None:
    """Cross-fade between stacked workspace views."""
    if new_index == stack.currentIndex():
        return

    outgoing = stack.currentWidget()
    stack.setCurrentIndex(new_index)
    incoming = stack.currentWidget()

    if outgoing is not None:
        fade_widget(outgoing, start=1.0, end=0.72, duration_ms=duration_ms // 2)

    if incoming is not None:
        fade_widget(incoming, start=0.55, end=1.0, duration_ms=duration_ms)


def pulse_widget(widget: QWidget, *, duration_ms: int = 420) -> None:
    """Brief scale pulse for primary action feedback."""
    anim_out = QPropertyAnimation(widget, b"maximumHeight", widget)
    base_h = widget.maximumHeight() if widget.maximumHeight() > 0 else widget.height()
    anim_out.setDuration(duration_ms // 2)
    anim_out.setStartValue(base_h)
    anim_out.setEndValue(base_h + 2)
    anim_out.setEasingCurve(QEasingCurve.Type.OutQuad)

    anim_in = QPropertyAnimation(widget, b"maximumHeight", widget)
    anim_in.setDuration(duration_ms // 2)
    anim_in.setStartValue(base_h + 2)
    anim_in.setEndValue(base_h)
    anim_in.setEasingCurve(QEasingCurve.Type.InQuad)

    seq = QSequentialAnimationGroup(widget)
    seq.addAnimation(anim_out)
    seq.addAnimation(anim_in)
    seq.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)


def flash_accent(widget: QWidget, *, duration_ms: int = 300) -> None:
    """Quick opacity flash on a widget for success feedback."""
    fade_widget(widget, start=1.0, end=0.65, duration_ms=duration_ms // 2)
    fade_widget(widget, start=0.65, end=1.0, duration_ms=duration_ms // 2)


def stagger_fade_in(widgets: list[QWidget], *, stagger_ms: int = 40, duration_ms: int = 200) -> None:
    """Staggered entrance for lists of cards or panels."""
    group = QParallelAnimationGroup()
    for i, w in enumerate(widgets):
        effect = QGraphicsOpacityEffect(w)
        w.setGraphicsEffect(effect)
        effect.setOpacity(0.0)
        anim = QPropertyAnimation(effect, b"opacity", w)
        anim.setDuration(duration_ms)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        group.addAnimation(anim)
        # Stagger via pause in sequential wrapper per widget
        seq = QSequentialAnimationGroup()
        if i > 0:
            pause = QPropertyAnimation(w, b"minimumWidth", w)
            pause.setDuration(stagger_ms * i)
            pause.setStartValue(w.minimumWidth())
            pause.setEndValue(w.minimumWidth())
            seq.addAnimation(pause)
        seq.addAnimation(anim)
        seq.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
