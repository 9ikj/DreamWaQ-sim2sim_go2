/**
 * Keyboard Handler
 * Handles keyboard input and sends commands to WebSocket
 */

class KeyboardHandler {
    constructor(wsClient) {
        this.wsClient = wsClient;
        this.activeKeys = new Set();
        this.commands = { x_vel: 0, y_vel: 0, ang_vel: 0 };

        this.keyMap = {
            'w': { axis: 'x_vel', value: 1.0 },
            'W': { axis: 'x_vel', value: 1.0 },
            's': { axis: 'x_vel', value: -1.0 },
            'S': { axis: 'x_vel', value: -1.0 },
            'a': { axis: 'y_vel', value: 1.0 },
            'A': { axis: 'y_vel', value: 1.0 },
            'd': { axis: 'y_vel', value: -1.0 },
            'D': { axis: 'y_vel', value: -1.0 },
            'q': { axis: 'ang_vel', value: 1.0 },
            'Q': { axis: 'ang_vel', value: 1.0 },
            'e': { axis: 'ang_vel', value: -1.0 },
            'E': { axis: 'ang_vel', value: -1.0 },
            'ArrowUp': { axis: 'x_vel', value: 1.0 },
            'ArrowDown': { axis: 'x_vel', value: -1.0 },
            'ArrowLeft': { axis: 'y_vel', value: 1.0 },
            'ArrowRight': { axis: 'y_vel', value: -1.0 }
        };

        this.setupEventListeners();
        console.log('[Keyboard] Handler initialized');
    }

    setupEventListeners() {
        window.addEventListener('keydown', (e) => this.onKeyDown(e));
        window.addEventListener('keyup', (e) => this.onKeyUp(e));
    }

    onKeyDown(event) {
        const key = event.key;

        if (!this.keyMap[key]) return;

        event.preventDefault();

        if (this.activeKeys.has(key)) return;

        this.activeKeys.add(key);
        this.updateCommands();
        this.updateUI();
    }

    onKeyUp(event) {
        const key = event.key;

        if (!this.keyMap[key]) return;

        event.preventDefault();

        this.activeKeys.delete(key);
        this.updateCommands();
        this.updateUI();
    }

    updateCommands() {
        this.commands = { x_vel: 0, y_vel: 0, ang_vel: 0 };

        for (const key of this.activeKeys) {
            const mapping = this.keyMap[key];
            if (mapping) {
                this.commands[mapping.axis] = mapping.value;
            }
        }

        this.wsClient.sendCommand(
            this.commands.x_vel,
            this.commands.y_vel,
            this.commands.ang_vel
        );
    }

    updateUI() {
        // Update active keys display
        const activeKeysContainer = document.getElementById('active-keys');
        if (activeKeysContainer) {
            if (this.activeKeys.size === 0) {
                activeKeysContainer.innerHTML = '<div class="no-keys text-gray-500 italic text-xs py-1.5">未按下任何键</div>';
            } else {
                const keyBadges = Array.from(this.activeKeys).map(key => {
                    const displayKey = key.replace('Arrow', '');
                    return `<span class="key-badge px-2 py-1 bg-[#e94560] text-white rounded text-xs font-bold">${displayKey}</span>`;
                }).join('');
                activeKeysContainer.innerHTML = keyBadges;
            }
        }

        // Highlight legend items
        document.querySelectorAll('.legend-item').forEach(item => {
            const key = item.dataset.key;
            if (key && (this.activeKeys.has(key) || this.activeKeys.has(key.toUpperCase()))) {
                item.classList.add('bg-[#e94560]/20', 'border-[#e94560]');
            } else {
                item.classList.remove('bg-[#e94560]/20', 'border-[#e94560]');
            }
        });

        // Update velocity display
        if (window.uiController) {
            window.uiController.updateVelocityDisplay(this.commands);
        }
    }
}
