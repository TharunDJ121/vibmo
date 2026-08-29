import numpy as np
import moderngl
from typing import Optional, Tuple
import scipy.ndimage as ndimage

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


class VhsTapeTrackingShader(GpuFilterBase):
    """
    Realistic horizontal VHS tracking noise band rolling vertically across screen.
    """
    def __init__(self, intensity: float = 1.0, speed: float = 0.5, band_height: float = 0.1, use_gpu: bool = True):
        self.intensity = intensity
        self.speed = speed
        self.band_height = band_height
        super().__init__(use_gpu=use_gpu)

    def get_fragment_shader(self) -> str:
        return """
            #version 330
            in vec2 v_uv;
            out vec4 f_color;
            uniform sampler2D tex;
            uniform float time;
            uniform float intensity;
            uniform float speed;
            uniform float band_height;

            float rand(vec2 co){
                return fract(sin(dot(co, vec2(12.9898, 78.233))) * 43758.5453);
            }

            void main() {
                float y_pos = fract(time * speed);
                float dist = abs(v_uv.y - y_pos);
                // Wrapping distance
                dist = min(dist, 1.0 - dist);

                float band = smoothstep(band_height, 0.0, dist);
                float noise = rand(v_uv + time) * 2.0 - 1.0;

                vec2 uv = v_uv;
                uv.x += noise * band * 0.02 * intensity;

                vec4 color = texture(tex, uv);
                float luma_noise = rand(v_uv * 100.0 + time) * 0.5 * intensity * band;
                color.rgb += luma_noise;

                f_color = color;
            }
        """

    def update_uniforms(self, w: int, h: int, time: float):
        if 'intensity' in self.prog:
            self.prog['intensity'].value = self.intensity
        if 'speed' in self.prog:
            self.prog['speed'].value = self.speed
        if 'band_height' in self.prog:
            self.prog['band_height'].value = self.band_height
        if 'time' in self.prog:
            self.prog['time'].value = time

    def apply_cpu(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        h, w, c = rgba.shape
        out = rgba.copy()
        y_pos = (time * self.speed) % 1.0

        y_coords = np.linspace(0, 1, h)
        dist = np.abs(y_coords - y_pos)
        dist = np.minimum(dist, 1.0 - dist)

        band = np.clip(1.0 - dist / max(self.band_height, 0.001), 0.0, 1.0)

        rng = np.random.RandomState(int((time * 1000) % 100000))
        noise = (rng.rand(h) * 2.0 - 1.0) * band * 0.02 * self.intensity * w

        for y in range(h):
            shift = int(noise[y])
            if shift > 0:
                out[y, shift:, :3] = rgba[y, :-shift, :3]
                out[y, :shift, :3] = rgba[y, 0, :3]
            elif shift < 0:
                out[y, :shift, :3] = rgba[y, -shift:, :3]
                out[y, shift:, :3] = rgba[y, -1, :3]

        luma_noise = rng.rand(h, w, 1) * 0.5 * self.intensity * 255.0
        luma_noise = luma_noise * band[:, None, None]

        rgb = np.clip(out[:, :, :3].astype(np.float32) + luma_noise, 0, 255).astype(np.uint8)
        out[:, :, :3] = rgb
        return out


class HeadSwitchingJitterLine(GpuFilterBase):
    """
    Bottom edge video head switching tear line and horizontal scanline shift.
    """
    def __init__(self, line_height: float = 0.05, shift_amount: float = 0.02, use_gpu: bool = True):
        self.line_height = line_height
        self.shift_amount = shift_amount
        super().__init__(use_gpu=use_gpu)

    def get_fragment_shader(self) -> str:
        return """
            #version 330
            in vec2 v_uv;
            out vec4 f_color;
            uniform sampler2D tex;
            uniform float time;
            uniform float line_height;
            uniform float shift_amount;

            float rand(float n){return fract(sin(n) * 43758.5453123);}

            void main() {
                vec2 uv = v_uv;

                if (uv.y > 1.0 - line_height) {
                    float noise = rand(uv.y * 100.0 + time) * 2.0 - 1.0;
                    uv.x += shift_amount * noise;
                }

                f_color = texture(tex, uv);

                if (uv.y > 1.0 - line_height) {
                    float scanline = sin(uv.y * 800.0) * 0.1;
                    f_color.rgb += scanline;
                }
            }
        """

    def update_uniforms(self, w: int, h: int, time: float):
        if 'line_height' in self.prog:
            self.prog['line_height'].value = self.line_height
        if 'shift_amount' in self.prog:
            self.prog['shift_amount'].value = self.shift_amount
        if 'time' in self.prog:
            self.prog['time'].value = time

    def apply_cpu(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        h, w, c = rgba.shape
        out = rgba.copy()

        tear_start = int(h * (1.0 - self.line_height))
        if tear_start >= h:
            return out

        rng = np.random.RandomState(int((time * 1000) % 100000))
        noise = (rng.rand(h - tear_start) * 2.0 - 1.0) * self.shift_amount * w

        for i, y in enumerate(range(tear_start, h)):
            shift = int(noise[i])
            if shift > 0:
                out[y, shift:, :3] = rgba[y, :-shift, :3]
                out[y, :shift, :3] = rgba[y, 0, :3]
            elif shift < 0:
                out[y, :shift, :3] = rgba[y, -shift:, :3]
                out[y, shift:, :3] = rgba[y, -1, :3]

            scanline = np.sin(y / h * 800.0) * 0.1 * 255.0
            out[y, :, :3] = np.clip(out[y, :, :3].astype(np.float32) + scanline, 0, 255).astype(np.uint8)

        return out


class ColorBleedChromaShift(GpuFilterBase):
    """
    Chroma subsampling 4:2:0 smear with red/cyan horizontal color phase displacement.
    """
    def __init__(self, red_shift: float = 0.02, blue_shift: float = -0.01, blur_amount: float = 2.0, use_gpu: bool = True):
        self.red_shift = red_shift
        self.blue_shift = blue_shift
        self.blur_amount = blur_amount
        super().__init__(use_gpu=use_gpu)

    def get_fragment_shader(self) -> str:
        return """
            #version 330
            in vec2 v_uv;
            out vec4 f_color;
            uniform sampler2D tex;
            uniform float red_shift;
            uniform float blue_shift;

            void main() {
                vec2 r_uv = v_uv + vec2(red_shift, 0.0);
                vec2 b_uv = v_uv + vec2(blue_shift, 0.0);

                float r = texture(tex, r_uv).r;
                float g = texture(tex, v_uv).g;
                float b = texture(tex, b_uv).b;
                float a = texture(tex, v_uv).a;

                f_color = vec4(r, g, b, a);
            }
        """

    def update_uniforms(self, w: int, h: int, time: float):
        if 'red_shift' in self.prog:
            self.prog['red_shift'].value = self.red_shift
        if 'blue_shift' in self.prog:
            self.prog['blue_shift'].value = self.blue_shift

    def apply_cpu(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        h, w, c = rgba.shape
        out = rgba.copy()

        r_shift = int(self.red_shift * w)
        b_shift = int(self.blue_shift * w)

        if r_shift > 0:
            out[:, :-r_shift, 0] = rgba[:, r_shift:, 0]
        elif r_shift < 0:
            out[:, -r_shift:, 0] = rgba[:, :r_shift, 0]

        if b_shift > 0:
            out[:, :-b_shift, 2] = rgba[:, b_shift:, 2]
        elif b_shift < 0:
            out[:, -b_shift:, 2] = rgba[:, :b_shift, 2]

        if self.blur_amount > 0:
            for i in [0, 2]:
                out[:, :, i] = ndimage.gaussian_filter(out[:, :, i], sigma=(0, self.blur_amount))

        return out


class AnalogStaticSnowBurst(GpuFilterBase):
    """
    Random magnetic tape dropouts and white noise spark bursts.
    """
    def __init__(self, intensity: float = 0.1, frequency: float = 0.05, use_gpu: bool = True):
        self.intensity = intensity
        self.frequency = frequency
        super().__init__(use_gpu=use_gpu)

    def get_fragment_shader(self) -> str:
        return """
            #version 330
            in vec2 v_uv;
            out vec4 f_color;
            uniform sampler2D tex;
            uniform float time;
            uniform float intensity;
            uniform float frequency;

            float rand(vec2 co){
                return fract(sin(dot(co, vec2(12.9898, 78.233))) * 43758.5453);
            }

            void main() {
                vec4 color = texture(tex, v_uv);

                float trigger = rand(vec2(time, time)) < frequency ? 1.0 : 0.0;

                if (trigger > 0.5) {
                    float noise = rand(v_uv + time);
                    if (noise > 1.0 - intensity) {
                        color.rgb = vec3(1.0); // White spark
                    } else if (noise < intensity) {
                        color.rgb = vec3(0.0); // Black dropout
                    }
                }

                f_color = color;
            }
        """

    def update_uniforms(self, w: int, h: int, time: float):
        if 'intensity' in self.prog:
            self.prog['intensity'].value = self.intensity
        if 'frequency' in self.prog:
            self.prog['frequency'].value = self.frequency
        if 'time' in self.prog:
            self.prog['time'].value = time

    def apply_cpu(self, rgba: np.ndarray, time: float = 0.0) -> np.ndarray:
        h, w, c = rgba.shape
        out = rgba.copy()

        rng = np.random.RandomState(int((time * 1000) % 100000))

        if rng.rand() < self.frequency:
            noise = rng.rand(h, w)

            white_mask = noise > (1.0 - self.intensity)
            black_mask = noise < self.intensity

            out[white_mask, :3] = 255
            out[black_mask, :3] = 0

        return out
