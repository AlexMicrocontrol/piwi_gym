import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
from piwi_gym.configs import *
import abc


class RewardStrategyFactory(object):

    def __init__(self, name='default'):
        self.name = name

    def create(self, strategy="PlainNegative"):
        if strategy == "PlainNegative":
            return PlainNegative()
        elif strategy == "LossProfit":
            return LossProfit()
        elif strategy == "Cash":
            return Cash()
        elif strategy == "SalesBuys":
            return SalesBuys()
        else:
            raise NotImplementedError


class RewardStrategy(metaclass=abc.ABCMeta):

    @abstractmethod
    def get_reward(self, **param):
        """Reward calculation"""
        pass


class SalesBuys(RewardStrategy):
    def get_reward(self, trade_history):
        sales = 0
        buys = 0

        for trade in trade_history:
            if trade[TYPE] == 'buy_ask':
                buys += trade['total']
            else:
                sales += trade['total']

        reward = sales - buys

        return reward


class Cash(RewardStrategy):
    def __init__(self):
        data = pd.Series(data=np.asarray([0], dtype=np.float32))
        self.reward_history = pd.DataFrame(data=data, columns=['rewards'])
        self.last_mean = 0.5

    def get_reward(self, wallet):
        reward = wallet[CSH] + wallet['vault']
        r_d = pd.Series(data=np.asarray([reward], dtype=np.float32))
        rew_df = pd.DataFrame(data=r_d, columns=['rewards'])
        self.reward_history = self.reward_history.append(rew_df)
        mean_reward = self.reward_history['rewards'].values.mean()

        return mean_reward


class PlainNegative(RewardStrategy):

    def get_reward(self, data):
        reward = -0.1

        return reward


class LossProfit(RewardStrategy):

    def __init__(self, name='LossProfit'):
        self.name = name

    def get_reward(self, wallet):
        loss = wallet[LSS]
        profit = wallet[PFT]
        reward = profit - loss

        return reward


class OptimalAction(RewardStrategy):

    def __init__(self, name='OptimalAction'):
        self.name = name

    def get_reward(self, pred_actions, true_actions):
        reward = []
        for pred, true in zip(pred_actions, true_actions['action'].values):
            if (int(np.argmax(pred)) == int(true)):
                reward.append(1.0)
            else:
                reward.append(-1.0)

        return np.asarray(reward)
