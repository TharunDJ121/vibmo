"""
Portable Project Format, Media Relinking, and Asset Bundling (.vibmo).
"""

from __future__ import annotations
import os
import json
import zipfile
import shutil
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class ProjectMediaItem:
    """A referenced media asset (video, audio, font, lottie, image)."""
    id: str
    name: str
    file_path: str
    kind: str  # "image", "video", "audio", "font", "lottie"
    size_bytes: int = 0
    missing: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "file_path": self.file_path,
            "kind": self.kind,
            "size_bytes": self.size_bytes,
            "missing": self.missing,
        }


class VibmoProject:
    """
    Top-level Motion Design Project container.
    Manages compositions, timelines, asset bins, media relinking, and portable .vibmo archives.
    """

    def __init__(
        self,
        name: str = "Untitled Project",
        width: int = 1920,
        height: int = 1080,
        fps: float = 60.0,
    ) -> None:
        self.name = name
        self.width = width
        self.height = height
        self.fps = fps
        self.media_items: Dict[str, ProjectMediaItem] = {}
        self.compositions: List[Any] = []
        self.metadata: Dict[str, Any] = {}

    def add_media(self, file_path: str, kind: str = "image", name: Optional[str] = None) -> ProjectMediaItem:
        """Registers a media asset into the project bin."""
        abs_path = os.path.abspath(file_path)
        item_name = name or os.path.basename(file_path)
        item_id = f"{kind}_{len(self.media_items) + 1}"
        size = os.path.getsize(abs_path) if os.path.exists(abs_path) else 0
        missing = not os.path.exists(abs_path)

        item = ProjectMediaItem(id=item_id, name=item_name, file_path=abs_path, kind=kind, size_bytes=size, missing=missing)
        self.media_items[item_id] = item
        return item

    def relink_assets(self, search_directories: List[str]) -> int:
        """Searches provided directories to find and relink missing media files."""
        relinked_count = 0
        for item in self.media_items.values():
            if not os.path.exists(item.file_path):
                target_filename = os.path.basename(item.file_path)
                for s_dir in search_directories:
                    if not os.path.exists(s_dir):
                        continue
                    for root, _, files in os.walk(s_dir):
                        if target_filename in files:
                            item.file_path = os.path.abspath(os.path.join(root, target_filename))
                            item.missing = False
                            item.size_bytes = os.path.getsize(item.file_path)
                            relinked_count += 1
                            break
                    if not item.missing:
                        break
        return relinked_count

    def save(self, file_path: str) -> None:
        """Saves project metadata to a JSON file."""
        data = {
            "name": self.name,
            "version": "1.0.0",
            "width": self.width,
            "height": self.height,
            "fps": self.fps,
            "media_items": [item.to_dict() for item in self.media_items.values()],
            "metadata": self.metadata,
        }
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, file_path: str) -> VibmoProject:
        """Loads project from a JSON file."""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        proj = cls(
            name=data.get("name", "Untitled Project"),
            width=data.get("width", 1920),
            height=data.get("height", 1080),
            fps=data.get("fps", 60.0),
        )
        for m_data in data.get("media_items", []):
            item = ProjectMediaItem(
                id=m_data["id"],
                name=m_data["name"],
                file_path=m_data["file_path"],
                kind=m_data["kind"],
                size_bytes=m_data.get("size_bytes", 0),
                missing=not os.path.exists(m_data["file_path"]),
            )
            proj.media_items[item.id] = item
        return proj

    def bundle(self, output_zip_path: str) -> str:
        """Packages project file and all media assets into a portable .vibmo archive."""
        out_abs = os.path.abspath(output_zip_path)
        with zipfile.ZipFile(out_abs, "w", zipfile.ZIP_DEFLATED) as zf:
            # Write project JSON
            proj_data = {
                "name": self.name,
                "version": "1.0.0",
                "width": self.width,
                "height": self.height,
                "fps": self.fps,
                "media_items": [],
            }
            for item in self.media_items.values():
                if os.path.exists(item.file_path):
                    rel_name = f"assets/{os.path.basename(item.file_path)}"
                    zf.write(item.file_path, arcname=rel_name)
                    proj_data["media_items"].append({
                        "id": item.id,
                        "name": item.name,
                        "file_path": rel_name,
                        "kind": item.kind,
                    })

            zf.writestr("project.json", json.dumps(proj_data, indent=2))
        return out_abs
