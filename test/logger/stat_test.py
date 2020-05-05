import unittest
from logger.stat import Market


class MarketTestCase(unittest.TestCase):
    def test_sample(self):
        pass

    def test_create(self):
        m = Market()

        m.load_csv('../../DATA/BF-TEST.log')


if __name__ == '__main__':
    unittest.main()
