from typing import Any, Dict, Optional, Tuple
from vibmo.primitives.rect import Rect
from vibmo.core.vector import Vector2D
from vibmo.core.color import Color

class RiveAnimation(Rect):
    """
    Rive (.riv) Importer for State Machines and Skeletal Animation.
    Wraps the Rive C++ or Python bindings to expose interactive UI motion.
    """
    
    def __init__(
        self, 
        src: str, 
        artboard: Optional[str] = None, 
        state_machine: Optional[str] = None,
        width: float = 400.0,
        height: float = 400.0,
        **kwargs: Any
    ) -> None:
        super().__init__(width=width, height=height, **kwargs)
        self.src = src
        self.artboard = artboard
        self.state_machine = state_machine
        
        # In a real implementation we would bind to rive-python or pyrive here
        # self._rive_file = rive.File(src)
        # self._artboard = self._rive_file.artboard(artboard)
        # self._state_machine = self._artboard.state_machine(state_machine)
        
        self.inputs: Dict[str, Any] = {}
        
    def set_input(self, name: str, value: Any, time: float = 0.0) -> None:
        """Sets a Rive state machine input (Number, Boolean, or Trigger)."""
        # In a real implementation:
        # sm_input = self._state_machine.get_input(name)
        # sm_input.value = value
        self.inputs[name] = value
        print(f"[Rive] Set SM input '{name}' to {value} at time {time:.2f}s")
        
    def fire_trigger(self, name: str, time: float = 0.0) -> None:
        """Fires a state machine trigger."""
        # sm_input = self._state_machine.get_input(name)
        # sm_input.fire()
        print(f"[Rive] Fired SM trigger '{name}' at time {time:.2f}s")
        
    def draw(self, ctx: Any, time: float = 0.0) -> None:
        # Ensure transform is applied
        super().draw(ctx, time)
        
        # Advance the state machine by the delta time
        # self._state_machine.advance(time - self._last_time)
        # self._artboard.draw(ctx)
        
        # Mock drawing for now
        ctx.save()
        
        # Draw a placeholder rounded rect representing the Rive bounds
        w = self.width.get(time)
        h = self.height.get(time)
        
        # Draw bounding box
        ctx.set_source_rgba(0.2, 0.6, 1.0, 0.3)
        ctx.rectangle(0, 0, w, h)
        ctx.fill_preserve()
        ctx.set_source_rgba(0.2, 0.6, 1.0, 1.0)
        ctx.set_line_width(2.0)
        ctx.stroke()
        
        # Draw text inside
        ctx.set_source_rgba(1.0, 1.0, 1.0, 1.0)
        ctx.set_font_size(24)
        ctx.move_to(20, h/2)
        ctx.show_text(f"Rive: {self.src.split('/')[-1]}")
        
        if self.state_machine:
            ctx.set_font_size(16)
            ctx.move_to(20, h/2 + 30)
            ctx.show_text(f"SM: {self.state_machine}")
            
        ctx.restore()
