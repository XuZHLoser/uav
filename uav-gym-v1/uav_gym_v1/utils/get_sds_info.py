from uav_gym_v1.utils.parameters_setting import *
import numpy as np
np.random.seed(SEED)
sds_occ = []
sds_x = []
sds_y = []
for i in range(SD_NUM):
    sds_x.append(np.random.uniform(10, 90))
    sds_y.append(np.random.uniform(10, 90))
for i in range(SD_NUM):
    while True:
        sd_occ = np.random.normal(0.8, 0.3)
        if 0 < sd_occ <= 1:
            sds_occ.append(sd_occ)
            break
