# 无人机数量
UAV_NUM = 3
# 地面设备数量
SD_NUM = 50
# 无人机可以服务的半径
SERVICE_RADIUS = 15
# 每个轮次的最大步数
MAX_EPISODE = 40
# 随机数种子 real:9 1:1
SEED = 9
# 地图的长宽最大值
LENGTH_MAX = 100
# 是否开启记录功能以方便绘图
LOG_AVAILABLE = True
# 产生的用户需求大小的均值以及方差, 产生的任务大小服从正态分布
TASK_MEAN = 1000000
TASK_VARIANCE = 1000000
# 每个SD任务队列能容纳的最大数据量
MAX_LOCAL_TASK_SIZE = 10 * TASK_MEAN
# # 无人机单次服务的最大时延
# UAV_LIMIT_TIME_DELAY = 2
# 处理每比特数据需要的cpu周期，64位cpu一个周期可以处理8字节数据
CPU_CYCLE = 0.125
# # uav的cpu频率 3.0GHz
# UAV_FREQUENCY = 3.0 * 1000000
# # 本地的cpu频率 2.0GHz
# LOCAL_FREQUENCY = 2.0 * 1000000
# 无人机计算能耗的因子
UAV_COMPUTING_FACTOR1 = 10
UAV_COMPUTING_FACTOR2 = 2
# 用户设备与无人机间的传输速度 2000mb/s
TRANS_SPEED = 40 * 1024 * 1024
# 无人机的初始电量
UAV_INITIAL_ENERGY = 2000
# 无人机的传输功率
TRANS_POWER = 5
# # 无人机的计算功率
# COM_POWER = 10
# 无人机飞行功率
FLYING_POWER = 1
# 会导致无人机碰撞的最小距离
COLLISION_DISTANCE = 5
# 无人机发生碰撞或出界后的惩罚系数
PENALTY_FACTOR = 10
# 无人机重量
UAV_WEIGHT = 15
# 无人机飞行速度
UAV_SPEED = 20
# 单位常量
K = 10 ** 3
M = 10 ** 6
G = 10 ** 9
# 真实数据集位置
FILE_PATH = "D:\\写的程序\\python项目\\uav\\dataset\\Telcome\\data.xlsx"
# 是否使用真实数据集
USE_REAL_DATASET = True
