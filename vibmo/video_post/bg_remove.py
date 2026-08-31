"""
AI Background Removal & Alpha Matting for Vibmo.

Removes backgrounds from video frames or images using Rembg (U2Net / BiRefNet),
generating clean transparent RGBA PNGs.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from PIL import Image


class BackgroundRemover:
    """Removes image backgrounds and generates alpha transparency."""

    @classmethod
    def is_available(cls) -> bool:
        try:
            import rembg  # noqa: F401
            return True
        except ImportError:
            return False

    @classmethod
    def remove_background(
        cls,
        input_image: str | Path | Image.Image,
        output_path: str | Path | None = None,
        alpha_matting: bool = False,
    ) -> Image.Image | None:
        try:
            import rembg
        except ImportError:
            return None

        if isinstance(input_image, (str, Path)):
            img = Image.open(input_image)
        else:
            img = input_image

        result = rembg.remove(img, alpha_matting=alpha_matting)

        if output_path:
            out_p = Path(output_path)
            out_p.parent.mkdir(parents=True, exist_ok=True)
            result.save(out_p, "PNG")

        return result
