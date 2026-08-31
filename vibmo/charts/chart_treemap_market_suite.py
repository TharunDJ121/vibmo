"""
Market Cap Treemap Chart Suite for visualizing asset valuation and performance.
"""

from __future__ import annotations
from typing import Any, List, Dict, Optional, Tuple, Union
import math

from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc
from vibmo.timeline.scheduler import ParallelGroup
from vibmo.scene.node import Node
from vibmo.primitives.rect import Rect
from vibmo.typography.text import Text
from vibmo.layout.container import FlexContainer
from vibmo.core.vector import Vector2D


def _interpolate_color(c1: Color, c2: Color, t: float) -> Color:
    """Linearly interpolate between two colors."""
    r = c1.r + (c2.r - c1.r) * t
    g = c1.g + (c2.g - c1.g) * t
    b = c1.b + (c2.b - c1.b) * t
    a = c1.a + (c2.a - c1.a) * t
    return Color(r, g, b, a)


class PercentageDeltaColor:
    """Utility to map performance percentage to color (Red to Green)."""

    @staticmethod
    def get_color(percentage: float) -> Color:
        clamped = max(-0.05, min(0.05, percentage))
        t = (clamped + 0.05) / 0.10

        red = colors.ROSE
        gray = colors.SLATE_700
        green = colors.EMERALD

        if t < 0.5:
            return _interpolate_color(red, gray, t * 2.0)
        else:
            return _interpolate_color(gray, green, (t - 0.5) * 2.0)


class ZoomableTreemapTile(Rect):
    """Individual company tile with ticker, market cap, and performance."""

    def __init__(
        self,
        ticker: str,
        market_cap: float,
        performance: float,
        width: float,
        height: float,
        sector: str = "",
        **kwargs: Any
    ):
        bg_color = PercentageDeltaColor.get_color(performance)
        super().__init__(width=width, height=height, fill=bg_color, corner_radius=4.0, **kwargs)

        self.ticker = ticker
        self.market_cap = market_cap
        self.performance = performance
        self.sector = sector

        self.clip = True

        font_size_ticker = max(8, min(width / 4, height / 3, 24))
        font_size_mc = font_size_ticker * 0.6
        font_size_perf = font_size_ticker * 0.6

        self.ticker_node = Text(
            text=ticker,
            font_size=font_size_ticker,
            color=colors.WHITE,
            bold=True,
            align="center"
        )
        self.ticker_node.position.set((width / 2, height / 2 - font_size_mc))

        if market_cap >= 1e12:
            mc_str = f"${market_cap / 1e12:.1f}T"
        elif market_cap >= 1e9:
            mc_str = f"${market_cap / 1e9:.1f}B"
        else:
            mc_str = f"${market_cap / 1e6:.1f}M"

        self.mc_node = Text(
            text=mc_str,
            font_size=font_size_mc,
            color=colors.WHITE,
            align="center"
        )
        self.mc_node.position.set((width / 2, height / 2 + font_size_mc * 0.5))

        perf_sign = "+" if performance > 0 else ""
        self.perf_node = Text(
            text=f"{perf_sign}{performance * 100:.2f}%",
            font_size=font_size_perf,
            color=colors.WHITE,
            align="center"
        )
        self.perf_node.position.set((width / 2, height / 2 + font_size_mc * 2.0))

        self.add(self.ticker_node, self.mc_node, self.perf_node)


class MarketSectorLegend(FlexContainer):
    """Header bar breaking down sectors."""

    def __init__(self, sectors: List[str], **kwargs: Any):
        super().__init__(direction="row", gap=20, padding=10, align_items="center", **kwargs)

        for sector in sectors:
            item = FlexContainer(direction="row", gap=8, padding=0, align_items="center")
            dot = Rect(width=12, height=12, corner_radius=6, fill=colors.SLATE_400)
            label = Text(text=sector, font_size=14, color=colors.SLATE_200)
            item.add(dot, label)
            self.add(item)


