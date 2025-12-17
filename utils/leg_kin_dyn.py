import numpy as np
import pinocchio as pin
from pinocchio.utils import *
from scipy.optimize import minimize

FL_path = "../model/urdf/Leg_FL.urdf"
FR_path = "../model/urdf/Leg_FR.urdf"
RL_path = "../model/urdf/Leg_RL.urdf"
RR_path = "../model/urdf/Leg_RR.urdf"

FL_model = pin.buildModelFromUrdf(FL_path)
FL_data = FL_model.createData()

FR_model = pin.buildModelFromUrdf(FR_path)
FR_data = FR_model.createData()

RL_model = pin.buildModelFromUrdf(RL_path)
RL_data = RL_model.createData()

RR_model = pin.buildModelFromUrdf(RR_path)
RR_data = RR_model.createData()

kps_ref = np.array([700.0, 700.0, 700.0])
kds_ref = np.array([20.0, 20.0, 20.0])
v_ref = np.array([0.0, 0.0, 0.0])

# FL_end_id = FL_model.getFrameId('FL_Foot')
# FR_end_id = FR_model.getFrameId('FR_Foot')
# RL_end_id = RL_model.getFrameId('RL_Foot')
# RR_end_id = RR_model.getFrameId('RR_Foot')

def forward_kinematics(model, data, q):
    """
    计算机械臂的运动学正解
    :param q: 关节角度向量
    :return: 末端执行器的位姿（SE(3) 矩阵）
    """
    # 计算正运动学
    pin.forwardKinematics(model, data, q)
    # 获取末端执行器的位姿
    pin.updateFramePlacements(model, data)
    pin.computeJointJacobians(model, data, q)
    j_local = pin.getFrameJacobian(model, data, 9, pin.ReferenceFrame.LOCAL)
    j_t = j_local[:3, :3].T

    position = data.oMf[9].translation
    return position, j_t

def force_feedback(model, data, q, qfrc):
    pin.computeJointJacobians(model, data, q)
    j_local = pin.getFrameJacobian(model, data, 9, pin.ReferenceFrame.LOCAL)
    j_t_inv = np.linalg.inv(j_local[:3, :3].T)
    f_fb = np.dot(j_t_inv, qfrc)
    return f_fb


def Leg_tau_compute(model, data, kps, kds, p_ref, v_ref, q, vq):
    pin.forwardKinematics(model, data, q)
    pin.updateFramePlacements(model, data)
    pin.computeJointJacobiansTimeVariation(model, data, q, vq)

    M = pin.crba(model, data, q)  # 计算惯性矩阵
    b = pin.nonLinearEffects(model, data, q, vq)  # 计算非线性项


    J_local = pin.getFrameJacobian(model, data, 9, pin.ReferenceFrame.LOCAL)
    dJ_dt = pin.getFrameJacobianTimeVariation(model, data, 9, pin.ReferenceFrame.LOCAL)

    p_now = data.oMf[9].translation
    v_now = J_local[:3, :3] @ vq

    # J_T_inv = np.linalg.inv(J_local[:3, :3].T)
    # F_fb = np.dot(J_T_inv, qfrc)

    # if (v_norm_L2 > 50):
    #     # print("v_now:" ,v_now)
    #     # print("norm:", v_norm_L2)
    #     # print("-----------------------------")
    #     tau_out = J_local[:3, :3].T @ (0.5 * kps * (p_ref - p_now) + 0.8 * kds * (v_ref - v_now))
    #     aq_ref = J_local[:3, :3].T @ (0.5 * kps * (p_ref - p_now) + 0.8 * kds * (v_ref - v_now) - dJ_dt[:3, :3] @ vq)
    # else:
    tau_out = J_local[:3, :3].T @ (kps * (p_ref - p_now) + kds * (v_ref - v_now))
    aq_ref = J_local[:3, :3].T @ (kps * (p_ref - p_now) + kds * (v_ref - v_now) - dJ_dt[:3, :3] @ vq)


    tau_ff = M @ aq_ref + b  # 计算关节力矩

    tau_out = tau_out + tau_ff
    tau_out = np.clip(tau_out, -5.0, 5.0)

    return tau_out


if __name__ == '__main__':
    pin.forwardKinematics(FL_model, FL_data, np.array([0.0, 0.7, -1.2]))
    pin.updateFramePlacements(FL_model, FL_data)
    p_FL = FL_data.oMf[9].translation

    pin.forwardKinematics(FR_model, FR_data, np.array([-0.0, 0.7, -1.2]))
    pin.updateFramePlacements(FR_model, FR_data)
    p_FR = FR_data.oMf[9].translation

    pin.forwardKinematics(RL_model, RL_data, np.array([0.0, -0.7, 1.2]))
    pin.updateFramePlacements(RL_model, RL_data)
    p_RL = RL_data.oMf[9].translation

    pin.forwardKinematics(RR_model, RR_data, np.array([-0.0, -0.7, 1.2]))
    pin.updateFramePlacements(RR_model, RR_data)
    p_RR = RR_data.oMf[9].translation

    pos, j_t = forward_kinematics(FL_model, FL_data, np.array([0.0, 0.7, -1.2]))


    print(pos)
    print(j_t)

    # print("FL:", FL_end_id)
    # print("FR:", FR_end_id)
    # print("RL:", RL_end_id)
    # print("RR:", RR_end_id)

