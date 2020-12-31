import unittest
from exchange.log import Trade
from exchange.log import TradeBar
from exchange.log import timestamp
import pandas as pd

class MyTestCase(unittest.TestCase):
    def log_load(self):
        self.log_loader = Trade()
        self.log_loader.append('../../DATA/BB/05/BB-2020-05-09T06-16-23.367761Z.log.gz')
        self.log_loader.append('../../DATA/BB/05/BB-2020-05-09T06-17-17.496249Z.log.gz')
        self.log_loader.append('../../DATA/BB/05/BB-2020-05-09T07-09-35.132396Z.log.gz')
        self.log_loader.append('../../DATA/BB/05/BB-2020-05-09T08-00-27.465324Z.log.gz')

        self.log_loader.update_logs()

    def test_load(self):
        self.log_load()

        print('bit')
        print(self.log_loader.bit_log)
        print('ask')
        print(self.log_loader.ask_log)
        print('short')
        print(self.log_loader.short_log)
        print('long')
        print(self.log_loader.long_log)

    def test_partial_index(self):
        self.log_load()

        print("---")
        print(self.log_loader.partial_log)
        print(self.log_loader.bit_log.loc[779:])
        print("---")
        print(self.log_loader.last_partial_index(self.log_loader.end_time))
        print("---")
        print(self.log_loader.last_partial_index(self.log_loader.start_time))
        print("---")
        print(self.log_loader.last_partial_index(self.log_loader.start_time+pd.Timedelta('1 h')))

    def test_partial_index2(self):
        self.log_load()

        partial_index = self.log_loader.last_partial_index(self.log_loader.end_time)
        print(partial_index)
        print(self.log_loader.ask_log.head())
        bit, ask = self.log_loader.get_board(self.log_loader.end_time)



        print(bit.head())
        print(ask.head())

    def test_partial_index3(self):
        self.log_load()

        df = self.log_loader.cut_partial_df(self.log_loader.ask_log, self.log_loader.end_time)
        print(df)

        df = self.log_loader.cut_partial_df(self.log_loader.bit_log, self.log_loader.end_time)
        print(df)


    def test_get_board(self):
        self.log_load()

        bit, ask = self.log_loader.get_board(self.log_loader.end_time)

        print(bit)

        print(ask)

    def test_board_prices(self):
        self.log_load()

        bit_price, bit_vol, bit_exec_price, ask_price, ask_vol, ask_exec_price = \
            self.log_loader.get_board_prices(self.log_loader.end_time, 1)

        print(bit_price, bit_vol, bit_exec_price, ask_price, ask_vol, ask_exec_price)

    def test_limit_prices(self):
        self.log_load()

        long_price, short_price = self.log_loader.calc_limit_price(self.log_loader.start_time, 1, 1)

        print(long_price, short_price)


    def test_limit_prices(self):
        self.log_load()

        long_price, short_price, bit_price, ask_price = self.log_loader.calc_best_prices(self.log_loader.start_time + pd.Timedelta('30m'))

        print(long_price, short_price, bit_price, ask_price)

        long_price, short_price, bit_price, ask_price = self.log_loader.calc_best_prices(self.log_loader.start_time + pd.Timedelta('31m'))

        print(long_price, short_price, bit_price, ask_price)

        long_price, short_price, bit_price, ask_price = self.log_loader.calc_best_prices(self.log_loader.start_time + pd.Timedelta('32m'))

        print(long_price, short_price, bit_price, ask_price)


    def test_log_ohlcv_update(self):
        self.log_load()
        bar = TradeBar()
        bar.setup_ochlv(self.log_loader)
        print(bar.bar)
        bar.update_price()

        print(bar.bar['open'])
        print(bar.bar['close'])
        print(bar.bar['high'])
        print(bar.bar['low'])

        pd.set_option('display.max_columns', 100)
        pd.set_option('display.max_rows', 500)
        print(bar.bar)

    def test_log_dollarbar(self):
        self.log_load()
        bar = TradeBar()
        bar.setup_dollar_bar(self.log_loader, 1)
        bar.update_price()

        print(bar.bar['open'])
        print(bar.bar['close'])
        print(bar.bar['high'])
        print(bar.bar['low'])

        pd.set_option('display.max_columns', 100)
        print(bar.bar)




if __name__ == '__main__':
    unittest.main()
