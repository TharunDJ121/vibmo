import math
from typing import Any, Dict, List, Optional
import cairo

from vibmo.scene.node import Node
from vibmo.core.color import Color, colors
from vibmo.core.signal import Signal

class WebhookEventStreamCard(Node):
    def __init__(self, events: List[Dict[str, str]], width: float = 400.0, height: float = 300.0, **kwargs):
        super().__init__(**kwargs)
        self.events = events
        self.width = width
        self.height = height

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        # Background
        ctx.rectangle(0, 0, self.width, self.height)
        r, g, b, a = Color.hex("#111827").to_cairo() # bg-gray-900
        ctx.set_source_rgba(r, g, b, a)
        ctx.fill()
        
        ctx.set_font_size(14)
        y_offset = 20.0
        
        for idx, event in enumerate(self.events):
            if y_offset > self.height - 20:
                break
            
            # Timestamp
            ctx.move_to(20, y_offset)
            r, g, b, a = Color.hex("#9CA3AF").to_cairo() # text-gray-400
            ctx.set_source_rgba(r, g, b, a)
            ctx.show_text(event.get('timestamp', '00:00:00'))
            
            # Event name
            ctx.move_to(100, y_offset)
            r, g, b, a = Color.hex("#F3F4F6").to_cairo() # text-gray-100
            ctx.set_source_rgba(r, g, b, a)
            ctx.show_text(event.get('event', 'unknown'))
            
            y_offset += 24.0
            
        super().draw(ctx, time)
        ctx.restore()

class HttpStatusBadge(Node):
    def __init__(self, status_code: int = 200, **kwargs):
        super().__init__(**kwargs)
        self.status_code = Signal(status_code)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        code = self.status_code.get()
        
        if code < 300:
            bg_color = Color.hex("#D1FAE5") # bg-emerald-100
            text_color = Color.hex("#065F46") # text-emerald-900
            text = f"{code} OK"
        elif code < 500:
            bg_color = Color.hex("#FEF3C7") # bg-amber-100
            text_color = Color.hex("#92400E") # text-amber-900
            if code == 404:
                text = "404 Not Found"
            else:
                text = f"{code} Error"
        else:
            bg_color = Color.hex("#FEE2E2") # bg-red-100
            text_color = Color.hex("#991B1B") # text-red-900
            text = "500 Server Error" if code == 500 else f"{code} Error"
            
        ctx.set_font_size(12)
        extents = ctx.text_extents(text)
        width = extents.width + 16
        height = 20
        
        # Draw pill
        ctx.arc(height/2, height/2, height/2, math.pi/2, 3*math.pi/2)
        ctx.arc(width - height/2, height/2, height/2, -math.pi/2, math.pi/2)
        ctx.close_path()
        r, g, b, a = bg_color.to_cairo()
        ctx.set_source_rgba(r, g, b, a)
        ctx.fill()
        
        # Text
        r, g, b, a = text_color.to_cairo()
        ctx.set_source_rgba(r, g, b, a)
        ctx.move_to(8, height/2 - extents.y_bearing/2)
        ctx.show_text(text)
        
        super().draw(ctx, time)
        ctx.restore()

class PayloadJsonInspector(Node):
    def __init__(self, payload: str, width: float = 400.0, height: float = 200.0, is_open: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.payload = payload
        self.width = width
        self.height = height
        self.is_open = Signal(1.0 if is_open else 0.0)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        
        open_ratio = self.is_open.get()
        current_height = self.height * open_ratio
        
        if current_height > 0:
            ctx.rectangle(0, 0, self.width, current_height)
            r, g, b, a = Color.hex("#1F2937").to_cairo() # bg-gray-800
            ctx.set_source_rgba(r, g, b, a)
            ctx.fill()
            
            ctx.rectangle(0, 0, self.width, current_height)
            ctx.clip()
            
            ctx.set_font_size(12)
            lines = self.payload.split('\n')
            y_offset = 20.0
            
            for line in lines:
                if y_offset > current_height:
                    break
                
                ctx.move_to(10, y_offset)
                
                # Simple syntax coloring logic
                if ':' in line:
                    key, val = line.split(':', 1)
                    r, g, b, a = Color.hex("#93C5FD").to_cairo() # key color
                    ctx.set_source_rgba(r, g, b, a)
                    ctx.show_text(key + ":")
                    
                    # string value
                    if '"' in val:
                        r, g, b, a = Color.hex("#A7F3D0").to_cairo()
                    else:
                        r, g, b, a = Color.hex("#FCD34D").to_cairo()
                    ctx.set_source_rgba(r, g, b, a)
                        
                    ext = ctx.text_extents(key + ":")
                    ctx.move_to(10 + ext.x_advance, y_offset)
                    ctx.show_text(val)
                else:
                    r, g, b, a = Color.hex("#D1D5DB").to_cairo()
                    ctx.set_source_rgba(r, g, b, a)
                    ctx.show_text(line)
                    
                y_offset += 16.0
                
        super().draw(ctx, time)
        ctx.restore()

class RetryEventButton(Node):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_retrying = Signal(0.0) # 0 to 1 for animation progress

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()
        
        width = 80
        height = 32
        
        # Button bg
        ctx.rectangle(0, 0, width, height)
        r, g, b, a = Color.hex("#3B82F6").to_cairo() # bg-blue-500
        ctx.set_source_rgba(r, g, b, a)
        ctx.fill()
        
        retrying = self.is_retrying.get()
        
        r, g, b, a = Color.hex("#FFFFFF").to_cairo()
        ctx.set_source_rgba(r, g, b, a)
        
        if retrying > 0:
            # Draw circular reload icon
            ctx.save()
            ctx.translate(width/2, height/2)
            ctx.rotate(retrying * math.pi * 2) # Spin
            
            ctx.arc(0, 0, 8, 0, math.pi * 1.5)
            ctx.set_line_width(2)
            ctx.stroke()
            
            # Arrow head
            ctx.move_to(6, -2)
            ctx.line_to(10, -2)
            ctx.line_to(8, -6)
            ctx.fill()
            
            ctx.restore()
        else:
            # Draw text
            ctx.set_font_size(12)
            extents = ctx.text_extents("Retry")
            ctx.move_to((width - extents.width)/2, height/2 - extents.y_bearing/2)
            ctx.show_text("Retry")
            
        super().draw(ctx, time)
        ctx.restore()
