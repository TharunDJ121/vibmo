from typing import Any, List, Dict
from vibmo.scene.node import Node
from vibmo.core.color import Color, colors

class ProCandlestickChart(Node):
    def __init__(self, data: List[Dict[str, float]], width: float, height: float, **kwargs) -> None:
        super().__init__(**kwargs)
        self.data = data
        self.width = width
        self.height = height

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        if not self.data:
            super().draw(ctx, time)
            return

        ctx.save()
        min_p = min(d['low'] for d in self.data)
        max_p = max(d['high'] for d in self.data)
        price_range = max_p - min_p if max_p != min_p else 1.0

        num_candles = len(self.data)
        candle_width = self.width / num_candles
        pad = candle_width * 0.2

        for i, d in enumerate(self.data):
            x = i * candle_width + candle_width / 2.0

            def map_y(p: float) -> float:
                return self.height - ((p - min_p) / price_range) * self.height

            y_open = map_y(d['open'])
            y_close = map_y(d['close'])
            y_high = map_y(d['high'])
            y_low = map_y(d['low'])

            is_bullish = d['close'] >= d['open']
            color = colors.EMERALD if is_bullish else colors.RED

            ctx.set_source_rgba(*color.to_cairo())

            # Draw wick
            ctx.set_line_width(1.0)
            ctx.move_to(x, y_high)
            ctx.line_to(x, y_low)
            ctx.stroke()

            # Draw body
            body_top = min(y_open, y_close)
            body_bottom = max(y_open, y_close)
            body_height = max(1.0, body_bottom - body_top)
            ctx.rectangle(x - candle_width / 2.0 + pad, body_top, candle_width - 2 * pad, body_height)
            ctx.fill()

        ctx.restore()
        super().draw(ctx, time)


class MovingAverageCurves(Node):
    def __init__(self, data: List[Dict[str, float]], width: float, height: float, **kwargs) -> None:
        super().__init__(**kwargs)
        self.data = data
        self.width = width
        self.height = height

    @staticmethod
    def compute_ema(data: List[float], period: int) -> List[float]:
        ema = []
        if not data:
            return ema
        k = 2.0 / (period + 1.0)
        current_ema = data[0]
        for val in data:
            current_ema = (val - current_ema) * k + current_ema
            ema.append(current_ema)
        return ema

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        if not self.data:
            super().draw(ctx, time)
            return

        ctx.save()
        min_p = min(d['low'] for d in self.data)
        max_p = max(d['high'] for d in self.data)
        price_range = max_p - min_p if max_p != min_p else 1.0

        num_candles = len(self.data)
        candle_width = self.width / num_candles

        def map_y(p: float) -> float:
            return self.height - ((p - min_p) / price_range) * self.height

        closes = [d['close'] for d in self.data]
        ema20 = self.compute_ema(closes, 20)
        ema50 = self.compute_ema(closes, 50)

        # Draw EMA 20 (Cyan)
        ctx.set_source_rgba(*colors.CYAN.to_cairo())
        ctx.set_line_width(2.0)
        for i, val in enumerate(ema20):
            x = i * candle_width + candle_width / 2.0
            y = map_y(val)
            if i == 0:
                ctx.move_to(x, y)
            else:
                ctx.line_to(x, y)
        ctx.stroke()

        # Draw EMA 50 (Amber)
        ctx.set_source_rgba(*colors.AMBER.to_cairo())
        ctx.set_line_width(2.0)
        for i, val in enumerate(ema50):
            x = i * candle_width + candle_width / 2.0
            y = map_y(val)
            if i == 0:
                ctx.move_to(x, y)
            else:
                ctx.line_to(x, y)
        ctx.stroke()

        ctx.restore()
        super().draw(ctx, time)


