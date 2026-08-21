/**
 * Vibmo Studio Pro Master Application Orchestrator & Inspector Controller.
 */

document.addEventListener("DOMContentLoaded", () => {
    const renderCanvas = document.getElementById("renderCanvas");
    const playPauseBtn = document.getElementById("playPauseBtn");
    const rewindBtn = document.getElementById("rewindBtn");
    const qualitySelect = document.getElementById("qualitySelect");
    const copyCodeBtn = document.getElementById("copyCodeBtn");
    const renderMasterBtn = document.getElementById("renderMasterBtn");
    const inspectorProperties = document.getElementById("inspectorProperties");
    const inspectorParams = document.getElementById("inspectorParams");
    const generatedCodeBox = document.getElementById("generatedCodeBox");
    const selectedBadge = document.getElementById("selectedBadge");

    // Initialize Subsystems
    const motionPage = new window.MotionPage();
    window.motionPage = motionPage;
    const fusionPage = new window.FusionPage();
    const colorPage = new window.ColorPage();
    const fairlightPage = new window.FairlightPage();
    const deliverPage = new window.DeliverPage();
    const viewport = new window.StudioViewport();


    let playbackRafId = null;
    let playbackStartTime = 0;
    let playbackStartPlayhead = 0;

    function playbackLoop(timestamp) {
        if (!window.store.isPlaying) return;

        const elapsed = (performance.now() - playbackStartTime) / 1000.0;
        let targetTime = playbackStartPlayhead + elapsed;

        if (targetTime >= window.store.duration) {
            targetTime = 0.0;
            playbackStartTime = performance.now();
            playbackStartPlayhead = 0.0;
            window.audioEngine.seek(0.0);
        }

        window.store.currentTime = targetTime;
        motionPage.updatePlayhead(targetTime);

        // Request frame at target timestamp
        window.socket.requestFrame(targetTime, window.store.scaleFactor);

        playbackRafId = requestAnimationFrame(playbackLoop);
    }

    function startPlayback() {
        window.store.isPlaying = true;
        playPauseBtn.innerText = "⏸ Pause";
        playbackStartTime = performance.now();
        playbackStartPlayhead = window.store.currentTime;
        window.audioEngine.play(window.store.currentTime);
        playbackRafId = requestAnimationFrame(playbackLoop);
    }

    function stopPlayback() {
        window.store.isPlaying = false;
        playPauseBtn.innerText = "▶ Play";
        if (playbackRafId) {
            cancelAnimationFrame(playbackRafId);
            playbackRafId = null;
        }
        window.audioEngine.pause();
    }

    function togglePlayback() {
        if (window.store.isPlaying) stopPlayback();
        else startPlayback();
    }

    window.socket = new window.StudioSocket((msg) => {
        if (msg.type === "frame") {
            renderCanvas.src = "data:image/jpeg;base64," + msg.image;
            if (!window.store.isPlaying) {
                window.store.currentTime = msg.time;
                motionPage.updatePlayhead(msg.time);
            }
            viewport.syncSize();
            viewport.drawGizmo();
        } else if (msg.type === "meta") {
            window.store.updateMetadata(msg);
            motionPage.renderRuler();
            motionPage.renderLayers();
            motionPage.renderTracks();
            buildParamControllers(msg.params || {});
            refreshPythonCode();
        }
    });

    window.seekTo = (t) => {
        if (window.store.isPlaying) {
            playbackStartTime = performance.now();
            playbackStartPlayhead = t;
        }
        window.store.currentTime = Math.max(0, Math.min(window.store.duration, t));
        motionPage.updatePlayhead(window.store.currentTime);
        window.socket.requestFrame(window.store.currentTime, window.store.scaleFactor);
        window.audioEngine.seek(window.store.currentTime);
    };

    playPauseBtn.onclick = togglePlayback;
    rewindBtn.onclick = () => window.seekTo(0.0);

    qualitySelect.onchange = (e) => {
        window.store.scaleFactor = parseFloat(e.target.value);
        window.seekTo(window.store.currentTime);
    };


    // DaVinci 5 Workspace Page Switcher Tabs
    document.querySelectorAll(".tab-btn").forEach(btn => {
        btn.onclick = () => {
            document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
            document.querySelectorAll(".page-view").forEach(p => p.classList.remove("active"));
            
            btn.classList.add("active");
            const pageId = btn.getAttribute("data-page");
            window.store.activePage = pageId;

            const targetView = document.getElementById(`page_${pageId}`);
            if (targetView) targetView.classList.add("active");

            if (pageId === "fusion") fusionPage.loadGraph();
            else if (pageId === "color") colorPage.render();
            else if (pageId === "fairlight") fairlightPage.render();
            else if (pageId === "deliver") deliverPage.render();
        };
    });

    // Node Selection & Inspector
    window.store.subscribe((event, payload) => {
        if (event === "selection_changed") {
            const node = window.store.getSelectedNode();
            selectedBadge.innerText = node ? node.name : "No Selection";
            buildNodeInspector(node);
            viewport.drawGizmo();
            motionPage.renderLayers();
            motionPage.renderTracks();
            refreshPythonCode();
        }
    });

    function buildNodeInspector(node) {
        if (!inspectorProperties) return;
        if (!node) {
            inspectorProperties.innerHTML = `<div style="text-align:center; padding:20px; color:#64748b; font-size:12px; font-style:italic;">Select a layer on canvas or timeline</div>`;
            return;
        }

        inspectorProperties.innerHTML = `
            <div class="ctrl-row">
                <div class="ctrl-label-val"><span>Position X</span><span class="ctrl-val">${Math.round(node.x)}px</span></div>
                <input class="ctrl-slider" type="range" min="0" max="${window.store.sceneWidth}" value="${node.x}" id="inp_x" />
            </div>
            <div class="ctrl-row">
                <div class="ctrl-label-val"><span>Position Y</span><span class="ctrl-val">${Math.round(node.y)}px</span></div>
                <input class="ctrl-slider" type="range" min="0" max="${window.store.sceneHeight}" value="${node.y}" id="inp_y" />
            </div>
            <div class="ctrl-grid-2">
                <div class="ctrl-row">
                    <div class="ctrl-label-val"><span>Scale</span><span class="ctrl-val">${node.scale_x.toFixed(2)}x</span></div>
                    <input class="ctrl-slider" type="range" min="0.1" max="3" step="0.05" value="${node.scale_x}" id="inp_scale" />
                </div>
                <div class="ctrl-row">
                    <div class="ctrl-label-val"><span>Opacity</span><span class="ctrl-val">${node.opacity.toFixed(2)}</span></div>
                    <input class="ctrl-slider" type="range" min="0" max="1" step="0.05" value="${node.opacity}" id="inp_opacity" />
                </div>
            </div>
            <div class="ctrl-grid-2">
                <div class="ctrl-row">
                    <div class="ctrl-label-val"><span>Rotate X (Pitch)</span><span class="ctrl-val">${(node.rotate_x || 0).toFixed(2)}</span></div>
                    <input class="ctrl-slider" type="range" min="-1.57" max="1.57" step="0.02" value="${node.rotate_x || 0}" id="inp_rx" />
                </div>
                <div class="ctrl-row">
                    <div class="ctrl-label-val"><span>Rotate Y (Yaw)</span><span class="ctrl-val">${(node.rotate_y || 0).toFixed(2)}</span></div>
                    <input class="ctrl-slider" type="range" min="-1.57" max="1.57" step="0.02" value="${node.rotate_y || 0}" id="inp_ry" />
                </div>
            </div>
        `;

        document.getElementById("inp_x").oninput = (e) => {
            const val = parseFloat(e.target.value);
            node.x = val;
            window.socket.send({ type: "set_node_prop", node_id: node.id, prop: "position_x", value: val });
            window.seekTo(window.store.currentTime);
            refreshPythonCode();
        };

        document.getElementById("inp_y").oninput = (e) => {
            const val = parseFloat(e.target.value);
            node.y = val;
            window.socket.send({ type: "set_node_prop", node_id: node.id, prop: "position_y", value: val });
            window.seekTo(window.store.currentTime);
            refreshPythonCode();
        };

        document.getElementById("inp_scale").oninput = (e) => {
            const val = parseFloat(e.target.value);
            node.scale_x = val;
            window.socket.send({ type: "set_node_prop", node_id: node.id, prop: "scale", value: val });
            window.seekTo(window.store.currentTime);
            refreshPythonCode();
        };

        document.getElementById("inp_opacity").oninput = (e) => {
            const val = parseFloat(e.target.value);
            node.opacity = val;
            window.socket.send({ type: "set_node_prop", node_id: node.id, prop: "opacity", value: val });
            window.seekTo(window.store.currentTime);
            refreshPythonCode();
        };

        document.getElementById("inp_rx").oninput = (e) => {
            const val = parseFloat(e.target.value);
            node.rotate_x = val;
            window.socket.send({ type: "set_node_prop", node_id: node.id, prop: "rotate_x", value: val });
            window.seekTo(window.store.currentTime);
            refreshPythonCode();
        };

        document.getElementById("inp_ry").oninput = (e) => {
            const val = parseFloat(e.target.value);
            node.rotate_y = val;
            window.socket.send({ type: "set_node_prop", node_id: node.id, prop: "rotate_y", value: val });
            window.seekTo(window.store.currentTime);
            refreshPythonCode();
        };
    }

    function buildParamControllers(params) {
        if (!inspectorParams) return;
        inspectorParams.innerHTML = "";
        const keys = Object.keys(params);
        if (keys.length === 0) {
            inspectorParams.innerHTML = `<div style="text-align:center; padding:12px; color:#64748b; font-size:12px; font-style:italic;">No scene.param defined</div>`;
            return;
        }

        keys.forEach(k => {
            const p = params[k];
            const div = document.createElement("div");
            div.className = "ctrl-row";
            if (p.type === "color") {
                div.innerHTML = `
                    <div class="ctrl-label-val"><span>${k}</span><span class="ctrl-val">${p.value}</span></div>
                    <input type="color" value="${p.value}" style="width:100%; height:32px; border-radius:6px; border:1px solid #1e293b; background:none; cursor:pointer;" />
                `;
                div.querySelector("input").oninput = (e) => {
                    window.socket.send({ type: "set_param", name: k, value: e.target.value });
                    window.seekTo(window.store.currentTime);
                    refreshPythonCode();
                };
            } else {
                div.innerHTML = `
                    <div class="ctrl-label-val"><span>${k}</span><span class="ctrl-val">${p.value}</span></div>
                    <input class="ctrl-slider" type="range" min="${p.min || 0}" max="${p.max || 100}" step="0.1" value="${p.value}" />
                `;
                div.querySelector("input").oninput = (e) => {
                    window.socket.send({ type: "set_param", name: k, value: parseFloat(e.target.value) });
                    window.seekTo(window.store.currentTime);
                    refreshPythonCode();
                };
            }
            inspectorParams.appendChild(div);
        });
    }

    async function refreshPythonCode() {
        try {
            const res = await fetch("/api/export_code");
            const data = await res.json();
            if (generatedCodeBox) {
                generatedCodeBox.innerText = data.code || "# No overrides yet";
            }
        } catch (_) {}
    }

    copyCodeBtn.onclick = () => {
        if (generatedCodeBox) {
            navigator.clipboard.writeText(generatedCodeBox.innerText);
            alert("✓ Python code overrides copied to clipboard!");
        }
    };

    renderMasterBtn.onclick = () => {
        renderMasterBtn.innerText = "⏳ Exporting...";
        window.socket.send({ type: "start_render", preset: deliverPage.selectedPreset });
        setTimeout(() => {
            renderMasterBtn.innerText = "✓ Export Started";
            setTimeout(() => renderMasterBtn.innerText = "⚡ Deliver Export", 3000);
        }, 1000);
    };

    // =========================================================================
    // AI DIRECTOR (LANGGRAPH) & API KEYS CONTROLLERS
    // =========================================================================
    const openAiDirectorBtn = document.getElementById("openAiDirectorBtn");
    const aiDirectorModalBackdrop = document.getElementById("aiDirectorModalBackdrop");
    const closeAiDirectorModalBtn = document.getElementById("closeAiDirectorModalBtn");
    const aiDirectorInput = document.getElementById("aiDirectorInput");
    const aiDirectorSubmitBtn = document.getElementById("aiDirectorSubmitBtn");
    const aiDirectorLogsBox = document.getElementById("aiDirectorLogsBox");

    const openApiKeysBtn = document.getElementById("openApiKeysBtn");
    const apiKeysModalBackdrop = document.getElementById("apiKeysModalBackdrop");
    const closeApiKeysModalBtn = document.getElementById("closeApiKeysModalBtn");
    const apiKeysListContainer = document.getElementById("apiKeysListContainer");
    const apiKeyStatusMessage = document.getElementById("apiKeyStatusMessage");

    // Toggle AI Director Modal
    if (openAiDirectorBtn && aiDirectorModalBackdrop) {
        openAiDirectorBtn.onclick = () => {
            aiDirectorModalBackdrop.classList.add("open");
            aiDirectorInput.focus();
        };
        closeAiDirectorModalBtn.onclick = () => {
            aiDirectorModalBackdrop.classList.remove("open");
        };
    }

    // Submit AI Director Prompt to LangGraph Engine
    if (aiDirectorSubmitBtn && aiDirectorInput) {
        aiDirectorSubmitBtn.onclick = async () => {
            const prompt = aiDirectorInput.value.trim();
            if (!prompt) return;

            aiDirectorSubmitBtn.innerText = "⏳ Applying...";
            aiDirectorSubmitBtn.disabled = true;
            aiDirectorLogsBox.innerText = `✦ LangGraph State Machine activated for: "${prompt}"\n`;

            try {
                const res = await fetch("/api/ai/edit", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ prompt }),
                });
                const data = await res.json();

                if (data.logs && data.logs.length > 0) {
                    aiDirectorLogsBox.innerText = data.logs.join("\n") + "\n\n" + `✓ ${data.message}`;
                } else {
                    aiDirectorLogsBox.innerText = `✓ ${data.message}`;
                }

                if (data.status === "ok") {
                    window.seekTo(window.store.currentTime);
                    refreshPythonCode();
                }
            } catch (err) {
                aiDirectorLogsBox.innerText += `\n❌ Error: ${err.message}`;
            } finally {
                aiDirectorSubmitBtn.innerText = "⚡ Apply Edit";
                aiDirectorSubmitBtn.disabled = false;
            }
        };

        aiDirectorInput.onkeydown = (e) => {
            if (e.key === "Enter") {
                aiDirectorSubmitBtn.click();
            }
        };
    }

    // Toggle API Keys Modal
    if (openApiKeysBtn && apiKeysModalBackdrop) {
        openApiKeysBtn.onclick = () => {
            apiKeysModalBackdrop.classList.add("open");
            loadApiKeys();
        };
        closeApiKeysModalBtn.onclick = () => {
            apiKeysModalBackdrop.classList.remove("open");
        };
    }

    async function loadApiKeys() {
        if (!apiKeysListContainer) return;
        apiKeysListContainer.innerHTML = `<div style="font-size:12px; color:#64748b;">Loading provider status...</div>`;
        try {
            const res = await fetch("/api/settings/keys");
            const data = await res.json();
            apiKeysListContainer.innerHTML = "";

            Object.entries(data.providers || {}).forEach(([pId, meta]) => {
                const row = document.createElement("div");
                row.style.cssText = "display:flex; align-items:center; justify-content:space-between; background:#0b1329; border:1px solid #1e293b; padding:10px 14px; border-radius:8px; gap:12px;";

                const statusBadge = meta.is_configured
                    ? `<span style="background:rgba(16,185,129,0.15); color:#34d399; font-size:10px; padding:2px 8px; border-radius:999px;">✓ Configured (${meta.masked_key})</span>`
                    : `<span style="background:rgba(239,68,68,0.15); color:#f87171; font-size:10px; padding:2px 8px; border-radius:999px;">Not Configured</span>`;

                row.innerHTML = `
                    <div style="display:flex; flex-direction:column; gap:2px; flex:1;">
                        <div style="display:flex; align-items:center; gap:8px;">
                            <strong style="font-size:13px; color:#f8fafc;">${meta.name}</strong>
                            ${statusBadge}
                        </div>
                        <span style="font-size:11px; color:#64748b;">${meta.env_var}</span>
                    </div>
                    <input type="password" placeholder="Enter new key..." id="input_key_${pId}" style="width:170px; background:#030712; border:1px solid #1e293b; border-radius:6px; color:#fff; padding:6px 10px; font-size:11px; outline:none;" />
                    <button class="btn-icon" style="background:#047857; color:#fff; border:none; font-size:11px;" id="save_btn_${pId}">Save & Test</button>
                `;

                row.querySelector(`#save_btn_${pId}`).onclick = async () => {
                    const val = row.querySelector(`#input_key_${pId}`).value.trim();
                    if (!val) return;
                    apiKeyStatusMessage.innerText = `Testing connection to ${meta.name}...`;
                    apiKeyStatusMessage.style.color = "#38bdf8";

                    try {
                        const saveRes = await fetch("/api/settings/keys", {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({ provider: pId, key: val }),
                        });
                        const saveData = await saveRes.json();
                        apiKeyStatusMessage.innerText = saveData.message;
                        apiKeyStatusMessage.style.color = saveData.status === "ok" ? "#34d399" : "#fbbf24";
                        loadApiKeys();
                    } catch (saveErr) {
                        apiKeyStatusMessage.innerText = `Error: ${saveErr.message}`;
                        apiKeyStatusMessage.style.color = "#f87171";
                    }
                };

                apiKeysListContainer.appendChild(row);
            });
        } catch (e) {
            apiKeysListContainer.innerHTML = `<div style="color:#f87171; font-size:12px;">Failed to load keys: ${e.message}</div>`;
        }
    }

    // Keyboard Shortcuts (Space=Play, Left/Right=Frame step, Ctrl+K=AI Director, Ctrl+E=Script Editor)
    window.onkeydown = (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === "k") {
            e.preventDefault();
            if (openAiDirectorBtn) openAiDirectorBtn.click();
            return;
        }
        if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") return;
        if (e.code === "Space") {
            e.preventDefault();
            togglePlayback();
        } else if (e.code === "ArrowLeft") {
            e.preventDefault();
            window.seekTo(window.store.currentTime - 1.0 / window.store.fps);
        } else if (e.code === "ArrowRight") {
            e.preventDefault();
            window.seekTo(window.store.currentTime + 1.0 / window.store.fps);
        }
    };
});
