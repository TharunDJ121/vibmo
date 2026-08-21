"""
Asset management, font loader, vector icons, gradients, advanced video nodes, and asset browser.
"""

from vibmo.assets.asset import Asset, ImageNode
from vibmo.assets.video import VideoNode, VideoClip
from vibmo.assets.library import (
    AssetLibrary,
    AssetMetadata,
    AssetType,
    AssetCategory,
    get_asset_library,
    create_gradient_preset,
    get_popular_gradients,
    get_asset_preview_url,
)
from vibmo.assets.icons import BuiltinIcon, Icon, ICON_REGISTRY
from vibmo.assets.gradients import Gradients, GRADIENT_PRESETS
from vibmo.assets.video_advanced import AdvancedVideoNode
from vibmo.studio.asset_browser import AssetBrowser, get_asset_browser, BrowserFilter

__all__ = [
    "Asset",
    "ImageNode",
    "VideoNode",
    "VideoClip",
    "AdvancedVideoNode",
    # Icons & Gradients
    "BuiltinIcon",
    "Icon",
    "ICON_REGISTRY",
    "Gradients",
    "GRADIENT_PRESETS",
    # Asset library & Browser
    "AssetLibrary",
    "AssetMetadata",
    "AssetType",
    "AssetCategory",
    "get_asset_library",
    "create_gradient_preset",
    "get_popular_gradients",
    "get_asset_preview_url",
    "AssetBrowser",
    "get_asset_browser",
    "BrowserFilter",
]
