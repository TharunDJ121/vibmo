"""
Asset Browser Manager for Studio UI and programmatic asset catalog management.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple, Union
from enum import Enum
from dataclasses import dataclass, field
import json
import os

from vibmo.assets.library import AssetLibrary, AssetMetadata, AssetType, AssetCategory, get_asset_library


@dataclass
class BrowserFilter:
    """Filter criteria for the asset browser."""
    search_query: str = ""
    asset_type: Optional[AssetType] = None
    category: Optional[AssetCategory] = None
    tags: List[str] = field(default_factory=list)
    favorites_only: bool = False


class AssetBrowser:
    """
    Studio Asset Browser subsystem for querying, filtering, and organizing assets.
    """

    def __init__(self, library: Optional[AssetLibrary] = None) -> None:
        self.library = library or get_asset_library()
        self.favorites: List[str] = []

    def toggle_favorite(self, asset_id: str) -> bool:
        """Toggle favorite status of an asset."""
        if asset_id in self.favorites:
            self.favorites.remove(asset_id)
            return False
        else:
            self.favorites.append(asset_id)
            return True

    def query(self, browser_filter: BrowserFilter) -> List[AssetMetadata]:
        """Query and filter the asset catalog."""
        results = self.library.search_assets(
            query=browser_filter.search_query if browser_filter.search_query else None,
            asset_type=browser_filter.asset_type,
            category=browser_filter.category,
            tags=browser_filter.tags if browser_filter.tags else None,
        )
        if browser_filter.favorites_only:
            results = [a for a in results if a.id in self.favorites]
        return results

    def get_catalog_summary(self) -> Dict[str, Any]:
        """Return catalog statistics and breakdown by category and type."""
        all_assets = list(self.library.assets.values())
        by_type: Dict[str, int] = {}
        by_cat: Dict[str, int] = {}

        for a in all_assets:
            t_key = a.asset_type.value if hasattr(a.asset_type, "value") else str(a.asset_type)
            c_key = a.category.value if hasattr(a.category, "value") else str(a.category)
            by_type[t_key] = by_type.get(t_key, 0) + 1
            by_cat[c_key] = by_cat.get(c_key, 0) + 1

        return {
            "total_assets": len(all_assets),
            "favorites_count": len(self.favorites),
            "by_type": by_type,
            "by_category": by_cat,
        }


# Global Singleton
_browser_instance: Optional[AssetBrowser] = None


def get_asset_browser() -> AssetBrowser:
    global _browser_instance
    if _browser_instance is None:
        _browser_instance = AssetBrowser()
    return _browser_instance
