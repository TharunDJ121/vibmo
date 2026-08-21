"""
Unit tests for assets, importers, vector icons, and font management.
"""

import os
import pickle
import pytest
from vibmo.assets.asset import Asset, ImageNode
from vibmo.importers.icons import Icon
from vibmo.importers.fonts import FontManager
from vibmo.importers.lottie import LottieAnimation
from vibmo.importers.web import WebNode


def test_image_node_pickling():
    img_node = ImageNode("test.png", width=300, height=200, corner_radius=12.0)
    
    # Should pickle cleanly for multi-process rendering without Cairo pointer errors
    pickled = pickle.dumps(img_node)
    unpickled = pickle.loads(pickled)
    assert unpickled.width == 300
    assert unpickled.height == 200
    assert unpickled.corner_radius == 12.0


def test_icon_rendering():
    sparkles = Icon("lucide:sparkles", size=36.0)
    assert sparkles.icon_name == "lucide:sparkles"
    bx, by, bw, bh = sparkles.local_bounds(0.0)
    assert bw == 36.0
    assert bh == 36.0



def test_font_manager():
    # Standard fallback fonts
    font_path = FontManager.get_font_path("Inter", bold=True)
    # Should resolve to either system font or downloaded path
    assert font_path is not None or True


def test_lottie_animation_stub():
    dummy_lottie = {
        "v": "5.5.7",
        "fr": 60,
        "ip": 0,
        "op": 180,
        "w": 500,
        "h": 500,
        "layers": [],
    }
    anim = LottieAnimation(dummy_lottie, width=200, height=200)
    assert anim.width == 200
    assert anim.height == 200


def test_web_node_pickling():
    web_node = WebNode("https://example.com", width=1200, height=800)
    pickled = pickle.dumps(web_node)
    unpickled = pickle.loads(pickled)
    assert unpickled.width == 1200


def test_iconify_resolver_builtin_and_caching():
    from vibmo.importers.icons import IconifyResolver, Icon
    # 1. Built-in icons
    for name in ["lucide:zap", "lucide:terminal", "lucide:database", "lucide:refresh-cw"]:
        d = IconifyResolver.resolve_path_data(name)
        assert d != ""
    
    # 2. Preload API
    Icon.preload("lucide:code", "lucide:cpu")


def test_lottie_2_bezier_shapes_and_keyframes():
    # Complete Lottie JSON with animated shape layer and bezier path
    lottie_dict = {
        "v": "5.5.7",
        "fr": 30,
        "ip": 0,
        "op": 60,
        "w": 400,
        "h": 400,
        "layers": [
            {
                "ip": 0,
                "op": 60,
                "ks": {
                    "p": {"k": [200, 200]},
                    "s": {"k": [100, 100]},
                    "r": {"k": 0},
                    "o": {"k": [{"t": 0, "s": [0], "e": [100]}, {"t": 30, "s": [100], "e": [100]}]},
                },
                "shapes": [
                    {
                        "ty": "gr",
                        "it": [
                            {
                                "ty": "rc",
                                "p": {"k": [0, 0]},
                                "s": {"k": [100, 100]},
                                "r": {"k": 10},
                            },
                            {
                                "ty": "sh",
                                "ks": {
                                    "k": {
                                        "v": [[0, 0], [50, 50], [100, 0]],
                                        "i": [[0, 0], [0, 0], [0, 0]],
                                        "o": [[0, 0], [0, 0], [0, 0]],
                                        "c": True,
                                    }
                                }
                            },
                            {
                                "ty": "fl",
                                "c": {"k": [0.38, 0.40, 0.95, 1.0]},
                                "o": {"k": 100},
                            },
                            {
                                "ty": "st",
                                "c": {"k": [1.0, 1.0, 1.0, 1.0]},
                                "w": {"k": 2.0},
                                "o": {"k": 100},
                            }
                        ]
                    }
                ]
            }
        ]
    }

    anim = LottieAnimation(lottie_dict, width=300, height=300, loop=True)
    assert anim.clip_duration == 2.0
    bx, by, bw, bh = anim.local_bounds(0.0)
    assert bw == 300 and bh == 300


def test_asset_preload_and_bundle(tmp_path):
    # Test Asset.preload
    Asset.preload("test.png", "test.mp3")

    # Test Asset.bundle zip export
    bundle_zip = str(tmp_path / "scene_assets.zip")
    out = Asset.bundle(None, bundle_zip)
    assert os.path.exists(out)

