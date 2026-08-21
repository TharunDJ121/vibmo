"""
High-Performance GLSL Shaders for ModernGL Hardware-Accelerated GPU Post-Processing.
Includes Bloom, Glow, Gaussian Blur, Chromatic Aberration, Vignette, Film Grain, and Color Grading.
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
