/**
 * Central State Store for Vibmo Studio Pro.
 */

class StudioStore {
    constructor() {
        this.currentTime = 0.0;
        this.duration = 5.0;
        this.fps = 60.0;
        this.sceneWidth = 1920;
        this.sceneHeight = 1080;
        this.isPlaying = false;
        this.activePage = "motion";
        this.scaleFactor = 0.5;
        this.selectedNodeId = null;
        this.nodes = [];
        this.params = {};
        this.sfxCues = [];
        this.listeners = [];
    }

    subscribe(fn) {
        this.listeners.push(fn);
    }

    notify(eventType, payload) {
        this.listeners.forEach(fn => fn(eventType, payload));
    }

    updateMetadata(meta) {
        this.duration = meta.duration || 5.0;
        this.fps = meta.fps || 60.0;
        this.sceneWidth = meta.width || 1920;
        this.sceneHeight = meta.height || 1080;
        this.nodes = meta.nodes || [];
        this.params = meta.params || {};
        this.sfxCues = meta.sfx_cues || [];
        this.notify("meta_updated", meta);
    }

    setSelectedNode(nodeId) {
        this.selectedNodeId = nodeId;
        this.notify("selection_changed", nodeId);
    }

    getSelectedNode() {
        if (!this.selectedNodeId) return null;
        return this.nodes.find(n => n.id === this.selectedNodeId) || null;
    }
}

window.store = new StudioStore();
