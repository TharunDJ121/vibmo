/**
 * Synchronized Web Audio API & HTML5 Audio Engine for Live Studio Playback.
 */

class StudioAudioEngine {
    constructor() {
        this.audioEl = new Audio();
        this.audioEl.src = "/api/audio";
        this.audioEl.preload = "auto";
        this.isLoaded = false;
        this.volume = 0.85;

        this.audioEl.oncanplaythrough = () => {
            this.isLoaded = true;
        };
    }

    play(startTime) {
        if (!this.isLoaded) return;
        this.audioEl.currentTime = startTime;
        this.audioEl.play().catch(() => {});
    }

    pause() {
        this.audioEl.pause();
    }

    seek(time) {
        if (this.isLoaded) {
            this.audioEl.currentTime = time;
        }
    }

    setVolume(val) {
        this.volume = Math.max(0, Math.min(1, val));
        this.audioEl.volume = this.volume;
    }
}

window.audioEngine = new StudioAudioEngine();
