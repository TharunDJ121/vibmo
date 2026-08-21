"""
Vibmo Plugins & Extensibility System.
"""

from vibmo.plugins.registry import PluginRegistry, register_component, register_filter

__all__ = [
    "PluginRegistry",
    "register_component",
    "register_filter",
]
