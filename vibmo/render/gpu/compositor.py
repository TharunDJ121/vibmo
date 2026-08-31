"""
ModernGL Hardware-Accelerated GPU Layer Compositor.
Executes multi-layer compositing, blend modes, track mattes, 3D quad perspective warping,
and 3D LUT grading directly on dedicated GPU VRAM.
"""

from __future__ import annotations
import math
import numpy as np
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
import moderngl

from vibmo.render.gpu.shaders import (
    VERTEX_SHADER_QUAD,
    VERTEX_SHADER_3D_QUAD,
    FRAGMENT_SHADER_QUAD_TEXTURE,
    FRAGMENT_SHADER_BLEND_MODES,
    FRAGMENT_SHADER_TRACK_MATTE,
    FRAGMENT_SHADER_LUT3D,
    FRAGMENT_SHADER_POST_FX,
    FRAGMENT_SHADER_BLOOM_EXTRACT,
    FRAGMENT_SHADER_SEPARABLE_BLUR,
)


_BLEND_MODE_MAP: Dict[str, int] = {
    "normal": 0,
    "multiply": 1,
    "screen": 2,
    "overlay": 3,
    "darken": 4,
    "lighten": 5,
    "color_dodge": 6,
    "color_burn": 7,
    "hard_light": 8,
    "soft_light": 9,
    "difference": 10,
    "exclusion": 11,
    "hue": 12,
    "saturation": 13,
    "color": 14,
    "luminosity": 15,
    "add": 16,
    "subtract": 17,
}


