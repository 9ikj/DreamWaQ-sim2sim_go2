from pynput import keyboard
import numpy as np
import threading
import atexit


class KeyboardController:
    """键盘控制器类，用于监听键盘输入并控制速度变量"""

    def __init__(self, max_vel=1.0):
        """初始化键盘控制器

        Args:
            max_vel: 最大速度值，默认为1.0
        """
        self.max_vel = max_vel
        self.x_vel = 0
        self.y_vel = 0
        self.ang_vel = 0
        self.scram = False
        # self.spin = False
        self.listener = None
        self.listener_thread = None
        self.running = False

        # 注册程序退出时的清理函数
        atexit.register(self.stop)

    def on_key_press(self, key):
        """按键按下时的处理函数"""
        if key == keyboard.Key.up:
            self.x_vel = self.max_vel
        elif key == keyboard.Key.down:
            self.x_vel = -self.max_vel
        elif key == keyboard.Key.left:
            self.y_vel = self.max_vel
        elif key == keyboard.Key.right:
            self.y_vel = -self.max_vel
        elif key == keyboard.KeyCode(char='q'):
            self.ang_vel = self.max_vel
        elif key == keyboard.KeyCode(char='e'):
            self.ang_vel = -self.max_vel

        # elif key == keyboard.Key.shift_l:
        #     self.spin = True

        elif key == keyboard.Key.space:
            self.scram = True

    def on_key_release(self, key):
        """按键释放时的处理函数"""
        if key in [keyboard.Key.up, keyboard.Key.down]:
            self.x_vel = 0
        elif key in [keyboard.Key.left, keyboard.Key.right]:
            self.y_vel = 0
        elif key == keyboard.KeyCode(char='q') or key == keyboard.KeyCode(char='e'):
            self.ang_vel = 0

        # elif key == keyboard.Key.shift_l:
        #     self.spin = False

        if key == keyboard.Key.f1:
            # 按下ESC键停止监听
            self.stop()
            return False

    def start_listening(self):
        """开始监听键盘输入"""
        if self.running:
            return

        self.running = True
        self.listener = keyboard.Listener(on_press=self.on_key_press,
                                          on_release=self.on_key_release)
        self.listener_thread = threading.Thread(target=self.listener.start)
        self.listener_thread.daemon = True
        self.listener_thread.start()

    def stop(self):
        """停止键盘监听"""
        if not self.running:
            return

        self.running = False
        if self.listener:
            self.listener.stop()
        if self.listener_thread and self.listener_thread.is_alive():
            self.listener_thread.join(timeout=1.0)

    def get_velocities(self):
        """获取当前速度值

        Returns:
            (x_vel, y_vel, ang_vel) - 当前的速度值元组
        """
        cmd = np.array([self.x_vel, self.y_vel, self.ang_vel])
        return cmd

    def get_scramble(self):
        return self.scram


# 以下为模块测试代码，仅在直接运行模块时执行
if __name__ == "__main__":
    import time

    print("键盘控制器模块测试开始...")
    print("使用方向键控制速度，按ESC键退出")

    # 创建键盘控制器实例
    controller = KeyboardController(max_vel=0.5)

    # 开始监听
    controller.start_listening()

    while True:
        # cmd = controller.get_velocities()
        # print(f"当前速度: cmd")
        scram = controller.get_scramble()
        print(scram)
        time.sleep(0.1)

