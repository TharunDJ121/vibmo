"""
Compositing Blend Modes for Photoshop / After Effects / DaVinci Resolve parity.
"""

from __future__ import annotations
from enum import Enum
from typing import Any, Union
import cairo


class BlendMode(str, Enum):
    """Supported 2D and 3D layer blend modes."""
    NORMAL = "normal"
    MULTIPLY = "multiply"
    SCREEN = "screen"
    OVERLAY = "overlay"
    DARKEN = "darken"
    LIGHTEN = "lighten"
    COLOR_DODGE = "color_dodge"
    COLOR_BURN = "color_burn"
    HARD_LIGHT = "hard_light"
    SOFT_LIGHT = "soft_light"
    DIFFERENCE = "difference"
    EXCLUSION = "exclusion"
    HUE = "hue"
    SATURATION = "saturation"
    COLOR = "color"
    LUMINOSITY = "luminosity"
    ADD = "add"
    SUBTRACT = "subtract"


_CAIRO_OPERATORS = {
    BlendMode.NORMAL: cairo.OPERATOR_OVER,
    BlendMode.MULTIPLY: cairo.OPERATOR_MULTIPLY,
    BlendMode.SCREEN: cairo.OPERATOR_SCREEN,
    BlendMode.OVERLAY: cairo.OPERATOR_OVERLAY,
    BlendMode.DARKEN: cairo.OPERATOR_DARKEN,
    BlendMode.LIGHTEN: cairo.OPERATOR_LIGHTEN,
    BlendMode.COLOR_DODGE: cairo.OPERATOR_COLOR_DODGE,
    BlendMode.COLOR_BURN: cairo.OPERATOR_COLOR_BURN,
    BlendMode.HARD_LIGHT: cairo.OPERATOR_HARD_LIGHT,
    BlendMode.SOFT_LIGHT: cairo.OPERATOR_SOFT_LIGHT,
    BlendMode.DIFFERENCE: cairo.OPERATOR_DIFFERENCE,
    BlendMode.EXCLUSION: cairo.OPERATOR_EXCLUSION,
    BlendMode.HUE: cairo.OPERATOR_HSL_HUE,
    BlendMode.SATURATION: cairo.OPERATOR_HSL_SATURATION,
    BlendMode.COLOR: cairo.OPERATOR_HSL_COLOR,
    BlendMode.LUMINOSITY: cairo.OPERATOR_HSL_LUMINOSITY,
    BlendMode.ADD: cairo.OPERATOR_ADD,
    "normal": cairo.OPERATOR_OVER,
    "multiply": cairo.OPERATOR_MULTIPLY,
    "screen": cairo.OPERATOR_SCREEN,
    "overlay": cairo.OPERATOR_OVERLAY,
    "darken": cairo.OPERATOR_DARKEN,
    "lighten": cairo.OPERATOR_LIGHTEN,
    "color_dodge": cairo.OPERATOR_COLOR_DODGE,
    "color_burn": cairo.OPERATOR_COLOR_BURN,
    "hard_light": cairo.OPERATOR_HARD_LIGHT,
    "soft_light": cairo.OPERATOR_SOFT_LIGHT,
    "difference": cairo.OPERATOR_DIFFERENCE,
    "exclusion": cairo.OPERATOR_EXCLUSION,
    "hue": cairo.OPERATOR_HSL_HUE,
    "saturation": cairo.OPERATOR_HSL_SATURATION,
    "color": cairo.OPERATOR_HSL_COLOR,
    "luminosity": cairo.OPERATOR_HSL_LUMINOSITY,
    "add": cairo.OPERATOR_ADD,
}


def get_cairo_operator(blend_mode: Union[BlendMode, str]) -> Any:
    """Maps a BlendMode enum or string to corresponding PyCairo Operator."""
    mode_key = blend_mode.value if isinstance(blend_mode, BlendMode) else str(blend_mode).lower()
    return _CAIRO_OPERATORS.get(mode_key, cairo.OPERATOR_OVER)
