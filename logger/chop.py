import pandas as pd
import os

PARTIAL = 1


def timestring(time):
    """

    :param time:
    :return:
    >>> timestring(1)
    '1970-01-01T00-00-00000001'
    """
    t = str(pd.Timestamp(time * 1000))
    t = t.replace(' ', 'T').replace(':', '-').replace('.', '')
    return t


class Loader:
    def __init__(self):
        self.df = None
        self.first_partial_rec = None
        self.first_partial_time = None
        self.last_rec = None
        self.last_time = None

    def load(self, file):
        names = ('action', 'time', 'seq', 'price', 'volume', 'checksum')
        self.df = pd.read_csv(file, names=names)
        self.analyze()

    def save(self, path_to_dir, compress=False):
        file_name = path_to_dir + os.sep + timestring(self.first_partial_time) + '-' + timestring(self.last_time)
        if compress:
            file_name = file_name + '.gz'
        self.df.to_csv(file_name, header=True, index=False)

    def cut(self, end_time):
        self.df = self.df[(self.df['time'] < end_time)]
        self.df.reset_index(inplace=True)
        self.analyze()

    def describe(self):
        print('first partial rec:', self.first_partial_rec)
        print('first partial time:', self.first_partial_time)
        print('last rec:', self.last_rec)
        print('last time:', self.last_time)

    def analyze(self):
        partial = self.df[self.df['action'] == PARTIAL]
        print('len->', len(partial))
        self.first_partial_rec = partial.index[0]
        self.last_rec = self.df.shape[0] - 1
        self.first_partial_time = self.df.loc[self.first_partial_rec]['time']
        self.last_time = self.df.loc[self.last_rec]['time']


if __name__ == "__main__":
    import doctest
    doctest.testmod()