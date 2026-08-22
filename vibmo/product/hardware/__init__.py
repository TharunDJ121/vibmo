"""Hardware chassis and device enclosure suites."""
from __future__ import annotations

from vibmo.product.hardware.hw_automotive_cockpit_suite import (
    TeslaCenterTouchscreen,
    CarPlayDashboardPill,
    DigitalGaugeClusterHud,
)
from vibmo.product.hardware.hw_camera_viewfinder_suite import (
    DslrCameraViewfinderHud,
    CinemaCameraCageRig,
    DroneGimbalTelemetryHud,
)
from vibmo.product.hardware.hw_cctv_surveillance_suite import (
    CctvQuadCameraGrid,
    PtzCameraTargetingHud,
    BodyCamRecOverlay,
)
from vibmo.product.hardware.hw_cyberdeck_terminal_suite import (
    CyberdeckMechanicalKeyboard,
    PopUpLcdScreen,
    IndustrialBumperCase,
    PatchCablesAndAntenna,
)
from vibmo.product.hardware.hw_eink_tablet_suite import (
    PaperEInkReaderFrame,
    StylusPenMockup,
    TextureMatteScreenBezel,
)
from vibmo.product.hardware.hw_foldable_device_suite import (
    FoldableBookPhone,
    ClamshellFlipPhone,
    DualScreenBookDevice,
    HingeCreaseIndicator,
)
from vibmo.product.hardware.hw_gaming_handheld_suite import (
    ClippedScreenContainer,
    HandheldBase,
    SteamDeckHandheldChassis,
    SwitchJoyConFrame,
    RetroGameBoyEnclosure,
)
from vibmo.product.hardware.hw_multi_monitor_suite import (
    ScreenContainer,
    DualDeveloperMonitors,
    VerticalSidecarDisplay,
    TripleCurvedSimulatorDeck,
)
from vibmo.product.hardware.hw_pos_retail_suite import (
    NfcHandheldPosTerminal,
    CountertopRegisterScreen,
    ThermalReceiptSlot,
    TapPaymentSensor,
)
from vibmo.product.hardware.hw_smart_home_hub_suite import (
    FabricAcousticSmartHub,
    RoundThermostatDial,
    WallMountSecurityKeypad,
)
from vibmo.product.hardware.hw_smart_tv_display_suite import (
    WallMountedDisplayShadow,
    FloatingTvStand,
    OledSmartTvFrame,
    CurvedCinemaDisplay,
)
from vibmo.product.hardware.hw_smartwatch_rugged_suite import (
    BaseWatch,
    TitaniumRuggedWatch,
    MinimalistSquareWatch,
    ClassicRoundSmartwatchFace,
)
from vibmo.product.hardware.hw_spatial_visor_suite import (
    VisionProSpatialGlassVisor,
    QuestGoggleFrame,
    SpatialHudCurvedProjection,
)
from vibmo.product.hardware.hw_super_ultrawide_suite import (
    MonitorArmPivotingBase,
    GamerBackGlowRgbLed,
    Curved49InchUltrawide,
)
from vibmo.product.hardware.hw_vintage_crt_suite import (
    _VintageNode,
    BeigeCrtMonitor1990s,
    ArcadeCabinetBezel,
    RetroPortableTvAntenna,
)

__all__ = [
    "TeslaCenterTouchscreen",
    "CarPlayDashboardPill",
    "DigitalGaugeClusterHud",
    "DslrCameraViewfinderHud",
    "CinemaCameraCageRig",
    "DroneGimbalTelemetryHud",
    "CctvQuadCameraGrid",
    "PtzCameraTargetingHud",
    "BodyCamRecOverlay",
    "CyberdeckMechanicalKeyboard",
    "PopUpLcdScreen",
    "IndustrialBumperCase",
    "PatchCablesAndAntenna",
    "PaperEInkReaderFrame",
    "StylusPenMockup",
    "TextureMatteScreenBezel",
    "FoldableBookPhone",
    "ClamshellFlipPhone",
    "DualScreenBookDevice",
    "HingeCreaseIndicator",
    "ClippedScreenContainer",
    "HandheldBase",
    "SteamDeckHandheldChassis",
    "SwitchJoyConFrame",
    "RetroGameBoyEnclosure",
    "ScreenContainer",
    "DualDeveloperMonitors",
    "VerticalSidecarDisplay",
    "TripleCurvedSimulatorDeck",
    "NfcHandheldPosTerminal",
    "CountertopRegisterScreen",
    "ThermalReceiptSlot",
    "TapPaymentSensor",
    "FabricAcousticSmartHub",
    "RoundThermostatDial",
    "WallMountSecurityKeypad",
    "WallMountedDisplayShadow",
    "FloatingTvStand",
    "OledSmartTvFrame",
    "CurvedCinemaDisplay",
    "BaseWatch",
    "TitaniumRuggedWatch",
    "MinimalistSquareWatch",
    "ClassicRoundSmartwatchFace",
    "VisionProSpatialGlassVisor",
    "QuestGoggleFrame",
    "SpatialHudCurvedProjection",
    "MonitorArmPivotingBase",
    "GamerBackGlowRgbLed",
    "Curved49InchUltrawide",
    "ArcadeCabinetBezel",
    "RetroPortableTvAntenna",
]

# Semantic Aliases
SuperUltrawideMonitorFrame = Curved49InchUltrawide
FoldableDeviceFrame = FoldableBookPhone
RuggedSmartwatchFrame = TitaniumRuggedWatch
PosTerminalFrame = NfcHandheldPosTerminal
CameraViewfinderOverlay = DslrCameraViewfinderHud
MinimalistEInkTabletFrame = PaperEInkReaderFrame
SmartHomeHubFrame = FabricAcousticSmartHub
RetroArcadeCrtCabinet = ArcadeCabinetBezel
CctvQuadViewOverlay = CctvQuadCameraGrid
SpatialVisorFrame = VisionProSpatialGlassVisor
OledCinemaTvFrame = OledSmartTvFrame
AutomotiveCockpitDash = TeslaCenterTouchscreen
HandheldGamingConsoleFrame = SteamDeckHandheldChassis
CyberdeckChassisFrame = IndustrialBumperCase
MultiMonitorDeveloperRig = DualDeveloperMonitors

__all__.extend([
    "SuperUltrawideMonitorFrame",
    "FoldableDeviceFrame",
    "RuggedSmartwatchFrame",
    "PosTerminalFrame",
    "CameraViewfinderOverlay",
    "MinimalistEInkTabletFrame",
    "SmartHomeHubFrame",
    "RetroArcadeCrtCabinet",
    "CctvQuadViewOverlay",
    "SpatialVisorFrame",
    "OledCinemaTvFrame",
    "AutomotiveCockpitDash",
    "HandheldGamingConsoleFrame",
    "CyberdeckChassisFrame",
    "MultiMonitorDeveloperRig",
])

