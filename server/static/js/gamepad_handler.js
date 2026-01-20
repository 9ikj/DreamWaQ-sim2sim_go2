/**
 * Gamepad Handler
 * Handles gamepad/controller input and sends commands to WebSocket
 *
 * Standard gamepad mapping:
 * - Left stick: Forward/Backward (Y-axis) and Left/Right strafe (X-axis)
 * - Right stick: Rotation (X-axis)
 * - Triggers/Buttons: Reserved for future use
 */

class GamepadHandler {
    constructor(wsClient) {
        this.wsClient = wsClient;
        this.gamepad = null;
        this.gamepadIndex = null;
        this.isActive = false;
        this.commands = { x_vel: 0, y_vel: 0, ang_vel: 0 };

        // Configuration
        this.config = {
            deadzone: 0.15,           // Ignore small stick movements
            maxVelocity: 1.0,         // Maximum velocity command
            updateRate: 50,           // Update rate in Hz (20ms)
            axisMapping: {
                leftStickX: 0,        // Left/Right strafe
                leftStickY: 1,        // Forward/Backward
                rightStickX: 2,       // Rotation
                rightStickY: 3        // Reserved
            }
        };

        this.updateInterval = null;
        this.lastUpdateTime = 0;

        this.setupEventListeners();
        console.log('[Gamepad] Handler initialized');
    }

    setupEventListeners() {
        window.addEventListener('gamepadconnected', (e) => this.onGamepadConnected(e));
        window.addEventListener('gamepaddisconnected', (e) => this.onGamepadDisconnected(e));

        // Start polling for gamepad state
        this.startPolling();
    }

    onGamepadConnected(event) {
        console.log('[Gamepad] Connected:', event.gamepad.id);
        this.gamepad = event.gamepad;
        this.gamepadIndex = event.gamepad.index;
        this.isActive = true;

        // Update UI
        this.updateConnectionStatus(true, event.gamepad.id);

        // Show notification
        this.showNotification(`手柄已连接: ${event.gamepad.id}`, 'success');
    }

    onGamepadDisconnected(event) {
        console.log('[Gamepad] Disconnected:', event.gamepad.id);

        if (this.gamepadIndex === event.gamepad.index) {
            this.gamepad = null;
            this.gamepadIndex = null;
            this.isActive = false;

            // Send zero commands
            this.commands = { x_vel: 0, y_vel: 0, ang_vel: 0 };
            this.sendCommands();

            // Update UI
            this.updateConnectionStatus(false);
            this.showNotification('手柄已断开', 'warning');
        }
    }

    startPolling() {
        // Use requestAnimationFrame for smooth updates
        const poll = () => {
            this.pollGamepad();
            requestAnimationFrame(poll);
        };
        requestAnimationFrame(poll);
    }

    pollGamepad() {
        if (!this.isActive || this.gamepadIndex === null) {
            return;
        }

        // Get latest gamepad state
        const gamepads = navigator.getGamepads();
        this.gamepad = gamepads[this.gamepadIndex];

        if (!this.gamepad) {
            return;
        }

        // Throttle updates to configured rate
        const now = performance.now();
        if (now - this.lastUpdateTime < 1000 / this.config.updateRate) {
            return;
        }
        this.lastUpdateTime = now;

        // Read axes
        const axes = this.gamepad.axes;
        const buttons = this.gamepad.buttons;

        // Apply deadzone and map to commands
        const leftX = this.applyDeadzone(axes[this.config.axisMapping.leftStickX]);
        const leftY = this.applyDeadzone(axes[this.config.axisMapping.leftStickY]);
        const rightX = this.applyDeadzone(axes[this.config.axisMapping.rightStickX]);

        // Map to robot commands
        // Note: Y-axis is inverted (up is negative)
        this.commands.x_vel = -leftY * this.config.maxVelocity;  // Forward/Backward
        this.commands.y_vel = -leftX * this.config.maxVelocity;  // Left/Right strafe
        this.commands.ang_vel = -rightX * this.config.maxVelocity; // Rotation

        // Send commands
        this.sendCommands();

        // Update UI
        this.updateUI();
    }

