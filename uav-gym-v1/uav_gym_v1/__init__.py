from gym.envs.registration import register


register(
    id='uav_env-v1',                                   # Format should be xxx-v0, xxx-v1....
    entry_point='uav_gym_v1.envs:UavEnv',              # Expalined in envs/__init__.py
)