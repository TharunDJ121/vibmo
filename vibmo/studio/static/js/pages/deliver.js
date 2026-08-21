/**
 * Deliver / Render Page: Export Presets and Queue Manager.
 */

class DeliverPage {
    constructor() {
        this.presetsContainer = document.getElementById("deliverPresetsContainer");
        this.presets = [];
        this.selectedPreset = "mp4_high";
        this.loadPresets();
    }

    async loadPresets() {
        try {
            const res = await fetch("/api/presets");
            const data = await res.json();
            this.presets = data.presets || [];
            this.render();
        } catch (_) {}
    }

    render() {
        if (!this.presetsContainer) return;
        this.presetsContainer.innerHTML = "";

        this.presets.forEach(p => {
            const card = document.createElement("div");
            const isSel = (this.selectedPreset === p.id);
            card.style.cssText = `background:${isSel ? 'rgba(99,102,241,0.15)' : '#0f172a'}; border:1px solid ${isSel ? '#6366f1' : '#334155'}; border-radius:12px; padding:16px; margin-bottom:12px; cursor:pointer;`;
            card.innerHTML = `
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div style="font-weight:700; font-size:14px; color:#fff;">${p.name}</div>
                    <span style="font-size:11px; background:#1e293b; color:#38bdf8; padding:2px 8px; border-radius:6px; font-weight:700;">.${p.format.toUpperCase()}</span>
                </div>
                <p style="font-size:12px; color:#94a3b8; margin-top:6px;">${p.description}</p>
            `;

            card.onclick = () => {
                this.selectedPreset = p.id;
                this.render();
            };

            this.presetsContainer.appendChild(card);
        });
    }
}

window.DeliverPage = DeliverPage;
