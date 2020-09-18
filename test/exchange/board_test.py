import unittest
from exchange.board import *
import matplotlib.pyplot as plt


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

        bit, ask = history.get_board(history.end_time)
        print(bit)
        print()
        print(ask)

        bit, ask = history.board_price(history.end_time)
        print(bit)
        print()
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

        last_index = history._get_last_partial_index(history._chop_log_data(history.log_data, start=0, end=1))
        print(last_index)

    def test_get_board_price(self):
        history = load_file('../../DATA/MERGE.log.gz')
        bit, ask = history.board_price(history.end_time - pd.Timedelta(seconds=60))
        print(bit, ask)

    def test_market_price(self):
        history = load_file('../../DATA/MERGE.log.gz')
        buy, sell = history.market_price(history.end_time - pd.Timedelta(seconds=60))
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

        for loc, rec in df.iterrows():
            print(loc)

    def test_export_to_json(self):
        history = load_file('../../DATA/MERGE.log.gz')
        long_df = history._filter_long(history.log_data)
        short_df = history._filter_short(history.log_data)

        self.write_json(long_df, '../../chart/html/long.json')
        self.write_json(short_df, '../../chart/html/short.json')

    def test_print_rows(self):
        history = load_file('../../DATA/MERGE.log.gz')
        df = history._filter_execute(history.log_data)
        for index, row in df.iterrows():
            print(row)


    def test_export_execute(self):
        history = load_file('../../DATA/MERGE.log.gz')
        df = history._filter_execute(history.log_data)

        VOL = 20
        tick = 0
        last_tick = 0
        size = 0
        doll = 0
        f = open('../../chart/html/dollbar.json', mode='w')
        f.write('[')
        t = 0

        o = h = l = c = None

        for index, row in df.iterrows():
            if row.action == Action.TRADE_LONG or row.action == Action.TRADE_SHORT_LIQUID \
                    or row.action == Action.TRADE_SHORT or row.action == Action.TRADE_SHORT_LIQUID:

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
                    line = ',{' + '"time": {0}, "open": {1}, "close": {2}, "high": {3}, "low": {4}' \
                              .format(t, o, c, h, l) + '}'
                    f.write(line)
                    o = c = h = l = None
        f.write(']')
        f.close()






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

    def test_doll_bar(self):

        for r in df.itertuples(name=None):
            time = int(r[1].value / 1000_000_000)
            if last_time == time:
                continue


#        long_df.to_json('long.json', orient='records')

if __name__ == '__main__':
    unittest.main()
