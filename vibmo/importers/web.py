"""
Headless Web, React & Tailwind HTML Ingestion Engine.
Renders live URLs, React components, and Tailwind snippets at 4K retina resolution for 3D scenes.
"""

from __future__ import annotations
import hashlib
import os
import shutil
import subprocess
import tempfile
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
from PIL import Image
import cairo

from vibmo.core.color import Color
from vibmo.core.vector import Vector2D
from vibmo.scene.node import Node


def find_system_browser() -> Optional[str]:
    """Finds Google Chrome, Microsoft Edge, or Chromium on the host OS."""
    candidates = [
        # Windows
        os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
        # macOS
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
        # Linux
        "/usr/bin/google-chrome",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/usr/bin/microsoft-edge",
        # PATH
        shutil.which("chrome"),
        shutil.which("chromium"),
        shutil.which("msedge"),
        shutil.which("google-chrome"),
    ]

    for c in candidates:
        if c and os.path.exists(c):
            return c
    return None


def get_web_cache_dir() -> str:
    cache_dir = os.path.join(os.getcwd(), ".vibmo_cache", "web")
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir


def capture_web_content(
    url_or_html: str,
    width: int = 1280,
    height: int = 800,
    scale: float = 2.0,
    wait_ms: int = 1500,
    cache_dir: Optional[str] = None,
) -> str:
    """
    Renders a live URL or raw HTML/Tailwind markup into a high-DPI retina PNG image.
    Returns the path to the cached PNG file.
    """
    target_cache_dir = cache_dir or get_web_cache_dir()
    browser_bin = find_system_browser()
    raw_input = str(url_or_html).strip()

    # Hash input + dimensions for instant cache hits
    content_hash = hashlib.sha256(f"{raw_input}_{width}_{height}_{scale}".encode()).hexdigest()[:16]
    cached_png = os.path.join(target_cache_dir, f"web_{content_hash}.png")

    if os.path.exists(cached_png) and os.path.getsize(cached_png) > 1024:
        return cached_png

    is_url = raw_input.startswith(("http://", "https://", "file://"))
    temp_html_path: Optional[str] = None

    if is_url:
        target_url = raw_input
    else:
        # Wrap HTML snippet with full document structure + Tailwind CDN
        has_doc = "<html" in raw_input.lower()
        if not has_doc:
            full_html = f"""<!DOCTYPE html>
<html class="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<script src="https://cdn.tailwindcss.com"></script>
<style>
  body {{
    margin: 0;
    padding: 0;
    background: transparent;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  }}
</style>
</head>
<body class="bg-transparent text-white">
{raw_input}
</body>
</html>"""
        else:
            full_html = raw_input

        temp_html_path = os.path.join(tempfile.gettempdir(), f"vibmo_web_{content_hash}.html")
        with open(temp_html_path, "w", encoding="utf-8") as f:
            f.write(full_html)
        target_url = f"file:///{temp_html_path}"

    if browser_bin:
        cmd = [
            browser_bin,
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
            "--allow-file-access-from-files",
            f"--window-size={width},{height}",
            f"--force-device-scale-factor={scale}",
            f"--virtual-time-budget={wait_ms}",
            f"--screenshot={cached_png}",
            target_url,
        ]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    # Clean up temp file
    if temp_html_path and os.path.exists(temp_html_path):
        try:
            os.remove(temp_html_path)
        except Exception:
            pass

    # Fallback if browser failed or unavailable: create styled placeholder
    if not os.path.exists(cached_png) or os.path.getsize(cached_png) < 100:
        pw = int(width * scale)
        ph = int(height * scale)
        fallback_img = Image.new("RGBA", (pw, ph), (15, 23, 42, 255))
        fallback_img.save(cached_png)

    return cached_png


class WebNode(Node):
    """
    Animatable scene node holding a rendered high-DPI HTML/CSS or live website texture.
    """

    def __init__(
        self,
        url_or_html: str,
        width: float = 1200.0,
        height: float = 750.0,
        scale: float = 2.0,
        corner_radius: float = 0.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.width_val = float(width)
        self.height_val = float(height)
        self.corner_radius = float(corner_radius)
        self.scale_factor = float(scale)
        self.source = str(url_or_html)
        
        # Capture web content
        self.image_path = capture_web_content(
            url_or_html=self.source,
            width=int(self.width_val),
            height=int(self.height_val),
            scale=self.scale_factor,
        )

        # Load image metadata
        if os.path.exists(self.image_path):
            img = Image.open(self.image_path)
            self.orig_w, self.orig_h = img.size
        else:
            self.orig_w, self.orig_h = int(self.width_val), int(self.height_val)


        self._surface_cache: Optional[cairo.ImageSurface] = None
        self._surface_arr: Optional[np.ndarray] = None

    @property
    def width(self) -> float:
        return self.width_val

    @property
    def height(self) -> float:
        return self.height_val

    def __getstate__(self) -> Dict[str, Any]:

        state = self.__dict__.copy()
        state.pop("_surface_cache", None)
        state.pop("_surface_arr", None)
        return state

    def __setstate__(self, state: Dict[str, Any]) -> None:
        self.__dict__.update(state)
        self._surface_cache = None
        self._surface_arr = None

    def _get_surface(self) -> Optional[cairo.ImageSurface]:
        if self._surface_cache is None and os.path.exists(self.image_path):
            img = Image.open(self.image_path).convert("RGBA")
            self.orig_w, self.orig_h = img.size
            # Cairo BGRA on little endian
            arr = np.array(img)
            bgra = np.zeros_like(arr)
            bgra[:, :, 0] = arr[:, :, 2]
            bgra[:, :, 1] = arr[:, :, 1]
            bgra[:, :, 2] = arr[:, :, 0]
            bgra[:, :, 3] = arr[:, :, 3]
            self._surface_arr = np.ascontiguousarray(bgra)
            self._surface_cache = cairo.ImageSurface.create_for_data(
                self._surface_arr, cairo.FORMAT_ARGB32, self.orig_w, self.orig_h
            )
        return self._surface_cache

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        surf = self._get_surface()
        if surf is None:
            return

        ctx.save()

        # Clip corner radius if specified
        if self.corner_radius > 0.0:
            r = min(self.corner_radius, self.width_val * 0.5, self.height_val * 0.5)
            import math
            ctx.new_path()
            ctx.arc(self.width_val - r, r, r, -math.pi * 0.5, 0)
            ctx.arc(self.width_val - r, self.height_val - r, r, 0, math.pi * 0.5)
            ctx.arc(r, self.height_val - r, r, math.pi * 0.5, math.pi)
            ctx.arc(r, r, r, math.pi, math.pi * 1.5)
            ctx.close_path()
            ctx.clip()

        sx = self.width_val / self.orig_w
        sy = self.height_val / self.orig_h
        ctx.scale(sx, sy)
        ctx.set_source_surface(surf, 0, 0)
        ctx.paint()

        ctx.restore()

