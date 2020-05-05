import sys
from glob import glob
import csv
from logger.util import *
from logger.table import LogTable
from tqdm import tqdm
import gzip


class LogMerge:
    def __init__(self, files, out_path=None):
        if out_path:
            self.out_path = out_path
        else:
            self.out_path = './MERGE'

        self.log_files = files
        self.log_file_index = 0
        self.log_file_number = len(self.log_files)

        self.main_generator = None
        self.next_generator = None

        self.next_time = None
        self.current_file_name = None
        self.current_file = None
        self.current_out_progress = None

    def open_new(self):
        self.main_generator = self.next_generator

        if self.log_file_index < self.log_file_number:
            file = self.log_files[self.log_file_index]
            self.next_generator = LogMerge.log_generator(file)
            self.log_file_index += 1
        else:
            self.next_generator = None

    def do(self):
        self.open_new()

        while True:
            self.open_new()

            time_n = 0
            if not self.main_generator:
                break

            if self.next_generator:
                action_n, time_n, index_n, price_n, size_n = next(self.next_generator,
                                                                  [None, None, None, None, None])
            else:
                time_n = None

            for action, time, index, price, size in self.main_generator:
                if (time_n and time < time_n) or (not time_n):
                    self.write(action, time, index, price, size)
                else:
                    if time_n:
                        self.write(action_n, time_n, index_n, price_n, size_n)
                    print('-----break------')
                    break

    def update_write_file(self, time):
        new_file_name = self.out_path + '-' + unix_time_to_date(time, True) + '.log.gz'
        if new_file_name == self.current_file_name:
            return

        self.current_file_name = new_file_name

        if self.current_file:
            self.current_file.close()

        self.current_file = gzip.open(self.current_file_name, mode='wt')

        if self.current_file is None:
            print('ERROR to open file', self.current_file_name)
            return

        self.current_out_progress = tqdm(desc='[OUT] ' + self.current_file_name, position=1)

    def write(self, action, time, index, price, size):
        if not self.current_file_name or action == Action.PARTIAL:
            self.update_write_file(time)

        f = self.current_file
        s = str(action) + ',' + str(time) + ',' + str(index) + ',' + str(price) + ',' + str(size) + '\n'
        f.write(s)
        self.current_out_progress.update(1)

    @staticmethod
    def log_generator(log_file):
        f = None
        if log_file.endswith('.gz'):
            f = gzip.open(log_file, 'rt', 'utf-8')
        else:
            f = open(log_file)

        if f is None:
            print('ERROR to open', log_file)
            return False

        reader = csv.reader(f)

        for row in tqdm(reader, position=0, desc='[FROM] ' + log_file):
            if len(row) == 0:
                continue
            action, time, index, price, size = LogTable.parse_line(row)

            yield action, time, index, price, size


if __name__ == '__main__':
    prefix = ''
    path = ''

    argc = len(sys.argv)

    if argc == 2:
        path = sys.argv[1]
    elif argc == 3:
        path = sys.argv[1]
        prefix = sys.argv[2]
    else:
        print('python -m logger.merge path_to_log [out_prefix]')
        exit(-1)

    if (not path.endswith('.log')) and (not path.endswith('log.gz')):
        path += '*.log'

    log_files = sorted(glob(path))
    print('processing...')
    print(log_files)

    merge = LogMerge(log_files, out_path=prefix)
    merge.do()



