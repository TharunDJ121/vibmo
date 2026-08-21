"""
Automatic Google Fonts downloader, resolver, and cross-platform caching.
"""

from __future__ import annotations
import os
import urllib.request
from pathlib import Path
from typing import Optional

CACHE_DIR = Path.home() / ".cache" / "vibmo" / "fonts"


class FontManager:
    """Manages font resolution, downloads, and caching."""

    _cached_fonts: dict = {}

    @classmethod
    def get_font_path(cls, family: str, bold: bool = False, italic: bool = False) -> Optional[str]:
        """Resolves font family to a local TTF/OTF filepath, downloading if necessary."""
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        key = f"{family}_{'bold' if bold else 'regular'}_{'italic' if italic else ''}".lower()
        if key in cls._cached_fonts:
            return cls._cached_fonts[key]

        # Check standard Windows / Linux font locations
        win_fonts = Path("C:/Windows/Fonts")
        if win_fonts.exists():
            clean_name = family.replace(" ", "")
            candidates = [
                win_fonts / f"{clean_name}.ttf",
                win_fonts / f"{clean_name}bd.ttf" if bold else win_fonts / f"{clean_name}.ttf",
                win_fonts / f"segoeui.ttf",
                win_fonts / f"arial.ttf",
            ]
            for c in candidates:
                if c.exists():
                    cls._cached_fonts[key] = str(c)
                    return str(c)

        # Download from Google Fonts repository if missing
        font_filename = f"{family.replace(' ', '+')}-{'Bold' if bold else 'Regular'}.ttf"
        cached_file = CACHE_DIR / f"{family}_{'Bold' if bold else 'Regular'}.ttf"
        if cached_file.exists():
            cls._cached_fonts[key] = str(cached_file)
            return str(cached_file)

        # Attempt download
        try:
            url = f"https://github.com/google/fonts/raw/main/ofl/{family.lower().replace(' ', '')}/{family.replace(' ', '')}-{'Bold' if bold else 'Regular'}.ttf"
            urllib.request.urlretrieve(url, str(cached_file))
            if cached_file.exists() and cached_file.stat().st_size > 1000:
                cls._cached_fonts[key] = str(cached_file)
                return str(cached_file)
        except Exception:
            pass

        return None
