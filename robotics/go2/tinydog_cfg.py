import numpy as np

class TinyDogConfig:
    simulation_duration = 500.0
    simulation_dt = 0.0013
    control_decimation = 13

    num_actions = 13
    num_single_obs = 48
    frame_stack = 8

    base_kp = 7.0
    base_kd = 0.2
    kps = np.array([base_kp, base_kp, base_kp, base_kp, base_kp, base_kp, 20.0,
                    base_kp, base_kp, base_kp, base_kp, base_kp, base_kp])
    kds = np.array([base_kd, base_kd, base_kd, base_kd, base_kd, base_kd, 0.5,
                    base_kd, base_kd, base_kd, base_kd, base_kd, base_kd])
    torque_limit = np.array([5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 15.0,
                             5.0, 5.0, 5.0, 5.0, 5.0, 5.0])

    hip_pos = -0.0
    thigh_pos = 0.7
    calf_pos = 1.3

    default_angles = np.array([-hip_pos, -thigh_pos,  calf_pos, hip_pos,  thigh_pos, -calf_pos, 0.,
                               hip_pos,  thigh_pos, -calf_pos, -hip_pos, -thigh_pos,  calf_pos])

    hip_low = 0.2
    thigh_low = 1.3
    calf_low = 2.0

    low_angles = np.array([-hip_low, -thigh_low, calf_low, hip_low, thigh_low, -calf_low, 0.03,
                           hip_low, thigh_low, -calf_low, -hip_low, -thigh_low, calf_low])

    # default_angles = np.array([-0., -0.5, 0.75, 0., 0.5, -0.75, 0.02,
    #                            0., 0.5, -0.75, -0., -0.5, 0.75])

    ang_vel_scale = 0.25
    dof_pos_scale = 1.0
    dof_vel_scale = 0.05

    action_scale = 0.25
    cmd_scale = np.array([2.0, 2.0, 0.25])

    clip_observations = 100.
    clip_actions = 100.

    hip_limit = 1.2
    thigh_limit = 2.2
    calf_limit = 4.0
    waist_limit = 1.0

    xml_path = "../model/waistdog-xml/scene_RL.xml"
    policy_path = "../policies/old4/new8.pt"

