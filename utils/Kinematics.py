import numpy as np

np.set_printoptions(suppress=True, precision=4)


def euler_to_rotation_matrix(yaw, pitch, roll):
    """
    将Z-Y-X顺序的欧拉角（弧度）转换为旋转矩阵
    :param yaw: 偏航角（绕Z轴），弧度
    :param pitch: 俯仰角（绕Y轴），弧度
    :param roll: 滚转角（绕X轴），弧度
    :return: 3x3旋转矩阵
    """

    # 计算三角函数值
    cy = np.cos(yaw)
    sy = np.sin(yaw)
    cp = np.cos(pitch)
    sp = np.sin(pitch)
    cr = np.cos(roll)
    sr = np.sin(roll)

    # 构建旋转矩阵（Z-Y-X顺序）
    R = np.array([
        [cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr],
        [sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr],
        [-sp, cp * sr, cp * cr]
    ])

    return R

class LegKinematics:
    def __init__(self):
        self.l_abcd = 0.077
        self.l_hip = 0.12
        self.l_knee_x = 0.044
        self.l_knee_z = 0.127
        self.l_knee = np.sqrt(self.l_knee_x ** 2 + self.l_knee_z ** 2)
        self.theta_knee = np.arctan2(self.l_knee_x, self.l_knee_z)
        self.dir = np.array([-1,1,1,-1,-1,-1,1,1,1,1,1,-1,-1])
        # self.p_3 = np.array([self.l_knee_x, 0, -self.l_knee_z, 1])
        self.fl_dir = np.concatenate([np.array([1, 1]), self.dir[7:10]])
        self.rl_dir = np.concatenate([np.array([1, -1]), self.dir[0:3]])
        self.fr_dir = np.concatenate([np.array([-1, 1]), self.dir[10:13]])
        self.rr_dir = np.concatenate([np.array([-1, -1]), self.dir[3:6]])
        # print("rl_dir:", self.rl_dir)
        # print("rr_dir:", self.rr_dir)
        # print("fl_dir:", self.fl_dir)
        # print("fr_dir:", self.fr_dir)

        # 逆解补偿 fl，rr = 1， fr, rl = -1 利用 dir[1] * dir[4]

    def forward_kinematics(self, theta, dir):
        a_1 = theta[0] * dir[2]
        a_2 = theta[1] * dir[3]
        a_3 = theta[2] * dir[4]
        l_1 = self.l_abcd * dir[0]
        l_2 = -self.l_hip
        p_3 = np.array([dir[1] * self.l_knee_x, 0, -self.l_knee_z, 1]).reshape(4, 1)
        t_01 = np.array([
            [1, 0, 0, 0],
            [0, np.cos(a_1), -np.sin(a_1), 0],
            [0, np.sin(a_1), np.cos(a_1), 0],
            [0, 0, 0, 1]
        ])
        t_12 = np.array([
            [np.cos(a_2), 0, np.sin(a_2), 0],
            [0, 1, 0, 0],
            [-np.sin(a_2), 0, np.cos(a_2), 0],
            [0, 0, 0, 1]
        ])
        t_23 = np.array([
            [np.cos(a_3), 0, np.sin(a_3), 0],
            [0, 1, 0, l_1],
            [-np.sin(a_3), 0, np.cos(a_3), l_2],
            [0, 0, 0, 1]
        ])
        p = t_01 @ t_12 @ t_23 @ p_3
        return p[:3].reshape(-1)

    def inverse_kinematics(self, target_pos, dir):
        l_1 = self.l_abcd * dir[0]
        l_2 = -self.l_hip
        l_3 = -self.l_knee
        o_3_a = self.l_hip
        o_3_p = self.l_knee
        a_p = np.sqrt(target_pos[0] ** 2 + target_pos[1] ** 2 + target_pos[2] ** 2 - l_1 ** 2)
        L = np.sqrt(target_pos[1] ** 2 + target_pos[2] ** 2 - l_1 ** 2)
        a_o_3_p = np.arccos((o_3_a ** 2 + o_3_p ** 2 - a_p ** 2) / (2 * o_3_p * o_3_a))

        ag_1 = np.arctan2(target_pos[2] * l_1 + target_pos[1] * L,
                          target_pos[1] * l_1 - target_pos[2] * L)

        ag_3 = (-np.pi + a_o_3_p) * dir[4] * dir[1] * dir[4]

        a_1 = target_pos[1] * np.sin(ag_1) - target_pos[2] * np.cos(ag_1)
        a_2 = target_pos[0]
        m_1 = l_3 * np.sin(ag_3)
        m_2 = l_3 * np.cos(ag_3) + l_2
        ag_2 = np.arctan2(a_1 * m_1 + a_2 * m_2, a_2 * m_1 - a_1 * m_2)

        x_1 = ag_1 * dir[2]
        x_2 = ag_2 * dir[3]
        x_3 = (ag_3 + self.theta_knee * dir[1]) * dir[4]  # fr

        theta = np.array([x_1, x_2, x_3])

        return theta

