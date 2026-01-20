/**
 * WebSocket Client Manager
 * Manages WebSocket connection to GO2 backend
 */

class WebSocketClient {
    constructor(serverUrl = 'ws://localhost:8000/ws') {
        this.url = serverUrl;
        this.ws = null;
        this.stateCallbacks = [];
        this.reconnectInterval = 1000;
        this.maxReconnectInterval = 10000;
        this.reconnectAttempts = 0;
        this.isConnecting = false;
        this.shouldReconnect = true;

        this.connect();
    }

    connect() {
        if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
            return;
        }

        this.isConnecting = true;
        console.log(`[WebSocket] Connecting to ${this.url}...`);

        try {
            this.ws = new WebSocket(this.url);

            this.ws.onopen = () => {
                console.log('[WebSocket] Connected!');
                this.isConnecting = false;
                this.reconnectAttempts = 0;
                this.reconnectInterval = 1000;
                this.notifyConnectionStatus(true);

                // Identify as web client
                this.ws.send(JSON.stringify({ type: 'web_connect' }));
            };

            this.ws.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data);

                    if (message.type === 'state') {
                        this.stateCallbacks.forEach(callback => {
                            try {
                                callback(message);
                            } catch (error) {
                                console.error('[WebSocket] Error in state callback:', error);
                            }
                        });
                    }
                } catch (error) {
                    console.error('[WebSocket] Error parsing message:', error);
                }
            };

            this.ws.onerror = (error) => {
                console.error('[WebSocket] Error:', error);
                this.isConnecting = false;
            };

            this.ws.onclose = () => {
                console.log('[WebSocket] Connection closed');
                this.isConnecting = false;
                this.notifyConnectionStatus(false);

                if (this.shouldReconnect) {
                    this.reconnectAttempts++;
                    const backoffInterval = Math.min(
                        this.reconnectInterval * Math.pow(1.5, this.reconnectAttempts),
                        this.maxReconnectInterval
                    );
                    console.log(`[WebSocket] Reconnecting in ${backoffInterval}ms...`);
                    setTimeout(() => this.connect(), backoffInterval);
                }
            };

        } catch (error) {
            console.error('[WebSocket] Connection error:', error);
            this.isConnecting = false;
        }
    }

    sendCommand(xVel, yVel, angVel) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            const message = {
                type: 'command',
                x_vel: xVel,
                y_vel: yVel,
                ang_vel: angVel
            };

            try {
                this.ws.send(JSON.stringify(message));
            } catch (error) {
                console.error('[WebSocket] Error sending command:', error);
            }
        }
    }

    onStateUpdate(callback) {
        this.stateCallbacks.push(callback);
    }

    notifyConnectionStatus(connected) {
        window.dispatchEvent(new CustomEvent('websocket-status', {
            detail: { connected }
        }));
    }

    disconnect() {
        this.shouldReconnect = false;
        if (this.ws) {
            this.ws.close();
        }
    }

    isConnected() {
        return this.ws && this.ws.readyState === WebSocket.OPEN;
    }
}
