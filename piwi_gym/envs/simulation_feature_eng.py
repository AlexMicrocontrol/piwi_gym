from piwi_gym.dataIO.data_processor import PlainDataLoader, OptimalActionDataLoader
from piwi_gym.configs import *


class SimulationFE(object):

    def __init__(self):
        self.data_fname = train_file
        self.i_split = tt_split
        self.cols = ['bid', 'ask', 'sell_vol', 'buy_vol', 'return', 'action']
        self.seq_len = sequence_len
        self.b_size = batch_size
        self.to_norm = shouldNormalize
        self.data_load = OptimalActionDataLoader(self.data_fname,
                                         self.i_split,
                                         self.cols)
        self.min_values = self.data_load.data_train.min(axis=0)
        self.max_values = self.data_load.data_train.max(axis=0)

        self.curr_idx = 0
        self.train_len = self.data_load.len_train
        self.window_shift = 1
        # self.reset()

    def reset(self, test_pahse=False):
        if test_pahse:
            obs = self.data_load.next_window_stream(self.train_len, self.seq_len, self.to_norm)
            rews_acts = self.data_load.next_opt_act_window_stream(self.train_len, self.seq_len)
            self.curr_idx = self.train_len - 1
        else:
            obs = self.data_load.next_window_stream(self.curr_idx, self.seq_len, self.to_norm)
            rews_acts = self.data_load.next_opt_act_window_stream(self.train_len, self.seq_len)
            self.curr_idx = self.seq_len - 1
        return obs, rews_acts

    def step(self):
        try:
            obs = self.data_load.next_window_stream(self.curr_idx, self.seq_len, self.to_norm)
            returns_and_optimal_actions =self.data_load.next_opt_act_window_stream(self.curr_idx, self.seq_len)
            self.curr_idx += self.window_shift
            done = False
        except StopIteration:
            obs, returns_and_optimal_actions = [], []
            done = True
        return obs, returns_and_optimal_actions, done
