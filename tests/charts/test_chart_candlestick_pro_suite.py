import pytest
from unittest.mock import MagicMock
from vibmo.charts.chart_candlestick_pro_suite import (
    ProCandlestickChart,
    MovingAverageCurves,
    VolumeProfileOverlay,
    CrosshairPriceTracker
)
from vibmo.core.color import colors

@pytest.fixture
def sample_data():
    return [
        {'date': '2023-01-01', 'open': 100, 'high': 110, 'low': 90, 'close': 105, 'volume': 1000},
        {'date': '2023-01-02', 'open': 105, 'high': 120, 'low': 100, 'close': 115, 'volume': 1500},
        {'date': '2023-01-03', 'open': 115, 'high': 115, 'low': 95, 'close': 100, 'volume': 2000},
    ]

@pytest.fixture
def mock_ctx():
    ctx = MagicMock()
    # Support basic properties needed in mock
    ctx.text_extents.return_value = MagicMock(width=40.0)
    return ctx

def test_procandlestickchart_draw(sample_data, mock_ctx):
    chart = ProCandlestickChart(data=sample_data, width=300, height=200)
    chart.draw(mock_ctx, 0.0)

    assert mock_ctx.save.called
    assert mock_ctx.restore.called
    assert mock_ctx.set_source_rgba.called
    assert mock_ctx.stroke.called
    assert mock_ctx.fill.called

def test_movingaveragecurves_compute_ema():
    data = [10.0, 11.0, 12.0, 13.0, 14.0]
    ema = MovingAverageCurves.compute_ema(data, period=3)

    assert len(ema) == 5
    assert ema[0] == 10.0
    # Expected EMA logic
    # k = 2 / (3 + 1) = 0.5
    # ema[1] = (11 - 10) * 0.5 + 10 = 10.5
    assert ema[1] == 10.5
    # ema[2] = (12 - 10.5) * 0.5 + 10.5 = 11.25
    assert ema[2] == 11.25

def test_movingaveragecurves_draw(sample_data, mock_ctx):
    chart = MovingAverageCurves(data=sample_data, width=300, height=200)
    chart.draw(mock_ctx, 0.0)

    assert mock_ctx.save.called
    assert mock_ctx.restore.called
    assert mock_ctx.stroke.called

def test_volumeprofileoverlay_draw(sample_data, mock_ctx):
    chart = VolumeProfileOverlay(data=sample_data, width=300, height=200)
    chart.draw(mock_ctx, 0.0)

    assert mock_ctx.save.called
    assert mock_ctx.restore.called
    assert mock_ctx.fill.called

def test_crosshairpricetracker_draw(sample_data, mock_ctx):
    chart = CrosshairPriceTracker(data=sample_data, width=300, height=200, cursor_x=150, cursor_y=100)
    chart.draw(mock_ctx, 0.0)

    assert mock_ctx.save.called
    assert mock_ctx.restore.called
    assert mock_ctx.stroke.called
    assert mock_ctx.fill.called
    assert mock_ctx.show_text.called
