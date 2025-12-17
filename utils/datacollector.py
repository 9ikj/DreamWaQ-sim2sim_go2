import numpy as np

# 用列表暂存数据（append高效）
# data_list = []
# total_cycles = 10
# data_dim = 10
#
# start_time = time.time()
# for i in range(total_cycles):
#     new_data = np.random.randn(data_dim)  # 示例数据
#     data_list.append(new_data)  # 列表append无复制，极快
# # 循环结束后，一次性转成NumPy数组（仅1次复制）
# stacked_data = np.array(data_list)
# end_time = time.time()
#
# print(f"循环+转数组耗时：{end_time - start_time:.2f}秒")  # 10万次≈0.2~0.5秒
#
# # 保存
# save_path = "../logs/large_data_list.csv"
# os.makedirs(os.path.dirname(save_path), exist_ok=True)
# np.savetxt(save_path,
#            stacked_data,
#            delimiter=',',
#            fmt='%.2g')

# np.savetxt(
#     full_path,
#     stacked_data,
#     delimiter=',',
#     fmt=['%.3g', '%.2f', '%.5g'],  # 列表长度需与数据列数一致
#     header='col1,col2,col3',
#     comments=''
# )


class DataCollector:
    def __init__(self, interval=0.1):
        self.data_list = []
        self.last_stack_time = 0
        self.interval = interval

    def base_collector(self, t, cmd, omega, euler, q, dq, action, target_q, power):
        if t - self.last_stack_time > self.interval:
            data = np.concatenate([
                np.array([t]),
                cmd,
                omega,
                euler,
                q,
                dq,
                action,
                target_q,
                np.array([power])
            ])
            self.data_list.append(data)
            self.last_stack_time = t

    def sim_collector(self, t, xyz_vel, cmd, omega, euler, q, dq, action, target_q, power, phase):
        if t - self.last_stack_time > self.interval:
            data = np.concatenate([
                np.array([t]),
                cmd,
                xyz_vel,
                omega,
                euler,
                q,
                dq,
                action,
                target_q,
                np.array([power]),
                np.array([phase]),
            ])
            self.data_list.append(data)
            self.last_stack_time = t

    def get_data(self):
        return np.array(self.data_list)
