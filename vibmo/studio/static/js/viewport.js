/**
 * Viewport Canvas & Pro Transform Gizmo (8-Way Scale Handles, Rotation Stalk & Live Direct Canvas Manipulation).
 */

class StudioViewport {
    constructor() {
        this.renderCanvas = document.getElementById("renderCanvas");
        this.overlayCanvas = document.getElementById("overlayCanvas");
        this.overlayCtx = this.overlayCanvas.getContext("2d");

        this.dragMode = null; // 'translate', 'scale', 'rotate'
        this.activeHandle = null;
        this.dragStartX = 0;
        this.dragStartY = 0;
        this.nodeInitialX = 0;
        this.nodeInitialY = 0;
        this.nodeInitialScaleX = 1.0;
        this.nodeInitialScaleY = 1.0;
        this.nodeInitialRot = 0.0;

        this.setupInteractions();
    }

    syncSize() {
        if (this.renderCanvas.clientWidth > 0 && this.renderCanvas.clientHeight > 0) {
            this.overlayCanvas.width = this.renderCanvas.clientWidth;
            this.overlayCanvas.height = this.renderCanvas.clientHeight;
        }
    }

    getGizmoBounds(selNode) {
        const scaleX = this.overlayCanvas.width / window.store.sceneWidth;
        const scaleY = this.overlayCanvas.height / window.store.sceneHeight;

        const bx = (selNode.bounds_x !== undefined ? selNode.bounds_x : selNode.x) * scaleX;
        const by = (selNode.bounds_y !== undefined ? selNode.bounds_y : selNode.y) * scaleY;
        const bw = Math.max(32, (selNode.width || 140) * scaleX);
        const bh = Math.max(24, (selNode.height || 80) * scaleY);
        return { bx, by, bw, bh };
    }

    drawGizmo() {
        this.overlayCtx.clearRect(0, 0, this.overlayCanvas.width, this.overlayCanvas.height);
        const selNode = window.store.getSelectedNode();
        if (!selNode) return;

        const { bx, by, bw, bh } = this.getGizmoBounds(selNode);

        this.overlayCtx.save();

        // 1. Selection Bounding Box Outline
        this.overlayCtx.strokeStyle = "#38bdf8";
        this.overlayCtx.lineWidth = 1.5;
        this.overlayCtx.setLineDash([4, 4]);
        this.overlayCtx.strokeRect(bx, by, bw, bh);

        // 2. Rotation Handle Stalk
        const rotX = bx + bw * 0.5;
        const rotY = by - 24;
        this.overlayCtx.beginPath();
        this.overlayCtx.moveTo(bx + bw * 0.5, by);
        this.overlayCtx.lineTo(rotX, rotY);
        this.overlayCtx.strokeStyle = "#6366f1";
        this.overlayCtx.lineWidth = 1.5;
        this.overlayCtx.setLineDash([]);
        this.overlayCtx.stroke();

        // Rotation Handle Circle
        this.overlayCtx.beginPath();
        this.overlayCtx.arc(rotX, rotY, 5, 0, Math.PI * 2);
        this.overlayCtx.fillStyle = "#6366f1";
        this.overlayCtx.fill();
        this.overlayCtx.strokeStyle = "#ffffff";
        this.overlayCtx.lineWidth = 1.5;
        this.overlayCtx.stroke();

        // 3. 8 Scale Handles
        const handles = [
            { x: bx, y: by, name: "nw" },
            { x: bx + bw * 0.5, y: by, name: "n" },
            { x: bx + bw, y: by, name: "ne" },
            { x: bx + bw, y: by + bh * 0.5, name: "e" },
            { x: bx + bw, y: by + bh, name: "se" },
            { x: bx + bw * 0.5, y: by + bh, name: "s" },
            { x: bx, y: by + bh, name: "sw" },
            { x: bx, y: by + bh * 0.5, name: "w" },
        ];

        this.overlayCtx.fillStyle = "#ffffff";
        this.overlayCtx.strokeStyle = "#0284c7";
        this.overlayCtx.lineWidth = 1;
        const hs = 7;
        for (const h of handles) {
            this.overlayCtx.fillRect(h.x - hs / 2, h.y - hs / 2, hs, hs);
            this.overlayCtx.strokeRect(h.x - hs / 2, h.y - hs / 2, hs, hs);
        }

        // 4. Center Anchor Crosshair
        const cx = bx + bw * 0.5;
        const cy = by + bh * 0.5;
        this.overlayCtx.beginPath();
        this.overlayCtx.arc(cx, cy, 3, 0, Math.PI * 2);
        this.overlayCtx.fillStyle = "#38bdf8";
        this.overlayCtx.fill();

        // 5. Transform HUD Tooltip (if dragging)
        if (this.dragMode) {
            const label = `X: ${Math.round(selNode.x)} Y: ${Math.round(selNode.y)} | Rot: ${(selNode.rotation || 0).toFixed(1)}°`;
            this.overlayCtx.font = "11px Inter, sans-serif";
            const tw = this.overlayCtx.measureText(label).width;
            this.overlayCtx.fillStyle = "rgba(15, 23, 42, 0.85)";
            this.overlayCtx.fillRect(bx, by - 44, tw + 16, 20);
            this.overlayCtx.fillStyle = "#f8fafc";
            this.overlayCtx.fillText(label, bx + 8, by - 30);
        }

        this.overlayCtx.restore();
    }

