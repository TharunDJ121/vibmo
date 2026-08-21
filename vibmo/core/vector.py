"""
Vector mathematics for 2D and 3D spatial operations in Vibmo.
"""

from __future__ import annotations
import math
from typing import Tuple, Union, Sequence


class Vector2D:
    """Represents a 2D vector with full arithmetic and geometric operations."""

    __slots__ = ("x", "y")

    def __init__(self, x: float = 0.0, y: float = 0.0) -> None:
        self.x = float(x)
        self.y = float(y)

    @classmethod
    def zero(cls) -> Vector2D:
        return cls(0.0, 0.0)

    @classmethod
    def one(cls) -> Vector2D:
        return cls(1.0, 1.0)

    @classmethod
    def from_polar(cls, radius: float, angle_rad: float) -> Vector2D:
        return cls(radius * math.cos(angle_rad), radius * math.sin(angle_rad))

    @classmethod
    def from_angle_deg(cls, radius: float, angle_deg: float) -> Vector2D:
        rad = math.radians(angle_deg)
        return cls(radius * math.cos(rad), radius * math.sin(rad))

    @classmethod
    def from_any(cls, val: Union[Vector2D, Sequence[float], float, int]) -> Vector2D:
        if isinstance(val, Vector2D):
            return cls(val.x, val.y)
        if isinstance(val, (int, float)):
            return cls(float(val), float(val))
        if isinstance(val, (tuple, list)) and len(val) >= 2:
            return cls(float(val[0]), float(val[1]))
        if isinstance(val, (tuple, list)) and len(val) == 1:
            return cls(float(val[0]), float(val[0]))
        raise ValueError(f"Cannot convert {val} of type {type(val)} to Vector2D")

    @property
    def magnitude(self) -> float:
        return math.hypot(self.x, self.y)

    @property
    def magnitude_sq(self) -> float:
        return self.x * self.x + self.y * self.y

    length = magnitude
    length_sq = magnitude_sq

    def normalize(self) -> Vector2D:
        m = self.magnitude
        if m < 1e-12:
            return Vector2D.zero()
        return Vector2D(self.x / m, self.y / m)

    def dot(self, other: Vector2D) -> float:
        return self.x * other.x + self.y * other.y

    def cross(self, other: Vector2D) -> float:
        """2D cross product returns scalar z-component."""
        return self.x * other.y - self.y * other.x

    def distance_to(self, other: Vector2D) -> float:
        return math.hypot(self.x - other.x, self.y - other.y)

    def angle(self) -> float:
        """Returns counter-clockwise angle in radians from positive X axis."""
        return math.atan2(self.y, self.x)

    def angle_deg(self) -> float:
        return math.degrees(self.angle())

    def angle_to(self, other: Vector2D) -> float:
        return math.atan2(self.cross(other), self.dot(other))

    def rotate(self, radians: float) -> Vector2D:
        cos_a = math.cos(radians)
        sin_a = math.sin(radians)
        return Vector2D(
            self.x * cos_a - self.y * sin_a,
            self.x * sin_a + self.y * cos_a
        )

    def rotate_deg(self, degrees: float) -> Vector2D:
        return self.rotate(math.radians(degrees))

    def lerp(self, target: Vector2D, t: float) -> Vector2D:
        return Vector2D(
            self.x + (target.x - self.x) * t,
            self.y + (target.y - self.y) * t
        )

    def __add__(self, other: Union[Vector2D, Sequence[float], float, int]) -> Vector2D:
        o = Vector2D.from_any(other)
        return Vector2D(self.x + o.x, self.y + o.y)

    def __radd__(self, other: Union[Vector2D, Sequence[float], float, int]) -> Vector2D:
        return self.__add__(other)

    def __sub__(self, other: Union[Vector2D, Sequence[float], float, int]) -> Vector2D:
        o = Vector2D.from_any(other)
        return Vector2D(self.x - o.x, self.y - o.y)

    def __rsub__(self, other: Union[Vector2D, Sequence[float], float, int]) -> Vector2D:
        o = Vector2D.from_any(other)
        return Vector2D(o.x - self.x, o.y - self.y)

    def __mul__(self, scalar: Union[float, int, Vector2D, Sequence[float]]) -> Vector2D:
        if isinstance(scalar, (int, float)):
            return Vector2D(self.x * scalar, self.y * scalar)
        o = Vector2D.from_any(scalar)
        return Vector2D(self.x * o.x, self.y * o.y)

    def __rmul__(self, scalar: Union[float, int, Vector2D, Sequence[float]]) -> Vector2D:
        return self.__mul__(scalar)

    def __truediv__(self, scalar: Union[float, int, Vector2D, Sequence[float]]) -> Vector2D:
        if isinstance(scalar, (int, float)):
            if abs(scalar) < 1e-12:
                raise ZeroDivisionError("Division by zero in Vector2D")
            return Vector2D(self.x / scalar, self.y / scalar)
        o = Vector2D.from_any(scalar)
        return Vector2D(self.x / o.x, self.y / o.y)

    def __neg__(self) -> Vector2D:
        return Vector2D(-self.x, -self.y)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, (Vector2D, tuple, list)):
            return False
        try:
            o = Vector2D.from_any(other)
            return math.isclose(self.x, o.x, abs_tol=1e-9) and math.isclose(self.y, o.y, abs_tol=1e-9)
        except Exception:
            return False

    def __iter__(self):
        yield self.x
        yield self.y

    def __getitem__(self, index: int) -> float:
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        raise IndexError("Vector2D index out of range (must be 0 or 1)")

    def __len__(self) -> int:
        return 2

    def to_tuple(self) -> Tuple[float, float]:
        return (self.x, self.y)

    def __repr__(self) -> str:
        return f"Vector2D({self.x:.3f}, {self.y:.3f})"


class Vector3D:
    """Represents a 3D vector with spatial mathematics."""

    __slots__ = ("x", "y", "z")

    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> None:
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    @classmethod
    def zero(cls) -> Vector3D:
        return cls(0.0, 0.0, 0.0)

    @property
    def magnitude(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def normalize(self) -> Vector3D:
        m = self.magnitude
        if m < 1e-12:
            return Vector3D.zero()
        return Vector3D(self.x / m, self.y / m, self.z / m)

    def dot(self, other: Vector3D) -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other: Vector3D) -> Vector3D:
        return Vector3D(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

    def lerp(self, target: Vector3D, t: float) -> Vector3D:
        return Vector3D(
            self.x + (target.x - self.x) * t,
            self.y + (target.y - self.y) * t,
            self.z + (target.z - self.z) * t
        )

    def __add__(self, other: Vector3D) -> Vector3D:
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: Vector3D) -> Vector3D:
        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: float) -> Vector3D:
        return Vector3D(self.x * scalar, self.y * scalar, self.z * scalar)

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z

    def __repr__(self) -> str:
        return f"Vector3D({self.x:.3f}, {self.y:.3f}, {self.z:.3f})"
