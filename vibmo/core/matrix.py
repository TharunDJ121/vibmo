"""
Affine 2D Matrix (3x3) transformations for scene graph hierarchy and camera projections.
"""

from __future__ import annotations
import math
from typing import Tuple, Union, Sequence
from vibmo.core.vector import Vector2D


class Matrix3x3:
    """
    Affine 2D transformation matrix:
    [ a, c, e ]   [ m00, m01, m02 ]
    [ b, d, f ] = [ m10, m11, m12 ]
    [ 0, 0, 1 ]   [ 0,   0,   1   ]
    """

    __slots__ = ("a", "b", "c", "d", "e", "f")

    def __init__(
        self,
        a: float = 1.0,
        b: float = 0.0,
        c: float = 0.0,
        d: float = 1.0,
        e: float = 0.0,
        f: float = 0.0,
    ) -> None:
        self.a = float(a)
        self.b = float(b)
        self.c = float(c)
        self.d = float(d)
        self.e = float(e)
        self.f = float(f)

    @classmethod
    def identity(cls) -> Matrix3x3:
        return cls(1.0, 0.0, 0.0, 1.0, 0.0, 0.0)

    @classmethod
    def translation(cls, tx: float, ty: float) -> Matrix3x3:
        return cls(1.0, 0.0, 0.0, 1.0, tx, ty)

    @classmethod
    def scaling(cls, sx: float, sy: float) -> Matrix3x3:
        return cls(sx, 0.0, 0.0, sy, 0.0, 0.0)

    @classmethod
    def rotation(cls, radians: float) -> Matrix3x3:
        cos_a = math.cos(radians)
        sin_a = math.sin(radians)
        return cls(cos_a, sin_a, -sin_a, cos_a, 0.0, 0.0)

    @classmethod
    def rotation_deg(cls, degrees: float) -> Matrix3x3:
        return cls.rotation(math.radians(degrees))

    @classmethod
    def skew(cls, skew_x_rad: float = 0.0, skew_y_rad: float = 0.0) -> Matrix3x3:
        return cls(1.0, math.tan(skew_y_rad), math.tan(skew_x_rad), 1.0, 0.0, 0.0)

    @classmethod
    def compose(
        cls,
        position: Union[Vector2D, Sequence[float]] = (0.0, 0.0),
        scale: Union[Vector2D, Sequence[float], float] = (1.0, 1.0),
        rotation_rad: float = 0.0,
        rotate_x_rad: float = 0.0,
        rotate_y_rad: float = 0.0,
        anchor: Union[Vector2D, Sequence[float]] = (0.0, 0.0),
        skew_rad: Union[Vector2D, Sequence[float]] = (0.0, 0.0),
    ) -> Matrix3x3:
        """
        Composes a 2.5D local transform (Orthographic Projection):
        Translate(pos) * RotateZ * RotateY * RotateX * Skew * Scale * Translate(-anchor).
        """
        pos = Vector2D.from_any(position)
        sc = Vector2D.from_any(scale)
        anc = Vector2D.from_any(anchor)
        sk = Vector2D.from_any(skew_rad)

        # Build 4x4 matrix for full 3D rotations
        from vibmo.core.matrix import Matrix4x4
        m4 = Matrix4x4.identity()

        # Translate (using 2D translation since we are projecting orthographically)
        m4 = m4 @ Matrix4x4.translation(pos.x, pos.y, 0.0)

        # Rotations Z, Y, X
        if rotation_rad != 0.0:
            m4 = m4 @ Matrix4x4.rotation_z(rotation_rad)
        if rotate_y_rad != 0.0:
            m4 = m4 @ Matrix4x4.rotation_y(rotate_y_rad)
        if rotate_x_rad != 0.0:
            m4 = m4 @ Matrix4x4.rotation_x(rotate_x_rad)

        # Skew (handled via 2D matrix, injected into top-left 2x2)
        if sk.x != 0.0 or sk.y != 0.0:
            skew_m4 = Matrix4x4([
                1.0, math.tan(sk.y), 0.0, 0.0,
                math.tan(sk.x), 1.0, 0.0, 0.0,
                0.0, 0.0, 1.0, 0.0,
                0.0, 0.0, 0.0, 1.0,
            ])
            m4 = m4 @ skew_m4

        # Scale
        if sc.x != 1.0 or sc.y != 1.0:
            m4 = m4 @ Matrix4x4.scaling(sc.x, sc.y, 1.0)

        # Anchor
        if anc.x != 0.0 or anc.y != 0.0:
            m4 = m4 @ Matrix4x4.translation(-anc.x, -anc.y, 0.0)

        # Extract 3x3 affine matrix from the 4x4 orthographic result
        # a, b, c, d are the 2x2 linear transform
        # e, f are the translation
        a = m4.m[0]
        b = m4.m[4]
        c = m4.m[1]
        d = m4.m[5]
        e = m4.m[3]
        f = m4.m[7]

        return cls(a, b, c, d, e, f)

    def multiply(self, other: Matrix3x3) -> Matrix3x3:
        """Matrix multiplication: self * other."""
        return Matrix3x3(
            a=self.a * other.a + self.c * other.b,
            b=self.b * other.a + self.d * other.b,
            c=self.a * other.c + self.c * other.d,
            d=self.b * other.c + self.d * other.d,
            e=self.a * other.e + self.c * other.f + self.e,
            f=self.b * other.e + self.d * other.f + self.f,
        )

    __matmul__ = multiply

    def transform_point(self, point: Union[Vector2D, Sequence[float]]) -> Vector2D:
        p = Vector2D.from_any(point)
        return Vector2D(
            self.a * p.x + self.c * p.y + self.e,
            self.b * p.x + self.d * p.y + self.f,
        )

    def transform_vector(self, vec: Union[Vector2D, Sequence[float]]) -> Vector2D:
        """Transforms direction vector (ignores translation component e, f)."""
        v = Vector2D.from_any(vec)
        return Vector2D(
            self.a * v.x + self.c * v.y,
            self.b * v.x + self.d * v.y,
        )

    @property
    def determinant(self) -> float:
        return self.a * self.d - self.b * self.c

    def inverse(self) -> Matrix3x3:
        det = self.determinant
        if abs(det) < 1e-12:
            raise ValueError("Cannot invert singular 3x3 matrix")
        inv_det = 1.0 / det
        return Matrix3x3(
            a=self.d * inv_det,
            b=-self.b * inv_det,
            c=-self.c * inv_det,
            d=self.a * inv_det,
            e=(self.c * self.f - self.d * self.e) * inv_det,
            f=(self.b * self.e - self.a * self.f) * inv_det,
        )

    def to_cairo_tuple(self) -> Tuple[float, float, float, float, float, float]:
        """Returns (xx, yx, xy, yy, x0, y0) format expected by Cairo matrix."""
        return (self.a, self.b, self.c, self.d, self.e, self.f)

    def __repr__(self) -> str:
        return f"Matrix3x3([[{self.a:.3f}, {self.c:.3f}, {self.e:.3f}], [{self.b:.3f}, {self.d:.3f}, {self.f:.3f}], [0, 0, 1]])"