class VolumeProfileOverlay(Node):
    def __init__(self, data: List[Dict[str, float]], width: float, height: float, **kwargs) -> None:
        super().__init__(**kwargs)
        self.data = data
        self.width = width
        self.height = height

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        if not self.data:
            super().draw(ctx, time)
            return

        ctx.save()
        max_v = max((float(d.get('volume', 0.0)) for d in self.data), default=0.0)
        if max_v == 0.0:
            max_v = 1.0

        num_candles = len(self.data)
        candle_width = self.width / num_candles
        pad = candle_width * 0.2

        for i, d in enumerate(self.data):
            x = i * candle_width + candle_width / 2.0
            v = float(d.get('volume', 0.0))

            bar_height = (v / max_v) * self.height
            y = self.height - bar_height

            is_bullish = d['close'] >= d['open']
            color = colors.EMERALD if is_bullish else colors.RED
            r, g, b, _ = color.to_cairo()

            ctx.set_source_rgba(r, g, b, 0.5)

            ctx.rectangle(x - candle_width / 2.0 + pad, y, candle_width - 2 * pad, bar_height)
            ctx.fill()

        ctx.restore()
        super().draw(ctx, time)


class CrosshairPriceTracker(Node):
    def __init__(self, data: List[Dict[str, Any]], width: float, height: float, cursor_x: float, cursor_y: float, **kwargs) -> None:
        super().__init__(**kwargs)
        self.data = data
        self.width = width
        self.height = height
        self.cursor_x = cursor_x
        self.cursor_y = cursor_y

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        if not self.data:
            super().draw(ctx, time)
            return

        ctx.save()

        ctx.set_source_rgba(*colors.SLATE_400.to_cairo())
        ctx.set_line_width(1.0)
        # Using [4.0, 4.0] and offset 0.0 for dashed line in pycairo
        if hasattr(ctx, 'set_dash'):
            ctx.set_dash([4.0, 4.0], 0.0)

        # Horizontal line
        ctx.move_to(0, self.cursor_y)
        ctx.line_to(self.width, self.cursor_y)
        ctx.stroke()

        # Vertical line
        ctx.move_to(self.cursor_x, 0)
        ctx.line_to(self.cursor_x, self.height)
        ctx.stroke()

        if hasattr(ctx, 'set_dash'):
            ctx.set_dash([], 0.0)

        num_candles = len(self.data)
        candle_width = self.width / num_candles
        idx = int(self.cursor_x / candle_width)
        idx = max(0, min(num_candles - 1, idx))
        d = self.data[idx]

        min_p = min(float(item['low']) for item in self.data)
        max_p = max(float(item['high']) for item in self.data)
        price_range = max_p - min_p if max_p != min_p else 1.0

        price_at_y = max_p - (self.cursor_y / self.height) * price_range
        price_text = f"{price_at_y:.2f}"

        if hasattr(ctx, 'set_font_size'):
            ctx.set_font_size(12)

        # cairo Context has text_extents
        t_width = 40.0
        if hasattr(ctx, 'text_extents'):
            extents = ctx.text_extents(price_text)
            # fallback if it returns tuple instead of object
            if isinstance(extents, tuple) and len(extents) >= 4:
                t_width = extents[2]
            elif hasattr(extents, 'width'):
                t_width = extents.width

        badge_w = t_width + 10.0
        badge_h = 20.0
        badge_x = self.width
        badge_y = self.cursor_y - badge_h / 2.0

        ctx.set_source_rgba(*colors.SLATE_800.to_cairo())
        ctx.rectangle(badge_x, badge_y, badge_w, badge_h)
        ctx.fill()

        ctx.set_source_rgba(*colors.WHITE.to_cairo())
        ctx.move_to(badge_x + 5, badge_y + 14)
        if hasattr(ctx, 'show_text'):
            ctx.show_text(price_text)

        date_text = str(d.get('date', ''))
        if date_text:
            date_w = 60.0
            if hasattr(ctx, 'text_extents'):
                extents = ctx.text_extents(date_text)
                if isinstance(extents, tuple) and len(extents) >= 4:
                    date_w = extents[2]
                elif hasattr(extents, 'width'):
                    date_w = extents.width
            date_badge_w = date_w + 10.0
            date_badge_h = 20.0
            date_badge_x = self.cursor_x - date_badge_w / 2.0
            date_badge_y = self.height

            ctx.set_source_rgba(*colors.SLATE_800.to_cairo())
            ctx.rectangle(date_badge_x, date_badge_y, date_badge_w, date_badge_h)
            ctx.fill()

            ctx.set_source_rgba(*colors.WHITE.to_cairo())
            ctx.move_to(date_badge_x + 5, date_badge_y + 14)
            if hasattr(ctx, 'show_text'):
                ctx.show_text(date_text)

        ctx.restore()
        super().draw(ctx, time)
