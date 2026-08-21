/**
 * Web Studio Pro Undo / Redo History Stack Manager.
 */

class HistoryStack {
    constructor(maxSize = 50) {
        this.maxSize = maxSize;
        this.undoStack = [];
        this.redoStack = [];
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
            }
        });
    }

    record() {
        const snapshot = JSON.stringify({
            overrides: window.store.userOverrides,
            params: window.store.paramOverrides,
            colorGrade: window.store.colorGrade,
            currentTime: window.store.currentTime,
        });

        this.undoStack.push(snapshot);
        if (this.undoStack.length > this.maxSize) {
            this.undoStack.shift();
        }
        this.redoStack = [];
    }

    undo() {
        if (this.undoStack.length <= 1) return;
        const current = this.undoStack.pop();
        this.redoStack.push(current);

        const prev = JSON.parse(this.undoStack[this.undoStack.length - 1]);
        this._applySnapshot(prev);
    }

    redo() {
        if (this.redoStack.length === 0) return;
        const next = JSON.parse(this.redoStack.pop());
        this.undoStack.push(JSON.stringify(next));
        this._applySnapshot(next);
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

}

window.HistoryStack = HistoryStack;
window.historyStack = new HistoryStack();
