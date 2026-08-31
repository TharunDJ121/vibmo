"""
Top-level Scene canvas, Animation orchestrator, Snapshots, Storyboards, and Video Renderer.
"""

from __future__ import annotations
import os
import math
from typing import Any, Callable, Dict, Generator, List, Optional, Sequence, Union
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from vibmo.core.color import Color, colors
from vibmo.scene.node import Node
from vibmo.scene.camera import Camera2D
from vibmo.timeline.scheduler import Choreographer, all as all_action, wait as wait_action
from vibmo.render.rasterizer import Rasterizer
from vibmo.render.pipeline import Pipeline


class Param:
    """Tweakable parameter exposed to the interactive web studio and CLI."""

    def __init__(
        self,
        name: str,
        default: Any,
        param_type: str = "auto",
        min_val: Optional[float] = None,
        max_val: Optional[float] = None,
        description: str = "",
    ) -> None:
        self.name = name
        self.value = default
        self.default = default
        self.param_type = param_type
        self.min_val = min_val
        self.max_val = max_val
        self.description = description

    def get(self) -> Any:
        return self.value

    def set(self, val: Any) -> None:
        self.value = val

    def __call__(self) -> Any:
        return self.value


class Scene:
    """The central canvas and timeline container for all motion graphic elements."""

    def __init__(
        self,
        width: int = 1920,
        height: int = 1080,
        fps: float = 60.0,
        duration: float = 5.0,
        background: Optional[Union[Color, str]] = colors.SLATE_950,
        theme: Optional[Any] = None,
        props: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.width = int(width)
        self.height = int(height)
        self.fps = float(fps)
        self.duration = float(duration)
        
        resolved_bg = Color.from_any(background) if background is not None else None
        self.background = resolved_bg
        self.theme = theme
        self.props = props.copy() if props is not None else {}

        self.camera = Camera2D(scene_width=self.width, scene_height=self.height)
        self.nodes: List[Node] = []
        self.post_fx: List[Any] = []
        self.audio_path: Optional[str] = None
        self.audio_tracks: List[Any] = []
        self.params: Dict[str, Param] = {}
        self._rasterizer = Rasterizer(self.width, self.height)
        
        self.markers: List[Any] = []
        self.tracks: List[Any] = []
        
        # Foley Sound Effects Track
        from vibmo.audio.sfx import SFXTrack
        self.sfx = SFXTrack()

    def add_marker(
        self,
        time: float,
        name: str,
        color: Union[Color, str] = colors.CYAN,
        comment: str = "",
        duration: float = 0.0,
    ) -> Any:
        """Places an editorial marker on the timeline for beat drops, transitions, or cues."""
        from vibmo.timeline.marker import Marker
        marker = Marker(time=float(time), name=str(name), color=color, comment=str(comment), duration=float(duration))
        self.markers.append(marker)
        return marker

    def get_marker(self, name: str) -> Optional[Any]:
        """Finds the first marker with matching name."""
        for m in self.markers:
            if m.name == name:
                return m
        return None

    def find_markers(self, start: float = 0.0, end: Optional[float] = None) -> List[Any]:
        """Returns all markers occurring within the given time range."""
        e = end if end is not None else self.duration
        return [m for m in self.markers if start <= m.time <= e]

    def track(self, name: str, kind: str = "video") -> Any:
        """Retrieves or creates a named NLE layer track (e.g. 'Graphics', 'VO')."""
        from vibmo.timeline.track import LayerTrack
        for tr in self.tracks:
            if tr.name == name:
                return tr
        tr = LayerTrack(name=name, kind=kind, index=len(self.tracks))
        self.tracks.append(tr)
        return tr

    def get_track(self, name: str) -> Optional[Any]:
        """Finds a track by name."""
        for tr in self.tracks:
            if tr.name == name:
                return tr
        return None


    def apply_style(self, style: Any) -> Scene:
        """Applies a curated design system StylePreset (Linear Dark, Apple Keynote, Cyberpunk, etc.)."""
        from vibmo.styles.applicator import apply_style_to_scene
        return apply_style_to_scene(self, style)

    def reflow(self, aspect_ratio: Any) -> Scene:
        """Auto-reflows scene dimensions and layer layout for mobile/social formats (9:16, 1:1, 4:5)."""
        from vibmo.layout.reflow import SceneReflowEngine
        return SceneReflowEngine.reflow(self, aspect_ratio)

    def add(self, *nodes: Node) -> Any:


        for n in nodes:
            if n not in self.nodes:
                self.nodes.append(n)
        if len(nodes) == 1:
            return nodes[0]
        return self

    def action(self, *actions: Any) -> Scene:
        """Schedules one or more AnimationActions / ParallelGroups onto the timeline."""
        for act in actions:
            if hasattr(act, "apply_at"):
                act.apply_at(0.0)
            elif isinstance(act, (list, tuple)):
                from vibmo.timeline.scheduler import ParallelGroup
                ParallelGroup(act).apply_at(0.0)
        return self

    def play(self, *actions: Any) -> Scene:
        """Alias for action(): Schedules animation verbs directly without generator boilerplate."""
        return self.action(*actions)

    def remove(self, node: Node) -> None:
        if node in self.nodes:
            self.nodes.remove(node)

    def add_post_fx(self, *fx: Any) -> Scene:
        self.post_fx.extend(fx)
        return self

    def add_audio(self, audio: Any, volume: float = 1.0) -> Scene:
        """Attaches an audio track for playback and final video muxing."""
        if isinstance(audio, str):
            self.audio_path = audio
        elif hasattr(audio, "file_path"):
            self.audio_path = audio.file_path
        self.audio_volume = float(volume)
        return self

    def add_audio_track(
        self,
        audio: Any,
        start: float = 0.0,
        duration: Optional[float] = None,
        volume: float = 1.0,
        fade_in: float = 0.0,
        fade_out: float = 0.0,
        name: str = "",
    ) -> Scene:
        """Places an audio file on the timeline for a final non-destructive mix."""
        from vibmo.audio.track import TimelineAudioClip

        path = audio if isinstance(audio, str) else getattr(audio, "file_path", None)
        if not path:
            raise ValueError("Audio tracks require a file path or AudioTrack.")
        self.audio_tracks.append(
            TimelineAudioClip(
                file_path=str(path),
                start=start,
                duration=duration,
                volume=volume,
                fade_in=fade_in,
                fade_out=fade_out,
                name=name,
            )
        )
        return self

    def add_sfx(self, sound: str, time: float, volume: float = 1.0) -> Scene:
        """Schedules a procedural Foley sound effect (pop, click, whoosh, riser, bass_drop, sparkle)."""
        self.sfx.add(sound, time, volume)
        return self

    def export_audio_stems(self, output_dir: str = "stems") -> Dict[str, str]:
        """Mixes and exports isolated audio stems (Music, VO, SFX, Master) as WAV files."""
        from vibmo.audio.stems import AudioStemMixer
        return AudioStemMixer.mix_stems(self.audio_tracks, self.duration, output_dir)



    def param(
        self,
        name: str,
        default: Any,
        min: Optional[float] = None,
        max: Optional[float] = None,
        type: str = "auto",
        description: str = "",
    ) -> Param:
        """Exposes an interactive parameter for Studio and data-driven overrides."""
        actual_val = self.props.get(name, default)
        p = Param(name=name, default=actual_val, min_val=min, max_val=max, param_type=type, description=description)
        self.params[name] = p
        return p

    def all(self, *actions: Any) -> Any:
        return all_action(*actions)

    def wait(self, duration: float) -> Any:
        return wait_action(duration)

    def animate(self, fn: Union[Callable[[], Generator], Generator]) -> Callable:
        """Decorator to execute generator-based animation choreography."""
        choreographer = Choreographer()
        computed_duration = choreographer.run(fn)
        if computed_duration > self.duration:
            self.duration = computed_duration
        return fn

    # ==========================================
    # VIBE CODING & AI VISUAL FEEDBACK TOOLS
    # ==========================================

    def render_frame(self, time: float = 0.0, scale: float = 1.0) -> np.ndarray:
        """Renders an instant RGBA numpy array frame buffer at timestamp `time`."""
        return self._rasterizer.render_frame(
            root_nodes=self.nodes,
            time=time,
            background=self.background,
            camera=self.camera,
            post_fx=self.post_fx,
            scale=scale,
        )

    def snapshot(self, time: float = 0.0, path: str = "snapshot.png") -> Image.Image:
        """Renders an instant high-res PNG image at timestamp time."""
        rgba = self.render_frame(time=time)
        img = Image.fromarray(rgba, "RGBA")
        if path:
            dir_name = os.path.dirname(path)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)
            img.save(path)
        return img

    def storyboard(self, path: str = "storyboard.png", rows: int = 2, cols: int = 3) -> Image.Image:
        """
        Renders a multi-frame contact sheet showing the progression of the animation.
        Enables AI agents and creators to visually inspect the whole scene at a glance!
        """
        count = rows * cols
        times = np.linspace(0.0, max(0.1, self.duration), count)
        thumb_w = self.width // 4
        thumb_h = self.height // 4
        pad = 20
        header_h = 30

        sheet_w = cols * thumb_w + (cols + 1) * pad
        sheet_h = rows * (thumb_h + header_h) + (rows + 1) * pad

        sheet = Image.new("RGBA", (sheet_w, sheet_h), (15, 23, 42, 255))
        draw = ImageDraw.Draw(sheet)

        for i, t in enumerate(times):
            r = i // cols
            c = i % cols
            x = pad + c * (thumb_w + pad)
            y = pad + r * (thumb_h + header_h + pad)

            # Render frame
            rgba = self._rasterizer.render_frame(
                root_nodes=self.nodes,
                time=float(t),
                background=self.background,
                camera=self.camera,
                post_fx=self.post_fx,
            )
            frame_img = Image.fromarray(rgba, "RGBA").resize((thumb_w, thumb_h), Image.Resampling.BILINEAR)
            sheet.paste(frame_img, (x, y + header_h))

            # Draw time label & frame border
            time_label = f"t = {t:.2f}s ({int(t * self.fps)}f / {int(self.duration * self.fps)}f)"
            draw.text((x + 4, y + 6), time_label, fill=(241, 245, 249, 255))
            draw.rectangle([x, y + header_h, x + thumb_w, y + header_h + thumb_h], outline=(99, 102, 241, 200), width=2)

        if path:
            dir_name = os.path.dirname(path)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)
            sheet.save(path)
        return sheet

    def render(
        self,
        output_path: str = "output.mp4",
        preset: str = "mp4",
        quality: str = "high",
        motion_blur: bool = False,
        shutter_angle: float = 180.0,
        show_progress: bool = True,
        max_workers: Optional[int] = None,
        resume: bool = False,
    ) -> None:
        """Renders the scene to an MP4, WebM (with alpha), ProRes, or GIF video file.
        Quality options: 'draft' (540p@30fps instant), 'fast' (720p@30fps), 'high' (1080p@60fps master).
        """
        # Automatically render foley SFX cues if scheduled
        if hasattr(self, "sfx") and len(self.sfx.cues) > 0 and not hasattr(self, "_sfx_audio_path"):
            import tempfile, uuid
            temp_wav = os.path.join(tempfile.gettempdir(), f"vibmo_sfx_{uuid.uuid4().hex[:8]}.wav")
            self.sfx.render_to_wav(self.duration, temp_wav)
            self.add_audio_track(temp_wav, name="Procedural SFX")
            self._sfx_audio_path = temp_wav

        pipeline = Pipeline(self)

        pipeline.render_to_file(
            output_path=output_path,
            preset=preset,
            quality=quality,
            motion_blur=motion_blur,
            shutter_angle=shutter_angle,
            show_progress=show_progress,
            max_workers=max_workers,
            resume=resume,
        )

    def export_otio(self, output_path: str, timeline_name: Optional[str] = None) -> str:
        """Exports the scene timeline and markers to OpenTimelineIO (.otio) JSON format."""
        from vibmo.render.otio_exporter import OtioExporter
        return OtioExporter.export_scene(self, output_path, timeline_name=timeline_name)

    def export_fcp_xml(self, output_path: str, project_name: str = "Vibmo Sequence") -> None:
        """Exports the scene to Final Cut Pro 7 XML format for DaVinci Resolve / Premiere Pro."""
        from vibmo.render.fcp_exporter import Fcp7Exporter
        from vibmo.core.schema import VibmoProject
        proj = getattr(self, "project", None)
        if proj is None:
            proj = VibmoProject(width=self.width, height=self.height, fps=int(self.fps), duration=self.duration)
        Fcp7Exporter.export(proj, output_path, project_name=project_name)

    def validate(self) -> List[str]:
        """Performs a comprehensive pre-flight check on scene nodes, assets, and animation timings.
        Returns a list of warning/error messages. If empty, the scene is 100% valid.
        """
        issues: List[str] = []
        
        # 1. Canvas dimensions & duration
        if self.width <= 0 or self.height <= 0:
            issues.append(f"Invalid canvas dimensions: {self.width}x{self.height} (must be > 0)")
        if self.duration <= 0:
            issues.append(f"Invalid duration: {self.duration}s (must be > 0)")
        if self.fps <= 0:
            issues.append(f"Invalid FPS: {self.fps} (must be > 0)")

        # 2. Audio asset verification
        if self.audio_path and not os.path.exists(self.audio_path):
            issues.append(f"Audio file not found: '{self.audio_path}'")
        for track in self.audio_tracks:
            if not os.path.exists(track.file_path):
                issues.append(f"Audio track '{track.name or track.file_path}' file not found: '{track.file_path}'")

        # 3. Node tree inspection
        def _check_node(node: Any, path: str):
            try:
                _ = node.local_bounds(0.0)
            except Exception as e:
                issues.append(f"Node '{node.name}' ({path}) raised error calculating bounds: {e}")

            if hasattr(node, "image_path"):
                p = getattr(node, "image_path")
                if p and not os.path.exists(p):
                    issues.append(f"ImageNode '{node.name}' file not found: '{p}'")
            if hasattr(node, "video_path"):
                vp = getattr(node, "video_path")
                if vp and not os.path.exists(vp):
                    issues.append(f"VideoNode '{node.name}' file not found: '{vp}'")

            for attr_name in ["position", "scale", "rotation", "opacity", "rotate_x", "rotate_y", "z"]:
                sig = getattr(node, attr_name, None)
                if sig and hasattr(sig, "_segments"):
                    for seg in sig._segments:
                        if seg.start_time + seg.duration > self.duration + 0.05:
                            issues.append(
                                f"Animation on '{node.name}.{attr_name}' ends at t={seg.start_time + seg.duration:.2f}s, exceeding scene duration ({self.duration:.2f}s)"
                            )

            if hasattr(node, "children") and node.children:
                for child in node.children:
                    _check_node(child, f"{path} > {child.name}")

        for n in self.nodes:
            _check_node(n, n.name)

        return issues

    def describe(self) -> str:
        """Generates a structured ASCII tree description of the scene for AI agent introspection."""
        bg_val = self.background.to_hex() if hasattr(self.background, "to_hex") else str(self.background)
        lines = [
            f"✦ Scene ({self.width}x{self.height} @ {int(self.fps)} FPS, {self.duration:.2f}s)",
            f"  Background: {bg_val}",

            f"  Audio: {len(self.audio_tracks)} timeline track(s), {self.audio_path or ('SFX Track' if hasattr(self, 'sfx') and len(self.sfx.cues) > 0 else 'None')}",
            f"  Tracks: {len(self.tracks)} explicit track(s) ({', '.join(t.name for t in self.tracks)})" if self.tracks else "  Tracks: Default Scene Graph",

            f"  Markers: {', '.join(f'{m.name}@{m.time:.2f}s' for m in self.markers)}" if self.markers else "  Markers: None",
            f"  Post FX: {', '.join(fx.__class__.__name__ for fx in self.post_fx) if self.post_fx else 'None'}",
            f"  Parameters: {list(self.params.keys()) if self.params else 'None'}",
            "  Layer Tree:",

        ]

        def _print_node(node: Any, indent: int = 4):
            sp = " " * indent
            pos = node.position.get(0.0) if hasattr(node, "position") else (0, 0)
            op = node.opacity.get(0.0) if hasattr(node, "opacity") else 1.0
            scale = node.scale.get(0.0) if hasattr(node, "scale") else (1, 1)
            try:
                _, _, bw, bh = node.local_bounds(0.0)
            except Exception:
                bw, bh = 0.0, 0.0
            px = pos.x if hasattr(pos, "x") else pos[0]
            py = pos.y if hasattr(pos, "y") else pos[1]
            sx = scale.x if hasattr(scale, "x") else scale[0]
            lines.append(f"{sp}└─ [{node.__class__.__name__}] '{node.name}' pos=({px:.1f}, {py:.1f}) bounds={bw:.0f}x{bh:.0f} scale={sx:.2f} op={op:.2f}")
            if hasattr(node, "children") and node.children:
                for child in node.children:
                    _print_node(child, indent + 3)

        for n in self.nodes:
            _print_node(n)

        return "\n".join(lines)

    def to_project(self) -> Any:
        """Exports the current Scene state to a serializable VibmoProject schema."""
        from vibmo.core.schema import VibmoProject, Track, Shot, Layer, LayerType
        
        proj = VibmoProject(
            width=self.width,
            height=self.height,
            fps=int(self.fps),
            duration=self.duration
        )
        
        # In this first iteration, we dump the root nodes into a single Shot in a single Track.
        # A fully structured NLE timeline would map self.tracks to proj.tracks.
        main_shot = Shot(id="main_shot", start_time=0.0, duration=self.duration)
        
        for idx, node in enumerate(self.nodes):
            # Simplistic mapping of node types to LayerTypes
            l_type = LayerType.COMPONENT
            if node.__class__.__name__ == "Text":
                l_type = LayerType.TEXT
            elif node.__class__.__name__ == "ImageNode":
                l_type = LayerType.IMAGE
            elif node.__class__.__name__ == "VideoNode":
                l_type = LayerType.VIDEO
                
            layer = Layer(
                id=f"layer_{idx}_{node.name}",
                type=l_type,
                name=node.name,
                start_time=0.0,
                duration=self.duration,
                properties={"type": node.__class__.__name__}
            )
            main_shot.layers.append(layer)
            
        proj.add_shot(0, main_shot)
        return proj

    @classmethod
    def from_project(cls, proj: Any) -> Scene:
        """Rehydrates a Scene from a VibmoProject schema."""
        scene = cls(
            width=proj.width,
            height=proj.height,
            fps=proj.fps,
            duration=proj.duration
        )
        
        # Import node classes for hydration
        from vibmo.typography.text import Text
        from vibmo.scene.node import Node
        
        # In a full implementation, we would iterate through all tracks and shots.
        # For this foundation, we'll extract layers from the first shot of the first track.
        if proj.tracks and proj.tracks[0].shots:
            main_shot = proj.tracks[0].shots[0]
            for layer in main_shot.layers:
                node_type = layer.properties.get("type", "Node")
                node = None
                
                # Simple Factory Pattern
                if node_type == "Text":
                    node = Text(
                        text=layer.properties.get("text", layer.name),
                        font_size=layer.properties.get("font_size", 32),
                        font_family=layer.properties.get("font_family", "Inter")
                    )
                else:
                    # Generic fallback
                    node = Node(name=layer.name)
                    
                if node:
                    scene.add(node)
                    
        return scene

    def preview(self, host: str = "127.0.0.1", port: int = 8000) -> None:
        """Launches the interactive in-browser studio for direct visual editing."""
        from vibmo.studio.server import launch_studio
        launch_studio(self, host=host, port=port)

    @classmethod
    def from_prompt(cls, prompt: str, duration: float = 4.0, **kwargs: Any) -> Scene:
        """Synthesizes a complete animated scene with components and choreographies from a natural language prompt."""
        from vibmo.ai.agent_scene import AgentSceneGenerator
        return AgentSceneGenerator.generate_from_prompt(prompt, duration=duration, **kwargs)
