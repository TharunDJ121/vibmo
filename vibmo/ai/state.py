"""
State definitions for the LangGraph Motion Graphics Engine.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Sequence, TypedDict, Union


class MotionGraphState(TypedDict, total=False):
    """The central state dictionary passed across LangGraph nodes."""
    prompt: str
    current_code: str
    provider: Optional[str]
    intent: str  # 'surgical_scene_edit' | 'new_story_generation' | 'timing_tweak' | 'style_tweak'
    target_scene_idx: Optional[int]
    target_node_name: Optional[str]
    operations: List[Dict[str, Any]]
    updated_code: str
    storyboard_path: Optional[str]
    validation_errors: List[str]
    is_valid: bool
    iteration: int
    execution_log: List[str]
    response_message: str
