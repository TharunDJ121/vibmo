/**
 * Web Studio Pro Undo / Redo History Stack Manager & Visual History Window.
 * Inspired by DaVinci Resolve Chapter 2 (Undo History Window & Visual Reversion).
 */

class HistoryStack {
    constructor(maxSize = 50) {
        this.maxSize = maxSize;
        this.undoStack = []; // [{ label, timestamp, snapshot }]
        this.redoStack = [];
        this.currentIndex = -1;
        this._setupShortcuts();
    }

    _setupShortcuts() {
        window.addEventListener("keydown", (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "z") {
                if (e.shiftKey) {
                    this.redo();
                } else {
                    this.undo();
                }
                e.preventDefault();
            } else if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "y") {
                this.redo();
                e.preventDefault();
            } else if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "h") {
                this.openHistoryWindow();
                e.preventDefault();
            }
        });
    }

    record(actionLabel = "Modify State") {
        const snapshot = JSON.stringify({
            overrides: window.store.userOverrides,
            params: window.store.paramOverrides,
            colorGrade: window.store.colorGrade,
            currentTime: window.store.currentTime,
        });

        const entry = {
            label: actionLabel,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
            snapshot: snapshot,
        };

        this.undoStack.push(entry);
        if (this.undoStack.length > this.maxSize) {
            this.undoStack.shift();
        }
        this.redoStack = [];
        this.currentIndex = this.undoStack.length - 1;
        this._updateHistoryModal();
    }

    undo() {
        if (this.undoStack.length <= 1) return;
        const current = this.undoStack.pop();
        this.redoStack.push(current);

        const prev = this.undoStack[this.undoStack.length - 1];
        this.currentIndex = this.undoStack.length - 1;
        this._applySnapshot(JSON.parse(prev.snapshot));
        this._updateHistoryModal();
    }

    redo() {
        if (this.redoStack.length === 0) return;
        const next = this.redoStack.pop();
        this.undoStack.push(next);
        this.currentIndex = this.undoStack.length - 1;
        this._applySnapshot(JSON.parse(next.snapshot));
        this._updateHistoryModal();
    }

    jumpToStep(index) {
        if (index < 0 || index >= this.undoStack.length) return;
        // Move items between undo and redo
        while (this.undoStack.length - 1 > index) {
            this.redoStack.push(this.undoStack.pop());
        }
        const target = this.undoStack[this.undoStack.length - 1];
        this.currentIndex = index;
        this._applySnapshot(JSON.parse(target.snapshot));
        this._updateHistoryModal();
    }

    _applySnapshot(snap) {
        window.store.userOverrides = snap.overrides || {};
        window.store.paramOverrides = snap.params || {};
        window.store.colorGrade = snap.colorGrade || {};
        
        // Push state to backend
        if (window.socket) {
            for (const [nodeId, ov] of Object.entries(window.store.userOverrides)) {
                if (ov.position) {
                    window.socket.send({ type: "set_node_prop", node_id: nodeId, prop: "position_x", value: ov.position[0] });
                    window.socket.send({ type: "set_node_prop", node_id: nodeId, prop: "position_y", value: ov.position[1] });
                }
            }
            window.seekTo(snap.currentTime || window.store.currentTime);
        }
    }

    openHistoryWindow() {
        let modal = document.getElementById("historyModalBackdrop");
        if (!modal) {
            modal = document.createElement("div");
            modal.id = "historyModalBackdrop";
            modal.className = "modal-backdrop";
            modal.innerHTML = `
                <div class="modal-dialog" style="max-width:440px; background:#0b1329; border:1px solid #1e293b; border-radius:12px; padding:20px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; border-bottom:1px solid #1e293b; padding-bottom:12px;">
                        <span style="font-weight:700; font-size:14px; color:#fff;">📜 Visual Undo History (DaVinci Mode)</span>
                        <button class="btn-icon" onclick="document.getElementById('historyModalBackdrop').classList.remove('open')">✕</button>
                    </div>
                    <div id="historyListContainer" style="display:flex; flex-direction:column; gap:6px; max-height:360px; overflow-y:auto;"></div>
                </div>
            `;
            document.body.appendChild(modal);
            modal.onclick = (e) => { if (e.target === modal) modal.classList.remove("open"); };
        }
        modal.classList.add("open");
        this._updateHistoryModal();
    }

    _updateHistoryModal() {
        const container = document.getElementById("historyListContainer");
        if (!container) return;
        container.innerHTML = "";

        if (this.undoStack.length === 0) {
            container.innerHTML = `<div style="text-align:center; padding:20px; color:#64748b; font-size:12px;">No recorded operations yet.</div>`;
            return;
        }

        // List actions from oldest to newest
        this.undoStack.forEach((entry, idx) => {
            const row = document.createElement("div");
            const isCurrent = (idx === this.undoStack.length - 1);
            row.style.cssText = `
                display:flex; justify-content:space-between; align-items:center;
                padding:8px 12px; border-radius:6px; font-size:12px; cursor:pointer;
                background:${isCurrent ? 'rgba(99, 102, 241, 0.2)' : '#070d1e'};
                border:1px solid ${isCurrent ? '#6366f1' : 'transparent'};
                color:${isCurrent ? '#ffffff' : '#94a3b8'};
            `;
            row.innerHTML = `
                <div style="display:flex; align-items:center; gap:8px;">
                    <span style="font-size:11px; opacity:0.6;">#${idx + 1}</span>
                    <span style="font-weight:${isCurrent ? '700' : '500'};">${entry.label}</span>
                </div>
                <span style="font-size:10px; color:#64748b; font-family:monospace;">${entry.timestamp}</span>
            `;
            row.onclick = () => this.jumpToStep(idx);
            container.appendChild(row);
        });

        // Also list available redo steps grayed out
        this.redoStack.slice().reverse().forEach((entry, rIdx) => {
            const row = document.createElement("div");
            row.style.cssText = `
                display:flex; justify-content:space-between; align-items:center;
                padding:8px 12px; border-radius:6px; font-size:12px; cursor:pointer;
                background:rgba(15, 23, 42, 0.4); border:1px dashed #334155; opacity:0.5; color:#64748b;
            `;
            row.innerHTML = `
                <div style="display:flex; align-items:center; gap:8px;">
                    <span style="font-size:11px;">↪</span>
                    <span>${entry.label} (Redo)</span>
                </div>
                <span style="font-size:10px; font-family:monospace;">${entry.timestamp}</span>
            `;
            row.onclick = () => this.redo();
            container.appendChild(row);
        });
    }
}

window.HistoryStack = HistoryStack;
window.historyStack = new HistoryStack();
