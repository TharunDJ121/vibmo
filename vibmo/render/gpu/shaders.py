"""
High-Performance GLSL Shaders for ModernGL Hardware-Accelerated GPU Post-Processing and Layer Compositing.
Includes Bloom, Glow, Gaussian Blur, Chromatic Aberration, Vignette, Film Grain,
Photoshop/After Effects Blend Modes, Track Mattes, 3D Quad Projection, and 3D LUTs.
"""

VERTEX_SHADER_QUAD = """
#version 330
in vec2 in_vert;
in vec2 in_uv;
out vec2 v_uv;

void main() {
    v_uv = in_uv;
    gl_Position = vec4(in_vert, 0.0, 1.0);
}
"""

VERTEX_SHADER_3D_QUAD = """
#version 330
uniform mat4 u_mvp;
in vec3 in_vert;
in vec2 in_uv;
out vec2 v_uv;

void main() {
    v_uv = in_uv;
    gl_Position = u_mvp * vec4(in_vert, 1.0);
}
"""

FRAGMENT_SHADER_QUAD_TEXTURE = """
#version 330
uniform sampler2D u_texture;
uniform float u_opacity;

in vec2 v_uv;
out vec4 fragColor;

void main() {
    vec4 col = texture(u_texture, v_uv);
    fragColor = vec4(col.rgb, col.a * clamp(u_opacity, 0.0, 1.0));
}
"""

FRAGMENT_SHADER_BLEND_MODES = """
#version 330
uniform sampler2D u_base_texture;
uniform sampler2D u_layer_texture;
uniform int u_blend_mode;
uniform float u_opacity;

in vec2 v_uv;
out vec4 fragColor;

// RGB <-> HSL conversions for color blend modes
vec3 rgb2hsl(vec3 c) {
    float cmin = min(min(c.r, c.g), c.b);
    float cmax = max(max(c.r, c.g), c.b);
    float delta = cmax - cmin;
    vec3 hsl = vec3(0.0);
    hsl.z = (cmax + cmin) * 0.5;

    if (delta > 1e-5) {
        hsl.y = hsl.z < 0.5 ? delta / (cmax + cmin) : delta / (2.0 - cmax - cmin);
        if (c.r == cmax) hsl.x = (c.g - c.b) / delta;
        else if (c.g == cmax) hsl.x = 2.0 + (c.b - c.r) / delta;
        else hsl.x = 4.0 + (c.r - c.g) / delta;
        hsl.x = fract(hsl.x / 6.0);
    }
    return hsl;
}

float hue2rgb(float p, float q, float t) {
    if (t < 0.0) t += 1.0;
    if (t > 1.0) t -= 1.0;
    if (t < 1.0/6.0) return p + (q - p) * 6.0 * t;
    if (t < 1.0/2.0) return q;
    if (t < 2.0/3.0) return p + (q - p) * (2.0/3.0 - t) * 6.0;
    return p;
}

vec3 hsl2rgb(vec3 hsl) {
    if (hsl.y < 1e-5) return vec3(hsl.z);
    float q = hsl.z < 0.5 ? hsl.z * (1.0 + hsl.y) : hsl.z + hsl.y - hsl.z * hsl.y;
    float p = 2.0 * hsl.z - q;
    return vec3(
        hue2rgb(p, q, hsl.x + 1.0/3.0),
        hue2rgb(p, q, hsl.x),
        hue2rgb(p, q, hsl.x - 1.0/3.0)
    );
}

void main() {
    vec4 base = texture(u_base_texture, v_uv);
    vec4 layer = texture(u_layer_texture, v_uv);
    float op = clamp(u_opacity, 0.0, 1.0) * layer.a;
    
    if (op <= 1e-5) {
        fragColor = base;
        return;
    }

    vec3 b = base.rgb;
    vec3 l = layer.rgb;
    vec3 blended = l;

    // 0: Normal
    if (u_blend_mode == 0) {
        blended = l;
    }
    // 1: Multiply
    else if (u_blend_mode == 1) {
        blended = b * l;
    }
    // 2: Screen
    else if (u_blend_mode == 2) {
        blended = 1.0 - (1.0 - b) * (1.0 - l);
    }
    // 3: Overlay
    else if (u_blend_mode == 3) {
        blended = mix(2.0 * b * l, 1.0 - 2.0 * (1.0 - b) * (1.0 - l), step(0.5, b));
    }
    // 4: Darken
    else if (u_blend_mode == 4) {
        blended = min(b, l);
    }
    // 5: Lighten
    else if (u_blend_mode == 5) {
        blended = max(b, l);
    }
    // 6: Color Dodge
    else if (u_blend_mode == 6) {
        blended = clamp(b / max(vec3(1e-4), 1.0 - l), 0.0, 1.0);
    }
    // 7: Color Burn
    else if (u_blend_mode == 7) {
        blended = clamp(1.0 - (1.0 - b) / max(vec3(1e-4), l), 0.0, 1.0);
    }
    // 8: Hard Light
    else if (u_blend_mode == 8) {
        blended = mix(2.0 * b * l, 1.0 - 2.0 * (1.0 - b) * (1.0 - l), step(0.5, l));
    }
    // 9: Soft Light
    else if (u_blend_mode == 9) {
        blended = (1.0 - 2.0 * l) * b * b + 2.0 * l * b;
    }
    // 10: Difference
    else if (u_blend_mode == 10) {
        blended = abs(b - l);
    }
    // 11: Exclusion
    else if (u_blend_mode == 11) {
        blended = b + l - 2.0 * b * l;
    }
    // 12: Hue
    else if (u_blend_mode == 12) {
        vec3 baseH = rgb2hsl(b);
        vec3 layerH = rgb2hsl(l);
        blended = hsl2rgb(vec3(layerH.x, baseH.y, baseH.z));
    }
    // 13: Saturation
    else if (u_blend_mode == 13) {
        vec3 baseH = rgb2hsl(b);
        vec3 layerH = rgb2hsl(l);
        blended = hsl2rgb(vec3(baseH.x, layerH.y, baseH.z));
    }
    // 14: Color
    else if (u_blend_mode == 14) {
        vec3 baseH = rgb2hsl(b);
        vec3 layerH = rgb2hsl(l);
        blended = hsl2rgb(vec3(layerH.x, layerH.y, baseH.z));
    }
    // 15: Luminosity
    else if (u_blend_mode == 15) {
        vec3 baseH = rgb2hsl(b);
        vec3 layerH = rgb2hsl(l);
        blended = hsl2rgb(vec3(baseH.x, baseH.y, layerH.z));
    }
    // 16: Add
    else if (u_blend_mode == 16) {
        blended = min(vec3(1.0), b + l);
    }
    // 17: Subtract
    else if (u_blend_mode == 17) {
        blended = max(vec3(0.0), b - l);
    }

    vec3 final_rgb = mix(base.rgb, blended, op);
    float final_a = clamp(base.a + op * (1.0 - base.a), 0.0, 1.0);
    fragColor = vec4(final_rgb, final_a);
}
"""

