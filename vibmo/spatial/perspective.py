"""
2.5D Depth, 3D Perspective Projection, and Homography Quad Warping.
"""

from __future__ import annotations
import math
from typing import Any, List, Optional, Sequence, Tuple, Union
import numpy as np
from PIL import Image
import cairo

from vibmo.core.vector import Vector2D


def find_perspective_coeffs(
    src_points: Sequence[Tuple[float, float]],
    dst_points: Sequence[Tuple[float, float]],
) -> List[float]:
    """
    Computes 8 coefficients (a, b, c, d, e, f, g, h) for PIL Image.Transform.PERSPECTIVE
    mapping destination pixel coordinates back to source texture coordinates.
    """
    matrix = []
    for (src_x, src_y), (dst_x, dst_y) in zip(src_points, dst_points):
        # We solve for dst -> src mapping for backward texture sampling
        matrix.append([dst_x, dst_y, 1, 0, 0, 0, -dst_x * src_x, -dst_y * src_x])
        matrix.append([0, 0, 0, dst_x, dst_y, 1, -dst_x * src_y, -dst_y * src_y])

    A = np.array(matrix, dtype=np.float64)
    B = np.array([pt for p in src_points for pt in p], dtype=np.float64)
    try:
        res = np.linalg.solve(A, B)
        return list(res)
    except np.linalg.LinAlgError:
        return [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0]


class Matrix3D:
    """4x4 Homogeneous Transformation Matrix for 2.5D/3D perspective projection."""

    def __init__(self, mat: Optional[np.ndarray] = None) -> None:
        if mat is not None:
            self.mat = mat.astype(np.float32)
        else:
            self.mat = np.eye(4, dtype=np.float32)

    @classmethod
    def identity(cls) -> Matrix3D:
        return cls(np.eye(4, dtype=np.float32))

    @classmethod
    def translation(cls, tx: float, ty: float, tz: float = 0.0) -> Matrix3D:
        m = np.eye(4, dtype=np.float32)
        m[0, 3] = tx
        m[1, 3] = ty
        m[2, 3] = tz
        return cls(m)

    @classmethod
    def scale(cls, sx: float, sy: float, sz: float = 1.0) -> Matrix3D:
        m = np.eye(4, dtype=np.float32)
        m[0, 0] = sx
        m[1, 1] = sy
        m[2, 2] = sz
        return cls(m)

    @classmethod
    def rotation_x(cls, rad: float) -> Matrix3D:
        m = np.eye(4, dtype=np.float32)
        c, s = math.cos(rad), math.sin(rad)
        m[1, 1] = c
        m[1, 2] = -s
        m[2, 1] = s
        m[2, 2] = c
        return cls(m)

    @classmethod
    def rotation_y(cls, rad: float) -> Matrix3D:
        m = np.eye(4, dtype=np.float32)
        c, s = math.cos(rad), math.sin(rad)
        m[0, 0] = c
        m[0, 2] = s
        m[2, 0] = -s
        m[2, 2] = c
        return cls(m)

    @classmethod
    def rotation_z(cls, rad: float) -> Matrix3D:
        m = np.eye(4, dtype=np.float32)
        c, s = math.cos(rad), math.sin(rad)
        m[0, 0] = c
        m[0, 1] = -s
        m[1, 0] = s
        m[1, 1] = c
        return cls(m)

    @classmethod
    def perspective(cls, d: float = 1200.0) -> Matrix3D:
        """Applies true perspective foreshortening for focal distance d."""
        m = np.eye(4, dtype=np.float32)
        if d > 0:
            m[3, 2] = -1.0 / float(d)
        return cls(m)

    def multiply(self, other: Matrix3D) -> Matrix3D:
        return Matrix3D(np.matmul(self.mat, other.mat))

    def __matmul__(self, other: Matrix3D) -> Matrix3D:
        return self.multiply(other)

    def project_point(self, x: float, y: float, z: float = 0.0) -> Tuple[float, float, float]:
        """Transforms a 3D point and applies perspective divide."""
        v = np.array([x, y, z, 1.0], dtype=np.float32)
        res = np.matmul(self.mat, v)
        w = res[3]
        if abs(w) > 1e-6:
            return (float(res[0] / w), float(res[1] / w), float(res[2] / w))
        return (float(res[0]), float(res[1]), float(res[2]))


class Projective3DWarp:
    """
    Renders an offscreen Cairo surface to canvas with true 3D projective perspective distortion.
    """

    @staticmethod
    def project_quad(
        local_bounds: Tuple[float, float, float, float],
        pos: Vector2D,
        scale: Vector2D,
        rotation_z: float,
        rotate_x: float,
        rotate_y: float,
        anchor: Vector2D,
        focal_dist: float = 1200.0,
    ) -> List[Tuple[float, float]]:
        """
        Projects 4 rectangular corners into screen space using full 3D rotation and perspective.
        """
        lx, ly, lw, lh = local_bounds
        # 4 Local Corners: Top-Left, Top-Right, Bottom-Right, Bottom-Left
        corners = [
            (lx, ly, 0.0),
            (lx + lw, ly, 0.0),
            (lx + lw, ly + lh, 0.0),
            (lx, ly + lh, 0.0),
        ]

        # Build complete 3D Model matrix
        # Translate(pos) * Perspective * RotateZ * RotateY * RotateX * Scale * Translate(-anchor)
        m = Matrix3D.translation(pos.x, pos.y, 0.0)
        m = m.multiply(Matrix3D.perspective(focal_dist))
        if rotation_z != 0.0:
            m = m.multiply(Matrix3D.rotation_z(rotation_z))
        if rotate_y != 0.0:
            m = m.multiply(Matrix3D.rotation_y(rotate_y))
        if rotate_x != 0.0:
            m = m.multiply(Matrix3D.rotation_x(rotate_x))
        if scale.x != 1.0 or scale.y != 1.0:
            m = m.multiply(Matrix3D.scale(scale.x, scale.y, 1.0))
        if anchor.x != 0.0 or anchor.y != 0.0:
            m = m.multiply(Matrix3D.translation(-anchor.x, -anchor.y, 0.0))

        projected = []
        for cx, cy, cz in corners:
            px, py, _ = m.project_point(cx, cy, cz)
            projected.append((px, py))

        return projected

