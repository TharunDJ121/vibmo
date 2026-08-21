"""
Asset library system for managing built-in assets.
Includes icons, gradients, textures, fonts, and audio assets.
"""

from __future__ import annotations
import os
import json
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

from vibmo.core.color import Color, colors


class AssetType(Enum):
    """Types of assets in the library."""
    ICON = "icon"
    GRADIENT = "gradient"
    TEXTURE = "texture"
    FONT = "font"
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"


class AssetCategory(Enum):
    """Categories for organizing assets."""
    UI = "ui"
    NATURE = "nature"
    TECHNOLOGY = "technology"
    BUSINESS = "business"
    ABSTRACT = "abstract"
    GRADIENTS = "gradients"
    PATTERNS = "patterns"
    ICONS = "icons"
    FONTS = "fonts"
    AUDIO = "audio"
    VIDEO = "video"


@dataclass
class AssetMetadata:
    """Metadata for an asset."""
    id: str
    name: str
    asset_type: AssetType
    category: AssetCategory
    description: str = ""
    tags: List[str] = None
    author: str = ""
    license: str = ""
    url: str = ""
    preview_url: str = ""
    file_path: str = ""
    file_size: int = 0
    dimensions: tuple = None  # For images/videos
    duration: float = 0.0  # For audio/video
    custom_data: Dict[str, Any] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.custom_data is None:
            self.custom_data = {}
        if self.dimensions is None:
            self.dimensions = (0, 0)


