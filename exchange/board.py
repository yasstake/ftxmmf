import pandas as pd
from logger.util import Action

TIME = 'time'
INDEX = 'index'
ACTION = 'action'
PRICE = 'price'
SIZE = 'size'
CHECKSUM = 'checksum'

PARTIAL_TIME = 600  # sec


'''


'''

class History:
    def __init__(self):
        self.log_data = None
        self.start_time = None
        self.end_time = None
        self.partial_time_width = pd.Timedelta('10 m')
        self.board_time_width = pd.Timedelta('1 d')

    def _chop_log_data(self, df, *, start=None, end=None):
        if start and end:
            df = df[(start < df[TIME] & df[TIME] < end)]
        elif start is None:
            df = df[df[TIME] < end]
        elif end is None:
            df = df[start < df[TIME]]
        else:
            print('ERROR param　error chop_log_data')

        return df

    def chop_max_time_width(self):
        one_day_before = self.end_time - self.board_time_width
        self.log_data = self._chop_log_data(self.log_data, start=one_day_before)
        self.update_log_time_frame()

    def update_log_time_frame(self):
        df = self.log_data
        self.start_time = df.head(1).iat[0, 1]
        self.end_time = df.tail(1).iat[0, 1]

    def load_file(self, file):
        names = (ACTION, TIME, INDEX, PRICE, SIZE, CHECKSUM)
        df = pd.read_csv(file, names=names)
        df[TIME] = pd.to_datetime(df[TIME] * 1000)
        self.log_data = df
        self.update_log_time_frame()

    def get_board(self, time):
        """
        :param time:
        :return: asks, bits
        """
        start_time = time - self.board_time_width
        df = self._chop_log_data(self.log_data, start=start_time, end=time)
        partial = df[(df[ACTION] == Action.PARTIAL)]
        last_partial = partial.drop_duplicates(subset=ACTION, keep='last')
        partial_index = last_partial.index[0]
        df = df.iloc[partial_index:]






    def get_open_interest(self, time, window):
        """

        :param time:
        :param window:
        :return: long, short
        """

    def board_price(self, time):
        """
        :param time: unix_time(UTC) to select
        :return: 5 record of board price(ask_price, ask_size, bit_price, bit_size)x5 times
        """
        # bit_price, bit_size, ask_price, ask_size

    def is_success_short_order(self, time, price, size, time_window=60):
        pass

    def is_success_long_order(self, time, price, size, time_window=60):
        pass

    def calc_price(self, time, price, volume, action, limit, time_window=60):
        """
        calc execute price
        :param time:
        :param price:
        :param volume:
        :param action:
        :param limit:
        :param time_window:
        :return:
        """

    def calc_price_short_limit(self):
        pass
    def calc_price_short_market(self):
        pass
    def calc_price_long_limit(self):
        pass
    def calc_price_long_market(self):
        """
        calc market buy price
        The price will be the top edge of the order book if there is enough volume on the board.
        if there is not enough volume, the price will be slip two tick.
        :return: the target price. return None: if not found the data.
        """
        rec = self.select_order_book_price_with_retry(time)
        if rec is None:
            return None


'''
        sell_min, sell_volume, buy_max, buy_volume = rec

        if order_volume * 1.5 < sell_volume:  # 1.5 means enough margin
            return sell_min
        else:
            return sell_min + PRICE_UNIT





def calc_market_order_sell(self, time, order_volume):
    """
    calc market buy price
    basically the price will be the bottom edge of the order book if there is enough volume on the board.
    if there is not enough volume, the price will be slip two tick.
    :return: the target price. return None: if not found the data.
    """
    rec = self.select_order_book_price_with_retry(time)
    if rec is None:
        return None

    sell_min, sell_volume, buy_max, buy_volume = rec

    if order_volume * 1.5 < buy_volume:  # 2 means enough margin
        return buy_max
    else:
        return buy_max - PRICE_UNIT


def is_suceess_fixed_order_sell(self, time, price, volume, time_width=ORDER_TIME_WIDTH):
    sell_min, sell_volume, buy_max, buy_volume = self.select_order_book_price_with_retry(time)

    sql_count_sell_trade = 'select sum(volume) from buy_trade where  ? <= time and time < ? and ? <= price'

    end_time = time + time_width
    self.cursor.execute(sql_count_sell_trade, (time, end_time, price))

    amount = self.cursor.fetchone()

    if amount[0] is None:
        return False

    if volume + sell_volume < amount[0]:
        return price, end_time
    else:
        return False


def _calc_order_book_price_sell(self, time):
    rec = self.select_order_book_price_with_retry(time)
    if rec is None:
        return None

    sell_min, sell_volume, buy_max, buy_volume = rec
    return sell_min


MIN_ORDER_TIME = 60


def calc_fixed_order_sell(self, time, volume, time_width=ORDER_TIME_WIDTH):
    """
    :param time: unix time at the order
    :param price: order price
    :param volume: order volume
    :param time_width: wait to order (sec)
    :return: (price, time) to be executed nor None if not executed
    """
    price = self._calc_order_book_price_sell(time)

    window = LogDb.MIN_ORDER_TIME

    result = None
    while window <= time_width:
        result = self.is_suceess_fixed_order_sell(time, price, volume, window)
        if result:
            break
        window += LogDb.MIN_ORDER_TIME

    return result


def is_suceess_fixed_order_buy(self, time, price, volume, time_width=ORDER_TIME_WIDTH):
    sell_min, sell_volume, buy_max, buy_volume = self.select_order_book_price_with_retry(time)
    sql_count_sell_trade = 'select sum(volume) from sell_trade where  ? <= time and time < ? and price <= ?'

    end_time = time + time_width
    self.cursor.execute(sql_count_sell_trade, (time, end_time, price))
    amount = self.cursor.fetchone()

    if amount[0] is None:
        return None

    if volume + buy_volume < amount[0]:
        return price, end_time
    else:
        return None


def _calc_order_book_price_buy(self, time):
    rec = self.select_order_book_price_with_retry(time)
    if rec is None:
        return None

    sell_min, sell_volume, buy_max, buy_volume = rec
    return buy_max


def calc_fixed_order_buy(self, time, volume, time_width=ORDER_TIME_WIDTH):
    """
    :param time: time in unix time
    :param volume: order volume
    :param time_width: time to execute
    :return: (price, time) to be executed nor None if not executed.
    """
    price = self._calc_order_book_price_buy(time)
    window = LogDb.MIN_ORDER_TIME

    result = None

    while window <= time_width:
        result = self.is_suceess_fixed_order_buy(time, price, volume, window)
        if result:
            break
        window += LogDb.MIN_ORDER_TIME

    return result
'''
