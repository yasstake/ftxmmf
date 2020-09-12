import unittest
from exchange.board import *


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

    def test_get_board(self):
        history = load_file('./testdata.csv')
        print(history.start_time)
        print(history.end_time)

        bit, ask = history._get_board_df(3)
        print(bit)
        print()
        print(ask)
        print('---')
        bit, ask = history.get_board(3)
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


if __name__ == '__main__':
    unittest.main()
