import time
import mujoco
import mujoco.viewer
import numpy as np
import torch
import math

from utils.keyboard_controller import KeyboardController
from utils.easy_math import get_gravity_orientation

from scipy.spatial.transform import Rotation as R
from collections import deque

Command_Generator = KeyboardController(max_vel = 1)
Command_Generator.start_listening()

def pd_control(kps, target_q, q, kds, target_dq, dq):
    """Calculates torques from position commands with customizable limits"""
    output = (target_q - q) * kps + (target_dq - dq) * kds
    return output

class Sim2simCfg:
    policy_root = "../policies/dreamwaq/go2/policy_dwaq.pt"

    whole_policy = torch.jit.load(policy_root)

    class sim_config:
        mujoco_model_path = "../robotics/go2/scene_terrain.xml"
        dt = 0.005
        decimation = 4

    class robot_config:
        base_kp = 28
        base_kd = 0.7
        kps = np.array([base_kp, base_kp, base_kp, base_kp, base_kp, base_kp,
                        base_kp, base_kp, base_kp, base_kp, base_kp, base_kp])
        kds = np.array([base_kd, base_kd, base_kd, base_kd, base_kd, base_kd,
                        base_kd, base_kd, base_kd, base_kd, base_kd, base_kd])
        hip_pos = 0.0
        thigh_pos = 0.8
        calf_pos = -1.5

        default_angles = np.array([hip_pos, thigh_pos, calf_pos,
                                   hip_pos, thigh_pos, calf_pos,
                                   hip_pos, thigh_pos, calf_pos,
                                   hip_pos, thigh_pos, calf_pos,])

        init_angles = np.array([hip_pos, thigh_pos, calf_pos,
                                hip_pos, thigh_pos, calf_pos,
                                hip_pos, 1., calf_pos,
                                hip_pos, 1., calf_pos])

    class env:
        num_actions = 12
        frame_stack = 6
        num_single_obs = 45
        num_observations = num_single_obs * frame_stack

    class control:
        action_scale = 0.25
        decimation = 4

    class normalization:
        class obs_scales:
            lin_vel = 2.0
            ang_vel = 0.25
            dof_pos = 1.0
            dof_vel = 0.05
            height_measurements = 5.0
            quat = 1.
        clip_observations = 100.
        clip_actions = 100.


def run_mujoco(cfg: Sim2simCfg):
    counter = 0
    model = mujoco.MjModel.from_xml_path(cfg.sim_config.mujoco_model_path)
    data = mujoco.MjData(model)
    model.opt.timestep = cfg.sim_config.dt
    mujoco.mj_step(model, data)
    action = np.zeros(cfg.env.num_actions, dtype=np.double)
    target_q = np.zeros(12, dtype=np.double)
    target_vel = np.zeros(12, dtype=np.double)

    obs = np.zeros(cfg.env.num_single_obs, dtype=np.float32)
    obs_hist_buf = np.zeros(cfg.env.num_observations, dtype=np.float32)

    obs_buff = torch.zeros(1, cfg.env.num_observations, dtype=torch.float)

    with mujoco.viewer.launch_passive(model, data) as viewer:
        start_0 = time.time()

        while viewer.is_running() and time.time() - start_0 < 0.5:
            mujoco.mj_step(model, data)
            counter += 1
            viewer.sync()
            time_until_next_step = model.opt.timestep - (time.time() - start_0)
            if time_until_next_step > 0:
                time.sleep(time_until_next_step)


        count_lowlevel = 1
        start_1 = time.time()
        start = time.time()
        while viewer.is_running() and time.time() - start < 500:

            xyz_vel = data.qvel[0:3].astype(np.double)

            cmd = Command_Generator.get_velocities()
            quat = data.qpos[3:7]
            omega = data.qvel[3:6]
            qj = data.qpos[7:]
            dqj = data.qvel[6:]

            if count_lowlevel % cfg.sim_config.decimation == 0:
                err_pos = qj - cfg.robot_config.default_angles

                obs[:3] = cmd * np.array([2.0, 2.0, 0.5])  # np.array([2.0, 2.0, 0.5])是命令的归一化参数，其实最后的0.5在训练的时候是0.25
                obs[3:6] = omega * cfg.normalization.obs_scales.ang_vel
                obs[6:9] = get_gravity_orientation(quat)
                # print(obs[6:9])
                obs[9:9+cfg.env.num_actions] = err_pos
                obs[9+cfg.env.num_actions:9+cfg.env.num_actions*2] = dqj * cfg.normalization.obs_scales.dof_vel
                obs[9+cfg.env.num_actions*2:9+cfg.env.num_actions*3] = action

                obs_hist_buf = obs_hist_buf[cfg.env.num_single_obs:]
                obs_hist_buf = np.concatenate((obs_hist_buf, obs), axis=-1)

                tmp = torch.from_numpy(obs_hist_buf)
                actor_input = tmp.unsqueeze(0)
                # print(actor_input.shape)

                action = cfg.whole_policy(actor_input).detach().numpy().squeeze()
                target_q = cfg.robot_config.default_angles + action * cfg.control.action_scale
                target_vel = np.zeros(cfg.env.num_actions)

            tau = pd_control(cfg.robot_config.kps, target_q, qj,
                             cfg.robot_config.kds, target_vel, dqj)


            data.ctrl = tau
            mujoco.mj_step(model, data)
            current_time = time.time()
            elapsed = current_time - start_1

            sleep_time = cfg.sim_config.dt - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)
            start_1 = current_time
            count_lowlevel += 1
            viewer.sync()

if __name__ == '__main__':
    cfg = Sim2simCfg()
    run_mujoco(cfg)
