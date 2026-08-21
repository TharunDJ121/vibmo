"""
ModernGL Hardware-Accelerated GPU Post-Processing and Shader Pipeline.
Executes Bloom, Optical Glow, Gaussian Blur, Chromatic Aberration, Vignette, and Film Grain
on dedicated GPU VRAM with Ping-Pong Framebuffer rendering.
"""

from __future__ import annotations
import numpy as np
from typing import Any, List, Optional, Tuple
import moderngl

from vibmo.render.gpu.shaders import (
    VERTEX_SHADER_QUAD,
    FRAGMENT_SHADER_POST_FX,
    FRAGMENT_SHADER_BLOOM_EXTRACT,
    FRAGMENT_SHADER_SEPARABLE_BLUR,
)


class GPUPostProcessor:
    """Hardware-accelerated ModernGL GPU post-processing pipeline running on dedicated GPU."""

    def __init__(self, width: int = 1920, height: int = 1080) -> None:
        self.width = max(16, int(width))
        self.height = max(16, int(height))
        self.ctx: Optional[moderngl.Context] = None
        self.is_available = False
        self._init_gl()

    def _init_gl(self) -> None:
        try:
            self.ctx = moderngl.create_context(standalone=True)
            self.device_name = self.ctx.info.get("GL_RENDERER", "Dedicated GPU")
            
            # 1. Compile Programs
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

            # 2. Quad Mesh (in_vert: x,y ; in_uv: u,v)
            quad_data = np.array([
                -1.0, -1.0, 0.0, 0.0,
                 1.0, -1.0, 1.0, 0.0,
                -1.0,  1.0, 0.0, 1.0,
                 1.0,  1.0, 1.0, 1.0,
            ], dtype=np.float32)

            self.vbo = self.ctx.buffer(quad_data.tobytes())
            self.vao_post = self.ctx.simple_vertex_array(self.prog_post, self.vbo, "in_vert", "in_uv")
            self.vao_extract = self.ctx.simple_vertex_array(self.prog_extract, self.vbo, "in_vert", "in_uv")
            self.vao_blur = self.ctx.simple_vertex_array(self.prog_blur, self.vbo, "in_vert", "in_uv")

            # 3. Textures & Framebuffers
            self._allocate_buffers(self.width, self.height)
            self.is_available = True
        except Exception as e:
            self.is_available = False
            self.device_name = "CPU Fallback"
            self.error_msg = str(e)

    def _allocate_buffers(self, w: int, h: int) -> None:
        """Allocates or resizes GPU textures and ping-pong framebuffers."""
        self.width = w
        self.height = h

        # Main In/Out
        self.tex_in = self.ctx.texture((w, h), 4, dtype="f1")
        self.tex_out = self.ctx.texture((w, h), 4, dtype="f1")
        self.fbo_out = self.ctx.framebuffer(color_attachments=[self.tex_out])

        # Bloom Ping-Pong Textures (Quarter resolution for high speed & wide blur)
        bw = max(8, w // 2)
        bh = max(8, h // 2)
        self.bloom_w = bw
        self.bloom_h = bh

        self.tex_bloom_raw = self.ctx.texture((bw, bh), 4, dtype="f1")
        self.fbo_bloom_raw = self.ctx.framebuffer(color_attachments=[self.tex_bloom_raw])

        self.tex_ping = self.ctx.texture((bw, bh), 4, dtype="f1")
        self.fbo_ping = self.ctx.framebuffer(color_attachments=[self.tex_ping])

        self.tex_pong = self.ctx.texture((bw, bh), 4, dtype="f1")
        self.fbo_pong = self.ctx.framebuffer(color_attachments=[self.tex_pong])

    def apply_post_fx(
        self,
        rgba: np.ndarray,
        time: float,
        post_fx: List[Any],
    ) -> np.ndarray:
        """Executes full post-processing pipeline on dedicated GPU in < 1ms."""
        if not self.is_available or not post_fx:
            return rgba

        h, w, _ = rgba.shape
        # Dynamically resize buffers if dimensions change (e.g. proxy mode)
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
        self.tex_in.write(rgba.tobytes())

        # 3. GPU Bloom Pass (if active)
        if bloom_intensity > 0.0:
            # Pass A: Extract Bright Pixels into Raw Bloom FBO
            self.fbo_bloom_raw.use()
            self.ctx.viewport = (0, 0, self.bloom_w, self.bloom_h)
            self.tex_in.use(location=0)
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

        # 4. Master Post-FX Composite Pass (Main + Bloom + Vignette + Grain + Chromatic Aberration)
        self.fbo_out.use()
        self.ctx.viewport = (0, 0, self.width, self.height)

        self.tex_in.use(location=0)
        self.prog_post["u_texture"].value = 0

        if bloom_intensity > 0.0:
            self.tex_pong.use(location=1)
            self.prog_post["u_bloom_texture"].value = 1
        else:
            self.tex_in.use(location=1)
            self.prog_post["u_bloom_texture"].value = 1

        self.prog_post["u_time"].value = float(time)
        self.prog_post["u_vignette_intensity"].value = float(vignette_intensity)
        self.prog_post["u_vignette_radius"].value = float(vignette_radius)
        self.prog_post["u_grain_amount"].value = float(grain_amount)
        self.prog_post["u_bloom_intensity"].value = float(bloom_intensity)
        self.prog_post["u_chromatic_aberration"].value = float(chromatic_aberration)
        self.prog_post["u_resolution"].value = (float(self.width), float(self.height))

        self.vao_post.render(moderngl.TRIANGLE_STRIP)

        # 5. Read back composite frame from GPU VRAM
        out_bytes = self.fbo_out.read(components=4, dtype="f1")
        return np.frombuffer(out_bytes, dtype=np.uint8).reshape((self.height, self.width, 4))
