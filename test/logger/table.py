import unittest
import tables
import pandas as pd


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)


    def test_write_table_data(self):
        pass

    def test_read_table_data(self):
        df = pd.read_hdf('../../logdb.h5')
        print(df)


if __name__ == '__main__':
    unittest.main()
