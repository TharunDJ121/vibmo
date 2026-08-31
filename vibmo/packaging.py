"""
Vibmo Project Archiving & Packaging System (.vibmo / .dra equivalent)
Inspired by DaVinci Resolve Chapter 3 Project Archiving.

Bundles Python motion graphics scripts, asset dependencies (images, audio, fonts, LUTs),
and project metadata into a self-contained, reproducible .vibmo archive container.
"""

import os
import sys
import json
import zipfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any


class ProjectArchive:
    """
    Manages bundling, inspecting, and restoring self-contained .vibmo project packages.
    """

    @staticmethod
    def package(
        script_path: str,
        output_path: Optional[str] = None,
        include_assets: bool = True,
        include_preview: bool = True,
        extra_files: Optional[List[str]] = None,
    ) -> str:
        """
        Bundle a script and all its dependencies into a single .vibmo archive.
        """
        script = Path(script_path).resolve()
        if not script.exists():
            raise FileNotFoundError(f"Source script '{script_path}' does not exist.")

        if output_path is None:
            output_path = str(script.with_suffix(".vibmo"))
        
        output_file = Path(output_path).resolve()
        parent_dir = script.parent

        manifest = {
            "version": "2.0.0",
            "format": "vibmo_project_archive",
            "entry_script": script.name,
            "created_at": str(os.path.getmtime(script)),
            "assets": [],
            "extra_files": [],
        }

        # Discover potential local assets in project directory
        asset_candidates = []
        if include_assets:
            for folder_name in ["assets", "audio", "fonts", "luts", "textures"]:
                folder = parent_dir / folder_name
                if folder.exists() and folder.is_dir():
                    for root, _, files in os.walk(folder):
                        for f in files:
                            full_p = Path(root) / f
                            rel_p = full_p.relative_to(parent_dir)
                            asset_candidates.append((full_p, str(rel_p)))

        if extra_files:
            for extra in extra_files:
                ep = Path(extra).resolve()
                if ep.exists():
                    rel_p = ep.name if ep.parent == parent_dir else f"extra/{ep.name}"
                    asset_candidates.append((ep, rel_p))

        # Check for storyboard/preview image
        preview_candidates = [
            parent_dir / "storyboard.png",
            parent_dir / f"{script.stem}_storyboard.png",
            parent_dir / "preview.png",
        ]
        preview_file = None
        if include_preview:
            for pc in preview_candidates:
                if pc.exists():
                    preview_file = pc
                    break

        # Create the zip archive
        with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zf:
            # 1. Write Entry Script
            zf.write(script, arcname=f"src/{script.name}")

            # 2. Write Assets
            for full_p, rel_p in asset_candidates:
                posix_rel = str(rel_p).replace("\\", "/")
                zf.write(full_p, arcname=posix_rel)
                manifest["assets"].append(posix_rel)

            # 3. Write Preview
            if preview_file:
                zf.write(preview_file, arcname="preview.png")
                manifest["has_preview"] = True
            else:
                manifest["has_preview"] = False

            # 4. Write Manifest
            manifest_bytes = json.dumps(manifest, indent=2).encode("utf-8")
            zf.writestr("manifest.json", manifest_bytes)

        return str(output_file)

    @staticmethod
    def inspect(archive_path: str) -> Dict[str, Any]:
        """
        Read the manifest and structure of a .vibmo archive without full extraction.
        """
        ap = Path(archive_path).resolve()
        if not ap.exists():
            raise FileNotFoundError(f"Archive file '{archive_path}' does not exist.")

        with zipfile.ZipFile(ap, "r") as zf:
            file_list = zf.namelist()
            if "manifest.json" in file_list:
                manifest_data = json.loads(zf.read("manifest.json").decode("utf-8"))
            else:
                manifest_data = {"version": "unknown", "entry_script": "unknown", "assets": []}
            
            manifest_data["archive_size_bytes"] = ap.stat().st_size
            manifest_data["total_files"] = len(file_list)
            manifest_data["files"] = file_list
            return manifest_data

    @staticmethod
    def unpackage(archive_path: str, target_dir: Optional[str] = None) -> str:
        """
        Extract a .vibmo archive into a directory ready for editing and rendering.
        """
        ap = Path(archive_path).resolve()
        if not ap.exists():
            raise FileNotFoundError(f"Archive file '{archive_path}' does not exist.")

        if target_dir is None:
            target_dir = str(ap.parent / ap.stem)

        dest = Path(target_dir).resolve()
        dest.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(ap, "r") as zf:
            manifest_data = {}
            if "manifest.json" in zf.namelist():
                manifest_data = json.loads(zf.read("manifest.json").decode("utf-8"))

            for member in zf.infolist():
                if member.filename.startswith("src/"):
                    script_name = os.path.basename(member.filename)
                    if script_name:
                        out_script_path = dest / script_name
                        with zf.open(member) as source, open(out_script_path, "wb") as target:
                            shutil.copyfileobj(source, target)
                elif member.filename in ["manifest.json", "preview.png"]:
                    zf.extract(member, dest)
                else:
                    out_p = dest / member.filename
                    out_p.parent.mkdir(parents=True, exist_ok=True)
                    if not member.is_dir():
                        with zf.open(member) as source, open(out_p, "wb") as target:
                            shutil.copyfileobj(source, target)

        return str(dest)
