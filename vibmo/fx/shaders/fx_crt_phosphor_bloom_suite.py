import numpy as np
import moderngl
from typing import Any, Optional, Tuple, Union

def get_gl_context():
    try:
        return moderngl.create_context(standalone=True, require=330)
    except Exception:
        return None

try:
    from vibmo.fx.filters import Filter
except ImportError:
    class Filter:
        def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
            raise NotImplementedError

class GpuFilterBase(Filter):
    def __init__(self, use_gpu: bool = True):
        self.use_gpu = use_gpu
        self.ctx = None
        self.prog = None
        self.vbo = None
        self.vao = None
        
        # Cache for rendering
        self._fbo = None
        self._texture = None
        
        if self.use_gpu:
            self.ctx = get_gl_context()
            if not self.ctx:
                self.use_gpu = False
            else:
                self._init_gl()

    def _init_gl(self):
        vertex_shader = """
            #version 330
            in vec2 in_vert;
            in vec2 in_uv;
            out vec2 v_uv;
            void main() {
                gl_Position = vec4(in_vert, 0.0, 1.0);
                v_uv = in_uv;
            }
        """
        self.prog = self.ctx.program(
            vertex_shader=vertex_shader,
            fragment_shader=self.get_fragment_shader()
        )
        vertices = np.array([
            -1.0, -1.0,  0.0, 0.0,
             1.0, -1.0,  1.0, 0.0,
            -1.0,  1.0,  0.0, 1.0,
             1.0,  1.0,  1.0, 1.0,
        ], dtype='f4')
        self.vbo = self.ctx.buffer(vertices)
        self.vao = self.ctx.vertex_array(
            self.prog,
            [
                (self.vbo, '2f 2f', 'in_vert', 'in_uv')
            ]
        )

    def get_fragment_shader(self) -> str:
        return """
            #version 330
            in vec2 v_uv;
            out vec4 f_color;
            uniform sampler2D tex;
            void main() {
                f_color = texture(tex, v_uv);
            }
        """

    def apply_gpu(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        h, w, _ = rgba.shape
        
        if self._fbo is None or self._fbo.size != (w, h):
            if self._fbo:
                self._fbo.release()
            if self._texture:
                self._texture.release()
            
            self._texture = self.ctx.texture((w, h), 4, dtype='f1')
            self._fbo = self.ctx.framebuffer(color_attachments=[self.ctx.texture((w, h), 4, dtype='f1')])
            
        # Upload current frame
        # Convert RGBA to contiguous buffer
        self._texture.write(np.ascontiguousarray(rgba))
        self._texture.use(0)
        
        self.update_uniforms(w, h, time)
        
        self._fbo.use()
        self.ctx.clear(0.0, 0.0, 0.0, 0.0)
        self.vao.render(moderngl.TRIANGLE_STRIP)
        
        # Read back pixels
        data = self._fbo.read(components=4, dtype='f1')
        out = np.frombuffer(data, dtype=np.uint8).reshape((h, w, 4))
        # Note: OpenGL framebuffers have origin at bottom-left, need vertical flip
        return np.flipud(out).copy()

    def update_uniforms(self, w: int, h: int, time: float):
        pass

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        if self.use_gpu and self.ctx:
            return self.apply_gpu(rgba, time)
        return self.apply_cpu(rgba, time)

    def apply_cpu(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        return rgba


class CrtPhosphorBloomShader(GpuFilterBase):
    def __init__(
        self,
        intensity: float = 0.5,
        radius: float = 5.0,
        use_gpu: bool = True,
        bloom: Optional[float] = None,
        aperture_grille: bool = True,
        **kwargs: Any
    ):
        self.intensity = float(bloom if bloom is not None else intensity)
        self.radius = float(radius)
        self.aperture_grille = bool(aperture_grille)
        import scipy.ndimage as ndimage
        self.ndimage = ndimage
        super().__init__(use_gpu=use_gpu)

    def get_fragment_shader(self) -> str:
        return """
            #version 330
            in vec2 v_uv;
            out vec4 f_color;
            uniform sampler2D tex;
            uniform float intensity;
            uniform float radius;
            uniform float width;
            uniform float height;
            uniform int aperture_grille;
            
            void main() {
                vec4 color = texture(tex, v_uv);
                
                vec4 bloom = vec4(0.0);
                float dx = radius / width;
                float dy = radius / height;
                
                bloom += texture(tex, v_uv + vec2(-dx, -dy));
                bloom += texture(tex, v_uv + vec2( 0.0, -dy));
                bloom += texture(tex, v_uv + vec2( dx, -dy));
                bloom += texture(tex, v_uv + vec2(-dx,  0.0));
                bloom += texture(tex, v_uv + vec2( dx,  0.0));
                bloom += texture(tex, v_uv + vec2(-dx,  dy));
                bloom += texture(tex, v_uv + vec2( 0.0,  dy));
                bloom += texture(tex, v_uv + vec2( dx,  dy));
                bloom /= 8.0;
                
                vec4 final_col = color + bloom * intensity;
                
                if (aperture_grille == 1) {
                    float mask = mod(gl_FragCoord.x, 3.0);
                    vec3 triad = vec3(0.0);
                    if (mask < 1.0) triad.r = 1.2;
                    else if (mask < 2.0) triad.g = 1.2;
                    else triad.b = 1.2;
                    
                    final_col.rgb *= triad;
                }
                
                f_color = final_col;
            }
        """

    def update_uniforms(self, w: int, h: int, time: float):
        if 'intensity' in self.prog:
            self.prog['intensity'].value = self.intensity
        if 'radius' in self.prog:
            self.prog['radius'].value = self.radius
        if 'width' in self.prog:
            self.prog['width'].value = float(w)
        if 'height' in self.prog:
            self.prog['height'].value = float(h)
        if 'aperture_grille' in self.prog:
            self.prog['aperture_grille'].value = int(self.aperture_grille)

    def apply_cpu(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        # Fast CPU fallback using Gaussian blur for bloom
        h, w, c = rgba.shape
        rgb = rgba[:, :, :3].astype(np.float32)
        
        # Calculate blurred bloom
        blurred = np.zeros_like(rgb)
        for i in range(3):
            blurred[:, :, i] = self.ndimage.gaussian_filter(rgb[:, :, i], sigma=self.radius)
            
        out_rgb = rgb + blurred * self.intensity
        
        if self.aperture_grille:
            # Triad phosphor mask along x-axis
            x_indices = np.arange(w) % 3
            mask = np.zeros((1, w, 3), dtype=np.float32)
            mask[0, x_indices == 0, 0] = 1.2
            mask[0, x_indices == 1, 1] = 1.2
            mask[0, x_indices == 2, 2] = 1.2
            out_rgb *= mask
            
        out_rgb = np.clip(out_rgb, 0, 255).astype(np.uint8)
        
        out = rgba.copy()
        out[:, :, :3] = out_rgb
        return out


class CurvedGlassBarrelDistortion(GpuFilterBase):
    def __init__(
        self,
        amount: float = 0.1,
        corner_darkness: float = 0.3,
        use_gpu: bool = True,
        distortion: Optional[float] = None,
        **kwargs: Any
    ):
        self.amount = float(distortion if distortion is not None else amount)
        self.corner_darkness = float(corner_darkness)
        import scipy.ndimage as ndimage
        self.ndimage = ndimage
        super().__init__(use_gpu=use_gpu)

    def get_fragment_shader(self) -> str:
        return """
            #version 330
            in vec2 v_uv;
            out vec4 f_color;
            uniform sampler2D tex;
            uniform float amount;
            uniform float corner_darkness;
            
            void main() {
                vec2 p = v_uv * 2.0 - 1.0;
                float r2 = dot(p, p);
                
                vec2 distorted_p = p + p * (r2 * amount);
                vec2 distorted_uv = distorted_p * 0.5 + 0.5;
                
                if (distorted_uv.x < 0.0 || distorted_uv.x > 1.0 || distorted_uv.y < 0.0 || distorted_uv.y > 1.0) {
                    f_color = vec4(0.0);
                } else {
                    f_color = texture(tex, distorted_uv);
                    float vignette = 1.0 - smoothstep(0.5, 1.5, r2);
                    f_color.rgb *= mix(1.0, vignette, corner_darkness);
                }
            }
        """

    def update_uniforms(self, w: int, h: int, time: float):
        if 'amount' in self.prog:
            self.prog['amount'].value = self.amount
        if 'corner_darkness' in self.prog:
            self.prog['corner_darkness'].value = self.corner_darkness

    def apply_cpu(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        h, w, c = rgba.shape
        y, x = np.indices((h, w), dtype=np.float32)
        
        # Normalize to [-1, 1]
        nx = (x / (w - 1)) * 2.0 - 1.0
        ny = (y / (h - 1)) * 2.0 - 1.0
        
        r2 = nx**2 + ny**2
        distorted_nx = nx + nx * (r2 * self.amount)
        distorted_ny = ny + ny * (r2 * self.amount)
        
        # Map back to pixel coords
        orig_x = ((distorted_nx + 1.0) * 0.5) * (w - 1)
        orig_y = ((distorted_ny + 1.0) * 0.5) * (h - 1)
        
        coords = np.array([orig_y, orig_x])
        out = np.zeros_like(rgba)
        for i in range(c):
            out[:, :, i] = self.ndimage.map_coordinates(rgba[:, :, i], coords, order=1, mode='constant', cval=0)
            
        # Vignette
        vignette = 1.0 - np.clip((r2 - 0.5) / 1.0, 0.0, 1.0)
        vignette = 1.0 * (1.0 - self.corner_darkness) + vignette * self.corner_darkness
        
        out_rgb = np.clip(out[:, :, :3].astype(np.float32) * vignette[:, :, None], 0, 255).astype(np.uint8)
        out[:, :, :3] = out_rgb
        return out


class PhosphorPersistenceTrail(GpuFilterBase):
    def __init__(self, decay: float = 0.8, use_gpu: bool = True, **kwargs: Any):
        self.decay = float(decay)
        self.prev_frame = None
        super().__init__(use_gpu=use_gpu)

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        return self.apply_cpu(rgba, time)

    def apply_cpu(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        if self.prev_frame is None or self.prev_frame.shape != rgba.shape:
            self.prev_frame = rgba.astype(np.float32)
            return rgba.copy()
            
        curr = rgba.astype(np.float32)
        # Decay previous and blend with current
        self.prev_frame = np.maximum(curr, self.prev_frame * self.decay)
        return np.clip(self.prev_frame, 0, 255).astype(np.uint8)


class HorizontalRGBBeamBleed(GpuFilterBase):
    def __init__(
        self,
        bleed_amount: float = 0.01,
        offset_r: Optional[float] = None,
        offset_g: Optional[float] = None,
        offset_b: Optional[float] = None,
        use_gpu: bool = True,
        **kwargs: Any
    ):
        self.bleed_amount = float(bleed_amount)
        self.offset_r = float(offset_r) if offset_r is not None else float(bleed_amount * 100.0)
        self.offset_g = float(offset_g) if offset_g is not None else 0.0
        self.offset_b = float(offset_b) if offset_b is not None else float(-bleed_amount * 100.0)
        super().__init__(use_gpu=use_gpu)

    def get_fragment_shader(self) -> str:
        return """
            #version 330
            in vec2 v_uv;
            out vec4 f_color;
            uniform sampler2D tex;
            uniform float offset_r;
            uniform float offset_g;
            uniform float offset_b;
            uniform float width;

            void main() {
                float r_uv_x = v_uv.x + (offset_r / width);
                float g_uv_x = v_uv.x + (offset_g / width);
                float b_uv_x = v_uv.x + (offset_b / width);

                float r = texture(tex, vec2(r_uv_x, v_uv.y)).r;
                float g = texture(tex, vec2(g_uv_x, v_uv.y)).g;
                float b = texture(tex, vec2(b_uv_x, v_uv.y)).b;
                float a = texture(tex, v_uv).a;

                f_color = vec4(r, g, b, a);
            }
        """

    def update_uniforms(self, w: int, h: int, time: float):
        if 'offset_r' in self.prog:
            self.prog['offset_r'].value = self.offset_r
        if 'offset_g' in self.prog:
            self.prog['offset_g'].value = self.offset_g
        if 'offset_b' in self.prog:
            self.prog['offset_b'].value = self.offset_b
        if 'width' in self.prog:
            self.prog['width'].value = float(w)

    def apply_cpu(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        h, w, c = rgba.shape
        out = rgba.copy()
        
        # Shift channels based on offsets
        r_shift = int(self.offset_r)
        g_shift = int(self.offset_g)
        b_shift = int(self.offset_b)

        if r_shift > 0:
            out[:, r_shift:, 0] = rgba[:, :-r_shift, 0]
            out[:, :r_shift, 0] = rgba[:, :1, 0]
        elif r_shift < 0:
            out[:, :r_shift, 0] = rgba[:, -r_shift:, 0]
            out[:, r_shift:, 0] = rgba[:, -1:, 0]

        if g_shift > 0:
            out[:, g_shift:, 1] = rgba[:, :-g_shift, 1]
            out[:, :g_shift, 1] = rgba[:, :1, 1]
        elif g_shift < 0:
            out[:, :g_shift, 1] = rgba[:, -g_shift:, 1]
            out[:, g_shift:, 1] = rgba[:, -1:, 1]

        if b_shift > 0:
            out[:, b_shift:, 2] = rgba[:, :-b_shift, 2]
            out[:, :b_shift, 2] = rgba[:, :1, 2]
        elif b_shift < 0:
            out[:, :b_shift, 2] = rgba[:, -b_shift:, 2]
            out[:, b_shift:, 2] = rgba[:, -1:, 2]

        return out


__all__ = [
    "GpuFilterBase",
    "CrtPhosphorBloomShader",
    "CurvedGlassBarrelDistortion",
    "PhosphorPersistenceTrail",
    "HorizontalRGBBeamBleed",
]
