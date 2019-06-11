from piwi_gym.dataIO.data_processor import CsvData, PlainData
from piwi_gym.configs import *


class Simulation(object):

    def __init__(self, configs):
        self._confs = configs
        self.train_conf = self._confs['training']
        self.data_fname = train_file
        self.i_split = tt_split
        self.cols = self._confs['data']['columns']
        self.seq_len = self._confs['data']['sequence_length']
        self.b_size = self.train_conf['batch_size']
        self.to_norm = self._confs['data']['normalise']
        self.data_load = PlainData(self.data_fname,
                                   self.i_split,
                                   self.cols)
        self.min_values = self.data_load.data_train.min(axis=0)
        self.max_values = self.data_load.data_train.max(axis=0)
        self.curr_idx = 0
        self.train_len = self.data_load.len_train
        self.window_shift = 1 #60min / 5min
        # self.reset()

    def reset(self, test_pahse=False):
        if test_pahse:
            obs = self.data_load.next_window_stream(self.train_len, self.seq_len, self.to_norm)
            self.curr_idx = self.train_len - 1
        else:
            obs = self.data_load.next_window_stream(self.curr_idx, self.seq_len, self.to_norm)
            self.curr_idx = self.seq_len - 1

        return obs

    def step(self):
        try:
            obs = self.data_load.next_window_stream(self.curr_idx, self.seq_len, self.to_norm)
            self.curr_idx += self.window_shift
            done = False
        except StopIteration:
            obs = []
            done = True
        return obs, done
