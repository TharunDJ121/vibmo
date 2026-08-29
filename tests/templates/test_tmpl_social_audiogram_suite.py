import pytest
from vibmo.templates.turnkey.tmpl_social_audiogram_suite import SocialAudiogramTemplate
import motio.agent_api as ma

def test_social_audiogram_template():
    scene = SocialAudiogramTemplate.create_scene("My Podcast", "Episode 1", duration=2.0)

    assert scene.width == 1080
    assert scene.height == 1920
    assert scene.duration >= 2.0

    # Verify nodes
    avatar = None
    spectrum = None
    captions = None
    particles = None

    for node in scene.nodes:
        if isinstance(node, ma.Avatar):
            avatar = node
        elif isinstance(node, ma.CircularSpectrum):
            spectrum = node
        elif isinstance(node, ma.KineticCaptions):
            captions = node
        elif isinstance(node, ma.ParticleEmitter):
            particles = node

    assert avatar is not None, "Avatar missing"
    assert spectrum is not None, "CircularSpectrum missing"
    assert captions is not None, "KineticCaptions missing"
    assert particles is not None, "ParticleEmitter missing"

    # Verify post fx
    vignette = None
    for fx in scene.post_fx:
        if isinstance(fx, ma.Vignette):
            vignette = fx

    assert vignette is not None, "Vignette FX missing"
