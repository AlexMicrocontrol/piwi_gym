import pandas as pd
from piwi_gym.utils.features import *
from sklearn import preprocessing
from abc import *


class Loader(metaclass=ABCMeta):
    def __init__(self, name="Loader"):
        self.name = name

    # @abstractmethod
    # def _load_from(self, filename, split, cols):
    #     pass

    @abstractmethod
    def get_test_data(self, seq_len, should_norm):
        '''
        Create x, y test data windows
        Warning: batch method, not generative, make sure you have enough memory to
        load data, otherwise reduce size of the training split.
        '''
        pass

    @abstractmethod
    def get_train_data(self, seq_len, should_norm):
        '''
        Create x, y train data windows
        Warning: batch method, not generative, make sure you have enough memory to
        load data, otherwise use generate_training_window() method.
        '''
        pass

    @abstractmethod
    def train_batch_generator(self, seq_len, batch_size, should_norm):
        '''Yield a generator of training data from filename on given list of cols split for train/test'''
        pass

    @abstractmethod
    def next_window(self, i, seq_len, should_norm):
        '''Generates the next data window from the given index location i'''
        pass

    def normalise_windows(self, window_data, single_window=False):
        '''Normalise window with a base value of zero'''
        normalised_data = []
        window_data = [window_data] if single_window else window_data
        for window in window_data:
            normalised_window = []
            for col_i in range(window.shape[1]):
                p0 = float(window[0, col_i])
                normalised_col = [((float(pi) / p0) - 1) for pi in window[:, col_i]]
                normalised_window.append(normalised_col)
            normalised_window = np.array(normalised_window).T
            normalised_data.append(normalised_window)
        return np.array(normalised_data)

    def denormalise_windows(self, window_data, single_window=False):
        '''Normalise window with a base value of zero'''
        denormalised_data = []
        window_data = [window_data] if single_window else window_data
        for window in window_data:
            denormalised_window = []
            for col_i in range(window.shape[1]):
                p0 = window[0:, col_i]
                denormalised_col = [((float(ni) + 1) * p0) for ni in window[:, col_i]]
                denormalised_window.append(denormalised_col)
            denormalised_window = np.array(
                denormalised_window).T  # reshape and transpose array back into original multidimensional format
            denormalised_data.append(denormalised_window)
        return np.array(denormalised_data)


class CsvData(Loader):

    def __init__(self, filename, split, cols):
        super().__init__("CsvData")
        dataframe = pd.read_csv(filename, delimiter=";")
        i_split = int(len(dataframe) * split)
        self.data_train = dataframe[cols].values[:i_split]
        self.data_test = dataframe[cols].values[i_split:]
        self.len_train = len(self.data_train)
        self.len_test = len(self.data_test)

    def _load_from(self, filename, split, cols):
        dataframe = pd.read_csv(filename, delimiter=';')
        i_split = int(len(dataframe) * split)
        self.data_train = dataframe[cols].values[:i_split]
        self.data_test = dataframe[cols].values[i_split:]
        self.len_train = len(self.data_train)
        self.len_test = len(self.data_test)

    def get_test_data(self, seq_len, normalise):
        '''
        Create x, y test data windows
        Warning: batch method, not generative, make sure you have enough memory to
        load data, otherwise reduce size of the training split.
        '''
        data_windows = []
        for i in range(self.len_test - seq_len):
            data_windows.append(self.data_test[i:i + seq_len])

        data_windows = np.array(data_windows).astype(float)
        data_windows = self.normalise_windows(data_windows, single_window=False) if normalise else data_windows

        x = data_windows[:, :-1]
        y = data_windows[:, -1, [0, 1]]
        return x, y

    def get_train_data(self, seq_len, normalise):
        '''
        Create x, y train data windows
        Warning: batch method, not generative, make sure you have enough memory to
        load data, otherwise use generate_training_window() method.
        '''
        data_x = []
        data_y = []
        for i in range(self.len_train - seq_len):
            x, y = self.next_window(i, seq_len, normalise)
            data_x.append(x)
            data_y.append(y)
        return np.array(data_x), np.array(data_y)

    def train_batch_generator(self, seq_len, batch_size, normalise):
        '''Yield a generator of training data from filename on given list of cols split for train/test'''
        i = 0
        while i < (self.len_train - seq_len):
            x_batch = []
            y_batch = []
            for b in range(batch_size):
                if i >= (self.len_train - seq_len):
                    # stop-condition for a smaller final batch if data doesn't divide evenly
                    yield np.array(x_batch), np.array(y_batch)
                    i = 0
                x, y = self.next_window(i, seq_len, normalise)
                x_batch.append(x)
                y_batch.append(y)
                i += 1
            yield np.array(x_batch), np.array(y_batch)

    def next_window(self, i, seq_len, normalise):
        '''Generates the next data window from the given index location i'''
        window = self.data_train[i:i + seq_len]
        window = self.normalise_windows(window, single_window=True)[0] if normalise else window
        # de_window = self.denormalise_windows(window, single_window=True)[0] if normalise else window
        x = window[:-1]
        y = window[-1, [0]]
        return x, y


