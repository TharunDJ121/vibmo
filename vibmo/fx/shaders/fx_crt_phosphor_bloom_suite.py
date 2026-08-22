import numpy as np
import moderngl
from typing import Optional, Tuple

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
        raise NotImplementedError

    def apply_gpu(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        h, w, c = rgba.shape
        
        # Initialize or resize FBO and texture
        if self._texture is None or self._texture.size != (w, h):
            if self._texture:
                self._texture.release()
            if self._fbo:
                self._fbo.release()
            
            self._texture = self.ctx.texture((w, h), 4)
            self._fbo = self.ctx.framebuffer(
                color_attachments=[self.ctx.texture((w, h), 4)]
            )
            
        self._texture.write(rgba.tobytes())
        self._texture.use(0)
        
        if 'tex' in self.prog:
            self.prog['tex'].value = 0
        if 'time' in self.prog:
            self.prog['time'].value = time
            
        self.update_uniforms(w, h, time)
        
        self._fbo.use()
        self.vao.render(moderngl.TRIANGLE_STRIP)
        
        raw = self._fbo.read(components=4)
        out = np.frombuffer(raw, dtype=np.uint8).reshape((h, w, 4))
        
        return out

    def update_uniforms(self, w: int, h: int, time: float):
        pass

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        if self.use_gpu and self.ctx:
            return self.apply_gpu(rgba, time)
        return self.apply_cpu(rgba, time)

    def apply_cpu(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        return rgba


class CrtPhosphorBloomShader(GpuFilterBase):
    def __init__(self, intensity: float = 0.5, radius: float = 5.0, use_gpu: bool = True):
        self.intensity = intensity
        self.radius = radius
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
            
            void main() {
                vec4 color = texture(tex, v_uv);
                
                vec4 bloom = vec4(0.0);
                float dx = radius / width;
                float dy = radius / height;
                
                bloom += texture(tex, v_uv + vec2(-dx, -dy));
                bloom += texture(tex, v_uv + vec2( 0.0, -dy));
                bloom += texture(tex, v_uv + vec2( dx, -dy));
                bloom += texture(tex, v_uv + vec2(-dx,  0.0));
                bloom += color;
                bloom += texture(tex, v_uv + vec2( dx,  0.0));
                bloom += texture(tex, v_uv + vec2(-dx,  dy));
                bloom += texture(tex, v_uv + vec2( 0.0,  dy));
                bloom += texture(tex, v_uv + vec2( dx,  dy));
                bloom /= 9.0;
                
                float grille = sin(v_uv.x * width * 3.14159) * 0.2 + 0.8;
                f_color = color * grille;
                f_color.rgb += bloom.rgb * intensity;
                f_color.a = color.a;
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

    def apply_cpu(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        h, w, c = rgba.shape
        rgb = rgba[:, :, :3].astype(np.float32) / 255.0
        
        bloom = np.zeros_like(rgb)
        for i in range(3):
            bloom[:, :, i] = self.ndimage.gaussian_filter(rgb[:, :, i], sigma=self.radius)
        
        x = np.arange(w)
        grille = (np.sin(x * np.pi) * 0.2 + 0.8)
        grille_mask = np.tile(grille, (h, 1))
        
        out_rgb = rgb * grille_mask[:, :, None]
        out_rgb += bloom * self.intensity
        out_rgb = np.clip(out_rgb * 255.0, 0, 255).astype(np.uint8)
        
        out = rgba.copy()
        out[:, :, :3] = out_rgb
        return out


class CurvedGlassBarrelDistortion(GpuFilterBase):
    def __init__(self, amount: float = 0.1, corner_darkness: float = 0.3, use_gpu: bool = True):
        self.amount = amount
        self.corner_darkness = corner_darkness
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
        y, x = np.mgrid[0:h, 0:w]
        
        nx = (x / w) * 2.0 - 1.0
        ny = (y / h) * 2.0 - 1.0
        r2 = nx**2 + ny**2
        
        dx = nx * r2 * self.amount
        dy = ny * r2 * self.amount
        
        map_x = x + dx * w * 0.5
        map_y = y + dy * h * 0.5
        
        out = np.zeros_like(rgba)
        for i in range(c):
            out[:, :, i] = self.ndimage.map_coordinates(rgba[:, :, i], [map_y, map_x], order=1, mode='constant', cval=0)
            
        vignette = 1.0 - np.clip((r2 - 0.5) / 1.0, 0, 1)
        vignette_mask = 1.0 * (1.0 - self.corner_darkness) + vignette * self.corner_darkness
        
        out[:, :, :3] = (out[:, :, :3] * vignette_mask[:, :, None]).astype(np.uint8)
        return out


class PhosphorPersistenceTrail(GpuFilterBase):
    def __init__(self, decay: float = 0.9, color: Tuple[float, float, float] = (0.1, 1.0, 0.2), use_gpu: bool = True):
        self.decay = decay
        self.color = np.array(color)
        self.prev_frame = None
        self.prev_fbo = None
        super().__init__(use_gpu=use_gpu)

    def get_fragment_shader(self) -> str:
        return """
            #version 330
            in vec2 v_uv;
            out vec4 f_color;
            uniform sampler2D tex;
            uniform sampler2D prev_tex;
            uniform float decay;
            uniform vec3 tint_color;
            
            void main() {
                vec4 current = texture(tex, v_uv);
                vec4 prev = texture(prev_tex, v_uv);
                
                vec3 trail = prev.rgb * decay * tint_color;
                vec3 out_rgb = max(current.rgb, trail);
                f_color = vec4(out_rgb, current.a);
            }
        """

    def update_uniforms(self, w: int, h: int, time: float):
        if 'decay' in self.prog:
            self.prog['decay'].value = self.decay
        if 'tint_color' in self.prog:
            self.prog['tint_color'].value = tuple(self.color)

    def apply_gpu(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        h, w, c = rgba.shape
        
        if self._texture is None or self._texture.size != (w, h):
            if self._texture:
                self._texture.release()
            if self._fbo:
                self._fbo.release()
            
            self._texture = self.ctx.texture((w, h), 4)
            self._fbo = self.ctx.framebuffer(
                color_attachments=[self.ctx.texture((w, h), 4)]
            )
            
        self._texture.write(rgba.tobytes())
        self._texture.use(0)
        
        if self.prev_fbo is None or self.prev_fbo.size != (w, h):
            if self.prev_fbo:
                self.prev_fbo.release()
            self.prev_fbo = self.ctx.texture((w, h), 4, rgba.tobytes())
            
        self.prev_fbo.use(1)

        if 'tex' in self.prog:
            self.prog['tex'].value = 0
        if 'prev_tex' in self.prog:
            self.prog['prev_tex'].value = 1
            
        self.update_uniforms(w, h, time)
        
        self._fbo.use()
        self.vao.render(moderngl.TRIANGLE_STRIP)
        
        raw = self._fbo.read(components=4)
        out = np.frombuffer(raw, dtype=np.uint8).reshape((h, w, 4))
        
        self.prev_fbo.write(raw)
        
        return out

    def apply_cpu(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        rgb = rgba[:, :, :3].astype(np.float32) / 255.0
        
        if self.prev_frame is None or self.prev_frame.shape != rgb.shape:
            self.prev_frame = rgb.copy()
            return rgba
            
        trail = self.prev_frame * self.decay * self.color[None, None, :]
        current_max = np.maximum(rgb, trail)
        self.prev_frame = current_max
        
        out_rgb = np.clip(current_max * 255.0, 0, 255).astype(np.uint8)
        out = rgba.copy()
        out[:, :, :3] = out_rgb
        return out


class HorizontalRGBBeamBleed(GpuFilterBase):
    def __init__(self, offset_r: float = -2.0, offset_g: float = 0.0, offset_b: float = 2.0, use_gpu: bool = True):
        self.offset_r = offset_r
        self.offset_g = offset_g
        self.offset_b = offset_b
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
                vec4 cr = texture(tex, v_uv - vec2(offset_r / width, 0.0));
                vec4 cg = texture(tex, v_uv - vec2(offset_g / width, 0.0));
                vec4 cb = texture(tex, v_uv - vec2(offset_b / width, 0.0));
                f_color = vec4(cr.r, cg.g, cb.b, (cr.a + cg.a + cb.a) / 3.0);
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
        
        for i, offset in enumerate([self.offset_r, self.offset_g, self.offset_b]):
            shift = int(offset)
            if shift > 0:
                out[:, shift:, i] = rgba[:, :-shift, i]
                out[:, :shift, i] = 0
            elif shift < 0:
                out[:, :shift, i] = rgba[:, -shift:, i]
                out[:, shift:, i] = 0
                
        return out
