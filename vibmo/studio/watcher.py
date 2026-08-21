"""
Live File Watcher & Auto-Reload for Vibmo Web Studio.
"""

from __future__ import annotations
import os
import time
import threading
from typing import Callable, Optional


class ScriptWatcher:
    """
    Watches a target Python script file for modifications and triggers a reload callback.
    """

    def __init__(self, script_path: str, on_change: Callable[[], None], poll_interval: float = 0.5) -> None:
        self.script_path = os.path.abspath(script_path)
        self.on_change = on_change
        self.poll_interval = poll_interval
        self._running = False
        self._last_mtime = self._get_mtime()
        self._thread: Optional[threading.Thread] = None

    def _get_mtime(self) -> float:
        if os.path.exists(self.script_path):
            return os.path.getmtime(self.script_path)
        return 0.0

    def start(self) -> None:
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False

    def _loop(self) -> None:
        while self._running:
            time.sleep(self.poll_interval)
            mtime = self._get_mtime()
            if mtime > self._last_mtime:
                self._last_mtime = mtime
                try:
                    self.on_change()
                except Exception:
                    pass
