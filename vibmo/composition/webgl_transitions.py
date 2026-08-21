"""
WebGL2-based transition engine for high-performance GPU transitions.
Inspired by Remotion's HTML-in-canvas transition system.
"""

from __future__ import annotations
import numpy as np
from typing import Any, Callable, Optional, Tuple, Union
from dataclasses import dataclass
import ctypes

try:
    import OpenGL.GL as gl
    import OpenGL.GL.shaders as shaders
    WEBGL_AVAILABLE = True
except ImportError:
    WEBGL_AVAILABLE = False
    print("Warning: OpenGL not available, falling back to CPU transitions")


@dataclass
class ShaderParams:
    """Parameters for shader-based transitions."""
    prev_image: np.ndarray
    next_image: np.ndarray
    width: int
    height: int
    time: float
    custom_params: dict[str, Any]


class WebGL2TransitionEngine:
    """
    WebGL2 context manager for GPU-accelerated transitions.
    Handles shader compilation, texture management, and frame buffer operations.
    """
    
    def __init__(self, width: int = 1920, height: int = 1080):
        self.width = width
        self.height = height
        self.context = None
        self.program = None
        self.prev_texture = None
        self.next_texture = None
        self.framebuffer = None
        self.vertex_array = None
        self.initialized = False
        
    def initialize(self) -> bool:
        """Initialize WebGL2 context and resources."""
        if not WEBGL_AVAILABLE:
            return False
            
        try:
            # Create OpenGL context (simplified - in production would use proper context creation)
            self.context = True  # Placeholder for actual context
            self.initialized = True
            return True
        except Exception as e:
            print(f"WebGL2 initialization failed: {e}")
            return False
    
    def compile_shader(self, source: str, shader_type: int) -> Optional[int]:
        """Compile a shader from source code."""
        if not self.initialized:
            return None
            
        try:
            shader = gl.glCreateShader(shader_type)
            gl.glShaderSource(shader, source)
            gl.glCompileShader(shader)
            
            # Check compilation status
            if gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS) != gl.GL_TRUE:
                error_log = gl.glGetShaderInfoLog(shader)
                gl.glDeleteShader(shader)
                raise RuntimeError(f"Shader compilation failed: {error_log}")
                
            return shader
        except Exception as e:
            print(f"Shader compilation error: {e}")
            return None
    
    def create_program(self, vertex_shader: str, fragment_shader: str) -> Optional[int]:
        """Create and link a shader program."""
        if not self.initialized:
            return None
            
        try:
            vs = self.compile_shader(vertex_shader, gl.GL_VERTEX_SHADER)
            fs = self.compile_shader(fragment_shader, gl.GL_FRAGMENT_SHADER)
            
            if vs is None or fs is None:
                return None
                
            program = gl.glCreateProgram()
            gl.glAttachShader(program, vs)
            gl.glAttachShader(program, fs)
            gl.glLinkProgram(program)
            
            # Check link status
            if gl.glGetProgramiv(program, gl.GL_LINK_STATUS) != gl.GL_TRUE:
                error_log = gl.glGetProgramInfoLog(program)
                gl.glDeleteProgram(program)
                raise RuntimeError(f"Program linking failed: {error_log}")
                
            # Clean up shaders (they're now part of the program)
            gl.glDeleteShader(vs)
            gl.glDeleteShader(fs)
            
            return program
        except Exception as e:
            print(f"Program creation error: {e}")
            return None
    
    def create_texture(self, image: np.ndarray) -> Optional[int]:
        """Create OpenGL texture from numpy array."""
        if not self.initialized:
            return None
            
        try:
            texture = gl.glGenTextures(1)
            gl.glBindTexture(gl.GL_TEXTURE_2D, texture[0])
            
            # Set texture parameters
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
            
            # Upload texture data
            if len(image.shape) == 3:
                h, w, c = image.shape
                if c == 4:  # RGBA
                    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, w, h, 0, 
                                   gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, image)
                elif c == 3:  # RGB
                    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, w, h, 0, 
                                   gl.GL_RGB, gl.GL_UNSIGNED_BYTE, image)
            else:
                # Grayscale
                h, w = image.shape
                gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RED, w, h, 0, 
                               gl.GL_RED, gl.GL_UNSIGNED_BYTE, image)
                
            return texture[0]
        except Exception as e:
            print(f"Texture creation error: {e}")
            return None
    
    def update_texture(self, texture_id: int, image: np.ndarray) -> bool:
        """Update existing texture with new image data."""
        if not self.initialized:
            return False
            
        try:
            gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)
            
            if len(image.shape) == 3:
                h, w, c = image.shape
                if c == 4:
                    gl.glTexSubImage2D(gl.GL_TEXTURE_2D, 0, 0, 0, w, h, 
                                      gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, image)
                elif c == 3:
                    gl.glTexSubImage2D(gl.GL_TEXTURE_2D, 0, 0, 0, w, h, 
                                      gl.GL_RGB, gl.GL_UNSIGNED_BYTE, image)
            else:
                h, w = image.shape
                gl.glTexSubImage2D(gl.GL_TEXTURE_2D, 0, 0, 0, w, h, 
                                  gl.GL_RED, gl.GL_UNSIGNED_BYTE, image)
            return True
        except Exception as e:
            print(f"Texture update error: {e}")
            return False
    
    def render_transition(self, params: ShaderParams) -> Optional[np.ndarray]:
        """Render a transition frame using GPU."""
        if not self.initialized:
            return None
            
        try:
            # This is a simplified version - actual implementation would:
            # 1. Bind shader program
            # 2. Set uniforms (time, custom params)
            # 3. Bind textures
            # 4. Draw fullscreen quad
            # 5. Read back framebuffer to numpy array
            
            # Placeholder for actual GPU rendering
            return self._cpu_fallback(params)
        except Exception as e:
            print(f"GPU rendering error: {e}")
            return self._cpu_fallback(params)
    
    def _cpu_fallback(self, params: ShaderParams) -> np.ndarray:
        """CPU fallback when GPU rendering fails."""
        # Simple crossfade as fallback
        p = max(0.0, min(1.0, params.time))
        return (params.prev_image.astype(np.float32) * (1.0 - p) + 
                params.next_image.astype(np.float32) * p).astype(np.uint8)
    
    def cleanup(self):
        """Clean up OpenGL resources."""
        if not self.initialized:
            return
            
        try:
            if self.program:
                gl.glDeleteProgram(self.program)
            if self.prev_texture:
                gl.glDeleteTextures([self.prev_texture])
            if self.next_texture:
                gl.glDeleteTextures([self.next_texture])
            if self.framebuffer:
                gl.glDeleteFramebuffers([self.framebuffer])
            if self.vertex_array:
                gl.glDeleteVertexArrays([self.vertex_array])
            self.initialized = False
        except Exception as e:
            print(f"Cleanup error: {e}")


