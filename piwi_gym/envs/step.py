import abc
from abc import abstractmethod


class Step(metaclass=abc.ABCMeta):
    @abstractmethod
    def step(self, **kwargs):
        pass


class SimpleStep(Step):
    def __init__(self, simulation, account, reward_strategy):
        self._account = account
        self._sim = simulation
        self._reward_strategy = reward_strategy

    def step(self, action):
        # Return the observation, done, reward from Simulator and Portfolio
        obs, done = self._sim.step()
        if not done:
            curr_bid_price = obs[-1][0]
            curr_ask_price = obs[-1][1]
            done_acc = self._account.perform_trade_action(action, curr_bid_price, curr_ask_price, self.sim.curr_idx)
            done = done or done_acc
            curr_trade = self._account.get_current_trade()
            reward = self._reward_strategy.get_reward(curr_trade)
            info = self._account.get_trade_history()
            # self.accountant.report_trade(curr_trade)

        else:
            raise StopIteration

        return obs, action, reward, info, done
