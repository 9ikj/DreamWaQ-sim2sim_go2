/**
 * GO2 Web Visualizer - Main Application
 * Initializes and coordinates all modules
 */

let wsClient;
let renderer;
let keyboard;
let uiController;
let isInitialized = false;

async function init() {
    console.log('='.repeat(60));
    console.log('GO2 Web Visualizer - Starting...');
    console.log('='.repeat(60));

    try {
        // 1. Initialize UI Controller
        console.log('[Init] Creating UI Controller...');
        uiController = new UIController();
        window.uiController = uiController;

        // 2. Initialize WebSocket Client
        console.log('[Init] Connecting to WebSocket server...');
        const wsUrl = getWebSocketUrl();
        wsClient = new WebSocketClient(wsUrl);

        // 3. Initialize 3D Renderer
        console.log('[Init] Initializing 3D renderer...');
        renderer = new RobotRenderer('canvas-container');
        window.renderer = renderer;

        // Load robot model
        await renderer.loadRobotModel();

        // 4. Initialize Keyboard Handler
        console.log('[Init] Setting up keyboard handler...');
        keyboard = new KeyboardHandler(wsClient);

        // 5. Connect WebSocket state updates to renderer and UI
        wsClient.onStateUpdate((state) => {
            renderer.updateRobotState(state);
            uiController.updateStateDisplay(state);
        });

        isInitialized = true;

        console.log('='.repeat(60));
        console.log('GO2 Web Visualizer - Ready!');
        console.log('='.repeat(60));
        console.log('');
        console.log('Controls:');
        console.log('  W/S or ↑/↓  - Forward/Backward');
        console.log('  A/D or ←/→  - Left/Right');
        console.log('  Q/E         - Rotate');
        console.log('');
        console.log('WebSocket:', wsUrl);
        console.log('='.repeat(60));

        showWelcomeMessage();

    } catch (error) {
        console.error('[Init] Initialization error:', error);
        showErrorMessage('初始化失败: ' + error.message);
    }
}

function getWebSocketUrl() {
    const params = new URLSearchParams(window.location.search);
    const wsParam = params.get('ws');
    if (wsParam) {
        return wsParam;
    }
    return 'ws://localhost:8000/ws';
}

function showWelcomeMessage() {
    const messageElement = document.getElementById('status-message');
    if (messageElement) {
        messageElement.innerHTML = `
            <div class="bg-green-500/95 text-white border-2 border-green-400 rounded-lg p-6 text-center">
                <h3 class="text-xl font-bold mb-2">🤖 GO2 Web Visualizer</h3>
                <p class="text-sm mb-1">已连接！使用 WASD 或方向键控制机器人。</p>
            </div>
        `;
        messageElement.classList.remove('hidden');
        setTimeout(() => {
            messageElement.classList.add('hidden');
        }, 5000);
    }
}

function showErrorMessage(message) {
    const messageElement = document.getElementById('status-message');
    if (messageElement) {
        messageElement.innerHTML = `
            <div class="bg-red-500/95 text-white border-2 border-red-400 rounded-lg p-6 text-center">
                <h3 class="text-xl font-bold mb-2">❌ 错误</h3>
                <p class="text-sm">${message}</p>
            </div>
        `;
        messageElement.classList.remove('hidden');
    }
}

window.addEventListener('beforeunload', () => {
    console.log('[Main] Cleaning up...');
    if (wsClient) wsClient.disconnect();
    if (renderer) renderer.dispose();
});

document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        console.log('[Main] Page hidden - pausing...');
    } else {
        console.log('[Main] Page visible - resuming...');
    }
});

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
