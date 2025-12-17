import time
from utils.joystick_controller import JoystickController

from threading import Thread, Lock
import pygame


# 假设原有JoystickController类已导入

class ThreadedJoystickController(JoystickController):
    """修复数据刷新问题的带线程功能的手柄控制器"""

    def __init__(self, max_vel=2.0, max_ang_vel=2.0, update_interval=0.01):
        super().__init__(max_vel, max_ang_vel)

        self.update_interval = update_interval
        self.thread = None
        self.is_running = False
        # 添加锁以确保线程安全
        self.data_lock = Lock()

    def _thread_loop(self):
        """线程循环，持续更新数据"""
        # 确保Pygame在当前线程初始化
        pygame.init()
        pygame.joystick.init()

        if self.joystick:
            self.joystick.init()

        while self.is_running:
            with self.data_lock:  # 确保数据更新的原子性
                self.update()
            time.sleep(self.update_interval)

    def start(self):
        if not self.is_running and self.joystick:
            self.is_running = True
            self.thread = Thread(target=self._thread_loop)
            self.thread.start()
            print("手柄控制线程已启动")

    def stop(self):
        if self.is_running:
            self.is_running = False
            if self.thread:
                self.thread.join()
            print("手柄控制线程已停止")

    # 重写数据获取方法，添加线程锁
    def get_cmd(self):
        with self.data_lock:
            return super().get_cmd()

    def get_height(self):
        with self.data_lock:
            return super().get_height()

    def get_scramble(self):
        with self.data_lock:
            return super().get_scramble()


# 使用示例
if __name__ == "__main__":
    joystick = ThreadedJoystickController()

    if joystick.joystick:  # 检查手柄是否连接
        joystick.start()

        try:
            while True:
                cmd = joystick.get_cmd()
                height = joystick.get_height()
                scram = joystick.get_scramble()

                print(f"速度命令: {cmd}, 高度: {height}, 紧急停止: {scram}")
                time.sleep(0.1)

        except KeyboardInterrupt:
            print("\n程序退出")
        finally:
            joystick.stop()
            pygame.quit()

