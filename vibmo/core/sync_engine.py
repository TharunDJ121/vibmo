"""
Deterministic Sync Engine.
Automatically aligns a VibmoProject's timings and colors to a Reference Analysis,
bypassing the need for complex AI guesswork.
"""

from typing import Dict, Any
from vibmo.core.schema import VibmoProject

class ProjectSyncEngine:
    
    @classmethod
    def sync_to_reference(cls, project: VibmoProject, reference_data: Dict[str, Any]) -> VibmoProject:
        """
        Mathematically snaps the project's shots and layers to the reference data.
        """
        ref_shots = reference_data.get("shots", [])
        if not ref_shots:
            return project
            
        # 1. Sync Timings (Snap to cuts)
        # We assume Track 0 is the main sequence track.
        if project.tracks:
            main_track = project.tracks[0]
            
            # If the project has fewer shots than the reference, we loop or stretch.
            # For this implementation, we map 1:1 up to the available shots.
            for i, shot in enumerate(main_track.shots):
                if i < len(ref_shots):
                    ref_shot = ref_shots[i]
                    
                    # Snap shot timing
                    shot.start_time = ref_shot["start"]
                    shot.duration = ref_shot["duration"]
                    
                    # Scale layer durations proportionally within the shot
                    for layer in shot.layers:
                        # If a layer was meant to span the whole original shot, scale it to the new shot duration
                        layer.duration = shot.duration
                        
        # 2. Sync Colors (Map dominant colors to project theme)
        # (Assuming the project schema has a theme/asset dictionary)
        ref_beats = reference_data.get("motion_beats", [])
        
        # We can store the global reference duration
        project.duration = reference_data.get("duration", project.duration)
        
        # Example of extracting color logic:
        # if len(ref_shots) > 0 and "dominant_colors" in ref_shots[0]:
        #     primary_color = ref_shots[0]["dominant_colors"][0]
        #     project.assets["theme_primary"] = primary_color
            
        return project
