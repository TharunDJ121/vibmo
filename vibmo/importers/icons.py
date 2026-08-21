"""
Vector Icon resolver and node renderer with Iconify API integration (200,000+ icons) and offline caching.
"""

from __future__ import annotations
import os
import re
import urllib.request
import json
import tempfile
from typing import Any, Dict, List, Optional, Tuple, Union
import cairo

from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal
from vibmo.scene.node import Node
from vibmo.primitives.path import Path

# Built-in SVG path dictionaries for instant offline rendering of popular UI icons
BUILTIN_ICONS: Dict[str, str] = {
    "lucide:sparkles": "M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z",
    "lucide:zap": "M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z",
    "lucide:check": "M20 6 9 17l-5-5",
    "lucide:heart": "M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z",
    "lucide:star": "M11.525 2.295a.53.53 0 0 1 .95 0l2.31 4.679a2.123 2.123 0 0 0 1.595 1.16l5.166.756a.53.53 0 0 1 .294.904l-3.736 3.638a2.123 2.123 0 0 0-.611 1.878l.882 5.14a.53.53 0 0 1-.771.56l-4.618-2.428a2.122 2.122 0 0 0-1.973 0L6.396 21.01a.53.53 0 0 1-.77-.56l.881-5.139a2.122 2.122 0 0 0-.611-1.879L2.16 9.795a.53.53 0 0 1 .294-.906l5.165-.755a2.122 2.122 0 0 0 1.597-1.16z",
    "lucide:shield": "M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z",
    "lucide:flame": "M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 3.5z",
    "lucide:rocket": "M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09zM12 15l-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z",
    "lucide:arrow-right": "M5 12h14M12 5l7 7-7 7",
    "lucide:bell": "M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9M10.3 21a1.94 1.94 0 0 0 3.4 0",
    "lucide:code": "m18 16 4-4-4-4M6 8l-4 4 4 4M14.5 4l-5 16",
    "lucide:terminal": "m4 17 6-6-6-6M12 19h8",
    "lucide:cpu": "M12 2v2M12 20v2M2 12h2M20 12h2M9 2v2M9 20v2M15 2v2M15 20v2M2 9h2M20 9h2M2 15h2M20 15h2M6 6h12v12H6z",
    "lucide:database": "M21 5c0 1.66-4 3-9 3s-9-1.34-9-3 4-3 9-3 9 1.34 9 3ZM3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5M3 12c0 1.66 4 3 9 3s9-1.34 9-3",
    "lucide:globe": "M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2Zm0 0a14.5 14.5 0 0 1 4 10 14.5 14.5 0 0 1-4 10 14.5 14.5 0 0 1-4-10 14.5 14.5 0 0 1 4-10ZM2 12h20",
    "lucide:lock": "M7 11V7a5 5 0 0 1 10 0v4M5 11h14v10H5z",
    "lucide:user": "M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z",
    "lucide:settings": "M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2zM12 15a3 3 0 1 1 0-6 3 3 0 0 1 0 6z",
    "lucide:search": "m21 21-4.35-4.35M19 11a8 8 0 1 1-16 0 8 8 0 0 1 16 0z",
    "lucide:download": "M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3",
    "lucide:upload": "M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12",
    "lucide:play": "m5 3 14 9-14 9V3z",
    "lucide:pause": "M6 4h4v16H6zM14 4h4v16h-4z",
    "lucide:volume-2": "M11 5 6 9H2v6h4l5 4V5zM19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07",
    "lucide:copy": "M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2M9 2h6a1 1 0 0 1 1 1v2a1 1 0 0 1-1 1H9a1 1 0 0 1-1-1V3a1 1 0 0 1 1-1z",
    "lucide:trash": "M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2",
    "lucide:refresh-cw": "M3 12a9 9 0 0 1 15-6.7L21 8M21 3v5h-5M21 12a9 9 0 0 1-15 6.7L3 16M3 21v-5h5",
    "lucide:plus": "M12 5v14M5 12h14",
    "lucide:minus": "M5 12h14",
}


class IconifyResolver:
    """
    Fetches and locally caches SVG paths from the Iconify API (200,000+ open-source icons).
    """

    _cache_dir: str = os.path.join(tempfile.gettempdir(), "vibmo_icons_cache")

    @classmethod
    def resolve_path_data(cls, icon_name: str) -> str:
        name = icon_name.lower().strip()
        
        # 1. Check built-in fast offline dictionary
        if name in BUILTIN_ICONS:
            return BUILTIN_ICONS[name]

        # 2. Check local disk cache
        os.makedirs(cls._cache_dir, exist_ok=True)
        sanitized = re.sub(r"[^a-zA-Z0-9_-]", "_", name)
        cache_file = os.path.join(cls._cache_dir, f"{sanitized}.d")

        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cached_d = f.read().strip()
                if cached_d:
                    return cached_d
            except Exception:
                pass

        # 3. Online fetch from Iconify API
        parts = name.split(":", 1)
        if len(parts) == 2:
            prefix, icon_id = parts[0], parts[1]
            url = f"https://api.iconify.design/{prefix}/{icon_id}.svg"
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Vibmo/0.1.0"})
                with urllib.request.urlopen(req, timeout=1.8) as resp:
                    svg_content = resp.read().decode("utf-8")
                
                # Extract path d attribute
                d_matches = re.findall(r'd="([^"]+)"', svg_content)
                if d_matches:
                    combined_d = " ".join(d_matches)
                    with open(cache_file, "w", encoding="utf-8") as f:
                        f.write(combined_d)
                    return combined_d
            except Exception:
                pass

        # Fallback to sparkles
        return BUILTIN_ICONS.get("lucide:sparkles", "M12 2v20M2 12h20")


class Icon(Node):
    """
    Vector Icon node supporting 200,000+ icons from Iconify (Lucide, Heroicons, Phosphor, Tabler, FontAwesome).
    """

    def __init__(
        self,
        name: str = "lucide:sparkles",
        size: float = 32.0,
        color: Optional[Union[Color, str]] = colors.WHITE,
        stroke_width: float = 2.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.icon_name = name.lower()
        self.size = Signal(float(size), f"{self.name}.size")
        
        resolved_color = Color.from_any(color) if isinstance(color, (str, Color)) else color
        self.color = Signal(resolved_color, f"{self.name}.color")
        self.stroke_width = Signal(float(stroke_width), f"{self.name}.stroke_width")

        d_path = IconifyResolver.resolve_path_data(self.icon_name)
        self._path_node = Path(
            d=d_path,
            fill=None,
            stroke=resolved_color,
            stroke_width=stroke_width,
        )
        self.add(self._path_node)

    @classmethod
    def preload(cls, *icon_names: str) -> None:
        """Pre-fetches icon SVGs to local disk cache."""
        for name in icon_names:
            IconifyResolver.resolve_path_data(name)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        sz = max(0.0, self.size.get(time))
        return (0.0, 0.0, sz, sz)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        sz = max(0.0, self.size.get(time))
        if sz <= 0:
            return
        
        scale_factor = sz / 24.0
        c = self.color.get(time)
        sw = self.stroke_width.get(time)

        self._path_node.scale.set((scale_factor, scale_factor))
        self._path_node.stroke.set(c)
        self._path_node.stroke_width.set(sw / max(1e-4, scale_factor))
