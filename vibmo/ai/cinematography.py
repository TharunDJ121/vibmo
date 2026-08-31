"""
5-Layer Cinematography & Shot Prompt Engineering Suite for Vibmo.

Based on professional cinematography direction:
  Layer 1: Camera (lens optics, focal length, depth of field)
  Layer 2: Camera Movement (shot framing size, trajectory, motion speed)
  Layer 3: Subject & Texture (core subject description + tactile material keywords)
  Layer 4: Lighting & Atmospheric Key (color temperature, contrast key, volumetric spill)
  Layer 5: Style & Aesthetic Mood (adapted from brand design playbook)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


_SHOT_SIZE_MAP = {
    "extreme_wide": "extreme wide shot establishing vast environment and spatial scale",
    "wide": "wide shot framing full subject and surrounding architecture",
    "medium_wide": "medium-wide shot framing subject with clear contextual environment",
    "medium": "medium shot framed from waist up with clean balanced composition",
    "medium_close": "medium close-up from chest up focusing on expression",
    "close_up": "close-up shot emphasizing fine micro-details and textures",
    "extreme_close_up": "extreme macro close-up revealing intricate surface fidelity",
    "over_shoulder": "cinematic over-the-shoulder perspective with foreground depth",
    "insert": "insert shot focusing exclusively on a specific tactile UI or product interaction",
    "establishing": "grand establishing shot setting the visual world and lighting tone",
}

_MOVEMENT_MAP = {
    "static": "locked-off tripod static camera with pristine stability",
    "pan_left": "smooth mechanical pan to the left across the scene",
    "pan_right": "smooth mechanical pan to the right across the scene",
    "tilt_up": "gentle cinematic tilt upward revealing height and grandeur",
    "tilt_down": "deliberate tilt downward focusing into the core subject",
    "dolly_in": "slow controlled dolly in toward the subject creating emotional intimacy",
    "dolly_out": "smooth dolly out revealing expanding surroundings",
    "tracking_left": "dynamic tracking shot moving parallel to the left",
    "tracking_right": "dynamic tracking shot moving parallel to the right",
    "orbital": "orbital 360 camera path smoothly rotating around the center subject",
    "crane_up": "sweeping crane shot rising vertically with dramatic elevation",
    "handheld": "subtle organic handheld camera with natural human micro-movement",
    "zoom_in": "gradual optical zoom in emphasizing subject focus",
}

_LIGHTING_MAP = {
    "high_key": "bright crisp high-key commercial lighting with minimal soft shadows",
    "low_key": "dramatic low-key moody lighting with rich chiaroscuro shadows",
    "neon": "cyberpunk neon lighting with vibrant cyan and magenta color spills",
    "golden_hour": "warm 3200K golden hour sunlight with long soft shadows",
    "blue_hour": "cool 6500K blue hour twilight with atmospheric haze",
    "volumetric": "volumetric light rays piercing through atmospheric fog",
    "rim_lit": "razor-sharp rim lighting emphasizing silhouette contours",
    "studio_clean": "pristine multi-point softbox studio lighting with neutral reflections",
}

_DOF_MAP = {
    "shallow": "shallow depth of field at f/1.4 with creamy circular bokeh",
    "medium": "medium depth of field at f/4.0 balancing subject separation and context",
    "deep": "deep focus at f/11 with sharp edge-to-edge clarity across all planes",
}


@dataclass
class ShotSpecification:
    shot_size: str = "medium_wide"
    movement: str = "dolly_in"
    lighting: str = "studio_clean"
    depth_of_field: str = "shallow"
    subject: str = "Modern sleek Glassmorphic dashboard card displaying live metrics"
    texture_keywords: list[str] | None = None
    color_temperature: str = "neutral"
    style_mood: str = "clean, futuristic, premium tech aesthetic"


class ShotPromptBuilder:
    """Constructs prompt specifications for AI generative media."""

    @classmethod
    def build_prompt(cls, shot: ShotSpecification | dict[str, Any]) -> str:
        if isinstance(shot, dict):
            shot_spec = ShotSpecification(
                shot_size=shot.get("shot_size", "medium_wide"),
                movement=shot.get("movement", "dolly_in"),
                lighting=shot.get("lighting", "studio_clean"),
                depth_of_field=shot.get("depth_of_field", "shallow"),
                subject=shot.get("subject", shot.get("description", "Aesthetic motion graphics asset")),
                texture_keywords=shot.get("texture_keywords", []),
                color_temperature=shot.get("color_temperature", "neutral"),
                style_mood=shot.get("style_mood", shot.get("style", "modern clean")),
            )
        else:
            shot_spec = shot

        layers: list[str] = []

        # Layer 1 & 2: Camera & Framing
        camera_part = _SHOT_SIZE_MAP.get(shot_spec.shot_size, shot_spec.shot_size)
        movement_part = _MOVEMENT_MAP.get(shot_spec.movement, shot_spec.movement)
        dof_part = _DOF_MAP.get(shot_spec.depth_of_field, shot_spec.depth_of_field)
        layers.append(f"{camera_part}, {movement_part}, {dof_part}")

        # Layer 3: Subject & Textures
        subject_str = shot_spec.subject
        if shot_spec.texture_keywords:
            subject_str += f", tactile textures: {', '.join(shot_spec.texture_keywords)}"
        layers.append(subject_str)

        # Layer 4: Lighting & Atmosphere
        lighting_str = _LIGHTING_MAP.get(shot_spec.lighting, shot_spec.lighting)
        if shot_spec.color_temperature != "neutral":
            lighting_str += f", {shot_spec.color_temperature} tone balance"
        layers.append(lighting_str)

        # Layer 5: Style & Mood
        layers.append(f"Aesthetic: {shot_spec.style_mood}, 8k render, Unreal Engine 5 octane lighting, masterwork composition")

        return " | ".join(layers)
