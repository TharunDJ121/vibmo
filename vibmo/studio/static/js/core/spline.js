/**
 * Visual Bézier Spline Curve Graph Editor for Vibmo Web Studio Pro.
 * Provides interactive cubic bezier handle editing, preset easing curves, and live code export.
 */

class SplineEditor {
    constructor() {
        this.p1 = { x: 0.25, y: 0.1 };
        this.p2 = { x: 0.25, y: 1.0 };
        this.activeHandle = null;
        this.currentNodeId = null;

        this._createModalDOM();
        this._setupEvents();
    }

    _createModalDOM() {
        const overlay = document.createElement("div");
        overlay.className = "spline-modal-overlay";
        overlay.id = "splineModalOverlay";
        overlay.innerHTML = `
            <div class="spline-card">
                <div class="spline-header">
                    <div style="display:flex; align-items:center; gap:8px;">
                        <span style="font-size:16px;">📈</span>
                        <span style="font-weight:700; font-size:14px;">Bézier Spline Curve Editor</span>
                    </div>
                    <button class="btn-icon" id="closeSplineBtn">✕</button>
                </div>
                <div class="spline-canvas-area">
                    <canvas id="splineCanvas" width="360" height="240"></canvas>
                    <div style="margin-top:12px; font-family:var(--font-mono); font-size:12px; color:var(--accent-cyan);" id="splineFormulaText">
                        Ease.bezier(0.25, 0.10, 0.25, 1.00)
                    </div>
                </div>
                <div class="spline-presets-row">
                    <button class="preset-chip" data-p1="0.16,1" data-p2="0.3,1">Out Expo</button>
                    <button class="preset-chip" data-p1="0.33,1" data-p2="0.68,1">Out Cubic</button>
                    <button class="preset-chip" data-p1="0.65,0" data-p2="0.35,1">In-Out Cubic</button>
                    <button class="preset-chip" data-p1="0.68,-0.6" data-p2="0.32,1.6">In-Out Back</button>
                    <button class="preset-chip" data-p1="0.34,1.56" data-p2="0.64,1">Spring Overshoot</button>
                    <button class="preset-chip" data-p1="0,0" data-p2="1,1">Linear</button>
                </div>
            </div>
        `;
        document.body.appendChild(overlay);

        this.overlay = overlay;
        this.canvas = document.getElementById("splineCanvas");
        this.ctx = this.canvas.getContext("2d");
        this.formulaText = document.getElementById("splineFormulaText");

        document.getElementById("closeSplineBtn").onclick = () => this.close();
        overlay.onclick = (e) => {
            if (e.target === overlay) this.close();
        };

        overlay.querySelectorAll(".preset-chip").forEach(chip => {
            chip.onclick = () => {
                const [x1, y1] = chip.getAttribute("data-p1").split(",").map(Number);
                const [x2, y2] = chip.getAttribute("data-p2").split(",").map(Number);
                this.p1 = { x: x1, y: y1 };
                this.p2 = { x: x2, y: y2 };
                this.draw();
            };
        });
    }

    _setupEvents() {
        const cvs = this.canvas;
        const toCanvasCoords = (e) => {
            const rect = cvs.getBoundingClientRect();
            return {
                x: e.clientX - rect.left,
                y: e.clientY - rect.top,
            };
        };

        const pad = 40;
        const gw = cvs.width - pad * 2;
        const gh = cvs.height - pad * 2;

        const valToPt = (p) => ({
            x: pad + p.x * gw,
            y: cvs.height - (pad + p.y * gh),
        });

        const ptToVal = (pt) => ({
            x: Math.max(0, Math.min(1, (pt.x - pad) / gw)),
            y: (cvs.height - pad - pt.y) / gh,
        });

        cvs.onmousedown = (e) => {
            const pt = toCanvasCoords(e);
            const pt1 = valToPt(this.p1);
            const pt2 = valToPt(this.p2);

            const d1 = Math.hypot(pt.x - pt1.x, pt.y - pt1.y);
            const d2 = Math.hypot(pt.x - pt2.x, pt.y - pt2.y);

            if (d1 < 14) this.activeHandle = "p1";
            else if (d2 < 14) this.activeHandle = "p2";
            else this.activeHandle = null;
        };

        window.addEventListener("mousemove", (e) => {
            if (!this.activeHandle) return;
            const pt = toCanvasCoords(e);
            const val = ptToVal(pt);

            if (this.activeHandle === "p1") this.p1 = val;
            else if (this.activeHandle === "p2") this.p2 = val;

            this.draw();
        });

        window.addEventListener("mouseup", () => {
            if (this.activeHandle && window.historyStack) {
                window.historyStack.record();
            }
            this.activeHandle = null;
        });
    }

    open(nodeId = null) {
        this.currentNodeId = nodeId;
        this.overlay.classList.add("open");
        this.draw();
    }

    close() {
        this.overlay.classList.remove("open");
    }

    draw() {
        const cvs = this.canvas;
        const ctx = this.ctx;
        ctx.clearRect(0, 0, cvs.width, cvs.height);

        const pad = 40;
        const gw = cvs.width - pad * 2;
        const gh = cvs.height - pad * 2;

        const valToPt = (p) => ({
            x: pad + p.x * gw,
            y: cvs.height - (pad + p.y * gh),
        });

        const p0 = valToPt({ x: 0, y: 0 });
        const p3 = valToPt({ x: 1, y: 1 });
        const p1 = valToPt(this.p1);
        const p2 = valToPt(this.p2);

        // 1. Grid Background
        ctx.strokeStyle = "rgba(30, 41, 59, 0.6)";
        ctx.lineWidth = 1;
        ctx.strokeRect(pad, pad, gw, gh);

        // 2. Diagonal Reference Line
        ctx.strokeStyle = "rgba(255, 255, 255, 0.1)";
        ctx.setLineDash([4, 4]);
        ctx.beginPath();
        ctx.moveTo(p0.x, p0.y);
        ctx.line_to ? ctx.line_to(p3.x, p3.y) : ctx.lineTo(p3.x, p3.y);
        ctx.stroke();
        ctx.setLineDash([]);

        // 3. Tangent Control Arms
        ctx.strokeStyle = "rgba(99, 102, 241, 0.6)";
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(p0.x, p0.y);
        ctx.lineTo(p1.x, p1.y);
        ctx.moveTo(p3.x, p3.y);
        ctx.lineTo(p2.x, p2.y);
        ctx.stroke();

        // 4. Cubic Bézier Curve
        ctx.strokeStyle = "#38bdf8";
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(p0.x, p0.y);
        ctx.bezierCurveTo(p1.x, p1.y, p2.x, p2.y, p3.x, p3.y);
        ctx.stroke();

        // 5. Tangent Handle Knobs
        const drawHandle = (pt, label, color) => {
            ctx.fillStyle = color;
            ctx.beginPath();
            ctx.arc(pt.x, pt.y, 6, 0, Math.PI * 2);
            ctx.fill();
            ctx.strokeStyle = "#ffffff";
            ctx.lineWidth = 1.5;
            ctx.stroke();
        };

        drawHandle(p1, "P1", "#6366f1");
        drawHandle(p2, "P2", "#ec4899");

        // Update formula text
        const code = `Ease.bezier(${this.p1.x.toFixed(2)}, ${this.p1.y.toFixed(2)}, ${this.p2.x.toFixed(2)}, ${this.p2.y.toFixed(2)})`;
        if (this.formulaText) {
            this.formulaText.innerText = code;
        }
    }
}

window.SplineEditor = SplineEditor;
window.splineEditor = new SplineEditor();
