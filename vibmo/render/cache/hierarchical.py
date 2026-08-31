import time
import hashlib
import numpy as np
from typing import Dict, Optional
from enum import Enum

class CacheTier(Enum):
    TIER1_SOURCE_FUSION = 1  # Pre-grade / Generative Backgrounds & FX
    TIER2_NODE_GRAPH = 2     # Per-node expensive filters (Denoise, Bloom)
    TIER3_SEQUENCE = 3       # Timeline transitions, composite blends

class HierarchicalRenderCache:
    """Three independently managed media caches for high-speed playback & rendering."""
    
    def __init__(self, scratch_dir: str):
        self.scratch_dir = scratch_dir
        self._source_cache: Dict[str, np.ndarray] = {}
        self._node_cache: Dict[str, np.ndarray] = {}
        self._sequence_cache: Dict[str, np.ndarray] = {}
        self._dirty_frames: set = set()
        self._last_user_activity = time.time()

    def invalidate_node(self, node_id: str, downstream: bool = True):
        """Flushes only the modified node and downstream stages; upstream nodes stay cached."""
        keys_to_del = [k for k in self._node_cache if k.startswith(node_id)]
        for k in keys_to_del:
            del self._node_cache[k]
        if downstream:
            self._sequence_cache.clear()

    def get_or_render(self, tier: CacheTier, cache_key: str, render_fn):
        cache_store = {
            CacheTier.TIER1_SOURCE_FUSION: self._source_cache,
            CacheTier.TIER2_NODE_GRAPH: self._node_cache,
            CacheTier.TIER3_SEQUENCE: self._sequence_cache,
        }[tier]
        
        if cache_key in cache_store:
            return cache_store[cache_key]
            
        # Compute and store
        frame_buffer = render_fn()
        cache_store[cache_key] = frame_buffer
        return frame_buffer