# 长379.4mm, 宽100mm
class BodyKinematics:
    def __init__(self, leg: LegKinematics):
        self.l = 0.3794
        self.d = 0.1
        self.leg = leg
        # self.fl_dir = np.array([1, 1])  # x方向， y方向
        # self.rl_dir = np.array([-1, 1])
        # self.fr_dir = np.array([1, -1])
        # self.rr_dir = np.array([-1, -1])

    def hip_point(self, waist_pos):
        # waist_pos为反馈值
        x = self.l * np.cos(waist_pos / 2) / 2
        y = self.d / 2
        fl_hip = np.array([x, y, 0.])
        fr_hip = np.array([x, -y, 0.])
        rl_hip = np.array([-x, y, 0.])
        rr_hip = np.array([-x, -y, 0.])
        return fl_hip, fr_hip, rl_hip, rr_hip

    def foot_point_body(self, q):
        # q为反馈值
        fl_pos = self.leg.forward_kinematics(q[7:10], self.leg.fl_dir)
        fr_pos = self.leg.forward_kinematics(q[10:13], self.leg.fr_dir)
        rl_pos = self.leg.forward_kinematics(q[0:3], self.leg.rl_dir)
        rr_pos = self.leg.forward_kinematics(q[3:6], self.leg.rr_dir)
        # print("pos:",fl_pos, fr_pos, rl_pos, rr_pos)
        fl_hip, fr_hip, rl_hip, rr_hip = self.hip_point(q[6])
        bd_fl = fl_pos + fl_hip
        bd_fr = fr_pos + fr_hip
        bd_rl = rl_pos + rl_hip
        bd_rr = rr_pos + rr_hip
        # return bd_rl, bd_rr, bd_fl, bd_fr
        return np.array([bd_rl, bd_rr, bd_fl, bd_fr]).reshape(-1)


dir = [ 1, -1, -1,  1,  1,
       -1, -1, -1, -1, -1,
        1,  1,  1,  1,  1,
       -1,  1,  1, -1, -1,]

import torch
class Test:
    def __init__(self):
        self.dir = [ 1, -1, -1,  1,  1,
                    -1, -1, -1, -1, -1,
                     1,  1,  1,  1,  1,
                    -1,  1,  1, -1, -1,]

        self.num_envs = 8
        self.device = torch.device('cpu')

    def foot_position_in_hip_frame(self, angles, i):
        dir = self.dir[i * 5:i * 5 + 5]
        l_1 = 0.077 * dir[0]
        l_2 = -0.12
        l_x = 0.044 * dir[1]
        l_z = -0.127

        a_1 = angles[:, 0] * dir[2]
        a_2 = angles[:, 1] * dir[3]
        a_3 = angles[:, 2] * dir[4]

        # 优化：减少冗余的三角函数计算
        cos_a3 = torch.cos(a_3)
        sin_a3 = torch.sin(a_3)
        p_1 = l_x * cos_a3 + l_z * sin_a3
        p_2 = l_1
        p_3 = l_2 + l_z * cos_a3 - l_x * sin_a3

        # 优化：减少冗余的三角函数计算
        cos_a2 = torch.cos(a_2)
        sin_a2 = torch.sin(a_2)
        p_x = p_1 * cos_a2 + p_3 * sin_a2
        p_y = p_2
        p_z = -p_1 * sin_a2 + p_3 * cos_a2

        # 优化：减少冗余的三角函数计算
        cos_a1 = torch.cos(a_1)
        sin_a1 = torch.sin(a_1)
        off_x = p_x
        off_y = p_y * cos_a1 - p_z * sin_a1
        off_z = p_y * sin_a1 + p_z * cos_a1
        return torch.stack([off_x, off_y, off_z], dim=-1)

    def foot_positions_in_base_frame(self, foot_angles):
        foot_positions = torch.zeros(self.num_envs, 12, dtype=torch.float16)
        waist = foot_angles[:, 6:7]
        dof_pos = torch.cat([foot_angles[:, :6], foot_angles[:, 7:]], dim=1)
        x = 0.3794 * torch.cos(waist / 2) / 2
        y = 0.05
        for i in range(4):
            foot_positions[:, i * 3:i * 3 + 3].copy_(
                self.foot_position_in_hip_frame(foot_angles[:, i * 3: i * 3 + 3], i))
        foot_positions[:, [0, 3]] -= x
        foot_positions[:, [4, 10]] -= y
        foot_positions[:, [6, 9]] += x
        foot_positions[:, [1, 7]] += y
        return foot_positions



if __name__ == '__main__':
    torch.set_printoptions(precision=5, sci_mode=False)

    leg = LegKinematics()
    p = leg.forward_kinematics(np.array([-0.1, -0.1, -0.1]), leg.fr_dir)
    q = leg.inverse_kinematics(p, leg.fl_dir)
    # print("pos:", p)
    # print("q:", q)
    body = BodyKinematics(leg)
    foot = body.foot_point_body(np.ones(13) * -1.2)
    # print(foot)
    foot_tensor = torch.from_numpy(foot)
    foot_8x13 = foot_tensor.repeat(8, 1)

    pos = torch.ones(8, 13) * -1.2

    test = Test()
    posx = test.foot_positions_in_base_frame(pos)

    torch_test = torch.sum(posx, dim=1)

    print(torch_test)

    print(posx)



