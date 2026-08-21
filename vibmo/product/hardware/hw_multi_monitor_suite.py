import math
from typing import Any, Optional, Tuple, Union

from vibmo.scene.node import Node
from vibmo.core.color import Color
from vibmo.layout.container import FlexContainer
from vibmo.core.vector import Vector2D

class ScreenContainer(Node):
    def __init__(self, width: float, height: float, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.width_val = width
        self.height_val = height

        self.content = FlexContainer(
            direction="column",
            width=self.width_val,
            height=self.height_val,
            fill=Color.TRANSPARENT,
            stroke=Color.TRANSPARENT,
        )
        self.add(self.content)

    def add_content(self, *nodes: Node) -> 'ScreenContainer':
        self.content.add(*nodes)
        return self

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width_val
        h = self.height_val

        ctx.save()
        # Draw screen background / bezel
        ctx.set_source_rgba(0.05, 0.05, 0.05, 1.0)
        ctx.rectangle(0, 0, w, h)
        ctx.fill_preserve()

        # Bezel border
        ctx.set_source_rgba(0.2, 0.2, 0.2, 1.0)
        ctx.set_line_width(4.0)
        ctx.stroke()
        ctx.restore()


class DualDeveloperMonitors(Node):
    """
    Side-by-side dual 27-inch 4K developer monitors with configurable inward angle.
    """
    def __init__(
        self,
        screen_width: float = 600.0,
        screen_height: float = 340.0,
        inward_angle: float = math.radians(15),
        gap: float = 20.0,
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)

        # We rotate them inwards, around their inner edges
        # Left screen
        self.left_screen = ScreenContainer(screen_width, screen_height, name=f"{self.name}_left")
        self.left_screen.anchor.set(Vector2D(screen_width, screen_height / 2))
        self.left_screen.position.set(Vector2D(-gap/2, 0))
        self.left_screen.rotate_y.set(inward_angle)

        # Right screen
        self.right_screen = ScreenContainer(screen_width, screen_height, name=f"{self.name}_right")
        self.right_screen.anchor.set(Vector2D(0, screen_height / 2))
        self.right_screen.position.set(Vector2D(gap/2, 0))
        self.right_screen.rotate_y.set(-inward_angle)

        self.center_screen: Optional[Node] = None

        self.add(self.left_screen, self.right_screen)

class VerticalSidecarDisplay(Node):
    """
    Horizontal primary display paired with a vertical 9:16 portrait code monitor.
    """
    def __init__(
        self,
        primary_width: float = 600.0,
        primary_height: float = 340.0,
        sidecar_width: float = 340.0,
        sidecar_height: float = 600.0,
        gap: float = 30.0,
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)

        self.center_screen = ScreenContainer(primary_width, primary_height, name=f"{self.name}_center")
        self.center_screen.anchor.set(Vector2D(primary_width / 2, primary_height / 2))
        self.center_screen.position.set(Vector2D(0, 0))

        self.left_screen = ScreenContainer(sidecar_width, sidecar_height, name=f"{self.name}_left")
        self.left_screen.anchor.set(Vector2D(sidecar_width / 2, sidecar_height / 2))
        self.left_screen.position.set(Vector2D(-(primary_width / 2 + gap + sidecar_width / 2), 0))

        self.right_screen: Optional[Node] = None

        self.add(self.center_screen, self.left_screen)

class TripleCurvedSimulatorDeck(Node):
    """
    Triple panoramic wrap-around display cockpit.
    """
    def __init__(
        self,
        screen_width: float = 600.0,
        screen_height: float = 340.0,
        wrap_angle: float = math.radians(30),
        gap: float = 10.0,
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)

        self.center_screen = ScreenContainer(screen_width, screen_height, name=f"{self.name}_center")
        self.center_screen.anchor.set(Vector2D(screen_width / 2, screen_height / 2))
        self.center_screen.position.set(Vector2D(0, 0))

        self.left_screen = ScreenContainer(screen_width, screen_height, name=f"{self.name}_left")
        self.left_screen.anchor.set(Vector2D(screen_width, screen_height / 2))
        self.left_screen.position.set(Vector2D(-(screen_width / 2 + gap), 0))
        self.left_screen.rotate_y.set(wrap_angle)

        self.right_screen = ScreenContainer(screen_width, screen_height, name=f"{self.name}_right")
        self.right_screen.anchor.set(Vector2D(0, screen_height / 2))
        self.right_screen.position.set(Vector2D(screen_width / 2 + gap, 0))
        self.right_screen.rotate_y.set(-wrap_angle)

        self.add(self.left_screen, self.center_screen, self.right_screen)
