import glob
import numpy as np
import pandas as pd
from logger.util import Action

TIME = 'time'
SEQ = 'sequence'
ACTION = 'action'
PRICE = 'price'
VOLUME = 'volume'
CHECKSUM = 'checksum'

PARTIAL_TIME = 600  # sec
EXEC_WINDOW =  600  # 10 min

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
    return df[df[ACTION].isin([Action.TRADE_BUY, Action.TRADE_BUY_LIQUID])]


def _filter_short(df):
    return df[df[ACTION].isin([Action.TRADE_SELL, Action.TRADE_SELL_LIQUID])]


def _filter_execute(df):
    return df[df[ACTION].isin([Action.TRADE_SELL, Action.TRADE_BUY_LIQUID,
                               Action.TRADE_BUY, Action.TRADE_SELL_LIQUID])]


def _filter_bit(df):
    return df[df[ACTION].isin([Action.UPDATE_BUY])]


def _filter_ask(df):
    return df[df[ACTION].isin([Action.UPDATE_SELL])]


def _filter_partial(df):
    return df[df[ACTION].isin([Action.PARTIAL])]


class Trade:
    def __init__(self):
        self.log_data = None
        self.start_time = None
        self.end_time = None
        self.short_log = None
        self.long_log = None
        self.exec_log = None
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
        self.exec_log = _filter_execute(self.log_data)
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

    def get_board(self, time):
        bit, ask = self._get_board_df(time)
        bit_board = board_df_to_list(bit, False)
        ask_board = board_df_to_list(ask, True)

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
        bit_edge_price, bit_edge_volume, market_buy, \
            ask_edge_price, ask_edge_volume, market_sell = self.calc_board_prices(time, volume)

        long_volume = ask_edge_volume + volume
        short_volume = bit_edge_volume + volume

        limit_buy, limit_sell = self.calc_limit_price(time, long_volume=long_volume, short_volume=short_volume)

        if limit_buy and limit_buy < ask_edge_price:
            limit_buy = ask_edge_price
        else:
            limit_buy = None

        if limit_sell and bit_edge_price < limit_sell:
            limit_sell = bit_edge_price
        else:
            limit_sell = None

        return bit_edge_price, bit_edge_volume, ask_edge_price, ask_edge_volume, \
               market_buy, market_sell, limit_buy, limit_sell

    def calc_board_prices(self, time, volume):
        '''
        BID -> Sell
        ASK -> Buy

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

    def calc_limit_price(self, time, long_volume=1, short_volume=1, window=EXEC_WINDOW, delay=3):
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
        df[PRICE] = df[PRICE] / 10

        self.log_data = df
        self.update_log_time_frame()
        print(file, self.file_name(), self.start_time, self.end_time)

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

        self.log_data = self.log_data[(self.start_time <= self.log_data['time']) & \
                                      (self.log_data['time'] <= self.end_time)]


class TradeBar:
    def __init__(self):
        self.bar = None
        self.trade = None

    def setup_ochlv(self, trade: Trade):
        self.trade = trade
        df = trade.exec_log.copy()
        # df = df.set_index('time')
        df['time'] = df['time'].dt.ceil('20s')
        df.loc[df[ACTION].isin([Action.TRADE_SELL, Action.TRADE_SELL_LIQUID]), 'sell_volume'] = df['volume']
        df.loc[df[ACTION].isin([Action.TRADE_BUY, Action.TRADE_BUY_LIQUID]), 'buy_volume'] = df['volume']

        df = df.groupby('time').agg({'time': 'last', 'price': ['first', 'last', 'max', 'min'],
                                   'sell_volume': 'sum', 'buy_volume': 'sum'}, axis=1)
        df.columns = ['time_stamp', 'open', 'close', 'high', 'low', 'sell_volume', 'buy_volume']
        df.reset_index(drop=True, inplace=True)
        df.index.name = 'time'
        df = df[['time_stamp', 'open', 'close', 'high', 'low', 'sell_volume', 'buy_volume']]

        df['bs_ratio'] = df['buy_volume'] / (df['sell_volume']+df['buy_volume'])

        self.bar = df

    def setup_dollar_bar(self, trade: Trade, var_volume=1):
        self.trade = trade
        df = trade.exec_log.copy()
        # df = df.set_index('time')
        df['sum'] = df[VOLUME].cumsum()  # 1BTC for each bin
        df['sum'] = np.floor(df['sum'] / var_volume)
        df.loc[df[ACTION].isin([Action.TRADE_SELL, Action.TRADE_SELL_LIQUID]), 'sell_volume'] = df['volume']
        df.loc[df[ACTION].isin([Action.TRADE_BUY, Action.TRADE_BUY_LIQUID]), 'buy_volume'] = df['volume']

        df = df.groupby('sum').agg({'time': 'last', 'price': ['first', 'last', 'max', 'min'],
                                    'sell_volume': 'sum', 'buy_volume': 'sum'}, axis=1)
        df.columns = ['time_stamp', 'open', 'close', 'high', 'low', 'sell_volume', 'buy_volume']
        df.reset_index(drop=True, inplace=True)
        df.index.name = 'time'
        df = df[['time_stamp', 'open', 'close', 'high', 'low', 'sell_volume', 'buy_volume']]
        df['bs_ratio'] = df['buy_volume'] / (df['sell_volume']+df['buy_volume'])

        self.bar = df

    def _calc_order_price(self, row, delay=ORDER_DELAY, window=EXEC_WINDOW, volume=0.1):
        time = row['time_stamp']
        if not time:
            print(time)

        board_bit, board_bit_vol, board_ask, board_ask_vol, \
             long_price, short_price, bit_execute_price, ask_execute_price = \
             self.trade.calc_best_prices(time)

        return pd.Series([board_bit, board_bit_vol, board_ask, board_ask_vol, long_price, short_price,
                          bit_execute_price, ask_execute_price])

    def update_price(self, trade: Trade = None):
        if trade:
            self.trade = Trade

        self.bar[['board_bit', 'board_bit_vol', 'board_ask', 'board_ask_vol',
                  'market_buy', 'market_sell', 'limit_buy', 'limit_sell']] = \
             self.bar.apply(self._calc_order_price, axis=1)

    '''
    def update_indicator(self, indicator_maker: IndicatorMaker):
        self.dollar_bar[indicator_maker.names] = \
             self.dollar_bar.apply(indicator_maker.update, axis=1)
    '''

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

        bar = _chop_log_data(self.bar, start=time_stamp, end=time_stamp + pd.Timedelta(seconds=Q_WINDOW),
                                    time_key='time_stamp')

        min_market_buy = bar['market_buy'].min()
        min_limit_buy = bar['limit_buy'].max()
        max_market_sell = bar['market_sell'].min()
        max_limit_sell = bar['limit_sell'].max()

        min_buy_price = min_market_buy
        if min_limit_buy and min_limit_buy < min_buy_price:
            min_buy_price = min_limit_buy

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
        self.bar[['q_market_buy', 'q_market_sell', 'q_limit_buy', 'q_limit_sell']] = \
              self.bar.apply(self._calc_q_value, axis=1)
