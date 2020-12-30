import glob
import pandas as pd
from logger.util import Action

TIME = 'time'
SEQ = 'sequence'
ACTION = 'action'
PRICE = 'price'
VOLUME = 'volume'
CHECKSUM = 'checksum'

PARTIAL_TIME = 600  # sec
ORDER_WINDOW = 360
Q_WINDOW = 360 * 2
ORDER_DELAY = 3


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


def board_df_to_list(df, ascending=True):
    """
    make [(price, volume),,,,] array
    :param df:
    :param reverse:
    :return:
    """
    df = df[[PRICE, VOLUME]].sort_values(PRICE, ascending=ascending)
    return df.values.tolist()

def execute_df_to_list(df, ascending=False):
    df = df[[PRICE, VOLUME]].sort_values(PRICE, ascending=ascending)
    return df.values.tolist()

def _chop_log_data(df, *, start=None, end=None, time_key=TIME):
    """
    chop log data as specified time frame
    :param df: pandas dataframe
    :param start: start time in EPOC us
    :param end: end time in EPOC us
    :return: new chopped data frame
    """
    start = timestamp(start)
    end = timestamp(end)

    if start and end:
        df = df[(start < df[time_key]) & (df[time_key] <= end)]
    elif (start is None) or (start <= timestamp(0)):
        df = df[df[time_key] <= end]
    elif end is None:
        df = df[start < df[time_key]]
    else:
        print('ERROR param　error chop_log_data')

    if len(df) == 0:
        print('chop too short', start, end)
        # raise str('error')

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


def _calc_execute_price(bit_price, bit_execute_price, ask_price, ask_execute_price):
    """
    calc prices to be expected
    :param bit_price: bit price by user
    :param bit_execute_price: best executed price(bit)
    :param ask_price: ask price by user
    :param ask_execute_price: best executed price(ask)
    :return:
    >>> _calc_execute_price(100, 100, 101, 101)
    (100, 101)
    >>> _calc_execute_price(100, 99, 101, 100)
    (100, 100)
    >>> _calc_execute_price(100, 101, 101, 102)
    (101, 101)
    """
    if bit_price < bit_execute_price:
        bit_price = bit_execute_price

    if ask_execute_price < ask_price:
        ask_price = ask_execute_price

    return bit_price, ask_price


def _filter_long(df):
    return df[df[ACTION].isin([Action.TRADE_LONG, Action.TRADE_LONG_LIQUID])]


def _filter_short(df):
    return df[df[ACTION].isin([Action.TRADE_SHORT, Action.TRADE_SHORT_LIQUID])]


def _filter_execute(df):
    return df[df[ACTION].isin([Action.TRADE_SHORT, Action.TRADE_SHORT_LIQUID,
                                         Action.TRADE_LONG, Action.TRADE_SHORT_LIQUID])]


def _filter_bit(df):
    return df[df[ACTION].isin([Action.UPDATE_BIT])]


def _filter_ask(df):
    return df[df[ACTION].isin([Action.UPDATE_ASK])]

def _filter_partial(df):
    return df[df[ACTION].isin([Action.PARTIAL])]



