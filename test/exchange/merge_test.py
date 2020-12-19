import unittest
from exchange.board import LogMerge

class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_load(self):
        log = LogMerge()
        log.append('../../DATA/BB/05/BB-2020-05-09T06-16-23.367761Z.log.gz')
        log.dump()

        print(log.file_name())

    def test_load_directory(self):
        log = LogMerge()
        log.append_directory('../../DATA/BB/05/*')

if __name__ == '__main__':
    unittest.main()
