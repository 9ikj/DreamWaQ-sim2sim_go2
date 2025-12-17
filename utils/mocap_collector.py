import numpy as np


def numpy_to_formatted_list(arr, decimals=5):
    """
    将 NumPy 数组转换为带有特定格式的字符串列表。
    """
    # 开始构建字符串
    formatted_str = "["

    # 遍历每一行
    for i, row in enumerate(arr):
        if i > 0:
            formatted_str += "  "  # 除了第一行，其他行前面加两个空格

        formatted_str += "["

        # 遍历行中的每个元素
        for j, elem in enumerate(row):
            # 格式化数字，保留指定小数位数
            formatted_str += f"{elem:.{decimals}f}"
            if j < len(row) - 1:
                formatted_str += ", "  # 元素之间加逗号和空格

        formatted_str += "]"
        if i < len(arr) - 1:
            formatted_str += ","  # 行之间加逗号

        formatted_str += "\n"  # 每行结束后换行

    formatted_str += "]"
    return formatted_str

class AMPCollector:
    def __init__(self, interval=0.02):
        self.data_list = []
        self.last_stack_time = 0
        self.interval = interval

    def amp_collector(self, t, pos, quat, q, foot_pos, vel, omega, dq, foot_vel):
        if t - self.last_stack_time > self.interval:
            data = np.concatenate([
                pos,
                quat,
                q,
                foot_pos,
                vel,
                omega,
                dq,
                foot_vel
            ])
            self.data_list.append(data)
            self.last_stack_time = t

    def get_data(self):
        data = np.array(self.data_list)
        print("shape of data:",data.shape)
        formatted_data = numpy_to_formatted_list(data)
        return formatted_data
