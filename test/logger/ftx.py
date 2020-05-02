import unittest
from logger.ftx import *
from logger.util import *


PM = "{'time': 1588243847.3685906, 'checksum': 2852320671, 'bids': [[8841.5, 86.3452], [8841.0, 1.1655]], 'asks': [[8842.0, 1.3722], [8843.0, 2.09], [8843.5, 0.4534], [8845.0, 0.0025], [8845.5, 91.4261], [8846.0, 67.46], [8849.0, 1.354], [8850.0, 1.4978], [8851.5, 1.856], [8852.0, 31.0916], [9059.5, 0.2]], 'action': 'partial'}"
UM = "{'time': 1588247034.0146255, 'checksum': 1508078090, 'bids': [[8949.5, 2.4925]], 'asks': [[8953.0, 5.1394], [9146.0, 0.0]], 'action': 'update'}"
TM = "[{'id': 39655788, 'price': 8950.5, 'size': 0.0001, 'side': 'sell', 'liquidation': False, 'time': '2020-04-30T11:43:53.734593+00:00'}]"
ISO_TIME =  '2020-04-30T11:43:53.734593+00:00'
ISO_TIME2 = '2020-04-30T11:43:53.734593Z'
ISO_TIME3 = '2020-04-30T11:43:53.7345933Z'
ISO_TIME4 = '2020-04-30T11:43:53.7345Z'
ISO_TIME0 = '2020-04-30T11:43:53.734593Z'
UNIX_TIME = 1588247033.734593

class TestFtxClient(unittest.TestCase):
    def test_board_partial_message_to_csv(self):
        client = FtxClient()
        json_message = PM
        csv_message = client._board_message_to_csv(json_message)
        print(csv_message)

    def test_board_update_message_to_csv(self):
        client = FtxClient()
        json_message = UM
        csv_message = client._board_message_to_csv(json_message)
        print(csv_message)

    def test_trade_message_to_csv(self):
        client = FtxClient()
        json_message = TM
        csv_message = client._trade_message_to_csv(json_message)
        print(csv_message)

    def test_isotime_to_unix(self):
        iso_time = ISO_TIME0
        unix_time = isotime_to_unix(iso_time)
        print(unix_time)
        self.assertEqual(unix_time, UNIX_TIME)

        iso_time = ISO_TIME
        unix_time = isotime_to_unix(iso_time)
        print(unix_time)
        self.assertEqual(unix_time, UNIX_TIME)

        iso_time = ISO_TIME2
        unix_time = isotime_to_unix(iso_time)
        print(unix_time)
        self.assertEqual(unix_time, UNIX_TIME)

        iso_time = ISO_TIME3
        unix_time = isotime_to_unix(iso_time)
        print(unix_time)
        self.assertEqual(unix_time, UNIX_TIME)

        iso_time = ISO_TIME4
        unix_time = isotime_to_unix(iso_time)
        print(unix_time)
        #self.assertEqual(unix_time, UNIX_TIME)

    def test_unixtime_to_iso(self):
        unix_time = UNIX_TIME
        iso_time = unixtime_to_iso(unix_time)
        print(iso_time)
        self.assertEqual(iso_time, ISO_TIME0)

    def test_unix_convert(self):
        unix_time = UNIX_TIME
        iso_time = unixtime_to_iso(unix_time)
        print(iso_time)
        unix_time2 = isotime_to_unix(iso_time)

        self.assertEqual(unix_time, unix_time2)
        print(unix_time2)

    def test_unix_time_now(self):
        unix_time = unixtime_now()
        print(unix_time)
        print(unixtime_to_iso(unix_time))

    def test_unix_time_only(self):
        iso_time_now  = '2020-04-30T23:59:59.999999Z'
        iso_time_day = '2020-04-30T00:00:00.000000Z'

        unix_now = isotime_to_unix(iso_time_now, True)
        unix_day = isotime_to_unix(iso_time_day, True)

        print(unix_now, unix_day, unix_now - unix_day, 2**32)
        print(unix_now - unix_day)
        print(2 ** 32)
        print(unix_now)
        print(2 ** 64)
        print(int(2 ** 64 / 1000))



if __name__ == '__main__':
    unittest.main()
