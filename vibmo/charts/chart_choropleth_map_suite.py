from typing import Any, Dict, List, Optional, Tuple
import cairo

from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal
from vibmo.core.vector import Vector2D
from vibmo.scene.node import Node
from vibmo.layout.container import FlexContainer
from vibmo.typography.text import Text
from vibmo.primitives.rect import Rect


class RegionalHeatPolygon(Node):
    """Smooth polygon boundary with animatable color heat fill."""
    def __init__(self, coordinates: List[Tuple[float, float]], value: float = 0.0, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.coordinates = coordinates
        self.heat_value = Signal(value)
        self.base_color = Color.from_any(colors.SLATE_800)
        self.heat_color = Color.from_any(colors.EMERALD)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        if not self.coordinates:
            super().draw(ctx, time)
            return

        ctx.save()

        # Interpolate color based on heat value
        val = self.heat_value.get()
        current_color = self.base_color.lerp(self.heat_color, val)

        ctx.set_source_rgba(*current_color.to_cairo())

        start_pt = self.coordinates[0]
        ctx.move_to(start_pt[0], start_pt[1])
        for pt in self.coordinates[1:]:
            ctx.line_to(pt[0], pt[1])
        ctx.close_path()
        ctx.fill()

        ctx.restore()
        super().draw(ctx, time)


class GeoDataTooltip(FlexContainer):
    """Floating pointer tooltip displaying country name, user count, and revenue."""
    def __init__(
        self,
        country_name: str,
        user_count: int,
        revenue: float,
        **kwargs: Any
    ) -> None:
        super().__init__(
            direction="column",
            gap=4.0,
            padding=12.0,
            corner_radius=8.0,
            fill=colors.SLATE_900,
            **kwargs
        )
        self.country_name = country_name
        self.user_count = user_count
        self.revenue = revenue

        self.add(
            Text(text=self.country_name, font_size=16, color=colors.WHITE, bold=True)
        )
        self.add(
            Text(text=f"Users: {self.user_count:,}", font_size=12, color=colors.SLATE_400)
        )
        self.add(
            Text(text=f"Revenue: ${self.revenue:,.2f}", font_size=12, color=colors.EMERALD)
        )


class CountryRankLeaderboard(FlexContainer):
    """Mini ranking leaderboard table alongside the map."""
    def __init__(self, rankings: List[Dict[str, Any]], **kwargs: Any) -> None:
        super().__init__(
            direction="column",
            gap=8.0,
            padding=16.0,
            corner_radius=12.0,
            fill=colors.SLATE_900,
            **kwargs
        )
        self.rankings = rankings

        # Header
        header = FlexContainer(direction="row", gap=24, justify_content="space_between", fill=None)
        header.add(Text(text="Rank", font_size=14, color=colors.SLATE_400, bold=True))
        header.add(Text(text="Country", font_size=14, color=colors.SLATE_400, bold=True))
        header.add(Text(text="Score", font_size=14, color=colors.SLATE_400, bold=True))
        self.add(header)

        # Rows
        for i, rank_data in enumerate(self.rankings):
            row = FlexContainer(direction="row", gap=24, justify_content="space_between", fill=None)
            row.add(Text(text=f"#{i+1}", font_size=14, color=colors.WHITE))
            row.add(Text(text=rank_data.get("country", "Unknown"), font_size=14, color=colors.WHITE))
            row.add(Text(text=str(rank_data.get("score", 0)), font_size=14, color=colors.EMERALD))
            self.add(row)


class ChoroplethWorldMiniMap(Node):
    """Stylized world vector polygon map where countries/regions are colored based on metric values."""
    def __init__(self, regions_data: Dict[str, Dict[str, Any]], **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.regions_data = regions_data

        self.polygons: Dict[str, RegionalHeatPolygon] = {}
        for region_id, data in self.regions_data.items():
            coords = data.get("coordinates", [])
            val = data.get("value", 0.0)
            poly = RegionalHeatPolygon(coordinates=coords, value=val)
            self.polygons[region_id] = poly
            self.add(poly)
