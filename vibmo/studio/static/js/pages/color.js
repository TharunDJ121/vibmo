/**
 * Color & Grading Page: Lift / Gamma / Gain Wheels & Post-FX parameters.
 */

class ColorPage {
    constructor() {
        this.container = document.getElementById("colorControlsContainer");
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
                    <div class="ctrl-label-val"><span>Exposure</span><span id="expVal">0.0 EV</span></div>
                    <input id="sliderExp" class="ctrl-slider" type="range" min="-2" max="2" step="0.05" value="0" />
                </div>
                <div class="ctrl-row">
                    <div class="ctrl-label-val"><span>Contrast</span><span id="contrastVal">1.0x</span></div>
                    <input id="sliderContrast" class="ctrl-slider" type="range" min="0.5" max="2.0" step="0.05" value="1.0" />
                </div>
                <div class="ctrl-row">
                    <div class="ctrl-label-val"><span>Saturation</span><span id="satVal">1.0x</span></div>
                    <input id="sliderSat" class="ctrl-slider" type="range" min="0" max="2.5" step="0.05" value="1.0" />
                </div>
                <div class="ctrl-row">
                    <div class="ctrl-label-val"><span>Color Temp</span><span id="tempVal">0</span></div>
                    <input id="sliderTemp" class="ctrl-slider" type="range" min="-1" max="1" step="0.05" value="0" />
                </div>
            </div>
        `;

        this._setupListeners();
    }

    _setupListeners() {
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

                // Convert wheel Cartesian position into RGB delta
                if (targetKey === "lift") {
                    this.grade.lift = [dx * 0.1, -dy * 0.1, (-dx - dy) * 0.05];
                } else if (targetKey === "gamma") {
                    this.grade.gamma = [1.0 + dx * 0.2, 1.0 - dy * 0.2, 1.0 + (-dx - dy) * 0.1];
                } else if (targetKey === "gain") {
                    this.grade.gain = [1.0 + dx * 0.2, 1.0 - dy * 0.2, 1.0 + (-dx - dy) * 0.1];
                }
                sendUpdate();
            };

            wheel.addEventListener("mousedown", (e) => {
                isDragging = true;
                onMove(e);
            });
            window.addEventListener("mousemove", onMove);
            window.addEventListener("mouseup", () => { isDragging = false; });
        };

        setupWheel("liftWheel", "liftHandle", "lift");
        setupWheel("gammaWheel", "gammaHandle", "gamma");
        setupWheel("gainWheel", "gainHandle", "gain");

        const bindSlider = (id, valId, unit, setter) => {
            const sl = document.getElementById(id);
            const vl = document.getElementById(valId);
            if (!sl || !vl) return;
            sl.addEventListener("input", (e) => {
                const v = parseFloat(e.target.value);
                vl.textContent = `${v}${unit}`;
                setter(v);
                sendUpdate();
            });
        };

        bindSlider("sliderExp", "expVal", " EV", (v) => { this.grade.exposure = v; });
        bindSlider("sliderContrast", "contrastVal", "x", (v) => { this.grade.contrast = v; });
        bindSlider("sliderSat", "satVal", "x", (v) => { this.grade.saturation = v; });
        bindSlider("sliderTemp", "tempVal", "", (v) => { this.grade.temperature = v; });
    }
}

window.ColorPage = ColorPage;

