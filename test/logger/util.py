import unittest
from logger.util import *
from binascii import crc32

class MyTestCase(unittest.TestCase):
    def test_create(self):
        log = Logger()
        log.write('message1')
        log.write('message2')
        log.write('message3')


    def test_order_book_clear(self):
        ob = OrderBook()
        ob.clear()

    def test_order_book_set_asksself(self):
        ob = OrderBook()
        ob.set_asks(100, 1)
        print(ob.asks)

    def test_order_book_set_bits(self):
        ob = OrderBook()
        ob.set_bids(101, 2)
        print(ob.bids)
        ob.set_bids(101, 3)
        print(ob.bids)

    def test_order_book_to_string(self):
        ob = OrderBook()
        ob.set_asks(1, 2)
        ob.set_asks(1.1, 2)
        ob.set_asks(1, 0)
        ob.set_bids(100, 2)
        ob.set_bids(105, 2)
        ob.set_bids(101, 2)

        print(ob.to_string())

        print(ob.crc32())


    def test_comprss(self):
        cp = BoardCompress()

        cp.set_bids(100, 1)
        cp.set_bids(101, 2)
        cp.set_bids(102, 3)
        cp.set_asks(103, 0.1)
        cp.set_asks(104, 0.2)

        print(cp.encode())

if __name__ == '__main__':
    unittest.main()
