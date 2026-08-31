/**
 * Motion / Edit Page Controller: NLE Multi-Track Timeline, Keyframes, Spline Graph & Audio Ribbon.
 */

class MotionPage {
    constructor() {
        this.timelineRuler = document.getElementById("timelineRuler");
        this.playheadNeedle = document.getElementById("playheadNeedle");
        this.macroTimelineBar = document.getElementById("macroTimelineBar");
        this.macroRuler = document.getElementById("macroRuler");
        this.macroPlayhead = document.getElementById("macroPlayhead");
        this.tracksStack = document.getElementById("tracksStack");
        this.layersList = document.getElementById("layersList");
        this.timecodeDisplay = document.getElementById("timecodeDisplay");
        this.snappingEnabled = true;
        this.waveformPeaks = [];
        this.activeKeyframes = {}; // node_id -> [times]

        this.loadWaveform();
        this._setupRulerClick();
        this._setupMacroTimelineClick();
    }

    _setupMacroTimelineClick() {
        if (!this.macroTimelineBar) return;
        const handleMacroScrub = (e) => {
            const rect = this.macroTimelineBar.getBoundingClientRect();
            const ratio = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
            const dur = window.store.duration || 5.0;
            let t = ratio * dur;
            if (this.snappingEnabled) {
                t = this.snapTime(t);
            }
            window.seekTo(t);
        };

        let isDraggingMacro = false;
        this.macroTimelineBar.addEventListener("mousedown", (e) => {
            isDraggingMacro = true;
            handleMacroScrub(e);
            const onMove = (ev) => { if (isDraggingMacro) handleMacroScrub(ev); };
            const onUp = () => {
                isDraggingMacro = false;
                window.removeEventListener("mousemove", onMove);
                window.removeEventListener("mouseup", onUp);
            };
            window.addEventListener("mousemove", onMove);
            window.addEventListener("mouseup", onUp);
        });
    }

    _setupRulerClick() {
        if (!this.timelineRuler) return;
        this.timelineRuler.onclick = (e) => {
            const rect = this.timelineRuler.getBoundingClientRect();
            const ratio = (e.clientX - rect.left) / rect.width;
            let t = Math.max(0, Math.min(window.store.duration, ratio * window.store.duration));
            if (this.snappingEnabled) {
                t = this.snapTime(t);
            }
            window.seekTo(t);
        };
    }

    snapTime(t, tolerance = 0.08) {
        const dur = window.store.duration || 5.0;
        const snapTargets = [0.0, dur];

        // Add 1s grid marks
        for (let s = 1.0; s < dur; s += 1.0) snapTargets.push(s);

        // Add node in/out points & keyframes
        window.store.nodes.forEach(n => {
            if (n.in_point !== null) snapTargets.push(n.in_point);
            if (n.out_point !== null) snapTargets.push(n.out_point);
            const kfs = this.activeKeyframes[n.id] || [0.0, 0.8];
            kfs.forEach(k => snapTargets.push(k));
        });

        for (const target of snapTargets) {
            if (Math.abs(t - target) <= tolerance) {
                return target;
            }
        }
        return t;
    }

    async loadWaveform() {
        try {
            const res = await fetch("/api/waveform");
            const data = await res.json();
            this.waveformPeaks = data.peaks || [];
            this.renderTracks();
        } catch (_) {}
    }

    renderLayers() {
        if (!this.layersList) return;
        this.layersList.innerHTML = "";
        window.store.nodes.forEach(n => {
            const item = document.createElement("div");
            item.className = "layer-item" + (window.store.selectedNodeId === n.id ? " selected" : "");
            item.innerHTML = `
                <span style="opacity:0.7">📦</span>
                <span style="flex:1;">${n.name}</span>
                <button class="btn-icon" style="padding:2px 6px; font-size:10px;" title="Edit Spline Curve" onclick="event.stopPropagation(); window.splineEditor.open('${n.id}')">📈</button>
            `;
            item.onclick = () => window.store.setSelectedNode(n.id);
            this.layersList.appendChild(item);
        });
    }

    renderRuler() {
        if (this.timelineRuler) {
            this.timelineRuler.innerHTML = "";
            const dur = window.store.duration || 5.0;
            const totalSec = Math.ceil(dur);
            for (let i = 0; i <= totalSec; i++) {
                const tick = document.createElement("div");
                tick.className = "ruler-second";
                tick.style.left = `${(i / dur) * 100}%`;
                tick.innerText = `${i}s`;
                this.timelineRuler.appendChild(tick);
            }
        }

        if (this.macroRuler) {
            this.macroRuler.innerHTML = "";
            const dur = window.store.duration || 5.0;
            const totalSec = Math.ceil(dur);
            for (let i = 0; i <= totalSec; i++) {
                const mTick = document.createElement("div");
                mTick.className = "macro-tick";
                mTick.style.left = `${(i / dur) * 100}%`;
                mTick.innerText = `${i}s`;
                this.macroRuler.appendChild(mTick);
            }
        }
    }