class ShaderTransition:
    """
    Base class for shader-based transitions.
    Provides common shader templates and utility functions.
    """
    
    # Common vertex shader for fullscreen quad
    VERTEX_SHADER = """
    #version 330 core
    layout (location = 0) in vec2 a_pos;
    layout (location = 1) in vec2 a_uv;
    out vec2 v_uv;
    
    void main() {
        v_uv = a_uv;
        gl_Position = vec4(a_pos, 0.0, 1.0);
    }
    """
    
    @staticmethod
    def create_fullscreen_quad() -> Tuple[np.ndarray, np.ndarray]:
        """Create vertex and UV data for fullscreen quad."""
        # Triangle strip for fullscreen quad
        vertices = np.array([
            -1.0, -1.0,  # Bottom-left
             1.0, -1.0,  # Bottom-right
            -1.0,  1.0,  # Top-left
             1.0,  1.0,  # Top-right
        ], dtype=np.float32)
        
        uvs = np.array([
            0.0, 0.0,  # Bottom-left
            1.0, 0.0,  # Bottom-right
            0.0, 1.0,  # Top-left
            1.0, 1.0,  # Top-right
        ], dtype=np.float32)
        
        return vertices, uvs
    
    @staticmethod
    def mix_color(color1: np.ndarray, color2: np.ndarray, t: float) -> np.ndarray:
        """Linear interpolation between two colors."""
        return color1 * (1.0 - t) + color2 * t
    
    @staticmethod
    def smooth_step(edge0: float, edge1: float, x: float) -> float:
        """Smooth step function for smooth transitions."""
        t = np.clip((x - edge0) / (edge1 - edge0), 0.0, 1.0)
        return t * t * (3.0 - 2.0 * t)


# Default shader templates for common transitions

class CrossFadeShader:
    """Simple crossfade transition shader."""
    
    FRAGMENT_SHADER = """
    #version 330 core
    in vec2 v_uv;
    out vec4 frag_color;
    
    uniform sampler2D u_prev;
    uniform sampler2D u_next;
    uniform float u_time;
    
    void main() {
        vec4 prev_color = texture(u_prev, v_uv);
        vec4 next_color = texture(u_next, v_uv);
        frag_color = mix(prev_color, next_color, u_time);
    }
    """


class LinearWipeShader:
    """Linear wipe transition shader."""
    
    FRAGMENT_SHADER = """
    #version 330 core
    in vec2 v_uv;
    out vec4 frag_color;
    
    uniform sampler2D u_prev;
    uniform sampler2D u_next;
    uniform float u_time;
    uniform vec2 u_direction;
    
    void main() {
        vec4 prev_color = texture(u_prev, v_uv);
        vec4 next_color = texture(u_next, v_uv);
        
        float progress = dot(v_uv - 0.5, u_direction) + 0.5;
        float mix_val = smoothstep(0.0, 0.1, progress - (1.0 - u_time));
        
        frag_color = mix(prev_color, next_color, mix_val);
    }
    """


class CircleIrisShader:
    """Circular iris wipe transition shader."""
    
    FRAGMENT_SHADER = """
    #version 330 core
    in vec2 v_uv;
    out vec4 frag_color;
    
    uniform sampler2D u_prev;
    uniform sampler2D u_next;
    uniform float u_time;
    uniform vec2 u_center;
    uniform float u_feather;
    
    void main() {
        vec4 prev_color = texture(u_prev, v_uv);
        vec4 next_color = texture(u_next, v_uv);
        
        float dist = distance(v_uv, u_center);
        float max_dist = distance(vec2(0.0, 0.0), u_center);
        float progress = dist / max_dist;
        
        float mix_val = smoothstep(u_time - u_feather, u_time + u_feather, progress);
        
        frag_color = mix(next_color, prev_color, mix_val);
    }
    """


def create_transition_engine(width: int = 1920, height: int = 1080) -> WebGL2TransitionEngine:
    """Factory function to create a transition engine."""
    engine = WebGL2TransitionEngine(width, height)
    if engine.initialize():
        return engine
    else:
        print("Using CPU fallback for transitions")
        return engine