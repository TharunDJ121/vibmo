from __future__ import annotations
import math
from typing import Any, Optional, Tuple, Union

import cairo

from vibmo.scene.node import Node
from vibmo.core.color import Color
from vibmo.layout.container import FlexContainer
from vibmo.core.vector import Vector2D


class ScreenContainer(Node):
    """
    Individual monitor display container with dark background, bezel border, and auto-layout content container.
    """
    def __init__(self, width: float, height: float, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.width_val = float(width)
        self.height_val = float(height)

        self.content = FlexContainer(
            direction="column",
            gap=8.0,
            padding=12.0,
            width=self.width_val,
            height=self.height_val,
            fill=Color.TRANSPARENT,
            stroke=Color.TRANSPARENT,
            corner_radius=4.0,
        )
        self.screen = self.content
        self.add(self.content)

    def add_screen(self, *nodes: Node) -> ScreenContainer:
        """Add child nodes to the monitor screen."""
        self.content.add(*nodes)
        return self

    def add_screen_content(self, *nodes: Node) -> ScreenContainer:
        """Alias for add_screen."""
        return self.add_screen(*nodes)

    def add_content(self, *nodes: Node) -> ScreenContainer:
        """Alias for add_screen."""
        return self.add_screen(*nodes)

    def local_bounds(self, time: float = 0.0) -> Tuple[float, float, float, float]:
        return (0.0, 0.0, self.width_val, self.height_val)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        w = self.width_val
        h = self.height_val

        ctx.save()
        ctx.set_source_rgba(0.05, 0.05, 0.05, 1.0)
        ctx.rectangle(0, 0, w, h)
        ctx.fill_preserve()

        ctx.set_source_rgba(0.2, 0.2, 0.22, 1.0)
        ctx.set_line_width(4.0)
        ctx.stroke()
        ctx.restore()


class MultiMonitorDeveloperRig(Node):
    """
    Multi-monitor developer workstation rig supporting side-by-side displays,
    optional vertical 9:16 portrait coding monitor, and inward angle perspective.
    """
    def __init__(
        self,
        left_vertical: bool = False,
        screen_width: float = 600.0,
        screen_height: float = 340.0,
        inward_angle: float = math.radians(15),
        gap: float = 20.0,
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.left_vertical = left_vertical

        if self.left_vertical:
            vert_w = screen_height
            vert_h = screen_width
            self.left_screen = ScreenContainer(vert_w, vert_h, name=f"{self.name}_left")
            self.left_screen.anchor.set(Vector2D(vert_w / 2, vert_h / 2))
            self.left_screen.position.set(Vector2D(-(screen_width / 2 + gap + vert_w / 2), 0))

            self.right_screen = ScreenContainer(screen_width, screen_height, name=f"{self.name}_right")
            self.right_screen.anchor.set(Vector2D(screen_width / 2, screen_height / 2))
            self.right_screen.position.set(Vector2D(0, 0))
            self.center_screen = self.right_screen
            self.screen = self.right_screen
            self.add(self.left_screen, self.right_screen)
        else:
            self.left_screen = ScreenContainer(screen_width, screen_height, name=f"{self.name}_left")
            self.left_screen.anchor.set(Vector2D(screen_width, screen_height / 2))
            self.left_screen.position.set(Vector2D(-gap / 2, 0))
            self.left_screen.rotate_y.set(inward_angle)

            self.right_screen = ScreenContainer(screen_width, screen_height, name=f"{self.name}_right")
            self.right_screen.anchor.set(Vector2D(0, screen_height / 2))
            self.right_screen.position.set(Vector2D(gap / 2, 0))
            self.right_screen.rotate_y.set(-inward_angle)

            self.center_screen = None
            self.screen = self.left_screen
            self.add(self.left_screen, self.right_screen)

    def add_screen(self, *nodes: Node) -> MultiMonitorDeveloperRig:
        """Add nodes to the primary monitor screen."""
        self.screen.add_screen(*nodes)
        return self

    def add_screen_content(self, *nodes: Node) -> MultiMonitorDeveloperRig:
        """Alias for add_screen."""
        return self.add_screen(*nodes)

    def add_content(self, *nodes: Node) -> MultiMonitorDeveloperRig:
        """Alias for add_screen."""
        return self.add_screen(*nodes)


# Semantic alias
DualDeveloperMonitors = MultiMonitorDeveloperRig


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
        self.screen = self.center_screen

        self.add(self.center_screen, self.left_screen)

    def add_screen(self, *nodes: Node) -> VerticalSidecarDisplay:
        self.screen.add_screen(*nodes)
        return self

    def add_screen_content(self, *nodes: Node) -> VerticalSidecarDisplay:
        """Alias for add_screen."""
        return self.add_screen(*nodes)

    def add_content(self, *nodes: Node) -> VerticalSidecarDisplay:
        return self.add_screen(*nodes)


class TripleCurvedSimulatorDeck(Node):
    """
    Triple panoramic wrap-around display cockpit for flight/driving simulator setups.
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

        self.screen = self.center_screen
        self.add(self.left_screen, self.center_screen, self.right_screen)

    def add_screen(self, *nodes: Node) -> TripleCurvedSimulatorDeck:
        self.screen.add_screen(*nodes)
        return self

    def add_screen_content(self, *nodes: Node) -> TripleCurvedSimulatorDeck:
        """Alias for add_screen."""
        return self.add_screen(*nodes)

    def add_content(self, *nodes: Node) -> TripleCurvedSimulatorDeck:
        return self.add_screen(*nodes)


class MultiMonitorSuite:
    """
    Suite factory for multi-monitor developer rigs, vertical sidecars, and triple curved decks.
    """
    @staticmethod
    def developer_rig(left_vertical: bool = True, **kwargs: Any) -> MultiMonitorDeveloperRig:
        return MultiMonitorDeveloperRig(left_vertical=left_vertical, **kwargs)

    @staticmethod
    def dual_monitors(**kwargs: Any) -> DualDeveloperMonitors:
        return DualDeveloperMonitors(**kwargs)

    @staticmethod
    def vertical_sidecar(**kwargs: Any) -> VerticalSidecarDisplay:
        return VerticalSidecarDisplay(**kwargs)

    @staticmethod
    def triple_deck(**kwargs: Any) -> TripleCurvedSimulatorDeck:
        return TripleCurvedSimulatorDeck(**kwargs)

    @staticmethod
    def screen_container(width: float, height: float, **kwargs: Any) -> ScreenContainer:
        return ScreenContainer(width=width, height=height, **kwargs)
