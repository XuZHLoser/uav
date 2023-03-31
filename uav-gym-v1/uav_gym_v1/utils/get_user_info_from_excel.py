import openpyxl
from uav_gym_v1.utils.parameters_setting import *
import random

def get_user_dict(file_path):
    wb = openpyxl.load_workbook(file_path)
    sheet = wb.active
    data = tuple(sheet.values)
    user_dict = {}
    # month date start_time end_time latitude longitude user_id
    for i in range(1, len(data)):
        user_dict[data[i][6]] = []
    for i in range(1, len(data)):
        user_dict[data[i][6]].append(data[i][3] - data[i][2])
    return user_dict

user_dict = get_user_dict(FILE_PATH)

def get_demand_list(index):
    # user_dict = get_user_dict(FILE_PATH)
    keys = list(user_dict.keys())
    user_key = keys[index]
    user_demand = user_dict[user_key]
    demand_list = [0] * MAX_EPISODE
    pro_list = range(MAX_EPISODE)
    occ_list = random.sample(pro_list, min(len(user_demand), MAX_EPISODE))
    for i, j in enumerate(occ_list):
        demand_list[j] = user_demand[i] * 100 * TASK_MEAN
    return demand_list