    applyDeadzone(value) {
        if (Math.abs(value) < this.config.deadzone) {
            return 0;
        }
        // Scale the remaining range to 0-1
        const sign = Math.sign(value);
        const magnitude = Math.abs(value);
        return sign * (magnitude - this.config.deadzone) / (1 - this.config.deadzone);
    }

    sendCommands() {
        // Only send if gamepad is active
        if (!this.isActive) {
            return;
        }

        this.wsClient.sendCommand(
            this.commands.x_vel,
            this.commands.y_vel,
            this.commands.ang_vel
        );
    }

    updateUI() {
        // Update gamepad status display
        const statusElement = document.getElementById('gamepad-status');
        if (statusElement && this.gamepad) {
            const hasInput = Math.abs(this.commands.x_vel) > 0.01 ||
                           Math.abs(this.commands.y_vel) > 0.01 ||
                           Math.abs(this.commands.ang_vel) > 0.01;

            statusElement.innerHTML = `
                <div class="text-xs space-y-1">
                    <div class="flex justify-between">
                        <span class="text-gray-400">前后:</span>
                        <span class="font-mono ${hasInput ? 'text-green-400' : 'text-gray-500'}">${this.commands.x_vel.toFixed(2)}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-400">左右:</span>
                        <span class="font-mono ${hasInput ? 'text-green-400' : 'text-gray-500'}">${this.commands.y_vel.toFixed(2)}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-400">旋转:</span>
                        <span class="font-mono ${hasInput ? 'text-green-400' : 'text-gray-500'}">${this.commands.ang_vel.toFixed(2)}</span>
                    </div>
                </div>
            `;
        }

        // Update velocity display in UI controller
        if (window.uiController && this.isActive) {
            window.uiController.updateVelocityDisplay(this.commands);
        }
    }

    updateConnectionStatus(connected, gamepadId = '') {
        const container = document.getElementById('gamepad-connection');
        if (!container) return;

        if (connected) {
            container.innerHTML = `
                <div class="flex items-center justify-between">
                    <div class="flex items-center gap-2">
                        <span class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                        <span class="text-xs text-green-400 font-semibold">已连接</span>
                    </div>
                </div>
                <div class="text-[10px] text-gray-500 mt-1 truncate" title="${gamepadId}">${gamepadId}</div>
            `;
        } else {
            container.innerHTML = `
                <div class="flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full bg-gray-600"></span>
                    <span class="text-xs text-gray-500">未连接</span>
                </div>
                <div class="text-[10px] text-gray-600 mt-1">请连接游戏手柄</div>
            `;
        }
    }

    showNotification(message, type = 'info') {
        const messageElement = document.getElementById('status-message');
        if (!messageElement) return;

        const colors = {
            success: 'bg-green-500/95 border-green-400',
            warning: 'bg-yellow-500/95 border-yellow-400',
            error: 'bg-red-500/95 border-red-400',
            info: 'bg-blue-500/95 border-blue-400'
        };

        const icons = {
            success: '✓',
            warning: '⚠',
            error: '✗',
            info: 'ℹ'
        };

        messageElement.innerHTML = `
            <div class="${colors[type]} text-white border-2 rounded-lg p-4 text-center">
                <span class="text-2xl mr-2">${icons[type]}</span>
                <span class="text-sm font-semibold">${message}</span>
            </div>
        `;
        messageElement.classList.remove('hidden');

        setTimeout(() => {
            messageElement.classList.add('hidden');
        }, 3000);
    }

    // Public methods
    isConnected() {
        return this.isActive && this.gamepad !== null;
    }

    getGamepadInfo() {
        if (!this.gamepad) return null;
        return {
            id: this.gamepad.id,
            index: this.gamepad.index,
            axes: this.gamepad.axes.length,
            buttons: this.gamepad.buttons.length
        };
    }

    setDeadzone(value) {
        this.config.deadzone = Math.max(0, Math.min(1, value));
        console.log('[Gamepad] Deadzone set to:', this.config.deadzone);
    }

    setMaxVelocity(value) {
        this.config.maxVelocity = Math.max(0, Math.min(2, value));
        console.log('[Gamepad] Max velocity set to:', this.config.maxVelocity);
    }
}
