"""
启动GO2 Web可视化系统
同时启动WebSocket服务器和仿真程序
"""

import subprocess
import sys
import time
import os

def main():
    print("=" * 60)
    print("GO2 Web Visualizer - 启动中...")
    print("=" * 60)

    processes = []

    # 设置环境变量
    env = os.environ.copy()
    env['PYTHONPATH'] = os.getcwd()

    try:
        # 1. 启动WebSocket服务器
        print("\n[1/2] 启动WebSocket服务器...")
        server_process = subprocess.Popen(
            [sys.executable, "server/websocket_server.py"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        processes.append(("WebSocket服务器", server_process))
        time.sleep(2)  # 等待服务器启动

        # 2. 启动仿真程序
        print("[2/2] 启动仿真程序...")
        sim_process = subprocess.Popen(
            [sys.executable, "scripts/dreamwaq_go2_web.py"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        processes.append(("仿真程序", sim_process))

        print("\n" + "=" * 60)
        print("✓ 启动完成！")
        print("=" * 60)
        print("\n请打开浏览器访问: http://localhost:8000")
        print("\n按 Ctrl+C 停止所有进程\n")

        # 保持运行并显示输出
        while True:
            for name, proc in processes:
                if proc.poll() is not None:
                    print(f"\n[错误] {name} 已退出")
                    raise KeyboardInterrupt
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n\n正在停止所有进程...")
        for name, proc in processes:
            proc.terminate()
            print(f"  - 停止 {name}")

        # 等待进程结束
        for name, proc in processes:
            proc.wait(timeout=5)

        print("\n已停止所有进程")

    except Exception as e:
        print(f"\n[错误] {e}")
        for name, proc in processes:
            proc.terminate()
        sys.exit(1)

if __name__ == "__main__":
    main()
