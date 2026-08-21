"""
Cinematic 2D & 3D Camera system with 3D Orbit, Rack Focus (DoF), Parallax, and Screen Shake.
"""

from __future__ import annotations
import math
from typing import Any, List, Optional, Sequence, Tuple, Union
from vibmo.core.vector import Vector2D
from vibmo.core.matrix import Matrix3x3
from vibmo.core.signal import Signal, AnimationAction
from vibmo.core.easing import Ease, EasingFunc


class _CameraFollowBinding:
    def __init__(self, target_node: Any, scene_width: float = 1920.0, scene_height: float = 1080.0):
        self.target_node = target_node
        self.cx = scene_width * 0.5
        self.cy = scene_height * 0.5

    def __call__(self, t: float) -> Vector2D:
        bx, by, bw, bh = self.target_node.world_bounds(t)
        node_center_x = bx + bw * 0.5
        node_center_y = by + bh * 0.5
        return Vector2D(node_center_x - self.cx, node_center_y - self.cy)


class Camera3D:
    """
    Cinematic 3D Camera with 3D Orbit, Parallax, Depth-of-Field (Rack Focus), and Screen Shake.
    """

    def __init__(
        self,
        position: Union[Vector2D, Sequence[float]] = (0.0, 0.0),
        zoom: float = 1.0,
        rotation: float = 0.0,
        yaw: float = 0.0,
        pitch: float = 0.0,
        roll: float = 0.0,
        focal_distance: float = 0.0,
        aperture: float = 0.0,
        scene_width: float = 1920.0,
        scene_height: float = 1080.0,
    ) -> None:
        self.scene_width = float(scene_width)
        self.scene_height = float(scene_height)
        
        # 2D & Spatial Pan/Zoom
        self.position = Signal(Vector2D.from_any(position), "camera.position")
        self.zoom = Signal(float(zoom), "camera.zoom")
        self.rotation = Signal(float(rotation), "camera.rotation")

        # 3D Orbit Angles (in radians)
        self.yaw = Signal(float(yaw), "camera.yaw")
        self.pitch = Signal(float(pitch), "camera.pitch")
        self.roll = Signal(float(roll), "camera.roll")

        # Depth of Field & Rack Focus
        self.focal_distance = Signal(float(focal_distance), "camera.focal_distance")
        self.aperture = Signal(float(aperture), "camera.aperture")

        self._shake_effects: List[tuple] = []

    def _resolve_target_pos(self, target: Any, time: float = 0.0) -> Vector2D:
        """Resolves target offset relative to canvas center."""
        cx = self.scene_width * 0.5
        cy = self.scene_height * 0.5
        if hasattr(target, "world_bounds"):
            bx, by, bw, bh = target.world_bounds(time)
            node_center_x = bx + bw * 0.5
            node_center_y = by + bh * 0.5
            return Vector2D(node_center_x - cx, node_center_y - cy)
        elif hasattr(target, "position"):
            pos = target.position.get(time)
            return Vector2D(pos.x - cx, pos.y - cy)
        else:
            p = Vector2D.from_any(target)
            return Vector2D(p.x - cx, p.y - cy)

    def zoom_to(
        self,
        target: Union[float, Any] = 1.5,
        zoom: Optional[float] = None,
        duration: float = 0.8,
        ease: EasingFunc = Ease.out_expo,
        delay: float = 0.0,
    ) -> Union[AnimationAction, List[AnimationAction]]:
        """
        Zooms and centers camera onto a target Node or coordinate.
        """
        if isinstance(target, (int, float)) and zoom is None:
            return self.zoom.to(float(target), duration=duration, ease=ease, delay=delay)

        target_zoom = zoom if zoom is not None else 1.8
        target_pos = self._resolve_target_pos(target)
        
        return [
            self.zoom.to(target_zoom, duration=duration, ease=ease, delay=delay),
            self.position.to(target_pos, duration=duration, ease=ease, delay=delay),
        ]

    def pan_to(
        self,
        target: Any,
        duration: float = 0.8,
        ease: EasingFunc = Ease.out_expo,
        delay: float = 0.0,
    ) -> AnimationAction:
        """Smoothly pans camera focus point to a Node or (x, y) coordinate."""
        target_pos = self._resolve_target_pos(target)
        return self.position.to(target_pos, duration=duration, ease=ease, delay=delay)

    def orbit(
        self,
        yaw: float = 0.0,
        pitch: float = 0.0,
        duration: float = 1.0,
        ease: EasingFunc = Ease.out_expo,
        delay: float = 0.0,
    ) -> List[AnimationAction]:
        """Orbits the 3D camera angles smoothly around the scene center."""
        return [
            self.yaw.to(float(yaw), duration=duration, ease=ease, delay=delay),
            self.pitch.to(float(pitch), duration=duration, ease=ease, delay=delay),
        ]

    def rack_focus(
        self,
        target: Any,
        aperture: float = 0.08,
        duration: float = 0.8,
        ease: EasingFunc = Ease.out_expo,
        delay: float = 0.0,
    ) -> Any:
        """
        Performs a cinematic rack focus onto target Node, setting focal distance and lens aperture.
        """
        from vibmo.timeline.scheduler import ParallelGroup
        actions = [self.aperture.to(float(aperture), duration=duration, ease=ease, delay=delay)]
        if hasattr(target, "z"):
            actions.append(self.focal_distance.to(float(target.z.get()), duration=duration, ease=ease, delay=delay))
        return ParallelGroup(actions)

    def reset(
        self,
        duration: float = 0.8,
        ease: EasingFunc = Ease.out_expo,
        delay: float = 0.0,
    ) -> Any:
        """Pulls camera back to default full canvas view (zoom=1.0, position=(0,0), angles=0)."""
        from vibmo.timeline.scheduler import ParallelGroup
        return ParallelGroup([
            self.zoom.to(1.0, duration=duration, ease=ease, delay=delay),
            self.position.to(Vector2D(0.0, 0.0), duration=duration, ease=ease, delay=delay),
            self.rotation.to(0.0, duration=duration, ease=ease, delay=delay),
            self.yaw.to(0.0, duration=duration, ease=ease, delay=delay),
            self.pitch.to(0.0, duration=duration, ease=ease, delay=delay),
        ])

    def follow(self, target_node: Any) -> None:
        """Binds camera position to dynamically track a moving node."""
        self.position.bind(_CameraFollowBinding(target_node, self.scene_width, self.scene_height))

    def shake(
        self,
        amplitude: float = 15.0,
        duration: float = 0.4,
        frequency: float = 25.0,
        start_time: float = 0.0,
    ) -> AnimationAction:
        """Adds a damped procedural screen shake with true exponential one-shot decay."""
        self._shake_effects.append((amplitude, duration, frequency, start_time))
        from vibmo.core.easing import Ease
        return self.position.to(self.position.get(start_time), duration=duration, ease=Ease.linear, delay=start_time)

    def get_shake_offset(self, time: float) -> Vector2D:
        ox, oy = 0.0, 0.0
        for amp, dur, freq, start_time in self._shake_effects:
            dt = time - start_time
            if 0.0 <= dt <= dur:
                decay = math.exp(-3.0 * (dt / max(1e-4, dur)))
                ox += math.sin(dt * freq) * amp * decay
                oy += math.cos(dt * freq * 1.3) * amp * decay
        return Vector2D(ox, oy)


    def view_matrix(self, scene_width: float, scene_height: float, time: float = 0.0) -> Matrix3x3:
        self.scene_width = scene_width
        self.scene_height = scene_height
        cx = scene_width * 0.5
        cy = scene_height * 0.5
        pos = self.position.get(time) + self.get_shake_offset(time)
        z = max(1e-4, float(self.zoom.get(time)))
        rot = float(self.rotation.get(time))
        yaw_val = float(self.yaw.get(time))
        pitch_val = float(self.pitch.get(time))

        # Combine 2D pan/zoom with 3D tilt offset
        tilt_x = math.sin(yaw_val) * (scene_width * 0.25)
        tilt_y = -math.sin(pitch_val) * (scene_height * 0.25)

        m = Matrix3x3.translation(cx + tilt_x, cy + tilt_y)
        if rot != 0.0:
            m = m.multiply(Matrix3x3.rotation(rot))
        if z != 1.0:
            m = m.multiply(Matrix3x3.scaling(z, z))
        m = m.multiply(Matrix3x3.translation(-cx - pos.x, -cy - pos.y))
        return m


Camera2D = Camera3D
Camera = Camera3D
