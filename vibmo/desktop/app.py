"""
Vibmo Desktop Application Entrypoint.
"""

from __future__ import annotations
import sys
import os
from typing import Optional

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from vibmo.graph.engine import VibmoStateGraph
from vibmo.desktop.main_window import VibmoMainWindow


def launch_desktop_studio(project_path: Optional[str] = None) -> int:
    """Launches the Vibmo Studio Pro Desktop GUI Application."""
    # Enable High-DPI scaling
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    app = QApplication(sys.argv)
    app.setApplicationName("Vibmo Studio Pro")
    app.setOrganizationName("Vibmo")

    state_graph = None
    if project_path and os.path.exists(project_path):
        state_graph = VibmoStateGraph.load_from_file(project_path)
    else:
        state_graph = VibmoStateGraph()

    window = VibmoMainWindow(state_graph=state_graph)
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(launch_desktop_studio())
