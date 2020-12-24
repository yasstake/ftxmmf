import unittest
from exchange.log import LogLoad
from exchange.log import timestamp
import pandas as pd

class MyTestCase(unittest.TestCase):
    def log_load(self):
        self.log_loader = LogLoad()
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
        print("---")
        print(self.log_loader.last_partial_index(self.log_loader.end_time))
        print("---")
        print(self.log_loader.last_partial_index(self.log_loader.start_time))
        print("---")
        print(self.log_loader.last_partial_index(self.log_loader.start_time+pd.Timedelta('1 h')))





if __name__ == '__main__':
    unittest.main()
