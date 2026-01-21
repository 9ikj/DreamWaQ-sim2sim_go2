/**
 * UI Controller
 * Manages UI updates and performance monitoring
 */

class UIController {
    constructor() {
        this.frameCount = 0;
        this.lastFpsUpdate = Date.now();
        this.stateUpdateCount = 0;
        this.lastStateUpdate = Date.now();
        this.latencySum = 0;
        this.latencyCount = 0;

        this.setupConnectionStatusListener();
        this.startPerformanceMonitoring();
        console.log('[UI] Controller initialized');
    }

    setupConnectionStatusListener() {
        window.addEventListener('websocket-status', (event) => {
            const connected = event.detail.connected;
            this.updateConnectionStatus(connected);
        });
    }

    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('connection-status');
        if (!statusElement) return;

        if (connected) {
            statusElement.className = 'mx-3 my-2 px-4 py-2 rounded-md font-semibold text-sm text-center flex items-center justify-center gap-2 bg-green-900/20 border-2 border-green-500 text-green-500';
            statusElement.innerHTML = '<span class="status-indicator w-3 h-3 rounded-full bg-green-500 inline-block"></span>已连接';
        } else {
            statusElement.className = 'mx-3 my-2 px-4 py-2 rounded-md font-semibold text-sm text-center flex items-center justify-center gap-2 bg-red-900/20 border-2 border-red-500 text-red-500';
            statusElement.innerHTML = '<span class="status-indicator w-3 h-3 rounded-full bg-red-500 inline-block"></span>连接中...';
        }
    }

    startPerformanceMonitoring() {
        setInterval(() => {
            const now = Date.now();
            const elapsed = (now - this.lastFpsUpdate) / 1000;

            if (elapsed > 0) {
                const fps = Math.round(this.frameCount / elapsed);
                this.updateFpsDisplay(fps);
                this.frameCount = 0;
                this.lastFpsUpdate = now;
            }

            const stateElapsed = (now - this.lastStateUpdate) / 1000;
            if (stateElapsed > 0) {
                const stateHz = Math.round(this.stateUpdateCount / stateElapsed);
                this.updateStateHzDisplay(stateHz);
                this.stateUpdateCount = 0;
                this.lastStateUpdate = now;
            }

            if (this.latencyCount > 0) {
                const avgLatency = Math.round(this.latencySum / this.latencyCount);
                this.updateLatencyDisplay(avgLatency);
                this.latencySum = 0;
                this.latencyCount = 0;
            }
        }, 1000);
    }

    incrementFrameCount() {
        this.frameCount++;
    }

    updateFpsDisplay(fps) {
        const fpsElement = document.querySelector('#fps-display .perf-value');
        if (fpsElement) {
            fpsElement.textContent = fps;
            fpsElement.className = `perf-value font-mono text-sm font-bold ${fps >= 50 ? 'text-green-400' : fps >= 30 ? 'text-yellow-400' : 'text-red-400'}`;
        }
    }

    updateStateHzDisplay(hz) {
        const hzElement = document.querySelector('#state-hz-display .perf-value');
        if (hzElement) {
            hzElement.textContent = `${hz} Hz`;
            hzElement.className = `perf-value font-mono text-sm font-bold ${hz >= 15 ? 'text-green-400' : hz >= 10 ? 'text-yellow-400' : 'text-red-400'}`;
        }
    }

    updateLatencyDisplay(latency) {
        const latencyElement = document.querySelector('#latency-display .perf-value');
        if (latencyElement) {
            latencyElement.textContent = `${latency} ms`;
            latencyElement.className = `perf-value font-mono text-sm font-bold ${latency <= 50 ? 'text-green-400' : latency <= 100 ? 'text-yellow-400' : 'text-red-400'}`;
        }
    }

    updateStateDisplay(state) {
        this.stateUpdateCount++;

        if (state.timestamp) {
            const latency = Date.now() - state.timestamp;
            this.latencySum += latency;
            this.latencyCount++;
        }

        // Update joint table
        if (state.joint_pos && state.joint_names) {
            this.updateJointTable(state.joint_names, state.joint_pos, state.joint_vel);
        }

        // Update base state
        if (state.base_pos && state.base_quat) {
            this.updateBaseState(state.base_pos, state.base_quat);
        }
    }

    updateJointTable(jointNames, jointPos, jointVel) {
        const tbody = document.getElementById('joint-table-body');
        if (!tbody) return;

        let html = '';
        for (let i = 0; i < jointNames.length && i < jointPos.length; i++) {
            const angle = (jointPos[i] * 180 / Math.PI).toFixed(1);
            // 将弧度/秒转换为度/秒，并保留1位小数
            const vel = jointVel && jointVel[i] !== undefined ? (jointVel[i] * 180 / Math.PI).toFixed(1) : '--';
            html += `
                <tr class="border-b border-[#2a2a3e] hover:bg-[#0f3460]/30">
                    <td class="px-2 py-1 text-gray-300">${jointNames[i]}</td>
                    <td class="px-2 py-1 font-mono text-[#53a8b6]">${angle}°</td>
                    <td class="px-2 py-1 font-mono text-gray-400">${vel}°/s</td>
                </tr>
            `;
        }
        tbody.innerHTML = html;
    }

    updateBaseState(pos, quat) {
        const baseStateElement = document.getElementById('base-state');
        if (!baseStateElement) return;

        const html = `
            <div class="space-y-1">
                <div class="flex justify-between py-1 border-b border-[#2a2a3e]">
                    <span class="text-gray-400">位置 X:</span>
                    <span class="font-mono text-[#53a8b6]">${pos[0].toFixed(3)} m</span>
                </div>
                <div class="flex justify-between py-1 border-b border-[#2a2a3e]">
                    <span class="text-gray-400">位置 Y:</span>
                    <span class="font-mono text-[#53a8b6]">${pos[1].toFixed(3)} m</span>
                </div>
                <div class="flex justify-between py-1">
                    <span class="text-gray-400">位置 Z:</span>
                    <span class="font-mono text-[#53a8b6]">${pos[2].toFixed(3)} m</span>
                </div>
            </div>
        `;
        baseStateElement.innerHTML = html;
    }

    updateVelocityDisplay(commands) {
        // This can be extended to show velocity commands in UI
    }
}
