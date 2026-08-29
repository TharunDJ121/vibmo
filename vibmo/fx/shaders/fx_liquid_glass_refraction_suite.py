import numpy as np
import moderngl
from typing import Optional, Tuple
from PIL import Image, ImageFilter

try:
    from vibmo.fx.filters import Filter
except ImportError:
    class Filter:
        def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
            raise NotImplementedError

def get_gl_context():
    try:
        return moderngl.create_context(standalone=True, require=330)
    except Exception:
        return None

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
            if self.ctx:
                self.setup_gl()
            else:
                self.use_gpu = False

    def setup_gl(self):
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
        fragment_shader = self.get_fragment_shader()
        self.prog = self.ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)

        vertices = np.array([
            -1.0, -1.0,  0.0, 0.0,
             1.0, -1.0,  1.0, 0.0,
            -1.0,  1.0,  0.0, 1.0,
             1.0,  1.0,  1.0, 1.0,
        ], dtype='f4')
        self.vbo = self.ctx.buffer(vertices)
        self.vao = self.ctx.vertex_array(
            self.prog,
            [(self.vbo, '2f 2f', 'in_vert', 'in_uv')]
        )

    def get_fragment_shader(self) -> str:
        raise NotImplementedError

    def update_uniforms(self, w: int, h: int, time: float):
        pass

    def apply(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        if self.use_gpu and self.ctx:
            return self.apply_gpu(rgba, time)
        return self.apply_cpu(rgba, time)

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

        if 'tex' in self.prog:
            self.prog['tex'].value = 0

        self.update_uniforms(w, h, time)

        self._fbo.use()
        self.vao.render(moderngl.TRIANGLE_STRIP)

        raw = self._fbo.read(components=4)
        return np.frombuffer(raw, dtype=np.uint8).reshape((h, w, 4))

    def apply_cpu(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        raise NotImplementedError

class LiquidGlassRefractionShader(GpuFilterBase):
    def __init__(self, refraction_index: float = 1.5, distortion: float = 20.0, normal_map: Optional[np.ndarray] = None, use_gpu: bool = True):
        self.refraction_index = refraction_index
        self.distortion = distortion
        self.normal_map = normal_map
        import scipy.ndimage as ndimage
        self.ndimage = ndimage
        self._normal_texture = None
        super().__init__(use_gpu=use_gpu)

    def get_fragment_shader(self) -> str:
        return """
            #version 330
            in vec2 v_uv;
            out vec4 f_color;
            uniform sampler2D tex;
            uniform sampler2D normal_tex;
            uniform float distortion;
            uniform float width;
            uniform float height;
            uniform bool use_normal_map;

            void main() {
                vec2 n_uv = v_uv;
                vec2 offset = vec2(0.0);

                if (use_normal_map) {
                    vec4 n_color = texture(normal_tex, v_uv);
                    vec2 normal = n_color.xy * 2.0 - 1.0;
                    offset = normal * (distortion / vec2(width, height));
                } else {
                    // Simple procedural normal if none provided
                    float dx = sin(v_uv.y * 20.0) * 0.5;
                    float dy = cos(v_uv.x * 20.0) * 0.5;
                    offset = vec2(dx, dy) * (distortion / vec2(width, height));
                }

                vec2 distorted_uv = clamp(v_uv + offset, 0.0, 1.0);
                f_color = texture(tex, distorted_uv);
            }
        """

    def update_uniforms(self, w: int, h: int, time: float):
        if 'distortion' in self.prog:
            self.prog['distortion'].value = self.distortion
        if 'width' in self.prog:
            self.prog['width'].value = float(w)
        if 'height' in self.prog:
            self.prog['height'].value = float(h)

        use_normal = self.normal_map is not None
        if 'use_normal_map' in self.prog:
            self.prog['use_normal_map'].value = use_normal

        if use_normal and self.ctx:
            nm_h, nm_w = self.normal_map.shape[:2]
            if self._normal_texture is None or self._normal_texture.size != (nm_w, nm_h):
                if self._normal_texture:
                    self._normal_texture.release()
                self._normal_texture = self.ctx.texture((nm_w, nm_h), self.normal_map.shape[2], self.normal_map.tobytes())

            self._normal_texture.use(1)
            if 'normal_tex' in self.prog:
                self.prog['normal_tex'].value = 1

    def apply_cpu(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        h, w, c = rgba.shape
        y, x = np.mgrid[0:h, 0:w]

        if self.normal_map is not None:
            nm_h, nm_w = self.normal_map.shape[:2]
            nm = self.normal_map.astype(np.float32) / 255.0
            if nm.shape[:2] != (h, w):
                import cv2
                nm = cv2.resize(nm, (w, h))
            nx = nm[:, :, 0] * 2.0 - 1.0
            ny = nm[:, :, 1] * 2.0 - 1.0
        else:
            nx = np.sin((y / h) * 20.0) * 0.5
            ny = np.cos((x / w) * 20.0) * 0.5

        dx = nx * self.distortion
        dy = ny * self.distortion

        map_x = np.clip(x + dx, 0, w - 1)
        map_y = np.clip(y + dy, 0, h - 1)

        out = np.zeros_like(rgba)
        for i in range(c):
            out[:, :, i] = self.ndimage.map_coordinates(rgba[:, :, i], [map_y, map_x], order=1, mode='nearest')

        return out


class ChromaticDispersionFilter(GpuFilterBase):
    def __init__(self, dispersion: float = 5.0, use_gpu: bool = True):
        self.dispersion = dispersion
        import scipy.ndimage as ndimage
        self.ndimage = ndimage
        super().__init__(use_gpu=use_gpu)

    def get_fragment_shader(self) -> str:
        return """
            #version 330
            in vec2 v_uv;
            out vec4 f_color;
            uniform sampler2D tex;
            uniform float dispersion;
            uniform float width;
            uniform float height;

            void main() {
                vec2 center = vec2(0.5, 0.5);
                vec2 dir = v_uv - center;
                float dist = length(dir);

                vec2 r_offset = dir * (dispersion / max(width, height)) * 1.0;
                vec2 g_offset = vec2(0.0);
                vec2 b_offset = dir * (dispersion / max(width, height)) * -1.0;

                float r = texture(tex, clamp(v_uv + r_offset, 0.0, 1.0)).r;
                float g = texture(tex, clamp(v_uv + g_offset, 0.0, 1.0)).g;
                float b = texture(tex, clamp(v_uv + b_offset, 0.0, 1.0)).b;
                float a = texture(tex, v_uv).a;

                f_color = vec4(r, g, b, a);
            }
        """

    def update_uniforms(self, w: int, h: int, time: float):
        if 'dispersion' in self.prog:
            self.prog['dispersion'].value = self.dispersion
        if 'width' in self.prog:
            self.prog['width'].value = float(w)
        if 'height' in self.prog:
            self.prog['height'].value = float(h)

    def apply_cpu(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        h, w, c = rgba.shape
        y, x = np.mgrid[0:h, 0:w]

        cx, cy = w / 2.0, h / 2.0
        dir_x = (x - cx) / max(w, h)
        dir_y = (y - cy) / max(w, h)

        rx = np.clip(x + dir_x * self.dispersion, 0, w - 1)
        ry = np.clip(y + dir_y * self.dispersion, 0, h - 1)

        bx = np.clip(x - dir_x * self.dispersion, 0, w - 1)
        by = np.clip(y - dir_y * self.dispersion, 0, h - 1)

        out = rgba.copy()
        out[:, :, 0] = self.ndimage.map_coordinates(rgba[:, :, 0], [ry, rx], order=1, mode='nearest')
        out[:, :, 2] = self.ndimage.map_coordinates(rgba[:, :, 2], [by, bx], order=1, mode='nearest')

        return out


class SpecularRimSheen(GpuFilterBase):
    def __init__(self, threshold: float = 0.5, intensity: float = 1.0, color: Tuple[float, float, float] = (1.0, 1.0, 1.0), use_gpu: bool = True):
        self.threshold = threshold
        self.intensity = intensity
        self.color = np.array(color)
        super().__init__(use_gpu=use_gpu)

    def get_fragment_shader(self) -> str:
        return """
            #version 330
            in vec2 v_uv;
            out vec4 f_color;
            uniform sampler2D tex;
            uniform float threshold;
            uniform float intensity;
            uniform vec3 sheen_color;
            uniform float width;
            uniform float height;

            void main() {
                vec4 c = texture(tex, v_uv);

                float dx = 1.0 / width;
                float dy = 1.0 / height;

                float a_up = texture(tex, v_uv + vec2(0.0, -dy)).a;
                float a_down = texture(tex, v_uv + vec2(0.0, dy)).a;
                float a_left = texture(tex, v_uv + vec2(-dx, 0.0)).a;
                float a_right = texture(tex, v_uv + vec2(dx, 0.0)).a;

                float grad = abs(c.a - a_up) + abs(c.a - a_down) + abs(c.a - a_left) + abs(c.a - a_right);

                float luma = dot(c.rgb, vec3(0.299, 0.587, 0.114));

                float edge = smoothstep(0.1, 0.5, grad);
                float highlight = smoothstep(threshold, 1.0, luma) * edge * intensity;

                vec3 final_rgb = c.rgb + sheen_color * highlight;
                f_color = vec4(final_rgb, c.a);
            }
        """

    def update_uniforms(self, w: int, h: int, time: float):
        if 'threshold' in self.prog:
            self.prog['threshold'].value = self.threshold
        if 'intensity' in self.prog:
            self.prog['intensity'].value = self.intensity
        if 'sheen_color' in self.prog:
            self.prog['sheen_color'].value = tuple(self.color)
        if 'width' in self.prog:
            self.prog['width'].value = float(w)
        if 'height' in self.prog:
            self.prog['height'].value = float(h)

    def apply_cpu(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        h, w, c = rgba.shape
        alpha = rgba[:, :, 3].astype(np.float32) / 255.0

        # Simple edge detection on alpha
        grad_y, grad_x = np.gradient(alpha)
        grad_mag = np.sqrt(grad_x**2 + grad_y**2)
        edge = np.clip((grad_mag - 0.1) / 0.4, 0.0, 1.0)

        rgb = rgba[:, :, :3].astype(np.float32) / 255.0
        luma = 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]

        highlight = np.clip((luma - self.threshold) / (1.0 - self.threshold), 0.0, 1.0) * edge * self.intensity

        sheen = self.color[None, None, :] * highlight[:, :, None]

        out_rgb = np.clip((rgb + sheen) * 255.0, 0, 255).astype(np.uint8)
        out = rgba.copy()
        out[:, :, :3] = out_rgb
        return out


class FrostedBackdropBlur(GpuFilterBase):
    def __init__(self, blur_radius: float = 10.0, passes: int = 3, noise_amount: float = 0.05, use_gpu: bool = True):
        self.blur_radius = blur_radius
        self.passes = max(1, passes)
        self.noise_amount = noise_amount
        import scipy.ndimage as ndimage
        self.ndimage = ndimage
        super().__init__(use_gpu=use_gpu)

    def get_fragment_shader(self) -> str:
        # Note: GPU implementation does a single pass blur for simplicity in this example
        return """
            #version 330
            in vec2 v_uv;
            out vec4 f_color;
            uniform sampler2D tex;
            uniform float blur_radius;
            uniform float noise_amount;
            uniform float time;
            uniform float width;
            uniform float height;

            float rand(vec2 co){
                return fract(sin(dot(co.xy ,vec2(12.9898,78.233))) * 43758.5453);
            }

            void main() {
                vec4 color = vec4(0.0);
                float dx = blur_radius / width;
                float dy = blur_radius / height;

                // Simple box blur approximation for Kawase pass
                color += texture(tex, v_uv + vec2(-dx, -dy));
                color += texture(tex, v_uv + vec2( dx, -dy));
                color += texture(tex, v_uv + vec2(-dx,  dy));
                color += texture(tex, v_uv + vec2( dx,  dy));
                color *= 0.25;

                float noise = (rand(v_uv + time) - 0.5) * 2.0 * noise_amount;
                f_color = vec4(clamp(color.rgb + vec3(noise), 0.0, 1.0), color.a);
            }
        """

    def update_uniforms(self, w: int, h: int, time: float):
        if 'blur_radius' in self.prog:
            self.prog['blur_radius'].value = self.blur_radius
        if 'noise_amount' in self.prog:
            self.prog['noise_amount'].value = self.noise_amount
        if 'time' in self.prog:
            self.prog['time'].value = time
        if 'width' in self.prog:
            self.prog['width'].value = float(w)
        if 'height' in self.prog:
            self.prog['height'].value = float(h)

    def apply_gpu(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        # Multi-pass on GPU not strictly implemented in this basic setup, just run it once
        return super().apply_gpu(rgba, time)

    def apply_cpu(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        h, w, c = rgba.shape
        rgb = rgba[:, :, :3].astype(np.float32) / 255.0

        # CPU Kawase-like multi-pass blur (using gaussian for simplicity)
        sigma = self.blur_radius / (self.passes * 2)
        blurred = np.zeros_like(rgb)
        for i in range(3):
            blurred[:, :, i] = rgb[:, :, i]
            for _ in range(self.passes):
                blurred[:, :, i] = self.ndimage.gaussian_filter(blurred[:, :, i], sigma=sigma)

        # Add noise
        rng = np.random.RandomState(int((time * 1000) % 100000))
        noise = (rng.rand(h, w, 3) - 0.5) * 2.0 * self.noise_amount

        out_rgb = np.clip((blurred + noise) * 255.0, 0, 255).astype(np.uint8)
        out = rgba.copy()
        out[:, :, :3] = out_rgb
        return out
