/**
 * Fairlight Audio Page: Soundboard triggers and Foley sound player.
 */

class FairlightPage {
    constructor() {
        this.container = document.getElementById("fairlightSoundboard");
        this.sounds = [];
        this.loadSoundboard();
    }

    async loadSoundboard() {
        try {
            const res = await fetch("/api/soundboard");
            const data = await res.json();
            this.sounds = data.sounds || [];
            this.render();
        } catch (_) {}
    }

    render() {
        if (!this.container) return;
        this.container.innerHTML = "";

        this.sounds.forEach(snd => {
            const card = document.createElement("div");
            card.style.cssText = "background:#0f172a; border:1px solid #334155; border-radius:10px; padding:16px; display:flex; align-items:center; justify-content:space-between; cursor:pointer;";
            card.innerHTML = `
                <div style="display:flex; align-items:center; gap:12px;">
                    <span style="font-size:24px;">${snd.icon}</span>
                    <div>
                        <div style="font-weight:700; font-size:13px; color:#fff;">${snd.label}</div>
                        <div style="font-size:11px; color:#94a3b8;">${snd.category} • :${snd.name}</div>
                    </div>
                </div>
                <button class="btn-icon" style="background:#6366f1; border-color:#6366f1; color:#fff;">🔊 Play</button>
            `;

            card.onclick = () => {
                const aud = new Audio(`/api/sfx/play/${snd.name}`);
                aud.play().catch(() => {});
            };


            this.container.appendChild(card);
        });
    }
}

window.FairlightPage = FairlightPage;
