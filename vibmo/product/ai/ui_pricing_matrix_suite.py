import cairo
import math
from typing import Any, List, Optional, Tuple, Union

from vibmo.scene.node import Node
from vibmo.core.color import Color
from vibmo.core.signal import Signal

class FeatureChecklistRow(Node):
    """Feature items with green checkmarks and tooltip indicator dots."""
    def __init__(self, text: str = "Feature included", active: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.active = active

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        
        # Draw checkmark or X
        if self.active:
            ctx.set_source_rgba(0.1, 0.8, 0.4, 1.0)
            ctx.arc(12, 12, 10, 0, math.pi * 2)
            ctx.fill()
            
            ctx.set_source_rgba(1.0, 1.0, 1.0, 1.0)
            ctx.set_line_width(2.0)
            ctx.move_to(7, 12)
            ctx.line_to(11, 16)
            ctx.line_to(17, 8)
            ctx.stroke()
        else:
            ctx.set_source_rgba(0.8, 0.8, 0.8, 1.0)
            ctx.arc(12, 12, 10, 0, math.pi * 2)
            ctx.fill()
        
        # Text
        ctx.set_source_rgba(0.2, 0.2, 0.2, 1.0)
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(14)
        ctx.move_to(32, 17)
        ctx.show_text(self.text)
        
        # Tooltip indicator dot (optional visual)
        ctx.set_source_rgba(0.7, 0.7, 0.7, 1.0)
        ctx.arc(200, 12, 3, 0, math.pi * 2)
        ctx.fill()
        
        ctx.restore()
        
        
class AnnualBillingToggle(Node):
    """Toggle switch for Monthly vs Annual pricing with '-20% DISCOUNT' badge."""
    def __init__(self, is_annual: Union[bool, Signal] = False, **kwargs):
        super().__init__(**kwargs)
        self.is_annual = Signal(is_annual) if not isinstance(is_annual, Signal) else is_annual
        
    def get_price(self, monthly_price: float) -> float:
        # returns price based on state
        val = self.is_annual.get() if isinstance(self.is_annual, Signal) else self.is_annual
        if val:
            return monthly_price * 0.8
        return monthly_price
        
    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        val = self.is_annual.get() if isinstance(self.is_annual, Signal) else self.is_annual
        
        # Background
        ctx.set_source_rgba(0.9, 0.9, 0.9, 1.0)
        ctx.new_path()
        ctx.arc(24, 16, 16, math.pi/2, 3*math.pi/2)
        ctx.arc(56, 16, 16, -math.pi/2, math.pi/2)
        ctx.close_path()
        ctx.fill()
        
        # Knob
        if val:
            ctx.set_source_rgba(0.2, 0.6, 1.0, 1.0)
        else:
            ctx.set_source_rgba(0.6, 0.6, 0.6, 1.0)
        
        knob_x = 56 if val else 24
        ctx.arc(knob_x, 16, 12, 0, 2*math.pi)
        ctx.fill()
        
        # Discount Badge
        ctx.set_source_rgba(0.1, 0.8, 0.4, 0.2)
        ctx.rectangle(80, 4, 120, 24)
        ctx.fill()
        ctx.set_source_rgba(0.1, 0.6, 0.3, 1.0)
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(12)
        ctx.move_to(88, 20)
        ctx.show_text("-20% DISCOUNT")
        
        ctx.restore()


class PopularGlowBadge(Node):
    """'MOST POPULAR' glowing badge atop the center Pro tier card with specular rim."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        # Glowing badge with specular rim
        w, h, r = 120, 30, 15
        
        # Glow
        glow_alpha = 0.5 + 0.3 * math.sin(time * 3.0)
        ctx.set_source_rgba(1.0, 0.8, 0.2, glow_alpha * 0.5)
        ctx.new_path()
        ctx.arc(w - r, r, r + 5, -math.pi/2, 0)
        ctx.arc(w - r, h - r, r + 5, 0, math.pi/2)
        ctx.arc(r, h - r, r + 5, math.pi/2, math.pi)
        ctx.arc(r, r, r + 5, math.pi, 3*math.pi/2)
        ctx.close_path()
        ctx.fill()
        
        # Base
        ctx.set_source_rgba(1.0, 0.6, 0.1, 1.0)
        ctx.new_path()
        ctx.arc(w - r, r, r, -math.pi/2, 0)
        ctx.arc(w - r, h - r, r, 0, math.pi/2)
        ctx.arc(r, h - r, r, math.pi/2, math.pi)
        ctx.arc(r, r, r, math.pi, 3*math.pi/2)
        ctx.close_path()
        ctx.fill()
        
        # Specular rim
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.8)
        ctx.set_line_width(2)
        ctx.new_path()
        ctx.arc(w - r, r, r, -math.pi/2, 0)
        ctx.arc(w - r, h - r, r, 0, math.pi/2)
        ctx.arc(r, h - r, r, math.pi/2, math.pi)
        ctx.arc(r, r, r, math.pi, 3*math.pi/2)
        ctx.close_path()
        ctx.stroke()
        
        ctx.set_source_rgba(1.0, 1.0, 1.0, 1.0)
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(12)
        ctx.move_to(16, 20)
        ctx.show_text("MOST POPULAR")
        
        ctx.restore()


class PricingTierGrid(Node):
    """3-card layout (Starter, Pro, Enterprise) with price headers, feature lists, and CTA buttons."""
    def __init__(self, toggle: Optional[AnnualBillingToggle] = None, **kwargs):
        super().__init__(**kwargs)
        self.toggle = toggle or AnnualBillingToggle()
        self.tiers = [
            {"name": "Starter", "price": 20, "features": ["1 User", "5GB Storage", "Basic Support"]},
            {"name": "Pro", "price": 50, "features": ["5 Users", "50GB Storage", "Priority Support", "Analytics"]},
            {"name": "Enterprise", "price": 120, "features": ["Unlimited Users", "1TB Storage", "24/7 Support", "Custom API"]}
        ]
        
    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        card_w = 300
        gap = 40
        num_cards = len(self.tiers)
        # width = 3 cards + 2 gaps
        width = num_cards * card_w + (num_cards - 1) * gap
        height = 500  # card height
        return (0.0, 0.0, width, height)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        
        card_w, card_h = 300, 500
        gap = 40
        
        # Optional: draw toggle at top center
        # For simplicity in testing sizing, the grid is primarily the cards, 
        # but let's draw toggle above them.
        ctx.save()
        ctx.translate((card_w * 3 + gap * 2) / 2 - 100, -60)
        self.toggle.draw(ctx, time)
        ctx.restore()
        
        for i, tier in enumerate(self.tiers):
            x = i * (card_w + gap)
            y = 0
            
            ctx.save()
            ctx.translate(x, y)
            
            # Card background
            ctx.set_source_rgba(1.0, 1.0, 1.0, 1.0)
            if i == 1:
                ctx.set_source_rgba(0.95, 0.98, 1.0, 1.0) # Highlight Pro
            
            ctx.rectangle(0, 0, card_w, card_h)
            ctx.fill()
            
            ctx.set_source_rgba(0.8, 0.8, 0.8, 1.0)
            ctx.set_line_width(1)
            ctx.rectangle(0, 0, card_w, card_h)
            ctx.stroke()
            
            if i == 1:
                badge = PopularGlowBadge()
                ctx.save()
                ctx.translate(card_w / 2 - 60, -15)
                badge.draw(ctx, time)
                ctx.restore()
                
            # Tier Name
            ctx.set_source_rgba(0.2, 0.2, 0.2, 1.0)
            ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(24)
            ctx.move_to(20, 40)
            ctx.show_text(tier["name"])
            
            # Price
            price = self.toggle.get_price(tier["price"])
            ctx.set_font_size(48)
            ctx.move_to(20, 100)
            ctx.show_text(f"${price:.2f}")
            ctx.set_font_size(16)
            ctx.show_text("/mo")
            
            # Features
            for j, f_text in enumerate(tier["features"]):
                feat = FeatureChecklistRow(text=f_text, active=True)
                ctx.save()
                ctx.translate(20, 150 + j * 40)
                feat.draw(ctx, time)
                ctx.restore()
                
            # CTA Button
            ctx.set_source_rgba(0.1, 0.4, 0.9, 1.0)
            ctx.rectangle(20, card_h - 60, card_w - 40, 40)
            ctx.fill()
            
            ctx.set_source_rgba(1.0, 1.0, 1.0, 1.0)
            ctx.set_font_size(16)
            ctx.move_to(card_w / 2 - 40, card_h - 35)
            ctx.show_text("Get Started")
            
            ctx.restore()
            
        ctx.restore()
