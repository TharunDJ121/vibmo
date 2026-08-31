/**
 * Deliver / Render Page: Export Presets and Batch Queue Manager.
 * Inspired by DaVinci Resolve Deliver Page.
 */

class DeliverPage {
    constructor() {
        this.presetsContainer = document.getElementById("deliverPresetsContainer");
        this.presets = [];
        this.selectedPreset = "mp4_1080p";
        this.queue = [];
        this.pollInterval = null;
        this.init();
    }

    async init() {
        await this.loadPresets();
        await this.loadQueue();
        this.startQueuePolling();
    }

    async loadPresets() {
        try {
            const res = await fetch("/api/presets");
            const data = await res.json();
            this.presets = data.presets || [];
            this.render();
        } catch (_) {}
    }

    async loadQueue() {
        try {
            const res = await fetch("/api/render/queue");
            const data = await res.json();
            this.queue = data.jobs || [];
            this.render();
        } catch (_) {}
    }

    startQueuePolling() {
        if (this.pollInterval) clearInterval(this.pollInterval);
        this.pollInterval = setInterval(async () => {
            if (document.getElementById("page_deliver") && document.getElementById("page_deliver").classList.contains("active")) {
                await this.loadQueue();
            }
        }, 1500);
    }

    async addToQueue(presetId) {
        try {
            const res = await fetch("/api/render/queue/add", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ preset_id: presetId }),
            });
            const data = await res.json();
            if (data.status === "ok") {
                await this.loadQueue();
            }
        } catch (e) {
            console.error("Error adding to render queue:", e);
        }
    }

    async deleteJob(jobId) {
        try {
            await fetch(`/api/render/queue/${jobId}`, { method: "DELETE" });
            await this.loadQueue();
        } catch (e) {
            console.error("Error deleting job:", e);
        }
    }

    async clearCompleted() {
        try {
            await fetch("/api/render/queue/clear_completed", { method: "POST" });
            await this.loadQueue();
        } catch (e) {
            console.error("Error clearing completed jobs:", e);
        }
    }

    async startBatch() {
        try {
            await fetch("/api/render/queue/start_batch", { method: "POST" });
            await this.loadQueue();
        } catch (e) {
            console.error("Error starting batch render:", e);
        }
    }

    render() {
        if (!this.presetsContainer) return;
        this.presetsContainer.innerHTML = "";

        const wrapper = document.createElement("div");
        wrapper.style.cssText = "display:grid; grid-template-columns:1.2fr 1fr; gap:24px; align-items:start;";

        // Left Column: Presets List
        const presetsCol = document.createElement("div");
        presetsCol.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <span style="font-weight:700; font-size:13px; color:#94a3b8; text-transform:uppercase; letter-spacing:0.5px;">Export Presets</span>
                <span style="font-size:11px; color:#64748b;">Click to select</span>
            </div>
        `;

        this.presets.forEach(p => {
            const card = document.createElement("div");
            const isSel = (this.selectedPreset === p.id);
            card.style.cssText = `background:${isSel ? 'rgba(99,102,241,0.15)' : '#0f172a'}; border:1px solid ${isSel ? '#6366f1' : '#334155'}; border-radius:12px; padding:14px 16px; margin-bottom:10px; cursor:pointer; transition:all 0.15s ease;`;
            card.innerHTML = `
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div style="font-weight:700; font-size:13px; color:#fff;">${p.name}</div>
                    <div style="display:flex; gap:6px; align-items:center;">
                        <span style="font-size:10px; background:#1e293b; color:#38bdf8; padding:2px 6px; border-radius:4px; font-weight:700;">${p.aspect_ratio || '16:9'}</span>
                        <span style="font-size:10px; background:#334155; color:#e2e8f0; padding:2px 6px; border-radius:4px; font-weight:700;">.${p.format.toUpperCase()}</span>
                    </div>
                </div>
                <p style="font-size:11px; color:#94a3b8; margin-top:4px; line-height:1.4;">${p.description}</p>
                <div style="margin-top:8px; display:flex; justify-content:flex-end; gap:8px;">
                    <button class="btn-icon" style="font-size:10px; padding:3px 10px; color:#38bdf8; border-color:rgba(56,189,248,0.4);" onclick="event.stopPropagation(); window.deliverPage.addToQueue('${p.id}')">➕ Add to Queue</button>
                </div>
            `;

            card.onclick = () => {
                this.selectedPreset = p.id;
                this.render();
            };

            presetsCol.appendChild(card);
        });

        // Right Column: Batch Render Queue
        const queueCol = document.createElement("div");
        queueCol.style.cssText = "background:#0f172a; border:1px solid #1e293b; border-radius:12px; padding:16px;";
        queueCol.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                <span style="font-weight:700; font-size:13px; color:#94a3b8; text-transform:uppercase; letter-spacing:0.5px;">📋 Render Queue (${this.queue.length})</span>
                <div style="display:flex; gap:6px;">
                    <button class="btn-icon" style="font-size:10px; padding:3px 8px; color:#94a3b8;" onclick="window.deliverPage.clearCompleted()">Clear Finished</button>
                    <button class="btn-icon btn-primary" style="font-size:11px; padding:4px 12px; background:#6366f1; color:#fff;" onclick="window.deliverPage.startBatch()">⚡ Render All</button>
                </div>
            </div>
        `;

        if (this.queue.length === 0) {
            queueCol.innerHTML += `
                <div style="text-align:center; padding:32px 16px; color:#64748b; font-size:12px; border:1px dashed #334155; border-radius:8px;">
                    Render Queue is empty.<br>Select a preset on the left and click <b>Add to Queue</b> to queue batch deliverables.
                </div>
            `;
        } else {
            const queueList = document.createElement("div");
            queueList.style.cssText = "display:flex; flex-direction:column; gap:8px;";

            this.queue.forEach(job => {
                const item = document.createElement("div");
                let statusColor = "#38bdf8";
                let statusBg = "rgba(56, 189, 248, 0.1)";
                if (job.status === "completed") { statusColor = "#34d399"; statusBg = "rgba(52, 211, 153, 0.1)"; }
                else if (job.status === "failed") { statusColor = "#f43f5e"; statusBg = "rgba(244, 63, 94, 0.1)"; }
                else if (job.status === "rendering") { statusColor = "#fbbf24"; statusBg = "rgba(251, 191, 36, 0.1)"; }

                item.style.cssText = `background:#1e293b; border:1px solid ${job.status === 'rendering' ? '#fbbf24' : '#334155'}; border-radius:8px; padding:10px 12px;`;
                item.innerHTML = `
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div style="font-size:12px; font-weight:700; color:#fff;">${job.name}</div>
                        <div style="display:flex; gap:6px; align-items:center;">
                            <span style="font-size:10px; color:${statusColor}; background:${statusBg}; padding:2px 6px; border-radius:4px; font-weight:700; text-transform:uppercase;">${job.status}</span>
                            <button style="background:transparent; border:none; color:#64748b; cursor:pointer; font-size:12px; padding:0 2px;" onclick="window.deliverPage.deleteJob('${job.job_id}')" title="Remove Job">✕</button>
                        </div>
                    </div>
                    <div style="font-size:10px; color:#94a3b8; margin-top:2px; font-family:monospace;">${job.output_filename} (${job.width}x${job.height})</div>
                    ${job.status === 'rendering' ? `
                        <div style="width:100%; height:4px; background:#0f172a; border-radius:2px; margin-top:8px; overflow:hidden;">
                            <div style="width:${job.progress}%; height:100%; background:#fbbf24; transition:width 0.3s ease;"></div>
                        </div>
                    ` : ''}
                    ${job.error_message ? `<div style="font-size:10px; color:#f43f5e; margin-top:4px;">Error: ${job.error_message}</div>` : ''}
                `;
                queueList.appendChild(item);
            });
            queueCol.appendChild(queueList);
        }

        wrapper.appendChild(presetsCol);
        wrapper.appendChild(queueCol);
        this.presetsContainer.appendChild(wrapper);
    }
}

window.DeliverPage = DeliverPage;
