import pygame
import numpy as np
import time
from multiprocessing import Process, Queue
import atexit

class JoystickController:
    """手柄控制器类，用于监听手柄输入并控制速度变量"""

    def __init__(self, max_vel=2.0, max_ang_vel=2.0):
        """初始化手柄控制器
        """
        self.max_vel = max_vel
        self.max_ang_vel = max_ang_vel

        # 速度变量
        self.x_vel = 0.0
        self.y_vel = 0.0
        self.ang_vel = 0.0

        self.height = int(0)

        # 特殊功能标志
        self.scram = False
        self.running = False

        self.waist_switch = False
        self.waist_range = 1.0

        # 死区阈值，防止摇杆中心漂移
        self.deadzone = 0.1

        # 手柄相关变量
        self.joystick = None

        # 初始化pygame
        pygame.init()
        # pygame.joystick.init()

        if pygame.joystick.get_count() == 0:
            print("未检测到手柄，请连接手柄后重试")
            return
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        print("connected!!")
        print(f"已连接手柄: {self.joystick.get_name()}")
        print(f"按钮数量: {self.joystick.get_numbuttons()}")

        # 注册程序退出时的清理函数
        # atexit.register(self.stop)

    def update(self):
        """更新速度值，内部循环函数"""
        pygame.event.get()
        self.scram = self.joystick.get_button(5)
        self.waist_switch = self.joystick.get_button(4)
        x_axis = -self.joystick.get_axis(1)
        y_axis = -self.joystick.get_axis(0)
        yaw_axis = -self.joystick.get_axis(2)

        if self.joystick.get_button(0):
            self.height += 1
        elif self.joystick.get_button(3):
            self.height -= 1
        if self.height < 0:
            self.height = 0
        elif self.height > 299:
            self.height = 299

        if abs(x_axis) < self.deadzone:
            self.x_vel = 0.0
        else:
            self.x_vel = x_axis * self.max_vel

        if abs(y_axis) < self.deadzone:
            self.y_vel = 0.0
        else:
            self.y_vel = y_axis * self.max_vel

        if abs(yaw_axis) < self.deadzone:
            self.ang_vel = 0.0
        else:
            self.ang_vel = yaw_axis * self.max_ang_vel

    def get_scramble(self):
        return self.scram

    def get_cmd(self):
        cmd = np.array([self.x_vel, self.y_vel, self.ang_vel])
        return cmd

    def get_height(self):
        return self.height

    def get_switch(self):
        return self.waist_switch


# 新增的带进程功能的控制器类
class ProcessedJoystickController:
    """带进程的手柄控制器，将更新循环放入独立进程"""

    def __init__(self, max_vel=2.0, max_ang_vel=2.0):
        self.max_vel = max_vel
        self.max_ang_vel = max_ang_vel
        self.data_queue = Queue()  # 用于进程间通信的队列
        self.process = None
        self.running = False
        self.last_data = (False, np.array([0.0, 0.0, 0.0]), 0)

        # 注册退出处理函数，确保进程正确终止
        atexit.register(self.stop)

    def _update_loop(self):
        """在独立进程中运行的更新循环 - 在这里初始化手柄"""
        # 在子进程中创建控制器实例，确保pygame和手柄在子进程中初始化
        controller = JoystickController(self.max_vel, self.max_ang_vel)

        self.running = True
        while self.running:
            controller.update()
            # 将数据放入队列，格式: (scram, cmd, height)
            data = (
                controller.get_scramble(),
                controller.get_cmd(),
                controller.get_height(),
                controller.get_switch()
            )
            # 确保队列中始终是最新数据
            if not self.data_queue.empty():
                try:
                    self.data_queue.get_nowait()
                except:
                    pass
            self.data_queue.put(data)
            time.sleep(0.02)  # 控制更新频率

    def start(self):
        """启动更新进程"""
        if self.process is None or not self.process.is_alive():
            self.process = Process(target=self._update_loop, daemon=True)
            self.process.start()
            print("手柄更新进程已启动")

    def stop(self):
        """停止更新进程"""
        self.running = False
        if self.process is not None and self.process.is_alive():
            self.process.join(timeout=1.0)
            print("手柄更新进程已停止")

    def get_data(self):
        """获取最新的手柄数据，如果队列为空则返回上一次的值"""
        if not self.data_queue.empty():
            # 如果队列中有数据，更新最后一次数据并返回
            self.last_data = self.data_queue.get()
        # 无论队列是否为空，都返回最后一次数据
        return self.last_data


# 使用示例
if __name__ == "__main__":
    # 创建带进程的控制器实例
    processed_controller = ProcessedJoystickController()

    try:
        # 启动更新进程
        processed_controller.start()
        print("please wait for Joystick process")
        time.sleep(2.5)

        # 主循环中获取数据
        while True:
            scram, cmd, height, sw = processed_controller.get_data()
            print(f"高度: {height}, 速度指令: {cmd}, 紧急停止: {sw}")
            time.sleep(0.01)  # 主进程的处理频率可以不同于更新频率
    except KeyboardInterrupt:
        print("程序被用户中断")
    finally:
        # 确保进程正确停止
        processed_controller.stop()