FRAGMENT_SHADER_TRACK_MATTE = """
#version 330
uniform sampler2D u_target_texture;
uniform sampler2D u_matte_texture;
uniform int u_matte_type; // 0: Alpha, 1: Luma
uniform bool u_inverted;

in vec2 v_uv;
out vec4 fragColor;

void main() {
    vec4 target = texture(u_target_texture, v_uv);
    vec4 matte = texture(u_matte_texture, v_uv);
    
    float factor = 1.0;
    if (u_matte_type == 0) {
        factor = matte.a;
    } else {
        factor = dot(matte.rgb, vec3(0.299, 0.587, 0.114));
    }

    if (u_inverted) {
        factor = 1.0 - factor;
    }

    factor = clamp(factor, 0.0, 1.0);
    fragColor = vec4(target.rgb, target.a * factor);
}
"""

FRAGMENT_SHADER_LUT3D = """
#version 330
uniform sampler2D u_texture;
uniform sampler3D u_lut;
uniform float u_intensity;

in vec2 v_uv;
out vec4 fragColor;

void main() {
    vec4 color = texture(u_texture, v_uv);
    vec3 graded = texture(u_lut, color.rgb).rgb;
    vec3 final_rgb = mix(color.rgb, graded, clamp(u_intensity, 0.0, 1.0));
    fragColor = vec4(final_rgb, color.a);
}
"""

