"""
Conversation Memory & Multi-turn Session Context for Vibmo AI Director.
Maintains history of prompts, code revisions, and agent suggestions.
"""

from __future__ import annotations
import time
from typing import Any, Dict, List, Optional


class ConversationTurn:
    def __init__(
        self,
        role: str,
        content: str,
        code: Optional[str] = None,
        changes: Optional[List[str]] = None,
        timestamp: Optional[float] = None,
    ) -> None:
        self.role = role  # "user" | "assistant" | "system"
        self.content = content
        self.code = code
        self.changes = changes or []
        self.timestamp = timestamp or time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "code": self.code,
            "changes": self.changes,
            "timestamp": self.timestamp,
        }


class ConversationMemory:
    """
    Stateful memory manager for multi-turn studio and CLI interactions.
    """

    def __init__(self, max_turns: int = 30) -> None:
        self.max_turns = max_turns
        self.turns: List[ConversationTurn] = []
        self.current_code: str = ""

    def add_user_turn(self, prompt: str) -> ConversationTurn:
        turn = ConversationTurn(role="user", content=prompt)
        self.turns.append(turn)
        self._trim()
        return turn

    def add_assistant_turn(
        self,
        message: str,
        code: Optional[str] = None,
        changes: Optional[List[str]] = None,
    ) -> ConversationTurn:
        if code:
            self.current_code = code
        turn = ConversationTurn(
            role="assistant",
            content=message,
            code=code,
            changes=changes,
        )
        self.turns.append(turn)
        self._trim()
        return turn

    def get_history_summary(self) -> str:
        """Formats conversation history into structured context for LLM prompts."""
        if not self.turns:
            return ""

        summary_lines = ["### Prior Conversation Context:"]
        for turn in self.turns[-6:]:  # last 6 turns
            prefix = "User" if turn.role == "user" else "AI Director"
            summary_lines.append(f"- **{prefix}**: {turn.content}")
            if turn.changes:
                for ch in turn.changes:
                    summary_lines.append(f"    * {ch}")

        return "\n".join(summary_lines)

    def to_list(self) -> List[Dict[str, Any]]:
        return [t.to_dict() for t in self.turns]

    def clear(self) -> None:
        self.turns.clear()
        self.current_code = ""

    def _trim(self) -> None:
        if len(self.turns) > self.max_turns:
            self.turns = self.turns[-self.max_turns:]


# Global singleton instance for studio session
_global_memory = ConversationMemory()


def get_global_memory() -> ConversationMemory:
    return _global_memory
