import math
import numpy as np
from typing import Tuple, List
from vibmo.core.vector import Vector2D

class Camera3D:
    """
    A lightweight 3D to 2D projection engine for Vibmo.
    Allows 2D Cairo scenes to render simulated 3D coordinates.
    """
    
    def __init__(self, focal_length: float = 1000.0, center: Tuple[float, float] = (960.0, 540.0)):
        self.focal_length = focal_length
        self.center = center
        
        # Camera rotation (Pitch, Yaw, Roll)
        self.pitch = 0.0
        self.yaw = 0.0
        self.roll = 0.0
        
        # Camera position
        self.position = np.array([0.0, 0.0, -1000.0])
        
    def _get_rotation_matrix(self) -> np.ndarray:
        """Calculates the 3x3 rotation matrix based on pitch, yaw, roll."""
        p, y, r = self.pitch, self.yaw, self.roll
        
        # Pitch (X-axis)
        rx = np.array([
            [1, 0, 0],
            [0, math.cos(p), -math.sin(p)],
            [0, math.sin(p), math.cos(p)]
        ])
        
        # Yaw (Y-axis)
        ry = np.array([
            [math.cos(y), 0, math.sin(y)],
            [0, 1, 0],
            [-math.sin(y), 0, math.cos(y)]
        ])
        
        # Roll (Z-axis)
        rz = np.array([
            [math.cos(r), -math.sin(r), 0],
            [math.sin(r), math.cos(r), 0],
            [0, 0, 1]
        ])
        
        return rz @ ry @ rx
        
    def project(self, points_3d: np.ndarray) -> np.ndarray:
        """
        Projects an N x 3 array of 3D points onto a 2D screen.
        Returns an N x 2 array of 2D points.
        """
        if len(points_3d) == 0:
            return np.zeros((0, 2))
            
        # Shift relative to camera
        shifted = points_3d - self.position
        
        # Apply rotation
        rot_matrix = self._get_rotation_matrix()
        rotated = shifted @ rot_matrix.T
        
        # Perspective projection
        z = rotated[:, 2]
        
        # Prevent division by zero or objects behind the camera
        z = np.maximum(z, 1.0)
        
        x = (rotated[:, 0] * self.focal_length) / z + self.center[0]
        y = (rotated[:, 1] * self.focal_length) / z + self.center[1]
        
        return np.column_stack((x, y))
        
    def project_point(self, x: float, y: float, z: float) -> Tuple[float, float]:
        """Projects a single 3D point."""
        arr = np.array([[x, y, z]])
        proj = self.project(arr)
        return (float(proj[0, 0]), float(proj[0, 1]))
