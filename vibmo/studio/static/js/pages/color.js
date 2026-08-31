/**
 * Color & Grading Page: Lift / Gamma / Gain Wheels & Real-Time Video Scopes.
 * Inspired by DaVinci Resolve Color Page (Color Wheels & Scopes).
 */

class ColorPage {
    constructor() {
        this.container = document.getElementById("colorControlsContainer");
        this.currentViewMode = "wheels"; // 'wheels' or 'scopes'
        this.scopeType = "parade"; // 'parade' or 'waveform'
        this.grade = {
            lift: [0.0, 0.0, 0.0],
            gamma: [1.0, 1.0, 1.0],
            gain: [1.0, 1.0, 1.0],
            exposure: 0.0,
            contrast: 1.0,
            saturation: 1.0,
            temperature: 0.0,
            tint: 0.0,
        };
    }

    render() {
        if (!this.container) return;
        this.container.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; border-bottom:1px solid #1e293b; padding-bottom:12px;">
                <div style="display:flex; gap:8px;">
                    <button class="btn-icon ${this.currentViewMode === 'wheels' ? 'btn-primary' : ''}" id="btnViewWheels" style="font-size:11px; padding:4px 12px;">🎨 Primary Wheels</button>
                    <button class="btn-icon ${this.currentViewMode === 'scopes' ? 'btn-primary' : ''}" id="btnViewScopes" style="font-size:11px; padding:4px 12px;">📊 Video Scopes</button>
                </div>
                ${this.currentViewMode === 'scopes' ? `
                    <select id="scopeTypeSelect" class="btn-icon" style="background:#111827; cursor:pointer; font-size:11px; padding:4px 8px;">
                        <option value="parade" ${this.scopeType === 'parade' ? 'selected' : ''}>RGB Parade</option>
                        <option value="waveform" ${this.scopeType === 'waveform' ? 'selected' : ''}>Luminance Waveform</option>
                    </select>
                ` : ''}
            </div>

            <div id="colorMainContent"></div>
        `;

        const content = document.getElementById("colorMainContent");
        if (this.currentViewMode === "wheels") {
            this._renderWheels(content);
        } else {
            this._renderScopes(content);
        }

        // View Mode Switchers
        document.getElementById("btnViewWheels").onclick = () => {
            this.currentViewMode = "wheels";
            this.render();
        };
        document.getElementById("btnViewScopes").onclick = () => {
            this.currentViewMode = "scopes";
            this.render();
        };

        const sel = document.getElementById("scopeTypeSelect");
        if (sel) {
            sel.onchange = (e) => {
                this.scopeType = e.target.value;
                this._renderScopes(content);
            };
        }
    }

    _renderWheels(content) {
        content.innerHTML = `
            <div class="color-wheels-container">
                <div class="wheel-card" id="liftCard">
                    <div class="wheel-circle" id="liftWheel"><div class="wheel-handle" id="liftHandle"></div></div>
                    <div class="wheel-title">LIFT (Shadows)</div>
                </div>
                <div class="wheel-card" id="gammaCard">
                    <div class="wheel-circle" id="gammaWheel"><div class="wheel-handle" id="gammaHandle"></div></div>
                    <div class="wheel-title">GAMMA (Midtones)</div>
                </div>
                <div class="wheel-card" id="gainCard">
                    <div class="wheel-circle" id="gainWheel"><div class="wheel-handle" id="gainHandle"></div></div>
                    <div class="wheel-title">GAIN (Highlights)</div>
                </div>
            </div>

            <div class="ctrl-grid-2" style="margin-top:20px;">
                <div class="ctrl-row">
                    <div class="ctrl-label-val"><span>Exposure</span><span id="expVal">${this.grade.exposure.toFixed(2)} EV</span></div>
                    <input id="sliderExp" class="ctrl-slider" type="range" min="-2" max="2" step="0.05" value="${this.grade.exposure}" />
                </div>
                <div class="ctrl-row">
                    <div class="ctrl-label-val"><span>Contrast</span><span id="contrastVal">${this.grade.contrast.toFixed(2)}x</span></div>
                    <input id="sliderContrast" class="ctrl-slider" type="range" min="0.5" max="2.0" step="0.05" value="${this.grade.contrast}" />
                </div>
                <div class="ctrl-row">
                    <div class="ctrl-label-val"><span>Saturation</span><span id="satVal">${this.grade.saturation.toFixed(2)}x</span></div>
                    <input id="sliderSat" class="ctrl-slider" type="range" min="0" max="2.5" step="0.05" value="${this.grade.saturation}" />
                </div>
                <div class="ctrl-row">
                    <div class="ctrl-label-val"><span>Color Temp</span><span id="tempVal">${this.grade.temperature.toFixed(2)}</span></div>
                    <input id="sliderTemp" class="ctrl-slider" type="range" min="-1" max="1" step="0.05" value="${this.grade.temperature}" />
                </div>
            </div>
        `;

        this._setupWheelListeners();
    }

    _renderScopes(content) {
        content.innerHTML = `
            <div style="background:#020617; border:1px solid #1e293b; border-radius:12px; padding:16px; display:flex; flex-direction:column; align-items:center;">
                <div style="display:flex; justify-content:space-between; width:100%; margin-bottom:8px; font-size:11px; color:#94a3b8; font-weight:700; text-transform:uppercase;">
                    <span>${this.scopeType === 'parade' ? 'RGB Parade Scope (0 - 100 IRE)' : 'Luminance Waveform Scope (0 - 100 IRE)'}</span>
                    <span style="color:#38bdf8;">Real-Time Frame Analysis</span>
                </div>
                <canvas id="scopeCanvas" width="680" height="280" style="width:100%; max-width:680px; height:280px; background:#040711; border:1px solid #0f172a; border-radius:8px;"></canvas>
            </div>
        `;
        this.drawScopes();
    }

    drawScopes() {
        const cvs = document.getElementById("scopeCanvas");
        const renderCvs = document.getElementById("renderCanvas");
        if (!cvs || !renderCvs || !renderCvs.complete || renderCvs.naturalWidth === 0) return;

        const ctx = cvs.getContext("2d");
        const W = cvs.width;
        const H = cvs.height;
        ctx.clearRect(0, 0, W, H);

        // Draw Graticule Lines (0%, 25%, 50%, 75%, 100% IRE)
        ctx.strokeStyle = "rgba(148, 163, 184, 0.15)";
        ctx.lineWidth = 1;
        ctx.font = "9px monospace";
        ctx.fillStyle = "rgba(148, 163, 184, 0.4)";
        for (let ire = 0; ire <= 100; ire += 25) {
            const y = H - (ire / 100.0) * (H - 20) - 10;
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(W, y);
            ctx.stroke();
            ctx.fillText(`${ire}%`, 6, y - 2);
        }

        // Downsample image for high-speed scope analysis
        const sampleCanvas = document.createElement("canvas");
        const sW = 160;
        const sH = 90;
        sampleCanvas.width = sW;
        sampleCanvas.height = sH;
        const sCtx = sampleCanvas.getContext("2d");
        try {
            sCtx.drawImage(renderCvs, 0, 0, sW, sH);
            const imgData = sCtx.getImageData(0, 0, sW, sH).data;

            if (this.scopeType === "parade") {
                // 3 Partitions: Red, Green, Blue
                const colW = (W - 20) / 3;
                for (let x = 0; x < sW; x++) {
                    for (let y = 0; y < sH; y++) {
                        const idx = (y * sW + x) * 4;
                        const r = imgData[idx] / 255.0;
                        const g = imgData[idx + 1] / 255.0;
                        const b = imgData[idx + 2] / 255.0;

                        const px = (x / sW) * colW;
                        
                        // Red Channel
                        ctx.fillStyle = "rgba(239, 68, 68, 0.4)";
                        const ry = H - r * (H - 24) - 12;
                        ctx.fillRect(px, ry, 1.5, 1.5);

                        // Green Channel
                        ctx.fillStyle = "rgba(34, 197, 94, 0.4)";
                        const gy = H - g * (H - 24) - 12;
                        ctx.fillRect(colW + 10 + px, gy, 1.5, 1.5);

                        // Blue Channel
                        ctx.fillStyle = "rgba(56, 189, 248, 0.4)";
                        const by = H - b * (H - 24) - 12;
                        ctx.fillRect(colW * 2 + 20 + px, by, 1.5, 1.5);
                    }
                }
            } else {
                // Luminance Waveform
                for (let x = 0; x < sW; x++) {
                    for (let y = 0; y < sH; y++) {
                        const idx = (y * sW + x) * 4;
                        const r = imgData[idx];
                        const g = imgData[idx + 1];
                        const b = imgData[idx + 2];
                        const lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0;

                        const px = (x / sW) * (W - 20) + 10;
                        const py = H - lum * (H - 24) - 12;

                        ctx.fillStyle = "rgba(52, 211, 153, 0.35)";
                        ctx.fillRect(px, py, 1.5, 1.5);
                    }
                }
            }
        } catch (_) {}
    }

    _setupWheelListeners() {
        const sendUpdate = () => {
            if (window.socket) {
                window.socket.send({
                    type: "set_color_grade",
                    ...this.grade
                });
                window.seekTo(window.store.currentTime);
            }
        };

        const setupWheel = (wheelId, handleId, targetKey) => {
            const wheel = document.getElementById(wheelId);
            const handle = document.getElementById(handleId);
            if (!wheel || !handle) return;

            let isDragging = false;

            const onMove = (e) => {
                if (!isDragging) return;
                const rect = wheel.getBoundingClientRect();
                const cx = rect.left + rect.width / 2;
                const cy = rect.top + rect.height / 2;
                let dx = (e.clientX - cx) / (rect.width / 2);
                let dy = (e.clientY - cy) / (rect.height / 2);
                const len = Math.hypot(dx, dy);
                if (len > 1.0) {
                    dx /= len;
                    dy /= len;
                }
                handle.style.left = `${50 + dx * 45}%`;
                handle.style.top = `${50 + dy * 45}%`;

                if (targetKey === "lift") {
                    this.grade.lift = [dx * 0.1, -dy * 0.1, (-dx - dy) * 0.05];
                } else if (targetKey === "gamma") {
                    this.grade.gamma = [1.0 + dx * 0.2, 1.0 - dy * 0.2, 1.0 + (-dx - dy) * 0.1];
                } else if (targetKey === "gain") {
                    this.grade.gain = [1.0 + dx * 0.3, 1.0 - dy * 0.3, 1.0 + (-dx - dy) * 0.15];
                }
                sendUpdate();
            };

            wheel.addEventListener("mousedown", (e) => {
                isDragging = true;
                onMove(e);
                const onUp = () => {
                    isDragging = false;
                    window.removeEventListener("mousemove", onMove);
                    window.removeEventListener("mouseup", onUp);
                };
                window.addEventListener("mousemove", onMove);
                window.addEventListener("mouseup", onUp);
            });
        };

        setupWheel("liftWheel", "liftHandle", "lift");
        setupWheel("gammaWheel", "gammaHandle", "gamma");
        setupWheel("gainWheel", "gainHandle", "gain");

        const sliderExp = document.getElementById("sliderExp");
        const expVal = document.getElementById("expVal");
        if (sliderExp) {
            sliderExp.oninput = (e) => {
                const val = parseFloat(e.target.value);
                this.grade.exposure = val;
                expVal.innerText = `${val.toFixed(2)} EV`;
                sendUpdate();
            };
        }

        const sliderContrast = document.getElementById("sliderContrast");
        const contrastVal = document.getElementById("contrastVal");
        if (sliderContrast) {
            sliderContrast.oninput = (e) => {
                const val = parseFloat(e.target.value);
                this.grade.contrast = val;
                contrastVal.innerText = `${val.toFixed(2)}x`;
                sendUpdate();
            };
        }

        const sliderSat = document.getElementById("sliderSat");
        const satVal = document.getElementById("satVal");
        if (sliderSat) {
            sliderSat.oninput = (e) => {
                const val = parseFloat(e.target.value);
                this.grade.saturation = val;
                satVal.innerText = `${val.toFixed(2)}x`;
                sendUpdate();
            };
        }

        const sliderTemp = document.getElementById("sliderTemp");
        const tempVal = document.getElementById("tempVal");
        if (sliderTemp) {
            sliderTemp.oninput = (e) => {
                const val = parseFloat(e.target.value);
                this.grade.temperature = val;
                tempVal.innerText = val.toFixed(2);
                sendUpdate();
            };
        }
    }
}

window.ColorPage = ColorPage;
