"""
Market Cap Treemap Chart Suite for visualizing asset valuation and performance.
"""

from __future__ import annotations
from typing import Any, List, Dict, Optional, Tuple
import math

from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal
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
        # Map -5% to 5% to 0.0 to 1.0
        # -5% -> bright crimson red
        # +5% -> bright emerald green
        # We clamp the percentage between -0.05 and 0.05
        clamped = max(-0.05, min(0.05, percentage))

        # Normalize to [0, 1]
        t = (clamped + 0.05) / 0.10

        # Red: ROSE, Green: Emerald. Center: Slate/Gray
        # For simplicity, we can interpolate from ROSE to Gray, then Gray to Emerald.
        red = colors.ROSE
        gray = colors.SLATE_700
        green = colors.EMERALD

        if t < 0.5:
            # Scale t from [0, 0.5] to [0, 1]
            return _interpolate_color(red, gray, t * 2.0)
        else:
            # Scale t from [0.5, 1] to [0, 1]
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
        **kwargs: Any
    ):
        bg_color = PercentageDeltaColor.get_color(performance)
        super().__init__(width=width, height=height, fill=bg_color, corner_radius=4.0, **kwargs)

        self.ticker = ticker
        self.market_cap = market_cap
        self.performance = performance

        self.clip = True # We want to clip text

        # Add texts
        # If the box is too small, we might not want to render text, or just make it small
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
        # Position centered
        self.ticker_node.position.set((width / 2, height / 2 - font_size_mc))

        # Format market cap
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

        # Just simple labels for sectors for now, maybe with a color box?
        # The prompt says "Header bar breaking down Tech, Healthcare, Finance, and Energy."
        for sector in sectors:
            # We can use a colored dot or just text
            item = FlexContainer(direction="row", gap=8, padding=0, align_items="center")
            dot = Rect(width=12, height=12, corner_radius=6, fill=colors.SLATE_400)
            label = Text(text=sector, font_size=14, color=colors.SLATE_200)
            item.add(dot, label)
            self.add(item)


class TreemapMarketCapGrid(Node):
    """Squarified treemap layout partitioning canvas by asset valuation."""

    def __init__(self, data: List[Dict[str, Any]], width: float, height: float, **kwargs: Any):
        super().__init__(**kwargs)
        self.data = sorted(data, key=lambda x: x.get('market_cap', 0), reverse=True)
        self.width = Signal(float(width), f"{self.name}.width")
        self.height = Signal(float(height), f"{self.name}.height")

        self.tiles: List[ZoomableTreemapTile] = []
        self._build_layout(width, height)

    def _build_layout(self, width: float, height: float):
        self.clear()
        self.tiles.clear()

        if not self.data:
            return

        # Squarify algorithm
        # We need to partition the width x height rectangle into rectangles
        # Area is proportional to market_cap
        total_mc = sum(d.get('market_cap', 0) for d in self.data)
        if total_mc <= 0:
            return

        total_area = width * height

        # Scale all values to area
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
                height=r['h']
            )
            tile.position.set((r['x'], r['y']))
            self.add(tile)
            self.tiles.append(tile)

    def _squarify(self, nodes: List[Dict], x: float, y: float, w: float, h: float) -> List[Dict]:
        """Squarify algorithm optimizing aspect ratios."""
        if not nodes:
            return []

        # Brag's and Hu's Squarified Treemaps algorithm conceptually.
        # It adds nodes to a row one by one until the aspect ratio gets worse,
        # then it commits the row and starts a new one.

        res = []

        def worst_ratio(row: List[Dict], length: float) -> float:
            if not row or length == 0:
                return float('inf')
            r_max = max(n['area'] for n in row)
            r_min = min(n['area'] for n in row)
            s = sum(n['area'] for n in row)
            if s == 0:
                return float('inf')

            # The aspect ratio is max(w/h, h/w)
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

            if w >= h: # Lay out vertically along width
                row_width = s / h
                curr_y = y
                for n in row:
                    rect_h = n['area'] / row_width if row_width else 0
                    res.append({'data': n['data'], 'x': x, 'y': curr_y, 'w': row_width, 'h': rect_h})
                    curr_y += rect_h
                return x + row_width, y, w - row_width, h
            else: # Lay out horizontally along height
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

            # Add first node
            row.append(current_nodes[0])

            # Try to add more nodes
            idx = 1
            while idx < len(current_nodes):
                next_node = current_nodes[idx]

                # Aspect ratio with current row
                r1 = worst_ratio(row, shortest_side)

                # Aspect ratio if we add next_node
                r2 = worst_ratio(row + [next_node], shortest_side)

                if r2 <= r1 or math.isclose(r2, r1, rel_tol=1e-5):
                    row.append(next_node)
                    idx += 1
                else:
                    break

            # Commit row
            current_nodes = current_nodes[len(row):]
            x, y, w, h = layout_row(row, x, y, w, h)

        return res
