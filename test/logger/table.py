import unittest
import h5py


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_create(self):
        f = h5py.File('/tmp/data.hdf5', mode='r+')
        f.close()

    def test_create_with(self):
        with h5py.File('/tmp/data.hdf5', mode='w') as f:
            f.create_group('/TRADE/')
            pass

    def test_crete_trade_data(self):
        with h5py.File('/tmp/data.hdf5', mode='w') as f:
            f.create_group('/TRADE/')
            f.create_dataset('')
            pass



if __name__ == '__main__':
    unittest.main()
