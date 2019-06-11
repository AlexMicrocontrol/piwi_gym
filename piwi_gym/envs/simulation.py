from piwi_gym.dataIO.data_processor import CsvData, FeatureEnrichedData
from piwi_gym.configs import *
from abc import ABCMeta, abstractmethod, abstractclassmethod
import abc


class Simulation(metaclass=ABCMeta):

    def __init__(self):
        pass

    @abstractmethod
    def reset(self, **kwargs):
        pass

    @abstractmethod
    def step(self):
        pass


class Simple(Simulation):

    def __init__(self):
        super().__init__()
        self.data_fname = train_file
        self.i_split = tt_split
        self.cols = columns
        self.seq_len = sequence_len
        self.b_size = batch_size
        self.to_norm = shouldNormalize
        self.data_load = CsvData(self.data_fname,
                                 self.i_split,
                                 self.cols)
        self.min_values = self.data_load.data_train.min(axis=0)
        self.max_values = self.data_load.data_train.max(axis=0)
        self.curr_idx = 0
        self.train_len = self.data_load.len_train
        self.window_shift = win_shift

    def reset(self, test_pahse=False):
        if test_pahse:
            obs = self.data_load.next_window(self.train_len, self.seq_len, self.to_norm)
            self.curr_idx = self.train_len - 1
        else:
            obs = self.data_load.next_window(self.curr_idx, self.seq_len, self.to_norm)
            self.curr_idx = self.seq_len - 1

        return obs

    def step(self):
        try:
            obs = self.data_load.next_window(self.curr_idx, self.seq_len, self.to_norm)
            self.curr_idx += self.window_shift
            done = False
        except StopIteration:
            obs = []
            done = True
        return obs, done
