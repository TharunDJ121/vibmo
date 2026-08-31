"""
High-level pre-built motion components (GlassCard, MetricCounter, CodeWindow, NotificationToast).
"""

from vibmo.components.glass import GlassCard
from vibmo.components.counter import MetricCounter
from vibmo.components.code import CodeWindow
from vibmo.components.toast import NotificationToast
from vibmo.components.code_stream import SyntaxHighlightCode
from vibmo.components.terminal_session import TerminalWindow, TerminalStep
from vibmo.components.code_card import CodeCard
from vibmo.components.diagram_node import DiagramNode, DiagramBox, DiagramConnection
from vibmo.product.mockups import BrowserWindow
from vibmo.product.cursor import Cursor, ClickIndicator
from vibmo.product.callouts import Spotlight, Callout, Tooltip

__all__ = [
    "GlassCard",
    "MetricCounter",
    "CodeWindow",
    "NotificationToast",
    "SyntaxHighlightCode",
    "TerminalWindow",
    "TerminalStep",
    "CodeCard",
    "DiagramNode",
    "DiagramBox",
    "DiagramConnection",
    "BrowserWindow",
    "Cursor",
    "ClickIndicator",
    "Spotlight",
    "Callout",
    "Tooltip",
]

