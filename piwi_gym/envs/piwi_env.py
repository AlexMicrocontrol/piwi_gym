import asyncio
import gym
from gym import spaces
from piwi_gym.envs.account import MonitoredAccount, Accountant
from piwi_gym.envs.simulation_feature_eng import SimulationFE
from piwi_gym.envs.simulation import Simple
from itertools import repeat
from piwi_gym.envs.reward_startegy import RewardStrategyFactory
from piwi_gym.configs import *
from prettyprinter import pprint
import numpy as np


class TradingPiwiEnv(gym.Env):
    """Custom Environment that follows gym interface"""
    metadata = {'render.modes': ['human', 'console']}

    def __init__(self):
        super(TradingPiwiEnv, self).__init__()
        self.strat_factory = RewardStrategyFactory()
        self.reward_strategy = self.strat_factory.create(REWARD_STRAT)
        self.sim = Simple()
        self.account = MonitoredAccount(start_cash,
                                        start_assets,
                                        buy_limit_pct, sell_limit_pct,
                                        trading_fee_pct)
        self.accountant = Accountant('Christian Wolf')
        self.observation_space = spaces.Box(self.sim.min_values, self.sim.max_values)
        self.action_space = spaces.Discrete(3)  # BUY,SELL,HOLD

    def step(self, action):
        # Return the observation, done, reward from Simulator and Portfolio
        obs, done = self.sim.step()
        if not done:
            curr_bid_price = obs[0][-1][0]
            curr_ask_price = obs[0][-1][1]
            done_acc = self.account.perform_trade_action(action, curr_bid_price, curr_ask_price, self.sim.curr_idx)
            done = done or done_acc
            curr_trade = self.account.get_current_trade()
            reward = self.reward_strategy.get_reward(curr_trade['wallet'])
            info = self.account.get_trade_history()
            # self.accountant.report_trade(curr_trade)

        else:
            raise StopIteration

        return obs, action, reward, info, done

    # def step(self, actions):
    #     # Return the observation, done, reward from Simulator and Portfolio
    #     _obs, optimal_actions, done = self.sim.step()
    #     reward = []
    #     new_obs, info = [], []
    #
    #     if not done:
    #
    #         curr_bid_price = _obs[-1][0]
    #         curr_ask_price = _obs[-1][1]
    #         if len(actions) > 1:
    #             act_ = np.argmax(actions[-1])
    #         else:
    #             act_ = actions
    #         done_acc = self.account.perform_trade_action(act_,
    #                                                      curr_bid_price,
    #                                                      curr_ask_price,
    #                                                      self.sim.curr_idx)
    #         done = done or done_acc
    #         curr_trade = self.account.get_current_trade()
    #         # self.accountant.append_trade_report(curr_trade)
    #         rew_ = self.reward_strategy.get_reward(curr_trade['wallet'])
    #         reward.append(rew_)
    #         info = self.account.get_trade_history()
    #         new_obs = self._extend_observation(_obs, info[self.sim.curr_idx - self.sim.seq_len:])
    #         if self.sim.curr_idx % 300 == 0:
    #             self.render()
    #
    #     return new_obs, reward, info, done

    def reset(self, test_phase=False, is_interrupted=False):
        if is_interrupted:
            asyncio.run(self._report_history())
        obs = self.sim.reset(test_pahse=test_phase)
        self.account.reset()
        info = self.account.get_trade_history()
        # obs = self._extend_observation(obs, info)

        return obs

    def render(self, mode='human'):
        '''Standard console Log'''
        wallet_ = self.account.get_wallet()
        pprint(wallet_)
        profit = wallet_[PFT] - wallet_[LSS]
        print('Your Balance is currently at {} btc'.format(profit))
        print('######' * 25)

    def _extend_observation(self, observation, info):
        '''Extend the Standard Observation by Wallet information'''
        default_extent = []
        cash_col = []
        coins_col = []
        profit_col = []
        loss_col = []

        diff = len(observation) - len(info)
        cntr_ = 0
        if diff > 0:
            for i in range(len(observation)):
                trade = info[cntr_]
                if i < diff:
                    cash_col.append([3.0])
                    coins_col.append([3.0])
                    profit_col.append([0])
                    loss_col.append([0])
                else:
                    cash_col.append([trade['wallet']['cash']])
                    coins_col.append([trade['wallet']['coins']])
                    profit_col.append([trade['wallet']['profit']])
                    loss_col.append([trade['wallet']['loss']])
                    cntr_ += 1
        else:
            for trade_ in info:
                cash_col.append([trade_['wallet']['cash']])
                coins_col.append([trade_['wallet']['coins']])
                profit_col.append([trade_['wallet']['profit']])
                loss_col.append([trade_['wallet']['loss']])

        cash_col = np.asarray(cash_col)  # .reshape((1, observation.shape[0]))
        coins_col = np.asarray(coins_col)  # .reshape((1, observation.shape[0]))
        profit_col = np.asarray(profit_col)  # .reshape((1, observation.shape[0]))
        loss_col = np.asarray(loss_col)  # .reshape((1, observation.shape[0]))

        new_obs = np.hstack([observation, cash_col])
        new_obs = np.hstack([new_obs, coins_col])
        new_obs = np.hstack([new_obs, profit_col])
        new_obs = np.hstack([new_obs, loss_col])

        return new_obs

    async def _report_history(self):
        '''Writing the Report on KeyBoardInteruption'''
        print('reporting')
        report_hist = self.account.get_trade_history()
        succes = await asyncio.gather(self.accountant.report_history(report_hist))
