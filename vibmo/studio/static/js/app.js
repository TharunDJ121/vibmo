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
    window.fusionPage = fusionPage;
    const colorPage = new window.ColorPage();
    window.colorPage = colorPage;
    const fairlightPage = new window.FairlightPage();
    window.fairlightPage = fairlightPage;
    const deliverPage = new window.DeliverPage();
    window.deliverPage = deliverPage;
    const viewport = new window.StudioViewport();
    window.viewport = viewport;


    let playbackRafId = null;
    let playbackStartTime = 0;
    let playbackStartPlayhead = 0;
    let playbackSpeed = 1.0;
    let isKDown = false;

    function playbackLoop(timestamp) {
        if (!window.store.isPlaying) return;

        const elapsed = (performance.now() - playbackStartTime) / 1000.0;
        let targetTime = playbackStartPlayhead + (elapsed * playbackSpeed);
        const dur = window.store.duration || 5.0;

        if (targetTime >= dur) {
            targetTime = 0.0;
            playbackStartTime = performance.now();
            playbackStartPlayhead = 0.0;
            window.audioEngine.seek(0.0);
        } else if (targetTime < 0.0) {
            targetTime = dur;
            playbackStartTime = performance.now();
            playbackStartPlayhead = dur;
            window.audioEngine.seek(dur);
        }

        window.store.currentTime = targetTime;
        motionPage.updatePlayhead(targetTime);

        // Request frame at target timestamp
        window.socket.requestFrame(targetTime, window.store.scaleFactor);

        playbackRafId = requestAnimationFrame(playbackLoop);
    }

    function startPlayback(speed = 1.0) {
        playbackSpeed = speed;
        window.store.isPlaying = true;
        playPauseBtn.innerText = speed > 1 ? `▶▶ ${speed}x` : (speed < 0 ? `◀◀ ${Math.abs(speed)}x` : "⏸ Pause");
        playbackStartTime = performance.now();
        playbackStartPlayhead = window.store.currentTime;
        if (speed > 0) window.audioEngine.play(window.store.currentTime);
        else window.audioEngine.pause();
        playbackRafId = requestAnimationFrame(playbackLoop);
    }

    function stopPlayback() {
        window.store.isPlaying = false;
        playbackSpeed = 1.0;
        playPauseBtn.innerText = "▶ Play";
        if (playbackRafId) {
            cancelAnimationFrame(playbackRafId);
            playbackRafId = null;
        }
        window.audioEngine.pause();
    }

    function togglePlayback() {
        if (window.store.isPlaying) stopPlayback();
        else startPlayback(1.0);
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
            if (window.store.activePage === "color" && window.colorPage && window.colorPage.currentViewMode === "scopes") {
                window.colorPage.drawScopes();
            }
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

        function attachVirtualScrubber(valEl, labelEl, sliderEl, min, max, step, defVal, onUpdate) {
            if (!valEl) return;
            let isScrubbing = false;
            let startX = 0;
            let startVal = 0;

            valEl.addEventListener("mousedown", (e) => {
                isScrubbing = true;
                startX = e.clientX;
                startVal = parseFloat(sliderEl.value);
                valEl.classList.add("scrubbing");
                document.body.style.cursor = "ew-resize";

                const onMove = (ev) => {
                    if (!isScrubbing) return;
                    const deltaX = ev.clientX - startX;
                    let sensitivity = step;
                    if (ev.shiftKey) sensitivity *= 0.1; // Fine sub-decimal step
                    else if (ev.ctrlKey || ev.altKey) sensitivity *= 5.0; // Coarse step

                    const newVal = Math.max(min, Math.min(max, startVal + deltaX * sensitivity));
                    sliderEl.value = newVal;
                    onUpdate(newVal);
                };

                const onUp = () => {
                    isScrubbing = false;
                    valEl.classList.remove("scrubbing");
                    document.body.style.cursor = "";
                    window.removeEventListener("mousemove", onMove);
                    window.removeEventListener("mouseup", onUp);
                };

                window.addEventListener("mousemove", onMove);
                window.addEventListener("mouseup", onUp);
            });

            if (labelEl) {
                labelEl.addEventListener("dblclick", () => {
                    sliderEl.value = defVal;
                    onUpdate(defVal);
                });
            }
        }

        inspectorProperties.innerHTML = `
            <div class="ctrl-row">
                <div class="ctrl-label-val"><span class="ctrl-label" id="lbl_x" title="Double click to reset">Position X</span><span class="ctrl-val" id="val_x">${Math.round(node.x)}px</span></div>
                <input class="ctrl-slider" type="range" min="0" max="${window.store.sceneWidth}" value="${node.x}" id="inp_x" />
            </div>
            <div class="ctrl-row">
                <div class="ctrl-label-val"><span class="ctrl-label" id="lbl_y" title="Double click to reset">Position Y</span><span class="ctrl-val" id="val_y">${Math.round(node.y)}px</span></div>
                <input class="ctrl-slider" type="range" min="0" max="${window.store.sceneHeight}" value="${node.y}" id="inp_y" />
            </div>
            <div class="ctrl-grid-2">
                <div class="ctrl-row">
                    <div class="ctrl-label-val"><span class="ctrl-label" id="lbl_scale" title="Double click to reset">Scale</span><span class="ctrl-val" id="val_scale">${node.scale_x.toFixed(2)}x</span></div>
                    <input class="ctrl-slider" type="range" min="0.1" max="3" step="0.05" value="${node.scale_x}" id="inp_scale" />
                </div>
                <div class="ctrl-row">
                    <div class="ctrl-label-val"><span class="ctrl-label" id="lbl_opacity" title="Double click to reset">Opacity</span><span class="ctrl-val" id="val_opacity">${node.opacity.toFixed(2)}</span></div>
                    <input class="ctrl-slider" type="range" min="0" max="1" step="0.05" value="${node.opacity}" id="inp_opacity" />
                </div>
            </div>
            <div class="ctrl-grid-2">
                <div class="ctrl-row">
                    <div class="ctrl-label-val"><span class="ctrl-label" id="lbl_rx" title="Double click to reset">Rotate X</span><span class="ctrl-val" id="val_rx">${(node.rotate_x || 0).toFixed(2)}</span></div>
                    <input class="ctrl-slider" type="range" min="-1.57" max="1.57" step="0.02" value="${node.rotate_x || 0}" id="inp_rx" />
                </div>
                <div class="ctrl-row">
                    <div class="ctrl-label-val"><span class="ctrl-label" id="lbl_ry" title="Double click to reset">Rotate Y</span><span class="ctrl-val" id="val_ry">${(node.rotate_y || 0).toFixed(2)}</span></div>
                    <input class="ctrl-slider" type="range" min="-1.57" max="1.57" step="0.02" value="${node.rotate_y || 0}" id="inp_ry" />
                </div>
            </div>
        `;

        const inpX = document.getElementById("inp_x");
        const valX = document.getElementById("val_x");
        const lblX = document.getElementById("lbl_x");
        const updateX = (val) => {
            node.x = val;
            valX.innerText = `${Math.round(val)}px`;
            window.socket.send({ type: "set_node_prop", node_id: node.id, prop: "position_x", value: val });
            window.seekTo(window.store.currentTime);
            refreshPythonCode();
        };
        inpX.oninput = (e) => updateX(parseFloat(e.target.value));
        attachVirtualScrubber(valX, lblX, inpX, 0, window.store.sceneWidth, 1.0, window.store.sceneWidth / 2, updateX);

        const inpY = document.getElementById("inp_y");
        const valY = document.getElementById("val_y");
        const lblY = document.getElementById("lbl_y");
        const updateY = (val) => {
            node.y = val;
            valY.innerText = `${Math.round(val)}px`;
            window.socket.send({ type: "set_node_prop", node_id: node.id, prop: "position_y", value: val });
            window.seekTo(window.store.currentTime);
            refreshPythonCode();
        };
        inpY.oninput = (e) => updateY(parseFloat(e.target.value));
        attachVirtualScrubber(valY, lblY, inpY, 0, window.store.sceneHeight, 1.0, window.store.sceneHeight / 2, updateY);

        const inpScale = document.getElementById("inp_scale");
        const valScale = document.getElementById("val_scale");
        const lblScale = document.getElementById("lbl_scale");
        const updateScale = (val) => {
            node.scale_x = val;
            valScale.innerText = `${val.toFixed(2)}x`;
            window.socket.send({ type: "set_node_prop", node_id: node.id, prop: "scale", value: val });
            window.seekTo(window.store.currentTime);
            refreshPythonCode();
        };
        inpScale.oninput = (e) => updateScale(parseFloat(e.target.value));
        attachVirtualScrubber(valScale, lblScale, inpScale, 0.1, 3.0, 0.01, 1.0, updateScale);

        const inpOpacity = document.getElementById("inp_opacity");
        const valOpacity = document.getElementById("val_opacity");
        const lblOpacity = document.getElementById("lbl_opacity");
        const updateOpacity = (val) => {
            node.opacity = val;
            valOpacity.innerText = val.toFixed(2);
            window.socket.send({ type: "set_node_prop", node_id: node.id, prop: "opacity", value: val });
            window.seekTo(window.store.currentTime);
            refreshPythonCode();
        };
        inpOpacity.oninput = (e) => updateOpacity(parseFloat(e.target.value));
        attachVirtualScrubber(valOpacity, lblOpacity, inpOpacity, 0.0, 1.0, 0.01, 1.0, updateOpacity);

        const inpRx = document.getElementById("inp_rx");
        const valRx = document.getElementById("val_rx");
        const lblRx = document.getElementById("lbl_rx");
        const updateRx = (val) => {
            node.rotate_x = val;
            valRx.innerText = val.toFixed(2);
            window.socket.send({ type: "set_node_prop", node_id: node.id, prop: "rotate_x", value: val });
            window.seekTo(window.store.currentTime);
            refreshPythonCode();
        };
        inpRx.oninput = (e) => updateRx(parseFloat(e.target.value));
        attachVirtualScrubber(valRx, lblRx, inpRx, -1.57, 1.57, 0.01, 0.0, updateRx);

        const inpRy = document.getElementById("inp_ry");
        const valRy = document.getElementById("val_ry");
        const lblRy = document.getElementById("lbl_ry");
        const updateRy = (val) => {
            node.rotate_y = val;
            valRy.innerText = val.toFixed(2);
            window.socket.send({ type: "set_node_prop", node_id: node.id, prop: "rotate_y", value: val });
            window.seekTo(window.store.currentTime);
            refreshPythonCode();
        };
        inpRy.oninput = (e) => updateRy(parseFloat(e.target.value));
        attachVirtualScrubber(valRy, lblRy, inpRy, -1.57, 1.57, 0.01, 0.0, updateRy);
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

    // Suggestion Chips
    document.querySelectorAll(".ai-chip").forEach(chip => {
        chip.onclick = () => {
            const p = chip.getAttribute("data-prompt");
            if (p && aiDirectorInput) {
                aiDirectorInput.value = p;
                aiDirectorSubmitBtn.click();
            }
        };
    });

    const clearAiHistoryBtn = document.getElementById("clearAiHistoryBtn");
    if (clearAiHistoryBtn) {
        clearAiHistoryBtn.onclick = async () => {
            try {
                await fetch("/api/ai/history/clear", { method: "POST" });
                aiDirectorLogsBox.innerText = "✦ Conversation history cleared. Awaiting new director instructions...";
            } catch (e) {}
        };
    }

    // Submit AI Director Prompt to LangGraph Engine
    if (aiDirectorSubmitBtn && aiDirectorInput) {
        aiDirectorSubmitBtn.onclick = async () => {
            const prompt = aiDirectorInput.value.trim();
            if (!prompt) return;

            const provider = document.getElementById("aiProviderSelect") ? document.getElementById("aiProviderSelect").value : null;

            aiDirectorSubmitBtn.innerText = "⏳ Applying...";
            aiDirectorSubmitBtn.disabled = true;
            aiDirectorLogsBox.innerText = `✦ LangGraph State Machine activated for: "${prompt}"\n`;

            try {
                const res = await fetch("/api/ai/edit", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ prompt, provider: provider || undefined }),
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

    // DaVinci Resolve Inspired Keyboard Shortcuts (J-K-L Shuttle, Space, Frame Jog, Cinema Viewer)
    window.addEventListener("keydown", (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
            e.preventDefault();
            if (openAiDirectorBtn) openAiDirectorBtn.click();
            return;
        }
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "f") {
            e.preventDefault();
            // Cinema Fullscreen Viewer Toggle (Command-F / Ctrl-F)
            const vp = document.querySelector(".viewport-stage");
            if (vp) {
                if (!document.fullscreenElement) vp.requestFullscreen().catch(() => {});
                else document.exitFullscreen().catch(() => {});
            }
            return;
        }

        if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") return;

        const key = e.key.toLowerCase();
        const fps = window.store.fps || 60;

        if (key === "k") {
            isKDown = true;
            stopPlayback();
            e.preventDefault();
            return;
        }

        if (key === "l") {
            e.preventDefault();
            if (isKDown) {
                // K + L: Jog forward 1 frame
                window.seekTo(window.store.currentTime + 1.0 / fps);
            } else {
                // L: Shuttle forward (1x -> 2x -> 4x)
                if (!window.store.isPlaying || playbackSpeed < 0) {
                    startPlayback(1.0);
                } else if (playbackSpeed === 1.0) {
                    startPlayback(2.0);
                } else if (playbackSpeed === 2.0) {
                    startPlayback(4.0);
                }
            }
            return;
        }

        if (key === "j") {
            e.preventDefault();
            if (isKDown) {
                // K + J: Jog backward 1 frame
                window.seekTo(window.store.currentTime - 1.0 / fps);
            } else {
                // J: Shuttle backward (-1x -> -2x -> -4x)
                if (!window.store.isPlaying || playbackSpeed > 0) {
                    startPlayback(-1.0);
                } else if (playbackSpeed === -1.0) {
                    startPlayback(-2.0);
                } else if (playbackSpeed === -2.0) {
                    startPlayback(-4.0);
                }
            }
            return;
        }

        if (e.code === "Space") {
            e.preventDefault();
            togglePlayback();
        } else if (e.code === "ArrowLeft") {
            e.preventDefault();
            window.seekTo(window.store.currentTime - 1.0 / fps);
        } else if (e.code === "ArrowRight") {
            e.preventDefault();
            window.seekTo(window.store.currentTime + 1.0 / fps);
        }
    });

    window.addEventListener("keyup", (e) => {
        if (e.key.toLowerCase() === "k") {
            isKDown = false;
        }
    });
});
