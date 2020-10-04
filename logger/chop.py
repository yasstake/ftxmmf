import pandas as pd
import os
import glob

PARTIAL = 1

def time_to_datetime(time):
    """
    convert time(in microsec from epoctime) to pd.Timestamp object
    :param time: time in logs(micro sec)
    :return: pd Timestamp object
    >>> t = time_to_datetime(1)
    >>> str(t) == '1970-01-01 00:00:00.000001'
    True
    """
    return pd.Timestamp(time * 1000)


def time_to_yymmdd(time):
    """
    convert time(in microsec from epoc) to YYMMDD
    :param time: time from epoctiem
    :return: YYMMDD string
    >>> time_to_yymmdd(1)
    '1970-01-01'
    >>> time_to_yymmdd(2)
    '1970-01-01'
    """
    time = time_to_datetime(time)
    yyyymmdd = time.strftime('%Y-%m-%d')

    return yyyymmdd

def time_to_hhmmss(time):
    """
    convert time(in microsec from epoc) to YYMMDD
    :param time: time from epoctiem
    :return: HHMMSS string (cut under the second)
    >>> time_to_hhmmss(1 * 1000_000)
    '00-00-01'
    >>> time_to_hhmmss(2.1 * 1000_000)
    '00-00-02'
    """
    time = time_to_datetime(time)
    hhmmsss = time.strftime('%H-%M-%S')

    return hhmmsss



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
        file_name = path_to_dir + os.sep + time_to_hhmmss(self.first_partial_time) +\
                    '-' + time_to_hhmmss(self.last_time)
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


def log_files(pattern):
    return glob.glob(pattern).sort()


def chop_log_files(pattern):
    loader = None
    for file in log_files(pattern):
        if loader is not None:
            pass

        loader = Loader()
        loader.load(file)

        pass



if __name__ == "__main__":
    import doctest
    doctest.testmod()