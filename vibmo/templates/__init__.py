"""
Turnkey Production Scene Builders and Project Starter Templates.
"""

from vibmo.templates.catalog import TEMPLATES, TEMPLATES as TEMPLATES_CATALOG
from vibmo.templates.turnkey import (
    create_saas_launch_scene,
    TmplSocialAudiogramSuite,
    SocialAudiogramTemplate,
    TmplDeveloperCliLaunchSuite,
    DeveloperCliLaunchTemplate,
    TmplAiCodeAssistantSuite,
    AiCodeAssistantTemplate,
    TmplFintechCryptoCardSuite,
    FintechCryptoCardTemplate,
    TmplSaasYcPitchSuite,
    SaasYcPitchTemplate,
)
from vibmo.templates.library import SceneTemplateLibrary

__all__ = [
    "TEMPLATES",
    "TEMPLATES_CATALOG",
    "create_saas_launch_scene",
    "SceneTemplateLibrary",
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
