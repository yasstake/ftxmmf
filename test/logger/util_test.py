import unittest

from logger.table import LogRecord
from logger.util import *


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

        print(ob.to_ftx_string())

        print(ob.ftx_crc32())


    def test_comprss(self):
        cp = BoardCompress()

        cp.set_bids(100, 1)
        cp.set_bids(101, 2)
        cp.set_bids(102, 3)
        cp.set_asks(103, 0.1)
        cp.set_asks(104, 0.2)

        print(cp.encode())

    def test_create_table(self):
        h5file = open_file('./test.h5', mode='w', title='testfile')
        group = h5file.create_group('/', 'LOG', 'log info')

        table = h5file.create_table(group, 'log', LogRecord, 'log_data')
        log_record = table.row

        for i in range(10):
            log_record['time'] = 1000 + i
            log_record['action'] = 1
            log_record.append()


    def test_log_loder(self):
        loader = LogTable()
        loader.open_db('./test.hd5')
        loader.load('./test.log')

    def test_okex_crc32(self):
        '''
        https://www.okex.com/docs/en/#spot_ws-checksum

        "asks": [["3366.8", "9", 10],[ "3368","8",3]],
        "bids": [["3366.1", "7", 0],[ "3366","6",3 ]]
        "checksum": -1881014294
        checksumstring: 3366.1:7:3366.8:9:3366:6:3368:8
        '''
        book = OrderBook()

        book.set_asks(3366.8, 9)
        book.set_asks(3368, 8)
        book.set_bids(3366.1, 7)
        book.set_bids(3366, 6)

        print(book.okex_crc32())
        print(book.to_okex_string())
        print('3366.1:7:3366.8:9:3366:6:3368:8  [expect]')



        '''
        "asks": [["3366.8", "9", 10],[ "3368","8",3],[ "3372","8",3 ]],
        "bids": [["3366.1", "7", 0]]
        "checksum": 831078360
        checksumstring: 3366.1:7:3366.8:9:3368:8:3372:8
        '''
        book = OrderBook()
        book.set_asks(3366.8, 9)
        book.set_asks(3368, 8)
        book.set_asks(3372, 8)
        book.set_bids(3366.1, 7)

        print(book.okex_crc32())
        print(book.to_okex_string())
        print('3366.1:7:3366.8:9:3368:8:3372:8  [expect]')


    def test_okex_crc3(self):
        """
        "asks": [["8.8", "96.99999966", 1],
            ["9", "39", 3],
            ["9.5", "100", 1],
            ["12", "12", 1],
            ["95", "0.42973686", 3],
            ["11111", "1003.99999795", 1]
            ]
        "bids": [
            ["5", "7", 4],
            ["3", "5", 3],
            ["2.5", "100", 2],
            ["1.5", "100", 1],
            ["1.1", "100", 1],
            ["1", "1004.9998", 1]
        ]
        "checksum": 468410539
        """
        book = OrderBook()

        book.set_asks(8.8, 96.99999966)
        book.set_asks(9, 39)
        book.set_asks(9.5, 100)
        book.set_asks(12, 12)
        book.set_asks(95, 0.42973686)
        book.set_asks(11111, 1003.99999795)
        book.set_bids(5, 7)
        book.set_bids(3, 5)
        book.set_bids(2.5,100)
        book.set_bids(1.5,100)
        book.set_bids(1.1,100)
        book.set_bids(1, 1004.9998)

        print(book.to_okex_string())
        print(book.okex_crc32())


        '''
        "bids": [
            ["3983", "789", 0, 3]
        ],
        "checksum": -1200119424
        '''
        book.set_bids(3983, 789)
        print(book.to_okex_string())
        print(book.okex_crc32())




    def test_okex_crc(self):
        crc = crc32('3366.1:7:3366.8:9:3368:8:3372:8'.encode())
        print(crc)

        crc = crc32('3366.1:7:3366.8:9:3366:6:3368:8'.encode())
        print(crc)
        print(crc - 2**32)

if __name__ == '__main__':
    unittest.main()
