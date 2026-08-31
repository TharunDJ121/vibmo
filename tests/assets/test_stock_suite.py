"""
Unit tests for StockAssetConnector.
"""

import pytest
from vibmo.assets.stock import StockAssetConnector, StockMediaItem


def test_stock_media_item_data_model():
    item = StockMediaItem(
        id="nasa_apollo",
        title="Apollo 11 Launch",
        description="Historic rocket liftoff",
        source="nasa",
        media_type="video",
        url="https://images.nasa.gov/sample.mp4",
        thumbnail_url="https://images.nasa.gov/thumb.jpg",
        license="NASA Public Domain",
    )
    assert item.source == "nasa"
    assert item.license == "NASA Public Domain"
