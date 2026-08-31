from __future__ import annotations
from typing import Any, Optional
from vibmo.scene.scene import Scene
from vibmo.core.color import Color, colors
from vibmo.audio.track import AudioTrack
from vibmo.product.social import Avatar
from vibmo.audio.visualizers import CircularSpectrum
from vibmo.typography.captions import KineticCaptions
from vibmo.physics.particles import ParticleEmitter
from vibmo.fx.filters import Vignette


class SocialAudiogramTemplate:
    @classmethod
    def create_scene(
        cls,
        podcast_title: str = "The Future of AI",
        episode_name: str = "Episode 1",
        audio: Optional[str] = None,
        duration: float = 6.0,
        **kwargs: Any,
    ) -> Scene:
        scene = Scene(width=1080, height=1920, fps=60, duration=duration, background=colors.SLATE_900)

        # Audio track placeholder using an empty or generated file if possible
        audio_track = AudioTrack(audio or "dummy.mp3")

        # We need an Avatar for Stage 1
        avatar = scene.add(Avatar(size=400, position=(540, 500)))

        # Audio-reactive pulsating glow ring
        spectrum = scene.add(CircularSpectrum(audio=audio_track, radius=250, position=(540, 500), colors_palette=[colors.EMERALD_500]))

        # TikTok-style KineticCaptions displaying dynamic bouncing karaoke subtitles
        words = []
        start_time = 0.0
        full_text = podcast_title + " " + episode_name
        word_list = full_text.split()
        time_per_word = duration / max(1, len(word_list))
        for w in word_list:
            words.append({"text": w, "start": start_time, "end": start_time + time_per_word})
            start_time += time_per_word

        captions = scene.add(KineticCaptions(words=words, position=(540, 1200)))

        # Subtle ambient floating dust particles and vignette lighting
        dust = scene.add(ParticleEmitter(preset="ambient_dust", position=(540, 1920), colors_palette=[colors.SLATE_400]))
        scene.add_post_fx(Vignette(intensity=0.5))

        @scene.animate
        def main():
            yield scene.all(
                avatar.pop_in(),
                spectrum.fade_in(),
                captions.fade_in()
            )
            yield scene.wait(duration)

        return scene


class TmplSocialAudiogramSuite(SocialAudiogramTemplate):
    @classmethod
    def build_scene(
        cls,
        title: Optional[str] = None,
        podcast_title: Optional[str] = None,
        episode: Optional[str] = None,
        episode_name: Optional[str] = None,
        audio: Optional[str] = None,
        duration: float = 6.0,
        **kwargs: Any,
    ) -> Scene:
        p_title = title if title is not None else (podcast_title if podcast_title is not None else "The Future of AI")
        e_name = episode if episode is not None else (episode_name if episode_name is not None else "Episode 1")
        aud = audio if audio is not None else kwargs.pop("audio_file", "dummy.mp3")
        return cls.create_scene(
            podcast_title=p_title,
            episode_name=e_name,
            audio=aud,
            duration=duration,
            **kwargs,
        )


__all__ = [
    "SocialAudiogramTemplate",
    "TmplSocialAudiogramSuite",
]
