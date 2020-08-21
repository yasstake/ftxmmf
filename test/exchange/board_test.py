import unittest
from exchange.board import *


class MyTestCase(unittest.TestCase):
    def test_something(self):
        history = History()
        history.load_file('../../DATA/MERGE.log.gz')
        print(history.start_time)
        print(history.end_time)


if __name__ == '__main__':
    unittest.main()
