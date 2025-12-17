import numpy as np
from scipy.spatial.transform import Rotation

def get_gravity_orientation(quaternion):
    qw = quaternion[0]
    qx = quaternion[1]
    qy = quaternion[2]
    qz = quaternion[3]

    gravity_orientation = np.zeros(3)

    gravity_orientation[0] = 2 * (-qz * qx + qw * qy)
    gravity_orientation[1] = -2 * (qz * qy + qw * qx)
    gravity_orientation[2] = 1 - 2 * (qw * qw + qz * qz)

    return gravity_orientation

def euler_to_projected_gravity(roll, pitch, yaw, g=1):
    """
    将欧拉角（滚转、俯仰、偏航）转换为 projected_gravity

    参数:
    roll (float): 滚转角（弧度）
    pitch (float): 俯仰角（弧度）
    yaw (float): 偏航角（弧度）
    g (float): 重力加速度，默认为 9.81 m/s^2

    返回:
    np.ndarray: projected_gravity 向量
    """
    # 构建绕 X 轴的旋转矩阵
    R_x = np.array([
        [1, 0, 0],
        [0, np.cos(roll), -np.sin(roll)],
        [0, np.sin(roll), np.cos(roll)]
    ])

    # 构建绕 Y 轴的旋转矩阵
    R_y = np.array([
        [np.cos(pitch), 0, np.sin(pitch)],
        [0, 1, 0],
        [-np.sin(pitch), 0, np.cos(pitch)]
    ])

    # 构建绕 Z 轴的旋转矩阵
    R_z = np.array([
        [np.cos(yaw), -np.sin(yaw), 0],
        [np.sin(yaw), np.cos(yaw), 0],
        [0, 0, 1]
    ])

    # 计算总的旋转矩阵
    R = np.dot(R_z, np.dot(R_y, R_x))

    # 定义重力向量
    g_vector = np.array([0, 0, -g])

    # 计算 projected_gravity
    projected_gravity = np.dot(R, g_vector)

    return projected_gravity

def linear_interpolation(now_pos, default_angles, num_steps):
    interpolation_points = np.zeros((num_steps + 1, len(now_pos)))
    interpolation_points[0] = now_pos
    step_size = (default_angles - now_pos) / num_steps
    for i in range(1, num_steps + 1):
        interpolation_points[i] = now_pos + i * step_size
    return interpolation_points

def _low_pass_action_filter(actions,last_actions):
    actions_filtered = last_actions * 0.2 + actions * 0.8
    return actions_filtered

# def quat_to_euler(q_wxyz):
#     """
#     输入:
#         q_wxyz - 形状 (4,) 的四元数，顺序 (w, x, y, z)
#     输出:
#         形状 (3,) 的欧拉角 (roll, pitch, yaw)（弧度）
#     """
#     # 调整顺序：scipy 要求 (x, y, z, w)
#     q_xyzw = q_wxyz[[1, 2, 3, 0]]  # (w,x,y,z) -> (x,y,z,w)
#
#     # 转换为欧拉角 (XYZ 顺序)
#     r = Rotation.from_quat(q_xyzw)
#     euler_xyz = r.as_euler('XYZ', degrees=False)  # 弧度
#
#     return euler_xyz  # (roll, pitch, yaw)

def quaternion_to_euler_array(quat):
    # Ensure quaternion is in the correct format [x, y, z, w]
    x, y, z, w = quat

    # Roll (x-axis rotation)
    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + y * y)
    roll_x = np.arctan2(t0, t1)

    # Pitch (y-axis rotation)
    t2 = +2.0 * (w * y - z * x)
    t2 = np.clip(t2, -1.0, 1.0)
    pitch_y = np.arcsin(t2)

    # Yaw (z-axis rotation)
    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (y * y + z * z)
    yaw_z = np.arctan2(t3, t4)

    # Returns roll, pitch, yaw in a NumPy array in radians
    return np.array([roll_x, pitch_y, yaw_z])