FRAGMENT_SHADER_POST_FX = """
#version 330
uniform sampler2D u_texture;
uniform sampler2D u_bloom_texture;
uniform float u_time;
uniform float u_vignette_intensity;
uniform float u_vignette_radius;
uniform float u_grain_amount;
uniform float u_bloom_intensity;
uniform float u_chromatic_aberration;
uniform vec2 u_resolution;

in vec2 v_uv;
out vec4 fragColor;

// High-speed pseudo-random hash
float hash(vec2 p) {
    vec3 p3  = fract(vec3(p.xyx) * 0.1031);
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.x + p3.y) * p3.z);
}

void main() {
    vec2 uv = v_uv;
    vec4 color;

    // 1. GPU Chromatic Aberration (RGB Radial Split)
    if (u_chromatic_aberration > 0.0) {
        vec2 dir = uv - 0.5;
        float dist = length(dir);
        vec2 offset = dir * (dist * u_chromatic_aberration * 0.03);
        
        float r = texture(u_texture, uv + offset).r;
        float g = texture(u_texture, uv).g;
        float b = texture(u_texture, uv - offset).b;
        float a = texture(u_texture, uv).a;
        color = vec4(r, g, b, a);
    } else {
        color = texture(u_texture, uv);
    }

    // 2. GPU Additive Bloom & Optical Glow
    if (u_bloom_intensity > 0.0) {
        vec4 bloom = texture(u_bloom_texture, uv);
        color.rgb += bloom.rgb * u_bloom_intensity;
    }
    
    // 3. GPU Smooth Vignette
    if (u_vignette_intensity > 0.0) {
        vec2 uv_norm = (uv - 0.5) * vec2(u_resolution.x / u_resolution.y, 1.0);
        float dist = length(uv_norm);
        float max_d = length(vec2(u_resolution.x / u_resolution.y, 1.0) * 0.5);
        float norm_d = dist / max_d;
        float falloff = clamp((norm_d - u_vignette_radius) / (1.0 - u_vignette_radius), 0.0, 1.0);
        color.rgb *= (1.0 - falloff * u_vignette_intensity);
    }
    
    // 4. GPU Film Grain & Anti-Banding Dither
    if (u_grain_amount > 0.0) {
        vec2 noise_uv = uv * u_resolution + vec2(u_time * 123.456, u_time * 789.012);
        float noise = (hash(noise_uv) - 0.5) * 2.0;
        float luma = dot(color.rgb, vec3(0.299, 0.587, 0.114));
        float weight = clamp(sin(luma * 3.14159) * 1.2, 0.0, 1.0);
        color.rgb += noise * u_grain_amount * weight;
    }
    
    fragColor = clamp(color, 0.0, 1.0);
}
"""

FRAGMENT_SHADER_BLOOM_EXTRACT = """
#version 330
uniform sampler2D u_texture;
uniform float u_threshold;

in vec2 v_uv;
out vec4 fragColor;

void main() {
    vec4 color = texture(u_texture, v_uv);
    float luma = dot(color.rgb, vec3(0.299, 0.587, 0.114));
    if (luma > u_threshold) {
        float factor = (luma - u_threshold) / max(0.01, 1.0 - u_threshold);
        fragColor = vec4(color.rgb * factor, color.a);
    } else {
        fragColor = vec4(0.0, 0.0, 0.0, 0.0);
    }
}
"""

FRAGMENT_SHADER_SEPARABLE_BLUR = """
#version 330
uniform sampler2D u_texture;
uniform vec2 u_direction;
uniform vec2 u_resolution;
uniform float u_blur_radius;

in vec2 v_uv;
out vec4 fragColor;

void main() {
    vec2 off = (u_direction * max(1.0, u_blur_radius)) / u_resolution;
    vec4 sum = vec4(0.0);
    
    // 13-Tap High-Quality Gaussian Kernel
    sum += texture(u_texture, v_uv - 6.0 * off) * 0.002216;
    sum += texture(u_texture, v_uv - 5.0 * off) * 0.008764;
    sum += texture(u_texture, v_uv - 4.0 * off) * 0.026995;
    sum += texture(u_texture, v_uv - 3.0 * off) * 0.064759;
    sum += texture(u_texture, v_uv - 2.0 * off) * 0.120985;
    sum += texture(u_texture, v_uv - 1.0 * off) * 0.176033;
    sum += texture(u_texture, v_uv)               * 0.200500;
    sum += texture(u_texture, v_uv + 1.0 * off) * 0.176033;
    sum += texture(u_texture, v_uv + 2.0 * off) * 0.120985;
    sum += texture(u_texture, v_uv + 3.0 * off) * 0.064759;
    sum += texture(u_texture, v_uv + 4.0 * off) * 0.026995;
    sum += texture(u_texture, v_uv + 5.0 * off) * 0.008764;
    sum += texture(u_texture, v_uv + 6.0 * off) * 0.002216;
    
    fragColor = sum;
}
"""
