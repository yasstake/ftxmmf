import pandas as pd
import numpy as np
from logger.util import Action
import matplotlib as plt

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
        # print(d[0], ':', d[1], end=', ')
        if volume < v:
            return d[0]

    # print('NO EXECUTE')
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
    return df[df[ACTION] == Action.UPDATE_BIT]


def _filter_ask(df):
    return df[df[ACTION] == Action.UPDATE_ASK]


class History:
    def __init__(self, file=None):
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
        self.dollar_bar = None
        self.q_window = Q_WINDOW

        if file:
            self._load(file)

    def load(self, file):
        if self.log_data is not None:
            append_history = History(file)
            self.merge_log(append_history)
            self.merge_dollar_bar(append_history)
        else:
            self._load(file)

    def loads(self, files):
        for file in files:
            history = History(file)
            self.merge_log(history)

    def _load(self, file):
        names = (ACTION, TIME, SEQ, PRICE, VOLUME, CHECKSUM)
        df = pd.read_csv(file, names=names)
        df[TIME] = pd.to_datetime(df[TIME] * 1000)
        df[PRICE] = df[PRICE] / 10

        self.log_data = df
        self.update_log_time_frame()

    def merge(self, history):
        self.merge_log(history)
        self.merge_dollar_bar(history)

    def merge_log(self, history):
        # merge row log
        cut_time = history.start_time
        self.trim_after(cut_time)
        df = pd.concat([self.log_data, history.log_data], ignore_index=True)
        df.reset_index(inplace=True, drop=True)
        self.log_data = df
        self.update_log_time_frame()

    def merge_dollar_bar(self, history):
        # merge dollar bar
        if self.dollar_bar is None:
            self.setup_dollar_bar()

        if history.dollar_bar is None:
            history.setup_dollar_bar()

        cut_time = history.dollar_bar.iloc[0]['time_stamp']
        df = self.dollar_bar[(self.dollar_bar['time_stamp'] < cut_time)]
        df.reset_index(inplace=True, drop=True)
        self.dollar_bar = df
        df = pd.concat([self.dollar_bar, history.dollar_bar], ignore_index=True)
        df.reset_index(inplace=True, drop=True)
        self.dollar_bar = df

    def chop_max_time_width(self):
        """
        TODO: chop at partial event
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

        partial = df[df[ACTION] == Action.PARTIAL]
        first_partial_rec = partial.index[0]
        last_rec = df.shape[0] - 1

        self.start_time = df.loc[first_partial_rec]['time']
        self.end_time = df.loc[last_rec]['time']
        self.log_data = self.log_data[first_partial_rec:]

    def trim_after(self, end_time):
        df = self.log_data[(self.log_data['time'] < end_time)]
        df.reset_index(inplace=True, drop=True)
        self.log_data = df
        self.update_log_time_frame()

    def get_board(self, time):
        bit, ask = self._get_board_df(time)
        bit_board = board_df_to_list(bit, True)
        ask_board = board_df_to_list(ask, False)

        return bit_board, ask_board

    def get_board_prices(self, time, volume):
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


    def _get_board_df(self, time):
        """
        :param time:
        :return: asks, bits
        """
        df = self._select_board_df(time)

        bit = df[df[ACTION] == Action.UPDATE_BIT]
        bit = bit.drop_duplicates(subset=PRICE, keep='last')
        bit = bit[bit[VOLUME] != 0]
        if len(bit) == 0:
            print('too short bit', time)

        ask = df[df[ACTION] == Action.UPDATE_ASK]
        ask = ask.drop_duplicates(subset=PRICE, keep='last')
        ask = ask[ask[VOLUME] != 0]
        if len(ask) == 0:
            print('too short ask', time)

        return bit, ask

    def _select_board_df(self, time):
        time = timestamp(time)
        # start_time = time - self.board_time_width
        df = _chop_log_data(self.log_data, end=time)
        partial_index = self._get_last_partial_index(df)
        if partial_index is None:
            print(self.board_time_width)
            print('short->', time, self.start_time, self.end_time)
        df = df.iloc[partial_index:]

        return df

    def _get_last_partial_index(self, df):
        """
        find and return last partial index
        :param df: data frame to search
        :return: partial index no of df
        """
        partial = df[df[ACTION] == Action.PARTIAL]

        if len(partial) == 0:
            print('TOO SHORT DATA(partial record is not found)')
            return None

        partial = partial[-1:]
        partial_index = partial.index[0]
        return partial_index

    def _select_execute_df(self, start, end):
        df = _chop_log_data(self.log_data, start=start, end=end)
        long_df = _filter_long(df)
        short_df = _filter_short(df)

        long_df = long_df[[PRICE, VOLUME]].groupby([PRICE], as_index=False).sum()
        short_df = short_df[[PRICE, VOLUME]].groupby([PRICE], as_index=False).sum()

        return long_df, short_df

    def select_execute(self, start, end):
        long_df, short_df = self._select_execute_df(start, end)

        long_list = execute_df_to_list(long_df, True)
        short_list = execute_df_to_list(short_df, False)

        return long_list, short_list

    def _get_board_price(self, time):
        bit, ask = self.get_board(time)

        bit_price = bit[0][0]
        bit_volume = bit[0][1]
        ask_price = ask[0][0]
        ask_volume = ask[0][1]

        return bit_price, bit_volume, ask_price, ask_volume

    def market_price(self, time, volume=0):
        """
        TODO: add execution delay
        :param time: unix_time(UTC) to select
        :return: board price(ask_price, ask_size, bit_price, bit_size)
        """
        bit, ask = self.get_board(time)

        try:
            bit_price = bit[0][0]
            bit_volume = bit[0][1]
            ask_price = ask[0][0]
            ask_volume = ask[0][1]
        except IndexError:
            print('get board error', bit, ask)

        # print('bit->')
        bit_execute_price = execute_price(ask, volume)
        # print('ask->')
        ask_execute_price = execute_price(bit, volume)

        return _calc_execute_price(bit_price, bit_execute_price, ask_price, ask_execute_price)

    def limit_price(self, time, volume=0, window=180, delay=3):
        '''
        TODO: adding execution time.
        :param time:
        :param volume:
        :param window:
        :param delay: delay time to execute
        :return: bit_price, ask_price
        '''
        bit, ask = self.get_board(time)
        bit_price = bit[0][0]
        bit_volume = bit[0][1]
        ask_price = ask[0][0]
        ask_volume = ask[0][1]

        # bit_price, bit_volume, _, ask_price, ask_volume, _ = self.get_board_prices(time, volume=0)

        bit_execute_price, ask_execute_price = self.calc_limit_price(time+pd.Timedelta(seconds=delay),
                                                                     volume + bit_volume, volume + ask_volume, window)

        # print('bit->', bit_execute_price, ask_price)
        if (bit_execute_price is None) or (bit_execute_price < ask_price):
            limit_bit_price = None
        else:
            limit_bit_price = ask_price

        # print('ask->', ask_execute_price, bit_price)
        if (ask_execute_price is None) or (bit_price < ask_execute_price):
            limit_ask_price = None
        else:
            limit_ask_price = bit_price

        return limit_bit_price, limit_ask_price

    def calc_limit_price(self, time, long_volume=0, short_volume=0, window=180, delay=1):
        time = time + pd.Timedelta(seconds=delay)
        window = pd.Timedelta(seconds=window)
        long, short = self.select_execute(time, time+window)

        long_execute_price = execute_price(long, long_volume)
        short_execute_price = execute_price(short, short_volume)

        return long_execute_price, short_execute_price

    def setup_dollar_bar(self, tick_vol=5):
        """
        TODO: if tick_vol is smaller than one trade, missing bar is generated.
        setup dollar bar.
        :param tick_vol: average volume of each bar.
        :return: dollar bar df.
        """
        df = _filter_execute(self.log_data).copy()
        df.loc[df[ACTION].isin([Action.TRADE_SHORT, Action.TRADE_SHORT_LIQUID]), 'sell_volume'] = df['volume']
        df.loc[df[ACTION].isin([Action.TRADE_LONG, Action.TRADE_LONG_LIQUID]), 'buy_volume'] = df['volume']
        max_vol = df[VOLUME].sum()
        start = int(max_vol + tick_vol) - max_vol

        ticks = np.arange(start, max_vol, tick_vol)
        df['sum'] = df[VOLUME].cumsum()
        bins = pd.cut(df['sum'], ticks)
        df = df.groupby(bins).agg({'time': 'last', 'price': ['first', 'last', 'max', 'min'],
                                   'sell_volume': 'sum', 'buy_volume': 'sum'}, axis=1)
        df.columns = ['time_stamp', 'open', 'close', 'high', 'low', 'sell_volume', 'buy_volume']

        # TODO: check drop is OK or Not for missing record
        df.dropna(inplace=True)
        df.reset_index(drop=True, inplace=True)
        df.index.name = 'time'
        df = df[['time_stamp', 'open', 'close', 'high', 'low', 'sell_volume', 'buy_volume']]

        df['bs_ratio'] = df['buy_volume'] / (df['sell_volume']+df['buy_volume'])
        self.dollar_bar = df

        '''
        self.dollar_bar['market_buy'] = None
        self.dollar_bar['market_sell'] = None
        self.dollar_bar['limit_buy'] = None
        self.dollar_bar['limit_sell'] = None
        '''

        return df

    def _calc_order_price(self, row, delay=ORDER_DELAY, window=ORDER_WINDOW, volume=0.1):
        time = row['time_stamp']
        if not time:
            print(time)

        bit_market_price, ask_market_price = self.market_price(time, volume=volume)
        bit_execute_price, ask_execute_price = self.limit_price(time, delay=delay, volume=volume, window=window)

        return pd.Series([bit_market_price, ask_market_price,
                          bit_execute_price, ask_execute_price])

    def update_price(self):
        self.dollar_bar[['market_buy', 'market_sell', 'limit_buy', 'limit_sell']] = \
             self.dollar_bar.apply(self._calc_order_price, axis=1)

    def _calc_q_value(self, row):
        '''
        calc Q value for each action
        TODO: trading free must be applied
        :param row:
        :return:
        '''
        time_stamp = row['time_stamp']

        market_buy = row['market_buy']
        market_sell = row['market_sell']
        limit_buy = row['limit_buy']
        limit_sell = row['limit_sell']

        dollar_bar = _chop_log_data(self.dollar_bar, start=time_stamp, end=time_stamp + pd.Timedelta(seconds=self.q_window),
                                    time_key='time_stamp')

        min_df = dollar_bar.min()
        max_df = dollar_bar.max()

        min_market_buy = min_df['market_buy']
        min_limit_buy = min_df['limit_buy']

        min_buy_price = min_market_buy
        if min_limit_buy and min_limit_buy < min_buy_price:
            min_buy_price = min_limit_buy

        max_market_sell = max_df['market_sell']
        max_limit_sell = max_df['limit_sell']

        max_sell_price = max_market_sell
        if max_limit_sell and max_market_sell < max_limit_sell:
            max_sell_price = max_limit_sell

        q_market_buy = max_sell_price - market_buy
        q_market_sell = market_sell - min_buy_price

        q_limit_buy = None
        if limit_buy:
            q_limit_buy = max_sell_price - limit_buy

        q_limit_sell = None
        if limit_sell:
            q_limit_sell = limit_sell - min_buy_price

        return pd.Series([q_market_buy, q_market_sell, q_limit_buy, q_limit_sell])

    def update_q_value(self):
        self.dollar_bar[['q_market_buy', 'q_market_sell', 'q_limit_buy', 'q_limit_sell']] = \
            self.dollar_bar.apply(self._calc_q_value, axis=1)

    def ochlv(self):
        df = _filter_execute(self.log_data).copy()
        df = df.set_index('time')
        df = df['price'].resample('m').agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'})

        return df



def load_file(file) -> History:
    '''
    create History object, load log file and return it!!
    :param file: path to file
    :return history object
    '''
    return History(file)



if __name__ == "__main__":
    import doctest
    doctest.testmod()
