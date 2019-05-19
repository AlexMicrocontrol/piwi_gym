from gym.envs.registration import register

register(
    id='piwi-v0',
    entry_point='piwi_gym.envs.trading_piwi_env:TradingPiwiEnv'
)