class AssetLibrary:
    """
    Central asset library for managing built-in and custom assets.
    Provides search, categorization, and asset management capabilities.
    """

    def __init__(self, library_path: Optional[str] = None):
        self.library_path = library_path or self._get_default_library_path()
        self.assets: Dict[str, AssetMetadata] = {}
        self._load_builtin_assets()
        self._load_custom_assets()

    def _get_default_library_path(self) -> str:
        """Get default library path from project structure."""
        project_root = Path(__file__).parent.parent.parent
        return str(project_root / "assets" / "library")

    def _load_builtin_assets(self):
        """Load built-in assets from the library."""
        # Load built-in gradients
        self._register_builtin_gradients()
        
        # Load built-in icons (placeholder for icon library)
        self._register_builtin_icons()
        
        # Load built-in textures (placeholder for texture library)
        self._register_builtin_textures()

        # Load built-in audio SFX and music library
        self._register_builtin_audio()

    def _register_builtin_audio(self):
        """Register built-in audio SFX and music assets."""
        project_root = Path(__file__).parent.parent.parent
        audio_dir = project_root / "assets" / "audio"
        manifest_file = audio_dir / "manifest.json"

        if manifest_file.exists():
            try:
                with open(manifest_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for rel_path, item in data.get("assets", {}).items():
                        stem = Path(rel_path).stem
                        asset_id = f"audio-{stem}"
                        is_music = "music" in rel_path
                        self.assets[asset_id] = AssetMetadata(
                            id=asset_id,
                            name=stem.replace("_", " ").title(),
                            asset_type=AssetType.AUDIO,
                            category=AssetCategory.AUDIO,
                            description=item.get("description", "Motion graphics sound"),
                            tags=["audio", "sfx" if not is_music else "music", stem],
                            file_path=str(audio_dir / rel_path),
                            license=item.get("license", "CC0"),
                        )
            except Exception:
                pass

    def _register_builtin_gradients(self):
        """Register built-in gradient assets."""
        gradients = [
            {
                "id": "gradient-sunset",
                "name": "Sunset",
                "asset_type": AssetType.GRADIENT,
                "category": AssetCategory.GRADIENTS,
                "description": "Warm sunset gradient from orange to purple",
                "tags": ["warm", "sunset", "orange", "purple"],
                "custom_data": {
                    "colors": [colors.ORANGE, colors.PURPLE],
                    "direction": "diagonal"
                }
            },
            {
                "id": "gradient-ocean",
                "name": "Ocean",
                "asset_type": AssetType.GRADIENT,
                "category": AssetCategory.GRADIENTS,
                "description": "Cool ocean gradient from blue to teal",
                "tags": ["cool", "ocean", "blue", "teal"],
                "custom_data": {
                    "colors": [colors.BLUE, colors.TEAL],
                    "direction": "vertical"
                }
            },
            {
                "id": "gradient-forest",
                "name": "Forest",
                "asset_type": AssetType.GRADIENT,
                "category": AssetCategory.GRADIENTS,
                "description": "Natural forest gradient from green to lime",
                "tags": ["nature", "forest", "green", "lime"],
                "custom_data": {
                    "colors": [colors.GREEN, colors.LIME],
                    "direction": "horizontal"
                }
            },
            {
                "id": "gradient-midnight",
                "name": "Midnight",
                "asset_type": AssetType.GRADIENT,
                "category": AssetCategory.GRADIENTS,
                "description": "Dark midnight gradient from navy to black",
                "tags": ["dark", "midnight", "navy", "black"],
                "custom_data": {
                    "colors": [colors.NAVY, colors.BLACK],
                    "direction": "radial"
                }
            },
            {
                "id": "gradient-candy",
                "name": "Candy",
                "asset_type": AssetType.GRADIENT,
                "category": AssetCategory.GRADIENTS,
                "description": "Sweet candy gradient from pink to cyan",
                "tags": ["bright", "candy", "pink", "cyan"],
                "custom_data": {
                    "colors": [colors.PINK, colors.CYAN],
                    "direction": "diagonal"
                }
            }
        ]
        
        for gradient_data in gradients:
            metadata = AssetMetadata(**gradient_data)
            self.assets[metadata.id] = metadata

    def _register_builtin_icons(self):
        """Register built-in icon assets (placeholder)."""
        # This would integrate with icon libraries like Lucide, Heroicons, etc.
        icon_categories = ["ui", "arrows", "media", "communication", "business"]
        
        for category in icon_categories:
            icon_id = f"icon-{category}-placeholder"
            metadata = AssetMetadata(
                id=icon_id,
                name=f"{category.capitalize()} Icons",
                asset_type=AssetType.ICON,
                category=AssetCategory.ICONS,
                description=f"Collection of {category} icons",
                tags=[category, "icons"],
                custom_data={"icon_set": category}
            )
            self.assets[icon_id] = metadata

    def _register_builtin_textures(self):
        """Register built-in texture assets (placeholder)."""
        textures = [
            {
                "id": "texture-noise",
                "name": "Noise Texture",
                "asset_type": AssetType.TEXTURE,
                "category": AssetCategory.PATTERNS,
                "description": "Perlin noise texture for organic effects",
                "tags": ["noise", "organic", "texture"],
                "custom_data": {"type": "noise", "scale": 1.0}
            },
            {
                "id": "texture-grain",
                "name": "Film Grain",
                "asset_type": AssetType.TEXTURE,
                "category": AssetCategory.PATTERNS,
                "description": "Film grain texture for cinematic effects",
                "tags": ["grain", "film", "cinematic"],
                "custom_data": {"type": "grain", "intensity": 0.5}
            },
            {
                "id": "texture-grid",
                "name": "Grid Pattern",
                "asset_type": AssetType.TEXTURE,
                "category": AssetCategory.PATTERNS,
                "description": "Grid pattern texture for technical designs",
                "tags": ["grid", "technical", "pattern"],
                "custom_data": {"type": "grid", "spacing": 50}
            }
        ]
        
        for texture_data in textures:
            metadata = AssetMetadata(**texture_data)
            self.assets[metadata.id] = metadata

    def _load_custom_assets(self):
        """Load custom assets from library path."""
        if not os.path.exists(self.library_path):
            return
            
        # Load custom assets from JSON metadata files
        metadata_file = os.path.join(self.library_path, "metadata.json")
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, 'r') as f:
                    custom_assets = json.load(f)
                    
                for asset_data in custom_assets:
                    metadata = AssetMetadata(**asset_data)
                    self.assets[metadata.id] = metadata
            except Exception as e:
                print(f"Error loading custom assets: {e}")

    def add_asset(self, metadata: AssetMetadata) -> bool:
        """Add a new asset to the library."""
        if metadata.id in self.assets:
            print(f"Asset with ID {metadata.id} already exists")
            return False
            
        self.assets[metadata.id] = metadata
        self._save_custom_assets()
        return True

    def get_asset(self, asset_id: str) -> Optional[AssetMetadata]:
        """Get asset metadata by ID."""
        return self.assets.get(asset_id)

    def search_assets(self, 
                     query: str = "", 
                     asset_type: Optional[AssetType] = None,
                     category: Optional[AssetCategory] = None,
                     tags: Optional[List[str]] = None) -> List[AssetMetadata]:
        """Search assets with filters."""
        results = []
        
        for asset in self.assets.values():
            # Filter by asset type
            if asset_type and asset.asset_type != asset_type:
                continue
                
            # Filter by category
            if category and asset.category != category:
                continue
                
            # Filter by tags
            if tags:
                if not any(tag in asset.tags for tag in tags):
                    continue
                    
            # Filter by search query
            if query:
                query_lower = query.lower()
                if (query_lower not in asset.name.lower() and 
                    query_lower not in asset.description.lower() and
                    query_lower not in " ".join(asset.tags).lower()):
                    continue
                    
            results.append(asset)
            
        return results

    def get_assets_by_type(self, asset_type: AssetType) -> List[AssetMetadata]:
        """Get all assets of a specific type."""
        return [asset for asset in self.assets.values() if asset.asset_type == asset_type]

    def get_assets_by_category(self, category: AssetCategory) -> List[AssetMetadata]:
        """Get all assets in a specific category."""
        return [asset for asset in self.assets.values() if asset.category == category]

    def get_gradient(self, gradient_id: str) -> Optional[Dict[str, Any]]:
        """Get gradient data by ID."""
        asset = self.get_asset(gradient_id)
        if asset and asset.asset_type == AssetType.GRADIENT:
            return asset.custom_data
        return None

    def get_icon(self, icon_id: str) -> Optional[Dict[str, Any]]:
        """Get icon data by ID."""
        asset = self.get_asset(icon_id)
        if asset and asset.asset_type == AssetType.ICON:
            return asset.custom_data
        return None

    def get_texture(self, texture_id: str) -> Optional[Dict[str, Any]]:
        """Get texture data by ID."""
        asset = self.get_asset(texture_id)
        if asset and asset.asset_type == AssetType.TEXTURE:
            return asset.custom_data
        return None

    def _save_custom_assets(self):
        """Save custom assets to metadata file."""
        if not os.path.exists(self.library_path):
            os.makedirs(self.library_path)
            
        metadata_file = os.path.join(self.library_path, "metadata.json")
        custom_assets = []
        
        for asset in self.assets.values():
            # Only save custom assets (not built-in)
            if not asset.id.startswith(("gradient-", "icon-", "texture-")):
                custom_assets.append(asdict(asset))
        
        try:
            with open(metadata_file, 'w') as f:
                json.dump(custom_assets, f, indent=2)
        except Exception as e:
            print(f"Error saving custom assets: {e}")

    def import_asset(self, file_path: str, metadata: AssetMetadata) -> bool:
        """Import an asset file into the library."""
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return False
            
        # Copy file to library directory
        import shutil
        asset_dir = os.path.join(self.library_path, metadata.asset_type.value)
        if not os.path.exists(asset_dir):
            os.makedirs(asset_dir)
            
        dest_path = os.path.join(asset_dir, os.path.basename(file_path))
        try:
            shutil.copy2(file_path, dest_path)
            metadata.file_path = dest_path
            metadata.file_size = os.path.getsize(dest_path)
            
            return self.add_asset(metadata)
        except Exception as e:
            print(f"Error importing asset: {e}")
            return False

    def delete_asset(self, asset_id: str) -> bool:
        """Delete an asset from the library."""
        asset = self.get_asset(asset_id)
        if not asset:
            return False
            
        # Delete file if it exists
        if asset.file_path and os.path.exists(asset.file_path):
            try:
                os.remove(asset.file_path)
            except Exception as e:
                print(f"Error deleting asset file: {e}")
        
        # Remove from library
        del self.assets[asset_id]
        self._save_custom_assets()
        return True

    def get_all_tags(self) -> List[str]:
        """Get all unique tags across all assets."""
        all_tags = set()
        for asset in self.assets.values():
            all_tags.update(asset.tags)
        return sorted(list(all_tags))

    def get_statistics(self) -> Dict[str, Any]:
        """Get library statistics."""
        stats = {
            "total_assets": len(self.assets),
            "by_type": {},
            "by_category": {},
            "total_tags": len(self.get_all_tags())
        }
        
        for asset in self.assets.values():
            # Count by type
            asset_type = asset.asset_type.value
            stats["by_type"][asset_type] = stats["by_type"].get(asset_type, 0) + 1
            
            # Count by category
            category = asset.category.value
            stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
            
        return stats


