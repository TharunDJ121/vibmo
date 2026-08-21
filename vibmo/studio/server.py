"""
Backwards-compatibility shim for vibmo.studio.server.
All implementation has moved to modular files in vibmo.studio.
"""

from vibmo.studio.router import create_studio_app, launch_studio

__all__ = [
    "create_studio_app",
    "launch_studio",
]