class Matrix4x4:
    """
    4x4 Matrix for 3D transformations (translation, rotation, scaling, perspective projection).
    Stored in row-major order.
    """
    __slots__ = ("m",)

    def __init__(self, values: Optional[Sequence[float]] = None) -> None:
        if values is None:
            self.m = [
                1.0, 0.0, 0.0, 0.0,
                0.0, 1.0, 0.0, 0.0,
                0.0, 0.0, 1.0, 0.0,
                0.0, 0.0, 0.0, 1.0,
            ]
        else:
            self.m = list(values)

    @classmethod
    def identity(cls) -> Matrix4x4:
        return cls()

    @classmethod
    def translation(cls, tx: float, ty: float, tz: float) -> Matrix4x4:
        return cls([
            1.0, 0.0, 0.0, float(tx),
            0.0, 1.0, 0.0, float(ty),
            0.0, 0.0, 1.0, float(tz),
            0.0, 0.0, 0.0, 1.0,
        ])

    @classmethod
    def scaling(cls, sx: float, sy: float, sz: float) -> Matrix4x4:
        return cls([
            float(sx), 0.0, 0.0, 0.0,
            0.0, float(sy), 0.0, 0.0,
            0.0, 0.0, float(sz), 0.0,
            0.0, 0.0, 0.0, 1.0,
        ])

    @classmethod
    def rotation_x(cls, radians: float) -> Matrix4x4:
        c, s = math.cos(radians), math.sin(radians)
        return cls([
            1.0, 0.0, 0.0, 0.0,
            0.0, c, -s, 0.0,
            0.0, s, c, 0.0,
            0.0, 0.0, 0.0, 1.0,
        ])

    @classmethod
    def rotation_y(cls, radians: float) -> Matrix4x4:
        c, s = math.cos(radians), math.sin(radians)
        return cls([
            c, 0.0, s, 0.0,
            0.0, 1.0, 0.0, 0.0,
            -s, 0.0, c, 0.0,
            0.0, 0.0, 0.0, 1.0,
        ])

    @classmethod
    def rotation_z(cls, radians: float) -> Matrix4x4:
        c, s = math.cos(radians), math.sin(radians)
        return cls([
            c, -s, 0.0, 0.0,
            s, c, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            0.0, 0.0, 0.0, 1.0,
        ])

    def multiply(self, other: Matrix4x4) -> Matrix4x4:
        a = self.m
        b = other.m
        res = [0.0] * 16
        for r in range(4):
            for c in range(4):
                res[r * 4 + c] = (
                    a[r * 4 + 0] * b[0 * 4 + c] +
                    a[r * 4 + 1] * b[1 * 4 + c] +
                    a[r * 4 + 2] * b[2 * 4 + c] +
                    a[r * 4 + 3] * b[3 * 4 + c]
                )
        return Matrix4x4(res)

    __matmul__ = multiply

    @classmethod
    def perspective(cls, fov_y_rad: float, aspect_ratio: float, near: float, far: float) -> Matrix4x4:
        f = 1.0 / math.tan(fov_y_rad / 2.0)
        range_inv = 1.0 / (near - far)
        return cls([
            f / aspect_ratio, 0.0, 0.0, 0.0,
            0.0, f, 0.0, 0.0,
            0.0, 0.0, (near + far) * range_inv, (2.0 * near * far) * range_inv,
            0.0, 0.0, -1.0, 0.0,
        ])

    def transform_point(self, point: Union['Vector3D', Sequence[float]]) -> 'Vector3D':
        """Transforms a 3D point and applies perspective divide (w)."""
        from vibmo.core.vector import Vector3D
        if not isinstance(point, Vector3D):
            p = Vector3D(point[0], point[1], point[2])
        else:
            p = point

        a = self.m
        x = a[0] * p.x + a[1] * p.y + a[2] * p.z + a[3]
        y = a[4] * p.x + a[5] * p.y + a[6] * p.z + a[7]
        z = a[8] * p.x + a[9] * p.y + a[10] * p.z + a[11]
        w = a[12] * p.x + a[13] * p.y + a[14] * p.z + a[15]

        if w != 1.0 and w != 0.0:
            x /= w
            y /= w
            z /= w

        return Vector3D(x, y, z)
