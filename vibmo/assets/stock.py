"""
Public Domain & Creative Commons Stock Asset Connectors for Vibmo / Motio.

Provides zero-API-key search and metadata retrieval for public domain stock video/images:
  - NASA Image and Video Library
  - Internet Archive (archive.org)
  - Library of Congress (LOC)
  - Wikimedia Commons
"""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Sequence


@dataclass
class StockMediaItem:
    id: str
    title: str
    description: str
    source: str  # "nasa", "archive_org", "loc", "wikimedia"
    media_type: str  # "video", "image", "audio"
    url: str
    thumbnail_url: str | None = None
    license: str = "Public Domain"


class StockAssetConnector:
    """Universal client for querying open public-domain media archives."""

    @classmethod
    def search_nasa(cls, query: str, media_type: str = "video", limit: int = 6) -> list[StockMediaItem]:
        """Search NASA Image and Video Library."""
        encoded_q = urllib.parse.quote(query)
        url = f"https://images-api.nasa.gov/search?q={encoded_q}&media_type={media_type}"
        items: list[StockMediaItem] = []
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "VibmoMotionGraphics/1.0"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            collection = data.get("collection", {}).get("items", [])
            for entry in collection[:limit]:
                data_list = entry.get("data", [{}])
                meta = data_list[0] if data_list else {}
                nasa_id = meta.get("nasa_id", "")
                title = meta.get("title", "NASA Media")
                desc = meta.get("description", "")[:140]

                links = entry.get("links", [{}])
                thumb = links[0].get("href") if links else None

                items.append(
                    StockMediaItem(
                        id=f"nasa_{nasa_id}",
                        title=title,
                        description=desc,
                        source="nasa",
                        media_type=media_type,
                        url=thumb or "",
                        thumbnail_url=thumb,
                        license="NASA Public Domain",
                    )
                )
        except Exception:
            # Graceful network fallback
            pass
        return items

    @classmethod
    def search_archive_org(cls, query: str, limit: int = 6) -> list[StockMediaItem]:
        """Search Internet Archive open media collections."""
        encoded_q = urllib.parse.quote(query)
        url = f"https://archive.org/advancedsearch.php?q={encoded_q}+AND+mediatype:(movies)&fl[]=identifier,title,description&rows={limit}&output=json"
        items: list[StockMediaItem] = []
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "VibmoMotionGraphics/1.0"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            docs = data.get("response", {}).get("docs", [])
            for doc in docs:
                ident = doc.get("identifier", "")
                title = doc.get("title", "Archive.org Video")
                desc = str(doc.get("description", ""))[:140]
                items.append(
                    StockMediaItem(
                        id=f"archive_{ident}",
                        title=title,
                        description=desc,
                        source="archive_org",
                        media_type="video",
                        url=f"https://archive.org/details/{ident}",
                        thumbnail_url=f"https://archive.org/services/img/{ident}",
                        license="Public Domain / Creative Commons",
                    )
                )
        except Exception:
            pass
        return items
