import unittest
from logger.util import *

class MyTestCase(unittest.TestCase):
    def test_create(self):
        log = Logger()
        log.write('message1')
        log.write('message2')
        log.write('message3')


    def test_something(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
