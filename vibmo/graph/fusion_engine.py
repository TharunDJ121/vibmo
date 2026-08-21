"""
Vibmo V2 Fusion Node DAG Execution & Image Processing Engine.
Evaluates node graphs in topological order and executes GPU/CPU shaders for VFX, Keying, and Compositing.
"""

from __future__ import annotations
import math
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
from PIL import Image, ImageFilter

from vibmo.graph.schema import FusionGraph, FusionNode, FusionConnection, AnimatableProperty


class FusionExecutionContext:
    """Carries time, resolution, and intermediate node frame buffers during a DAG evaluation pass."""

    def __init__(self, width: int = 1920, height: int = 1080, time: float = 0.0, fps: float = 60.0) -> None:
        self.width = width
        self.height = height
        self.time = time
        self.fps = fps
        self.frame = int(round(time * fps))
        self.buffers: Dict[str, np.ndarray] = {}  # node_id -> RGBA uint8 numpy array (H, W, 4)

    def create_empty_buffer(self) -> np.ndarray:
        return np.zeros((self.height, self.width, 4), dtype=np.uint8)


class FusionDAGExecutor:
    """Topological DAG evaluator for Fusion compositions."""

    @classmethod
    def execute_graph(cls, graph: FusionGraph, ctx: FusionExecutionContext) -> Optional[np.ndarray]:
        """Evaluates the entire node graph and returns the master RGBA buffer from the active output node."""
        if not graph.nodes:
            return None

        # 1. Topological Sort of nodes
        sorted_node_ids = cls._topological_sort(graph)

        # 2. Sequential execution of each node
        for node_id in sorted_node_ids:
            node = graph.nodes.get(node_id)
            if not node or not node.enabled:
                continue

            # Gather input buffers
            input_buffers = cls._gather_inputs(graph, node_id, ctx)
            
            # Execute node logic
            out_buf = cls._execute_node(node, input_buffers, ctx)
            if out_buf is not None:
                ctx.buffers[node_id] = out_buf

        # 3. Return active output node buffer or MediaOut
        output_id = graph.active_output_node
        if output_id and output_id in ctx.buffers:
            return ctx.buffers[output_id]

        # Fallback to last executed node
        if sorted_node_ids and sorted_node_ids[-1] in ctx.buffers:
            return ctx.buffers[sorted_node_ids[-1]]

        return ctx.create_empty_buffer()

    @classmethod
    def _topological_sort(cls, graph: FusionGraph) -> List[str]:
        """Calculates topological execution order from DAG connections."""
        in_degree: Dict[str, int] = {nid: 0 for nid in graph.nodes}
        adj_list: Dict[str, List[str]] = {nid: [] for nid in graph.nodes}

        for conn in graph.connections:
            if conn.from_node in adj_list and conn.to_node in in_degree:
                adj_list[conn.from_node].append(conn.to_node)
                in_degree[conn.to_node] += 1

        queue = [nid for nid, deg in in_degree.items() if deg == 0]
        order = []

        while queue:
            curr = queue.pop(0)
            order.append(curr)
            for neighbor in adj_list.get(curr, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Append any unlinked nodes
        for nid in graph.nodes:
            if nid not in order:
                order.append(nid)

        return order

    @classmethod
    def _gather_inputs(cls, graph: FusionGraph, node_id: str, ctx: FusionExecutionContext) -> Dict[str, np.ndarray]:
        """Finds input buffers connected to this node's sockets."""
        inputs: Dict[str, np.ndarray] = {}
        for conn in graph.connections:
            if conn.to_node == node_id:
                if conn.from_node in ctx.buffers:
                    inputs[conn.to_socket] = ctx.buffers[conn.from_node]
        return inputs

    @classmethod
    def _execute_node(cls, node: FusionNode, inputs: Dict[str, np.ndarray], ctx: FusionExecutionContext) -> np.ndarray:
        """Dispatches node execution to specialized operators."""
        t = node.node_type

        # 1. MediaIn / Passthrough
        if t in ["MediaIn", "MediaOut"]:
            if "input" in inputs:
                return inputs["input"]
            return ctx.create_empty_buffer()

        # 2. Background Generator (Solid / Gradient)
        elif t == "Background":
            return cls._op_background(node, ctx)

        # 3. FastNoise Generator
        elif t == "FastNoise":
            return cls._op_fast_noise(node, ctx)

        # 4. Gaussian Blur
        elif t == "GaussianBlur":
            base = inputs.get("input") if "input" in inputs else ctx.create_empty_buffer()
            return cls._op_gaussian_blur(base, node, ctx)

        # 5. Optical Glow
        elif t == "Glow":
            base = inputs.get("input") if "input" in inputs else ctx.create_empty_buffer()
            return cls._op_glow(base, node, ctx)

        # 6. Color Corrector
        elif t == "ColorCorrector":
            base = inputs.get("input") if "input" in inputs else ctx.create_empty_buffer()
            return cls._op_color_corrector(base, node, ctx)

        # 7. DeltaKeyer (Chroma Key / Green Screen)
        elif t == "DeltaKeyer":
            base = inputs.get("input") if "input" in inputs else ctx.create_empty_buffer()
            return cls._op_delta_keyer(base, node, ctx)

        # 8. Merge (Compositor with Blend Modes)
        elif t == "Merge":
            bg = inputs.get("input", ctx.create_empty_buffer())
            fg = inputs.get("foreground", ctx.create_empty_buffer())
            mask = inputs.get("mask")
            return cls._op_merge(bg, fg, mask, node, ctx)

        # 9. Transform 2D
        elif t == "Transform2D":
            base = inputs.get("input") if "input" in inputs else ctx.create_empty_buffer()
            return cls._op_transform2d(base, node, ctx)

        # Default fallback: return primary input or empty
        return inputs.get("input", ctx.create_empty_buffer())

    # -------------------------------------------------------------------------
    # Node Operators
    # -------------------------------------------------------------------------

    @classmethod
    def _op_background(cls, node: FusionNode, ctx: FusionExecutionContext) -> np.ndarray:
        buf = np.zeros((ctx.height, ctx.width, 4), dtype=np.uint8)
        r = int(node.properties.get("r", AnimatableProperty(name="r", value=15.0)).value)
        g = int(node.properties.get("g", AnimatableProperty(name="g", value=23.0)).value)
        b = int(node.properties.get("b", AnimatableProperty(name="b", value=42.0)).value)
        a = int(node.properties.get("a", AnimatableProperty(name="a", value=255.0)).value)

        buf[:, :, 0] = r
        buf[:, :, 1] = g
        buf[:, :, 2] = b
        buf[:, :, 3] = a
        return buf

    @classmethod
    def _op_fast_noise(cls, node: FusionNode, ctx: FusionExecutionContext) -> np.ndarray:
        scale = float(node.properties.get("scale", AnimatableProperty(name="scale", value=20.0)).value)
        seed = float(node.properties.get("seed", AnimatableProperty(name="seed", value=1.0)).value)

        # Generate animated procedural noise grid
        y, x = np.mgrid[0:ctx.height, 0:ctx.width]
        freq = 1.0 / max(1.0, scale)
        val = np.sin(x * freq + seed + ctx.time * 2.0) * np.cos(y * freq + seed)
        val = ((val + 1.0) * 0.5 * 255.0).astype(np.uint8)

        buf = np.zeros((ctx.height, ctx.width, 4), dtype=np.uint8)
        buf[:, :, 0] = val
        buf[:, :, 1] = val
        buf[:, :, 2] = val
        buf[:, :, 3] = 255
        return buf

    @classmethod
    def _op_gaussian_blur(cls, base: np.ndarray, node: FusionNode, ctx: FusionExecutionContext) -> np.ndarray:
        radius = float(node.properties.get("radius", AnimatableProperty(name="radius", value=10.0)).value)
        if radius <= 0.5:
            return base

        img = Image.fromarray(base)
        blurred = img.filter(ImageFilter.GaussianBlur(radius=radius))
        return np.array(blurred, dtype=np.uint8)

    @classmethod
    def _op_glow(cls, base: np.ndarray, node: FusionNode, ctx: FusionExecutionContext) -> np.ndarray:
        threshold = float(node.properties.get("threshold", AnimatableProperty(name="threshold", value=0.5)).value) * 255.0
        glow_size = float(node.properties.get("size", AnimatableProperty(name="size", value=15.0)).value)

        # High-pass filter above threshold
        luma = (0.299 * base[:, :, 0] + 0.587 * base[:, :, 1] + 0.114 * base[:, :, 2])
        mask = (luma > threshold).astype(np.float32)[:, :, None]

        high_pass = (base.astype(np.float32) * mask).astype(np.uint8)
        img_high = Image.fromarray(high_pass)
        glow_layer = np.array(img_high.filter(ImageFilter.GaussianBlur(radius=glow_size)), dtype=np.float32)

        # Additive blend
        result = base.astype(np.float32) + glow_layer * 1.5
        return np.clip(result, 0, 255).astype(np.uint8)

    @classmethod
    def _op_color_corrector(cls, base: np.ndarray, node: FusionNode, ctx: FusionExecutionContext) -> np.ndarray:
        contrast = float(node.properties.get("contrast", AnimatableProperty(name="contrast", value=1.0)).value)
        sat = float(node.properties.get("saturation", AnimatableProperty(name="saturation", value=1.0)).value)
        gain = float(node.properties.get("gain", AnimatableProperty(name="gain", value=1.0)).value)

        arr = base.astype(np.float32)

        # Gain
        arr[:, :, :3] *= gain

        # Contrast around 128
        arr[:, :, :3] = (arr[:, :, :3] - 128.0) * contrast + 128.0

        # Saturation
        luma = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]
        for c in range(3):
            arr[:, :, c] = luma + (arr[:, :, c] - luma) * sat

        return np.clip(arr, 0, 255).astype(np.uint8)

    @classmethod
    def _op_delta_keyer(cls, base: np.ndarray, node: FusionNode, ctx: FusionExecutionContext) -> np.ndarray:
        """Green Screen / Chroma Keying Despill operator."""
        arr = base.copy().astype(np.float32)
        r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]

        # Excess green metric: max(0, G - max(R, B))
        excess_green = np.maximum(0.0, g - np.maximum(r, b))
        
        # Modulate alpha based on green excess
        alpha = np.clip(1.0 - (excess_green / 50.0), 0.0, 1.0)
        arr[:, :, 3] = (arr[:, :, 3] * alpha)

        # Green Despill
        arr[:, :, 1] = np.minimum(arr[:, :, 1], np.maximum(r, b))

        return np.clip(arr, 0, 255).astype(np.uint8)

    @classmethod
    def _op_merge(
        cls,
        bg: np.ndarray,
        fg: np.ndarray,
        mask: Optional[np.ndarray],
        node: FusionNode,
        ctx: FusionExecutionContext,
    ) -> np.ndarray:
        """Multi-layer alpha compositing with blend mode support."""
        blend = str(node.properties.get("blend", AnimatableProperty(name="blend", value="over")).value).lower()
        opacity = float(node.properties.get("opacity", AnimatableProperty(name="opacity", value=1.0)).value)

        fg_alpha = (fg[:, :, 3].astype(np.float32) / 255.0) * opacity
        if mask is not None:
            mask_luma = (mask[:, :, 0].astype(np.float32) / 255.0)
            fg_alpha *= mask_luma

        fg_a3 = fg_alpha[:, :, None]
        bg_a = bg[:, :, 3].astype(np.float32) / 255.0

        if blend == "add":
            out_rgb = bg[:, :, :3].astype(np.float32) + fg[:, :, :3].astype(np.float32) * fg_a3
        elif blend == "multiply":
            out_rgb = bg[:, :, :3].astype(np.float32) * (fg[:, :, :3].astype(np.float32) / 255.0) * fg_a3 + bg[:, :, :3] * (1.0 - fg_a3)
        elif blend == "screen":
            out_rgb = (255.0 - ((255.0 - bg[:, :, :3]) * (255.0 - fg[:, :, :3])) / 255.0) * fg_a3 + bg[:, :, :3] * (1.0 - fg_a3)
        else:
            # Standard 'over' blend
            out_rgb = fg[:, :, :3].astype(np.float32) * fg_a3 + bg[:, :, :3].astype(np.float32) * (1.0 - fg_a3)

        out_a = np.clip((fg_alpha + bg_a * (1.0 - fg_alpha)) * 255.0, 0, 255)
        
        result = np.zeros_like(bg)
        result[:, :, :3] = np.clip(out_rgb, 0, 255).astype(np.uint8)
        result[:, :, 3] = out_a.astype(np.uint8)
        return result

    @classmethod
    def _op_transform2d(cls, base: np.ndarray, node: FusionNode, ctx: FusionExecutionContext) -> np.ndarray:
        scale = float(node.properties.get("scale", AnimatableProperty(name="scale", value=1.0)).value)
        angle = float(node.properties.get("angle", AnimatableProperty(name="angle", value=0.0)).value)

        if abs(scale - 1.0) < 0.001 and abs(angle) < 0.001:
            return base

        img = Image.fromarray(base)
        if abs(angle) > 0.001:
            img = img.rotate(angle, resample=Image.Resampling.BILINEAR)

        if abs(scale - 1.0) > 0.001:
            w = max(1, int(ctx.width * scale))
            h = max(1, int(ctx.height * scale))
            scaled = img.resize((w, h), resample=Image.Resampling.BILINEAR)
            
            # Paste back to center
            res = Image.new("RGBA", (ctx.width, ctx.height), (0, 0, 0, 0))
            offset_x = (ctx.width - w) // 2
            offset_y = (ctx.height - h) // 2
            res.paste(scaled, (offset_x, offset_y))
            return np.array(res, dtype=np.uint8)

        return np.array(img, dtype=np.uint8)
