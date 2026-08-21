/**
 * Vibmo Studio Pro - In-Studio Python Script Editor & Hot Reloader.
 */

class ScriptEditorManager {
    constructor() {
        this.backdrop = document.getElementById("scriptModalBackdrop");
        this.editor = document.getElementById("scriptCodeEditor");
        this.templateSelect = document.getElementById("scriptTemplateSelect");
        this.promptInput = document.getElementById("promptInput");
        this.generatePromptBtn = document.getElementById("generatePromptBtn");
        this.runBtn = document.getElementById("runScriptBtn");
        this.saveBtn = document.getElementById("saveScriptBtn");
        this.revertBtn = document.getElementById("revertScriptBtn");
        this.closeBtn = document.getElementById("closeScriptModalBtn");
        this.openBtn = document.getElementById("openScriptModalBtn");
        this.consoleBox = document.getElementById("scriptConsoleBox");
        this.statusBadge = document.getElementById("scriptStatusBadge");

        this.originalCode = "";
        this.init();
    }

    init() {
        if (!this.backdrop || !this.editor) return;

        // Open & Close bindings
        this.openBtn.addEventListener("click", () => this.open());
        this.closeBtn.addEventListener("click", () => this.close());
        this.backdrop.addEventListener("click", (e) => {
            if (e.target === this.backdrop) this.close();
        });

        // Run / Save / Revert bindings
        this.runBtn.addEventListener("click", () => this.runScript());
        this.saveBtn.addEventListener("click", () => this.saveScript());
        this.revertBtn.addEventListener("click", () => {
            this.editor.value = this.originalCode;
            this.showConsole("Reverted to original script code", "success");
        });

        // Template selection
        this.templateSelect.addEventListener("change", (e) => {
            const val = e.target.value;
            if (!val) return;
            const tmpl = this.templates.find(t => t.id === val);
            if (tmpl) {
                this.editor.value = tmpl.code;
                this.showConsole(`Loaded template: ${tmpl.name}`, "success");
            }
        });

        // Text-to-Motion prompt generator
        this.generatePromptBtn.addEventListener("click", () => this.generateFromPrompt());
        this.promptInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter") this.generateFromPrompt();
        });

        // Tab key support in textarea
        this.editor.addEventListener("keydown", (e) => {
            if (e.key === "Tab") {
                e.preventDefault();
                const start = this.editor.selectionStart;
                const end = this.editor.selectionEnd;
                this.editor.value = this.editor.value.substring(0, start) + "    " + this.editor.value.substring(end);
                this.editor.selectionStart = this.editor.selectionEnd = start + 4;
            } else if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
                e.preventDefault();
                this.runScript();
            }
        });

        // Global shortcut Ctrl+E to toggle editor
        window.addEventListener("keydown", (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "e") {
                e.preventDefault();
                if (this.isOpen()) this.close();
                else this.open();
            }
        });

        // Fetch initial script and templates
        this.fetchScript();
        this.fetchTemplates();
    }

    isOpen() {
        return this.backdrop.classList.contains("open");
    }

    open() {
        this.backdrop.classList.add("open");
        this.fetchScript();
        this.editor.focus();
    }

    close() {
        this.backdrop.classList.remove("open");
    }

    async fetchScript() {
        try {
            const res = await fetch("/api/script");
            const data = await res.json();
            this.editor.value = data.code || "";
            this.originalCode = data.code || "";
            if (data.script_path) {
                this.statusBadge.textContent = data.script_path.split(/[\\/]/).pop();
            } else {
                this.statusBadge.textContent = "Live Dynamic Scene";
            }
        } catch (e) {
            console.error("Failed to fetch script", e);
        }
    }

    async fetchTemplates() {
        try {
            const res = await fetch("/api/templates");
            const data = await res.json();
            this.templates = data.templates || [];
            this.templateSelect.innerHTML = '<option value="">✦ Choose a Template...</option>';
            this.templates.forEach(t => {
                const opt = document.createElement("option");
                opt.value = t.id;
                opt.textContent = `${t.name} — ${t.description}`;
                this.templateSelect.appendChild(opt);
            });
        } catch (e) {
            console.error("Failed to fetch templates", e);
        }
    }

    async runScript() {
        const code = this.editor.value;
        this.runBtn.textContent = "⚡ Running...";
        this.runBtn.disabled = true;

        try {
            const res = await fetch("/api/script/run", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ code }),
            });
            const data = await res.json();

            if (res.ok && data.success) {
                this.showConsole(`✓ Scene compiled and reloaded successfully! (Duration: ${data.meta.duration}s, ${data.meta.nodes.length} nodes)`, "success");
                // Re-request frame at current playhead via WS
                if (window.socket) {
                    window.socket.send({ type: "run_script", code: code });
                }
            } else {
                this.showConsole(data.error || "Unknown compilation error", "error");
            }
        } catch (e) {
            this.showConsole(`Network error: ${e.message}`, "error");
        } finally {
            this.runBtn.textContent = "▶ Run & Hot Reload (Ctrl+Enter)";
            this.runBtn.disabled = false;
        }
    }

    async saveScript() {
        const code = this.editor.value;
        try {
            const res = await fetch("/api/script/save", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ code }),
            });
            const data = await res.json();
            if (data.success) {
                this.showConsole(`✓ Script saved to ${data.path}`, "success");
            }
        } catch (e) {
            this.showConsole(`Save failed: ${e.message}`, "error");
        }
    }

    async generateFromPrompt() {
        const prompt = this.promptInput.value.trim();
        if (!prompt) return;

        this.generatePromptBtn.textContent = "Synthesizing...";
        this.generatePromptBtn.disabled = true;

        try {
            const res = await fetch("/api/prompt/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ prompt, duration: 4.0 }),
            });
            const data = await res.json();
            if (res.ok && data.success) {
                await this.fetchScript();
                this.showConsole(`✓ Synthesized scene from prompt: "${prompt}"`, "success");
                if (window.socket && window.store) {
                    window.seekTo(0.0);
                }
            } else {
                this.showConsole(data.detail || "Prompt synthesis failed", "error");
            }
        } catch (e) {
            this.showConsole(`Prompt synthesis error: ${e.message}`, "error");
        } finally {
            this.generatePromptBtn.textContent = "✨ Generate";
            this.generatePromptBtn.disabled = false;
        }
    }

    showConsole(msg, type) {
        this.consoleBox.textContent = msg;
        this.consoleBox.className = `script-console ${type}`;
    }
}

document.addEventListener("DOMContentLoaded", () => {
    window.scriptEditor = new ScriptEditorManager();
});
