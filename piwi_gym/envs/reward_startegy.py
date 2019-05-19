import numpy as np
import pandas as pd
from abc import ABC, abstractmethod


class RewardStrategy(ABC):
    @abstractmethod
    def get_reward(self, **param):
        raise NotImplemented


class SalesBuysStrategy(object):
    def get_reward(self, trade_history):
        sales = 0
        buys = 0

        for trade in trade_history:
            if trade['trade_type'] == 'buy_ask':
                buys += trade['total']
            else:
                sales += trade['total']

        reward = sales - buys

        return reward


class CashStrategy(object):
    def __init__(self):
        data = pd.Series(data=np.asarray([0], dtype=np.float32))
        self.reward_history = pd.DataFrame(data=data, columns=['rewards'])
        self.last_mean = 0.5

    def get_reward(self, wallet):
        reward = wallet['cash'] + wallet['vault']
        r_d = pd.Series(data=np.asarray([reward], dtype=np.float32))
        rew_df = pd.DataFrame(data=r_d, columns=['rewards'])
        self.reward_history = self.reward_history.append(rew_df)
        mean_reward = self.reward_history['rewards'].values.mean()

        return mean_reward


class PlainNegativeStartegy(object):
    def __init__(self):
        pass

    def get_reward(self, data):
        reward = -0.1

        return reward


class LossProfit(RewardStrategy):

    def __init__(self, name='LossProfit'):
        self.name = name

    def get_reward(self, wallet):
        loss = wallet['loss']
        profit = wallet['profit']
        reward = profit - loss

        return reward

    def get_rewards(self, trade_history):
        rewards = []
        for trade in trade_history:
            wallet = trade['wallet']


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
