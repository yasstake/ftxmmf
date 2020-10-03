import unittest
from logger.chop import *

class MyTestCase(unittest.TestCase):
    def test_load(self):
        loader = Loader()
        loader.load('../../DATA/MERGE.log.gz')
        loader.describe()

    def test_cut(self):
        loader = Loader()
        loader.load('../../DATA/MERGE.log.gz')
        loader.describe()
        loader.cut(loader.last_time - 10000)
        print('------')
        loader.describe()

    def test_save(self):
        loader = Loader()
        loader.load('../../DATA/MERGE.log.gz')
        loader.describe()
        loader.save('./', compress=True)

if __name__ == '__main__':
    unittest.main()
