import numpy as np
from uav_gym_v1.utils.parameters_setting import *
import matplotlib.pyplot as plt
import matplotlib.patches as mpathes
import matplotlib.colors as colors
from matplotlib import cm


class Plot(object):
    def __init__(self):
        # 存放每架uav的轨迹
        self.uavs_traj = [[] for _ in range(UAV_NUM)]
        # 存放所有地面设备的坐标
        self.sds = []

    def log_uavs(self, uavs: []):
        for uav, trj in zip(uavs, self.uavs_traj):
            trj.append([uav.coordinate_x, uav.coordinate_y])

    def log_sds(self, sds: []):
        self.sds = sds

    def plot_map(self):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        # 去掉上边框
        ax.spines['top'].set_visible(False)
        # 去掉右边框
        ax.spines['right'].set_visible(False)
        # 设置边框线宽
        ax.spines['left'].set_linewidth(0.2)
        ax.spines['bottom'].set_linewidth(0.2)
        plt.axis('square')
        plt.axis([-LENGTH_MAX * 0.1, LENGTH_MAX * 1.1, -LENGTH_MAX * 0.1, LENGTH_MAX * 1.1])
        # print(self.users_circs)
        border = plt.Rectangle((0, 0), LENGTH_MAX, LENGTH_MAX, linewidth=2, edgecolor='black',
                               facecolor='none')
        ax.add_patch(border)

        # for idx, sd in enumerate(self.sds):
        #     circle = mpathes.Circle(np.array([sd.coordinate_x, sd.coordinate_y]), 2, facecolor='gray', alpha=sd.occurrence_rate)
        #     ax.add_patch(circle)
        colors = []
        x = []
        y = []
        for sd in self.sds:
            x.append(sd.coordinate_x)
            y.append(sd.coordinate_y)
            colors.append(sd.occurrence_rate)
        plt.scatter(x, y, c=colors, cmap='viridis')
        plt.colorbar()
        for idx, trj in enumerate(self.uavs_traj):
            trj = np.array(trj)
            plt.plot(trj[:, 0].tolist(), trj[:, 1].tolist(), label='uav' + str(idx))
        plt.legend(ncol=UAV_NUM, loc=9)
        # 绘制颜色条
        # cmap = colors.LinearSegmentedColormap.from_list('custom_grey',
        #                                                 [(0, 'white'),
        #                                                  (0.8, 'darkgrey'),
        #                                                  (1, 'grey')], N=256)
        # sm = cm.ScalarMappable(cmap=cmap)
        # plt.colorbar(sm)
        plt.show()
        # 保存图片
        fig.savefig(fname='D:\\写的程序\\python项目\\uav\\fig1\\maddpg-real.svg', format='svg', dpi=150)