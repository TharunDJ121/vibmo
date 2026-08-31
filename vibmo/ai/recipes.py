"""
Masterpiece Recipe Library.
A collection of pre-curated, studio-quality VibmoProject JSON schemas.
The AI's job is simply to select a recipe and inject the user's copy, guaranteeing broadcast-quality layout.
"""

from typing import Dict, Any, List
import copy
from vibmo.core.schema import VibmoProject, Track, Shot, Layer, LayerType

class RecipeLibrary:
    
    # In a real production system, these would be loaded from .json files crafted in the Web Studio.
    # For now, we define the schemas procedurally.
    
    _recipes = {
        "apple_keynote_title": {
            "description": "Minimalist, high-contrast title card with smooth ease-out scaling, Apple style.",
            "build_fn": lambda text_payload: RecipeLibrary._build_apple_title(text_payload)
        },
        "vox_explainer_map": {
            "description": "A split-screen layout with a map or image on the left, and kinetic highlight text on the right.",
            "build_fn": lambda text_payload: RecipeLibrary._build_vox_map(text_payload)
        }
    }
    
    @classmethod
    def get_available_recipes(cls) -> List[Dict[str, str]]:
        return [{"id": k, "description": v["description"]} for k, v in cls._recipes.items()]
        
    @classmethod
    def generate_from_recipe(cls, recipe_id: str, payload: Dict[str, Any]) -> VibmoProject:
        """
        Instantiates a pristine, studio-quality schema and injects the AI's content payload.
        """
        if recipe_id not in cls._recipes:
            raise ValueError(f"Unknown recipe: {recipe_id}")
            
        return cls._recipes[recipe_id]["build_fn"](payload)
        
    @staticmethod
    def _build_apple_title(payload: Dict[str, Any]) -> VibmoProject:
        proj = VibmoProject(duration=4.0, fps=60)
        shot = Shot(id="s1", start_time=0.0, duration=4.0)
        
        # Background Solid
        shot.layers.append(Layer(
            id="bg", type=LayerType.SOLID, name="Background",
            properties={"color": payload.get("bg_color", "#000000")}
        ))
        
        # Typography Layer (perfectly kerned, centered)
        shot.layers.append(Layer(
            id="title", type=LayerType.TEXT, name="Main Title",
            properties={
                "text": payload.get("headline", "PRO"),
                "font_family": "SF Pro Display",
                "font_size": 180,
                "color": payload.get("text_color", "#FFFFFF"),
                "align": "center",
                "tracking": -0.02 # Studio polish: tight tracking for massive display text
            }
        ))
        
        # Subtitle Layer
        shot.layers.append(Layer(
            id="subtitle", type=LayerType.TEXT, name="Sub Title",
            properties={
                "text": payload.get("subhead", "Now with M4."),
                "font_family": "SF Pro Text",
                "font_size": 42,
                "color": "#888888",
                "align": "center",
                "position_y": 120
            }
        ))
        
        proj.add_shot(0, shot)
        return proj
        
    @staticmethod
    def _build_vox_map(payload: Dict[str, Any]) -> VibmoProject:
        proj = VibmoProject(duration=6.0, fps=60)
        shot = Shot(id="s1", start_time=0.0, duration=6.0)
        
        # Left split screen media
        shot.layers.append(Layer(
            id="media_left", type=LayerType.IMAGE, name="Map/Graphic",
            properties={
                "image_path": payload.get("image_path", "assets/default_map.png"),
                "width": 960, "height": 1080, "position_x": -480
            }
        ))
        
        # Right split solid
        shot.layers.append(Layer(
            id="bg_right", type=LayerType.SOLID, name="Right Pane",
            properties={"color": "#F4F4F0", "width": 960, "height": 1080, "position_x": 480}
        ))
        
        # Highlight Text
        shot.layers.append(Layer(
            id="explainer_text", type=LayerType.TEXT, name="Explainer",
            properties={
                "text": payload.get("highlight", "The crisis started here."),
                "font_family": "Helvetica Neue",
                "font_size": 72,
                "color": "#111111",
                "highlight_color": "#FFDE00", # Vox yellow
                "position_x": 480,
                "align": "left",
                "max_width": 800
            }
        ))
        
        proj.add_shot(0, shot)
        return proj
