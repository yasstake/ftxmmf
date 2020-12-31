import pandas as pd
from logger.util import Action

TIME = 'time'
INDEX = 'index'
ACTION = 'action'
PRICE = 'price'
SIZE = 'size'
N_SEC = 1_000_000_000


class Market:
    def __init__(self, time_window_min=2, execute_window_min=2):
        self.start_time = 0
        self.end_time = 0
        self.time_window = pd.DateOffset(minutes=time_window_min)
        self.execute_window = pd.DateOffset(minutes=execute_window_min)
        self.current_time = None
        self.df = None

        self.trade_long = None
        self.trade_short = None
        self.asks = None
        self.bits = None

    def set_start(self):
        self.current_time = self.start_time + self.time_window
        self.new_sec()

    def new_sec(self, datetime=None):
        if datetime:
            self.current_time = datetime
        else:
            self.current_time = self.current_time + pd.DateOffset(second=1)

        return self._check_current_time_is_ok()

    def _display_times(self):
        print('[start]', self.start_time)
        print('[end  ]', self.end_time)
        print('[diff ]', self.end_time - self.start_time)
        print('[now]', self.current_time)

    def _check_current_time_is_ok(self):
        if ((self.start_time + self.time_window < self.current_time) and
           (self.current_time < self.end_time + self.execute_window)):
            return True
        else:
            return False

    def get_bids_board(self):
        pass

    def get_asks_boards(self):
        pass

    def get_center_price(self):
        pass

    def calc_long_price_take(self, lot_size=1.0):
        pass

    def calc_long_price_make(self, lot_size=1.0):
        pass

    def calc_short_price_take(self, lot_size=1.0):
        pass

    def calc_short_price_make(self, lot_size=1.0):
        pass

    def load_csv(self, file):
        names = (ACTION, TIME, INDEX, PRICE, SIZE)

        self.df = pd.read_csv(file, names=names)
        self.df[TIME] = pd.to_datetime(self.df[TIME] * 1000)

        # first

        start = self.df.head(1).iat[0, 1]
        end = self.df.tail(1).iat[0, 1]

        self.start_time = pd.Timestamp(int(start.timestamp() + 1), unit='s')
        self.end_time = pd.Timestamp(int(end.timestamp() - 1), unit='s')

        self.set_start()
        check_data = self._check_current_time_is_ok()
        print(check_data)
        self._display_times()


    def update_data(self):
        data_after = self.df[(self.current_time <= self.df[TIME] & self.df[TIME] < self.current_time + self.time_window)]

        self.trade_long = data_after[
            ((data_after[ACTION] == Action.TRADE_BUY) | (data_after[ACTION] == Action.TRADE_BUY_LIQUID))]

        self.trade_short = data_after[((data_after[ACTION] == Action.TRADE_SELL) |
                                       (data_after[ACTION] == Action.TRADE_SELL_LIQUID))]

        data_before = self.df[(self.current_time - self.time_window <= self.df[TIME] & self.df[TIME] < self.current_time)]

        self.bits = self._select_board_info(data_before, Action.UPDATE_BUY)
        self.bits = self._select_board_info(data_before, Action.UPDATE_SELL)

    def _select_board_info(self, data_before, bit_or_ask):
        board = data_before[((data_before[ACTION] == Action.PARTIAL) | (data_before[ACTION] == bit_or_ask))]
        board = board.drop_duplicates(subset=PRICE, keep='last')
        last_partial_index = board[(board[ACTION] == Action.PARTIAL)].index[0]
        board = board[(last_partial_index < board.index)]

        return board


    def new_tick(self):
        pass

    def load_csv_line(self, line):
        pass

    def partial(self):
        pass

    def bit(self, price, size):
        pass

    def ask(self, price, size):
        pass

    def long(self, price, size):
        pass

    def short(self, price, size):
        pass


