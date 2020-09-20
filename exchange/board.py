import pandas as pd
import numpy as np
from logger.util import Action
import matplotlib as plt

TIME = 'time'
INDEX = 'index'
ACTION = 'action'
PRICE = 'price'
VOLUME = 'volume'
CHECKSUM = 'checksum'

PARTIAL_TIME = 600  # sec


def timestamp(time) -> pd.Timestamp:
    """
    >>> timestamp(1) == pd.Timestamp('1970-01-01 00:00:01')
    True
    >>> timestamp(pd.Timestamp('1970-01-01 00:00:02')) == pd.Timestamp('1970-01-01 00:00:02')
    True
    """
    if time is None:
        return time

    if type(time) is int:
        return pd.Timestamp(ts_input=time*1000_000_000)
    else:
        return time


def board_df_to_list(df, reverse=False):
    """
    make [(price, volume),,,,] array
    :param df:
    :param reverse:
    :return:
    """
    df = df[[PRICE, VOLUME]].sort_values(PRICE, ascending=reverse)
    return df.values.tolist()


def execute_df_to_list(df, reverse=False):
    df = df[[PRICE, VOLUME]].sort_values(PRICE, ascending=reverse)
    return df.values.tolist()


def _chop_log_data(df, *, start=None, end=None):
    """
    chop log data as specified time frame
    :param df: pandas dataframe
    :param start: start time in EPOC us
    :param end: end time in EPOC us
    :return: new chopped data frame
    """
    start = timestamp(start)
    end = timestamp(end)

    if (start is None) or (start <= timestamp(0)):
        df = df[df[TIME] <= end]
    elif end is None:
        df = df[start < df[TIME]]
    if start and end:
        df = df[(start < df[TIME]) & (df[TIME] <= end)]
    else:
        print('ERROR param　error chop_log_data')
    return df


def execute_price(data, volume):
    """
    calc price to consume volume
    :param data: [price, volume] list
    :param volume: volume to consume
    :return: the edge price
    """
    v = 0
    for d in data:
        v += d[1]
        if volume < v:
            return d[0]
    return None


class History:
    def __init__(self):
        """
        >>> history = History()
        >>> history is not None
        True
        """
        self.log_data = None
        self.start_time = None
        self.end_time = None
        self.partial_time_width = pd.Timedelta('10 m')
        self.board_time_width = pd.Timedelta('1 d')

    def chop_max_time_width(self):
        """

        :return:
        """
        one_day_before = self.end_time - self.board_time_width
        self.log_data = _chop_log_data(self.log_data, start=one_day_before)
        self.update_log_time_frame()

    def update_log_time_frame(self):
        """
        initialize start_time and end_time accroding to the trade log.
        """
        df = self.log_data
        self.start_time = df.head(1).iat[0, 1]
        self.end_time = df.tail(1).iat[0, 1]

    def get_board(self, time):
        bit, ask = self._get_board_df(time)
        bit_board = board_df_to_list(bit, False)
        ask_board = board_df_to_list(ask, True)

        return bit_board, ask_board

    def _get_board_df(self, time):
        """
        :param time:
        :return: asks, bits
        """
        df = self._select_board_df(time)
        bit = df[df[ACTION] == Action.UPDATE_BIT]
        ask = df[df[ACTION] == Action.UPDATE_ASK]
        bit = bit.drop_duplicates(subset=PRICE, keep='last')
        ask = ask.drop_duplicates(subset=PRICE, keep='last')

        return bit[bit[VOLUME] != 0], ask[ask[VOLUME] != 0]

    def _select_board_df(self, time):
        time = timestamp(time)
        start_time = time - self.board_time_width
        df = _chop_log_data(self.log_data, start=start_time, end=time)
        partial_index = self._get_last_partial_index(df)
        df = df.iloc[partial_index:]

        return df

    def _get_last_partial_index(self, df):
        """
        find and return last partial index
        :param df: data frame to search
        :return: partial index no of df
        """
        partial = df[df[ACTION] == Action.PARTIAL]
        last_partial = partial.drop_duplicates(subset=ACTION, keep='last')
        partial_index = last_partial.index[0]

        return partial_index

    def _filter_long(self, df):
        long_df = df[df[ACTION].isin([Action.TRADE_LONG, Action.TRADE_LONG_LIQUID])]
        return long_df

    def _filter_short(self, df):
        short_df = df[df[ACTION].isin([Action.TRADE_SHORT, Action.TRADE_SHORT_LIQUID])]
        return short_df

    def _filter_execute(self, df):
        df = df[df[ACTION].isin([Action.TRADE_SHORT, Action.TRADE_SHORT_LIQUID,
                                         Action.TRADE_LONG, Action.TRADE_SHORT_LIQUID])]
        return df

    def _select_execute_df(self, start, end):
        df = _chop_log_data(self.log_data, start=start, end=end)
        long_df = self._filter_long(df)
        short_df = self._filter_short(df)

        long_df = long_df[[PRICE, VOLUME]].groupby([PRICE], as_index=False).sum()
        short_df = short_df[[PRICE, VOLUME]].groupby([PRICE], as_index=False).sum()

        return long_df, short_df

    def select_execute(self, start, end):
        long_df, short_df = self._select_execute_df(start, end)
        long_list = execute_df_to_list(long_df, False)
        short_list = execute_df_to_list(short_df, True)

        return long_list, short_list

    def board_price(self, time, volume=0):
        """
        :param time: unix_time(UTC) to select
        :return: board price(ask_price, ask_size, bit_price, bit_size)
        """
        bit, ask = self.get_board(time)

        bit_price = bit[0][0]
        bit_volume = bit[0][1]
        ask_price = ask[0][0]
        ask_volume = ask[0][0]

        bit_execute_price, ask_execute_price = execute_price(bit, volume+bit_volume), execute_price(ask, volume+ask_volume)

        if bit_price < bit_execute_price:
            bit_price = None

        if ask_execute_price < ask_price:
            ask_price = None

        return bit_price, ask_price

    def market_price(self, time, volume=0, window=10):
        window = pd.Timedelta(seconds=window)
        long, short = self.select_execute(time, time+window)

        return execute_price(long, volume), execute_price(short, volume)

    def dollar_bar(self, tick_vol=5):
        df = self._filter_execute(self.log_data).copy()
        max_vol = df[VOLUME].sum()
        start = int(max_vol + tick_vol) - max_vol

        ticks = np.arange(start, max_vol, tick_vol)
        df['sum'] = df[VOLUME].cumsum()
        bins = pd.cut(df['sum'], ticks)
        df = df.groupby(bins).agg({'time': 'last', 'price': ['first', 'last', 'max', 'min']}, axis=1)
        df.columns = ['time_stamp', 'open', 'close', 'high', 'low']
        df = df.reset_index(drop=True)
        df.index.name = 'time'
        df = df[['time_stamp', 'open', 'close', 'high', 'low']]
        print(df)

        return df


def load_file(file) -> History:
    '''
    create History object, load log file and return it!!
    :param file: path to file
    :return history object
    '''
    names = (ACTION, TIME, INDEX, PRICE, VOLUME, CHECKSUM)
    df = pd.read_csv(file, names=names)
    df[TIME] = pd.to_datetime(df[TIME] * 1000)
    history = History()
    history.log_data = df
    history.update_log_time_frame()

    return history


if __name__ == "__main__":
    import doctest
    doctest.testmod()