class TreemapMarketCapGrid(Node):
    """Squarified treemap layout partitioning canvas by asset valuation."""

    def __init__(
        self,
        data: Optional[Union[List[Dict[str, Any]], Dict[str, Any]]] = None,
        width: float = 1200.0,
        height: float = 800.0,
        stocks: Optional[Union[List[Dict[str, Any]], Dict[str, Any]]] = None,
        **kwargs: Any
    ):
        super().__init__(**kwargs)

        raw = stocks if stocks is not None else (data or [])
        parsed_data: List[Dict[str, Any]] = []

        if isinstance(raw, dict):
            for key, val in raw.items():
                if isinstance(val, list):
                    for item in val:
                        d = dict(item)
                        if "sector" not in d:
                            d["sector"] = key
                        parsed_data.append(d)
                elif isinstance(val, dict):
                    d = dict(val)
                    if "ticker" not in d:
                        d["ticker"] = key
                    parsed_data.append(d)
                else:
                    parsed_data.append({
                        "ticker": key,
                        "market_cap": float(val),
                        "performance": 0.0,
                        "sector": ""
                    })
        elif isinstance(raw, list):
            for item in raw:
                if isinstance(item, dict):
                    parsed_data.append(dict(item))
                else:
                    parsed_data.append({"ticker": str(item), "market_cap": 1.0, "performance": 0.0})

        self.data = sorted(parsed_data, key=lambda x: x.get('market_cap', 0), reverse=True)
        self.width = Signal(float(width), f"{self.name}.width")
        self.height = Signal(float(height), f"{self.name}.height")

        self.tiles: List[ZoomableTreemapTile] = []
        self._build_layout(width, height)

    def _build_layout(self, width: float, height: float):
        self.clear()
        self.tiles.clear()

        if not self.data:
            return

        total_mc = sum(d.get('market_cap', 0) for d in self.data)
        if total_mc <= 0:
            return

        total_area = width * height

        nodes = []
        for d in self.data:
            area = (d.get('market_cap', 0) / total_mc) * total_area
            nodes.append({'data': d, 'area': area})

        rects = self._squarify(nodes, 0, 0, width, height)

        for r in rects:
            d = r['data']
            tile = ZoomableTreemapTile(
                ticker=d.get('ticker', ''),
                market_cap=d.get('market_cap', 0),
                performance=d.get('performance', 0),
                width=r['w'],
                height=r['h'],
                sector=d.get('sector', '')
            )
            tile.position.set((r['x'], r['y']))
            self.add(tile)
            self.tiles.append(tile)

    def _squarify(self, nodes: List[Dict], x: float, y: float, w: float, h: float) -> List[Dict]:
        if not nodes:
            return []

        res = []

        def worst_ratio(row: List[Dict], length: float) -> float:
            if not row or length == 0:
                return float('inf')
            r_max = max(n['area'] for n in row)
            r_min = min(n['area'] for n in row)
            s = sum(n['area'] for n in row)
            if s == 0:
                return float('inf')

            return max(
                (length**2 * r_max) / (s**2),
                (s**2) / (length**2 * r_min)
            )

        def layout_row(row: List[Dict], x: float, y: float, w: float, h: float) -> Tuple[float, float, float, float]:
            if not row:
                return x, y, w, h

            s = sum(n['area'] for n in row)
            if s == 0:
                return x, y, w, h

            if w >= h:
                row_width = s / h
                curr_y = y
                for n in row:
                    rect_h = n['area'] / row_width if row_width else 0
                    res.append({'data': n['data'], 'x': x, 'y': curr_y, 'w': row_width, 'h': rect_h})
                    curr_y += rect_h
                return x + row_width, y, w - row_width, h
            else:
                row_height = s / w
                curr_x = x
                for n in row:
                    rect_w = n['area'] / row_height if row_height else 0
                    res.append({'data': n['data'], 'x': curr_x, 'y': y, 'w': rect_w, 'h': row_height})
                    curr_x += rect_w
                return x, y + row_height, w, h - row_height

        current_nodes = nodes[:]
        while current_nodes:
            shortest_side = min(w, h)
            row = []

            row.append(current_nodes[0])

            idx = 1
            while idx < len(current_nodes):
                next_node = current_nodes[idx]
                r1 = worst_ratio(row, shortest_side)
                r2 = worst_ratio(row + [next_node], shortest_side)

                if r2 <= r1 or math.isclose(r2, r1, rel_tol=1e-5):
                    row.append(next_node)
                    idx += 1
                else:
                    break

            current_nodes = current_nodes[len(row):]
            x, y, w, h = layout_row(row, x, y, w, h)

        return res

    def zoom_sector(
        self,
        sector: str,
        duration: float = 1.2,
        delay: float = 0.0,
        ease: Optional[EasingFunc] = None
    ) -> ParallelGroup:
        """Animates focus zoom and emphasis onto a specific sector or ticker category."""
        e = ease or Ease.out_expo
        actions = []
        for tile in self.tiles:
            is_match = (tile.sector.lower() == sector.lower()) or (tile.ticker.lower() == sector.lower())
            target_opacity = 1.0 if (is_match or not sector) else 0.35
            target_scale = 1.05 if is_match else 0.98
            actions.append(tile.opacity.to(target_opacity, duration=duration, delay=delay, ease=e))
            actions.append(tile.scale.to(target_scale, duration=duration, delay=delay, ease=e))
        return ParallelGroup(actions)


MarketCapTreemap = TreemapMarketCapGrid
TreemapCellNode = ZoomableTreemapTile
