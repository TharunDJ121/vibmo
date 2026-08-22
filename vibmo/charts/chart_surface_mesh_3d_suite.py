import math
from typing import Any, Callable, List, Tuple
from vibmo.scene.node import Node
from vibmo.core.signal import Signal
from vibmo.core.color import Color, colors

class ElevationColorGradient:
    """Continuous color gradient mapping height to color (Blue valley -> Green plains -> White mountain peaks)."""

    def __init__(self, valley: Color = Color.hex("#1E3A8A"), plains: Color = Color.hex("#10B981"), peaks: Color = Color.hex("#FFFFFF"), min_z: float = -1.0, max_z: float = 1.0):
        self.valley = valley
        self.plains = plains
        self.peaks = peaks
        self.min_z = min_z
        self.max_z = max_z

    def get_color(self, z: float) -> Color:
        # Normalize z
        range_z = self.max_z - self.min_z
        if range_z == 0:
            norm_z = 0.5
        else:
            norm_z = (z - self.min_z) / range_z

        norm_z = max(0.0, min(1.0, norm_z))

        if norm_z < 0.5:
            # Interpolate valley to plains
            return self.valley.lerp(self.plains, norm_z * 2.0)
        else:
            # Interpolate plains to peaks
            return self.plains.lerp(self.peaks, (norm_z - 0.5) * 2.0)

class CameraRotationRig:
    """Smooth interactive azimuth and elevation angle control for 3D rotation."""

    def __init__(self, azimuth: float = math.pi/4, elevation: float = math.pi/6, scale: float = 100.0):
        self.azimuth = Signal(azimuth, "CameraRotationRig.azimuth")
        self.elevation = Signal(elevation, "CameraRotationRig.elevation")
        self.scale = Signal(scale, "CameraRotationRig.scale")

    def project(self, x: float, y: float, z: float) -> Tuple[float, float, float]:
        """Project 3D point to 2D using isometric-like projection based on azimuth and elevation."""
        az = self.azimuth.get()
        el = self.elevation.get()
        s = self.scale.get()

        # Rotate around Z axis (azimuth)
        x_rot = x * math.cos(az) - y * math.sin(az)
        y_rot = x * math.sin(az) + y * math.cos(az)

        # Rotate around X axis (elevation)
        y_rot2 = y_rot * math.cos(el) - z * math.sin(el)
        z_rot2 = y_rot * math.sin(el) + z * math.cos(el)

        # Project to 2D screen space, y is inverted in screen space usually, we'll keep it standard mathematical for now
        # and invert in the draw function if needed. Actually let's just project.
        screen_x = x_rot * s
        screen_y = -y_rot2 * s # negative to point UP in screen coordinates

        return (screen_x, screen_y, z_rot2)


class WireframeContourGrid(Node):
    """Top and bottom projection grid lines showing coordinate reference planes."""

    def __init__(self, rig: CameraRotationRig, size: float = 10.0, grid_steps: int = 10, bottom_z: float = -2.0, top_z: float = 2.0, **kwargs):
        super().__init__(**kwargs)
        self.rig = rig
        self.size = size
        self.grid_steps = grid_steps
        self.bottom_z = bottom_z
        self.top_z = top_z
        self.color = Color.hex("#475569").with_alpha(0.5)

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()

        ctx.set_source_rgba(*self.color.to_cairo())
        ctx.set_line_width(1.0)

        half_size = self.size / 2.0
        step = self.size / self.grid_steps

        for z in [self.bottom_z, self.top_z]:
            # Draw X lines
            for i in range(self.grid_steps + 1):
                y = -half_size + i * step
                x1, y1, _ = self.rig.project(-half_size, y, z)
                x2, y2, _ = self.rig.project(half_size, y, z)

                ctx.move_to(x1, y1)
                ctx.line_to(x2, y2)

            # Draw Y lines
            for i in range(self.grid_steps + 1):
                x = -half_size + i * step
                x1, y1, _ = self.rig.project(x, -half_size, z)
                x2, y2, _ = self.rig.project(x, half_size, z)

                ctx.move_to(x1, y1)
                ctx.line_to(x2, y2)

        ctx.stroke()
        ctx.restore()

        super().draw(ctx, time)

class Animated3DSurfaceMesh(Node):
    """3D isometric wireframe terrain surface mesh representing Z = f(X, Y, t) with rotating elevation peaks."""

    def __init__(
        self,
        rig: CameraRotationRig,
        func: Callable[[float, float, float], float] = lambda x, y, t: math.sin(math.sqrt(x*x + y*y) - t),
        size: float = 10.0,
        resolution: int = 20,
        gradient: ElevationColorGradient = None,
        wireframe_color: Color = Color.hex("#ffffff").with_alpha(0.3),
        **kwargs
    ):
        super().__init__(**kwargs)
        self.rig = rig
        self.func = func
        self.size = size
        self.resolution = resolution
        self.gradient = gradient or ElevationColorGradient()
        self.wireframe_color = wireframe_color

    def draw(self, ctx: Any, time: float = 0.0) -> None:
        ctx.save()

        half_size = self.size / 2.0
        step = self.size / self.resolution

        # Calculate vertices
        vertices = []
        for i in range(self.resolution + 1):
            row = []
            x = -half_size + i * step
            for j in range(self.resolution + 1):
                y = -half_size + j * step
                z = self.func(x, y, time)
                row.append((x, y, z))
            vertices.append(row)

        # Calculate faces and project
        faces = []
        for i in range(self.resolution):
            for j in range(self.resolution):
                v1_3d = vertices[i][j]
                v2_3d = vertices[i+1][j]
                v3_3d = vertices[i+1][j+1]
                v4_3d = vertices[i][j+1]

                v1_2d = self.rig.project(*v1_3d)
                v2_2d = self.rig.project(*v2_3d)
                v3_2d = self.rig.project(*v3_3d)
                v4_2d = self.rig.project(*v4_3d)

                avg_z_depth = (v1_2d[2] + v2_2d[2] + v3_2d[2] + v4_2d[2]) / 4.0
                avg_z_height = (v1_3d[2] + v2_3d[2] + v3_3d[2] + v4_3d[2]) / 4.0

                # We sort by depth (z_rot2). Smaller z_rot2 means it's further away and should be drawn first.
                faces.append({
                    'depth': avg_z_depth,
                    'height': avg_z_height,
                    'points': [(v1_2d[0], v1_2d[1]), (v2_2d[0], v2_2d[1]), (v3_2d[0], v3_2d[1]), (v4_2d[0], v4_2d[1])]
                })

        # Depth sort (Painter's algorithm)
        faces.sort(key=lambda f: f['depth'])

        for face in faces:
            # Fill color
            fill_color = self.gradient.get_color(face['height'])
            ctx.set_source_rgba(*fill_color.to_cairo())

            pts = face['points']
            ctx.move_to(pts[0][0], pts[0][1])
            ctx.line_to(pts[1][0], pts[1][1])
            ctx.line_to(pts[2][0], pts[2][1])
            ctx.line_to(pts[3][0], pts[3][1])
            ctx.close_path()

            ctx.fill_preserve()

            # Wireframe
            ctx.set_source_rgba(*self.wireframe_color.to_cairo())
            ctx.set_line_width(1.0)
            ctx.stroke()

        ctx.restore()
        super().draw(ctx, time)