class Decorator(Loader):

    def __init__(self, component, name="Decorat"):
        """

        :type component: Loader
        """
        super().__init__(name)
        self._component = component


class FeatureEnrichedData(Decorator):

    def __init__(self, component="Dummy"):
        super().__init__(component, name="FeatureDecorat")
        self.returns_actions = None
        self.bid_data_train = None
        self.ask_data_train = None
        self.bid_data_test = None
        self.ask_data_test = None

    def _load_from(self, filename, split, cols):
        min_max_scaler = preprocessing.MinMaxScaler()
        dataframe = pd.read_csv(filename, delimiter=';', usecols=cols)
        volume_data = dataframe[['sell_vol', 'buy_vol']]
        self.returns_actions = dataframe[['return', 'action']]
        del dataframe['sell_vol']
        del dataframe['buy_vol']
        i_split = int(len(dataframe) * split)
        bid_df, ask_df = create_features(dataframe)
        sell_volume = min_max_scaler.fit_transform(volume_data['sell_vol'].values.reshape(-1, 1))
        buy_volume = min_max_scaler.fit_transform(volume_data['buy_vol'].values.reshape(-1, 1))
        bid_df['sell_volume'] = sell_volume
        ask_df['buy_volume'] = buy_volume

        self.bid_data_train = bid_df.values[:i_split]
        self.ask_data_train = ask_df.values[:i_split]
        self.bid_data_test = bid_df.values[i_split:]
        self.ask_data_test = ask_df.values[i_split:]

    def get_test_data(self, seq_len, should_norm):
        if Loader.__instancecheck__(self._component):
            return self._component.get_test_data(seq_len, should_norm)

    def get_train_data(self, seq_len, should_norm):
        if Loader.__instancecheck__(self._component):
            return self._component.get_train_data(seq_len, should_norm)

    def train_batch_generator(self, seq_len, batch_size, should_norm):
        if Loader.__instancecheck__(self._component):
            return self._component.train_batch_generator(seq_len, batch_size, should_norm)

    def next_window(self, i, seq_len, should_norm):
        if Loader.__instancecheck__(self._component):
            return self._component.next_window(i, seq_len, should_norm)

    def next_window_stream(self, i, seq_len, normalise):
        '''Generates the next data window from the given index location i'''
        window = self._component.data_train[i:i + seq_len]
        window = self.normalise_windows(window, single_window=True)[0] if normalise else window
        return window

    def next_bid_ask_window(self, i, seq_len, normalise):
        '''Generates the next data window from the given index location i'''
        window_ask = self.ask_data_train[i:i + seq_len]
        window_ask = self.normalise_windows(window_ask, single_window=True)[0] if normalise else window_ask

        window_bid = self.bid_data_train[i:i + seq_len]
        window_bid = self.normalise_windows(window_bid, single_window=True)[0] if normalise else window_bid

        return window_ask, window_bid

    def next_returns_actions_window(self, i, seq_len):
        window_ra = self.returns_actions[i:i + seq_len]
        return window_ra


