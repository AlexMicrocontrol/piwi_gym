from gym.envs.registration import register

register(
    id='piwi-v0',
    entry_point='piwi_gym.envs.piwi_env:TradingPiwiEnv'
)