class Trade:
    def __init__(self):
        self.log_data = None
        self.start_time = None
        self.end_time = None
        self.short_log = None
        self.long_log = None
        self.bit_log = None
        self.ask_log = None
        self.partial_log = None
        self.partial_time_width = pd.Timedelta('1 h')

    def append_directory(self, log_directory):
        for file_path in sorted(glob.glob(log_directory)):
            print(file_path)
            self.append(file_path)

    def append(self, log_file):
        if self.log_data is not None:
            log = Trade()
            log._load(log_file)
            self.merge_log(log)
        else:
            self._load(log_file)

    def update_logs(self):
        self.short_log = _filter_short(self.log_data)
        self.long_log = _filter_long(self.log_data)
        self.bit_log = _filter_bit(self.log_data)
        self.ask_log = _filter_ask(self.log_data)
        self.partial_log = _filter_partial(self.log_data)

    def last_partial_index(self, time):
        '''
        get partial index before and after one rec accoding to time
        :param time:
        :return: before_index, after_idnex
        '''
        df = self.partial_log
        # df = df[((time - self.partial_time_width) < df[TIME]) & (df[TIME] <= time)]
        df = df[df[TIME] <= time]

        if len(df) == 0:
            print('TOO SHORT DATA(partial record is not found)')
            return None

        df = df[-1:]

        df = self.partial_log.loc[df.index[0]:].head(2)

        if 1 < len(df):
            return df.index[0], df.index[1]
        elif 1 == len(df):
            return df.index[0], None
        else:
            print('[error] partial index not found')
            return None

    def cut_partial_df(self, df, time):
        index_before, index_after = self.last_partial_index(time)
        df = df.loc[index_before:index_after]
        df = df[df[TIME] < time]

        return df

    def update_tick_board(self):
        pass

    def get_board(self, time):
        bit, ask = self._get_board_df(time)
        bit_board = board_df_to_list(bit, True)
        ask_board = board_df_to_list(ask, False)
        return bit_board, ask_board

    def _get_board_df(self, time):
        bit = self.cut_partial_df(self.bit_log, time)
        bit = bit.drop_duplicates(subset=PRICE, keep='last')
        bit = bit[bit[VOLUME] != 0]

        ask = self.cut_partial_df(self.ask_log, time)
        ask = ask.drop_duplicates(subset=PRICE, keep='last')
        ask = ask[ask[VOLUME] != 0]

        return bit, ask

    def calc_best_prices(self, time, volume=1):
        bit_edge_price, bit_edge_volume, bit_execute_price, \
            ask_edge_price, ask_edge_volume, ask_execute_price = self.calc_board_prices(time, volume)

        long_price, short_price = self.calc_limit_price(time)

        if long_price and long_price < bit_edge_price:
            long_price = None

        if short_price and ask_edge_price < short_price:
            short_price = None

        return long_price, short_price, bit_execute_price, ask_execute_price

    def calc_board_prices(self, time, volume):
        '''

        :param time:
        :param volume:
        :return: bit_edge_price, bit_edge_volume, bit_execute_price, ask_edge_price, ask_edge_volume, ask_execute_price
        '''
        bit, ask = self.get_board(time)
        # print('bit array->', bit)
        # print('ask array->', ask)
        try:
            bit_edge_price = bit[0][0]
            bit_edge_volume = bit[0][1]
            ask_edge_price = ask[0][0]
            ask_edge_volume = ask[0][1]
        except IndexError:
            print('Index error', time)
            print('bit->', bit)
            print('ask->', ask)

        bit_execute_price = execute_price(ask, volume)
        ask_execute_price = execute_price(bit, volume)

        return bit_edge_price, bit_edge_volume, bit_execute_price,\
               ask_edge_price, ask_edge_volume, ask_execute_price

    def calc_limit_price(self, time, long_volume=0, short_volume=0, window=180, delay=1):
        time = time + pd.Timedelta(seconds=delay)
        window = pd.Timedelta(seconds=window)
        long_df = _chop_log_data(self.long_log, start=time, end=time+window)
        short_df = _chop_log_data(self.short_log, start=time, end=time+window)

        long_df = long_df[[PRICE, VOLUME]].groupby([PRICE], as_index=False).sum()
        short_df = short_df[[PRICE, VOLUME]].groupby([PRICE], as_index=False).sum()

        long_list = execute_df_to_list(long_df, True)
        short_list = execute_df_to_list(short_df, False)

        long_execute_price = execute_price(long_list, long_volume)
        short_execute_price = execute_price(short_list, short_volume)

        return long_execute_price, short_execute_price

    def file_name(self):
        """

        """
        t1 = self.start_time
        t2 = self.end_time

        return t1.strftime('%Y%m%d%H-%m%S--') + t2.strftime('%Y%m%d%H-%m%S')

    def dump(self):
        self.log_data.to_csv('./out.csv.gz')

    def _load(self, file):
        names = (ACTION, TIME, SEQ, PRICE, VOLUME, CHECKSUM)
        df = pd.read_csv(file, names=names)
        df[TIME] = pd.to_datetime(df[TIME] * 1000)

        self.log_data = df
        self.update_log_time_frame()
        print(file, self.file_name())

    def trim_after(self, end_time):
        df = self.log_data[(self.log_data['time'] < end_time)]
        df.reset_index(inplace=True, drop=True)
        self.log_data = df
        self.update_log_time_frame()

    def merge_log(self, log):
        # merge row log
        cut_time = log.start_time
        self.trim_after(cut_time)
        df = pd.concat([self.log_data, log.log_data], ignore_index=True)
        df.reset_index(inplace=True, drop=True)
        self.log_data = df
        self.update_log_time_frame()

    def update_log_time_frame(self):
        """
        initialize start_time and end_time accroding to the trade log.
        """
        df = self.log_data

        partial = df[df[ACTION] == Action.PARTIAL]
        first_partial_rec = partial.index[0]
        last_rec = df.shape[0] - 1

        self.start_time = df.loc[first_partial_rec]['time']
        self.end_time = df.loc[last_rec]['time']
        self.log_data = self.log_data[first_partial_rec:]