#deprecated
class PlainData(Loader):
    """A class for loading and transforming data for the lstm model"""

    def __init__(self, filename, split, cols):
        # bid_df, ask_df = {}, {}
        super().__init__("PlainData")
        min_max_scaler = preprocessing.MinMaxScaler()
        dataframe = pd.read_csv(filename, delimiter=';', usecols=cols)
        volume_data = dataframe[['sell_vol', 'buy_vol']]
        self.ret_act_data = dataframe[['return', 'action']]
        del dataframe['sell_vol']
        del dataframe['buy_vol']
        i_split = int(len(dataframe) * split)
        bid_df, ask_df = create_features(dataframe)
        sell_volume = min_max_scaler.fit_transform(volume_data['sell_vol'].values.reshape(-1, 1))
        buy_volume = min_max_scaler.fit_transform(volume_data['buy_vol'].values.reshape(-1, 1))
        bid_df['sell_volume'] = sell_volume
        ask_df['buy_volume'] = buy_volume

        self.bid_data_train = bid_df.values[:i_split]
        self.ask_data_train = ask_df.values[:i_split]
        self.bid_data_test = bid_df.values[i_split:]
        self.ask_data_test = ask_df.values[i_split:]

        self.data_train = dataframe.values[:i_split]
        self.data_test = dataframe.values[i_split:]
        self.len_train = len(self.data_train)
        self.len_test = len(self.data_test)
        self.len_train_windows = None

    def next_window_stream(self, i, seq_len, normalise):
        '''Generates the next data window from the given index location i'''
        window = self.data_train[i:i + seq_len]
        window = self.normalise_windows(window, single_window=True)[0] if normalise else window
        return window

    def next_ba_window_stream(self, i, seq_len, normalise):
        '''Generates the next data window from the given index location i'''
        window_a = self.ask_data_train[i:i + seq_len]
        window_a = self.normalise_windows(window_a, single_window=True)[0] if normalise else window_a

        window_b = self.bid_data_train[i:i + seq_len]
        window_b = self.normalise_windows(window_b, single_window=True)[0] if normalise else window_b

        return window_a, window_b

    def next_ra_window_stream(self, i, seq_len):
        window_ra = self.ret_act_data[i:i + seq_len]
        return window_ra

    def normalise_windows(self, window_data, single_window=False):
        '''Normalise window with a base value of zero'''
        normalised_data = []
        window_data = [window_data] if single_window else window_data
        for window in window_data:
            normalised_window = []
            for col_i in range(window.shape[1]):
                p0 = float(window[0, col_i])
                normalised_col = [((float(pi) / p0) - 1) for pi in window[:, col_i]]
                normalised_window.append(normalised_col)
            normalised_window = np.array(normalised_window).T
            normalised_data.append(normalised_window)
        return np.array(normalised_data)

#depricated
class OptimalActionDataLoader():
    """A class for loading and transforming data for the lstm model"""

    def __init__(self, filename, split, cols):
        # bid_df, ask_df = {}, {}
        min_max_scaler = preprocessing.MinMaxScaler()
        dataframe = pd.read_csv(filename, delimiter=';', usecols=cols)
        volume_data = dataframe[['sell_vol', 'buy_vol']]
        self.act_data = dataframe[['action']]
        del dataframe['sell_vol']
        del dataframe['buy_vol']
        del dataframe['action']
        i_split = int(len(dataframe) * split)

        sell_volume = min_max_scaler.fit_transform(volume_data['sell_vol'].values.reshape(-1, 1))
        buy_volume = min_max_scaler.fit_transform(volume_data['buy_vol'].values.reshape(-1, 1))
        dataframe['sell_volume'] = sell_volume
        dataframe['buy_volume'] = buy_volume

        self.data_train = dataframe.values[:i_split]
        self.data_test = dataframe.values[i_split:]
        self.len_train = len(self.data_train)
        self.len_test = len(self.data_test)
        self.len_train_windows = None

    def next_window_stream(self, i, seq_len, normalise):
        '''Generates the next data window from the given index location i'''
        window = self.data_train[i:i + seq_len]
        window = self.normalise_windows(window, single_window=True)[0] if normalise else window
        return window

    def next_opt_act_window_stream(self, i, seq_len):
        window_ra = self.act_data[i:i + seq_len]
        return window_ra

    def normalise_windows(self, window_data, single_window=False):
        '''Normalise window with a base value of zero'''
        normalised_data = []
        window_data = [window_data] if single_window else window_data
        for window in window_data:
            normalised_window = []
            for col_i in range(window.shape[1]):
                p0 = float(window[0, col_i])
                normalised_col = [((float(pi) / p0) - 1) for pi in window[:, col_i]]
                normalised_window.append(normalised_col)
            normalised_window = np.array(normalised_window).T
            normalised_data.append(normalised_window)
        return np.array(normalised_data)
