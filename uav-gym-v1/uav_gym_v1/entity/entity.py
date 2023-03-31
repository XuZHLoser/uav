import math
import numpy as np
from uav_gym_v1.utils.parameters_setting import *
from uav_gym_v1.utils.get_user_info_from_excel import *


# from uav_gym_v1.utils.get_sds_info import *

class Entity(object):
    def __init__(self):
        # x, y坐标
        self.coordinate_x = None
        self.coordinate_y = None


class SD(Entity):
    def __init__(self, index):
        self.index = index
        self.coordinate_x = np.random.uniform(10, 90)
        self.coordinate_y = np.random.uniform(10, 90)
        # self.coordinate_x = sds_x[index]
        # self.coordinate_y = sds_y[index]
        # SD的数据大小
        self.total_task_size = 0
        # 任务发生率
        # self.occurrence_rate = 1
        self.occurrence_rate = np.random.uniform(0.5, 0.9)
        # while True:
        #     self.occurrence_rate = np.random.normal(0.8, 0.1)
        #     if self.occurrence_rate > 0 and self.occurrence_rate < 1:
        #         break
        # self.served_times = 0
        # self.collaberate_uav = None
        if USE_REAL_DATASET:
            self.task_dataset = get_demand_list(index)
            # print(self.task_dataset)
            occ = 0
            for demand in self.task_dataset:
                if demand > 0:
                    occ += 1
            self.occurrence_rate = occ * 1.0 / MAX_EPISODE
        else:
            # self.occurrence_rate = sds_occ[index]
            self.task_dataset = []
            for _ in range(MAX_EPISODE):
                self.task_dataset.append(self.generate_task())
            # print(self.task_dataset)
        print('无人机的初始位置：(%f, %f), 任务卸载率 %f' % (self.coordinate_x, self.coordinate_y, self.occurrence_rate))

    def reset(self):
        self.total_task_size = 0
        # self.served_times = 0

    def get_task_size(self, i_episode):
        task_size = self.task_dataset[i_episode]
        self.total_task_size = min(self.total_task_size + task_size, MAX_LOCAL_TASK_SIZE)

    def generate_task(self):
        list = [True, False]
        task_size = 0
        p = np.array([self.occurrence_rate, 1 - self.occurrence_rate])
        has_user_demand = np.random.choice(list, p=p)
        if has_user_demand:
            while True:
                task_size = np.random.normal(TASK_MEAN, TASK_VARIANCE)
                # print("tasksize = %f" % task_size)
                # 确保任务大小大于0
                if task_size > 0:
                    # self.total_task_size = min(self.total_task_size + task_size, MAX_LOCAL_TASK_SIZE)
                    # self.total_task_size = task_size
                    break
        return task_size


class UAV(Entity):
    def __init__(self):
        super(UAV, self).__init__()
        self.energy = 0
        self.frequency = 0
        # self.task_offloading_rate = 0
        self.length = 0
        self.sd_service_times = None
        self.service_times = 0
        self.task_size = 0

    def reset(self, idx):
        # uav的初始位置列表，最多同时有4台uav
        initial_coordinate_list1 = [10, 90, 10, 90]
        initial_coordinate_list2 = [90, 10, 10, 90]
        self.coordinate_x = initial_coordinate_list1[idx]
        self.coordinate_y = initial_coordinate_list2[idx]
        self.energy = UAV_INITIAL_ENERGY
        self.sd_service_times = [0 for _ in range(SD_NUM)]
        self.service_times = 0

    def step(self, action):  # 第0维代表长度，第1维代表角度, 第3维代表cpu频率
        action = (action + 1) / 2
        self.coordinate_x += 20 * action[0] * math.cos(action[1] * math.pi * 2)
        self.coordinate_y += 20 * action[0] * math.sin(action[1] * math.pi * 2)
        self.frequency = action[2]
        self.length = action[0] * 20

    def move(self, action):  # 直接给出移动后的坐标
        if action[0] != 0:
            self.coordinate_x = action[0]
            self.coordinate_y = action[1]
            self.frequency = action[2]
            self.length = action[0]
        else:
            self.frequency = action[2]
            self.length = action[0]
