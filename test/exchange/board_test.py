import unittest
from exchange.board import *
import matplotlib.pyplot as plt
import numpy as np
from logger.util import OrderBook
import time

class MyTestCase(unittest.TestCase):
    def test_load_file(self):
        history = load_file('../../DATA/MERGE.log.gz')
        print(history.start_time)
        print(history.end_time)

    def test_load_file2(self):
        history = load_file('./testdata.csv')
        print(history.start_time)
        print(history.end_time)

        board = history._select_board_df(3)
        print(board)

        board = history._select_board_df(4)
        print(board)

    def test_get_board3(self):
        history = load_file('../../DATA/BF-TEST.log')
        print(history.start_time)
        print(history.end_time)

        bit, ask = history.get_board(history.start_time)
        print(bit[0][0])
        print(ask[0][0])
        print()

        bit, ask = history.market_price(history.start_time)
        print(bit)
        print(ask)

    def test_limited_price(self):
        history = load_file('../../DATA/BF-TEST.log')
        print(history.start_time)
        print(history.end_time)

        bit, ask = history.get_board(history.start_time)
        print(bit[0][0])
        print(ask[0][0])
        print()

        bit, ask = history.limit_price(history.start_time, window=10*60*60)
        print(bit)
        print(ask)

        print('--- short window---')
        bit, ask = history.limit_price(history.start_time, window=0.1)
        print(bit)
        print(ask)

        print('--- short window---')
        bit, ask = history.limit_price(history.start_time, window=0.8)
        print(bit)
        print(ask)

        print('--- short window---')
        bit, ask = history.limit_price(history.start_time, window=10)
        print(bit)
        print(ask)

        print('--- short window---')
        bit, ask = history.limit_price(history.start_time, window=100)
        print(bit)
        print(ask)


    def test_board_to_array(self):
        history = load_file('./testdata.csv')
        bit, ask = history._get_board_df(3)
        print(bit)
        bit_array = board_df_to_list(bit)
        print(bit_array)

    def test_select_execute_df(self):
        history = load_file('./testdata.csv')
        long, short = history._select_execute_df(1, 4)
        print(long)
        print(short)

    def test_select_execute(self):
        history = load_file('./testdata.csv')
        long, short = history.select_execute(1, 4)
        print(long)
        print(short)

    def test_select_execute(self):
        history = load_file('./testdata.csv')
        long, short = history.select_execute(1, 4)
        print(long)
        print(short)


    def test_select_data_frame(self):
        history = load_file('./testdata.csv')
        history._select_board_df(1)

    def test_get_last_partial_index(self):
        history = load_file('./testdata.csv')
        print(history.start_time)
        print(history.end_time)

        last_index = history._get_last_partial_index(history.log_data)
        print(last_index)

    def test_get_board_price(self):
        history = load_file('../../DATA/MERGE.log.gz')
        bit, ask = history.market_price(history.end_time - pd.Timedelta(seconds=60))
        print(bit, ask)

    def test_market_price(self):
        history = load_file('../../DATA/MERGE.log.gz')
        buy, sell = history.limit_price(history.end_time - pd.Timedelta(seconds=60))
        print(buy, sell)

    def test_execute_price(self):
        data = [[10, 1], [11, 2], [12, 3]]
        price = execute_price(data, 0)
        self.assertEqual(price, 10)

        price = execute_price(data, 0.9)
        self.assertEqual(price, 10)

        price = execute_price(data, 1)
        self.assertEqual(price, 11)

        price = execute_price(data, 1.5)
        self.assertEqual(price, 11)

        price = execute_price(data, 3)
        self.assertEqual(price, 12)

        data = [[12, 3], [11, 2], [10, 1]]
        price = execute_price(data, 0)
        self.assertEqual(price, 12)

        price = execute_price(data, 2.9)
        self.assertEqual(price, 12)

        price = execute_price(data, 3)
        self.assertEqual(price, 11)

        price = execute_price(data, 4.9)
        self.assertEqual(price, 11)

        price = execute_price(data, 5)
        self.assertEqual(price, 10)

    def test_info(self):
        history = load_file('../../DATA/MERGE.log.gz')
        df = history._filter_short(history.log_data)
        print(df.describe())

        df = history._filter_long(history.log_data)
        print(df.describe())

    def test_plot1(self):
        history = load_file('../../DATA/MERGE.log.gz')
        short_df = history._filter_short(history.log_data)
        long_df = history._filter_long(history.log_data)

        plt.scatter(long_df[TIME], long_df[PRICE])
        plt.scatter(short_df[TIME], short_df[PRICE])

        plt.show()

    def test_plot2(self):
        history = load_file('../../DATA/MERGE.log.gz')
        long_df = history._filter_long(history.log_data)
        short_df = history._filter_short(history.log_data)

        plt.hist(long_df[PRICE])
        plt.hist(short_df[PRICE])
        plt.show()

    def test_loop_df(self):
        history = load_file('../../DATA/MERGE.log.gz')
        df = history.log_data

        i = 0
        for loc, rec in df.iterrows():
            print(loc)
            i = i + 1
            if 100 < i:
                break

    def test_export_to_json(self):
        history = load_file('../../DATA/MERGE.log.gz')
        long_df = history._filter_long(history.log_data)
        short_df = history._filter_short(history.log_data)

        self.write_json(long_df, '../../chart/html/long.json')
        self.write_json(short_df, '../../chart/html/short.json')

    def test_print_rows(self):
        history = load_file('../../DATA/MERGE.log.gz')
        df = history.log_data

        t = time.time()
        for index, row in df.iterrows():
            pass

        print('iterrows->', time.time()-t)

    def test_get_board(self):
        history = History('../../DATA/MERGE.log.gz')
        board = history.get_board(history.start_time)
        print(board)

        print('--------')
        board = history.get_board(history.end_time)
        print(board)


    def test_dollar_bar1(self):
        history = load_file('../../DATA/MERGE.log.gz')

        df = history.setup_dollar_bar(tick_vol=10)

        plt.hist(df['close'])
        plt.show()

        plt.scatter(df.index, df['close'])
        plt.show()


    def test_doll_bar2(self):
        history = load_file('../../DATA/MERGE.log.gz')
        df = history._filter_execute(history.log_data).copy()

        TICK = 5

        max = df[VOLUME].sum()
        start = int(max + TICK) - max

        ticks = np.arange(start, max, TICK)
        df['sum'] = df[VOLUME].cumsum()
        print(df.tail())
        bins = pd.cut(df['sum'], ticks)
        print(bins)

        history = df.groupby(bins).agg({'time': 'last', 'price': ['first', 'last', 'max', 'min']}, axis=1)
        print(history)

    def test_export_execute(self):
        history = load_file('../../DATA/MERGE.log.gz')
        df = history._filter_execute(history.log_data)

        VOL = 20
        tick = 0
        last_tick = 0
        size = 0
        doll = 0
        t = 0
        o = h = l = c = None
        list_t = []
        list_o = []
        list_h = []
        list_l = []
        list_c = []
        d_df = pd.DataFrame()
        for index, row in df.iterrows():
            if row.action in [Action.TRADE_BUY, Action.TRADE_SELL_LIQUID,
                              Action.TRADE_SELL, Action.TRADE_SELL_LIQUID]:

                price = row.price
                if not o:
                    o = price
                if h is None or h < price:
                    h = price
                if l is None or price < l:
                    l = price

                size += row[VOLUME]
                doll += row[VOLUME]

                tick = int(doll / VOL)
                if last_tick != tick:
                    last_tick = tick
                    c = price
                    t = t + 1
                    list_t += [t]
                    list_o += [o]
                    list_c += [c]
                    list_h += [h]
                    list_l += [l]
                    o = c = h = l = None

        d_df = pd.DataFrame({'time': list_t, 'open': list_o, 'close': list_c,
                             'high': list_h, 'low': list_l},
                            columns=['time', 'open', 'close', 'high', 'low'])
        print(d_df)

        d_df.to_json('d.json', orient='records')

    def test_update_price(self):
        history = load_file('../../DATA/MERGE.log.gz')
        history.setup_dollar_bar()

        df = history.dollar_bar

        print(df)

        print(df[df['time_stamp'].isnull()])


    def write_json(self, df, file):
        df = df[[TIME, PRICE]]
        df = df.rename(columns={VOLUME: 'value'})

        with open(file, mode='w') as f:
            f.write('[')

            last_time = 0
            not_first = False
            for r in df.itertuples(name=None):
                time = int(r[1].value / 1000_000_000)
                if last_time == time:
                    continue

                last_time = time
                if not_first:
                    f.write(',')
                f.write('{"time":')
                f.write(str(time))
                f.write(',')
                f.write('"value":')
                f.write(str(int(r[2]/10)))
                f.write('}')
                not_first = True
            f.write(']')

    def test_update_q_value(self):
        '''
        :return:
        '''
        #history = load_file('../../DATA/MERGE.log.gz')    # NG
        history = load_file('../../MERGE-2020-05-04.log.gz') # OK
        history.setup_dollar_bar()

        history.update_price()
        #history.update_q_value()

        print(history.dollar_bar)

    def test_update_board(self):
        history = load_file('../../DATA/MERGE.log.gz') # OK

        order_book = OrderBook()
        df = history.log_data
        row_count = 0
        partial = False
        for index, row in df.iterrows():
            row_count = row_count + 1
            if partial:
                if row.action == Action.UPDATE_BUY:
                    order_book.set_asks(row.price, row.volume)
                elif row.action == Action.UPDATE_SELL:
                    order_book.set_bids(row.price, row.volume)

            if row.action == Action.PARTIAL:
                # print('partial', row.time, row_count)
                partial = True
                order_book.clear()


    def test_update_q_value2(self):
        '''
        :return:
        '''
        t = time.time()
        # history = load_file('../../DATA/MERGE.log.gz')    # NG
        history = load_file('../../MERGE-2020-05-04.log.gz') # OK
        print(history.start_time, history.end_time)
        print('load time', time.time() - t)


        t = time.time()
        history.setup_dollar_bar()
        print('setup dollar bar', time.time() - t)

        t = time.time()
        history.update_price()
        print('update price', time.time() - t)


        t = time.time()
        history.update_price()
        print('update price2', time.time() - t)

        t = time.time()
        history.update_q_value()
        print('update q value', time.time() - t)




    def test_update_q_value3(self):
        '''
        :return:
        '''
        history = load_file('../../DATA/MERGE.log.gz')    # NG
        # history = load_file('../../MERGE-2020-05-04.log.gz') # OK
        history.setup_dollar_bar()

        history.update_price()
        history.update_q_value()

        print(history.dollar_bar)

    def test_load_merge(self):
        history1 = load_file('../../DATA/BB/05/BB-2020-05-09T07-09-35.132396Z.log.gz')
        history1.setup_dollar_bar()
        history1.update_price()
        history1.update_q_value()

        history2 = load_file('../../DATA/BB/05/BB-2020-05-09T08-00-27.465324Z.log.gz')
        history2.setup_dollar_bar()
        history2.update_price()
        history2.update_q_value()

        history1.merge_log(history2)

    def test_load_files(self):
        files = (
            'BB-2020-10-01T00-09-41.084127Z.log.gz',
            'BB-2020-10-01T01-00-58.670877Z.log.gz',
            'BB-2020-10-01T01-53-02.064144Z.log.gz',
            'BB-2020-10-01T02-44-49.406307Z.log.gz',
            'BB-2020-10-01T03-36-14.186767Z.log.gz',
            'BB-2020-10-01T04-27-59.817297Z.log.gz',
            'BB-2020-10-01T05-19-36.804052Z.log.gz',
            'BB-2020-10-01T06-11-06.849645Z.log.gz',
            'BB-2020-10-01T07-02-24.289180Z.log.gz',
            'BB-2020-10-01T07-54-13.840578Z.log.gz',
            'BB-2020-10-01T08-45-42.229831Z.log.gz',
            'BB-2020-10-01T09-37-01.732325Z.log.gz',
            'BB-2020-10-01T10-28-16.647548Z.log.gz')

        root_path = '../../DATA/BB/10/'

        history1 = load_file(root_path+files[0])
        history2 = load_file(root_path+files[1])
        history3 = load_file(root_path+files[2])
        history4 = load_file(root_path+files[3])

        history1.merge_log(history2)
        history1.setup_dollar_bar()
        history1.update_price()
        history1.update_q_value()
        print(len(history1.dollar_bar))

        history2.merge_log(history3)
        history2.setup_dollar_bar()
        history2.update_price()
        history2.update_q_value()
        print(len(history2.dollar_bar))

        history3.merge_log(history4)
        history3.setup_dollar_bar()
        history3.update_price()
        history3.update_q_value()
        print(len(history3.dollar_bar))

        history1.merge_dollar_bar(history2)
        print(len(history1.dollar_bar))
        history1.merge_dollar_bar(history3)
        print(len(history1.dollar_bar))

        print(history1.dollar_bar)

    def test_load_globs(self):
        load_directory('../../DATA/BB/05/BB-2020-05-09T0*.log.gz')

if __name__ == '__main__':
    unittest.main()
