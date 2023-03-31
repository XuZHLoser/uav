import gym
from gym import spaces
import numpy as np
import random
from uav_gym_v1.entity.entity import *
from uav_gym_v1.utils.parameters_setting import *
from uav_gym_v1.utils.plot import Plot


class UavEnv(gym.Env):
    def __init__(self):
        np.random.seed(SEED)
        random.seed(SEED)
        self.sds = [SD(index) for index in range(SD_NUM)]
        self.uavs = [UAV() for _ in range(UAV_NUM)]
        # self.sd_fairness = 0
        self.uav_fairness = 0
        self.sd_service_times = [0 for _ in range(SD_NUM)]
        # 每个无人机观测值的维度：无人机位置 + 其他无人机的距离 + 所有无人机的累计服务次数 + 所有SD的累计服务次数
        self.observation_shape = 2 + UAV_NUM - 1 + UAV_NUM + SD_NUM
        # 每个无人机动作的维度：长度、角度以及cpu频率
        self.action_shape = 3
        # 动作空间为所有agent动作值的集合
        self.action_space = [spaces.Box(low=0, high=1, shape=(self.action_shape,), dtype=np.float32) for _ in
                             range(UAV_NUM)]
        # 总的观测值就为所有agent观测值的集合
        self.observation_space = [spaces.Box(low=0, high=100, shape=(self.observation_shape,), dtype=np.float32) for _
                                  in range(UAV_NUM)]
        self.i_episode = 0

        # 是否对观测值做标准化
        self.is_standard = True
        # 是否在出界时返回True
        self.done_flag = True
        # 是否开启训练
        self.is_train = True
        # 是否使用角度和距离来移动
        self.use_step = True
        # 是否使用ddpg
        self.use_ddpg = False

    def step(self, actions):
        observations = []
        rewards = []
        dones = []
        infos = []
        for i in range(UAV_NUM):
            if self.use_step:
                self.uavs[i].step(actions[i])
            else:
                self.uavs[i].move(actions[i])
        self._world_step()
        if LOG_AVAILABLE:
            self.plot.log_uavs(self.uavs)
        for uav in self.uavs:
            rewards.append(self._get_uav_reward(uav))
            if not self.use_ddpg:
                observations.append(self._get_uav_obs(uav))
            else:
                observations.append(self._get_single_uav_obs(uav))
            dones.append(self._get_uav_done(uav))
            infos.append(self._get_uav_info(uav))
        return observations, rewards, dones, infos

    def _get_single_uav_obs(self, uav):
        uav_coordinate = [uav.coordinate_x / 50, uav.coordinate_y / 50]
        all_sd_service_times = []
        for service_times in uav.sd_service_times:
            all_sd_service_times.append(service_times)
        obs = uav_coordinate + all_sd_service_times + [uav.service_times]
        if self.is_standard:
            return self.standardization(obs)
        else:
            return obs

    def _get_uav_obs(self, uav):
        uav_coordinate = [uav.coordinate_x / 50, uav.coordinate_y / 50]
        other_uav_distances = [x / 50.0 for x in self._get_all_uav_distances(uav)]
        all_sd_service_times = []
        for service_times in uav.sd_service_times:
            all_sd_service_times.append(service_times)
        all_uav_service_times = []
        for uav in self.uavs:
            all_uav_service_times.append(uav.service_times)
        obs = uav_coordinate + other_uav_distances + all_sd_service_times + all_uav_service_times
        if self.is_standard:
            return self.standardization(obs)
        else:
            return obs

    def _world_step(self):
        for uav in self.uavs:
            uav.task_size = 0
            for idx, sd in enumerate(self.sds):
                if sd.total_task_size > 0 and self._get_relative_distance(sd, uav) < SERVICE_RADIUS:
                    uav.task_size += sd.total_task_size
                    uav.sd_service_times[idx] += 1
                    uav.service_times += 1
                    sd.total_task_size = 0
                    self.sd_service_times[idx] += 1
        self.i_episode += 1
        for sd in self.sds:
            sd.get_task_size(self.i_episode)
        molecular = 0
        denominator = 0
        for uav in self.uavs:
            # print(sd.served_times)
            molecular += uav.service_times
            denominator += uav.service_times ** 2
        if molecular == 0:
            self.uav_fairness = 0
        else:
            self.uav_fairness = molecular ** 2 / (denominator * UAV_NUM)

    def standardization(self, data):
        return (data - np.mean(data)) / np.std(data)

    def _get_uav_reward(self, uav):
        molecular = 0
        denominator = 0
        for service_times in uav.sd_service_times:
            molecular += service_times
            denominator += service_times ** 2
        if molecular == 0:
            sd_fairness = 0
        else:
            sd_fairness = molecular ** 2 / (denominator * SD_NUM)
        penalty = 0
        if self._is_uav_outrange(uav):
            penalty = PENALTY_FACTOR
        for uav_ in self.uavs:
            if uav == uav_:
                continue
            if self._get_relative_distance(uav_, uav) <= COLLISION_DISTANCE:
                penalty = PENALTY_FACTOR
                break
        # 传输时延
        trans_delay = uav.task_size / TRANS_SPEED
        # # 本地执行时延
        # local_exec_delay = CPU_CYCLE * uav.task_size * (1 - uav.task_offloading_rate) / LOCAL_FREQUENCY
        # uav执行时延 +0.01防止除0异常
        uav_exec_delay = CPU_CYCLE * uav.task_size / ((uav.frequency + 0.01) * M)
        # 最终时延
        task_delay = trans_delay + uav_exec_delay
        # print("task_size=%f" % uav.task_size)
        # print("trans_delay=%f, local_exec_delay=%f, uav_exec_delay=%f,"
        #           "task_delay=%f" % (trans_delay, local_exec_delay, uav_exec_delay, task_delay))
        # print("uav.frequency: %f"% uav.frequency)
        # print("task_delay: %f, flying: %f" % (task_delay, uav.length / UAV_SPEED))
        uav_consumption = trans_delay * TRANS_POWER + UAV_COMPUTING_FACTOR1 * uav_exec_delay * uav.frequency ** UAV_COMPUTING_FACTOR2 + (
                    task_delay + uav.length / UAV_SPEED) * FLYING_POWER
        # print("tran:%f, exec:%f, flying:%f" % (trans_delay * TRANS_POWER, UAV_COMPUTING_FACTOR1 * uav_exec_delay * uav.frequency ** UAV_COMPUTING_FACTOR2, (task_delay + uav.length/UAV_SPEED) * FLYING_POWER))
        uav.energy -= uav_consumption
        # print("uav.energy = %f" % uav.energy)
        if not self.is_train:
            return uav.task_size / M
        # print(uav_consumption)
        return sd_fairness * self.uav_fairness * uav.task_size / M - penalty

    def _get_uav_done(self, uav):
        if uav.energy < 0:
            return True
        if self._is_uav_outrange(uav) and self.done_flag:
            return True
        # for uav_ in self.uavs:
        #     if uav == uav_:
        #         continue
        #     if self._get_relative_distance(uav_, uav) < COLLISION_DISTANCE:
        #         return True
        return False

    def _get_uav_info(self, uav):
        pass

    def _get_relative_distance(self, point1, point2):
        return math.sqrt(math.pow(point1.coordinate_x - point2.coordinate_x, 2) +
                         math.pow(point1.coordinate_y - point2.coordinate_y, 2))

    def _is_uav_outrange(self, uav):
        if uav.coordinate_x < 0 or uav.coordinate_x > 100 or uav.coordinate_y < 0 or uav.coordinate_y > 100:
            return True
        else:
            return False

    # 得到无人机之间的相对距离
    def _get_all_uav_distances(self, uav):
        distances = []
        for uav_ in self.uavs:
            if uav == uav_:
                continue
            distance = self._get_relative_distance(uav_, uav)
            distances.append(distance)
        return distances

    def render(self):
        self.plot.plot_map()

    def reset(self):
        self.use_step = True
        self.sd_service_times = [0 for _ in range(SD_NUM)]
        self.i_episode = 0
        for i, uav in enumerate(self.uavs):
            uav.reset(i)
        for sd in self.sds:
            sd.reset()
        for sd in self.sds:
            sd.get_task_size(self.i_episode)
        # for i, uav in enumerate(self.uavs):
        #     uav.print_info(i)
        # for i, user in enumerate(self.users):
        #     user.print_info(i)
        if LOG_AVAILABLE:
            self.plot = Plot()
            self.plot.log_sds(self.sds)
            self.plot.log_uavs(self.uavs)
        obs = []
        for uav in self.uavs:
            if not self.use_ddpg:
                obs.append(self._get_uav_obs(uav))
            else:
                obs.append(self._get_single_uav_obs(uav))
        return obs

    def set_standard(self, standard):
        self.is_standard = standard

    def set_done_flag(self, done):
        self.done_flag = done

    def set_train(self, train):
        self.is_train = train

    def set_step(self, use_step):
        self.use_step = use_step

    def set_ddpg(self, ddpg):
        self.use_ddpg = ddpg

    def get_fairness(self):
        molecular = 0
        denominator = 0
        for service_times in self.sd_service_times:
            molecular += service_times
            denominator += service_times ** 2
        if molecular == 0:
            sd_fairness = 0
        else:
            sd_fairness = molecular ** 2 / (denominator * SD_NUM)
        return sd_fairness, self.uav_fairness

    # 得到无人机移动范围之内的所有sd信息
    def get_sd_list(self):
        sd_list = [[] for _ in range(UAV_NUM)]
        for i, uav in enumerate(self.uavs):
            for sd in self.sds:
                if self._get_relative_distance(uav, sd) < 20 and sd.total_task_size > 0:
                    sd_list[i].append(sd)
        return sd_list
