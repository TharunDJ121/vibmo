/**
 * WebSocket Communication Layer with Automatic Backpressure and Request Queueing.
 */

class StudioSocket {
    constructor(onMessage) {
        this.onMessage = onMessage;
        this.inFlight = false;
        this.pendingTime = null;
        this.lastRequestedTime = -1;
        this.lastRequestStamp = 0;
        this.ws = null;
        this.connect();
    }

    connect() {
        const proto = location.protocol === "https:" ? "wss:" : "ws:";
        this.ws = new WebSocket(`${proto}//${location.host}/ws`);

        this.ws.onopen = () => {
            this.send({ type: "init" });
            this.requestFrame(0.0);
        };

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                // Clear flight lock on ANY message from server so we never deadlock
                this.inFlight = false;
                
                if (data.type === "frame") {
                    if (this.pendingTime !== null) {
                        const t = this.pendingTime;
                        this.pendingTime = null;
                        this.requestFrame(t);
                    }
                }
                if (this.onMessage) {
                    this.onMessage(data);
                }
            } catch (e) {
                console.error("WS Parse error", e);
            }
        };

        this.ws.onclose = () => {
            this.inFlight = false;
            setTimeout(() => this.connect(), 1000);
        };

        this.ws.onerror = () => {
            this.inFlight = false;
        };
    }

    send(data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            try {
                this.ws.send(JSON.stringify(data));
            } catch (_) {}
        }
    }

    requestFrame(t, scale = 0.5) {
        if (this.inFlight) {
            // Absolute safety net: if server vanished without error, reset lock after 1.5s
            if (this.lastRequestedTime !== -1 && (Date.now() - this.lastRequestStamp > 1500)) {
                this.inFlight = false;
            } else {
                this.pendingTime = t;
                return;
            }
        }

        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.inFlight = true;
            this.lastRequestedTime = t;
            this.lastRequestStamp = Date.now();
            this.send({
                type: "get_frame",
                time: t,
                scale: scale,
            });
        }
    }
}

window.StudioSocket = StudioSocket;
