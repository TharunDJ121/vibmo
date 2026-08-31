import pytest
import numpy as np
from motio.agent_api import (
    Scene,
    TmplAiCodeAssistantSuite,
    TmplFintechCryptoCardSuite,
    TmplDeveloperCliLaunchSuite,
    TmplSaasYcPitchSuite,
    TmplSocialAudiogramSuite,
    AiCodeAssistantTemplate,
    FintechCryptoCardTemplate,
    DeveloperCliLaunchTemplate,
    SaasYcPitchTemplate,
    SocialAudiogramTemplate,
)


@pytest.mark.parametrize(
    "suite_cls,build_kwargs",
    [
        (TmplAiCodeAssistantSuite, {"prompt": "Build a SaaS in Python"}),
        (TmplFintechCryptoCardSuite, {"cardholder": "SATOSHI NAKAMOTO"}),
        (TmplDeveloperCliLaunchSuite, {"command": "npm install -g vibmo"}),
        (TmplSaasYcPitchSuite, {"mrr": "$120k", "growth": "+40%"}),
        (TmplSocialAudiogramSuite, {"audio": "podcast.mp3", "title": "The Future of AI"}),
    ],
)
def test_turnkey_templates_agents_md_recipes(suite_cls, build_kwargs):
    """Verifies that all 5 turnkey suites build scenes according to AGENTS.md catalog recipes."""
    scene = suite_cls.build_scene(**build_kwargs)
    assert isinstance(scene, Scene)
    assert scene.duration > 0.0
    assert scene.width > 0
    assert scene.height > 0

    # Verify frame rendering
    frame = scene.render_frame(0.5)
    assert isinstance(frame, np.ndarray)
    assert frame.shape == (scene.height, scene.width, 4)

    # Verify storyboard generation
    sb = scene.storyboard(rows=1, cols=3)
    assert sb is not None


def test_turnkey_templates_god_import():
    """Confirms all 5 turnkey template suites and base templates are directly exposed in motio.agent_api."""
    import motio.agent_api as ma

    expected_symbols = [
        "TmplAiCodeAssistantSuite",
        "AiCodeAssistantTemplate",
        "TmplFintechCryptoCardSuite",
        "FintechCryptoCardTemplate",
        "TmplDeveloperCliLaunchSuite",
        "DeveloperCliLaunchTemplate",
        "TmplSaasYcPitchSuite",
        "SaasYcPitchTemplate",
        "TmplSocialAudiogramSuite",
        "SocialAudiogramTemplate",
    ]

    for sym in expected_symbols:
        assert hasattr(ma, sym), f"{sym} must be present in motio.agent_api"
        assert sym in ma.__all__, f"{sym} must be in motio.agent_api.__all__"