    setupInteractions() {
        this.overlayCanvas.onpointerdown = (e) => {
            const rect = this.overlayCanvas.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;

            const scaleX = this.overlayCanvas.width / window.store.sceneWidth;
            const scaleY = this.overlayCanvas.height / window.store.sceneHeight;
            const sceneMouseX = (mouseX / this.overlayCanvas.width) * window.store.sceneWidth;
            const sceneMouseY = (mouseY / this.overlayCanvas.height) * window.store.sceneHeight;

            const selNode = window.store.getSelectedNode();

            // Check if clicking rotation handle or scale handles of selected node
            if (selNode) {
                const { bx, by, bw, bh } = this.getGizmoBounds(selNode);
                const rotX = bx + bw * 0.5;
                const rotY = by - 24;

                // Rotation handle hit
                if (Math.hypot(mouseX - rotX, mouseY - rotY) <= 8) {
                    this.dragMode = "rotate";
                    this.dragStartX = mouseX;
                    this.dragStartY = mouseY;
                    this.nodeInitialRot = selNode.rotation || 0.0;
                    this.overlayCanvas.setPointerCapture(e.pointerId);
                    return;
                }

                // Check scale handles
                const hs = 8;
                const handles = [
                    { x: bx, y: by, name: "nw" },
                    { x: bx + bw, y: by, name: "ne" },
                    { x: bx + bw, y: by + bh, name: "se" },
                    { x: bx, y: by + bh, name: "sw" },
                ];
                for (const h of handles) {
                    if (Math.abs(mouseX - h.x) <= hs && Math.abs(mouseY - h.y) <= hs) {
                        this.dragMode = "scale";
                        this.activeHandle = h.name;
                        this.dragStartX = mouseX;
                        this.dragStartY = mouseY;
                        this.nodeInitialScaleX = selNode.scale_x || 1.0;
                        this.nodeInitialScaleY = selNode.scale_y || 1.0;
                        this.overlayCanvas.setPointerCapture(e.pointerId);
                        return;
                    }
                }
            }

            // Hit test nodes in reverse z-order
            let hitNode = null;
            for (let i = window.store.nodes.length - 1; i >= 0; i--) {
                const n = window.store.nodes[i];
                const nx = (n.bounds_x !== undefined ? n.bounds_x : n.x) || 0;
                const ny = (n.bounds_y !== undefined ? n.bounds_y : n.y) || 0;
                const nw = n.width || 200;
                const nh = n.height || 100;
                if (sceneMouseX >= nx && sceneMouseX <= nx + nw && sceneMouseY >= ny && sceneMouseY <= ny + nh) {
                    hitNode = n;
                    break;
                }
            }

            if (hitNode) {
                window.store.setSelectedNode(hitNode.id);
                this.dragMode = "translate";
                this.dragStartX = e.clientX;
                this.dragStartY = e.clientY;
                this.nodeInitialX = hitNode.x || 0;
                this.nodeInitialY = hitNode.y || 0;
                this.overlayCanvas.setPointerCapture(e.pointerId);
                this.drawGizmo();
            }
        };

        this.overlayCanvas.onpointermove = (e) => {
            if (!this.dragMode) return;
            const selNode = window.store.getSelectedNode();
            if (!selNode) return;

            const scaleX = this.overlayCanvas.width / window.store.sceneWidth;
            const scaleY = this.overlayCanvas.height / window.store.sceneHeight;

            if (this.dragMode === "translate") {
                const deltaX = (e.clientX - this.dragStartX) / scaleX;
                const deltaY = (e.clientY - this.dragStartY) / scaleY;

                const newX = Math.round(this.nodeInitialX + deltaX);
                const newY = Math.round(this.nodeInitialY + deltaY);

                selNode.x = newX;
                selNode.y = newY;

                window.socket.send({ type: "set_node_prop", node_id: selNode.id, prop: "position_x", value: newX });
                window.socket.send({ type: "set_node_prop", node_id: selNode.id, prop: "position_y", value: newY });
            } else if (this.dragMode === "rotate") {
                const rect = this.overlayCanvas.getBoundingClientRect();
                const mouseX = e.clientX - rect.left;
                const mouseY = e.clientY - rect.top;
                const { bx, by, bw, bh } = this.getGizmoBounds(selNode);
                const cx = bx + bw * 0.5;
                const cy = by + bh * 0.5;

                const angleRad = Math.atan2(mouseY - cy, mouseX - cx) + Math.PI * 0.5;
                const angleDeg = Math.round((angleRad * 180) / Math.PI);
                selNode.rotation = angleDeg;

                window.socket.send({ type: "set_node_prop", node_id: selNode.id, prop: "rotation", value: angleDeg });
            }

            this.drawGizmo();
            window.seekTo(window.store.currentTime);
        };

        this.overlayCanvas.onpointerup = (e) => {
            this.dragMode = null;
            this.activeHandle = null;
            try { this.overlayCanvas.releasePointerCapture(e.pointerId); } catch (_) {}
            this.drawGizmo();
        };
    }
}

window.StudioViewport = StudioViewport;
