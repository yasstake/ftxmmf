from glob import glob
import os
import sys
import csv
from logger.util import LogLoader
from logger.util import *


class LogMerge:
    def __init__(self, files, out_path=None):
        if out_path:
            self.out_path = out_path
        else:
            self.out_path = './'

        self.log_files = files
        self.log_file_index = 0
        self.log_file_number = len(self.log_files)

        self.main_generator = None
        self.next_generator = None

        self.next_time = None
        self.current_file = None

    def open_new(self):
        self.main_generator = self.next_generator

        if self.log_file_index < self.log_file_number:
            file = self.log_files[self.log_file_index]
            print('openfile=', file)
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

    def update_write_file_name(self, time):
        self.current_file = self.out_path + os.sep + unix_time_to_date(time, True) + '.log'

    def write(self, action, time, index, price, size):
        if not self.current_file or action == Action.PARTIAL:
            self.update_write_file_name(time)

        with open(self.current_file, mode='a') as f:
            s = str(action) + ',' + str(time) + ',' + str(index) + ',' + str(price) + ',' + str(size) + '\n'
            f.write(s)

    @staticmethod
    def log_generator(log_file):
        with open(log_file) as f:
            reader = csv.reader(f)

            for row in reader:
                if len(row) == 0:
                    continue
                action, time, index, price, size = LogLoader.parse_line(row)
                yield action, time, index, price, size

    def output_file_name(self, date):
        date_string = unix_time_to_date(date)
        return date_string


if __name__ == '__main__':
    argc = len(sys.argv)

    print(argc)
    if argc != 2:
        print('python -m logger.merge path_to_log')
        exit(-1)

    path = sys.argv[1] + '*.log'

    print(path)
    log_files = sorted(glob(path))
    print(log_files)

    merge = LogMerge(log_files)
    merge.do()