# Global asset library instance
_global_library: Optional[AssetLibrary] = None


def get_asset_library() -> AssetLibrary:
    """Get the global asset library instance."""
    global _global_library
    if _global_library is None:
        _global_library = AssetLibrary()
    return _global_library


def create_gradient_preset(name: str, colors: List[Color], direction: str = "linear") -> str:
    """Create a custom gradient preset and add it to the library."""
    library = get_asset_library()
    
    gradient_id = f"gradient-custom-{name.lower().replace(' ', '-')}"
    
    metadata = AssetMetadata(
        id=gradient_id,
        name=name,
        asset_type=AssetType.GRADIENT,
        category=AssetCategory.GRADIENTS,
        description=f"Custom gradient: {name}",
        tags=["custom", "gradient"],
        custom_data={
            "colors": colors,
            "direction": direction
        }
    )
    
    if library.add_asset(metadata):
        return gradient_id
    return ""


def get_popular_gradients() -> List[str]:
    """Get IDs of popular gradient presets."""
    return [
        "gradient-sunset",
        "gradient-ocean", 
        "gradient-forest",
        "gradient-midnight",
        "gradient-candy"
    ]


def get_asset_preview_url(asset_id: str) -> Optional[str]:
    """Get preview URL for an asset."""
    library = get_asset_library()
    asset = library.get_asset(asset_id)
    if asset:
        return asset.preview_url or asset.file_path
    return None