class GPUCompositor:
    """
    Dedicated GPU Layer Compositor running on ModernGL.
    Provides hardware layer blending, track mattes, 3D quad projection, and post-processing.
    """

    def __init__(self, width: int = 1920, height: int = 1080) -> None:
        self.width = max(16, int(width))
        self.height = max(16, int(height))
        self.ctx: Optional[moderngl.Context] = None
        self.is_available = False
        self.device_name = "CPU Fallback"
        self._lut_cache: Dict[int, moderngl.Texture3D] = {}
        self._init_gl()

    def _init_gl(self) -> None:
        try:
            self.ctx = moderngl.create_context(standalone=True)
            self.device_name = self.ctx.info.get("GL_RENDERER", "Dedicated GPU")

            # 1. Compile Programs
            self.prog_blend = self.ctx.program(
                vertex_shader=VERTEX_SHADER_QUAD,
                fragment_shader=FRAGMENT_SHADER_BLEND_MODES,
            )
            self.prog_matte = self.ctx.program(
                vertex_shader=VERTEX_SHADER_QUAD,
                fragment_shader=FRAGMENT_SHADER_TRACK_MATTE,
            )
            self.prog_3d_quad = self.ctx.program(
                vertex_shader=VERTEX_SHADER_3D_QUAD,
                fragment_shader=FRAGMENT_SHADER_QUAD_TEXTURE,
            )
            self.prog_lut3d = self.ctx.program(
                vertex_shader=VERTEX_SHADER_QUAD,
                fragment_shader=FRAGMENT_SHADER_LUT3D,
            )
            self.prog_post = self.ctx.program(
                vertex_shader=VERTEX_SHADER_QUAD,
                fragment_shader=FRAGMENT_SHADER_POST_FX,
            )
            self.prog_extract = self.ctx.program(
                vertex_shader=VERTEX_SHADER_QUAD,
                fragment_shader=FRAGMENT_SHADER_BLOOM_EXTRACT,
            )
            self.prog_blur = self.ctx.program(
                vertex_shader=VERTEX_SHADER_QUAD,
                fragment_shader=FRAGMENT_SHADER_SEPARABLE_BLUR,
            )

            # 2. Quad Mesh (Full-Screen Quad: in_vert: x,y ; in_uv: u,v)
            # OpenGL texture coords: (0,0) bottom-left, (1,1) top-right.
            # We map (0,0) UV to top-left for standard image coordinates.
            quad_data = np.array([
                -1.0, -1.0, 0.0, 1.0,
                 1.0, -1.0, 1.0, 1.0,
                -1.0,  1.0, 0.0, 0.0,
                 1.0,  1.0, 1.0, 0.0,
            ], dtype=np.float32)

            self.vbo_quad = self.ctx.buffer(quad_data.tobytes())
            self.vao_blend = self.ctx.simple_vertex_array(self.prog_blend, self.vbo_quad, "in_vert", "in_uv")
            self.vao_matte = self.ctx.simple_vertex_array(self.prog_matte, self.vbo_quad, "in_vert", "in_uv")
            self.vao_lut3d = self.ctx.simple_vertex_array(self.prog_lut3d, self.vbo_quad, "in_vert", "in_uv")
            self.vao_post = self.ctx.simple_vertex_array(self.prog_post, self.vbo_quad, "in_vert", "in_uv")
            self.vao_extract = self.ctx.simple_vertex_array(self.prog_extract, self.vbo_quad, "in_vert", "in_uv")
            self.vao_blur = self.ctx.simple_vertex_array(self.prog_blur, self.vbo_quad, "in_vert", "in_uv")

            # 3. Dynamic 3D Quad VBO
            self.vbo_3d = self.ctx.buffer(reserve=4 * 5 * 4, dynamic=True)
            self.vao_3d = self.ctx.simple_vertex_array(self.prog_3d_quad, self.vbo_3d, "in_vert", "in_uv")

            # 4. Textures & Framebuffers
            self._allocate_buffers(self.width, self.height)
            self.is_available = True
        except Exception as e:
            self.is_available = False
            self.device_name = "CPU Fallback"
            self.error_msg = str(e)

    def _allocate_buffers(self, w: int, h: int) -> None:
        """Allocates or resizes GPU textures and ping-pong framebuffers."""
        self.width = max(16, int(w))
        self.height = max(16, int(h))

        # Main Input / Output Textures
        self.tex_base = self.ctx.texture((self.width, self.height), 4, dtype="f1")
        self.tex_layer = self.ctx.texture((self.width, self.height), 4, dtype="f1")
        self.tex_out = self.ctx.texture((self.width, self.height), 4, dtype="f1")
        self.fbo_out = self.ctx.framebuffer(color_attachments=[self.tex_out])

        # Dynamic Layer Texture for arbitrary sized sub-layers
        self.tex_layer_dynamic: Optional[moderngl.Texture] = None

        # Bloom Ping-Pong Textures (Quarter resolution)
        bw = max(8, self.width // 2)
        bh = max(8, self.height // 2)
        self.bloom_w = bw
        self.bloom_h = bh

        self.tex_bloom_raw = self.ctx.texture((bw, bh), 4, dtype="f1")
        self.fbo_bloom_raw = self.ctx.framebuffer(color_attachments=[self.tex_bloom_raw])

        self.tex_ping = self.ctx.texture((bw, bh), 4, dtype="f1")
        self.fbo_ping = self.ctx.framebuffer(color_attachments=[self.tex_ping])

        self.tex_pong = self.ctx.texture((bw, bh), 4, dtype="f1")
        self.fbo_pong = self.ctx.framebuffer(color_attachments=[self.tex_pong])

    def composite_layers(
        self,
        base_rgba: np.ndarray,
        layer_rgba: np.ndarray,
        blend_mode: str = "normal",
        opacity: float = 1.0,
    ) -> np.ndarray:
        """Composites foreground layer over background base on GPU using hardware blend modes."""
        if not self.is_available:
            return base_rgba

        h, w, _ = base_rgba.shape
        if w != self.width or h != self.height:
            self._allocate_buffers(w, h)

        mode_id = _BLEND_MODE_MAP.get(str(blend_mode).lower(), 0)

        # Upload textures
        self.tex_base.write(base_rgba.tobytes())
        self.tex_layer.write(layer_rgba.tobytes())

        self.fbo_out.use()
        self.ctx.viewport = (0, 0, self.width, self.height)

        self.tex_base.use(location=0)
        self.tex_layer.use(location=1)

        self.prog_blend["u_base_texture"].value = 0
        self.prog_blend["u_layer_texture"].value = 1
        self.prog_blend["u_blend_mode"].value = mode_id
        self.prog_blend["u_opacity"].value = float(opacity)

        self.vao_blend.render(moderngl.TRIANGLE_STRIP)

        out_bytes = self.fbo_out.read(components=4, dtype="f1")
        return np.frombuffer(out_bytes, dtype=np.uint8).reshape((self.height, self.width, 4))

    def apply_track_matte(
        self,
        target_rgba: np.ndarray,
        matte_rgba: np.ndarray,
        matte_type: str = "alpha",
        inverted: bool = False,
    ) -> np.ndarray:
        """Applies Alpha or Luma track matte to target layer on GPU."""
        if not self.is_available:
            return target_rgba

        h, w, _ = target_rgba.shape
        if w != self.width or h != self.height:
            self._allocate_buffers(w, h)

        m_type = 0 if matte_type.lower() == "alpha" else 1

        self.tex_base.write(target_rgba.tobytes())
        self.tex_layer.write(matte_rgba.tobytes())

        self.fbo_out.use()
        self.ctx.viewport = (0, 0, self.width, self.height)

        self.tex_base.use(location=0)
        self.tex_layer.use(location=1)

        self.prog_matte["u_target_texture"].value = 0
        self.prog_matte["u_matte_texture"].value = 1
        self.prog_matte["u_matte_type"].value = m_type
        self.prog_matte["u_inverted"].value = bool(inverted)

        self.vao_matte.render(moderngl.TRIANGLE_STRIP)

        out_bytes = self.fbo_out.read(components=4, dtype="f1")
        return np.frombuffer(out_bytes, dtype=np.uint8).reshape((self.height, self.width, 4))

    def render_3d_quad(
        self,
        layer_rgba: np.ndarray,
        bounds: Tuple[float, float, float, float],
        position: Tuple[float, float],
        scale: Tuple[float, float],
        rot_z: float,
        rx: float,
        ry: float,
        anchor: Tuple[float, float] = (0.5, 0.5),
        opacity: float = 1.0,
        focal_dist: float = 1200.0,
        scene_dim: Optional[Tuple[int, int]] = None,
    ) -> np.ndarray:
        """Hardware 3D Perspective Projection of a 2D layer using ModernGL."""
        if not self.is_available:
            return layer_rgba

        sw = scene_dim[0] if scene_dim else self.width
        sh = scene_dim[1] if scene_dim else self.height

        if sw != self.width or sh != self.height:
            self._allocate_buffers(sw, sh)

        lh, lw, _ = layer_rgba.shape
        if lw < 2 or lh < 2:
            return np.zeros((sh, sw, 4), dtype=np.uint8)

        # Upload layer texture
        tex_quad = self.ctx.texture((lw, lh), 4, data=layer_rgba.tobytes(), dtype="f1")
        tex_quad.filter = (moderngl.LINEAR, moderngl.LINEAR)

        # Calculate 3D transformation matrix
        # Coordinate system: scene center is (0, 0, 0)
        px = position[0] - sw * 0.5
        py = position[1] - sh * 0.5
        sx, sy = scale[0], scale[1]
        bx, by, bw, bh = bounds
        ax, ay = anchor[0], anchor[1]

        # 4 corners in layer local space relative to anchor
        local_x0 = (bx - ax * bw) * sx
        local_y0 = (by - ay * bh) * sy
        local_x1 = (bx + bw - ax * bw) * sx
        local_y1 = (by + bh - ay * bh) * sy

        # Build 3D quad vertices (x, y, z)
        # Apply 3D Euler rotations (RX, RY, RZ)
        cos_x, sin_x = math.cos(rx), math.sin(rx)
        cos_y, sin_y = math.cos(ry), math.sin(ry)
        cos_z, sin_z = math.cos(rot_z), math.sin(rot_z)

        corners_2d = [
            (local_x0, local_y0, 0.0, 0.0),
            (local_x1, local_y0, 1.0, 0.0),
            (local_x0, local_y1, 0.0, 1.0),
            (local_x1, local_y1, 1.0, 1.0),
        ]

        vbo_array = []
        for lx, ly, u, v in corners_2d:
            # 1. Rotate Z
            xz = lx * cos_z - ly * sin_z
            yz = lx * sin_z + ly * cos_z
            zz = 0.0

            # 2. Rotate Y
            xy = xz * cos_y + zz * sin_y
            yy = yz
            zy = -xz * sin_y + zz * cos_y

            # 3. Rotate X
            xx = xy
            yx = yy * cos_x - zy * sin_x
            zx = yy * sin_x + zy * cos_x

            # 4. Translate in 3D Scene space
            wx = xx + px
            wy = yx + py
            wz = zx

            # 5. Perspective division (Focal length projection into NDC [-1, 1])
            dist = focal_dist + wz
            if dist < 10.0:
                dist = 10.0
            ndc_x = (wx * focal_dist / dist) / (sw * 0.5)
            ndc_y = -(wy * focal_dist / dist) / (sh * 0.5)  # flip Y for GL

            vbo_array.extend([ndc_x, ndc_y, wz / 2000.0, u, v])

        vbo_bytes = np.array(vbo_array, dtype=np.float32).tobytes()
        self.vbo_3d.write(vbo_bytes)

        # Render into clean FBO
        self.fbo_out.use()
        self.fbo_out.clear(0.0, 0.0, 0.0, 0.0)
        self.ctx.viewport = (0, 0, self.width, self.height)
        self.ctx.enable(moderngl.BLEND)

        tex_quad.use(location=0)
        self.prog_3d_quad["u_texture"].value = 0
        self.prog_3d_quad["u_opacity"].value = float(opacity)
        # Identity MVP because vertices are pre-projected into NDC
        self.prog_3d_quad["u_mvp"].write(np.eye(4, dtype=np.float32).tobytes())

        self.vao_3d.render(moderngl.TRIANGLE_STRIP)
        tex_quad.release()

        out_bytes = self.fbo_out.read(components=4, dtype="f1")
        return np.frombuffer(out_bytes, dtype=np.uint8).reshape((self.height, self.width, 4))

    def apply_lut3d(
        self,
        rgba: np.ndarray,
        lut_data: np.ndarray,
        intensity: float = 1.0,
    ) -> np.ndarray:
        """Hardware 3D LUT Color Grading using ModernGL 3D texture sampler."""
        if not self.is_available:
            return rgba

        h, w, _ = rgba.shape
        if w != self.width or h != self.height:
            self._allocate_buffers(w, h)

        lut_hash = hash(lut_data.tobytes()[:128])
        if lut_hash not in self._lut_cache:
            lut_dim = int(round(lut_data.shape[0]))
            tex3d = self.ctx.texture3d((lut_dim, lut_dim, lut_dim), 3, data=lut_data.astype(np.float32).tobytes(), dtype="f4")
            tex3d.filter = (moderngl.LINEAR, moderngl.LINEAR)
            self._lut_cache[lut_hash] = tex3d

        tex_lut = self._lut_cache[lut_hash]

        self.tex_base.write(rgba.tobytes())
        self.fbo_out.use()
        self.ctx.viewport = (0, 0, self.width, self.height)

        self.tex_base.use(location=0)
        tex_lut.use(location=1)

        self.prog_lut3d["u_texture"].value = 0
        self.prog_lut3d["u_lut"].value = 1
        self.prog_lut3d["u_intensity"].value = float(intensity)

        self.vao_lut3d.render(moderngl.TRIANGLE_STRIP)

        out_bytes = self.fbo_out.read(components=4, dtype="f1")
        return np.frombuffer(out_bytes, dtype=np.uint8).reshape((self.height, self.width, 4))

    def apply_post_fx(
        self,
        rgba: np.ndarray,
        time: float,
        post_fx: List[Any],
    ) -> np.ndarray:
        """Executes full GPU post-processing pipeline (Bloom, Glow, Vignette, Grain, Chromatic Aberration)."""
        if not self.is_available or not post_fx:
            return rgba

        h, w, _ = rgba.shape
        if w != self.width or h != self.height:
            self._allocate_buffers(w, h)

        # 1. Parse FX Parameters
        vignette_intensity = 0.0
        vignette_radius = 0.75
        grain_amount = 0.0
        bloom_threshold = 0.65
        bloom_intensity = 0.0
        bloom_radius = 16.0
        chromatic_aberration = 0.0

        has_active_fx = False
        for fx in post_fx:
            fx_name = fx.__class__.__name__.lower()
            if "vignette" in fx_name:
                vignette_intensity = float(getattr(fx, "intensity", 0.25))
                vignette_radius = float(getattr(fx, "radius", 0.75))
                has_active_fx = True
            elif "grain" in fx_name:
                grain_amount = float(getattr(fx, "amount", 0.008))
                has_active_fx = True
            elif "bloom" in fx_name or "glow" in fx_name:
                bloom_threshold = float(getattr(fx, "threshold", 0.65))
                bloom_intensity = float(getattr(fx, "intensity", 0.35))
                bloom_radius = float(getattr(fx, "radius", 16.0))
                has_active_fx = True
            elif "chromatic" in fx_name:
                chromatic_aberration = float(getattr(fx, "offset", 1.0))
                has_active_fx = True

        if not has_active_fx:
            return rgba

        # 2. Upload main frame to VRAM
        self.tex_base.write(rgba.tobytes())

        # 3. GPU Bloom Pass (if active)
        if bloom_intensity > 0.0:
            # Pass A: Extract Bright Pixels into Raw Bloom FBO
            self.fbo_bloom_raw.use()
            self.ctx.viewport = (0, 0, self.bloom_w, self.bloom_h)
            self.tex_base.use(location=0)
            self.prog_extract["u_texture"].value = 0
            self.prog_extract["u_threshold"].value = bloom_threshold
            self.vao_extract.render(moderngl.TRIANGLE_STRIP)

            # Pass B: Horizontal Gaussian Blur (Raw -> Ping)
            self.fbo_ping.use()
            self.tex_bloom_raw.use(location=0)
            self.prog_blur["u_texture"].value = 0
            self.prog_blur["u_direction"].value = (1.0, 0.0)
            self.prog_blur["u_resolution"].value = (float(self.bloom_w), float(self.bloom_h))
            self.prog_blur["u_blur_radius"].value = float(bloom_radius * 0.5)
            self.vao_blur.render(moderngl.TRIANGLE_STRIP)

            # Pass C: Vertical Gaussian Blur (Ping -> Pong)
            self.fbo_pong.use()
            self.tex_ping.use(location=0)
            self.prog_blur["u_texture"].value = 0
            self.prog_blur["u_direction"].value = (0.0, 1.0)
            self.prog_blur["u_resolution"].value = (float(self.bloom_w), float(self.bloom_h))
            self.prog_blur["u_blur_radius"].value = float(bloom_radius * 0.5)
            self.vao_blur.render(moderngl.TRIANGLE_STRIP)

        # 4. Master Post-FX Composite Pass
        self.fbo_out.use()
        self.ctx.viewport = (0, 0, self.width, self.height)

        self.tex_base.use(location=0)
        self.prog_post["u_texture"].value = 0

        if bloom_intensity > 0.0:
            self.tex_pong.use(location=1)
            self.prog_post["u_bloom_texture"].value = 1
        else:
            self.tex_base.use(location=1)
            self.prog_post["u_bloom_texture"].value = 1

        self.prog_post["u_time"].value = float(time)
        self.prog_post["u_vignette_intensity"].value = float(vignette_intensity)
        self.prog_post["u_vignette_radius"].value = float(vignette_radius)
        self.prog_post["u_grain_amount"].value = float(grain_amount)
        self.prog_post["u_bloom_intensity"].value = float(bloom_intensity)
        self.prog_post["u_chromatic_aberration"].value = float(chromatic_aberration)
        self.prog_post["u_resolution"].value = (float(self.width), float(self.height))

        self.vao_post.render(moderngl.TRIANGLE_STRIP)

        out_bytes = self.fbo_out.read(components=4, dtype="f1")
        return np.frombuffer(out_bytes, dtype=np.uint8).reshape((self.height, self.width, 4))
