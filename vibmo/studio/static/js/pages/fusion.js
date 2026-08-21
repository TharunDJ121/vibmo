/**
 * DaVinci Fusion Node-Based Compositing Canvas (Nodes, Sockets, and Bezier Cables).
 */

class FusionPage {
    constructor() {
        this.nodeContainer = document.getElementById("fusionNodeContainer");
        this.svgWires = document.getElementById("fusionSvgWires");
        this.nodesData = [];
        this.connectionsData = [];
    }

    async loadGraph() {
        try {
            const res = await fetch("/api/fusion");
            const data = await res.json();
            this.nodesData = data.nodes || [];
            this.connectionsData = data.connections || [];
            this.render();
        } catch (_) {}
    }

    render() {
        if (!this.nodeContainer || !this.svgWires) return;
        this.nodeContainer.innerHTML = "";
        this.svgWires.innerHTML = "";

        // 1. Render Nodes
        this.nodesData.forEach(n => {
            const el = document.createElement("div");
            el.className = "f-node";
            el.id = `f_${n.id}`;
            el.style.left = `${n.x}px`;
            el.style.top = `${n.y}px`;

            el.innerHTML = `
                <div class="f-node-header ${n.category}">
                    <span>${n.title}</span>
                    <span style="font-size:9px; opacity:0.6;">${n.category.toUpperCase()}</span>
                </div>
                <div class="f-node-body">
                    ${n.type || n.category}
                </div>
                <div class="f-node-sockets">
                    <div class="f-socket input"></div>
                    <div class="f-socket output"></div>
                </div>
            `;

            // Simple drag
            let isDragging = false;
            let sx = 0, sy = 0;
            el.onpointerdown = (e) => {
                isDragging = true;
                sx = e.clientX - n.x;
                sy = e.clientY - n.y;
                el.setPointerCapture(e.pointerId);
            };
            el.onpointermove = (e) => {
                if (!isDragging) return;
                n.x = e.clientX - sx;
                n.y = e.clientY - sy;
                el.style.left = `${n.x}px`;
                el.style.top = `${n.y}px`;
                this.drawWires();
            };
            el.onpointerup = (e) => {
                isDragging = false;
                try { el.releasePointerCapture(e.pointerId); } catch(_) {}
            };

            this.nodeContainer.appendChild(el);
        });

        this.drawWires();
    }

    drawWires() {
        if (!this.svgWires) return;
        let pathsHtml = "";

        this.connectionsData.forEach(conn => {
            const fromNode = this.nodesData.find(n => n.id === conn.from);
            const toNode = this.nodesData.find(n => n.id === conn.to);
            if (!fromNode || !toNode) return;

            const x1 = fromNode.x + 170;
            const y1 = fromNode.y + 70;
            const x2 = toNode.x + 10;
            const y2 = toNode.y + 70;

            const dx = Math.max(40, (x2 - x1) * 0.5);
            const d = `M ${x1} ${y1} C ${x1 + dx} ${y1}, ${x2 - dx} ${y2}, ${x2} ${y2}`;

            pathsHtml += `<path d="${d}" fill="none" stroke="#6366f1" stroke-width="2.5" stroke-linecap="round" />`;
        });

        this.svgWires.innerHTML = pathsHtml;
    }
}

window.FusionPage = FusionPage;