    renderTracks() {
        if (!this.tracksStack) return;
        this.tracksStack.innerHTML = "";
        const dur = window.store.duration || 5.0;
        const colors = ["cyan", "emerald", "amber", ""];

        // 1. Scene Layer Tracks
        window.store.nodes.forEach((n, idx) => {
            const row = document.createElement("div");
            row.className = "track-row" + (window.store.selectedNodeId === n.id ? " active" : "");

            const inP = n.in_point || 0.0;
            const outP = n.out_point !== null ? n.out_point : dur;
            const startPct = (inP / dur) * 100;
            const widthPct = Math.max(4, ((outP - inP) / dur) * 100);
            const c = colors[idx % colors.length];

            // Default Keyframes for animated layer
            if (!this.activeKeyframes[n.id]) {
                this.activeKeyframes[n.id] = [inP, Math.min(dur, inP + 0.8)];
            }
            const keyframes = this.activeKeyframes[n.id];

            let diamondsHtml = "";
            keyframes.forEach((kfTime, kfIdx) => {
                const kfPct = (kfTime / dur) * 100;
                diamondsHtml += `<div class="keyframe-diamond" data-node="${n.id}" data-idx="${kfIdx}" style="left: ${kfPct}%;" title="Keyframe at ${kfTime.toFixed(2)}s"></div>`;
            });

            row.innerHTML = `
                <div class="track-meta">
                    <span style="font-size:11px; opacity:0.6;">T${idx + 1}</span>
                    <span style="flex:1; overflow:hidden; text-overflow:ellipsis;">${n.name}</span>
                    <button class="btn-icon" style="padding:1px 5px; font-size:10px;" title="Spline Graph" onclick="event.stopPropagation(); window.splineEditor.open('${n.id}')">📈</button>
                </div>
                <div class="track-bar-lane">
                    <div class="track-clip ${c}" style="left: ${startPct}%; width: ${widthPct}%;">
                        ${n.name}
                    </div>
                    ${diamondsHtml}
                </div>
            `;
            row.onclick = () => window.store.setSelectedNode(n.id);
            this.tracksStack.appendChild(row);
        });

        // 2. Audio Master Track with Waveform Peaks
        if (this.waveformPeaks.length > 0) {
            const audioRow = document.createElement("div");
            audioRow.className = "track-row";
            audioRow.innerHTML = `
                <div class="track-meta">
                    <span style="font-size:11px; color:#ec4899;">A1</span>
                    <span>Master Audio</span>
                </div>
                <div class="track-bar-lane">
                    <div class="track-clip audio" style="left: 0%; width: 100%;">
                        <canvas class="audio-waveform-canvas" id="audioWaveformCanvas"></canvas>
                        <span style="position:relative; z-index:2;">🎵 Audio Track</span>
                    </div>
                </div>
            `;
            this.tracksStack.appendChild(audioRow);
            setTimeout(() => this.drawWaveformRibbon(), 20);
        }

        this._setupKeyframeDrag();
    }

    _setupKeyframeDrag() {
        document.querySelectorAll(".keyframe-diamond").forEach(diamond => {
            diamond.onmousedown = (e) => {
                e.stopPropagation();
                const nodeId = diamond.getAttribute("data-node");
                const kfIdx = parseInt(diamond.getAttribute("data-idx"));
                const lane = diamond.parentElement;
                const dur = window.store.duration || 5.0;

                const onMove = (moveEv) => {
                    const rect = lane.getBoundingClientRect();
                    let ratio = (moveEv.clientX - rect.left) / rect.width;
                    let t = Math.max(0, Math.min(dur, ratio * dur));
                    if (this.snappingEnabled) {
                        t = this.snapTime(t);
                    }
                    this.activeKeyframes[nodeId][kfIdx] = t;
                    diamond.style.left = `${(t / dur) * 100}%`;
                    diamond.title = `Keyframe at ${t.toFixed(2)}s`;
                    window.seekTo(t);
                };

                const onUp = () => {
                    window.removeEventListener("mousemove", onMove);
                    window.removeEventListener("mouseup", onUp);
                    if (window.historyStack) window.historyStack.record();
                };

                window.addEventListener("mousemove", onMove);
                window.addEventListener("mouseup", onUp);
            };
        });
    }

    drawWaveformRibbon() {
        const cvs = document.getElementById("audioWaveformCanvas");
        if (!cvs) return;
        cvs.width = cvs.clientWidth || 800;
        cvs.height = cvs.clientHeight || 24;
        const ctx = cvs.getContext("2d");
        ctx.clearRect(0, 0, cvs.width, cvs.height);

        ctx.fillStyle = "rgba(255, 255, 255, 0.6)";
        const step = cvs.width / this.waveformPeaks.length;
        const cy = cvs.height * 0.5;

        this.waveformPeaks.forEach((p, i) => {
            const h = p * cy;
            ctx.fillRect(i * step, cy - h, Math.max(1, step - 0.5), h * 2);
        });
    }

    updatePlayhead(t) {
        const dur = window.store.duration || 5.0;
        const clampedT = Math.max(0, Math.min(dur, t));

        if (this.playheadNeedle) {
            const totalW = (this.tracksStack && this.tracksStack.clientWidth) ? this.tracksStack.clientWidth : 1000;
            const laneWidth = Math.max(100, totalW - 200);
            const px = 200 + (clampedT / dur) * laneWidth;
            this.playheadNeedle.style.left = `${px}px`;
        }

        if (this.macroPlayhead) {
            const macroPct = (clampedT / dur) * 100;
            this.macroPlayhead.style.left = `${macroPct}%`;
        }

        if (this.timecodeDisplay) {
            this.timecodeDisplay.innerText = `${t.toFixed(2)}s / ${dur.toFixed(2)}s`;
        }
    }
}


window.MotionPage = MotionPage;
